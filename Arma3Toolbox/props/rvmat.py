import bpy
from ..utilities import data

class A3OB_PG_properties_material(bpy.types.PropertyGroup):
    textureType: bpy.props.EnumProperty ( 
        name = "Texture source",
        description = "Source of face texture",
        items = (
            ('TEX', "File", "Texture file"),
            ('COLOR', "Color", "Procedural color"),
            ('CUSTOM', "Custom", "Raw custom input")
        ),
        default = 'TEX',
        options = set()
    )
    texturePath: bpy.props.StringProperty (
        name = "Texture",
        description = "Path to texture file",
        subtype = 'FILE_PATH',
        default = "",
        options = set()
    )
    colorValue: bpy.props.FloatVectorProperty (
        name = "Color",
        description = "Color used to generate procedural texture string",
        subtype = 'COLOR_GAMMA',
        min = 0.0,
        max = 1.0,
        default = (1,1,1,1),
        size = 4,
        options = set()
    )
    colorType: bpy.props.EnumProperty (
        name = "Type",
        description = "Procedural texture type",
        items = data.textureTypes,
        default = 'CO',
        options = set()
    )
    colorString: bpy.props.StringProperty (
        name = "Raw input",
        description = "Raw string intput that will be directly copied into the exported model",
        default = "",
        options = set()
    )
    materialPath: bpy.props.StringProperty (
        name = "Material",
        description = "Path to RVMAT file",
        subtype = 'FILE_PATH',
        default = "",
        options = set()
    )
    hiddenSelection: bpy.props.StringProperty (
        name = "Create selection",
        description = "Name of the selection to create for the material (leave empty to not create selection)",
        default = "",
        options = set()
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