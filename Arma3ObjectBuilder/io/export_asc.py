# Processing functions to export DTM data to ESRI ASCII grid (*.asc) files.
# The actual file handling is implemented in the data_asc module.


import math
import time

from . import data_asc as asc
from ..utilities.logger import ProcessLogger


def calc_resolution(operator, count_vertex):
    nrows = 0
    ncols = 0

    if operator.dimensions == 'SQUARE':
        nrows = ncols = int(math.sqrt(count_vertex))
    elif operator.dimensions == 'LANDSCAPE':
        nrows = int(math.sqrt(count_vertex / 2))
        ncols = 2 * nrows
    elif operator.dimensions == 'PORTRAIT':
        ncols = int(math.sqrt(count_vertex / 2))
        nrows = 2 * ncols
    else:
        nrows = operator.rows
        ncols = operator.columns
    
    return nrows, ncols


def get_points(vertices, nrows, ncols):
    points = [vertex.co for vertex in vertices]
    points.sort(key=lambda vert: vert[1], reverse=True)

    data = []
    for i in range(nrows):
        row = points[i * ncols : (i + 1) * ncols]
        row.sort(key=lambda vert: vert[0])
        data.append([vert[2] for vert in row])
    
    assert len(data) == nrows

    return data


def write_file(operator, context, file, obj):
    logger = ProcessLogger()
    time_start = time.time()
    logger.step("ASC raster export to %s" % operator.filepath)
    logger.level_up()

    obj = context.active_object
    if obj.mode == 'EDIT':
        obj.update_from_editmode()

    logger.step("Processing data:")
    logger.level_up()
        
    if operator.apply_modifiers:
        obj = obj.evaluated_get(context.evaluated_depsgraph_get())
        logger.step("Applied modifiers")
        
    mesh = obj.data
    object_props = obj.a3ob_properties_object_dtm
    
    raster = asc.ASC_File()
    pos_type = asc.ASC_File.POS_CENTER if object_props.origin == 'CENTER' else asc.ASC_File.POS_CORNER
    raster.pos = (pos_type, object_props.easting, object_props.northing)
    raster.nodata = object_props.nodata

    count_vertex = len(mesh.vertices)
    nrows, ncols = calc_resolution(operator, count_vertex)
    if count_vertex != (nrows * ncols):
        raise asc.ASC_Error("Invalid dimensions: %d x %d (vertex count: %d)" % (nrows, ncols, count_vertex))
    
    logger.step("Calculated dimensions")

    raster.data = get_points(mesh.vertices, nrows, ncols)
    logger.step("Collected data")
    
    cellsize = object_props.cellsize
    if object_props.cellsize_source == 'CALCULATED' and count_vertex > 1:
        cellsize = raster.get_cellsize_from_data()
        if cellsize is None:
            raise asc.ASC_Error("Could not calculate cellsize")
        logger.step("Calculated cellsize")
        
    raster.cellsize = cellsize
    logger.level_down()

    logger.step("File report:")
    logger.level_up()
    logger.step("Dimensions: %d x %d" % (nrows, ncols))
    logger.step("DTM type: %s" % ("raster" if pos_type == asc.ASC_File.POS_CENTER else "grid"))
    logger.step("Easting: %f" % object_props.easting)
    logger.step("Northing: %f" % object_props.northing)
    logger.step("NULL indicator: %f" % object_props.nodata)
    logger.level_down()

    raster.write(file)
    
    logger.level_down()
    logger.step("ASC export finished in %f sec" % (time.time() - time_start))