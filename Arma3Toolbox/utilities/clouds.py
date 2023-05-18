import bpy
import bmesh
from mathutils import Vector

def validate_references(source,target):
    if source or target:
        if source == target and source.users == 2:
            bpy.data.objects.remove(source)
            source,target = None,None
        else:
            if source and source.users == 1:
                bpy.data.objects.remove(source)
                source = None
            if target and target.users == 1:
                bpy.data.objects.remove(target)
                target = None
    
    return source,target

def is_inside(obj,point):
    result,closest,normal,_ = obj.closest_point_on_mesh(point)
    
    if not result:
        return False
    
    return (closest-point).dot(normal) > 0
    
def create_selection(obj,selection):
    group = obj.vertex_groups.get(selection,None)
    
    if not group:
        group = obj.vertex_groups.new(name=selection.strip())

    group.add([vert.index for vert in obj.data.vertices],1,'REPLACE')
    
def calculate_grid(bbox,minCoord,maxCoord,spacing):
    dim = maxCoord-minCoord
    
    if dim < spacing:
        return (minCoord + dim/2,)
        
    count = int(dim // spacing)
    padding = (dim - (spacing * count)) / 2
    points = Vector.Linspace(minCoord+padding,maxCoord-padding,count+1)
    
    return points

def generate_hitpoints(operator,context):
    wm = context.window_manager
    OBprops = wm.a3ob_hitpoint_generator
    
    source,target = validate_references(OBprops.source,OBprops.target)
    
    if not source or len(source.data.polygons) == 0:
        return
    
    sourceObj = source

    if OBprops.triangulate == 'BEFORE':
        modifTri = sourceObj.modifiers.new("A3OB_HitPointTris",'TRIANGULATE')
        
    modifBevel = sourceObj.modifiers.new("A3OB_HitPointBevel",'BEVEL')
    modifBevel.segments = OBprops.bevel_segments
    modifBevel.width = OBprops.bevel_offset
    
    if OBprops.triangulate == 'AFTER':
        modifTri = sourceObj.modifiers.new("A3OB_HitPointTris",'TRIANGULATE')

    sourceObjEval = sourceObj.evaluated_get(bpy.context.evaluated_depsgraph_get())

    bbox = sourceObjEval.bound_box

    minX = min(bbox, key=lambda pos: pos[0])[0]
    minY = min(bbox, key=lambda pos: pos[1])[1]
    minZ = min(bbox, key=lambda pos: pos[2])[2]

    maxX = max(bbox, key=lambda pos: pos[0])[0]
    maxY = max(bbox, key=lambda pos: pos[1])[1]
    maxZ = max(bbox, key=lambda pos: pos[2])[2]
    
    spacingX = OBprops.spacing[0]
    spacingY = OBprops.spacing[1]
    spacingZ = OBprops.spacing[2]
    
    pointsX = calculate_grid(bbox,minX,maxX,spacingX)
    pointsY = calculate_grid(bbox,minY,maxY,spacingY)
    pointsZ = calculate_grid(bbox,minZ,maxZ,spacingZ)

    points = []
    bm = bmesh.new()

    for X in pointsX:
        for Y in pointsY:
            for Z in pointsZ:
                if is_inside(sourceObjEval,Vector((X,Y,Z))):
                    bm.verts.new((X,Y,Z))
                
    mesh = bpy.data.meshes.new("Point cloud")
    bm.to_mesh(mesh)
    bm.free()
    
    collection = sourceObj.users_collection
    
    if not target:
        targetObj = bpy.data.objects.new("Point cloud",mesh)
        if len(collection) > 0:
            collection = collection[0]
        else:
            collection = context.scene.collection
        
        collection.objects.link(targetObj)
    else:
        targetObj = target
        targetObj.data = mesh
        
    targetObj.matrix_world = sourceObj.matrix_world
    
    targetObj.modifiers.clear()

    sourceObj.modifiers.remove(modifTri)
    sourceObj.modifiers.remove(modifBevel)
    
    if OBprops.selection.strip() != "" and len(targetObj.data.vertices) > 0:
        create_selection(targetObj,OBprops.selection)
