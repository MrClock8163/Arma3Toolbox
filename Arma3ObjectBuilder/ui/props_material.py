import bpy

from ..utilities import generic as utils


class A3OB_OT_paste_common_material(bpy.types.Operator):
    """Paste a common material path"""
    
    bl_label = "Paste Common Material"
    bl_idname = "a3ob.paste_common_material"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat
    
    def invoke(self, context, event):
        scene_props = context.scene.a3ob_commons
        scene_props.materials.clear()

        builtin_vis, custom_vis = utils.get_common("materials")
        builtin_pen, custom_pen = utils.get_common("materials_penetration")

        if custom_vis is None or custom_pen is None:
            self.report({'INFO'}, "Custom data JSON could not be loaded")
        
        if custom_vis is not None:
            builtin_vis.update(custom_vis)

        if custom_pen is not None:
            builtin_pen.update(custom_pen)
        
        for name in builtin_vis:
            item = scene_props.materials.add()
            item.name = name
            item.path = utils.replace_slashes(builtin_vis[name])
        
        for name in builtin_pen:
            item = scene_props.materials.add()
            item.name = name
            item.path = utils.replace_slashes(builtin_pen[name])
            item.type = 'PENETRATION'
        
        scene_props.materials_index = 0

        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        scene_props = context.scene.a3ob_commons
        layout = self.layout
        layout.template_list("A3OB_UL_common_materials", "A3OB_common_materials", scene_props, "materials", scene_props, "materials_index", item_dyntip_propname="path")

    def execute(self, context):
        mat = context.material
        scene_props = context.scene.a3ob_commons

        if utils.is_valid_idx(scene_props.materials_index, scene_props.materials):
            new_item = scene_props.materials[scene_props.materials_index]
            mat_props = mat.a3ob_properties_material
            mat_props.material_path = new_item.path
        
        return {'FINISHED'}


class A3OB_OT_paste_common_procedural(bpy.types.Operator):
    """Paste a common procedural texture"""
    
    bl_label = "Paste Common Procedural"
    bl_idname = "a3ob.paste_common_procedural"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return bool(context.material)
    
    def invoke(self, context, event):
        scene_props = context.scene.a3ob_commons
        scene_props.procedurals.clear()

        procedurals, custom = utils.get_common("procedurals")
        if custom is None:
            self.report({'INFO'}, "Custom data JSON could not be loaded")
        else:
            procedurals.update(custom)
        
        for name in procedurals:
            item = scene_props.procedurals.add()
            item.name = name
            item.value = procedurals[name]
        
        scene_props.procedurals_index = 0

        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        scene_props = context.scene.a3ob_commons
        layout = self.layout
        layout.template_list("A3OB_UL_common_procedurals", "A3OB_common_procedurals", scene_props, "procedurals", scene_props, "procedurals_index")

        selection_index = scene_props.procedurals_index
        if utils.is_valid_idx(selection_index, scene_props.procedurals):
            row = layout.row()
            item = scene_props.procedurals[selection_index]
            row.prop(item, "value", text="")
            row.enabled = False

    def execute(self, context):
        mat = context.material
        scene_props = context.scene.a3ob_commons

        if utils.is_valid_idx(scene_props.procedurals_index, scene_props.procedurals):
            new_item = scene_props.procedurals[scene_props.procedurals_index]
            mat_props = mat.a3ob_properties_material
            mat_props.color_raw = new_item.value
        
        return {'FINISHED'}


class A3OB_UL_common_materials(bpy.types.UIList):
    filter_type: bpy.props.EnumProperty(
        name = "Type",
        items = (
            ('ALL', "All", "No filtering", 'NONE', 0),
            ('VISUAL', "Visual", "Visual materials", 'MATERIAL', 1),
            ('PENETRATION', "Penetration", "Penetration materials", 'SNAP_VOLUME', 2)
        ),
        default = 'ALL'
    )
    use_filter_name_invert: bpy.props.BoolProperty(
        name = "Invert",
        description = "Invert name filtering"
    )

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        icon = 'MATERIAL'
        if item.type == 'PENETRATION':
            icon = 'SNAP_VOLUME'

        layout.label(text=item.name, icon=icon)
    
    def draw_filter(self, context, layout):
        row_filter = layout.row(align=True)
        row_filter.prop(self, "filter_type", text=" ", expand=True)

        row_order = layout.row(align=True)
        row_order.prop(self, "filter_name", text="")
        row_order.prop(self, "use_filter_name_invert", text="", icon='ARROW_LEFTRIGHT')
        row_order.separator()
        row_order.prop(self, "use_filter_sort_alpha", text="", icon='SORTALPHA')
        row_order.prop(self, "use_filter_sort_reverse", text="", icon='SORT_DESC' if self.use_filter_sort_reverse else 'SORT_ASC')
    
    def filter_items(self, context, data, property):
        mats = getattr(data, property)

        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []

        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, mats, "name", reverse=self.use_filter_name_invert)
        
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(mats)

        if self.filter_type != 'ALL':
            for i, mat in enumerate(mats):
                if mat.type == self.filter_type:
                    continue

                flt_flags[i] = 0

        if self.use_filter_sort_alpha:
            flt_neworder = helper_funcs.sort_items_by_name(mats, "name")

        return flt_flags, flt_neworder


class A3OB_UL_common_procedurals(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)


class A3OB_PT_material(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Material Properties"
    bl_context = "material"

    doc_url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/material"
    
    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat
        
    def draw_header(self, context):
        utils.draw_panel_header(self)
        
    def draw(self, context):
        material = context.material
        material_props = material.a3ob_properties_material
        
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        row = layout.row()
        row.prop(material_props, "texture_type", expand=True)
        layout.separator()
        
        texture_type = material_props.texture_type
        if texture_type == 'TEX':
            layout.prop(material_props, "texture_path", text="", icon='TEXTURE')
        elif texture_type == 'COLOR':
            row_color = layout.row(align=True)
            row_color.prop(material_props, "color_value", icon='COLOR')
            row_color.prop(material_props, "color_type", text="")
        elif texture_type == 'CUSTOM':
            row_raw = layout.row(align=True)
            row_raw.operator("a3ob.paste_common_procedural", text="", icon='PASTEDOWN')
            row_raw.prop(material_props, "color_raw", text="", icon='TEXT')
        
        row_material = layout.row(align=True)
        row_material.operator("a3ob.paste_common_material", text="", icon='PASTEDOWN')
        row_material.prop(material_props, "material_path", text="", icon='MATERIAL')


classes = (
    A3OB_OT_paste_common_material,
    A3OB_OT_paste_common_procedural,
    A3OB_UL_common_materials,
    A3OB_UL_common_procedurals,
    A3OB_PT_material,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: material properties")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: material properties")