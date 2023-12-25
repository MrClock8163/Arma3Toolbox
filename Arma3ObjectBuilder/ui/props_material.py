import bpy

from ..utilities import generic as utils


class A3OB_OT_materials_common(bpy.types.Operator):
    """Paste a common material path"""
    
    bl_label = "Common Material"
    bl_idname = "a3ob.materials_common"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat
    
    def invoke(self, context, event):
        scene = context.scene
        scene.a3ob_materials_common.clear()

        materials, custom = utils.get_common("materials")
        if custom is None:
            self.report({'ERROR'}, "Custom data JSON could not be loaded")
        else:
            materials.update(custom)
        
        for mat in materials:
            item = scene.a3ob_materials_common.add()
            item.name = mat
            item.path = utils.replace_slashes(materials[mat])
        
        scene.a3ob_materials_common_index = 0

        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.template_list("A3OB_UL_materials", "A3OB_materials_common", scene, "a3ob_materials_common", scene, "a3ob_materials_common_index")

        selection_index = scene.a3ob_materials_common_index
        if selection_index in range(len(scene.a3ob_materials_common)):
            row = layout.row()
            item = scene.a3ob_materials_common[selection_index]
            row.prop(item, "path", text="")
            row.enabled = False

    def execute(self, context):
        mat = context.material
        scene = context.scene

        if scene.a3ob_materials_common_index in range(len(scene.a3ob_materials_common)):
            new_item = scene.a3ob_materials_common[scene.a3ob_materials_common_index]
            mat_props = mat.a3ob_properties_material
            mat_props.material_path = new_item.path
        
        return {'FINISHED'}


class A3OB_OT_paste_common_procedural(bpy.types.Operator):
    """Paste a common procedural texture"""
    
    bl_label = "Common Procedural"
    bl_idname = "a3ob.paste_common_procedural"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat
    
    def invoke(self, context, event):
        scene_props = context.scene.a3ob_commons
        scene_props.procedurals.clear()

        procedurals, custom = utils.get_common("procedurals")
        if custom is None:
            self.report({'ERROR'}, "Custom data JSON could not be loaded")
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
        if selection_index in range(len(scene_props.procedurals)):
            row = layout.row()
            item = scene_props.procedurals[selection_index]
            row.prop(item, "value", text="")
            row.enabled = False

    def execute(self, context):
        mat = context.material
        scene_props = context.scene.a3ob_commons

        if scene_props.procedurals_index in range(len(scene_props.procedurals)):
            new_item = scene_props.procedurals[scene_props.procedurals_index]
            mat_props = mat.a3ob_properties_material
            mat_props.color_raw = new_item.value
        
        return {'FINISHED'}


class A3OB_UL_materials(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)


class A3OB_UL_common_procedurals(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)


class A3OB_PT_material(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Material Properties"
    bl_context = "material"
    
    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat
        
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/material"
        
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
        row_material.operator("a3ob.materials_common", text="", icon='PASTEDOWN')
        row_material.prop(material_props, "material_path", text="", icon='MATERIAL')


classes = (
    A3OB_OT_materials_common,
    A3OB_OT_paste_common_procedural,
    A3OB_UL_materials,
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