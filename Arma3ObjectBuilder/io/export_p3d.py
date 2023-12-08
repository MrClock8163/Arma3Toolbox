import time
import struct

import bpy
import bmesh

from . import binary_handler as binary
from . import data_p3d as p3d
from ..utilities import generic as utils
from ..utilities import lod as lodutils
from ..utilities import flags as flagutils
from ..utilities import compat as computils
from ..utilities import data
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


def get_resolution(obj):
    object_props = obj.a3ob_properties_object
    return lodutils.get_lod_signature(int(object_props.lod), object_props.resolution)


def get_lod_data(operator, context):
    addon_prefs = utils.get_addon_preferences()
    scene = context.scene
    export_objects = scene.objects

    if operator.use_selection:
        export_objects = context.selected_objects

    lod_list = []

    for obj in [obj for obj in export_objects if not operator.visible_only or obj.visible_get()]:
        # lod_item = []
        
        if obj.type != 'MESH' or not obj.a3ob_properties_object.is_a3_lod or obj.parent != None or obj.a3ob_properties_object.lod == '30':
            continue
        
        lod_list.append(duplicate_object(obj))


    return lod_list


def process_flags_vertex(obj):
    return {i: flag.get_flag() for i, flag in enumerate(obj.a3ob_properties_object_flags.vertex)}


def process_vertices(obj, bm):
    flag_groups = process_flags_vertex(obj)
    layer = flagutils.get_layer_flags_vertex(bm)

    output = {}

    for vert in bm.verts:
        output[vert.index] = (*vert.co, flag_groups.get(vert[layer], 0))

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


def process_flags_face(obj):
    return {i: flag.get_flag() for i, flag in enumerate(obj.a3ob_properties_object_flags.face)}


def process_faces(obj, bm, normals_lookup):
    output = {}
    materials = process_materials(obj)
    flags = process_flags_face(obj)

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

        output[face.index] = (verts, normals, uvs, *materials[face.material_index], flags.get(face[flag_layer], 0))

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


# def process_tagg_selection_item(obj, bm):
#     pass


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


def process_taggs(obj, bm):
    object_props = obj.a3ob_properties_object
    taggs = [process_tagg_sharp(bm)]

    uv_index = 0
    for layer in bm.loops.layers.uv.values():
        uvset = process_tagg_uvset(bm, layer)
        uvset.data.id = uv_index
        taggs.append(uvset)
        uv_index += 1
    
    for prop in object_props.properties:
        taggs.append(process_tagg_property(prop))
    
    if object_props.lod == '6':
        layer = bm.verts.layers.float.get("a3ob_mass")
        if layer:
            taggs.append(process_tagg_mass(bm, layer))
    
    taggs.extend(process_taggs_selections(obj, bm))


    return taggs


def process_lod(obj):
    output = p3d.P3D_LOD()
    output.signature = "P3DM"
    output.version = (0x1c, 0x100)
    output.resolution = get_resolution(obj)

    mesh = obj.data
    mesh.calc_normals_split()

    normals, normals_lookup_dict = process_normals(mesh)
    output.normals = normals

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    output.verts = process_vertices(obj, bm)
    output.faces = process_faces(obj, bm, normals_lookup_dict)
    output.taggs = process_taggs(obj, bm)

    bm.free()

    return output


def write_file(operator, context, file):
    time_file_start = time.time()

    lod_list = get_lod_data(operator, context)
    lod_list.sort(key=lambda lod: get_resolution(lod))

    mlod = p3d.P3D_MLOD()
    mlod.version = 257
    mlod.signature = "MLOD"

    mlod_lods = []
    for lod in lod_list:
        mlod_lods.append(process_lod(lod))
    
    mlod.lods = mlod_lods

    mlod.write(file)

    print("P3D export finished in %f sec" % (time.time() - time_file_start))

    return len(lod_list), len(mlod_lods)