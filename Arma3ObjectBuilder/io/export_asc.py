import math

import bpy

from ..utilities.logger import ProcessLogger


def valid_resolution(operator, context, obj):
    if operator.apply_modifiers:
        obj = obj.evaluated_get(context.evaluated_depsgraph_get())
    
    mesh = obj.data
    resolution = int(math.sqrt(len(mesh.vertices)))
    return len(mesh.vertices) == resolution**2


def write_header(file, cellsize, easting, northing, centered, resolution, nodata, logger):
    logger.step("Header parameters:")
    logger.level_up()
    
    logger.step("ncols, nrows: %d" % resolution)
    file.write("ncols         " + str(resolution) + "\n")
    file.write("nrows         " + str(resolution) + "\n")
    
    if centered:
        logger.step("xllcenter: %f" % easting)
        logger.step("yllcenter: %f" % northing)
        file.write("xllcenter     " + str(easting) + "\n")
        file.write("yllcenter     " + str(northing) + "\n")
    else:
        logger.step("xllcorner: %f" % easting)
        logger.step("yllcorner: %f" % northing)
        file.write("xllcorner     " + str(easting) + "\n")
        file.write("yllcorner     " + str(northing) + "\n")
        
    logger.step("cellsize: %f" % cellsize)
    logger.step("NODATA_value: %f" % nodata)
    file.write("cellsize      " + str(cellsize) + "\n")
    file.write("NODATA_value  " + str(nodata) + "\n")
    
    logger.level_down()


def sort_points(mesh, resolution, logger):
    points = [vertex.co for vertex in mesh.vertices]
    points.sort(reverse=True, key=lambda vert: vert[1])
    
    rows = []
    for i in range(resolution):
        row = points[i*resolution : (i + 1)*resolution]
        row.sort(key=lambda vert: vert[0])
        rows.append(row)
        
    logger.step("Sorted points: %d" % len(points))
    logger.step("Sorted rows: %d" % len(rows))
        
    return rows


def write_raster(file, rows, logger):
    for row in rows:
        row_string = []
        for value in row:
            row_string.append("{:.4f}".format(value[2]))
            
        file.write(" ".join(row_string) + "\n")
    
    logger.step("Wrote raster values")


def write_file(operator, context, file, obj):
    logger = ProcessLogger()
    logger.step("ASC raster export to %s" % operator.filepath)
    logger.level_up()

    obj = context.active_object
    if obj.mode == 'EDIT':
        obj.update_from_editmode()
        
    if operator.apply_modifiers:
        obj = obj.evaluated_get(context.evaluated_depsgraph_get())
        
    mesh = obj.data
    object_props = obj.a3ob_properties_object_dtm
    
    cellsize = object_props.cellsize
    easting = object_props.easting
    northing = object_props.northing
    centered = object_props.origin == 'CENTER'
    nodata = object_props.nodata
    resolution = int(math.sqrt(len(mesh.vertices)))
    
    rows = sort_points(mesh, resolution, logger)
    
    if object_props.cellsize_source == 'CALCULATED' and resolution != 1:
        cellsize = rows[0][1][0] - rows[0][0][0]
    
    write_header(file, cellsize, easting, northing, centered, resolution, nodata, logger)
    write_raster(file, rows, logger)
    
    logger.level_down()
    logger.step("")
    logger.step("ASC export finished")