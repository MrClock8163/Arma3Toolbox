import bpy

from ..utilities import properties as proputils
from ..utilities import data


class A3OB_PG_properties_named_property(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty (
        name = "Name",
        description = "Property name"
    )
    value: bpy.props.StringProperty (
        name = "Value",
        description = "Property value"
    )


class A3OB_PG_properties_object_mesh(bpy.types.PropertyGroup):
    is_a3_lod: bpy.props.BoolProperty (
        name = "Arma 3 LOD",
        description = "This object is a LOD for an Arma 3 P3D",
        default = False
    )
    lod: bpy.props.EnumProperty (
        name = "LOD Type",
        description = "Type of LOD",
        items = data.enum_lod_types,
        default = '0'
    )
    resolution: bpy.props.IntProperty (
        name = "Resolution/Index",
        description = "Resolution or index value of LOD object",
        default = 1,
        min = 0,
        soft_max = 10000,
        step = 1
    )
    properties: bpy.props.CollectionProperty (
        name = "Named Properties",
        description = "Named properties associated with the LOD",
        type = A3OB_PG_properties_named_property
    )
    property_index: bpy.props.IntProperty (
        name = "Named Property Index",
        description = "Index of the currently selected named property",
        default = -1
    )


class A3OB_PG_properties_object_proxy(bpy.types.PropertyGroup):
    is_a3_proxy: bpy.props.BoolProperty (
        name = "Arma 3 Model Proxy",
        description = "This object is a proxy (cannot change manually)",
        default = False
    )
    proxy_path: bpy.props.StringProperty (
        name = "Path",
        description = "File path to the proxy model",
        default = "",
        subtype = 'FILE_PATH'
    )
    proxy_index: bpy.props.IntProperty (
        name = "Index",
        description = "Index of proxy",
        default = 1,
        min = 0,
        max = 999
    )


classes = (
    A3OB_PG_properties_named_property,
    A3OB_PG_properties_object_mesh,
    A3OB_PG_properties_object_proxy
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Object.a3ob_properties_object = bpy.props.PointerProperty(type=A3OB_PG_properties_object_mesh)
    bpy.types.Object.a3ob_properties_object_proxy = bpy.props.PointerProperty(type=A3OB_PG_properties_object_proxy)
    bpy.types.Object.a3ob_selection_mass = bpy.props.FloatProperty ( # Can't be in property group due to reference requirements
        name = "Current Mass",
        description = "Total mass of current selection",
        default = 0.0,
        min = 0,
        max = 1000000,
        step = 10,
        soft_max = 100000,
        precision = 3,
        unit = 'MASS',
        get = proputils.get_selection_mass,
        set = proputils.set_selection_mass
    )
    
    print("\t" + "Properties: object")


def unregister():
    del bpy.types.Object.a3ob_selection_mass
    del bpy.types.Object.a3ob_properties_object_proxy
    del bpy.types.Object.a3ob_properties_object
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "Properties: object")