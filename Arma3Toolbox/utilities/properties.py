import bpy
import bmesh

def canEditMass(context):
    obj = context.active_object
    return len(context.selected_objects) == 1 and obj and obj.type == 'MESH' and obj.mode == 'EDIT' 
    
def selectionMassGet(self):
    mesh = self.data
    
    if mesh.vertex_layers_float.get("a3ob_mass") is None:
        return 0
    
    bm = bmesh.from_edit_mesh(mesh)
    
    layer = bm.verts.layers.float.get("a3ob_mass")
    
    mass = 0
    for v in bm.verts:
        if v.select:
            mass += v[layer]
        
    return round(mass,3) 
    
def selectionMassSet(self,value):
    mesh = self.data
    
    bm = bmesh.from_edit_mesh(mesh)
    
    layer = bm.verts.layers.float.get("a3ob_mass")
    if layer is None:
        layer = bm.verts.layers.float.new("a3ob_mass")
        
    verts = [v for v in bm.verts if v.select]
    
    if len(verts) == 0:
        return
    
    currentMass = selectionMassGet(self)
    diff = value - currentMass
    
    correction = diff/len(verts)
    
    for v in verts:
        v[layer] = round(v[layer] + correction,3)
        
    bmesh.update_edit_mesh(mesh,False,False)
    
def selectionMassSetEach(obj,value):
    mesh = obj.data
    
    bm = bmesh.from_edit_mesh(mesh)
    
    layer = bm.verts.layers.float.get("a3ob_mass")
    if layer is None:
        layer = bm.verts.layers.float.new("a3ob_mass")
        
    for vert in bm.verts:
        if vert.select:
            vert[layer] = round(value,3)
            
def selectionMassDistribute(obj,value):
    mesh = obj.data
    
    bm = bmesh.from_edit_mesh(mesh)
    
    layer = bm.verts.layers.float.get("a3ob_mass")
    if layer is None:
        layer = bm.verts.layers.float.new("a3ob_mass")
        
    verts = [v for v in bm.verts if v.select]
    
    if len(verts) == 0:
        return
        
    vertValue = value / len(verts)
        
    for v in verts:
        v[layer] = vertValue
        
def clearMasses(obj):
    mesh = obj.data
    
    layer = mesh.vertex_layers_float.get("a3ob_mass")
    if layer is None:
        return 
    
    bm = bmesh.from_edit_mesh(mesh)
    
    layer = bm.verts.layers.float.get("a3ob_mass")
    bm.verts.layers.float.remove(layer)
    
    bmesh.update_edit_mesh(mesh)
    
def addNamedProperty(obj,key,value):
    OBprops = obj.a3ob_properties_object
    
    item = OBprops.properties.add()
    item.name = key
    item.value = value
    
    OBprops.propertyIndex = len(OBprops.properties)-1    