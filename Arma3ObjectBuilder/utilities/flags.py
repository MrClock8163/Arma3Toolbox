import bpy
import bmesh


def get_layer_flags_vertex(bm, create = True):
    layer = bm.verts.layers.int.get("a3ob_flags_vertex")
    if not layer and create:
        layer = bm.verts.layers.int.new("a3ob_flags_vertex")
    
    return layer


def get_layer_flags_face(bm, create = True):
    layer = bm.faces.layers.int.get("a3ob_flags_face")
    if not layer and create:
        layer = bm.faces.layers.int.new("a3ob_flags_face")
    
    return layer


def clear_layer_flags_vertex(bm):
    layer = bm.verts.layers.int.get("a3ob_flags_vertex")
    if not layer:
        return

    bm.verts.layers.int.remove(layer)


def clear_layer_flags_face(bm):
    layer = bm.faces.layers.int.get("a3ob_flags_face")
    if not layer:
        return

    bm.faces.layers.int.remove(layer)


def remove_group_vertex(obj, group_id):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    layer = get_layer_flags_vertex(bm)
    
    for vertex in bm.verts:
        if vertex[layer] >= group_id:
            vertex[layer] -= 1


def assign_group_vertex(obj, group_id):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    layer = get_layer_flags_vertex(bm)
    
    for vertex in bm.verts:
        if vertex.select:
            vertex[layer] = group_id
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def select_group_vertex(obj, group_id, select = True):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    layer = get_layer_flags_vertex(bm)
    
    for vertex in bm.verts:
        if vertex[layer] == group_id:
            vertex.select = select
    
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def remove_group_face(obj, group_id):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.faces.ensure_lookup_table()
    
    layer = get_layer_flags_face(bm)
    
    for face in bm.faces:
        if face[layer] >= group_id:
            face[layer] -= 1


def assign_group_face(obj, group_id):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.faces.ensure_lookup_table()
    
    layer = get_layer_flags_face(bm)
    
    for face in bm.faces:
        if face.select:
            face[layer] = group_id
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def select_group_face(obj, group_id, select = True):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.faces.ensure_lookup_table()
    
    layer = get_layer_flags_face(bm)
    
    for face in bm.faces:
        if face[layer] == group_id:
            face.select = select
    
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)