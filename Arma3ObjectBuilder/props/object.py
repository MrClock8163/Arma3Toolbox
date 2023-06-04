import os

import bpy

from ..utilities import properties as proputils
from ..utilities import data


def proxy_path_update(self, context):
    obj = self.id_data
    name = os.path.basename(os.path.splitext(self.proxy_path)[0]).strip()
    if name == "":
        name = "Proxy"
        
    name += " %d" % self.proxy_index
    obj.name = name
    obj.data.name = name


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
        subtype = 'FILE_PATH',
        update = proxy_path_update
    )
    proxy_index: bpy.props.IntProperty (
        name = "Index",
        description = "Index of proxy",
        default = 1,
        min = 0,
        max = 999
    )


class A3OB_PG_properties_object_dtm(bpy.types.PropertyGroup):
    origin: bpy.props.EnumProperty (
        name = "Origin",
        description = "Origin point of DTM mesh",
        items = (
            ('CENTER', "Center", "Center of the lower left cell"),
            ('CORNER', "Corner", "Lower left corner of the lower left cell")
        ),
        default = 'CORNER'
    )
    easting: bpy.props.FloatProperty (
        name = "Easting",
        description = "",
        unit = 'LENGTH',
        default = 200000,
        soft_max = 1000000
    )
    northing: bpy.props.FloatProperty (
        name = "Northing",
        description = "",
        unit = 'LENGTH',
        default = 0,
        soft_max = 1000000
    )
    cellsize: bpy.props.FloatProperty (
        name = "Raster Spacing",
        description = "Horizontal and vertical spacing between raster points",
        unit = 'LENGTH',
        default = 1.0
    )
    nodata: bpy.props.FloatProperty (
        name = "NULL Indicator",
        description = "Filler value where data does not exist",
        default = -9999.0
    )
    
    
class A3OB_PG_properties_keyframe(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty (
        name = "Frame Index",
        description = "Index of the keyframe to export",
        default = 0
    )
    
    
class A3OB_PG_properties_object_armature(bpy.types.PropertyGroup):
    motion_source: bpy.props.EnumProperty (
        name = "Motion Source",
        description = "Source of motion vector",
        items = (
            ('MANUAL', "Manual", "The motion vector is explicitly set"),
            ('CALCULATED', "Calculated", "The motion vector is calculated from the motion of a specific bone during the animation")
        ),
        default = 'MANUAL'
    )
    motion_vector: bpy.props.FloatVectorProperty (
        name = "Motion Vector",
        description = "Total motion done during the animation",
        default = (0, 0, 0),
        subtype = 'XYZ',
        unit = 'LENGTH'
    )
    motion_bone: bpy.props.StringProperty (
        name = "Reference Bone",
        description = "Bone to track for motion calculation",
        default = ""
    )
    frames: bpy.props.CollectionProperty (
        name = "RTM keyframes",
        description = "List of keyframes to export to RTM",
        type = A3OB_PG_properties_keyframe
    )
    frames_index: bpy.props.IntProperty (
        name = "Selection Index",
        description = "Index of the currently selected RTM frame",
        default = -1
    )


classes = (
    A3OB_PG_properties_named_property,
    A3OB_PG_properties_object_mesh,
    A3OB_PG_properties_object_proxy,
    A3OB_PG_properties_object_dtm,
    A3OB_PG_properties_keyframe,
    A3OB_PG_properties_object_armature
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Object.a3ob_properties_object = bpy.props.PointerProperty(type=A3OB_PG_properties_object_mesh)
    bpy.types.Object.a3ob_properties_object_proxy = bpy.props.PointerProperty(type=A3OB_PG_properties_object_proxy)
    bpy.types.Object.a3ob_properties_object_dtm = bpy.props.PointerProperty(type=A3OB_PG_properties_object_dtm)
    bpy.types.Object.a3ob_properties_object_armature = bpy.props.PointerProperty(type=A3OB_PG_properties_object_armature)
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
    del bpy.types.Object.a3ob_properties_object_armature
    del bpy.types.Object.a3ob_properties_object_dtm
    del bpy.types.Object.a3ob_properties_object_proxy
    del bpy.types.Object.a3ob_properties_object
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "Properties: object")