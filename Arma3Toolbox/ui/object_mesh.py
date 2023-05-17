import bpy
from ..utilities import generic as utils
from ..utilities import data
from ..utilities import proxy as proxyutils

class A3OB_OT_proxy_add(bpy.types.Operator):
    '''Add Arma 3 proxy object and parent to the active object'''
    
    bl_idname = "a3ob.proxy_add"
    bl_label = "Arma 3 proxy"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls,context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'OBJECT' and obj.parent == None and not obj.a3ob_properties_object_proxy.isArma3Proxy
        
    def execute(self,context):
        activeObj = context.active_object
        
        obj = proxyutils.createProxy()
        obj.location = context.scene.cursor.location
        activeObj.users_collection[0].objects.link(obj)
        obj.parent = activeObj
        
        return {'FINISHED'}
        
class A3OB_OT_proxy_common(bpy.types.Operator):
    '''Paste a common proxy model path'''
    
    bl_idname = "a3ob.proxy_common"
    bl_label = "Common Proxy"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls,context):
        activeObj = context.active_object
        
        return activeObj.type == 'MESH' and activeObj.a3ob_properties_object_proxy.isArma3Proxy
    
    def invoke(self,context,event):
        obj = context.object
        wm = context.window_manager
        
        wm.a3ob_proxy_common.clear()
        
        commonProxies = utils.get_common_proxies(context)
        for proxy in commonProxies:
            item = wm.a3ob_proxy_common.add()
            item.name = proxy
            item.path = utils.replace_slashes(commonProxies[proxy])
        
        wm.a3ob_proxy_common_index = 0
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self,context):
        wm = context.window_manager
        layout = self.layout
        layout.template_list('A3OB_UL_common_proxies',"A3OB_proxies_common",context.window_manager,'a3ob_proxy_common',context.window_manager,'a3ob_proxy_common_index')
        
        selectionIndex = wm.a3ob_proxy_common_index
        if selectionIndex in range(len(wm.a3ob_proxy_common)):
            row = layout.row()
            item = wm.a3ob_proxy_common[selectionIndex]
            row.prop(item,"path",text="")
            row.enabled = False
    
    def execute(self,context):
        obj = context.object
        wm = context.window_manager
        
        if len(wm.a3ob_proxy_common) > 0 and wm.a3ob_proxy_common_index in range(len(wm.a3ob_proxy_common)):
            newItem = wm.a3ob_proxy_common[wm.a3ob_proxy_common_index]
            
            obj.a3ob_properties_object_proxy.proxyPath = newItem.path
            
        return {'FINISHED'}
    
class A3OB_OT_namedprops_add(bpy.types.Operator):
    '''Add named property to the active object'''
    
    bl_idname = "a3ob.namedprops_add"
    bl_label = "Add Named Property"
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
    bl_label = "Remove Named Property"
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
        
        return {'FINISHED'}
        
class A3OB_OT_namedprops_common(bpy.types.Operator):
    '''Add a common named property'''
    
    bl_label = "Common Named Property"
    bl_idname = "a3ob.namedprops_common"
    
    @classmethod
    def poll(cls,context):
        return context.object is not None
    
    def invoke(self,context,event):
        obj = context.object
        wm = context.window_manager
        
        wm.a3ob_namedprops_common.clear()
        
        customNamedprops = utils.get_common_namedprops(context)
        for prop in customNamedprops:
            item = wm.a3ob_namedprops_common.add()
            item.name = prop
            item.value = customNamedprops[prop]
        
        wm.a3ob_namedprops_common_index = 0
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self,context):
        layout = self.layout
        layout.template_list('A3OB_UL_namedprops',"A3OB_namedprops_common",context.window_manager,'a3ob_namedprops_common',context.window_manager,'a3ob_namedprops_common_index')

    def execute(self,context):
        obj = context.object
        wm = context.window_manager
        
        if len(wm.a3ob_namedprops_common) > 0 and wm.a3ob_namedprops_common_index in range(len(wm.a3ob_namedprops_common)):
            newItem = wm.a3ob_namedprops_common[wm.a3ob_namedprops_common_index]
            
            OBprops = obj.a3ob_properties_object
            item = OBprops.properties.add()
            item.name = newItem.name
            item.value = newItem.value
            
            OBprops.propertyIndex = len(OBprops.properties)-1
        
        return {'FINISHED'}

class A3OB_UL_namedprops(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=f"{item.name} = {item.value}")
        
class A3OB_UL_common_proxies(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)

class A3OB_PT_object_mesh(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: LOD Properties"
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
        layout.use_property_decorate = False
        
        if OBprops.isArma3LOD:
            layout.prop(OBprops,"LOD",text="Type")
            
            if int(OBprops.LOD) in data.LODtypeResolutionPosition.keys():
                layout.prop(OBprops,"resolution")
        
class A3OB_PT_object_mesh_namedprops(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Named Properties"
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
        col2.separator()
        col2.operator("a3ob.namedprops_common",icon='PASTEDOWN',text="")
        
class A3OB_PT_object_proxy(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Proxy Properties"
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
        row.prop(OBprops,"isArma3Proxy",text="Is Arma 3 Proxy",toggle=1)
        row.enabled = False
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        layout.separator()
        path_row = layout.row(align=True)
        path_row.operator('a3ob.proxy_common',text="",icon='PASTEDOWN')
        path_row.prop(OBprops,"proxyPath",icon='MESH_CUBE',text="")
        layout.prop(OBprops,"proxyIndex",text="")
        
def menu_func(self,context):
    self.layout.separator()
    self.layout.operator(A3OB_OT_proxy_add.bl_idname,icon='EMPTY_ARROWS')
        
classes = (
    A3OB_OT_proxy_add,
    A3OB_OT_proxy_common,
    A3OB_OT_namedprops_add,
    A3OB_OT_namedprops_remove,
    A3OB_OT_namedprops_common,
    A3OB_UL_namedprops,
    A3OB_UL_common_proxies,
    A3OB_PT_object_mesh,
    A3OB_PT_object_mesh_namedprops,
    A3OB_PT_object_proxy
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(menu_func)
    
def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)