# Reader functions to import multiple LODs as meshes
# from the BI MLOD P3D format. Format specifications can
# be found on the community wiki (although not withoug errors):
# https://community.bistudio.com/wiki/P3D_File_Format_-_MLOD


# import struct
import math
import re
import time
import os

import bpy
import bmesh
import mathutils

# from . import binary_handler as binary
from . import data_p3d as p3d
from ..utilities import generic as utils
from ..utilities import lod as lodutils
from ..utilities import compat as computils
from ..utilities import proxy as proxyutils
from ..utilities import flags as flagutils
from ..utilities import structure as structutils
from ..utilities import data
from ..utilities import errors
from ..utilities.logger import ProcessLogger


def read_lod(context, file, material_dict, additional_data, dynamic_naming, logger, addon_prefs):
    return


def categorize_lods(operator, context, mlod):
    categories = {}
    lods = []

    root = context.scene.collection
    if operator.enclose:
        root = bpy.data.collections.new(name=os.path.basename(operator.filepath))
        bpy.context.scene.collection.children.link(root)
    
    if operator.groupby == 'NONE':
        categories["None"] = [0, root]
        lods = [[*lodutils.get_lod_id(lod.resolution), 0] for lod in mlod.lods]

    else:
        for lod in mlod.lods:
            lod_index, lod_resolution = lodutils.get_lod_id(lod.resolution)
            group_dict = data.lod_groups[operator.groupby]
            group_name = group_dict[lod_index]

            if group_name not in categories:
                new_category = bpy.data.collections.new(name=group_name)
                root.children.link(new_category)
                categories[group_name] = [len(categories), new_category]
            
            lods.append([lod_index, lod_resolution, categories[group_name][0]])

    return [cat[1] for cat in categories.values()], lods


def create_blender_materials(lookup):
    materials = []
    
    for texture, material in lookup.keys():
        material_name = "P3D: %s :: %s" % (os.path.basename(texture), os.path.basename(material))
        if texture == "" and material == "":
            material_name = "P3D: no material"
            
        new_mat = bpy.data.materials.new(material_name)
        new_mat.a3ob_properties_material.from_p3d(texture.strip(), material.strip())
        materials.append(new_mat)
        
    return materials


def process_normals(mesh, lod):
    loop_normals = lod.loop_normals()
    
    if len(mesh.loops) == len(loop_normals):
        mesh.normals_split_custom_set(loop_normals)


def process_sharps(bm, lod):
    data = None
    for tagg in lod.taggs:
        if tagg.name == "#SharpEdges#":
            data = tagg.data
            break
    
    if not data:
        return
    
    for edge in bm.edges:
        edge.smooth = True
    
    for item in data.edges:
        edge = bm.edges.get([bm.verts[item[0]], bm.verts[item[1]]])
        if edge:
            edge.smooth = False


def process_uvsets(bm, lod):
    uvsets = lod.uvsets()
        
    for idx in uvsets:
        uvs = uvsets[idx]
        layer_name = "UVSet %d" % idx
        layer = bm.loops.layers.uv.get(layer_name)
        if not layer:
            layer = bm.loops.layers.uv.new(layer_name) 
        
        for face in bm.faces:
            for loop in face.loops:
                loop[layer].uv = uvs[loop.index]


def process_selections(bm, lod):
    bm.verts.layers.deform.verify()
    layer = bm.verts.layers.deform.active
    
    selection_names = []
    for tagg in lod.taggs:
        if tagg.name[0] == tagg.name[-1] == "#":
            continue
        
        selection_idx = len(selection_names)
        weights = tagg.data.weight_verts
        for idx in weights:
            bm.verts[idx][layer][selection_idx] = weights[idx]
        
        selection_names.append(tagg.name)
    
    return selection_names


def process_materials(mesh, bm, lod, materials, materials_lookup):
    face_indices, material_indices = lod.get_sections(materials_lookup)
    
    for i, idx in enumerate(face_indices):
        bm.faces[i].material_index = idx
    
    for idx in material_indices:
        mesh.materials.append(materials[idx])


def process_mass(bm, lod):
    data = None
    for tagg in lod.taggs:
        if tagg.name == "#Mass#":
            data = tagg.data
    
    if not data:
        return
    
    layer = bm.verts.layers.float.new("a3ob_mass")
    for vert in bm.verts:
        vert[layer] = data.masses[vert.index]


def process_properties(obj, lod):
    for tagg in lod.taggs:
        if tagg.name != "#Property#":
            continue
        
        new_prop = obj.a3ob_properties_object.properties.add()
        new_prop.name = tagg.data.key
        new_prop.value = tagg.data.value


def process_flag_groups_vertex(obj, bm, lod):
    groups, values = lod.flag_groups_vertex()

    layer = flagutils.get_layer_flags_vertex(bm)
    for vert in bm.verts:
        vert[layer] = values[vert.index]
    
    for i, grp in enumerate(groups):
        new_group = obj.a3ob_properties_object_flags.vertex.add()
        new_group.name = ("Group %d" % i if i > 0 else "Default")
        new_group.set_flag(grp)


def process_flag_groups_face(obj, bm, lod):
    groups, values = lod.flag_groups_face()

    layer = flagutils.get_layer_flags_face(bm)
    for face in bm.faces:
        face[layer] = values[face.index]
    
    for i, grp in enumerate(groups):
        new_group = obj.a3ob_properties_object_flags.face.add()
        new_group.name = ("Group %d" % i if i > 0 else "Default")
        new_group.set_flag(grp)


# Align the object coordinate system with the proxy coordinates.
# https://mrcmodding.gitbook.io/home/documents/proxy-coordinates
def transform_proxy(obj):
    rotation_matrix = proxyutils.get_transform_rotation(obj)
    obj.data.transform(rotation_matrix)
    obj.matrix_world @= rotation_matrix.inverted()
    
    translate = mathutils.Matrix.Translation(-proxyutils.find_axis_vertices(obj.data)[0].co)
    obj.data.transform(translate)
    obj.matrix_world @= translate.inverted()
    
    obj.data.update()


def process_proxies(operator, obj, proxy_lookup, empty_material):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

    for key in proxy_lookup:
        vgroup = obj.vertex_groups.get(key)
        if not vgroup:
            continue
            
        obj.vertex_groups.active = vgroup
        computils.call_operator_ctx(bpy.ops.object.vertex_group_select)

        try:
            bpy.ops.mesh.separate(type='SELECTED')
            obj.vertex_groups.remove(vgroup)
        except:
            pass

    bpy.ops.object.mode_set(mode='OBJECT')
        
    proxy_objects = [proxy for proxy in bpy.context.selected_objects if proxy != obj]
        
    bpy.ops.object.select_all(action='DESELECT')
    
    if operator.proxy_action == 'CLEAR':
        computils.call_operator_ctx(bpy.ops.object.delete, {"selected_objects": proxy_objects})

    elif operator.proxy_action == 'SEPARATE':
        for i, proxy_obj in enumerate(proxy_objects):
            proxy_obj.a3ob_properties_object.is_a3_lod = False
            proxy_obj.a3ob_properties_object_proxy.dynamic_naming = operator.dynamic_naming

            transform_proxy(proxy_obj)
            structutils.cleanup_vertex_groups(proxy_obj) # need to remove the unused groups leftover from the separation

            vgroup = proxy_obj.vertex_groups.get("@proxy_%d" % i)
            if not vgroup:
                continue
            
            path, index = proxy_lookup[vgroup.name]
            proxy_obj.vertex_groups.remove(vgroup)
            proxy_obj.a3ob_properties_object_proxy.proxy_path = utils.restore_absolute(path, ".p3d")
            proxy_obj.a3ob_properties_object_proxy.proxy_index = index

            proxy_obj.a3ob_properties_object_flags.vertex.clear()
            proxy_obj.a3ob_properties_object_flags.face.clear()

            bm = bmesh.new()
            bm.from_mesh(proxy_obj.data)

            flagutils.clear_layer_flags_vertex(bm)
            flagutils.clear_layer_flags_face(bm)

            bm.to_mesh(proxy_obj.data)
            bm.free()

            proxy_obj.a3ob_properties_object_proxy.is_a3_proxy = True
            proxy_obj.data.materials.clear()
            proxy_obj.data.materials.append(empty_material)
            proxy_obj.parent = obj


def process_lod(operator, context, lod, additional_data, materials, materials_lookup, categories, lod_links):
    lod_index = lod_links[0]
    lod_resolution = lod_links[1]
    lod_name = lodutils.format_lod_name(lod_index, lod_resolution)
    
    mesh = bpy.data.meshes.new(lod_name)
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(180)
    
    mesh.from_pydata(*lod.pydata())
    mesh.update(calc_edges=True)
    
    obj = bpy.data.objects.new(lod_name, mesh)

    # Setup LOD properties
    object_props = obj.a3ob_properties_object
    object_props.dynamic_naming = operator.dynamic_naming
    try:
        object_props.lod = str(lod_index)
    except:
        object_props.lod = "30"
        
    object_props.resolution = lod_resolution

    
    for face in mesh.polygons:
        face.use_smooth = True
    
    if 'NORMALS' in additional_data:
        process_normals(mesh, lod)
    
    # Process TAGGs
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    process_sharps(bm, lod)
    
    if 'UV' in additional_data:
        process_uvsets(bm, lod)
    
    selection_names = []
    proxy_lookup = {}
    if 'SELECTIONS' in additional_data:
        proxy_lookup = lod.proxies_to_placeholders()
        selection_names = process_selections(bm, lod)
    
    if 'MATERIALS' in additional_data:
        process_materials(mesh, bm, lod, materials, materials_lookup)
    
    if 'MASS' in additional_data:
        process_mass(bm, lod)
    
    process_properties(obj, lod)
    process_flag_groups_vertex(obj, bm, lod)
    process_flag_groups_face(obj, bm, lod)
        
    for name in selection_names:
        obj.vertex_groups.new(name=name)

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    collection = categories[lod_links[2]]
    collection.objects.link(obj)

    if operator.proxy_action != 'NOTHING' and 'SELECTIONS' in additional_data:
        process_proxies(operator, obj, proxy_lookup, materials[0])

    object_props.is_a3_lod = True


def read_file(operator, context, file, first_lod_only = False):
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
        
    context.view_layer.objects.active = None

    time_file_start = time.time()
    
    mlod = p3d.P3D_MLOD.read(file, first_lod_only)
    categories, lod_links = categorize_lods(operator, context, mlod)

    # print(categories, lod_links)
    
    # return mlod.lods

    additional_data = set()
    if operator.additional_data_allowed:
        additional_data = operator.additional_data
    
    materials = None
    materials_lookup = None
    if 'MATERIALS' in additional_data:
        materials_lookup = mlod.get_materials()
        materials = create_blender_materials(materials_lookup)
    
    for i, lod in enumerate(mlod.lods):
        process_lod(operator, context, lod, additional_data, materials, materials_lookup, categories, lod_links[i])
    
    print("P3D Import finished in %f sec" % (time.time() - time_file_start))
    
    return mlod.lods