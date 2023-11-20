import bpy
import bmesh


def get_layer_flags_vertex(bm):
    layer = bm.verts.layers.int.get("a3ob_flags_vertex")
    if not layer:
        layer = bm.verts.layers.int.new("a3ob_flags_vertex")
    
    return layer


def remove_group(obj, group_id):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    layer = get_layer_flags_vertex(bm)
    
    for vertex in bm.verts:
        if vertex[layer] >= group_id:
            vertex[layer] -= 1


def assign_group(obj, group_id):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    layer = get_layer_flags_vertex(bm)
    
    for vertex in bm.verts:
        if vertex.select:
            vertex[layer] = group_id
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def select_group(obj, group_id, select = True):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    layer = get_layer_flags_vertex(bm)
    
    for vertex in bm.verts:
        if vertex[layer] == group_id:
            vertex.select = select
    
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)