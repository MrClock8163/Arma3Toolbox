import bmesh


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
        
    bmesh.update_edit_mesh(mesh, False, False)


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
    bmesh.update_edit_mesh(mesh)


def add_namedprop(obj, key, value):
    object_props = obj.a3ob_properties_object
    item = object_props.properties.add()
    item.name = key
    item.value = value
    object_props.property_index = len(object_props.properties) - 1    