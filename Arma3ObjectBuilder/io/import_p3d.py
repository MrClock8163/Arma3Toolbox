import struct
import math
import re
import time
import os

import bpy
import bmesh
import mathutils

from . import binary_handler as binary
from ..utilities import generic as utils
from ..utilities import lod as lodutils
from ..utilities import proxy as proxyutils
from ..utilities import structure as structutils
from ..utilities import data
from ..utilities.logger import ProcessLogger


def read_signature(file):
    return binary.read_char(file, 4)


def read_file_header(file):
    signature = read_signature(file)
    if signature != "MLOD":
        raise IOError(f"Invalid MLOD signature: {signature}")
        
    version = binary.read_ulong(file)
    count_lod = binary.read_ulong(file)
    
    return version, count_lod


def read_vertex(file):
    x, y, z = struct.unpack('<fff', file.read(12))
    file.read(4) # dump vertex flags
    return x, z, y


def read_normal(file):
    x, y, z = struct.unpack('<fff', file.read(12))
    return -x, -z, -y


def read_face_pseudo_vertextable(file):
    point_id, normal_id = struct.unpack('<II', file.read(8))
    file.read(8) # dump embedded UV coordinates
    return point_id, normal_id


def read_face(file):
    count_sides = binary.read_ulong(file)
    vertex_tables = [read_face_pseudo_vertextable(file) for i in range(count_sides)] # should instead return the individual lists to avoid unecessary data
    
    if count_sides < 4:
        file.read(16) # dump null bytes
        
    file.read(4) # dump face flags
    texture = binary.read_asciiz(file)
    material = binary.read_asciiz(file)
    
    return vertex_tables, texture, material


# The 32-bit floats written to the P3D may have lost
# their normalization due to the precision loss, and
# this would cause blender to produce weird results.
def renormalize_vertex_normals(normals_dict):
    for i in normals_dict:
        normal = normals_dict[i]
        length = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
        
        if length == 0:
            continue
            
        coef = 1 / length
        normals_dict[i] = (normal[0] * coef, normal[1] * coef, normal[2] * coef)
    
    return normals_dict


def decode_selection_weight(weight):
    if weight == 0:
        return 0.0
    elif weight == 1:
        return 1.0
        
    value = (256 - weight) / 255
    
    if value > 1:
        return 0
        
    return value


def get_file_path(path, addon_prefs, extension = ""):
    path = utils.replace_slashes(path.strip().lower())
    
    if not addon_prefs.import_absolute:
        return path
    
    if path == "":
        return ""
    
    if os.path.splitext(path)[1].lower() != extension:
        path += extension
    
    if addon_prefs.import_absolute:
        root = addon_prefs.project_root.strip().lower()
        if not path.startswith(root):
            absPath = os.path.join(root, path)
            if os.path.exists(absPath):
                return absPath
    
    return path


def process_taggs(file, bm, additional_data, count_verts, count_faces, logger):
    count = 0
    named_selections = []
    named_properties = {}
    
    while True:
        file.read(1)
        tagg_name = binary.read_asciiz(file)
        tagg_length = binary.read_ulong(file)
        
        # EOF
        if tagg_name == "#EndOfFile#":
            if tagg_length != 0:
                raise IOError("Invalid EOF")
            break
            
        # Sharps
        elif tagg_name == "#SharpEdges#":
            sharp_edges = []
            
            for i in range(int(tagg_length / (4 * 2))):
                point1_id = binary.read_ulong(file)
                point2_id = binary.read_ulong(file)
                
                if point1_id != point2_id:
                    edge = bm.edges.get([bm.verts[point1_id], bm.verts[point2_id]])
                    if edge is not None:
                        sharp_edges.append(edge)
            
            for edge in bm.edges:
                edge.smooth = edge not in sharp_edges
        
        # Property
        elif tagg_name == "#Property#" and 'PROPS' in additional_data:
            if tagg_length != 128:
                raise IOError(f"Invalid named property length: {tagg_length}")
                
            key = binary.read_char(file, 64)
            value = binary.read_char(file, 64)
            
            if key not in named_properties:
                named_properties[key] = value
        
        # Mass
        elif tagg_name == "#Mass#" and 'MASS' in additional_data:
            massLayer = bm.verts.layers.float.new("a3ob_mass") # create new BMesh layer to store mass data
            for i in range(count_verts):
                mass = binary.read_float(file)
                bm.verts[i][massLayer] = mass
            
        # UV
        elif tagg_name == "#UVSet#" and 'UV' in additional_data:
            uv_id = binary.read_ulong(file)
            uv_layer = bm.loops.layers.uv.new(f"UVSet {uv_id}")
            
            for face in bm.faces:
                for loop in face.loops:
                    loop[uv_layer].uv = (binary.read_float(file), 1-binary.read_float(file))
            
            
        # Named selections
        elif not re.match("#.*#",tagg_name) and 'SELECTIONS' in additional_data:
            bm.verts.layers.deform.verify()
            named_selections.append(tagg_name)
            deform = bm.verts.layers.deform.active
            
            for i in range(count_verts):
                b = binary.read_byte(file)
                weight = decode_selection_weight(b)
                if b != 0:
                    bm.verts[i][deform][len(named_selections) - 1] = weight
                
            file.read(count_faces) # dump face selection data
            
        else:
            file.read(tagg_length) # dump all other TAGGs
            
        count += 1
            
    logger.step("Read TAGGs: %d" % count)
            
    return named_selections, named_properties


def process_materials(mesh, face_data_dict, material_dict, addon_prefs):
    blender_material_indices = {} # needed because otherwise materials and textures with same names, but in different folders may cause issues
    regex_procedural = "#\(.*?\)\w+\(.*?\)"
    regex_procedural_color = "#\(\s*argb\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)color\(\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,\s*(\d+.?\d*)\s*,([a-zA-Z]+)\)"
    
    for i in range(len(face_data_dict)):
        face_data = face_data_dict[i]
        texture_name = face_data[1].strip()
        material_name = face_data[2].strip()
        
        blender_material = None
        if (texture_name, material_name) in material_dict:
            blender_material = material_dict[(texture_name, material_name)]
        else:
            blender_material = bpy.data.materials.new(f"P3D: {os.path.basename(texture_name)} :: {os.path.basename(material_name)}")
            material_props = blender_material.a3ob_properties_material
                
            if re.match(regex_procedural, texture_name):
                tex = re.match(regex_procedural_color, texture_name)
                if tex:
                    material_props.texture_type = 'COLOR'
                    groups = tex.groups()
                    
                    try:
                        material_props.color_type = groups[4].upper()
                        material_props.color_value = (float(groups[0]), float(groups[1]), float(groups[2]), float(groups[3]))
                    except:
                        material_props.texture_type = 'CUSTOM'
                        material_props.color_raw = texture_name
                        
                else:
                    material_props.texture_type = 'CUSTOM'
                    material_props.color_raw = texture_name
            else:
                material_props.texture_path = get_file_path(texture_name, addon_prefs)
            
            material_props.material_path = get_file_path(material_name, addon_prefs)
            material_dict[(texture_name, material_name)] = blender_material
            
        if blender_material.name not in mesh.materials:
            mesh.materials.append(blender_material)
            blender_material_indices[blender_material] = len(mesh.materials) - 1

        material_index = blender_material_indices[blender_material]
            
        mesh.polygons[i].material_index = material_index
        
    return material_dict


def process_normals(mesh, face_data_dict, normals_dict):
    loop_normals = []
    for face in mesh.polygons:
        vertex_tables = face_data_dict[face.index][0]
        
        for i in face.loop_indices:
            loop = mesh.loops[i]
            vertex_index = loop.vertex_index
            
            for table in vertex_tables:
                if table[0] == vertex_index:
                    loop_normals.insert(i, normals_dict[table[1]])   
    
    mesh.normals_split_custom_set(loop_normals)


def group_lod_data(lod_objects, groupby = 'TYPE'):    
    collections = {}
    group_dict = data.lod_groups[groupby]
    
    for obj, resolution, _ in lod_objects:
        lod_index, _ = lodutils.get_lod_id(resolution)
        group_name = group_dict[lod_index]
        
        if group_name not in collections:
            collections[group_name] = bpy.data.collections.new(name=group_name)
            
        collections[group_name].objects.link(obj)
            
    return collections


def build_collections(lod_objects, operator, root_collection):
    if operator.enclose:
        root_collection = bpy.data.collections.new(name=os.path.basename(operator.filepath))
        bpy.context.scene.collection.children.link(root_collection)
    
    if operator.groupby == 'NONE':
        for item in lod_objects:
            root_collection.objects.link(item[0])
    else:
        colls = group_lod_data(lod_objects, operator.groupby)
            
        for group in colls.values():
            root_collection.children.link(group)


def transform_proxy(obj): # Align the object coordinate system with the proxy directions
    rotation_matrix = proxyutils.get_transform_rotation(obj)
    obj.data.transform(rotation_matrix)
    obj.matrix_world @= rotation_matrix.inverted()
    
    translate = mathutils.Matrix.Translation(-proxyutils.find_axis_vertices(obj.data)[0].co)
    obj.data.transform(translate)
    obj.matrix_world @= translate.inverted()
    
    obj.data.update()


def process_proxies(lod_data, operator, material_dict, dynamic_naming, addon_prefs):
    regex_proxy = "proxy:(.*)\.(\d{3})"
    regex_proxy_placeholder = "@proxy_(\d{4})"
    
    for obj, _, proxy_selections_dict in lod_data:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        
        for group in obj.vertex_groups:
            selection = group.name
            if not re.match(regex_proxy_placeholder, selection):
                continue
                
            obj.vertex_groups.active = group
            bpy.ops.object.vertex_group_select()
            
            try:
                bpy.ops.mesh.separate(type='SELECTED')
                obj.vertex_groups.remove(group)
            except:
                pass
            
        bpy.ops.object.mode_set(mode='OBJECT')
        
        proxy_objects = [proxy for proxy in bpy.context.selected_objects if proxy != obj]
        
        if operator.proxy_action == 'CLEAR':
            bpy.ops.object.delete({"selected_objects": proxy_objects})
            
        elif operator.proxy_action == 'SEPARATE':
            for proxy_obj in proxy_objects:
                proxy_obj.a3ob_properties_object.is_a3_lod = False
                proxy_obj.a3ob_properties_object_proxy.dynamic_naming = dynamic_naming
                
                transform_proxy(proxy_obj)
                structutils.cleanup_vertex_groups(proxy_obj)
                
                for group in proxy_obj.vertex_groups:
                    name = group.name
                    
                    if name not in proxy_selections_dict:
                        continue
                    
                    proxy_data = re.match(regex_proxy, proxy_selections_dict[name])
                    proxy_obj.vertex_groups.remove(group)
                    proxy_data_groups = proxy_data.groups()
                    proxy_obj.a3ob_properties_object_proxy.proxy_path = get_file_path(proxy_data_groups[0], addon_prefs, ".p3d")
                    proxy_obj.a3ob_properties_object_proxy.proxy_index = int(proxy_data_groups[1])
                
                proxy_obj.a3ob_properties_object_proxy.is_a3_proxy = True
                proxy_obj.data.materials.clear()
                proxy_obj.data.materials.append(material_dict[("", "")])
                proxy_obj.parent = obj
                
        bpy.ops.object.select_all(action='DESELECT')


def read_lod(context, file, material_dict, additional_data, dynamic_naming, logger, addon_prefs):
    logger.level_up()

    # Read LOD header
    signature = read_signature(file)
    if signature != "P3DM":
        raise IOError(f"Unsupported LOD signature: {signature}")
        
    version_major = binary.read_ulong(file)
    version_minor = binary.read_ulong(file)
    
    if version_major != 0x1c or version_minor != 0x100:
        raise IOError(f"Unsupported LOD version: {version_major}.{version_minor}")
        
    logger.step("Type: P3DM")
    logger.step(f"Version: {version_major}.{version_minor}")
                
    count_verts = binary.read_ulong(file)
    count_normals = binary.read_ulong(file)
    count_faces = binary.read_ulong(file)
    
    file.read(4) # dump unknown flag byte
    
    # Read vertex table
    vertices = [read_vertex(file) for i in range(count_verts)]
    logger.step("Read vertices: %d" % count_verts)
    
    # Read vertex normal table
    normals_dict = {i: read_normal(file) for i in range(count_normals)}
    logger.step("Read vertex normals: %d" % count_normals)
    
    # Read faces
    faces = []
    face_data_dict = {}
    for i in range(count_faces):
        new_face = read_face(file)
        faces.append([i[0] for i in new_face[0]])
        face_data_dict[i] = new_face
        
    logger.step("Read faces: %d" % count_faces)
    
    # Construct mesh
    mesh = bpy.data.meshes.new("Temp LOD")
    mesh.from_pydata(vertices, [], faces) # from_pydata is both faster than BMesh and does not break when fed invalid geometry
    mesh.update(calc_edges=True)
    
    for face in mesh.polygons:
        face.use_smooth = True
    
    # Apply split normals
    #
    # Split normals apparently also set up hard edges where necessary,
    # but due to a seemingly Blender specific phenomenon, random sharp
    # edges tend to appear where the loop vertices on both edges of an edge
    # have split normals. To combat this, the normals have to be processed
    # before the #SharpEdges# TAGG, so that the sharp edges get cleaned up
    # by the TAGG processing.
    if 'NORMALS' in additional_data:
        normals_dict = renormalize_vertex_normals(normals_dict)
        process_normals(mesh, face_data_dict, normals_dict)
        logger.step("Applied split normals")
        
    # Read TAGGs
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    taggSignature = read_signature(file)
    if taggSignature != "TAGG":
        raise IOError(f"Invalid TAGG section signature: {taggSignature}")
    
    named_selections, named_properties = process_taggs(file, bm, additional_data, count_verts, count_faces, logger)
    
    # EOF
    lod_resolution_signature = binary.read_float(file)
    logger.step("Resolution signature: %d" % lod_resolution_signature)
    
    # Create object
    lod_index, lod_resolution = lodutils.get_lod_id(lod_resolution_signature)
    lod_name = lodutils.format_lod_name(lod_index,lod_resolution)
    logger.step("Name: %s" % lod_name)
    
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(180)
    mesh.name = lod_name
    obj = bpy.data.objects.new(lod_name, mesh)
    
    # Setup LOD property
    object_props = obj.a3ob_properties_object
    object_props.dynamic_naming = dynamic_naming
    try:
        object_props.lod = str(lod_index)
    except:
        object_props.lod = "30"
        
    object_props.resolution = lod_resolution
    object_props.is_a3_lod = True
    
    # Add named properties
    for key in named_properties:
        item = object_props.properties.add()
        item.name = key
        item.value = named_properties[key]
    
    if len(named_properties) > 0:
        logger.step("Added named properties: %d" % len(named_properties))
    
    # Push to Mesh data
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    # Create materials
    if 'MATERIALS' in additional_data:
        material_dict = process_materials(mesh, face_data_dict, material_dict, addon_prefs)
        logger.step("Assigned materials")
        
    # Cleanup split normals if they are not needed
    if 'NORMALS' in additional_data and lod_index not in data.lod_visuals: 
        bpy.ops.mesh.customdata_custom_splitnormals_clear({"active_object": obj, "object": obj})
        
    # Add vertex group names to object
    #
    # Blender only allows vertex group names to have up to 63 characters.
    # Since proxy selection names (file paths) are often longer than that,
    # they have to be replaced by formatted placeholders and later looked up
    # from a dictionary when needed.
    regex_proxy = "proxy:(.*)\.(\d{3})"
    proxy_selections_dict = {}
    proxy_index = 0
    for name in named_selections:
        if re.match(regex_proxy, name):
            group_name = "@proxy_%04d" % proxy_index
            proxy_selections_dict[group_name] = name
            name = group_name
            proxy_index += 1
            
        obj.vertex_groups.new(name=name)
    
    if len(proxy_selections_dict) > 0:
        logger.step("Added proxy name place holders: %d" % len(proxy_selections_dict))
        
    if len(named_selections) > 0:
        logger.step("Added named selections: %d" % len(named_selections))
    
    logger.level_down()
    return obj, lod_resolution_signature, material_dict, proxy_selections_dict


def read_file(operator, context, file, first_lod_only = False):
    # If something is left selected in the scene, the proxy separation trips up with the operators
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
        
    context.view_layer.objects.active = None
    
    wm = context.window_manager
    wm.progress_begin(0, 1000)
    logger = ProcessLogger()
    logger.step("P3D import from %s" % operator.filepath)
    
    time_file_start = time.time()

    additional_data = set()
    if operator.additional_data_allowed:
        additional_data = operator.additional_data
    
    version, count_lod = read_file_header(file)
    if first_lod_only and count_lod > 1:
        count_lod = 1
    
    logger.log(f"File version: {version}")
    logger.log(f"Number of LODs: {count_lod}")
    
    if version != 257:
        raise IOError(f"Unsupported file version: {version}")
    
    lod_data = []
    
    material_dict = None
    if 'MATERIALS' in additional_data:
        material_dict = {
            ("", ""): bpy.data.materials.get("P3D: no material", bpy.data.materials.new("P3D: no material"))
        }
    
    logger.level_up()
    
    addon_prefs = utils.get_addon_preferences(context)
    for i in range(count_lod):
        time_lod_start = time.time()
        logger.step("LOD %d" % i)
        
        lod_object, lod_resolution, material_dict, proxy_selections_dict = read_lod(context, file, material_dict, additional_data, operator.dynamic_naming, logger, addon_prefs)

        if operator.validate_meshes:
            lod_object.data.validate(clean_customdata=False)
        
        lod_data.append((lod_object, lod_resolution, proxy_selections_dict))
        
        logger.log("Done in %f sec" % (time.time() - time_lod_start))
        wm.progress_update(i+1)
        
    logger.level_down()
    
    root_collection = context.scene.collection
    build_collections(lod_data, operator, root_collection)
    
    # Set up proxies
    if operator.proxy_action != 'NOTHING' and 'SELECTIONS' in additional_data:
        process_proxies(lod_data, operator, material_dict, operator.dynamic_naming, addon_prefs)
               
    logger.step("")
    logger.step("P3D Import finished in %f sec" % (time.time() - time_file_start))
    wm.progress_end()
    
    return lod_data