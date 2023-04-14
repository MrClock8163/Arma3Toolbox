import bpy
import bmesh
import re
from . import generic as utils

def findComponents(convexHull=False):
    utils.forceEditMode()
    
    bpy.ops.mesh.select_mode(type='VERT')
    
    activeObj = bpy.context.active_object
    
    # Remove pre-existing component selections
    componentGroups = []
    for group in activeObj.vertex_groups:
        if re.match('component\d+',group.name,re.IGNORECASE):
            componentGroups.append(group.name)
    
    for i,group in enumerate(componentGroups):
        bpy.ops.object.vertex_group_set_active(group=group)
        bpy.ops.object.vertex_group_remove()
        
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create new groups
    componentID = 1
    for i in range(len(activeObj.data.vertices)):
        if activeObj.data.vertices[i].hide == True: # Will break because the convex hull decreases the number of vertices
            continue
        
        activeObj.data.vertices[i].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_linked()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if convexHull:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.convex_hull()
            bpy.ops.object.mode_set(mode='OBJECT')
            
        bpy.ops.object.mode_set(mode='EDIT')
        activeObj.vertex_groups.new(name=('Component%02d' % componentID))
        bpy.ops.object.vertex_group_assign()
        componentID += 1
        bpy.ops.mesh.hide()
        bpy.ops.object.mode_set(mode='OBJECT')
        
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

def convexHull():
    utils.forceEditMode()
    
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.select_all(action = 'SELECT')

    bpy.ops.mesh.convex_hull()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='OBJECT')

def componentConvexHull(): # DEPRECATED
    utils.forceEditMode()
    
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
    utils.forceEditMode()
    
    bpy.ops.mesh.select_mode(type="EDGE")
    
    bpy.ops.mesh.select_non_manifold()

def checkConvexity():
    utils.forceObjectMode()
    
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