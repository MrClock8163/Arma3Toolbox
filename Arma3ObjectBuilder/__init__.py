bl_info = {
    "name": "Arma 3 Object Builder",
    "description": "Collection of tools for editing Arma 3 content",
    "author": "MrClock (present add-on), Hans-Joerg \"Alwarren\" Frieden (original ArmaToolbox add-on)",
    "version": (1, 0, 0, "rc"),
    "blender": (2, 90, 0),
    "location": "Object Builder panels",
    "warning": "Release candidate",
    "doc_url": "https://mrcmodding.gitbook.io/arma-3-object-builder/home",
    "tracker_url": "https://github.com/MrClock8163/Arma3ObjectBuilder/issues",
    "category": "3D View"
}


if "bpy" in locals():
    import importlib
    
    importlib.reload(props)
    importlib.reload(ui)

else:
    from . import props
    from . import ui


import winreg

import bpy


class A3OB_OT_find_a3_tools(bpy.types.Operator):
    """Find the Arma 3 Tools installation through the registry"""
    
    bl_idname = "a3ob.find_a3_tools"
    bl_label = "Find Arma 3 Tools"
    bl_options = {'UNDO'}
    
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


class A3OB_AT_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    tabs: bpy.props.EnumProperty (
        name = "Tabs",
        description = "",
        default = 'GENERAL',
        items = (
            ('GENERAL', "General", "General and misc settings", 'PREFERENCES', 0),
            ('PATHS', "Paths", "File path related settings", 'FILE_TICK', 1)
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
            row_a3_tools.operator("a3ob.find_a3_tools", text="", icon='VIEWZOOM')
            box.prop(self, "show_info_links")
            box.prop(self, "preserve_faulty_output")
            row_theme = box.row(align=True)
            row_theme.prop(self, "icon_theme", expand=True)
            
        elif self.tabs == 'PATHS':
            box.prop(self, "project_root", icon='DISK_DRIVE')
            box.prop(self, "export_relative")
            box.prop(self, "import_absolute")
            box.prop(self, "custom_data", icon='PRESET')


classes = (
    A3OB_OT_find_a3_tools,
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