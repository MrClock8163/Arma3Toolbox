import os

import bpy

from ..utilities import generic as utils
from ..utilities import masses as massutils
from ..utilities import lod as lodutils
from ..utilities import flags as flagutils
from ..utilities import data


def proxy_name_update(self, context):
    if not self.is_a3_proxy:
        return
    
    name = "proxy: %s" % self.get_name()
    obj = self.id_data
    obj.name = name
    obj.data.name = name


class A3OB_PG_properties_named_property(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name = "Name",
        description = "Property name"
        # search = lambda self, context, edit_text: [item for item in data.known_namedprops if item.lower().startswith(edit_text.lower())],
        # search_options = {'SORT', 'SUGGESTION'}
    )
    value: bpy.props.StringProperty(
        name = "Value",
        description = "Property value"
        # search = lambda self, context, edit_text: [item for item in data.known_namedprops.get(self.name.lower(), []) if item.startswith(edit_text.lower())],
        # search_options = {'SORT', 'SUGGESTION'}
    )


class A3OB_PG_properties_flag_vertex(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", description="Name of the vertex flag group")
    surface: bpy.props.EnumProperty(
        name = "Surface",
        items = (
            ('NORMAL', "Normal", ""),
            ('SURFACE_ON', "On Surface", ""),
            ('SURFACE_ABOVE', "Above Surface", ""),
            ('SURFACE_UNDER', "Under Surface", ""),
            ('KEEP_HEIGHT', "Keep Height", "")
        ),
        default = 'NORMAL'
    )
    fog: bpy.props.EnumProperty(
        name = "Fog",
        items = (
            ('NORMAL', "Normal", ""),
            ('SKY', "Sky", ""),
            ('NONE', "None", "")
        ),
        default = 'NORMAL'
    )
    decal: bpy.props.EnumProperty(
        name = "Decal",
        items = (
            ('NORMAL', "Normal", ""),
            ('DECAL', "Decal", "")
        ),
        default = 'NORMAL'
    )
    lighting: bpy.props.EnumProperty(
        name = "Lighting",
        items = (
            ('NORMAL', "Normal", ""),
            ('SHINING', "Shining", ""),
            ('SHADOW', "Always in Shadow", ""),
            ('LIGHTED_HALF', "Half Lighted", ""),
            ('LIGHTED_FULL', "Fully Lighted", ""),
        ),
        default = 'NORMAL'
    )
    normals: bpy.props.EnumProperty(
        name = "Normals",
        items = (
            ('AREA', "Face Dimension", ""),
            ('ANGLE', "Impedance Angle", ""),
            ('FIXED', "Fixed", ""),
        ),
        default = 'AREA'
    )
    hidden: bpy.props.BoolProperty(name="Hidden Vertex") # True: 0x00000000 False: 0x01000000
    
    def get_flag(self):        
        return flagutils.get_flag_vertex(self)
    
    def set_flag(self, value):
        flagutils.set_flag_vertex(self, value)


class A3OB_PG_properties_flag_face(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", description="Name of the face flag group")
    lighting: bpy.props.EnumProperty(
        name = "Lighting & Shadows",
        items = (
            ('NORMAL', "Normal", ""),
            ('BOTH', "Both Sides", ""),
            ('POSITION', "Position", ""),
            ('FLAT', "Flat", ""),
            ('REVERSED', "Reversed", "")
        ),
        default = 'NORMAL'
    )
    zbias: bpy.props.EnumProperty(
        name = "Z Bias",
        items = (
            ('NONE', "None", ""),
            ('LOW', "Low", ""),
            ('MIDDLE', "Middle", ""),
            ('HIGH', "High", "")
        )
    )
    shadow: bpy.props.BoolProperty(name="Enable Shadow", default=True) # True: 0x00000000 False: 0x00000010
    merging: bpy.props.BoolProperty(name="Enable Texture Merging", default=True) # True: 0x00000000 False: 0x01000000
    user: bpy.props.IntProperty(
        name = "User Value",
        min = 0,
        max = 127
    )
    
    def get_flag(self):
        return flagutils.get_flag_face(self)

    def set_flag(self, value):
        flagutils.set_flag_face(self, value)


class A3OB_PG_properties_object_mesh(bpy.types.PropertyGroup):
    is_a3_lod: bpy.props.BoolProperty(
        name = "Arma 3 LOD",
        description = "This object is a LOD for an Arma 3 P3D"
    )
    lod: bpy.props.EnumProperty(
        name = "LOD Type",
        description = "Type of LOD",
        items = data.enum_lod_types,
        default = '0'
    )
    resolution: bpy.props.IntProperty(
        name = "Resolution/Index",
        description = "Resolution or index value of LOD object",
        default = 1,
        min = 0,
        soft_max = 1000,
        step = 1
    )
    properties: bpy.props.CollectionProperty(
        name = "Named Properties",
        description = "Named properties associated with the LOD",
        type = A3OB_PG_properties_named_property
    )
    property_index: bpy.props.IntProperty(name="Active Property Index", description="Double click to change name and value")

    def get_name(self):
        return lodutils.format_lod_name(int(self.lod), self.resolution)

    def get_signature(self):
        return lodutils.get_lod_signature(int(self.lod), self.resolution)


class A3OB_PG_properties_object_flags(bpy.types.PropertyGroup):
    vertex: bpy.props.CollectionProperty(
        name = "Vertex Flag Groups",
        description = "Vertex flag groups used in the LOD",
        type = A3OB_PG_properties_flag_vertex
    )
    vertex_index: bpy.props.IntProperty(name="Vertex Flag Group Index")
    face: bpy.props.CollectionProperty(
        name = "Active Face Flag Groups",
        description = "Face flag groups used in the LOD",
        type = A3OB_PG_properties_flag_face
    )
    face_index: bpy.props.IntProperty(name="Active Face Flag Group Index")


class A3OB_PG_properties_object_proxy(bpy.types.PropertyGroup):
    is_a3_proxy: bpy.props.BoolProperty(
        name = "Arma 3 Model Proxy",
        description = "This object is a proxy (cannot change manually)",
        update = proxy_name_update
    )
    proxy_path: bpy.props.StringProperty(
        name = "Path",
        description = "File path to the proxy model",
        subtype = 'FILE_PATH',
        update = proxy_name_update
    )
    proxy_index: bpy.props.IntProperty(
        name = "Index",
        description = "Index of proxy",
        default = 1,
        min = 0,
        max = 999,
        update = proxy_name_update
    )
    
    def to_placeholder(self):
        addon_prefs = utils.get_addon_preferences()

        path = utils.format_path(utils.abspath(self.proxy_path), utils.abspath(addon_prefs.project_root), addon_prefs.export_relative, False)
        if len(path) > 0 and path[0] != "\\":
            path = "\\" + path
        
        return path, self.proxy_index
    
    def get_name(self):
        name = os.path.basename(os.path.splitext(utils.abspath(self.proxy_path))[0]).strip()
        if name == "":
            name = "unknown"
            
        name = "%s %d" % (name, self.proxy_index)

        return name


class A3OB_PG_properties_object_dtm(bpy.types.PropertyGroup):
    origin: bpy.props.EnumProperty(
        name = "Origin",
        description = "Origin point of DTM mesh",
        items = (
            ('CENTER', "Center", "Center of the lower left cell"),
            ('CORNER', "Corner", "Lower left corner of the lower left cell")
        ),
        default = 'CORNER'
    )
    easting: bpy.props.FloatProperty(
        name = "Easting",
        unit = 'LENGTH',
        default = 200000,
        soft_max = 1000000
    )
    northing: bpy.props.FloatProperty(
        name = "Northing",
        unit = 'LENGTH',
        soft_max = 1000000
    )
    cellsize_source: bpy.props.EnumProperty(
        name = "Source",
        description = "Source of raster spacing",
        items = (
            ('MANUAL', "Manual", "The raster spacing is explicitly set"),
            ('CALCULATED', "Calculated", "The raster spacing is from the distance of the first 2 points of the gird")
        ),
        default = 'MANUAL'
    )
    cellsize: bpy.props.FloatProperty(
        name = "Raster Spacing",
        description = "Horizontal and vertical spacing between raster points",
        unit = 'LENGTH',
        default = 1.0
    )
    nodata: bpy.props.FloatProperty(
        name = "NULL Indicator",
        description = "Filler value where data does not exist",
        default = -9999.0
    )


class A3OB_PG_properties_keyframe(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty(name="Frame Index", description="Index of the keyframe to export")


class A3OB_PG_properties_object_armature(bpy.types.PropertyGroup):
    motion_source: bpy.props.EnumProperty(
        name = "Motion Source",
        description = "Source of motion vector",
        items = (
            ('MANUAL', "Manual", "The motion vector is explicitly set"),
            ('CALCULATED', "Calculated", "The motion vector is calculated from the motion of a specific bone during the animation")
        ),
        default = 'MANUAL'
    )
    motion_vector: bpy.props.FloatVectorProperty(
        name = "Motion Vector",
        description = "Total motion done during the animation",
        default = (0, 0, 0),
        subtype = 'XYZ',
        unit = 'LENGTH'
    )
    motion_bone: bpy.props.StringProperty(name="Reference Bone", description="Bone to track for motion calculation")
    frames: bpy.props.CollectionProperty(
        name = "RTM keyframes",
        description = "List of keyframes to export to RTM",
        type = A3OB_PG_properties_keyframe
    )
    frames_index: bpy.props.IntProperty(name="Active Keyrame Index")


classes = (
    A3OB_PG_properties_named_property,
    A3OB_PG_properties_flag_vertex,
    A3OB_PG_properties_flag_face,
    A3OB_PG_properties_object_mesh,
    A3OB_PG_properties_object_flags,
    A3OB_PG_properties_object_proxy,
    A3OB_PG_properties_object_dtm,
    A3OB_PG_properties_keyframe,
    A3OB_PG_properties_object_armature
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Object.a3ob_properties_object = bpy.props.PointerProperty(type=A3OB_PG_properties_object_mesh)
    bpy.types.Object.a3ob_properties_object_flags = bpy.props.PointerProperty(type=A3OB_PG_properties_object_flags)
    bpy.types.Object.a3ob_properties_object_proxy = bpy.props.PointerProperty(type=A3OB_PG_properties_object_proxy)
    bpy.types.Object.a3ob_properties_object_dtm = bpy.props.PointerProperty(type=A3OB_PG_properties_object_dtm)
    bpy.types.Object.a3ob_properties_object_armature = bpy.props.PointerProperty(type=A3OB_PG_properties_object_armature)
    bpy.types.Object.a3ob_selection_mass = bpy.props.FloatProperty( # Can't be in property group due to reference requirements
        name = "Current Mass",
        description = "Total mass of current selection",
        min = 0,
        max = 1000000,
        step = 10,
        soft_max = 100000,
        precision = 3,
        unit = 'MASS',
        get = massutils.get_selection_mass,
        set = massutils.set_selection_mass
    )
    
    print("\t" + "Properties: object")


def unregister():
    del bpy.types.Object.a3ob_selection_mass
    del bpy.types.Object.a3ob_properties_object_armature
    del bpy.types.Object.a3ob_properties_object_dtm
    del bpy.types.Object.a3ob_properties_object_proxy
    del bpy.types.Object.a3ob_properties_object_flags
    del bpy.types.Object.a3ob_properties_object
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "Properties: object")