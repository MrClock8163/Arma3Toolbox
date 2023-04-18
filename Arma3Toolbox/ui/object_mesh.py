import bpy
from ..utilities import data

class A3OB_OT_namedprops_add(bpy.types.Operator):
    '''Add named property to the active object'''
    
    bl_idname = "a3ob.namedprops_add"
    bl_label = "Add named property"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls,context):
        return True
        
    def execute(self,context):
        activeObj = context.active_object
        OBprops = activeObj.a3ob_properties_object
        
        item = OBprops.properties.add()
        item.name = "New property"
        item.value = "no value"
        
        OBprops.propertyIndex = len(OBprops.properties)-1
        
        return {'FINISHED'}

class A3OB_OT_namedprops_remove(bpy.types.Operator):
    '''Remove named property from the active object'''
    
    bl_idname = "a3ob.namedprops_remove"
    bl_label = "Remove named property"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls,context):
        activeObj = context.active_object
        
        return activeObj.a3ob_properties_object.propertyIndex != -1
        
    def execute(self,context):
        activeObj = context.active_object
        OBprops = activeObj.a3ob_properties_object
        
        index = OBprops.propertyIndex
        
        if index != -1:
            OBprops.properties.remove(index)
            if len(OBprops.properties) == 0:
                OBprops.propertyIndex = -1
            elif index > len(OBprops.properties)-1:
                OBprops.propertyIndex = len(OBprops.properties)-1
            
            # if index > len(OB)
            
        
        return {'FINISHED'}

class A3OB_UL_namedprops(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=f"{item.name} = {item.value}")

class A3OB_PT_object_mesh(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: LOD properties"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls,context):
        return (context.active_object
            and context.active_object.select_get() == True
            and context.active_object.type == 'MESH'
            and not context.active_object.a3ob_properties_object_proxy.isArma3Proxy
            
        )
        
    def draw(self,context):
        activeObj = context.active_object
        OBprops = activeObj.a3ob_properties_object
        
        layout = self.layout
        
        
        layout.prop(OBprops,"isArma3LOD",text="Is P3D LOD",toggle=1)
        layout.use_property_split = True
        
        if OBprops.isArma3LOD:
            layout.prop(OBprops,"LOD",text="Type")
            
            if int(OBprops.LOD) in data.LODtypeResolutionPosition.keys():
                layout.prop(OBprops,"resolution")
        
class A3OB_PT_object_mesh_namedprops(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Named properties"
    bl_context = "data"
    bl_parent_id = 'A3OB_PT_object_mesh'
    
    @classmethod
    def poll(cls,context):
        activeObj = context.active_object
        
        return activeObj.a3ob_properties_object.isArma3LOD and not activeObj.a3ob_properties_object_proxy.isArma3Proxy
    
    def draw(self,context):
        activeObj = context.active_object
        OBprops = activeObj.a3ob_properties_object
        layout = self.layout
        
        row = layout.row()
        col1 = row.column()
        col1.template_list('A3OB_UL_namedprops',"A3OB_namedprops",OBprops,"properties",OBprops,"propertyIndex")
        
        if OBprops.propertyIndex in range(len(OBprops.properties)):
            rowEdit = col1.row(align=True)
            prop = OBprops.properties[OBprops.propertyIndex]
            rowEdit.prop(prop,"name",text="")
            rowEdit.prop(prop,"value",text="")
            
        col2 = row.column(align=True)
        col2.operator("a3ob.namedprops_add",text="",icon='ADD')
        col2.operator("a3ob.namedprops_remove",text="",icon='REMOVE')
        
class A3OB_PT_object_proxy(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: proxy properties"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls,context):
        activeObj = context.active_object
        
        return activeObj.type == 'MESH' and activeObj.a3ob_properties_object_proxy.isArma3Proxy
        
        # return (context.active_object
            # and context.active_object.select_get() == True
            # and context.active_object.type == 'MESH'
        # )
        
    def draw(self,context):
        activeObj = context.active_object
        OBprops = activeObj.a3ob_properties_object_proxy
        layout = self.layout
        
        row = layout.row()
        row.prop(OBprops,"isArma3Proxy",text="Is Arma 3 proxy",toggle=1)
        row.enabled = False
        
        layout.use_property_split = True
        
        layout.separator()
        layout.prop(OBprops,"proxyPath",icon='MESH_CUBE',text="")
        layout.prop(OBprops,"proxyIndex",text="")
        
classes = (
    A3OB_OT_namedprops_add,
    A3OB_OT_namedprops_remove,
    A3OB_UL_namedprops,
    A3OB_PT_object_mesh,
    A3OB_PT_object_mesh_namedprops,
    A3OB_PT_object_proxy
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)