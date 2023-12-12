import os

import bpy

from ..utilities import generic as utils
from ..utilities import masses as massutils
from ..utilities import lod as lodutils
from ..utilities import data


def create_default_flag_groups(self, context):
    obj = self.id_data
    flag_props = obj.a3ob_properties_object_flags
    
    if len(flag_props.vertex) < 1:
        new_group = flag_props.vertex.add()
        new_group.name = "Default"
        new_group.normals = 'FIXED'
        flag_props.vertex_index = 0
    
    if len(flag_props.face) < 1:
        new_group = flag_props.face.add()
        new_group.name = "Default"
        flag_props.face_index = 0


def lod_props_update(self, context):
    if not self.is_a3_lod:
        return
    
    create_default_flag_groups(self, context)


def proxy_props_update(self, context):
    if not self.is_a3_proxy:
        return
    
    create_default_flag_groups(self, context)


class A3OB_PG_properties_named_property(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty (
        name = "Name",
        description = "Property name"
    )
    value: bpy.props.StringProperty (
        name = "Value",
        description = "Property value"
    )


class A3OB_PG_properties_flag_vertex(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty (
        name = "Name",
        description = "Name of the vertex flag group",
        default = ""
    )
    surface: bpy.props.EnumProperty (
        name = "Surface",
        description = "",
        items = (
            ('NORMAL', "Normal", "", 0x00000000),
            ('SURFACE_ON', "On Surface", "", 0x00000001),
            ('SURFACE_ABOVE', "Above Surface", "", 0x00000002),
            ('SURFACE_UNDER', "Under Surface", "", 0x00000004),
            ('KEEP_HEIGHT', "Keep Height", "", 0x00000008)
        ),
        default = 'NORMAL'
    )
    fog: bpy.props.EnumProperty (
        name = "Fog",
        description = "",
        items = (
            ('NORMAL', "Normal", "", 0x00000000),
            ('SKY', "Sky", "", 0x00002000),
            ('NONE', "None", "", 0x00001000)
        ),
        default = 'NORMAL'
    )
    decal: bpy.props.EnumProperty (
        name = "Decal",
        description = "",
        items = (
            ('NORMAL', "Normal", "", 0x00000000),
            ('DECAL', "Decal", "", 0x00000100)
        ),
        default = 'NORMAL'
    )
    lighting: bpy.props.EnumProperty (
        name = "Lighting",
        description = "",
        items = (
            ('NORMAL', "Normal", "", 0x00000000),
            ('SHINING', "Shining", "", 0x00000010),
            ('SHADOW', "Always in Shadow", "", 0x00000020),
            ('LIGHTED_HALF', "Half Lighted", "", 0x00000080),
            ('LIGHTED_FULL', "Fully Lighted", "", 0x00000040),
        ),
        default = 'NORMAL'
    )
    normals: bpy.props.EnumProperty (
        name = "Normals",
        description = "Weighted average calculation mode",
        items = (
            ('AREA', "Face Dimension", "", 0x00000000),
            ('ANGLE', "Impedance Angle", "", 0x04000000),
            ('FIXED', "Fixed", "", 0x02000000),
        ),
        default = 'AREA'
    )
    hidden: bpy.props.BoolProperty (
        name = "Hidden Vertex",
        description = "",
        default = False # True: 0x00000000 False: 0x01000000
    )
    
    def get_flag(self):
        flag = 0
        flag += data.flags_vertex_surface[self.surface]
        flag += data.flags_vertex_fog[self.fog]
        flag += data.flags_vertex_decal[self.decal]
        flag += data.flags_vertex_lighting[self.lighting]
        flag += data.flags_vertex_normals[self.normals]
        
        if self.hidden:
            flag += data.flag_vertex_hidden
        
        return flag
    
    def set_flag(self, value):        
        for name in data.flags_vertex_surface:
            if value & data.flags_vertex_surface[name]:
                self.surface = name
                break
                
        for name in data.flags_vertex_fog:
            if value & data.flags_vertex_fog[name]:
                self.fog = name
                break
                
        for name in data.flags_vertex_lighting:
            if value & data.flags_vertex_lighting[name]:
                self.lighting = name
                break
                
        for name in data.flags_vertex_decal:
            if value & data.flags_vertex_decal[name]:
                self.decal = name
                break
                
        for name in data.flags_vertex_normals:
            if value & data.flags_vertex_normals[name]:
                self.normals = name
                break
        
        if value & data.flag_vertex_hidden:
            self.hidden = True


class A3OB_PG_properties_flag_face(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty (
        name = "Name",
        description = "Name of the face flag group",
        default = ""
    )
    lighting: bpy.props.EnumProperty (
        name = "Lighting & Shadows",
        description = "",
        items = (
            ('NORMAL', "Normal", "", 0x00000000),
            ('BOTH', "Both Sides", "", 0x00000020),
            ('POSITION', "Position", "", 0x00000080),
            ('FLAT', "Flat", "", 0x00100000),
            ('REVERSED', "Reversed", "", 0x00200000)
        ),
        default = 'NORMAL'
    )
    zbias: bpy.props.EnumProperty (
        name = "Z Bias",
        description = "",
        items = (
            ('NONE', "None", "", 0x00000000),
            ('LOW', "Low", "", 0x00000100),
            ('MIDDLE', "Middle", "", 0x00000200),
            ('HIGH', "High", "", 0x00000300)
        )
    )
    shadow: bpy.props.BoolProperty (
        name = "Enable Shadow",
        description = "",
        default = True # True: 0x00000000 False: 0x00000010
    )
    merging: bpy.props.BoolProperty (
        name = "Enable Texture Merging",
        description = "",
        default = True # True: 0x00000000 False: 0x01000000
    )
    
    def get_flag(self):
        flag = 0
        flag += data.flags_face_lighting[self.lighting]
        flag += data.flags_face_zbias[self.zbias]
        
        if not self.shadow:
            flag += data.flag_face_noshadow
        
        if not self.merging:
            flag += data.flag_face_merging
        
        return flag

    def set_flag(self, value):
        for name in data.flags_face_lighting:
            if value & data.flags_face_lighting[name]:
                self.lighting = name
                break

        for name in data.flags_face_zbias:
            if value & data.flags_face_zbias[name]:
                self.zbias = name
                break
        
        if value & data.flag_face_noshadow:
            self.shadow = False
        
        if value & data.flag_face_merging:
            self.merging = False


class A3OB_PG_properties_object_mesh(bpy.types.PropertyGroup):
    is_a3_lod: bpy.props.BoolProperty (
        name = "Arma 3 LOD",
        description = "This object is a LOD for an Arma 3 P3D",
        default = False,
        update = lod_props_update
    )
    lod: bpy.props.EnumProperty (
        name = "LOD Type",
        description = "Type of LOD",
        items = data.enum_lod_types,
        default = '0',
        update = lod_props_update
    )
    resolution: bpy.props.IntProperty (
        name = "Resolution/Index",
        description = "Resolution or index value of LOD object",
        default = 1,
        min = 0,
        soft_max = 1000,
        step = 1,
        update = lod_props_update
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

    def get_name(self):
        return lodutils.format_lod_name(int(self.lod), self.resolution)

    def get_signature(self):
        return lodutils.get_lod_signature(int(self.lod), self.resolution)


class A3OB_PG_properties_object_flags(bpy.types.PropertyGroup):
    vertex: bpy.props.CollectionProperty (
        name = "Vertex Flag Groups",
        description = "Vertex flag groups used in the LOD",
        type = A3OB_PG_properties_flag_vertex
    )
    vertex_index: bpy.props.IntProperty (
        name = "Vertex Flag Group Index",
        description = "Index of the currently selected vertex flag group",
        default = -1
    )
    face: bpy.props.CollectionProperty (
        name = "Face Flag Groups",
        description = "Face flag groups used in the LOD",
        type = A3OB_PG_properties_flag_face
    )
    face_index: bpy.props.IntProperty (
        name = "Face Flag Group Index",
        description = "Index of the currently selected face flag group",
        default = -1
    )


class A3OB_PG_properties_object_proxy(bpy.types.PropertyGroup):
    is_a3_proxy: bpy.props.BoolProperty (
        name = "Arma 3 Model Proxy",
        description = "This object is a proxy (cannot change manually)",
        default = False,
        update = proxy_props_update
    )
    proxy_path: bpy.props.StringProperty (
        name = "Path",
        description = "File path to the proxy model",
        default = "",
        subtype = 'FILE_PATH',
        update = proxy_props_update
    )
    proxy_index: bpy.props.IntProperty (
        name = "Index",
        description = "Index of proxy",
        default = 1,
        min = 0,
        max = 999,
        update = proxy_props_update
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
    cellsize_source: bpy.props.EnumProperty (
        name = "Source",
        description = "Source of raster spacing",
        items = (
            ('MANUAL', "Manual", "The raster spacing is explicitly set"),
            ('CALCULATED', "Calculated", "The raster spacing is from the distance of the first 2 points of the gird")
        ),
        default = 'MANUAL'
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