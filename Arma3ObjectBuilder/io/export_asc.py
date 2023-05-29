import math

import bpy


def valid_resolution(mesh):
    resolution = int(math.sqrt(len(mesh.vertices)))
    return len(mesh.vertices) == resolution**2


def write_header(file, cellsize, easting, northing, centered, resolution, nodata):    
    file.write("ncols         " + str(resolution) + "\n")
    file.write("nrows         " + str(resolution) + "\n")
    
    if centered:
        file.write("xllcenter     " + str(easting) + "\n")
        file.write("yllcenter     " + str(northing) + "\n")
    else:
        file.write("xllcorner     " + str(easting) + "\n")
        file.write("yllcorner     " + str(northing) + "\n")
        
    file.write("cellsize      " + str(cellsize) + "\n")
    file.write("NODATA_value  " + str(nodata) + "\n")


def sort_points(mesh, resolution):
    points = [vertex.co for vertex in mesh.vertices]
    
    points.sort(reverse=True, key=lambda vert: vert[1])
    
    rows = []
    for i in range(resolution):
        row = points[i*resolution : (i + 1)*resolution]
        row.sort(key=lambda vert: vert[0])
        rows.append(row)
        
    return rows


def write_raster(file, rows):
    for row in rows:
        row_string = []
        for value in row:
            row_string.append("{:.4f}".format(value[2]))
            
        file.write(" ".join(row_string) + "\n")


def write_file(operator, context, file, obj):
    obj = context.active_object
    mesh = obj.data
    object_props = obj.a3ob_properties_object_dtm
    
    resolution = int(math.sqrt(len(mesh.vertices)))
    if len(mesh.vertices) != resolution**2:
        # print("not square")
        return False
    
    cellsize = object_props.cellsize
    easting = object_props.easting
    northing = object_props.northing
    centered = object_props.origin == 'CENTER'
    nodata = object_props.nodata
    
    write_header(file, cellsize, easting, northing, centered, resolution, nodata)
    rows = sort_points(mesh, resolution)
    write_raster(file, rows)