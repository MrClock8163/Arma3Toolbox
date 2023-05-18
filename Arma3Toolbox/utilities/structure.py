import bpy
import bmesh
import re
from . import generic as utils

def findComponents(doConvexHull=False):
    utils.force_mode_object()
    activeObj = bpy.context.active_object
    
    # Remove pre-existing component selections
    componentGroups = []
    for group in activeObj.vertex_groups:
        if re.match('component\d+',group.name,re.IGNORECASE):
            componentGroups.append(group.name)
    
    for group in componentGroups:
        bpy.ops.object.vertex_group_set_active(group=group)
        bpy.ops.object.vertex_group_remove()
    
    # Split mesh
    bpy.ops.mesh.separate(type='LOOSE')
    
    # Iterate components
    components = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
    
    componentID = 1
    for obj in components:
        bpy.context.view_layer.objects.active = obj
            
        if len(obj.data.vertices) < 4: # Ignore proxies
            continue
        
        if doConvexHull:
            convexHull()
            
        group = obj.vertex_groups.new(name=('Component%02d' % (componentID)))
        group.add([vert.index for vert in obj.data.vertices],1,'REPLACE')
        
        componentID += 1
    
    for obj in components:
        obj.select_set(True)
        
    bpy.context.view_layer.objects.active = activeObj
    bpy.ops.object.join()

def convexHull():
    utils.force_mode_edit()
    
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.select_all(action = 'SELECT')

    bpy.ops.mesh.convex_hull()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='OBJECT')    

def componentConvexHull(): # DEPRECATED
    utils.force_mode_edit()
    
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    
    activeObj = bpy.context.selected_objects[0]
    activeObj.vertex_groups.active_index = 0
    print(activeObj.vertex_groups.active_index)
    
    for i,group in enumerate(activeObj.vertex_groups):
        if not re.match('component\d+',group.name,re.IGNORECASE):
            continue
                
        bpy.ops.mesh.select_all(action = 'DESELECT')
        activeObj.vertex_groups.active_index = i
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.convex_hull()
        
    bpy.ops.mesh.select_all(action = 'DESELECT')

def checkClosed():
    utils.force_mode_edit()
    
    bpy.ops.mesh.select_mode(type="EDGE")
    
    bpy.ops.mesh.select_non_manifold()

def checkConvexity():
    utils.force_mode_object()
    
    activeObj = bpy.context.selected_objects[0]
    bm = bmesh.new(use_operators=True)
    bm.from_mesh(activeObj.data)
    
    concaveCount = 0
    
    for edge in bm.edges:
        if not edge.is_convex:

            face1 = edge.link_faces[0]
            face2 = edge.link_faces[1]
            dot = face1.normal.dot(face2.normal)
            
            if not (0.9999 <= dot and dot <=1.0001):
                edge.select_set(True)
                concaveCount += 1
            
    bm.to_mesh(activeObj.data)
        
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="EDGE")
    
    return activeObj.name, concaveCount

def cleanupVertexGroups(obj):
    mesh = obj.data
    
    removed = 0

    usedGroups = {}
    for vert in obj.data.vertices:
        for vgroup in vert.groups:
            gIndex = vgroup.group
            if gIndex not in usedGroups:
                usedGroups[gIndex] = obj.vertex_groups[gIndex]

    for group in obj.vertex_groups:
        if group not in usedGroups.values():
            obj.vertex_groups.remove(group)
            removed += 1
        
    return removed
    
def redefineVertexGroup(obj):
    mesh = obj.data
    
    group = obj.vertex_groups.active
    
    if group is None:
        return
    
    groupName = group.name
    
    obj.vertex_groups.remove(group)
    obj.vertex_groups.new(name=groupName)
    bpy.ops.object.vertex_group_assign()
    