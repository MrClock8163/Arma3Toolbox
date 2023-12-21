import bpy

from ..utilities import generic as utils
from ..utilities import data
from ..utilities import proxy as proxyutils
from ..utilities import flags as flagutils


class A3OB_OT_proxy_add(bpy.types.Operator):
    """Add Arma 3 proxy object and parent to the active object"""
    
    bl_idname = "a3ob.proxy_add"
    bl_label = "Arma 3 proxy"
    bl_options = {'REGISTER', 'UNDO'}
    
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
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        
        return obj and obj.type == 'MESH' and obj.a3ob_properties_object_proxy.is_a3_proxy
    
    def invoke(self, context, event):
        scene = context.scene
        scene.a3ob_proxy_common.clear()
        
        common_proxies = utils.get_common_proxies()
        for proxy in common_proxies:
            item = scene.a3ob_proxy_common.add()
            item.name = proxy
            item.path = utils.replace_slashes(common_proxies[proxy])
        
        scene.a3ob_proxy_common_index = 0
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.template_list("A3OB_UL_common_proxies", "A3OB_proxies_common", scene, "a3ob_proxy_common", scene, "a3ob_proxy_common_index")
        
        selectionIndex = scene.a3ob_proxy_common_index
        if selectionIndex in range(len(scene.a3ob_proxy_common)):
            row = layout.row()
            item = scene.a3ob_proxy_common[selectionIndex]
            row.prop(item, "path", text="")
            row.enabled = False
    
    def execute(self, context):
        obj = context.object
        scene = context.scene
        
        if len(scene.a3ob_proxy_common) > 0 and scene.a3ob_proxy_common_index in range(len(scene.a3ob_proxy_common)):
            new_item = scene.a3ob_proxy_common[scene.a3ob_proxy_common_index]
            obj.a3ob_properties_object_proxy.proxy_path = new_item.path
            
        return {'FINISHED'}


class A3OB_OT_namedprops_add(bpy.types.Operator):
    """Add named property to the active object"""
    
    bl_idname = "a3ob.namedprops_add"
    bl_label = "Add Named Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH'
        
    def execute(self, context):
        obj = context.object
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
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.a3ob_properties_object.property_index != -1
        
    def execute(self, context):
        obj = context.object
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
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH'
    
    def invoke(self, context, event):
        scene = context.scene
        scene.a3ob_namedprops_common.clear()
        
        common_namedprops = utils.get_common_namedprops()
        for prop in common_namedprops:
            item = scene.a3ob_namedprops_common.add()
            item.name = prop
            item.value = common_namedprops[prop]
        
        scene.a3ob_namedprops_common_index = 0
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.template_list("A3OB_UL_namedprops", "A3OB_namedprops_common", scene, "a3ob_namedprops_common", scene, "a3ob_namedprops_common_index")

    def execute(self, context):
        obj = context.object
        scene = context.scene
        
        if len(scene.a3ob_namedprops_common) > 0 and scene.a3ob_namedprops_common_index in range(len(scene.a3ob_namedprops_common)):
            new_item = scene.a3ob_namedprops_common[scene.a3ob_namedprops_common_index]
            object_props = obj.a3ob_properties_object
            item = object_props.properties.add()
            item.name = new_item.name
            item.value = new_item.value
            object_props.property_index = len(object_props.properties) - 1
        
        return {'FINISHED'}


class A3OB_OT_flags_vertex_add(bpy.types.Operator):
    """Add a new vertex flag group to the active object"""
    
    bl_label = "Add Vertex Flag Group"
    bl_idname = "a3ob.flags_vertex_add"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH'
    
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        item = flag_props.vertex.add()
        item.name = "New Flag Group"
        item.set_flag(utils.get_addon_preferences().flag_vertex)
        flag_props.vertex_index = len(flag_props.vertex) - 1
        
        return {'FINISHED'}


class A3OB_OT_flags_vertex_remove(bpy.types.Operator):
    """Remove the active vertex flag group from the active object"""
    
    bl_idname = "a3ob.flags_vertex_remove"
    bl_label = "Remove Vertex Flag Group"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.a3ob_properties_object_flags.vertex_index in range(len(obj.a3ob_properties_object_flags.vertex))
        
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        index = flag_props.vertex_index

        flag_props.vertex.remove(index)
        flag_props.vertex_index = len(flag_props.vertex) - 1            
    
        flagutils.remove_group_vertex(obj, index)
        
        return {'FINISHED'}


class A3OB_OT_flags_vertex_assign(bpy.types.Operator):
    """Assign selected vertices to the active vertex flag group"""
    
    bl_label = "Assign"
    bl_idname = "a3ob.flags_vertex_assign"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT' and obj.a3ob_properties_object_flags.vertex_index in range(len(obj.a3ob_properties_object_flags.vertex))
    
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        flagutils.assign_group_vertex(obj, flag_props.vertex_index)
        
        return {'FINISHED'}


class A3OB_OT_flags_vertex_select(bpy.types.Operator):
    """Select all vertices assigned to the active vertex flag group"""
    
    bl_label = "Select"
    bl_idname = "a3ob.flags_vertex_select"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT' and obj.a3ob_properties_object_flags.vertex_index in range(len(obj.a3ob_properties_object_flags.vertex))
    
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        flagutils.select_group_vertex(obj, flag_props.vertex_index)
        bpy.ops.mesh.select_mode(type='VERT')
        
        return {'FINISHED'}


class A3OB_OT_flags_vertex_deselect(bpy.types.Operator):
    """Deselect all selected vertices assigned to the active vertex flag group"""
    
    bl_label = "Deselect"
    bl_idname = "a3ob.flags_vertex_deselect"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT' and obj.a3ob_properties_object_flags.vertex_index in range(len(obj.a3ob_properties_object_flags.vertex))
    
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        flagutils.select_group_vertex(obj, flag_props.vertex_index, False)
        bpy.ops.mesh.select_mode(type='VERT')
        
        return {'FINISHED'}


class A3OB_OT_flags_vertex_clear(bpy.types.Operator):
    """Clear all vertex flag groups from the active object"""
    
    bl_label = "Clear"
    bl_idname = "a3ob.flags_vertex_clear"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and len(obj.a3ob_properties_object_flags.vertex) > 0
    
    def execute(self, context):
        obj = context.object
        flagutils.clear_groups_vertex(obj)

        return {'FINISHED'}


class A3OB_OT_flags_face_add(bpy.types.Operator):
    """Add a new face flag group to the active object"""
    
    bl_label = "Add Face Flag Group"
    bl_idname = "a3ob.flags_face_add"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH'
    
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        item = flag_props.face.add()
        item.name = "New Flag Group"
        item.set_flag(utils.get_addon_preferences().flag_face)
        flag_props.face_index = len(flag_props.face) - 1
        
        return {'FINISHED'}


class A3OB_OT_flags_face_remove(bpy.types.Operator):
    """Remove the active face flag group from the active object"""
    
    bl_idname = "a3ob.flags_face_remove"
    bl_label = "Remove Face Flag Group"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.a3ob_properties_object_flags.face_index in range(len(obj.a3ob_properties_object_flags.face))
        
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        index = flag_props.face_index
        
        flag_props.face.remove(index)
        flag_props.face_index = len(flag_props.face) - 1            
        
        flagutils.remove_group_face(obj, index)
        
        return {'FINISHED'}


class A3OB_OT_flags_face_assign(bpy.types.Operator):
    """Assign selected vertices to the active face flag group"""
    
    bl_label = "Assign"
    bl_idname = "a3ob.flags_face_assign"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT' and obj.a3ob_properties_object_flags.face_index in range(len(obj.a3ob_properties_object_flags.face))
    
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        flagutils.assign_group_face(obj, flag_props.face_index)
        
        return {'FINISHED'}


class A3OB_OT_flags_face_select(bpy.types.Operator):
    """Select all vertices assigned to the active face flag group"""
    
    bl_label = "Select"
    bl_idname = "a3ob.flags_face_select"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT' and obj.a3ob_properties_object_flags.face_index in range(len(obj.a3ob_properties_object_flags.face))
    
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        flagutils.select_group_face(obj, flag_props.face_index)
        bpy.ops.mesh.select_mode(type='FACE')
        
        return {'FINISHED'}


class A3OB_OT_flags_face_deselect(bpy.types.Operator):
    """Deselect all selected vertices assigned to the active face flag group"""
    
    bl_label = "Deselect"
    bl_idname = "a3ob.flags_face_deselect"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT' and obj.a3ob_properties_object_flags.face_index in range(len(obj.a3ob_properties_object_flags.face))
    
    def execute(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        flagutils.select_group_face(obj, flag_props.face_index, False)
        bpy.ops.mesh.select_mode(type='FACE')
        
        return {'FINISHED'}


class A3OB_OT_flags_face_clear(bpy.types.Operator):
    """Clear all face flag groups from the active object"""
    
    bl_label = "Clear"
    bl_idname = "a3ob.flags_face_clear"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and len(obj.a3ob_properties_object_flags.face) > 0
    
    def execute(self, context):
        obj = context.object
        flagutils.clear_groups_face(obj)

        return {'FINISHED'}


class A3OB_UL_namedprops(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text="%s = %s" % (item.name, item.value))


class A3OB_UL_common_proxies(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)


class A3OB_UL_flags_vertex(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)
        layout.label(text=("%08x" % item.get_flag()))


class A3OB_UL_flags_face(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)
        layout.label(text=("%08x" % item.get_flag()))


class A3OB_PT_object_mesh(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: LOD Properties"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and not obj.a3ob_properties_object_proxy.is_a3_proxy
        
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/lod"
        
    def draw(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object
        
        layout = self.layout
        row_toggle = layout.row(align=True)
        row_toggle.prop(object_props, "is_a3_lod", text="Is P3D LOD", toggle=True)
        
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
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.a3ob_properties_object.is_a3_lod and not obj.a3ob_properties_object_proxy.is_a3_proxy
    
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


class A3OB_PT_object_mesh_flags(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Flag Groups"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH'
    
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/flag-groups"

    def draw(self, context):
        pass


class A3OB_PT_object_mesh_flags_vertex(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Vertex Flag Groups"
    bl_context = "data"
    bl_parent_id = "A3OB_PT_object_mesh_flags"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH'
    
    def draw(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        
        layout = self.layout
        row = layout.row()
        col_list = row.column()
        col_list.template_list("A3OB_UL_flags_vertex", "A3OB_flags_vertex", flag_props, "vertex", flag_props, "vertex_index")
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        if flag_props.vertex_index in range(len(flag_props.vertex)):
            if obj.mode == 'EDIT':
                row_operators = layout.row(align=True)
                row_operators.operator("a3ob.flags_vertex_assign")
                row_operators.operator("a3ob.flags_vertex_select")
                row_operators.operator("a3ob.flags_vertex_deselect")
            
            prop = flag_props.vertex[flag_props.vertex_index]
            layout.prop(prop, "name")
            layout.prop(prop, "surface")
            layout.prop(prop, "fog")
            layout.prop(prop, "decal")
            layout.prop(prop, "lighting")
            layout.prop(prop, "normals")
            layout.prop(prop, "hidden")
            
        col_operators = row.column(align=True)
        col_operators.operator("a3ob.flags_vertex_add", text="", icon='ADD')
        col_operators.operator("a3ob.flags_vertex_remove", text="", icon='REMOVE')
        col_operators.separator()
        col_operators.operator("a3ob.flags_vertex_clear", text="", icon='TRASH')


class A3OB_PT_object_mesh_flags_face(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Face Flag Groups"
    bl_context = "data"
    bl_parent_id = "A3OB_PT_object_mesh_flags"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH'
    
    def draw(self, context):
        obj = context.object
        flag_props = obj.a3ob_properties_object_flags
        
        layout = self.layout
        row = layout.row()
        col_list = row.column()
        col_list.template_list("A3OB_UL_flags_face", "A3OB_flags_face", flag_props, "face", flag_props, "face_index")
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        if flag_props.face_index in range(len(flag_props.face)):
            if obj.mode == 'EDIT':
                row_operators = layout.row(align=True)
                row_operators.operator("a3ob.flags_face_assign")
                row_operators.operator("a3ob.flags_face_select")
                row_operators.operator("a3ob.flags_face_deselect")
            
            prop = flag_props.face[flag_props.face_index]
            layout.prop(prop, "name")
            layout.prop(prop, "lighting")
            layout.prop(prop, "zbias")
            layout.prop(prop, "shadow")
            layout.prop(prop, "merging")
            layout.prop(prop, "user")
            
        col_operators = row.column(align=True)
        col_operators.operator("a3ob.flags_face_add", text="", icon='ADD')
        col_operators.operator("a3ob.flags_face_remove", text="", icon='REMOVE')
        col_operators.separator()
        col_operators.operator("a3ob.flags_face_clear", text="", icon='TRASH')


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
        
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/proxy"
        
    def draw(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_proxy
        
        layout = self.layout
        row = layout.row(align=True)
        col_enable = row.column(align=True)
        col_enable.prop(object_props, "is_a3_proxy", text="Is P3D Proxy", toggle=True)
        col_enable.enabled = False
        col_naming = row.column(align=True)
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        layout.separator()
        row_path = layout.row(align=True)
        row_path.operator("a3ob.proxy_common", text="", icon='PASTEDOWN')
        row_path.prop(object_props, "proxy_path", text="", icon='MESH_CUBE')
        layout.prop(object_props, "proxy_index", text="")


class A3OB_PT_object_dtm(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Raster DTM Properties"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and not obj.a3ob_properties_object_proxy.is_a3_proxy
        
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/raster-dtm"
        
    def draw(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_dtm
        
        layout = self.layout
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col_cellsize = layout.column(align=True)
        row_cellsize_source = col_cellsize.row(align=True)
        row_cellsize_source.prop(object_props, "cellsize_source", text="Raster Spacing", expand=True)
        if object_props.cellsize_source == 'MANUAL':
            col_cellsize.prop(object_props, "cellsize", text=" ")
        
        col_origin = layout.column(align=True)
        row_origin = col_origin.row(align=True)
        row_origin.prop(object_props, "origin", text="Reference Point", expand=True)
        col_origin.prop(object_props, "easting")
        col_origin.prop(object_props, "northing")
        layout.prop(object_props, "nodata")


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(A3OB_OT_proxy_add.bl_idname, icon_value=utils.get_icon("op_proxy_add"))


classes = (
    A3OB_OT_proxy_add,
    A3OB_OT_proxy_common,
    A3OB_OT_namedprops_add,
    A3OB_OT_namedprops_remove,
    A3OB_OT_namedprops_common,
    A3OB_OT_flags_vertex_add,
    A3OB_OT_flags_vertex_remove,
    A3OB_OT_flags_vertex_assign,
    A3OB_OT_flags_vertex_select,
    A3OB_OT_flags_vertex_deselect,
    A3OB_OT_flags_vertex_clear,
    A3OB_OT_flags_face_add,
    A3OB_OT_flags_face_remove,
    A3OB_OT_flags_face_assign,
    A3OB_OT_flags_face_select,
    A3OB_OT_flags_face_deselect,
    A3OB_OT_flags_face_clear,
    A3OB_UL_namedprops,
    A3OB_UL_common_proxies,
    A3OB_UL_flags_vertex,
    A3OB_UL_flags_face,
    A3OB_PT_object_mesh,
    A3OB_PT_object_mesh_namedprops,
    A3OB_PT_object_mesh_flags,
    A3OB_PT_object_mesh_flags_vertex,
    A3OB_PT_object_mesh_flags_face,
    A3OB_PT_object_proxy,
    A3OB_PT_object_dtm
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(menu_func)
    
    print("\t" + "UI: mesh properties")


def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: mesh properties")