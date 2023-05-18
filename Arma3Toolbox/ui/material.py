import bpy

class A3OB_PT_material(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: Material Properties"
    bl_context = "material"
    
    @classmethod
    def poll(cls,context):
        return (context.active_object
            and context.active_object.select_get() == True
            and context.active_object.type == 'MESH'
            and context.active_object.active_material
        )
        
    def draw(self,context):
        activeObj = context.active_object
        activeMat = activeObj.active_material
        OBprops = activeMat.a3ob_properties_material
        
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        row = layout.row()
        row.prop(OBprops,"texture_type",expand=True)
        layout.separator()
        
        texType = OBprops.texture_type
        if texType == 'TEX':
            layout.prop(OBprops,"texture_path",icon='TEXTURE',text="")
        elif texType == 'COLOR':
            colorRow = layout.row(align=True)
            colorRow.prop(OBprops, "color_value",icon='COLOR')
            colorRow.prop(OBprops, "color_type",text="")
        elif texType == 'CUSTOM':
            layout.prop(OBprops, "color_raw",icon='TEXT',text="")
        
        layout.prop(OBprops,"material_path",icon='MATERIAL',text="")
        
        layout.separator()
        
        layout.prop(OBprops,"translucent")
        
classes = (
    A3OB_PT_material,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)