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
    if centered:
        start_x = -cellsize / 2
        start_y = -cellsize / 2
        
    start_y += (nrows - 1) * cellsize
        
    points = []
    for i in range(nrows):
        for j in range(ncols):
            points.append((start_x + i * cellsize, start_y + j * -cellsize, values[i*ncols + j]))
            
    return points
    
    
def build_faces(ncols, nrows):
    faces = []
    for i in range(nrows - 1):
        for j in range(ncols - 1):
            faces.append((i*ncols + j, i*ncols + j + 1, (i + 1)*ncols + j + 1, (i + 1)*ncols + j))
    
    return faces
            

def read_file(operator, context, file):
    params = {}
    try:
        params = read_header(file)
    except:
        return False
        
    values = []
    try:
        values = read_raster(file, params["ncols"], params["nrows"], 0.01)
    except:
        return False
    
    points = []
    faces = []   
    try:
        points = build_points(values, params["ncols"], params["nrows"], params["cellsize"], "yllcenter" in params)
        faces = build_faces(params["ncols"], params["nrows"])    
    except:
        return False    
        
    mesh = bpy.data.meshes.new("Esri ASCII grid")
    mesh.from_pydata(points, [], faces)
    mesh.update(calc_edges=True)
    
    obj = bpy.data.objects.new("Esri ASCII grid", mesh)
    context.scene.collection.objects.link(obj)
    
    return True
    
    
#def main():
#    filepath = "C:/Users/Vekkerur/Desktop/import_asc_dev.asc"
#    
#    with open(filepath, "rt") as file:
#        read_file(None, bpy.context, file)