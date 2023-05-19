import bpy


class A3OB_PT_material(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Material Properties"
    bl_context = "material"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj
            and obj.select_get() == True
            and obj.type == 'MESH'
            and obj.active_material
        )
        
    def draw(self, context):
        obj = context.active_object
        material = obj.active_material
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
            layout.prop(material_props, "color_raw", text="", icon='TEXT')
        
        layout.prop(material_props, "material_path", text="", icon='MATERIAL')
        layout.separator()
        layout.prop(material_props, "translucent")


classes = (
    A3OB_PT_material,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)