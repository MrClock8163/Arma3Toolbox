# Processing functions to export animation data to the RTM file format.
# The actual file handling is implemented in the data_rtm module.


import re

import mathutils

from . import data_rtm as rtm
from ..utilities.logger import ProcessLogger


# For movement animations, a motion vector is supported. Motion
# can be manually set, or calculated from the start and end position of a selected bone.
def process_motion(context, obj, frame_start, frame_end):
    object_props = obj.a3ob_properties_object_armature
    
    motion_vector = mathutils.Vector((0, 0, 0))
    if object_props.motion_source == 'MANUAL' or object_props.motion_bone not in obj.pose.bones:
        motion_vector = object_props.motion_vector
    else:
        bone = obj.pose.bones.get(object_props.motion_bone)
        if not bone:
            return (0, 0, 0)
        
        context.scene.frame_set(frame_start)
        pos_start = (obj.matrix_world @ bone.matrix).to_translation()
        
        context.scene.frame_set(frame_end)
        pos_end = (obj.matrix_world @ bone.matrix).to_translation()
        
        motion_vector = pos_end - pos_start

    return tuple(motion_vector)


def process_bones(obj):
    return [bone.name for bone in obj.data.bones if not re.match(r"[^a-zA-Z0-9_]", bone.name)]


def process_frame(obj, bones, phase):
    output = rtm.RTM_Frame()
    output.phase = phase

    transforms = []
    for bone in bones:
        trans = rtm.RTM_Transform()
        trans.bone = bone
        pose_bone = obj.pose.bones[bone]
        matrix = pose_bone.matrix_channel.copy()
        matrix.transpose()

        trans.matrix = matrix

        transforms.append(trans)
    
    output.transforms = transforms

    return output


def write_file(operator, context, file, obj):
    logger = ProcessLogger()
    logger.step("RTM export to %s" % operator.filepath)

    object_props = obj.a3ob_properties_object_armature
    
    frame_start = operator.frame_start
    frame_end = operator.frame_end
    frame_range = frame_end - frame_start

    frame_indices = list(set([frame.index for frame in object_props.frames if not operator.clamp or frame.index >= frame_start and frame.index <= frame_end]))
    static_pose = operator.static_pose or len(frame_indices) == 0

    if static_pose:
        logger.log("Detected static pose")
        frame_indices = [context.scene.frame_current, context.scene.frame_current]
    else:
        logger.log("Detected %d frames" % len(frame_indices))
    
    logger.log("Processing data:")
    logger.level_up()

    anim = rtm.RTM_File()
    if not static_pose:
        anim.motion = process_motion(context, obj, frame_start, frame_end)
        logger.log("Calculated motion")

    anim.bones = process_bones(obj)
    logger.log("Collected bones")
    
    if static_pose:
        anim.frames = [
            process_frame(obj, anim.bones, 0),
            process_frame(obj, anim.bones, 1)
        ]
    else:
        frame_indices.sort()
        frames = []
        for index in frame_indices:
            phase = (index - frame_start) / frame_range
            context.scene.frame_set(index)
            frames.append(process_frame(obj, anim.bones, phase))
        
        anim.frames = frames
    
    logger.log("Collected frames")
    logger.level_down()

    logger.log("File report:")
    logger.level_up()

    logger.log("Motion: %f, %f, %f" %  tuple(anim.motion))
    logger.log("Bones: %d" % len(anim.bones))
    logger.log("Frames: %d" % len(anim.frames))

    logger.level_down()

    if operator.force_lowercase:
        anim.force_lowercase()

    anim.write(file)

    return static_pose, len(frame_indices)