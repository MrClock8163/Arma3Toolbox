import bpy

from ..utilities import generic as utils


class A3OB_OT_proxy_vgroup_add(bpy.types.Operator):
    """Add vertex group to Arma 3 proxy"""

    bl_idname = "a3ob.proxy_vgroups_add"
    bl_label = "Add Vertex Group"
    bl_options = {'REGISTER'}

    obj: bpy.props.StringProperty(
        name = "Proxy Object",
        description = "Proxy object to add vertex group to"
    )

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = context.scene.objects.get(self.obj, context.active_object)
        if not obj or obj.type != 'EMPTY' or not obj.a3ob_properties_object_proxy.is_a3_proxy:
            self.report({'INFO'}, "Cannot add vertex group")
            return {'FINISHED'}
        
        obj.a3ob_properties_object_proxy.vgroups.add().name = "Group"

        return {'FINISHED'}


class A3OB_OT_proxy_vgroup_remove(bpy.types.Operator):
    """Remove vertex group from Arma 3 proxy"""

    bl_idname = "a3ob.proxy_vgroups_remove"
    bl_label = "Remove Vertex Group"
    bl_options = {'REGISTER'}

    obj: bpy.props.StringProperty(
        name = "Proxy Object",
        description = "Proxy object to remove vertex group from"
    )

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = context.scene.objects.get(self.obj, context.active_object)
        if not obj or obj.type != 'EMPTY' or not obj.a3ob_properties_object_proxy.is_a3_proxy:
            self.report({'ERROR'}, "Object is not proxy")
            return {'FINISHED'}
        
        proxy_props = obj.a3ob_properties_object_proxy
        if not utils.is_valid_idx(proxy_props.vgroups_index, proxy_props.vgroups):
            return {'FINISHED'}
        
        proxy_props.vgroups.remove(proxy_props.vgroups_index)

        return {'FINISHED'}


class A3OB_OT_proxy_vgroup_clear(bpy.types.Operator):
    """Clear all vertex group from Arma 3 proxy"""

    bl_idname = "a3ob.proxy_vgroups_clear"
    bl_label = "Clear Vertex Groups"
    bl_options = {'REGISTER'}

    obj: bpy.props.StringProperty(
        name = "Proxy Object",
        description = "Proxy object to clear vertex groups from"
    )

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = context.scene.objects.get(self.obj, context.active_object)
        if not obj or obj.type != 'EMPTY' or not obj.a3ob_properties_object_proxy.is_a3_proxy:
            self.report({'ERROR'}, "Object is not proxy")
            return {'FINISHED'}
        
        obj.a3ob_properties_object_proxy.vgroups.clear()

        return {'FINISHED'}


class A3OB_OT_proxy_add(bpy.types.Operator):
    """Add an Arma 3 proxy object and parent to the active object"""
    
    bl_idname = "a3ob.proxy_add"
    bl_label = "Add Proxy"
    bl_options = {'REGISTER'}

    parent: bpy.props.StringProperty(
        name = "Parent LOD Object",
        description = "Name of the LOD object to parent the new proxy to"
    )
    path: bpy.props.StringProperty (
        name = "Proxy Path",
        description = "Proxy file path to assign to new proxy object"
    )
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        obj = context.scene.objects.get(self.parent, context.active_object)
        if not obj:
            self.report({'INFO'}, "Cannot add new proxy object without parent")
            return {'FINISHED'}

        proxy_object = bpy.data.objects.new("proxy", None)
        proxy_object.empty_display_type = 'ARROWS'
        proxy_object.location = context.scene.cursor.location
        obj.users_collection[0].objects.link(proxy_object)
        proxy_object.parent = obj
        proxy_object.matrix_parent_inverse = obj.matrix_world.inverted()
        proxy_object.a3ob_properties_object_proxy.proxy_path = self.path
        proxy_object.a3ob_properties_object_proxy.is_a3_proxy = True
        return {'FINISHED'}


class A3OB_OT_proxy_remove(bpy.types.Operator):
    """Remove an Arma 3 proxy object from the active object"""

    bl_idname = "a3ob.proxy_remove"
    bl_label = "Remove Proxy"
    bl_options = {'REGISTER'}

    obj: bpy.props.StringProperty(
        name = "Proxy Object",
        description = "Name of the proxy object to remove"
    )

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = context.scene.objects.get(self.obj, context.active_object)
        if not obj or obj.type != 'EMPTY' or not obj.a3ob_properties_object_proxy.is_a3_proxy:
            self.report({'ERROR'}, "Cannot remove proxy")
            return {'FINISHED'}
        
        bpy.data.objects.remove(obj)

        return {'FINISHED'}


class A3OB_OT_paste_common_proxy(bpy.types.Operator):
    """Paste a common proxy model path"""
    
    bl_idname = "a3ob.paste_common_proxy"
    bl_label = "Paste Common Proxy"
    bl_options = {'REGISTER'}

    obj: bpy.props.StringProperty(
        name = "Proxy Object",
        description = "Proxy object to assign path to"
    )
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        scene_props = context.scene.a3ob_commons
        scene_props.proxies.clear()
        
        proxies, custom = utils.get_common("proxies")
        if custom is None:
            self.report({'ERROR'}, "Custom data JSON could not be loaded")
        else:
            proxies.update(custom)

        for name in proxies:
            item = scene_props.proxies.add()
            item.name = name
            item.path = utils.replace_slashes(proxies[name])
        
        scene_props.proxies_index = 0
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        scene_props = context.scene.a3ob_commons
        layout = self.layout
        layout.template_list("A3OB_UL_common_proxies", "A3OB_proxies_common", scene_props, "proxies", scene_props, "proxies_index")
        
        selection_index = scene_props.proxies_index
        if utils.is_valid_idx(selection_index, scene_props.proxies):
            row = layout.row()
            item = scene_props.proxies[selection_index]
            row.prop(item, "path", text="")
            row.enabled = False
    
    def execute(self, context):
        obj = context.scene.objects.get(self.obj, context.object)
        if not obj or obj.type != 'EMPTY' or not obj.a3ob_properties_object_proxy.is_a3_proxy:
            self.report({'INFO'}, "No proxy object was selected")
            return {'FINISHED'}

        scene_props = context.scene.a3ob_commons
        
        if utils.is_valid_idx(scene_props.proxies_index, scene_props.proxies):
            new_item = scene_props.proxies[scene_props.proxies_index]
            obj.a3ob_properties_object_proxy.proxy_path = new_item.path
            
        return {'FINISHED'}


class A3OB_UL_proxy_vertex_groups(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", icon='GROUP_VERTEX', emboss=False)
    
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        
        sorter = getattr(data, propname)
        flt_neworder = helper_funcs.sort_items_by_name(sorter, "name")
        
        return flt_flags, flt_neworder


class A3OB_PT_object_empty_proxy(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Proxy Properties"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    doc_url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/proxy"
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'EMPTY' and obj.a3ob_properties_object_proxy.is_a3_proxy
        
    def draw_header(self, context):
        utils.draw_panel_header(self)
        
    def draw(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_proxy
        
        layout = self.layout
        row = layout.row(align=True)
        col_enable = row.column(align=True)
        col_enable.prop(object_props, "is_a3_proxy", text="Is P3D Proxy", toggle=True)
        col_enable.enabled = False
        
        row_select = layout.row(align=True)
        op = row_select.operator("a3ob.select_object", text="Select Parent LOD", icon='RESTRICT_SELECT_OFF')
        if obj.parent and obj.parent.type == 'MESH' and obj.parent.a3ob_properties_object.is_a3_lod:
            op.object_name = obj.parent.name
            op.identify_lod = False
        else:
            row_select.enabled = False
        
        layout.separator()
        row_path = layout.row(align=True)
        row_path.operator("a3ob.paste_common_proxy", text="", icon='PASTEDOWN')
        row_path.prop(object_props, "proxy_path", text="", icon='MESH_CUBE')
        layout.prop(object_props, "proxy_index")

        row_vgroups = layout.row()
        col_list = row_vgroups.column()
        col_list.template_list("A3OB_UL_proxy_vertex_groups", "A3OB_proxy_groups", object_props, "vgroups", object_props, "vgroups_index")

        col_operators = row_vgroups.column(align=True)
        col_operators.operator("a3ob.proxy_vgroups_add", text="", icon='ADD')
        col_operators.operator("a3ob.proxy_vgroups_remove", text="", icon='REMOVE')
        col_operators.separator()
        col_operators.operator("a3ob.proxy_vgroups_clear", icon='TRASH', text="")


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(A3OB_OT_proxy_add.bl_idname, text="Arma 3 Proxy", icon_value=utils.get_icon("op_proxy_add"))


classes = (
    A3OB_OT_proxy_vgroup_add,
    A3OB_OT_proxy_vgroup_remove,
    A3OB_OT_proxy_vgroup_clear,
    A3OB_OT_proxy_add,
    A3OB_OT_proxy_remove,
    A3OB_OT_paste_common_proxy,
    A3OB_UL_proxy_vertex_groups,
    A3OB_PT_object_empty_proxy,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(menu_func)
    
    print("\t" + "UI: empty properties")


def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: empty properties")