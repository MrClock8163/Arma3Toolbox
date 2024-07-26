import time
import math

import bpy
import mathutils

from . import data_tbcsv as tb
from ..utilities.logger import ProcessLogger


def build_matrices(objects):
    matrices = []
    
    for obj in objects:
        trans = obj.transform
        rot = mathutils.Euler([math.radians(angle) for angle in trans.rot], 'ZXY').to_matrix().to_4x4()
        locrot = rot + mathutils.Matrix.Translation(trans.loc) - mathutils.Matrix.Identity(4)
        mat = locrot @ mathutils.Matrix.Scale(trans.scale, 4)

        matrices.append((obj.name, mat))

    return matrices


def read_file(operator, context, file):
    logger = ProcessLogger()
    logger.step("Map objects list import from %s" % operator.filepath)
    time_file_start = time.time()

    tbcsv = tb.TBCSV_File.read(file)
    logger.log("Read objects: %d" % len(tbcsv.objects))

    targets = bpy.data.objects
    if operator.targets == 'SCENE':
        targets = context.scene.objects
    elif operator.targets == 'SELECTION':
        targets = {obj.name: obj for obj in context.selected_objects}
    
    count_found = 0
    for name, mat in build_matrices(tbcsv.objects):
        obj = targets.get(name)
        if not obj:
            continue
        
        count_found += 1
        obj.matrix_world = mat

    
    logger.log("Matched objects: %d" % count_found)

    logger.step("Map objects list import finished in %f sec" % (time.time() - time_file_start))

    return len(tbcsv.objects), count_found
