# Backend functions of the utility functions.


import re

import bpy
import bmesh

from . import generic as utils
from . import compat as computils


def find_components(obj):
    obj.update_from_editmode()
    mesh = obj.data
    
    for group in obj.vertex_groups:
        if re.match("component\d+", group.name, re.IGNORECASE):
            obj.vertex_groups.remove(group)
    
    lookup, components = utils.get_components(mesh)
    
    verts = {i: [] for i in range(len(components))}
    for id in lookup:
        verts[lookup[id]].append(id)
    
    for component in verts:
        group = obj.vertex_groups.new(name="Component%02d" % (component + 1))
        group.add(verts[component], 1, 'REPLACE')
    
    return component + 1


def component_convex_hull(obj):
    utils.force_mode_object()
    
    # Remove pre-existing component selections
    for group in obj.vertex_groups:
        if re.match("component\d+", group.name, re.IGNORECASE):
            obj.vertex_groups.remove(group)
    
    # Split mesh
    bpy.ops.mesh.separate(type='LOOSE')
    
    # Iterate components
    components = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
    component_id = 0
    for component_object in components:
        component_id += 1
        
        bpy.context.view_layer.objects.active = component_object
            
        if len(component_object.data.vertices) < 4: # Ignore proxies
            continue
        
        convex_hull()
            
        group = component_object.vertex_groups.new(name=("Component%02d" % component_id))
        group.add([vert.index for vert in component_object.data.vertices], 1, 'REPLACE')
        
    if len(components) > 0:
        ctx = bpy.context.copy()
        ctx["selected_objects"] = components
        ctx["selected_editable_objects"] = components
        ctx["active_object"] = obj
        
        computils.call_operator_ctx(bpy.ops.object.join, ctx)
        
    bpy.context.view_layer.objects.active = obj
    
    return component_id


def convex_hull():
    utils.force_mode_edit()
    
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='OBJECT')


def check_closed():
    utils.force_mode_edit()
    
    bpy.ops.mesh.select_mode(type='EDGE')
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
    
    return obj.name, count_concave


def cleanup_vertex_groups(obj):
    obj.update_from_editmode()
    
    removed = 0
    used_groups = {}
    for vert in obj.data.vertices:
        for group in vert.groups:
            group_index = group.group
            used_groups[group_index] = obj.vertex_groups[group_index]

    for group in obj.vertex_groups:
        if group not in used_groups.values():
            obj.vertex_groups.remove(group)
            removed += 1
        
    return removed


def redefine_vertex_group(obj, weight):
    obj.update_from_editmode()
    mesh = obj.data
    
    group = obj.vertex_groups.active
    if group is None:
        return
    
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.verts.layers.deform.verify()
    deform = bm.verts.layers.deform.active
    
    for vert in bm.verts:
        if vert.select:
            vert[deform][group.index] = weight
        elif group.index in vert[deform]:
            del vert[deform][group.index]
        
    bmesh.update_edit_mesh(mesh)