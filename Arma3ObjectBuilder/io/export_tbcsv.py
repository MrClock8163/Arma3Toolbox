import time
import math

import bpy
# import mathutils

from . import data_tbcsv as tb
from ..utilities.logger import ProcessLogger


def matrix_to_transform(mat):
    trans = tb.TBCSV_Transform()

    loc, rot, scale = mat.decompose()
    yaw, pitch, roll = rot.to_euler('XYZ')
    east, north, elev = loc

    trans.loc = (east, north, elev)
    trans.rot = (math.degrees(yaw), math.degrees(pitch), math.degrees(roll))
    trans.scale = math.fsum([comp for comp in scale]) / 3

    return trans


def write_file(operator, context, file):
    logger = ProcessLogger()
    logger.step("Map objects list export to %s" % operator.filepath)
    time_file_start = time.time()

    targets = bpy.data.objects
    if operator.targets == 'SCENE':
        targets = context.scene.objects
    elif operator.targets == 'SELECTION':
        targets = context.selected_objects
    
    if context.collection:
        if not bpy.data.collections.get(operator.collection):
            raise tb.TBCSV_Error("Collection (%s) was not found" % operator.collection)
        
        logger.log("Exporting collection")
        targets = bpy.data.collections.get(operator.collection).objects

    tbcsv = tb.TBCSV_File()
    for obj in targets:
        entry = tb.TBCSV_Object(obj.name)
        entry.transform = matrix_to_transform(obj.matrix_world)
        tbcsv.objects.append(entry)
    
    logger.log("Collected objects: %d" % len(tbcsv.objects))
    
    tbcsv.write(file)

    logger.step("Map objects list export finished in %f sec" % (time.time() - time_file_start))

    return len(tbcsv.objects)