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
    isArma3LOD: bpy.props.BoolProperty (
        name = "Arma 3 LOD",
        description = "This object is a LOD for an Arma 3 P3D",
        default = False,
        options = set()
    )
    LOD: bpy.props.EnumProperty (
        name = "LOD type",
        description = "Type of LOD",
        items = data.LODTypes,
        default = '0',
        options = set()
    )
    resolution: bpy.props.IntProperty (
        name = "Resolution/Index",
        description = "Resolution or index value of LOD object",
        default = 1,
        min = 0,
        soft_max = 10000,
        step = 1,
        options = set()
    )
    properties: bpy.props.CollectionProperty (
        name = "Named properties",
        description = "Named properties associated with the LOD",
        type = A3OB_PG_properties_named_property,
        options = set()
    )
    propertyIndex: bpy.props.IntProperty (
        name = "Named property index",
        description = "Index of the currently selected named property",
        default = -1,
        options = set()
    )
    
class A3OB_PG_properties_object_proxy(bpy.types.PropertyGroup):
    isArma3Proxy: bpy.props.BoolProperty (
        name = "Arma 3 model proxy",
        description = "This object is a proxy",
        default = False,
        options = set()
    )
    proxyPath: bpy.props.StringProperty (
        name = "Path",
        description = "File path to the proxy model",
        default = "",
        options = set(),
        subtype = 'FILE_PATH'
    )
    proxyIndex: bpy.props.IntProperty (
        name = "Index",
        description = "Index of proxy",
        default = 1,
        min = 0,
        options = set()
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
        
    bpy.types.Object.a3ob_selectionMass = bpy.props.FloatProperty (
        name = "Current mass",
        description = "Total mass of current selection",
        default = 0.0,
        min = 0,
        max = 1000000,
        step = 10,
        soft_max = 100000,
        precision = 3,
        unit = 'MASS',
        get = proputils.selectionMassGet,
        set = proputils.selectionMassSet
    )
    
    bpy.types.Object.a3ob_selectionMassTarget = bpy.props.FloatProperty (
        name = "Mass",
        description = "Mass to set equally or distribute",
        default = 0.0,
        unit = 'MASS',
        min = 0,
        max = 1000000,
        soft_max = 100000,
        step = 10,
        precision = 3
    )
    
def unregister():
    del bpy.types.Object.a3ob_selectionMassTarget
    del bpy.types.Object.a3ob_selectionMass
    
    del bpy.types.Object.a3ob_properties_object_proxy
    del bpy.types.Object.a3ob_properties_object
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)