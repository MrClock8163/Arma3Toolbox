import os
from itertools import chain

import bpy
from mathutils import Matrix, Vector

from . import data_rtm


def create_action(obj, name):
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    if not obj.animation_data:
        obj.animation_data_create()
    if not obj.animation_data.action:
        obj.animation_data.action = action
    
    return action


def build_transform_lookup(rtm_data):
    transforms = {}
    for i, frame in enumerate(rtm_data.frames):
        for item in frame.transforms:
            transforms[item.bone.lower(), i] = Matrix(item.matrix).transposed()

    return transforms


def build_frame_list(operator, rtm_data):
    frames = {}

    frame_start = operator.frame_start
    frame_end = operator.frame_end
    if operator.mapping_mode == 'FPS':
        frame_start = 1
        frame_end = operator.fps * operator.time + 1
    elif operator.mapping_mode == 'DIRECT':
        frame_start = 1
        frame_end = len(rtm_data.frames)

    for i, frame in enumerate(rtm_data.frames):
        frames[i] = frame.phase * frame_end + (1 - frame.phase) * frame_start
    
    if operator.mapping_mode != 'DIRECT' and operator.round_frames:
        frames = {i: round(frames[i]) for i in frames}

    return frames


def build_fcurves(action, pose_bone):
    rot_mode = "rotation_euler"
    channel_count = 3
    if pose_bone.rotation_mode == 'QUATERNION':
        rot_mode = "rotation_quaternion"
        channel_count = 4
    elif pose_bone.rotation_mode == 'AXIS_ANGLE':
        rot_mode = "rotation_axis_angle"
        channel_count = 4

    path_loc = pose_bone.path_from_id("location")
    path_rot = pose_bone.path_from_id(rot_mode)
    path_scale = pose_bone.path_from_id("scale")

    props = [(path_loc, 3, pose_bone.name),
            (path_rot, channel_count, pose_bone.name),
            (path_scale, 3, pose_bone.name)]
    
    fcurves = [action.fcurves.new(prop, index=channel, action_group=grpname)
                for prop, nbr_channels, grpname in props for channel in range(nbr_channels)]

    return fcurves


def store_keyframes(dictionary, frame_idx, iterator):
    for fc, value in iterator:
        fc_key = (fc.data_path, fc.array_index)
        if not dictionary.get(fc_key):
            dictionary[fc_key] = []
        dictionary[fc_key].extend((frame_idx, value))


def add_keyframes(action, fcurves, dictionary):
    for fc_key, key_values in dictionary.items():
        data_path, index = fc_key

        fcurve = action.fcurves.find(data_path=data_path, index=index)
        num_keys = len(key_values) // 2
        fcurve.keyframe_points.add(num_keys)
        fcurve.keyframe_points.foreach_set('co', key_values)
        linear_enum_value = bpy.types.Keyframe.bl_rna.properties['interpolation'].enum_items['LINEAR'].value
        fcurve.keyframe_points.foreach_set('interpolation', (linear_enum_value,) * num_keys)

    for fc in fcurves:
        fc.update()


def import_keyframes(obj, action, transforms, frames):
    for pose_bone in obj.pose.bones:
        fcurves = build_fcurves(action, pose_bone)

        mat_rest = pose_bone.bone.matrix_local.copy()

        rot_eul_prev = pose_bone.rotation_euler.copy()
        rot_quat_prev = pose_bone.rotation_quaternion.copy()

        keyframes = {}
        for i in range(len(frames)):
            mat_channel = transforms.get((pose_bone.name.lower(), i), Matrix())
            mat_parent_channel = transforms.get((pose_bone.parent.name.lower() if pose_bone.parent else "", i), Matrix())
            mat_basis = mat_rest.inverted_safe() @ mat_parent_channel.inverted_safe() @ (mat_channel @ mat_rest)
            loc, rot, scale = mat_basis.decompose()

            if pose_bone.rotation_mode == 'QUATERNION':
                if rot_quat_prev.dot(rot) < 0.0:
                    rot = -rot
                rot_quat_prev = rot
            elif pose_bone.rotation_mode == 'AXIS_ANGLE':
                vec, ang = rot.to_axis_angle()
                rot = ang, vec.x, vec.y, vec.z
            else:  # Euler
                rot = rot.to_euler(pose_bone.rotation_mode, rot_eul_prev)
                rot_eul_prev = rot
            
            if pose_bone.bone.use_connect:
                loc = Vector() # clean computational residuals

            store_keyframes(keyframes, frames[i], zip(fcurves, chain(loc, rot, scale)))

        add_keyframes(action, fcurves, keyframes)


def import_file(operator, obj):
    action = create_action(obj, os.path.basename(operator.filepath))
    rtm_data = data_rtm.RTM_File.read_file(operator.filepath)
    transforms = build_transform_lookup(rtm_data)
    frames = build_frame_list(operator, rtm_data)

    import_keyframes(obj, action, transforms, frames)

    return len(frames)