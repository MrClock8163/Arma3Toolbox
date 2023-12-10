import time

import bpy
import bmesh

from . import data_p3d as p3d
from ..utilities import generic as utils
from ..utilities import lod as lodutils
from ..utilities import flags as flagutils
from ..utilities import compat as computils
from ..utilities import errors
from ..utilities.logger import ProcessLogger


# Simple check to not even start the export if there are
# no LOD objects in the scene.
def can_export(operator, context):
    scene = context.scene
    export_objects = scene.objects
    
    if operator.use_selection:
        export_objects = context.selected_objects
        
    for obj in export_objects:
        if (not operator.visible_only or obj.visible_get()) and  obj.type == 'MESH' and obj.a3ob_properties_object.is_a3_lod and obj.parent == None and obj.a3ob_properties_object.lod != '30':
            return True
            
    return False


def duplicate_object(obj):
    new_object = obj.copy()
    new_object.data = obj.data.copy()
    return new_object


# May be worth looking into bpy.ops.object.convert(target='MESH')
# instead to reduce operator calls.
def apply_modifiers(obj):
    ctx = {"object": obj}
    
    for m in obj.modifiers:
        try:
            ctx["modifier"] = m
            computils.call_operator_ctx(bpy.ops.object.modifier_apply, ctx, modifier= m.name)
        except:
            obj.modifiers.remove(m)


# Maybe transfer to the object props PG as a method?
def get_resolution(obj):
    object_props = obj.a3ob_properties_object
    return lodutils.get_lod_signature(int(object_props.lod), object_props.resolution)


# In order to simplify merging the LOD parts, and the data access later on, the dereferenced
# flags need to be written directly into their respective integer bmesh layers.
def bake_flags_vertex(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()

    layer = flagutils.get_layer_flags_vertex(bm)
    if layer:
        flags_vertex = {i: item.get_flag() for i, item in enumerate(obj.a3ob_properties_object_flags.vertex)}
        for vert in bm.verts:
            vert[layer] = flags_vertex.get(vert[layer], 0)
    
    bm.to_mesh(obj.data)
    bm.free()


def bake_flags_face(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    layer = flagutils.get_layer_flags_face(bm)
    if layer:
        flags_face = {i: item.get_flag() for i, item in enumerate(obj.a3ob_properties_object_flags.face)}
        for face in bm.faces:
            face[layer] = flags_face.get(face[layer], 0)
    
    bm.to_mesh(obj.data)
    bm.free()


def merge_into_lod(operator, main_object, sub_objects, proxy_objects):
    proxy_lookup = {}
    for i, proxy in enumerate(proxy_objects):
        placeholder = "@proxy_%d" % i
        utils.create_selection(proxy, placeholder)
        proxy_lookup[placeholder] = proxy.a3ob_properties_object_proxy.to_placeholder()

    all_objects = sub_objects + proxy_objects + [main_object]
    for obj in all_objects:
        bake_flags_face(obj)
        bake_flags_vertex(obj)

        if operator.apply_modifiers:
            apply_modifiers(obj)

    if len(all_objects) > 1:
        ctx = {
            "active_object": main_object,
            "selected_objects": all_objects,
            "selected_editable_objects": all_objects
        }
        computils.call_operator_ctx(bpy.ops.object.join, ctx)
    
    # Duplicate cleanup
    for obj in (sub_objects + proxy_objects):
        bpy.data.meshes.remove(obj.data, do_unlink=True)

    return proxy_lookup


def get_lod_data(operator, context):
    scene = context.scene
    export_objects = scene.objects

    if operator.use_selection:
        export_objects = context.selected_objects

    lod_list = []

    for obj in [obj for obj in export_objects if not operator.visible_only or obj.visible_get()]:       
        if obj.type != 'MESH' or not obj.a3ob_properties_object.is_a3_lod or obj.parent != None or obj.a3ob_properties_object.lod == '30':
            continue
            
        # Some operator polls fail later if an object is in edit mode.
        if not obj.mode == 'OBJECT':
            computils.call_operator_ctx(bpy.ops.object.mode_set, {"active_object": obj}, mode='OBJECT')
        
        main_obj = duplicate_object(obj)

        sub_objects = []
        proxy_objects = []
        for child in obj.children:
            if child.type != 'MESH':
                continue
                
            if not child.mode == 'OBJECT':
                computils.call_operator_ctx(bpy.ops.object.mode_set, {"active_object": obj}, mode='OBJECT')
            
            child_copy = duplicate_object(child)

            if child_copy.a3ob_properties_object_proxy.is_a3_proxy:
                proxy_objects.append(child_copy)
            else:
                sub_objects.append(child_copy)
        
        proxy_lookup = merge_into_lod(operator, main_obj, sub_objects, proxy_objects)

        if operator.apply_transforms:
            ctx = {
                "active_object": main_obj,
                "selected_editable_objects": [main_obj]
            }
            computils.call_operator_ctx(bpy.ops.object.transform_apply, ctx, location = True, scale = True, rotation = True)
        
        if operator.validate_meshes:
            main_obj.data.validate(clean_customdata=False)
            
        if not operator.preserve_normals:
            ctx = {
                "active_object": main_obj,
                "object": main_obj
            }
            computils.call_operator_ctx(bpy.ops.mesh.customdata_custom_splitnormals_clear, ctx)

        if operator.sort_sections:
            sections = {0: []}
            for slot in main_obj.material_slots:
                sections[slot.slot_index] = []

            bm = bmesh.new()
            bm.from_mesh(main_obj.data)
            bm.faces.ensure_lookup_table()

            for face in bm.faces:
                sections[face.material_index].append(face)
            
            face_index = 0
            for section in sections.values():
                for face in section:
                    face.index = face_index
                    face_index -=- 1

            bm.faces.sort()
            bm.to_mesh(main_obj.data)
            bm.free()

        lod_list.append((main_obj, proxy_lookup))

    return lod_list


def process_vertices(bm):
    layer = flagutils.get_layer_flags_vertex(bm)

    output = {}

    for vert in bm.verts:
        output[vert.index] = (*vert.co, vert[layer])

    return output


def process_normals(mesh):
    output = {}
    normals_index = {}
    normals_lookup_dict = {}

    for i, loop in enumerate(mesh.loops):
        normal = loop.normal.copy().freeze()
        
        if normal not in normals_index:
            normals_index[normal] = len(normals_index)
            output[len(output)] = normal
        
        normals_lookup_dict[i] = normals_index[normal]
    
    return output, normals_lookup_dict


def process_materials(obj):
    output = {0: ("", "")}

    for i, slot in enumerate(obj.material_slots):
        mat = slot.material
        if mat:
            output[i] = mat.a3ob_properties_material.to_p3d()
        else:
            output[i] = ("", "")

    return output


def process_faces(obj, bm, normals_lookup):
    output = {}
    materials = process_materials(obj)

    uv_layer = None
    if len(bm.loops.layers.uv.values()) > 0: # 1st UV set needs to be written into the face data section too
        uv_layer = bm.loops.layers.uv.values()[0]
    
    flag_layer = flagutils.get_layer_flags_face(bm)
    
    for face in bm.faces:
        verts = []
        normals = []
        uvs = []

        for loop in face.loops:
            verts.append(loop.vert.index)
            normals.append(normals_lookup[loop.index])
            uvs.append((loop[uv_layer].uv[0], 1 - loop[uv_layer].uv[1]) if uv_layer else (0, 0))

        output[face.index] = (verts, normals, uvs, *materials[face.material_index], face[flag_layer])

    return output


def process_tagg_sharp(bm):
    output = p3d.P3D_TAGG()
    output.name = "#SharpEdges#"
    output.data = p3d.P3D_TAGG_DataSharpEdges()

    flat_face_edges = set()
    for face in bm.faces:
        if not face.smooth:
            flat_face_edges.update({edge for edge in face.edges})
    
    for edge in bm.edges:
        if not edge.smooth or edge in flat_face_edges:
            output.data.edges.append((edge.verts[0].index, edge.verts[1].index))

    return output


def process_tagg_uvset(bm, layer):
    output = p3d.P3D_TAGG()
    output.name = "#UVSet#"
    output.data = p3d.P3D_TAGG_DataUVSet()
    uvs = {}

    for face in bm.faces:
        for loop in face.loops:
            uvs[loop.index] = (loop[layer].uv[0], loop[layer].uv[1])

    output.data.uvs = dict(sorted(uvs.items()))

    return output


def process_tagg_property(prop):
    output = p3d.P3D_TAGG()
    output.name = "#Property#"
    output.data = p3d.P3D_TAGG_DataProperty()
    output.data.key = prop.name
    output.data.value = prop.value

    return output


def process_tagg_mass(bm, layer):
    output = p3d.P3D_TAGG()
    output.name = "#Mass#"
    output.data = p3d.P3D_TAGG_DataMass()

    for vert in bm.verts:
        output.data.masses[vert.index] = vert[layer]

    return output


def process_taggs_selections(obj, bm):
    output = {}

    for i, group in enumerate(obj.vertex_groups):
        new_tagg = p3d.P3D_TAGG()
        new_tagg.name = group.name
        new_tagg.data = p3d.P3D_TAGG_DataSelection()
        new_tagg.data.count_verts = len(bm.verts)
        new_tagg.data.count_faces = len(bm.faces)
        output[i] = new_tagg

    bm.verts.layers.deform.verify()
    layer = bm.verts.layers.deform.active

    for vert in bm.verts:
        for idx in vert[layer].keys():
            output[idx].data.weight_verts[vert.index] = vert[layer][idx]
    
    for face in bm.faces:
        indices = [idx for vert in face.verts for idx in vert[layer].keys()]
        unique = set(indices)
        for idx in unique:
            if indices.count(idx) == len(face.loops):
                output[idx].data.weight_faces[face.index] = 1

    return output.values()


def process_taggs(obj, bm, logger):
    object_props = obj.a3ob_properties_object
    taggs = [process_tagg_sharp(bm)]
    logger.log("Collected sharp edges")

    uv_index = 0
    for layer in bm.loops.layers.uv.values():
        uvset = process_tagg_uvset(bm, layer)
        uvset.data.id = uv_index
        taggs.append(uvset)
        uv_index += 1
    logger.log("Collected UV sets")
    
    for prop in object_props.properties:
        taggs.append(process_tagg_property(prop))
    logger.log("Collected named properties")

    if object_props.lod == '6':
        layer = bm.verts.layers.float.get("a3ob_mass")
        if layer:
            taggs.append(process_tagg_mass(bm, layer))
            logger.log("Collected vertex masses")

    taggs.extend(process_taggs_selections(obj, bm))
    logger.log("Collected selections")

    return taggs


def process_lod(obj, proxy_lookup, validator, logger):
    lod_name = obj.a3ob_properties_object.get_name()

    logger.level_up()
    logger.step("Name: %s" % lod_name)
    logger.step("Processing data:")

    if lodutils.Validator.has_ngons(obj.data):
        logger.log("N-gons detected -> skipping LOD")
        logger.level_down()
        return None

    if validator:
        validator.lod = obj
        if not validator.validate(obj.a3ob_properties_object.lod):
            logger.log("Failed validation -> skipping LOD (run manual validation for details)")
            logger.level_down()
            return None

    output = p3d.P3D_LOD()
    output.signature = "P3DM"
    output.version = (0x1c, 0x100)
    output.resolution = get_resolution(obj)

    mesh = obj.data
    mesh.calc_normals_split()

    normals, normals_lookup_dict = process_normals(mesh)
    output.normals = normals
    logger.log("Collected vertex normals")

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    output.verts = process_vertices(bm)
    logger.log("Collected vertices")
    output.faces = process_faces(obj, bm, normals_lookup_dict)
    logger.log("Collected faces")
    output.taggs = process_taggs(obj, bm, logger)

    bm.free()

    output.placeholders_to_proxies(proxy_lookup)
    logger.log("Finalized proxy selection names")

    logger.step("File report:")
    logger.log("Signature: %d" % output.resolution)
    logger.log("Type: P3DM")
    logger.log("Version: 28.256")
    logger.log("Vertices: %d" % len(output.verts))
    logger.log("Normals: %d" % len(output.normals))
    logger.log("Faces: %d" % len(output.faces))
    logger.log("Taggs: %d" % (len(output.taggs) + 1))

    logger.level_down()

    return output


def write_file(operator, context, file):
    wm = context.window_manager
    wm.progress_begin(0, 1000)
    wm.progress_update(0)
    
    validator = None
    if operator.validate_lods:
        validator = lodutils.Validator(None, operator.validate_lods_warnings_errors, True)
    
    logger = ProcessLogger()
    logger.step("P3D export to %s" % operator.filepath)

    time_file_start = time.time()

    lod_list = get_lod_data(operator, context)
    
    logger.log("Preprocessing done in %f sec" % (time.time() - time_file_start))
    logger.log("Detected %d LOD objects" % len(lod_list))

    mlod = p3d.P3D_MLOD()
    mlod.version = 257
    mlod.signature = "MLOD"
    logger.log("File version: %d" % 257)

    logger.log("Processing LOD data:")
    logger.level_up()

    mlod_lods = []
    for i, (lod, proxy_lookup) in enumerate(lod_list):
        time_lod_start = time.time()
        logger.step("LOD %d" % (i + 1))

        new_lod = process_lod(lod, proxy_lookup, validator, logger)
        if new_lod:
            mlod_lods.append(new_lod)
        bpy.data.meshes.remove(lod.data, do_unlink=True)

        logger.log("Done in %f sec" % (time.time() - time_lod_start))
        wm.progress_update(i + 1)

    mlod_lods.sort(key=lambda lod: lod.resolution)
    mlod.lods = mlod_lods

    mlod.write(file)
    
    logger.level_down()
    logger.step("P3D export finished in %f sec" % (time.time() - time_file_start))

    return len(lod_list), len(mlod_lods)