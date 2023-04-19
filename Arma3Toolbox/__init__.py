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

import sys, os

if "bpy" in locals():
    import importlib

    importlib.reload(ui.import_export)
    importlib.reload(ui.utilities)
    importlib.reload(ui.mass)
    importlib.reload(ui.material)
    importlib.reload(ui.object_mesh)
    importlib.reload(props.windowmanager)
    importlib.reload(props.object)
    importlib.reload(props.rvmat)

else:    
    from .ui import import_export
    from .ui import utilities
    from .ui import mass
    from .ui import material
    from .ui import object_mesh
    from .props import windowmanager
    from .props import object
    from .props import rvmat

import bpy
import os

class A3OB_AT_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    # Tab selection
    tabs: bpy.props.EnumProperty(
        name = "Tabs",
        description = "",
        default = 'GENERAL',
        items = (
            ('GENERAL',"General","General and misc settings",'PREFERENCES',0),
        )
    )
    
    # Arma 3 Tools settings
    armaToolsFolder: bpy.props.StringProperty(
        description = "Install directory of the official Arma 3 Tools",
        name = "Path",
        default = "",
        subtype = 'DIR_PATH'
    )
    
    def draw(self,context):
        layout = self.layout
        
        row = layout.row(align=True)
        row.prop(self,"tabs",expand=True)
        box = layout.box()
        
        if self.tabs == 'GENERAL':
            grid = box.grid_flow(align=True,columns=2,row_major=True,even_columns=True,even_rows=True)
            grid.label(text="Arma 3 Tools")
            grid.prop(self,"armaToolsFolder",text="")

classes = (
    A3OB_AT_Preferences,
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
    windowmanager.register()
    object.register()
    rvmat.register()
    material.register()
    
    print("Register done")

def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    material.unregister()
    rvmat.unregister()
    object.unregister()
    windowmanager.unregister()
    mass.unregister()
    object_mesh.unregister()
    utilities.unregister()
    import_export.unregister()
    
if __name__ == "__main__":
    register()