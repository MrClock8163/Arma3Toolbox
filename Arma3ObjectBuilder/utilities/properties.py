import bpy
import bmesh

from . import generic as utils
from . import lod as lodutils


def can_edit_mass(context):
    obj = context.active_object
    return len(context.selected_objects) == 1 and obj and obj.type == 'MESH' and obj.mode == 'EDIT' 


def get_selection_mass(self):
    mesh = self.data
    
    if mesh.vertex_layers_float.get("a3ob_mass") is None:
        return 0
    
    bm = bmesh.from_edit_mesh(mesh)
    layer = bm.verts.layers.float.get("a3ob_mass")
    
    mass = 0
    for vertex in bm.verts:
        if vertex.select:
            mass += vertex[layer]
        
    return round(mass, 3)


def set_selection_mass(self, value):
    mesh = self.data
    bm = bmesh.from_edit_mesh(mesh)
    
    layer = bm.verts.layers.float.get("a3ob_mass")
    if layer is None:
        layer = bm.verts.layers.float.new("a3ob_mass")
        
    verts = [vertex for vertex in bm.verts if vertex.select]
    if len(verts) == 0:
        return
    
    current_mass = get_selection_mass(self)
    diff = value - current_mass
    correction = diff / len(verts)
    
    for vertex in verts:
        vertex[layer] = round(vertex[layer] + correction, 3)
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def set_selection_mass_each(obj, value):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    
    layer = bm.verts.layers.float.get("a3ob_mass")
    if layer is None:
        layer = bm.verts.layers.float.new("a3ob_mass")
        
    for vertex in bm.verts:
        if vertex.select:
            vertex[layer] = round(value, 3)

   
def set_selection_mass_distribute(obj, value):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    
    layer = bm.verts.layers.float.get("a3ob_mass")
    if layer is None:
        layer = bm.verts.layers.float.new("a3ob_mass")
        
    verts = [vertex for vertex in bm.verts if vertex.select]
    if len(verts) == 0:
        return
        
    vertex_value = value / len(verts)
    for vertex in verts:
        vertex[layer] = vertex_value


def clear_selection_masses(obj):
    mesh = obj.data
    
    layer = mesh.vertex_layers_float.get("a3ob_mass")
    if layer is None:
        return 
    
    bm = bmesh.from_edit_mesh(mesh)
    layer = bm.verts.layers.float.get("a3ob_mass")
    bm.verts.layers.float.remove(layer)
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def calculate_volume(bm):
    loops = bm.calc_loop_triangles()
    
    volume = 0
    for face in loops:
        v1 = face[0].vert.co
        v2 = face[1].vert.co
        v3 = face[2].vert.co
        volume += v1.dot(v2.cross(v3)) / 6.0
            
    return volume
    
def set_selection_mass_density(obj, density):
    utils.force_mode_object()
    
    bpy.ops.mesh.separate(type='LOOSE')
    
    components = bpy.context.selected_objects
    
    for component_object in components:
        if len(component_object.data.polygons) == 0:
            continue
            
        bm = bmesh.new()
        bm.from_mesh(component_object.data)
        
        volume = calculate_volume(bm)
        vertex_mass = volume * density / len(bm.verts)
        
        layer = bm.verts.layers.float.get("a3ob_mass")
        if not layer:
            layer = bm.verts.layers.float.new("a3ob_mass")
            
        for vertex in bm.verts:
            vertex[layer] = vertex_mass
            
        bm.to_mesh(component_object.data)
        bm.free()
    
    if len(components) > 1:
        ctx = bpy.context.copy()
        ctx["selected_objects"] = components
        ctx["selected_editable_objects"] = components
        ctx["active_object"] = obj
        
        bpy.ops.object.join(ctx)
        
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    contiguous = lodutils.is_contiguous_mesh(bm)
    bm.free()
    
    utils.force_mode_edit()
    
    return contiguous


def add_namedprop(obj, key, value):
    object_props = obj.a3ob_properties_object
    item = object_props.properties.add()
    item.name = key
    item.value = value
    object_props.property_index = len(object_props.properties) - 1    