import bpy
import mathutils
import math

def find_center_index(mesh):
    # 1st vert
    angle = (mesh.vertices[1].co - mesh.vertices[0].co).angle(mesh.vertices[2].co - mesh.vertices[0].co)
    if round(math.degrees(angle),-1) == 90:
        return 0
       
    # 2nd vert
    angle = (mesh.vertices[0].co - mesh.vertices[1].co).angle(mesh.vertices[2].co - mesh.vertices[1].co)
    if round(math.degrees(angle),-1) == 90:
        return 1
       
    # 3rd vert
    angle = (mesh.vertices[0].co - mesh.vertices[2].co).angle(mesh.vertices[1].co - mesh.vertices[2].co)
    if round(math.degrees(angle),-1) == 90:
        return 2
        
    return 0

def find_axis_indices(mesh):
    centerID = find_center_index(mesh)
    verts = [0,1,2]
    verts.remove(centerID)
    
    dist1 = (mesh.vertices[verts[0]].co - mesh.vertices[centerID].co).length
    dist2 = (mesh.vertices[verts[1]].co - mesh.vertices[centerID].co).length
    
    if dist1 > dist2:
        return centerID, verts[1], verts[0]
        
    elif dist1 < dist2:
        return centerID, verts[0], verts[1]

def get_transform_rotation(obj):
    centerID,yID,zID = find_axis_indices(obj.data)
    
    x = -obj.data.polygons[0].normal.normalized()
    y = (obj.data.vertices[yID].co - obj.data.vertices[centerID].co).normalized()
    z = (obj.data.vertices[zID].co - obj.data.vertices[centerID].co).normalized()
    
    m = mathutils.Matrix(((*x,0),(*y,0),(*z,0),(0,0,0,1)))
    return m
    
def create_proxy():
    objData = bpy.data.meshes.new("Proxy")
    objData.from_pydata([(0,0,0),(0,0,2),(0,1,0)],[],[(0,1,2)])
    objData.update(calc_edges=True)
    
    objData.polygons[0].use_smooth = True
    
    obj = bpy.data.objects.new("Proxy",objData)
    obj.a3ob_properties_object_proxy.isArma3Proxy = True
    
    return obj