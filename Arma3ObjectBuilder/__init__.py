bl_info = {
    "name": "Arma 3 Object Builder",
    "description": "Collection of tools for editing Arma 3 content",
    "author": "MrClock (present add-on), Hans-Joerg \"Alwarren\" Frieden (original ArmaToolbox add-on)",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "Object Builder panels in various views",
    "warning": "Work In Progress",
    "wiki_url": "https://github.com/MrClock8163/Arma3ObjectBuilder/wiki",
    "tracker_url": "",
    "category": "3D View"
}


if "bpy" in locals():
    import importlib

    importlib.reload(ui.import_export_p3d)
    importlib.reload(ui.import_export_asc)
    importlib.reload(ui.utilities)
    importlib.reload(ui.mass)
    importlib.reload(ui.material)
    importlib.reload(ui.object_mesh)
    importlib.reload(ui.hitpoint)
    importlib.reload(ui.validation)
    importlib.reload(ui.conversion)
    importlib.reload(props.windowmanager)
    importlib.reload(props.object)
    importlib.reload(props.rvmat)

else:    
    from .ui import import_export_p3d
    from .ui import import_export_asc
    from .ui import utilities
    from .ui import mass
    from .ui import material
    from .ui import object_mesh
    from .ui import hitpoint
    from .ui import validation
    from .ui import conversion
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
    a3_tools: bpy.props.StringProperty (
        description = "Install directory of the official Arma 3 Tools",
        name = "Path",
        default = "",
        subtype = 'DIR_PATH'
    )
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
            # box.prop(self, "a3_tools", text="Arma 3 Tools", icon='TOOL_SETTINGS')
            row_label = box.row()
            row_label.label(text="There are no settings in this category at the present time")
            row_label.enabled = False
            
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
    import_export_asc.register()
    object_mesh.register()
    material.register()
    mass.register()
    hitpoint.register()
    validation.register()
    conversion.register()
    utilities.register()
    
    print("Register done")


def unregister():
    from bpy.utils import unregister_class

    print("Unregistering Arma 3 Object Builder ( '" + __name__ + "' )")
    
    for cls in reversed(classes):
        unregister_class(cls)

    utilities.unregister()
    conversion.unregister()
    validation.unregister()
    hitpoint.unregister()
    mass.unregister()
    material.unregister()
    object_mesh.unregister()
    import_export_asc.unregister()
    import_export_p3d.unregister()
    windowmanager.unregister()
    rvmat.unregister()
    object.unregister()
    
    print("Unregister done")
    
    
if __name__ == "__main__":
    register()