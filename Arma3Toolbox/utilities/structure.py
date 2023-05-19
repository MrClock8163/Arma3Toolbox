import re

import bpy
import bmesh

from . import generic as utils


def find_components(do_convex_hull=False):
    utils.force_mode_object()
    obj = bpy.context.active_object
    
    # Remove pre-existing component selections
    existing_component_groups = []
    for group in obj.vertex_groups:
        if re.match("component\d+", group.name, re.IGNORECASE):
            existing_component_groups.append(group.name)
    
    for group in existing_component_groups:
        bpy.ops.object.vertex_group_set_active(group=group)
        bpy.ops.object.vertex_group_remove()
    
    # Split mesh
    bpy.ops.mesh.separate(type='LOOSE')
    
    # Iterate components
    components = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
    component_id = 1
    for obj in components:
        bpy.context.view_layer.objects.active = obj
            
        if len(obj.data.vertices) < 4: # Ignore proxies
            continue
        
        if do_convex_hull:
            convex_hull()
            
        group = obj.vertex_groups.new(name=("Component%02d" % (component_id)))
        group.add([vert.index for vert in obj.data.vertices], 1, 'REPLACE')
        
        component_id += 1
    
    for obj in components:
        obj.select_set(True)
        
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()


def convex_hull():
    utils.force_mode_edit()
    
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='OBJECT')    


def component_convex_hull(): # DEPRECATED
    utils.force_mode_edit()
    
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')
    
    obj = bpy.context.selected_objects[0]
    obj.vertex_groups.active_index = 0
    for i,group in enumerate(obj.vertex_groups):
        if not re.match("component\d+", group.name, re.IGNORECASE):
            continue
                
        bpy.ops.mesh.select_all(action='DESELECT')
        obj.vertex_groups.active_index = i
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.convex_hull()
        
    bpy.ops.mesh.select_all(action='DESELECT')


def check_closed():
    utils.force_mode_edit()
    
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.select_non_manifold()


def check_convexity():
    utils.force_mode_object()
    
    obj = bpy.context.selected_objects[0]
    bm = bmesh.new(use_operators=True)
    bm.from_mesh(obj.data)
    
    count_concave = 0
    for edge in bm.edges:
        if not edge.is_convex:
            face1 = edge.link_faces[0]
            face2 = edge.link_faces[1]
            dot = face1.normal.dot(face2.normal)
            
            if not (0.9999 <= dot and dot <=1.0001):
                edge.select_set(True)
                count_concave += 1
            
    bm.to_mesh(obj.data)
        
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="EDGE")
    
    return obj.name, count_concave


def cleanup_vertex_groups(obj):
    removed = 0
    used_groups = {}
    for vert in obj.data.vertices:
        for group in vert.groups:
            group_index = group.group
            if group_index not in used_groups:
                used_groups[group_index] = obj.vertex_groups[group_index]

    for group in obj.vertex_groups:
        if group not in used_groups.values():
            obj.vertex_groups.remove(group)
            removed += 1
        
    return removed


def redefine_vertex_group(obj):
    group = obj.vertex_groups.active
    if group is None:
        return
    
    group_name = group.name
    
    obj.vertex_groups.remove(group)
    obj.vertex_groups.new(name=group_name)
    
    bpy.ops.object.vertex_group_assign()