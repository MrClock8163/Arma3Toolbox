import bpy
from ..utilities import data

class A3OB_PG_properties_material(bpy.types.PropertyGroup):
    textureType: bpy.props.EnumProperty ( 
        name = "Texture Source",
        description = "Source of face texture",
        items = (
            ('TEX', "File", "Texture file"),
            ('COLOR', "Color", "Procedural color"),
            ('CUSTOM', "Custom", "Raw custom input")
        ),
        default = 'TEX'
    )
    texturePath: bpy.props.StringProperty (
        name = "Texture",
        description = "Path to texture file",
        subtype = 'FILE_PATH',
        default = ""
    )
    colorValue: bpy.props.FloatVectorProperty (
        name = "Color",
        description = "Color used to generate procedural texture string",
        subtype = 'COLOR_GAMMA',
        min = 0.0,
        max = 1.0,
        default = (1,1,1,1),
        size = 4
    )
    colorType: bpy.props.EnumProperty (
        name = "Type",
        description = "Procedural texture type",
        items = data.textureTypes,
        default = 'CO'
    )
    colorString: bpy.props.StringProperty (
        name = "Raw Input",
        description = "Raw string intput that will be directly copied into the exported model",
        default = ""
    )
    materialPath: bpy.props.StringProperty (
        name = "Material",
        description = "Path to RVMAT file",
        subtype = 'FILE_PATH',
        default = ""
    )
    hiddenSelection: bpy.props.StringProperty (
        name = "Create Selection",
        description = "Name of the selection to create for the material (leave empty to not create selection)",
        default = ""
    )
    
classes = (
    A3OB_PG_properties_material,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Material.a3ob_properties_material = bpy.props.PointerProperty (type=A3OB_PG_properties_material)
    
def unregister():
    del bpy.types.Material.a3ob_properties_material
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)