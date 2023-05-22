import bpy

from ..utilities import generic as utils
from ..utilities import data
from ..utilities import proxy as proxyutils


class A3OB_OT_proxy_add(bpy.types.Operator):
    """Add Arma 3 proxy object and parent to the active object"""
    
    bl_idname = "a3ob.proxy_add"
    bl_label = "Arma 3 proxy"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'OBJECT' and obj.parent == None and not obj.a3ob_properties_object_proxy.is_a3_proxy
        
    def execute(self, context):
        obj = context.active_object
        proxy_object = proxyutils.create_proxy()
        proxy_object.location = context.scene.cursor.location
        obj.users_collection[0].objects.link(proxy_object)
        proxy_object.parent = obj
        proxy_object.matrix_parent_inverse = obj.matrix_world.inverted()
        return {'FINISHED'}


class A3OB_OT_proxy_common(bpy.types.Operator):
    """Paste a common proxy model path"""
    
    bl_idname = "a3ob.proxy_common"
    bl_label = "Common Proxy"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        
        return obj.type == 'MESH' and obj.a3ob_properties_object_proxy.is_a3_proxy
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.a3ob_proxy_common.clear()
        
        common_proxies = utils.get_common_proxies(context)
        for proxy in common_proxies:
            item = wm.a3ob_proxy_common.add()
            item.name = proxy
            item.path = utils.replace_slashes(common_proxies[proxy])
        
        wm.a3ob_proxy_common_index = 0
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        layout.template_list("A3OB_UL_common_proxies", "A3OB_proxies_common", context.window_manager, "a3ob_proxy_common", context.window_manager, "a3ob_proxy_common_index")
        
        selectionIndex = wm.a3ob_proxy_common_index
        if selectionIndex in range(len(wm.a3ob_proxy_common)):
            row = layout.row()
            item = wm.a3ob_proxy_common[selectionIndex]
            row.prop(item, "path", text="")
            row.enabled = False
    
    def execute(self, context):
        obj = context.object
        wm = context.window_manager
        
        if len(wm.a3ob_proxy_common) > 0 and wm.a3ob_proxy_common_index in range(len(wm.a3ob_proxy_common)):
            new_item = wm.a3ob_proxy_common[wm.a3ob_proxy_common_index]
            obj.a3ob_properties_object_proxy.proxy_path = new_item.path
            
        return {'FINISHED'}


class A3OB_OT_namedprops_add(bpy.types.Operator):
    """Add named property to the active object"""
    
    bl_idname = "a3ob.namedprops_add"
    bl_label = "Add Named Property"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        obj = context.active_object
        object_props = obj.a3ob_properties_object
        item = object_props.properties.add()
        item.name = "New property"
        item.value = "no value"
        object_props.property_index = len(object_props.properties) - 1
        
        return {'FINISHED'}


class A3OB_OT_namedprops_remove(bpy.types.Operator):
    """Remove named property from the active object"""
    
    bl_idname = "a3ob.namedprops_remove"
    bl_label = "Remove Named Property"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj.a3ob_properties_object.property_index != -1
        
    def execute(self, context):
        obj = context.active_object
        object_props = obj.a3ob_properties_object
        index = object_props.property_index
        if index != -1:
            object_props.properties.remove(index)
            if len(object_props.properties) == 0:
                object_props.property_index = -1
            elif index > len(object_props.properties) - 1:
                object_props.property_index = len(object_props.properties) - 1            
        
        return {'FINISHED'}


class A3OB_OT_namedprops_common(bpy.types.Operator):
    """Add a common named property"""
    
    bl_label = "Common Named Property"
    bl_idname = "a3ob.namedprops_common"
    
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.a3ob_namedprops_common.clear()
        
        common_namedprops = utils.get_common_namedprops(context)
        for prop in common_namedprops:
            item = wm.a3ob_namedprops_common.add()
            item.name = prop
            item.value = common_namedprops[prop]
        
        wm.a3ob_namedprops_common_index = 0
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.template_list("A3OB_UL_namedprops", "A3OB_namedprops_common", context.window_manager, "a3ob_namedprops_common", context.window_manager, "a3ob_namedprops_common_index")

    def execute(self, context):
        obj = context.object
        wm = context.window_manager
        
        if len(wm.a3ob_namedprops_common) > 0 and wm.a3ob_namedprops_common_index in range(len(wm.a3ob_namedprops_common)):
            new_item = wm.a3ob_namedprops_common[wm.a3ob_namedprops_common_index]
            object_props = obj.a3ob_properties_object
            item = object_props.properties.add()
            item.name = new_item.name
            item.value = new_item.value
            object_props.property_index = len(object_props.properties) - 1
        
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
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.a3ob_properties_object.is_a3_lod and not obj.a3ob_properties_object_proxy.is_a3_proxy
        
    def draw(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object
        
        layout = self.layout
        layout.prop(object_props, "is_a3_lod", text="Is P3D LOD", toggle=1)
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        if object_props.is_a3_lod:
            layout.prop(object_props, "lod", text="Type")
            if int(object_props.lod) in data.lod_resolution_position.keys():
                layout.prop(object_props, "resolution")


class A3OB_PT_object_mesh_namedprops(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Named Properties"
    bl_context = "data"
    bl_parent_id = "A3OB_PT_object_mesh"
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj == 'MESH' and obj.a3ob_properties_object.is_a3_lod and not obj.a3ob_properties_object_proxy.is_a3_proxy
    
    def draw(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object
        
        layout = self.layout
        row = layout.row()
        col_list = row.column()
        col_list.template_list("A3OB_UL_namedprops", "A3OB_namedprops", object_props, "properties", object_props, "property_index")
        
        if object_props.property_index in range(len(object_props.properties)):
            row_edit = col_list.row(align=True)
            prop = object_props.properties[object_props.property_index]
            row_edit.prop(prop, "name", text="")
            row_edit.prop(prop, "value", text="")
            
        col_operators = row.column(align=True)
        col_operators.operator("a3ob.namedprops_add", text="", icon='ADD')
        col_operators.operator("a3ob.namedprops_remove", text="", icon='REMOVE')
        col_operators.separator()
        col_operators.operator("a3ob.namedprops_common", icon='PASTEDOWN', text="")


class A3OB_PT_object_proxy(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Proxy Properties"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.a3ob_properties_object_proxy.is_a3_proxy and not obj.a3ob_properties_object.is_a3_lod
        
    def draw(self, context):
        obj = context.active_object
        object_props = obj.a3ob_properties_object_proxy
        
        layout = self.layout
        row = layout.row()
        row.prop(object_props, "is_a3_proxy", text="Is Arma 3 Proxy", toggle=1)
        row.enabled = False
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        layout.separator()
        row_path = layout.row(align=True)
        row_path.operator('a3ob.proxy_common', text="", icon='PASTEDOWN')
        row_path.prop(object_props, "proxy_path", text="", icon='MESH_CUBE')
        layout.prop(object_props, "proxy_index", text="")


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(A3OB_OT_proxy_add.bl_idname, icon='EMPTY_ARROWS')


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