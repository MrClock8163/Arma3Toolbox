import bpy
import mathutils
import math

def find_center_index(mesh):
    # 1st vert
    angle = (mesh.vertices[1].co - mesh.vertices[0].co).angle(mesh.vertices[2].co - mesh.vertices[0].co)
    if round(math.degrees(angle), -1) == 90:
        return 0
       
    # 2nd vert
    angle = (mesh.vertices[0].co - mesh.vertices[1].co).angle(mesh.vertices[2].co - mesh.vertices[1].co)
    if round(math.degrees(angle), -1) == 90:
        return 1
       
    # 3rd vert
    angle = (mesh.vertices[0].co - mesh.vertices[2].co).angle(mesh.vertices[1].co - mesh.vertices[2].co)
    if round(math.degrees(angle), -1) == 90:
        return 2
        
    return 0

def find_axis_indices(mesh):
    center_id = find_center_index(mesh)
    verts = [0, 1, 2]
    verts.remove(center_id)
    
    dist1 = (mesh.vertices[verts[0]].co - mesh.vertices[center_id].co).length
    dist2 = (mesh.vertices[verts[1]].co - mesh.vertices[center_id].co).length
    
    if dist1 > dist2:
        return center_id, verts[1], verts[0]
        
    elif dist1 < dist2:
        return center_id, verts[0], verts[1]

def get_transform_rotation(obj):
    center_id, y_id, z_id = find_axis_indices(obj.data)
    
    x = -obj.data.polygons[0].normal.normalized()
    y = (obj.data.vertices[y_id].co - obj.data.vertices[center_id].co).normalized()
    z = (obj.data.vertices[z_id].co - obj.data.vertices[center_id].co).normalized()
    
    m = mathutils.Matrix(((*x , 0), (*y, 0), (*z, 0), (0, 0, 0, 1)))
    return m
    
def create_proxy():
    mesh = bpy.data.meshes.new("Proxy")
    mesh.from_pydata([(0, 0, 0), (0, 0, 2), (0, 1, 0)], [], [(0, 1, 2)])
    mesh.update(calc_edges=True)
    
    mesh.polygons[0].use_smooth = True
    
    obj = bpy.data.objects.new("Proxy", mesh)
    obj.a3ob_properties_object_proxy.is_a3_proxy = True
    
    return obj