import bpy

from ..utilities.logger import ProcessLogger


def read_parameter(file):
    line = file.readline().split()
    return line[0].strip().lower(), float(line[1].strip())


def read_header(file, logger):
    logger.step("Header parameters:")
    logger.level_up()
    
    params = {}
    for i in range(6):
        keyword, value = read_parameter(file)
        params[keyword] = value
        logger.step("%s: %f" %(keyword, value))
        
    params["ncols"] = int(params["ncols"])
    params["nrows"] = int(params["nrows"])
    
    logger.level_down()
    
    return params
    
    
def read_raster(file, ncols, nrows, vscale, logger):
    data = []
    for i in range(nrows):
        for value in file.readline().split():
            data.append(float(value) * vscale)
    
    if len(data) != ncols * nrows:
        raise errors.ASCError("Raster value table is incomplete")
    
    logger.step("Read values: %d" % len(data))
    
    return data
    
    
def build_points(values, ncols, nrows, cellsize, centered, logger):
    start_x = 0
    start_y = 0
    if not centered:
        start_x = cellsize / 2
        start_y = cellsize / 2
        
    start_y += (nrows - 1) * cellsize
        
    points = []
    for i in range(nrows):
        for j in range(ncols):
            points.append((start_x + j * cellsize, start_y + i * -cellsize, values[i*ncols + j]))
            
    logger.step("Built points: %d" % len(points))
            
    return points
    
    
def build_faces(ncols, nrows, logger):
    faces = []
    for i in range(nrows - 1):
        for j in range(ncols - 1):
            faces.append((i*ncols + j, (i + 1)*ncols + j, (i + 1)*ncols + j + 1, i*ncols + j + 1))
            
    logger.step("Built faces: %d" % len(faces))
    
    return faces
            

def read_file(operator, context, file):
    logger = ProcessLogger()
    logger.step("ASC raster import from %s" % operator.filepath)
    logger.level_up()

    params = read_header(file, logger)
    values = read_raster(file, params["ncols"], params["nrows"], operator.vertical_scale, logger)
    points = build_points(values, params["ncols"], params["nrows"], params["cellsize"], "yllcenter" in params, logger)
    faces = build_faces(params["ncols"], params["nrows"], logger)
        
    mesh = bpy.data.meshes.new("DTM")
    mesh.from_pydata(points, [], faces)
    mesh.update(calc_edges=True)
    
    obj = bpy.data.objects.new("DTM", mesh)
    context.scene.collection.objects.link(obj)
    
    object_props = obj.a3ob_properties_object_dtm
    object_props.cellsize_source = 'MANUAL'
    object_props.cellsize = params["cellsize"]
    
    if "yllcenter" in params:
        object_props.origin = 'CENTER'
        object_props.easting = params["xllcenter"]
        object_props.northing = params["yllcenter"]
    else:
        object_props.origin = 'CORNER'
        object_props.easting = params["xllcorner"]
        object_props.northing = params["yllcorner"]
        
    object_props.nodata = params["nodata_value"]
    
    logger.level_down()
    logger.step("")
    logger.step("ASC export finished")