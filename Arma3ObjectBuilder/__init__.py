bl_info = {
    "name": "Arma 3 Object Builder",
    "description": "Collection of tools for editing Arma 3 content",
    "author": "MrClock (present add-on), Hans-Joerg \"Alwarren\" Frieden (original ArmaToolbox add-on)",
    "version": (2, 0, 0, "rc"),
    "blender": (2, 90, 0),
    "location": "Object Builder panels",
    "warning": "",
    "doc_url": "https://mrcmodding.gitbook.io/arma-3-object-builder/home",
    "tracker_url": "https://github.com/MrClock8163/Arma3ObjectBuilder/issues",
    "category": "3D View"
}


if "bpy" in locals():
    import importlib
    
    importlib.reload(props)
    importlib.reload(ui)
    importlib.reload(utilities.flags)

else:
    from . import props
    from . import ui
    from .utilities import flags as flagutils


import winreg

import bpy


def outliner_enable_update(self, context):
    if self.outliner == 'ENABLED' and ui.tool_outliner.depsgraph_update_post_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(ui.tool_outliner.depsgraph_update_post_handler)
        ui.tool_outliner.depsgraph_update_post_handler(context.scene, None)
    elif self.outliner == 'DISABLED' and ui.tool_outliner.depsgraph_update_post_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(ui.tool_outliner.depsgraph_update_post_handler)
        context.scene.a3ob_outliner.clear()


class A3OB_OT_prefs_find_a3_tools(bpy.types.Operator):
    """Find the Arma 3 Tools installation through the registry"""
    
    bl_idname = "a3ob.prefs_find_a3_tools"
    bl_label = "Find Arma 3 Tools"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"software\bohemia interactive\arma 3 tools")
            value, _type = winreg.QueryValueEx(key, "path")
            prefs = context.preferences.addons["Arma3ObjectBuilder"].preferences
            prefs.a3_tools = value
            
        except Exception:
            self.report({'ERROR'}, "The Arma 3 Tools installation could not be found, it has to be set manually")
        
        return {'FINISHED'}


class A3OB_OT_prefs_edit_flag_vertex(bpy.types.Operator):
    """Set the default vertex flag value"""

    bl_idname = "a3ob.prefs_edit_flag_vertex"
    bl_label = "Edit"
    bl_options = {'REGISTER', 'UNDO'}

    surface: bpy.props.EnumProperty (
        name = "Surface",
        description = "",
        items = (
            ('NORMAL', "Normal", ""),
            ('SURFACE_ON', "On Surface", ""),
            ('SURFACE_ABOVE', "Above Surface", ""),
            ('SURFACE_UNDER', "Under Surface", ""),
            ('KEEP_HEIGHT', "Keep Height", "")
        ),
        default = 'NORMAL'
    )
    fog: bpy.props.EnumProperty (
        name = "Fog",
        description = "",
        items = (
            ('NORMAL', "Normal", ""),
            ('SKY', "Sky", ""),
            ('NONE', "None", "")
        ),
        default = 'NORMAL'
    )
    decal: bpy.props.EnumProperty (
        name = "Decal",
        description = "",
        items = (
            ('NORMAL', "Normal", ""),
            ('DECAL', "Decal", "")
        ),
        default = 'NORMAL'
    )
    lighting: bpy.props.EnumProperty (
        name = "Lighting",
        description = "",
        items = (
            ('NORMAL', "Normal", ""),
            ('SHINING', "Shining", ""),
            ('SHADOW', "Always in Shadow", ""),
            ('LIGHTED_HALF', "Half Lighted", ""),
            ('LIGHTED_FULL', "Fully Lighted", ""),
        ),
        default = 'NORMAL'
    )
    normals: bpy.props.EnumProperty (
        name = "Normals",
        description = "Weighted average calculation mode",
        items = (
            ('AREA', "Face Dimension", ""),
            ('ANGLE', "Impedance Angle", ""),
            ('FIXED', "Fixed", ""),
        ),
        default = 'AREA'
    )
    hidden: bpy.props.BoolProperty (
        name = "Hidden Vertex",
        description = "",
        default = False # True: 0x00000000 False: 0x01000000
    )
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        prefs = context.preferences.addons["Arma3ObjectBuilder"].preferences
        flagutils.set_flag_vertex(self, prefs.flag_vertex)

        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        prefs = context.preferences.addons["Arma3ObjectBuilder"].preferences
        prefs.flag_vertex = flagutils.get_flag_vertex(self)

        return {'FINISHED'}


class A3OB_OT_prefs_edit_flag_face(bpy.types.Operator):
    """Set the default face flag value"""

    bl_idname = "a3ob.prefs_edit_flag_face"
    bl_label = "Edit"
    bl_options = {'REGISTER', 'UNDO'}
    
    lighting: bpy.props.EnumProperty (
        name = "Lighting & Shadows",
        description = "",
        items = (
            ('NORMAL', "Normal", ""),
            ('BOTH', "Both Sides", ""),
            ('POSITION', "Position", ""),
            ('FLAT', "Flat", ""),
            ('REVERSED', "Reversed", "")
        ),
        default = 'NORMAL'
    )
    zbias: bpy.props.EnumProperty (
        name = "Z Bias",
        description = "",
        items = (
            ('NONE', "None", ""),
            ('LOW', "Low", ""),
            ('MIDDLE', "Middle", ""),
            ('HIGH', "High", "")
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

    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        prefs = context.preferences.addons["Arma3ObjectBuilder"].preferences
        flagutils.set_flag_face(self, prefs.flag_face)

        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        prefs = context.preferences.addons["Arma3ObjectBuilder"].preferences
        prefs.flag_face = flagutils.get_flag_face(self)

        return {'FINISHED'}


class A3OB_AT_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    tabs: bpy.props.EnumProperty (
        name = "Tabs",
        description = "",
        default = 'GENERAL',
        items = (
            ('GENERAL', "General", "General and misc settings", 'PREFERENCES', 0),
            ('PATHS', "Paths", "File path related settings", 'FILE_TICK', 1),
            ('DEFAULTS', "Defaults", "Default fallback values", 'RECOVER_LAST', 2)
        )
    )
    # General
    a3_tools: bpy.props.StringProperty (
        name = "Arma 3 Tools",
        description = "Install directory of the official Arma 3 Tools",
        default = "",
        subtype = 'DIR_PATH'
    )
    show_info_links: bpy.props.BoolProperty (
        name = "Show Help Links",
        description = "Display links to the addon documentation in the headers of panels",
        default = True
    )
    preserve_faulty_output: bpy.props.BoolProperty (
        name = "Preserve Faulty Output",
        description = "Preserve the .temp files if an export failed (could be useful to attach to a bug report)",
        default = False
    )
    icon_theme: bpy.props.EnumProperty (
        name = "Icon Theme",
        description = "Color theme of custom icons",
        items = (
            ('DARK', "Dark", "Icons with light main color, ideal for dark themes in Blender"),
            ('LIGHT', "Light", "Icons with dark main color, ideal for light themes in Blender")
        ),
        default = 'DARK'
    )
    outliner: bpy.props.EnumProperty (
        name = "Outliner",
        description = "Enable or disable LOD object outliner panel",
        items = (
            ('ENABLED', "Enabled", ""),
            ('DISABLED', "Disabled", "")
        ),
        default = 'ENABLED',
        update = outliner_enable_update
    )
    # Paths
    project_root: bpy.props.StringProperty (
        name = "Project Root",
        description = "Root directory of the project (should be P:\ for most cases)",
        default = "P:\\",
        subtype = 'DIR_PATH'
    )
    export_relative: bpy.props.BoolProperty (
        name = "Export Relative",
        description = "Export file paths as relative to the project root",
        default = True
    )
    import_absolute: bpy.props.BoolProperty (
        name = "Reconstruct Absolute Paths",
        description = "Attempt to reconstruct absolute file paths during import (based on the project root)",
        default = True
    )
    custom_data: bpy.props.StringProperty (
        name = "Custom Data",
        description = "Path to JSON file containing data for custom preset list items (common named properties and proxies)",
        default = "",
        subtype = 'FILE_PATH'
    )
    flag_vertex: bpy.props.IntProperty (
        name = "Vertex Flag",
        description = "Default vertex flag",
        default = 0x02000000,
        options = {'HIDDEN'}
    )
    flag_face: bpy.props.IntProperty (
        name = "Face Flag",
        description = "Default face flag",
        default = 0
    )
    
    def draw(self,context):
        layout = self.layout
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self,"tabs",expand=True)
        box = col.box()
        box.use_property_split = True
        box.use_property_decorate = False
        
        if self.tabs == 'GENERAL':
            row_a3_tools = box.row(align=True)
            row_a3_tools.prop(self, "a3_tools", icon='TOOL_SETTINGS')
            row_a3_tools.operator("a3ob.prefs_find_a3_tools", text="", icon='VIEWZOOM')
            box.prop(self, "show_info_links")
            box.prop(self, "preserve_faulty_output")
            row_theme = box.row(align=True)
            row_theme.prop(self, "icon_theme", expand=True)
            row_outliner = box.row(align=True)
            row_outliner.prop(self, "outliner", expand=True)
            
        elif self.tabs == 'PATHS':
            box.prop(self, "project_root", icon='DISK_DRIVE')
            box.prop(self, "export_relative")
            box.prop(self, "import_absolute")
            box.prop(self, "custom_data", icon='PRESET')
        
        elif self.tabs == 'DEFAULTS':
            col_flags = box.column(heading="Flags")
            
            row_vertex = col_flags.row(align=True)
            row_vertex.label(text="Vertex Flag")
            row_vertex.label(text="%08x" % self.flag_vertex)
            row_vertex.operator("a3ob.prefs_edit_flag_vertex", text="", icon='GREASEPENCIL')
            
            row_face = col_flags.row(align=True)
            row_face.label(text="Face Flag")
            row_face.label(text="%08x" % self.flag_face)
            row_face.operator("a3ob.prefs_edit_flag_face", text="", icon='GREASEPENCIL')


classes = (
    A3OB_OT_prefs_find_a3_tools,
    A3OB_OT_prefs_edit_flag_vertex,
    A3OB_OT_prefs_edit_flag_face,
    A3OB_AT_preferences
)


modules = (
    props.object,
    props.material,
    props.scene,
    ui.props_object_mesh,
    ui.props_object_armature,
    ui.props_material,
    ui.import_export_p3d,
    ui.import_export_rtm,
    ui.import_export_asc,
    ui.tool_outliner,
    ui.tool_mass,
    ui.tool_hitpoint,
    ui.tool_paths,
    ui.tool_proxies,
    ui.tool_validation,
    ui.tool_rtm,
    ui.tool_conversion,
    ui.tool_color,
    ui.tool_weights,
    ui.tool_utilities
)


def register():
    from bpy.utils import register_class
    from .utilities import generic
        
    print("Registering Arma 3 Object Builder ( '" + __name__ + "' )")
    
    for cls in classes:
        register_class(cls)
    
    for mod in modules:
        mod.register()
    
    generic.register_icons()
    
    print("Register done")


def unregister():
    from bpy.utils import unregister_class
    from .utilities import generic

    print("Unregistering Arma 3 Object Builder ( '" + __name__ + "' )")
    
    generic.unregister_icons()
    
    for mod in reversed(modules):
        mod.unregister()
    
    for cls in reversed(classes):
        unregister_class(cls)
    
    print("Unregister done")