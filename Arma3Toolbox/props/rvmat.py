import bpy

from ..utilities import data


class A3OB_PG_properties_material(bpy.types.PropertyGroup):
    texture_type: bpy.props.EnumProperty ( 
        name = "Texture Source",
        description = "Source of face texture",
        items = (
            ('TEX', "File", "Texture file"),
            ('COLOR', "Color", "Procedural color"),
            ('CUSTOM', "Custom", "Raw custom input")
        ),
        default = 'TEX'
    )
    texture_path: bpy.props.StringProperty (
        name = "Texture",
        description = "Path to texture file",
        subtype = 'FILE_PATH',
        default = ""
    )
    color_value: bpy.props.FloatVectorProperty (
        name = "Color",
        description = "Color used to generate procedural texture string",
        subtype = 'COLOR_GAMMA',
        min = 0.0,
        max = 1.0,
        default = (1,1,1,1),
        size = 4
    )
    color_type: bpy.props.EnumProperty (
        name = "Type",
        description = "Procedural texture type",
        items = data.enum_texture_types,
        default = 'CO'
    )
    color_raw: bpy.props.StringProperty (
        name = "Raw Input",
        description = "Raw string intput that will be directly copied into the exported model",
        default = ""
    )
    material_path: bpy.props.StringProperty (
        name = "Material",
        description = "Path to RVMAT file",
        subtype = 'FILE_PATH',
        default = ""
    )
    translucent: bpy.props.BoolProperty (
        name = "Translucent",
        description = "The material is translucent",
        default = False
    )
    # hidden_selection: bpy.props.StringProperty (
        # name = "Create Selection",
        # description = "Name of the selection to create for the material (leave empty to not create selection)",
        # default = ""
    # )


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