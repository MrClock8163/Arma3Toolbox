import struct
import re

import bpy
import mathutils

from ..io import binary_handler as binary
from ..utilities.logger import ProcessLogger


def write_bone(file, name):
    file.write(struct.pack('<32s', name.encode('ASCII')))


def write_matrix(file, matrix):
    file.write(struct.pack('<3f', matrix[0][0], matrix[0][2], matrix[0][1]))
    file.write(struct.pack('<3f', matrix[2][0], matrix[2][2], matrix[2][1]))
    file.write(struct.pack('<3f', matrix[1][0], matrix[1][2], matrix[1][1]))
    file.write(struct.pack('<3f', matrix[3][0], matrix[3][2], matrix[3][1]))


def write_frame(file, obj, bones, phase):
    binary.write_float(file, phase)
    for bone in bones:
        write_bone(file, bone)
        
        pose_bone = obj.pose.bones[bone]
        matrix = pose_bone.matrix_channel.copy()
        matrix.transpose()
        write_matrix(file, matrix)

  
def write_motion(context, file, obj, frame_start, frame_end, logger):
    object_props = obj.a3ob_properties_object_armature
    
    motion_vector = mathutils.Vector((0, 0, 0))
    if object_props.motion_source == 'MANUAL' or object_props.motion_bone not in obj.pose.bones:
        motion_vector = object_props.motion_vector
    else:
        bone = obj.pose.bones[object_props.motion_bone]
        
        context.scene.frame_set(frame_start)
        pos_start = (obj.matrix_world @ bone.matrix).to_translation()
        
        context.scene.frame_set(frame_end)
        pos_end = (obj.matrix_world @ bone.matrix).to_translation()
        
        motion_vector = pos_end - pos_start
    
    file.write((struct.pack('<3f', motion_vector[0], motion_vector[2], motion_vector[1])))
    logger.step("Motion: %f" % motion_vector.length)


def write_file(operator, context, file, obj):
    logger = ProcessLogger()
    logger.step("RTM export to %s" % operator.filepath)
    
    object_props = obj.a3ob_properties_object_armature
    
    armature = obj.data
    frame_start = operator.frame_start
    frame_end = operator.frame_end
    frame_range = frame_end - frame_start
    
    
    frame_indices = list(set([frame.index for frame in object_props.frames if not operator.clamp or frame.index >= frame_start and frame.index <= frame_end]))
    static_pose = operator.static_pose or len(frame_indices) == 0
    
    if static_pose:
        frame_indices = [context.scene.frame_current, context.scene.frame_current]  
    
    bones = [bone.name for bone in armature.bones if not re.match(r"[^a-zA-Z0-9_]", bone.name)]
    
    logger.level_up()
    
    binary.write_chars(file, "RTM_0101")
    write_motion(context, file, obj, frame_start, frame_end, logger)
    
    binary.write_ulong(file, len(frame_indices))
    binary.write_ulong(file, len(bones))
    
    for bone in bones:
        write_bone(file, bone)
        
    logger.step("Wrote bones: %d" % len(bones))
        
    if static_pose:
        write_frame(file, obj, bones, 0)
        write_frame(file, obj, bones, 1)
    else:
        frame_indices.sort()
        for index in frame_indices:
            phase = (index - frame_start) / frame_range
            
            context.scene.frame_set(index)
            write_frame(file, obj, bones, phase)
        
    logger.step("Wrote frames: %d" % len(frame_indices))
            
    logger.level_down()
    logger.step("")
    logger.step("RTM export finished")
    
    return static_pose, len(frame_indices)