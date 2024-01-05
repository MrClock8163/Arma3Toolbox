

import bpy
from mathutils import Vector

from . import data_p3d
from . import import_mcfg as mcfg


def vector_average(vectors):
    result = Vector()
    if len(vectors) == 0:
        return result
    
    for vec in vectors:
        result += vec
    
    return result / len(vectors)


def extract_pivot_coords(lod):
    pivot_points = {}
    for tagg in lod.taggs:
        if not tagg.is_selection():
            continue

        data = tagg.data
        if len(data.weight_verts) < 1:
            continue

        vert_idx = list(data.weight_verts.keys())[0]
        vert_co = lod.verts[vert_idx][0:3]

        pivot_points[tagg.name.lower()] = Vector(vert_co)
        
    return pivot_points


def read_pivots(pivots_path):
    p3d_data = data_p3d.P3D_MLOD.read_file(pivots_path)
    pivots = extract_pivot_coords(p3d_data.lods[0])

    return pivots


def read_bones(mcfg_path, skeleton_name):
    mcfg_data = mcfg.read_mcfg(mcfg_path)
    if not mcfg_data:
        return []
    
    bones_compiled = mcfg.get_bones_compiled(mcfg_data, skeleton_name)
    
    return bones_compiled


def filter_bones(bones, pivots):
    return [bone for bone in bones if bone.name.lower() in pivots]


def force_lowercase_bones(bones):
    return [bone.to_lowercase() for bone in bones]


def build_bone_hierarchy(parent, bones):
    hierarchy = {}

    for item in bones:
        if item.parent.lower() != parent.lower():
            continue

        hierarchy[item.name] = build_bone_hierarchy(item.name, bones)

    return hierarchy


def build_bones(armature, parent, hierarchy, pivot_points):
    for item in hierarchy:
        children = hierarchy[item]

        bone = armature.edit_bones.new(item)
        bone.head = pivot_points[item.lower()]

        tail = Vector((0, 0, 1))
        if len(children) > 0:
            tail = vector_average([pivot_points[child.lower()] for child in children])
        elif parent.lower() in pivot_points:
            tail_offset = (pivot_points[item.lower()] - pivot_points[parent.lower()]).length
            tail = bone.head + Vector((0, 0, 1)) * tail_offset

        bone.tail = tail

        build_bones(armature, item, children, pivot_points)


def link_bones(arm, parent, hierarchy):
    for item in hierarchy:
        bone = arm.edit_bones.get(item)
        if parent:
            bone.parent = parent
            if len(hierarchy) == 1:
                bone.use_connect = True
        
        link_bones(arm, bone, hierarchy[item])


def build_armature(hierarchy, pivot_points, skeleton_name):
    armature = bpy.data.armatures.new(skeleton_name)
    obj = bpy.data.objects.new(skeleton_name, armature)

    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')

    build_bones(armature, "", hierarchy, pivot_points)
    link_bones(armature, None, hierarchy)

    bpy.ops.object.mode_set(mode='OBJECT')

    return obj


def import_armature(operator):
    pivots = read_pivots(operator.path_pivots)
    bones = read_bones(operator.path_mcfg, operator.skeleton)
    filtered = filter_bones(bones, pivots)
    if operator.force_lowercase:
        filtered = force_lowercase_bones(filtered)

    hierarchy = build_bone_hierarchy("", filtered)
    obj = build_armature(hierarchy, pivots, operator.skeleton)
    
    return obj