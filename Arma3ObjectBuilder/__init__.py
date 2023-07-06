bl_info = {
    "name": "Arma 3 Object Builder",
    "description": "Collection of tools for editing Arma 3 content",
    "author": "MrClock (present add-on), Hans-Joerg \"Alwarren\" Frieden (original ArmaToolbox add-on)",
    "version": (0, 3, 2),
    "blender": (2, 80, 0),
    "location": "Object Builder panels in various views",
    "warning": "Work In Progress",
    "wiki_url": "https://mrcmodding.gitbook.io/arma-3-object-builder/home",
    "tracker_url": "https://github.com/MrClock8163/Arma3ObjectBuilder/issues",
    "category": "3D View"
}


if "bpy" in locals():
    import importlib

    importlib.reload(ui.import_export_p3d)
    importlib.reload(ui.import_export_rtm)
    importlib.reload(ui.import_export_asc)
    importlib.reload(ui.tool_utilities)
    importlib.reload(ui.tool_mass)
    importlib.reload(ui.props_material)
    importlib.reload(ui.props_object_mesh)
    importlib.reload(ui.props_object_armature)
    importlib.reload(ui.tool_hitpoint)
    importlib.reload(ui.tool_validation)
    importlib.reload(ui.tool_proxies)
    importlib.reload(ui.tool_rtm)
    importlib.reload(ui.tool_conversion)
    importlib.reload(ui.tool_paths)
    importlib.reload(ui.tool_color)
    importlib.reload(ui.tool_weights)
    importlib.reload(props.windowmanager)
    importlib.reload(props.object)
    importlib.reload(props.rvmat)

else:    
    from .ui import import_export_p3d
    from .ui import import_export_rtm
    from .ui import import_export_asc
    from .ui import tool_utilities
    from .ui import tool_mass
    from .ui import props_material
    from .ui import props_object_mesh
    from .ui import props_object_armature
    from .ui import tool_hitpoint
    from .ui import tool_validation
    from .ui import tool_proxies
    from .ui import tool_rtm
    from .ui import tool_conversion
    from .ui import tool_paths
    from .ui import tool_color
    from .ui import tool_weights
    from .props import windowmanager
    from .props import object
    from .props import rvmat


import bpy


class A3OB_AT_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    tabs: bpy.props.EnumProperty (
        name = "Tabs",
        description = "",
        default = 'GENERAL',
        items = (
            ('GENERAL',"General","General and misc settings",'PREFERENCES',0),
            ('PATHS',"Paths","File path related settings",'FILE_TICK',1)
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
        name = "Show Tool Help Links",
        description = "Display links to the addon documentation in the headers of tool panels",
        default = True
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
            box.prop(self, "a3_tools", icon='TOOL_SETTINGS')
            box.prop(self, "show_info_links")
            
        elif self.tabs == 'PATHS':
            box.prop(self, "project_root", icon='DISK_DRIVE')
            box.prop(self, "export_relative")
            box.prop(self, "import_absolute")
            box.prop(self, "custom_data", icon='PRESET')


classes = (
    A3OB_AT_preferences,
)


def register():
    from bpy.utils import register_class
        
    print("Registering Arma 3 Object Builder ( '" + __name__ + "' )")
    
    for cls in classes:
        register_class(cls)
        
    object.register()
    rvmat.register()
    windowmanager.register()
    import_export_p3d.register()
    import_export_rtm.register()
    import_export_asc.register()
    props_object_mesh.register()
    props_object_armature.register()
    props_material.register()
    tool_mass.register()
    tool_hitpoint.register()
    tool_paths.register()
    tool_proxies.register()
    tool_validation.register()
    tool_rtm.register()
    tool_conversion.register()
    tool_color.register()
    tool_weights.register()
    tool_utilities.register()
    
    print("Register done")


def unregister():
    from bpy.utils import unregister_class

    print("Unregistering Arma 3 Object Builder ( '" + __name__ + "' )")
    
    for cls in reversed(classes):
        unregister_class(cls)

    tool_utilities.unregister()
    tool_weights.unregister()
    tool_color.unregister()
    tool_conversion.unregister()
    tool_rtm.unregister()
    tool_validation.unregister()
    tool_proxies.unregister()
    tool_paths.unregister()
    tool_hitpoint.unregister()
    tool_mass.unregister()
    props_material.unregister()
    props_object_armature.unregister()
    props_object_mesh.unregister()
    import_export_asc.unregister()
    import_export_rtm.unregister()
    import_export_p3d.unregister()
    windowmanager.unregister()
    rvmat.unregister()
    object.unregister()
    
    print("Unregister done")
    
    
if __name__ == "__main__":
    register()