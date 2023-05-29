import bpy


def read_parameter(file):
    line = file.readline().split()
    return line[0].strip().lower(), float(line[1].strip())


def read_header(file):
    params = {}
    for i in range(6):
        keyword, value = read_parameter(file)
        params[keyword] = value
        
    params["ncols"] = int(params["ncols"])
    params["nrows"] = int(params["nrows"])
    
    return params
    
    
def read_raster(file, ncols, nrows, vscale = 0.01):
    data = []
    for i in range(nrows):
        for value in file.readline().split():
            data.append(float(value) * vscale)
    
    if len(data) != ncols * nrows:
        raise IOError("Raster value table is incomplete")
    
    return data
    
    
def build_points(values, ncols, nrows, cellsize, centered):
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
            
    return points
    
    
def build_faces(ncols, nrows):
    faces = []
    for i in range(nrows - 1):
        for j in range(ncols - 1):
            faces.append((i*ncols + j, (i + 1)*ncols + j, (i + 1)*ncols + j + 1, i*ncols + j + 1))
    
    return faces
            

def read_file(operator, context, file):
    params = {}
    try:
        params = read_header(file)
    except:
        return False
        
    values = read_raster(file, params["ncols"], params["nrows"], operator.vertical_scale)
    points = build_points(values, params["ncols"], params["nrows"], params["cellsize"], "yllcenter" in params)
    faces = build_faces(params["ncols"], params["nrows"])
        
    mesh = bpy.data.meshes.new("Esri ASCII grid")
    mesh.from_pydata(points, [], faces)
    mesh.update(calc_edges=True)
    
    obj = bpy.data.objects.new("Esri ASCII grid", mesh)
    context.scene.collection.objects.link(obj)
    
    object_props = obj.a3ob_properties_object_dtm
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
    
    return True