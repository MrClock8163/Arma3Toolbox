bl_info = {
    "name": "Arma 3 Object Builder",
    "description": "Collection of tools for editing Arma 3 content",
    "author": "MrClock, Hans-Joerg \"Alwarren\" Frieden (original add-on)",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Object Builder panels in various views",
    "warning": '',
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}

if "bpy" in locals():
    import importlib

    importlib.reload(ui.import_export)
    importlib.reload(ui.utilities)
    importlib.reload(ui.mass)
    importlib.reload(ui.material)
    importlib.reload(ui.object_mesh)
    importlib.reload(ui.hitpoint)
    importlib.reload(props.windowmanager)
    importlib.reload(props.object)
    importlib.reload(props.rvmat)

else:    
    from .ui import import_export
    from .ui import utilities
    from .ui import mass
    from .ui import material
    from .ui import object_mesh
    from .ui import hitpoint
    from .props import windowmanager
    from .props import object
    from .props import rvmat

import bpy
import os

class A3OB_AT_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    # Tab selection
    tabs: bpy.props.EnumProperty(
        name = "Tabs",
        description = "",
        default = 'GENERAL',
        items = (
            ('GENERAL',"General","General and misc settings",'PREFERENCES',0),
            ('PATHS',"Paths","File path related settings",'FILE_TICK',1)
        )
    )
    
    # Arma 3 Tools settings
    a3_tools: bpy.props.StringProperty(
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
            # grid = box.grid_flow(align=True,columns=2,row_major=True,even_columns=True,even_rows=True)
            # layout = self.layout
            # box.label(text="Arma 3 Tools")
            box.prop(self,"a3_tools",text="Arma 3 Tools",icon='TOOL_SETTINGS')
        elif self.tabs == 'PATHS':
            box.prop(self,"project_root",icon='DISK_DRIVE')
            box.prop(self,"export_relative")
            box.prop(self,"import_absolute")
            box.prop(self,"custom_data",icon='PRESET')

classes = (
    A3OB_AT_preferences,
)

def register():
    from bpy.utils import register_class
        
    print("Registering Arma 3 Toolbox ( '" + __name__ + "' )")
    
    for cls in classes:
        register_class(cls)
        
    import_export.register()
    utilities.register()
    object_mesh.register()
    mass.register()
    object.register()
    rvmat.register()
    material.register()
    windowmanager.register()
    hitpoint.register()
    
    print("Register done")

def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    hitpoint.unregister()
    windowmanager.unregister()
    material.unregister()
    rvmat.unregister()
    object.unregister()
    mass.unregister()
    object_mesh.unregister()
    utilities.unregister()
    import_export.unregister()
    
if __name__ == "__main__":
    register()