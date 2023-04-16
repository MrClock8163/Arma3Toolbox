import bpy

class A3OB_PT_material(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: material properties"
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
        
        row = layout.row()
        row.prop(OBprops,"textureType",expand=True)
        layout.separator()
        
        texType = OBprops.textureType
        if texType == 'TEX':
            layout.prop(OBprops,"texturePath",icon='TEXTURE',text="")
        elif texType == 'COLOR':
            layout.prop(OBprops, "colorValue",icon='COLOR')
            layout.prop(OBprops, "colorType")
        elif texType == 'CUSTOM':
            layout.prop(OBprops, "colorString",icon='TEXT',text="")
        
        layout.prop(OBprops,"materialPath",icon='MATERIAL',text="")
        
        layout.separator()
        
        layout.prop(OBprops,"hiddenSelection",icon='MESH_DATA')
        
classes = (
    A3OB_PT_material,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)