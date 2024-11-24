import os
import re

import bpy

from .generic import restore_absolute
from ..io.import_paa import import_file
from ..io import config


class RVMATTemplateField:
    def __init__(self, string):
        if not string.startswith("<") or not string.endswith(">") or string.count("|") != 2:
            print(string)
            raise ValueError("Invalid RVMAT template field definition")
        
        string = string[1:-1]
        suffixes, extensions, default = string.split("|")

        self.suffixes = [("_%s" % item.strip().lower()) for item in suffixes.split(",")]
        self.extensions = [(".%s" % item.strip().lower()) for item in extensions.split(",")]

        self.default = default
    
    def generate_paths(self, folder, basename):
        return [os.path.join(folder, basename + sfx + ext) for sfx in self.suffixes for ext in self.extensions]
    
    def generate_value(self, root, folder, basename, check_files_exist):
        paths = self.generate_paths(folder, basename)
        print(paths)

        for item in paths:
            if os.path.isfile(item):
                return os.path.relpath(item, root)
        
        if not check_files_exist:
            return os.path.relpath(paths[0], root)
        
        return self.default


class RVMATTemplate:
    RE_STAGE = re.compile(r"<.*>")

    def __init__(self, filepath):
        self.fields = []
        with open(filepath) as file:
            self.template = file.read()

        for match in self.RE_STAGE.finditer(self.template):
            try:
                self.fields.append(RVMATTemplateField(match.group(0)))
            except ValueError as ex:
                self.fields.append(None)
    
    def write_output(self, root, folder, basename, check_files_exist):
        values = ((field.generate_value(root, folder, basename, check_files_exist) if field else None) for field in self.fields)
        
        def repl(match):
            string = next(values)
            if string is None:
                return match.group(0)
            
            return "\"%s\"" % string
        
        try:
            if not os.path.isdir(folder):
                os.makedirs(folder)

            with open(os.path.join(folder, basename + ".rvmat"), "w") as file:
                file.write(self.RE_STAGE.sub(repl, self.template))
                return True
            
        except Exception as ex:
            print(ex)
            return False


class DummyPAAOperator:
    def __init__(self, filepath, color_space):
        self.filepath = filepath
        self.color_space = color_space


def import_texture(ast, path, isdata):
    relpath = ast.get_prop(path)
    if not relpath:
        return None
    
    filepath = restore_absolute(relpath.topy())
    if not os.path.isfile(filepath):
        return None
    
    with open(filepath, "rb") as file:
        img, _ = import_file(DummyPAAOperator(filepath, 'DATA' if isdata else 'SRGB'), bpy.context, file)
    
    return img


def setup_nohq(tree, shadernode, rvmat):
    nodes = tree.nodes
    links = tree.links

    img = import_texture(rvmat, "rvmat/stage1/texture", True)
    if not img:
        return
    
    texnode = nodes.new('ShaderNodeTexImage')
    texnode.image = img

    sepnode = nodes.new('ShaderNodeSeparateColor')
    mergenode = nodes.new('ShaderNodeCombineColor')
    normalnode = nodes.new('ShaderNodeNormalMap')
    invnode = nodes.new('ShaderNodeInvert')

    links.new(texnode.outputs[0], sepnode.inputs[0])
    links.new(sepnode.outputs[0], mergenode.inputs[0])
    links.new(sepnode.outputs[1], invnode.inputs[1])
    links.new(invnode.outputs[0], mergenode.inputs[1])
    links.new(sepnode.outputs[2], mergenode.inputs[2])
    links.new(mergenode.outputs[0], normalnode.inputs[1])
    links.new(normalnode.outputs[0], shadernode.inputs[22])


def setup_mc(tree, shadernode, texnode, rvmat):
    nodes = tree.nodes
    links = tree.links

    img = import_texture(rvmat, "rvmat/stage3/texture", False)
    if not img:
        return
    
    mcnode = nodes.new('ShaderNodeTexImage')
    mcnode.image = img
    
    if not texnode:
        texnode = nodes.new('ShaderNodeRGB')
        texnode.outputs[0].default_value = shadernode.inputs[0].default_value

    mixnode = nodes.new('ShaderNodeMix')
    mixnode.data_type = 'RGBA'
    mixnode.inputs[0].default_value = 1
    
    links.new(texnode.outputs[0], mixnode.inputs[6])
    links.new(mcnode.outputs[0], mixnode.inputs[7])
    links.new(mcnode.outputs[1], mixnode.inputs[0])
    links.new(mixnode.outputs[2], shadernode.inputs[0])


def setup_smdi(tree, shadernode, rvmat):
    nodes = tree.nodes
    links = tree.links

    img = import_texture(rvmat, "rvmat/stage5/texture", True)
    if not img:
        return
    
    texnode = nodes.new('ShaderNodeTexImage')
    texnode.image = img

    sepnode = nodes.new('ShaderNodeSeparateColor')
    invnode = nodes.new('ShaderNodeInvert')

    links.new(texnode.outputs[0], sepnode.inputs[0])
    links.new(sepnode.outputs[2], invnode.inputs[1])
    links.new(sepnode.outputs[1], shadernode.inputs[7])
    links.new(invnode.outputs[0], shadernode.inputs[9])


def setup_supershader(tree, shadernode, texnode, rvmat):
    setup_nohq(tree, shadernode, rvmat)
    setup_mc(tree, shadernode, texnode, rvmat)
    setup_smdi(tree, shadernode, rvmat)


def setup_color(mat: bpy.types.Material, shadernode: bpy.types.ShaderNodeBsdfPrincipled):
    mat_props = mat.a3ob_properties_material
    tree = mat.node_tree
    
    if mat_props.texture_type == 'TEX' and os.path.isfile(mat_props.texture_path):
        with open(mat_props.texture_path, "rb") as file:
            try:
                img, _ = import_file(DummyPAAOperator(mat_props.texture_path, 'SRGB'), bpy.context, file)
            except:
                return None

        texnode = tree.nodes.new('ShaderNodeTexImage')
        texnode.image = img
        tree.links.new(texnode.outputs[0], shadernode.inputs[0])
        return texnode

    elif mat_props.texture_type == 'COLOR':
        texnode = tree.nodes.new('ShaderNodeRGB')
        texnode.inputs[0].default_value = mat_props.color_value
        tree.links.new(texnode.outputs[0], shadernode.inputs[0])
        return texnode
    
    return None


def setup_color_ambient(mat, shadernode, rvmat):
    ambient = rvmat.get_prop("rvmat/ambient")
    if not ambient:
        return
    
    color = ambient.topy()

    try:
        mat.diffuse_color = color
        shadernode.inputs[0].default_value = color
    except:
        pass


def setup_material(mat: bpy.types.Material):
    mat_props = mat.a3ob_properties_material
    mat.use_nodes = True
    mat.use_backface_culling = True
    tree = mat.node_tree
    tree.nodes.clear()

    outnode = tree.nodes.new('ShaderNodeOutputMaterial')
    shadernode = tree.nodes.new('ShaderNodeBsdfPrincipled')
    tree.links.new(shadernode.outputs[0], outnode.inputs[0])

    texnode = setup_color(mat, shadernode)

    if not os.path.isfile(mat_props.material_path):
        return

    try:
        tokens = config.tokenize_file(mat_props.material_path)
        tokens = config.wrap(tokens, "rvmat")
        rvmat = config.parse(tokens)
    except:
        return
    
    setup_color_ambient(mat, shadernode, rvmat)
    
    shadertype = rvmat.get_prop("rvmat/PixelShaderID")
    if shadertype and shadertype.topy() == "Super":
        setup_supershader(tree, shadernode, texnode, rvmat)
