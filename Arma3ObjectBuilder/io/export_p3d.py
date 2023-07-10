import time
import struct

import bpy
import bmesh

from . import binary_handler as binary
from ..utilities import generic as utils
from ..utilities import lod as lodutils
from ..utilities import data
from ..utilities.logger import ProcessLogger


# may be worth looking into bpy.ops.object.convert(target='MESH') instead to reduce operator calls
def apply_modifiers(obj, context):
    ctx = context.copy()
    ctx["object"] = obj
    
    for m in obj.modifiers:
        try:
            ctx["modifier"] = m
            bpy.ops.object.modifier_apply(ctx, modifier=m.name)
        except:
            obj.modifiers.remove(m)


def merge_objects(main_object, sub_objects, context):
    ctx = context.copy()
    ctx["active_object"] = main_object
    ctx["selected_objects"] = (sub_objects + [main_object])
    ctx["selected_editable_objects"] = (sub_objects + [main_object])
    
    bpy.ops.object.join(ctx)


def duplicate_object(obj):
    new_object = obj.copy()
    new_object.data = obj.data.copy()
    return new_object


def get_texture_string(material_properties, addon_prefs):
    texture_type = material_properties.texture_type
    
    if texture_type == 'TEX':
        return format_path(material_properties.texture_path, addon_prefs.project_root, addon_prefs.export_relative)
    elif texture_type == 'COLOR':
        color = material_properties.color_value
        return f"#(argb,8,8,3)color({round(color[0],3)},{round(color[1],3)},{round(color[2],3)},{round(color[3],3)},{material_properties.color_type})"
    elif texture_type == 'CUSTOM':
        return material_properties.color_raw
    else:
        return ""


def get_material_string(material_properties, addon_prefs):
    return format_path(material_properties.material_path, addon_prefs.project_root, addon_prefs.export_relative)


def get_proxy_string(proxy_props, addon_prefs):
    path = format_path(proxy_props.proxy_path, addon_prefs.project_root, addon_prefs.export_relative, True)
    if len(path) > 0 and path[0] != "\\":
        path = "\\" + path
        
    return f"proxy:{path}.{'%03d' % proxy_props.proxy_index}"


def format_path(path, root = "", make_relative = True, strip_extension = False):
    path = utils.replace_slashes(path.strip())
    
    if make_relative:
        root = utils.replace_slashes(root.strip())
        path = utils.make_relative(path, root)
        
    if strip_extension:
        path = utils.strip_extension(path)
        
    return path


def get_lod_data(operator, context):
    addon_prefs = utils.get_addon_preferences(context)
    scene = context.scene
    export_objects = scene.objects
    
    if operator.use_selection:
        export_objects = context.selected_objects
    
    lod_list = []
    for obj in export_objects:
        lod_item = []
        
        if obj.type != 'MESH' or not obj.a3ob_properties_object.is_a3_lod or obj.parent != None or obj.a3ob_properties_object.lod == '30':
            continue
            
        main_object = duplicate_object(obj)
        
        if operator.apply_modifiers:
            apply_modifiers(main_object, context)
        
        children = obj.children
        
        sub_objects = []
        object_proxies = {}
        for i, child in enumerate(children):
            if obj.type != 'MESH':
                continue
                
            sub_object = duplicate_object(child)
            object_props = sub_object.a3ob_properties_object_proxy
            if object_props.is_a3_proxy:
                placeholder = "@proxy_%04d" % i
                utils.create_selection(sub_object, placeholder)
                object_proxies[placeholder] = get_proxy_string(object_props, addon_prefs)
            
            if operator.apply_modifiers:
                apply_modifiers(sub_object, context)
            
            sub_objects.append(sub_object)
            
        if len(sub_objects) > 0:
            merge_objects(main_object, sub_objects, context)
        
        for obj in sub_objects:
            bpy.data.meshes.remove(obj.data, do_unlink=True)
        
        if operator.apply_transforms:
            bpy.ops.object.transform_apply({"active_object": main_object, "selected_editable_objects": [main_object]}, location = True, scale = True, rotation = True)
        
        if operator.validate_meshes:
            main_object.data.validate(clean_customdata=False)
            
        if not operator.preserve_normals:
            ctx = context.copy()
            ctx["active_object"] = main_object
            ctx["object"] = main_object
            
            bpy.ops.mesh.customdata_custom_splitnormals_clear(ctx)
        
        lod_item.append(main_object)
        lod_item.append(object_proxies)
        
        object_materials = {0: ("", "")}
        translucency = {0: False}
        
        for i, slot in enumerate(main_object.material_slots):
            mat = slot.material
            if mat:
                object_materials[i] = (get_texture_string(mat.a3ob_properties_material, addon_prefs), get_material_string(mat.a3ob_properties_material, addon_prefs))
                translucency[i] = mat.a3ob_properties_material.translucent
            else:
                object_materials[i] = ("", "")
                translucency[i] = False
                
        lod_item.append(object_materials)
        lod_list.append(lod_item)
                
        bm = bmesh.new()
        bm.from_mesh(main_object.data)
        bm.faces.ensure_lookup_table()
        
        index_offset = len(bm.faces) - 1
        count_translucent = 0
        for face in bm.faces:
            if translucency[face.material_index]:
                face.index = index_offset + count_translucent
                count_translucent += 1
                
        bm.faces.sort()
        bm.to_mesh(main_object.data)
        bm.free()
    
    return lod_list


def can_export(operator, context):
    scene = context.scene
    export_objects = scene.objects
    
    if operator.use_selection:
        export_objects = context.selected_objects
        
    for obj in export_objects:
        if obj.type == 'MESH' and obj.a3ob_properties_object.is_a3_lod and obj.parent == None and obj.a3ob_properties_object.lod != '30':
            return True
            
    return False


def get_resolution(obj):
    object_props = obj.a3ob_properties_object
    return lodutils.get_lod_signature(int(object_props.lod), object_props.resolution)


def encode_selection_weight(weight):
    if weight == 0:
        return 0
    elif weight  == 1:
        return 1
        
    value = round(256 - 255 * weight)
    
    if value == 256:
        return 0
        
    return value


def write_vertex(file, co, flag = 0):
    file.write(struct.pack('<fff', co[0], co[2], co[1]))
    binary.write_ulong(file, flag)


def write_normal(file, normal):
    file.write(struct.pack('<fff', -normal[0], -normal[2], -normal[1]))


def write_face_pseudo_vertextable(file, loop, uv_layer):
    binary.write_ulong(file,loop.vert.index)
    binary.write_ulong(file,loop.index)
    
    if not uv_layer:
        file.write(struct.pack('<ff', 0, 0))
    
    file.write(struct.pack('<ff', loop[uv_layer].uv[0], 1-loop[uv_layer].uv[1]))


def write_face(file, bm, face, materials, uv_layer):
    count_sides = len(face.loops)
    binary.write_ulong(file, count_sides)
    
    for i in range(count_sides):
        write_face_pseudo_vertextable(file, face.loops[i], uv_layer)
        
    if count_sides < 4:
        file.write(struct.pack('<4I', 0, 0, 0, 0)) # empty filler for triangles
    
    material_data = materials[face.material_index]
    binary.write_ulong(file, 0) # face flags
    binary.write_asciiz(file, material_data[0]) # texture
    binary.write_asciiz(file, material_data[1]) # material


def write_tagg_sharps_edges(file, bm):
    binary.write_byte(file, 1)
    binary.write_asciiz(file, "#SharpEdges#")
    data_start_pos = file.tell()
    binary.write_ulong(file, 0) # temporary placeholder value for field length
    
    flat_face_edges = set()
    
    for face in bm.faces:
        if not face.smooth:
            flat_face_edges.update({edge for edge in face.edges})
    
    for edge in bm.edges:
        if not edge.smooth or edge in flat_face_edges:
            file.write(struct.pack('<II', edge.verts[0].index, edge.verts[1].index))

    data_end_pos = file.tell()
    file.seek(data_start_pos, 0)
    binary.write_ulong(file, data_end_pos-data_start_pos-4) # fill in length data
    file.seek(data_end_pos, 0)


def write_tagg_uv_sets_item(file, bm, layer, index):
    binary.write_byte(file, 1)
    binary.write_asciiz(file, "#UVSet#")
    data_start_pos = file.tell()
    binary.write_ulong(file, 0) # temporary placeholder value for field length
    binary.write_ulong(file, index)
    
    for face in bm.faces:
        for loop in face.loops:
            file.write(struct.pack('<ff', loop[layer].uv[0], 1-loop[layer].uv[1]))
        
    data_end_pos = file.tell()
    file.seek(data_start_pos, 0)
    binary.write_ulong(file, data_end_pos-data_start_pos-4) # fill in length data
    file.seek(data_end_pos, 0)


def write_tagg_uv_sets(file, bm, logger):
    index = 0
    for layer in bm.loops.layers.uv.values():
        write_tagg_uv_sets_item(file, bm, layer, index)
        index += 1
        
    logger.step("Wrote UV sets: %d" % index)


def write_tagg_mass(file, bm, count_verts):
    layer = bm.verts.layers.float.get("a3ob_mass")
    
    if not layer:
        return
        
    binary.write_byte(file, 1)
    binary.write_asciiz(file, "#Mass#")
    binary.write_ulong(file, count_verts*4)
    
    for vertex in bm.verts:
        binary.write_float(file, vertex[layer])


def write_tagg_selections_item(file, name, count_vert, count_face, vertices, faces, proxies):
    real_name = name
    
    if name.strip().startswith("@proxy"):
        try:
            real_name = proxies[name]
        except:
            pass
            
    binary.write_byte(file, 1)
    binary.write_asciiz(file, real_name)
    data_start_pos = file.tell()
    binary.write_ulong(file, 0) # temporary placeholder value for field length

    bytes_vert = bytearray(count_vert) # array of 0x0 bytes (effective because this way not every vertex has to be iterated)
    for vertex in vertices:
        bytes_vert[vertex[0]] = encode_selection_weight(vertex[1])
        
    file.write(bytes_vert)

    bytes_face = bytearray(count_face)
    for face in faces:
        bytes_face[face] = 1
        
    file.write(bytes_face)

    data_end_pos = file.tell()
    file.seek(data_start_pos, 0)
    binary.write_ulong(file, data_end_pos-data_start_pos-4) # fill in length data
    file.seek(data_end_pos, 0)


def write_tagg_selections(file, obj, proxies, logger):
    mesh = obj.data
    
    # Build selection database for faster lookup
    selections_vert = {}
    selections_face = {}
    
    for group in obj.vertex_groups:
        selections_vert[group.name] = set()
        selections_face[group.name] = set()
    
    for vertex in mesh.vertices:
        for group in vertex.groups:
            name = obj.vertex_groups[group.group].name
            weight = group.weight
            selections_vert[name].add((vertex.index, weight))
            
    for face in mesh.polygons:
        groups = set([group.group for vertex in face.vertices for group in mesh.vertices[vertex].groups])
        for group_id in groups:
            weight = sum([group.weight for vertex in face.vertices for group in mesh.vertices[vertex].groups if group.group == group_id])
            if weight > 0:
                name = obj.vertex_groups[group_id].name
                selections_face[name].add(face.index)
    
    count_vert = len(mesh.vertices)
    count_face = len(mesh.polygons)
    
    for i, group in enumerate(obj.vertex_groups):
        name = group.name
        write_tagg_selections_item(file, name, count_vert, count_face, selections_vert[name], selections_face[name], proxies)
        
    logger.step("Wrote named selections: %d" % (i + 1))


def write_tagg_named_properties_item(file, key, value):
    binary.write_byte(file, 1)
    binary.write_asciiz(file, "#Property#")
    binary.write_ulong(file, 128)
    file.write(struct.pack('<64s', key.encode('ASCII')))
    file.write(struct.pack('<64s', value.encode('ASCII')))


def write_tagg_named_properties(file, obj):
    object_props = obj.a3ob_properties_object
    written_props = set()
    for prop in object_props.properties:
        if prop.name not in written_props:
            written_props.add(prop.name)
            write_tagg_named_properties_item(file, prop.name, prop.value)


def write_file_header(file, count_lod):
    binary.write_chars(file, "MLOD")
    binary.write_ulong(file, 257)
    binary.write_ulong(file, count_lod)


def write_lod(file, obj, materials, proxies, logger):
    logger.level_up()
    
    for face in obj.data.polygons:
        if len(face.vertices) > 4:
            logger.step("N-gons detected -> skipping lod")
            logger.level_down()
            return False
    
    binary.write_chars(file, "P3DM")
    binary.write_ulong(file, 0x1c)
    binary.write_ulong(file, 0x100)
    
    if obj.mode == 'EDIT':
        obj.update_from_editmode()
        
    mesh = obj.data
    mesh.calc_normals_split()
    
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    count_verts = len(mesh.vertices)
    count_loops = len(mesh.loops)
    count_faces = len(mesh.polygons)
    
    binary.write_ulong(file, count_verts)
    binary.write_ulong(file, count_loops) # number of normals
    binary.write_ulong(file, count_faces)
    binary.write_ulong(file, 0) # unknown flags/padding
    
    vertex_flag = 33554432
    if obj.a3ob_properties_object.normals_flag == 'AVG':
        vertex_flag = 0
    
    for vert in bm.verts:
        write_vertex(file, vert.co, vertex_flag)
        
    logger.step("Wrote veritces: %d" % count_verts)
        
    for loop in mesh.loops:
        write_normal(file, loop.normal)
        
    logger.step("Wrote vertex normals: %d" % count_loops)
        
    first_uv_layer = None
    if len(bm.loops.layers.uv.values()) > 0: # 1st UV set needs to be written into the face data section too
        first_uv_layer = bm.loops.layers.uv.values()[0]
        
    for face in bm.faces:
        write_face(file, bm, face, materials, first_uv_layer)
        
    logger.step("Wrote faces: %d" % count_faces)
        
    binary.write_chars(file, "TAGG") # TAGG section start
    
    write_tagg_sharps_edges(file, bm)
    write_tagg_uv_sets(file, bm, logger)
    
    if obj.a3ob_properties_object.lod == '6':
        write_tagg_mass(file, bm, count_verts) # need to make sure to only export for Geo LODs
        logger.step("Wrote vertex mass")
        
    bm.free()
        
    write_tagg_named_properties(file, obj)
    
    if len(obj.vertex_groups) > 0:
        write_tagg_selections(file, obj, proxies, logger)
    
    binary.write_byte(file, 1)
    binary.write_asciiz(file, "#EndOfFile#") # EOF signature
    binary.write_ulong(file, 0)
    binary.write_float(file,get_resolution(obj)) # LOD resolution index
    
    logger.step("Resolution signature: %d" % float(get_resolution(obj)))
    logger.step("Name: %s" % f"{data.lod_type_names[int(obj.a3ob_properties_object.lod)][0]} {obj.a3ob_properties_object.resolution}")
    
    logger.level_down()
    
    return True


def write_file(operator, context, file):
    wm = context.window_manager
    wm.progress_begin(0, 1000)
    logger = ProcessLogger()
    logger.step("P3D export to %s" % operator.filepath)
    
    time_file_start = time.time()
    
    lod_list = get_lod_data(operator, context)
    lod_list.sort(key=lambda lod: get_resolution(lod[0]))
    
    count_lod = len(lod_list)
    
    logger.log("Detected %d LOD objects" % count_lod)
    
    write_file_header(file,count_lod)
    
    logger.level_up()
    
    exported_count = 0
    for i, lod in enumerate(lod_list):
        time_lod_start = time.time()
        logger.step("LOD %d" % i)
        
        success = write_lod(file, lod[0], lod[2], lod[1], logger)
        if success:
            exported_count += 1
            
        bpy.data.meshes.remove(lod[0].data, do_unlink=True)
        
        logger.log("Done in %f sec" % (time.time() - time_lod_start))
        wm.progress_update(i+1)
        
    logger.level_down()
    logger.step("")
    logger.step("P3D export finished in %f sec" % (time.time() - time_file_start))
    wm.progress_end()
    
    return count_lod,exported_count