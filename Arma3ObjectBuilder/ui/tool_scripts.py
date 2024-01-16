import os

import bpy

from ..utilities import generic as utils


scripts = {
    "vertex_groups": {
        "Lowercase": "vertex_groups_lowercase.py",
        "Match Armature": "vertex_groups_match_armature_case.py"
    },
    "import": {
        "P3D batch": "import_p3d_batch.py",
        "RTM batch": "import_rtm_batch.py"
    },
    "misc": {
        "Convert ATBX to A3OB": "convert_atbx_to_a3ob.py"
    }
}


def get_scripts_directory():
    return os.path.join(utils.get_addon_directory(), "scripts")


class A3OB_MT_scripts_import(bpy.types.Menu):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        scripts_vgroups = scripts["import"]

        for item in scripts_vgroups:
            layout.operator("text.open", text=item).filepath = os.path.join(get_scripts_directory(), scripts_vgroups[item])


class A3OB_MT_scripts_vertex_groups(bpy.types.Menu):
    bl_label = "Vertex Groups"

    def draw(self, context):
        layout = self.layout
        scripts_vgroups = scripts["vertex_groups"]

        for item in scripts_vgroups:
            layout.operator("text.open", text=item).filepath = os.path.join(get_scripts_directory(), scripts_vgroups[item])


class A3OB_MT_scripts_misc(bpy.types.Menu):
    bl_label = "Misc"

    def draw(self, context):
        layout = self.layout
        scripts_vgroups = scripts["misc"]

        for item in scripts_vgroups:
            layout.operator("text.open", text=item).filepath = os.path.join(get_scripts_directory(), scripts_vgroups[item])


class A3OB_MT_scripts(bpy.types.Menu):
    """Utility scripts from Arma 3 Object Builder"""

    bl_label = "Scripts"

    def draw(self, context):
        layout = self.layout
        layout.menu("A3OB_MT_scripts_import")
        layout.menu("A3OB_MT_scripts_vertex_groups")
        layout.menu("A3OB_MT_scripts_misc")


classes = (
    A3OB_MT_scripts_import,
    A3OB_MT_scripts_vertex_groups,
    A3OB_MT_scripts_misc,
    A3OB_MT_scripts
)


def draw_scripts_menu(self, context):
    self.layout.separator()
    self.layout.menu("A3OB_MT_scripts", text="Object Builder", icon_value=utils.get_icon("addon"))


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.TEXT_MT_templates.append(draw_scripts_menu)
    
    print("\t" + "UI: Scripts")


def unregister():
    bpy.types.TEXT_MT_templates.remove(draw_scripts_menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: Scripts")