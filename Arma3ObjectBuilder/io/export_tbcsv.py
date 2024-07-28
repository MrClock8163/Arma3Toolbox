# Processing functions to export object positions into list format
# acceptable by Terrain Builder
# Thanks to HorribleGoat for the help and suggestions


import time
import math

import bpy

from . import data_tbcsv as tb
from ..utilities.logger import ProcessLogger


def include_object(obj, operator):
    if obj.type != 'MESH':
        return False
    
    if operator.only_lods and not obj.a3ob_properties_object.is_a3_lod:
        return False

    return True


def get_object_name(obj, operator):
    if operator.name_source == 'COLLECTION' and operator.collection:
        return operator.collection
    elif operator.name_source == 'PROPERTY' and obj.get(operator.name_prop):
        return obj.get(operator.name_prop)
    elif operator.name_source == 'OBJECT':
        return obj.name.split(".")[0]
    
    return ""


def matrix_to_transform(mat):
    trans = tb.TBCSV_Transform()

    loc, rot, scale = mat.decompose()
    pitch, roll, yaw = rot.to_euler('ZXY')
    east, north, elev = loc

    trans.loc = (east, north, elev)
    trans.rot = (math.degrees(-yaw), math.degrees(pitch), math.degrees(roll))
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

    if operator.only_lods:
        logger.log("Exporting LOD objects only")
    
    if operator.collection:
        if not bpy.data.collections.get(operator.collection):
            raise tb.TBCSV_Error("Collection (%s) was not found" % operator.collection)
        
        logger.log("Exporting collection")
        targets = bpy.data.collections.get(operator.collection).objects

    tbcsv = tb.TBCSV_File()
    for obj in (target for target in targets if include_object(target, operator)):
        name = get_object_name(obj, operator)
        if not name:
            logger.log("Could not determine name for %s" % obj.name)
            continue

        entry = tb.TBCSV_Object(name)
        entry.transform = matrix_to_transform(obj.matrix_world)
        tbcsv.objects.append(entry)
    
    logger.log("Exported objects: %d" % len(tbcsv.objects))
    
    tbcsv.write(file)

    logger.step("Map objects list export finished in %f sec" % (time.time() - time_file_start))

    return len(tbcsv.objects)
