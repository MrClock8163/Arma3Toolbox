# Utility functions not exclusively related to a specific tool.


import os
import json
from contextlib import contextmanager

import bpy
import bpy_extras.mesh_utils as meshutils
import bmesh

from . import data


def print_context():
    print("=======================")
    for attr in dir(bpy.context):
        print(attr, eval('bpy.context.%s' %  attr))
    print("=======================")


def show_info_box(message, title = "", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
        
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def abspath(path):
    if not path.startswith("//"):
        return path
    
    return os.path.abspath(bpy.path.abspath(path))


def strip_extension(path):
    return os.path.splitext(path)[0]


def get_addon_preferences():
    return bpy.context.preferences.addons["Arma3ObjectBuilder"].preferences


def is_valid_idx(index, subscriptable):
    return 0 <= index < len(subscriptable)


def draw_panel_header(panel):
    if not get_addon_preferences().show_info_links:
        return
        
    row = panel.layout.row(align=True)
    row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = panel.doc_url


@contextmanager
def edit_bmesh(obj, loop_triangles = False, destructive = False):
    mesh = obj.data
    if obj.mode == 'EDIT':
        try:
            yield bmesh.from_edit_mesh(mesh)
        finally:
            bmesh.update_edit_mesh(mesh, loop_triangles=loop_triangles, destructive=destructive)
    else:
        try:
            bm = bmesh.new()
            bm.from_mesh(mesh)
            yield bm
        finally:
            bm.to_mesh(mesh)
            bm.free()


@contextmanager
def query_bmesh(obj):
    mesh = obj.data
    if obj.mode == 'EDIT':
        try:
            bm = bmesh.from_edit_mesh(mesh)
            yield bm
        finally:
            bm.free()
    else:
        try:
            bm = bmesh.new()
            bm.from_mesh(mesh)
            yield bm
        finally:
            bm.free()


class OutputManager():
    def __init__(self, filepath, mode = "w"):
        self.filepath = filepath
        self.temppath = filepath + ".temp"
        self.mode = mode
        self.file = None
        self.success = False

    def __enter__(self):
        file = open(self.temppath, self.mode)
        self.file = file

        return file

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.file.close()
        addon_prefs = get_addon_preferences()

        if self.success:
            if os.path.isfile(self.filepath) and addon_prefs.create_backups:
                self.force_rename(self.filepath, self.filepath + ".bak")

            self.force_rename(self.temppath, self.filepath)
        
        elif not addon_prefs.preserve_faulty_output:
            os.remove(self.temppath)
        
        return False
    
    @staticmethod
    def force_rename(old, new):
        if os.path.isfile(new):
            os.remove(new)
        
        os.rename(old, new)


def get_components(mesh):
    mesh.calc_loop_triangles()
    components = meshutils.mesh_linked_triangles(mesh)
    component_lookup = {}

    for id, comp in enumerate(components):
        for tri in comp:
            for vert in tri.vertices:
                component_lookup[vert] = id
    
    loose = [vert.index for vert in mesh.vertices if component_lookup.get(vert.index, None) is None]
    count_components = len(components)
    component_lookup.update({id: count_components + i for i, id in enumerate(loose)})
    components.extend([[] for i in range(len(loose))])
    
    return component_lookup, components


def force_mode_object():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


def force_mode_edit():
    force_mode_object()
    bpy.ops.object.mode_set(mode='EDIT')


def create_selection(obj, selection):
    group = obj.vertex_groups.get(selection, None)
    if not group:
        group = obj.vertex_groups.new(name=selection.strip())

    group.add([vert.index for vert in obj.data.vertices], 1, 'REPLACE')


def replace_slashes(path):
    return path.replace("/", "\\")


# Attempt to restore absolute paths to the set project root (P drive by default).
def restore_absolute(path, extension = ""):
    path = replace_slashes(path.strip().lower())
    addon_prefs = get_addon_preferences()
    
    if path == "":
        return ""
    
    if os.path.splitext(path)[1].lower() != extension:
        path += extension
    
    root = abspath(addon_prefs.project_root).lower()
    if not path.startswith(root):
        abs_path = os.path.join(root, path)
        if os.path.exists(abs_path):
            return abs_path
    
    return path


def make_relative(path, root):
    path = path.lower()
    root = root.lower()
    
    if root != "" and path.startswith(root):
        return os.path.relpath(path, root)
    
    drive = os.path.splitdrive(path)[0]
    if drive:
       path = os.path.relpath(path, drive)
    
    return path


def format_path(path, root = "", to_relative = True, extension = True):
    path = replace_slashes(path.strip())
    
    if to_relative:
        root = replace_slashes(root.strip())
        path = make_relative(path, root)
        
    if not extension:
        path = strip_extension(path)
        
    return path


def get_addon_directory():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))


def get_cfg_convert():
    return os.path.join(get_addon_preferences().a3_tools, "cfgconvert/cfgconvert.exe")


def load_common_data(scene):
    prefs = get_addon_preferences()
    custom_path = abspath(prefs.custom_data)
    builtin = data.common_data
    json_data = {}
    try:
        with open(custom_path) as file:
            json_data = json.load(file)
    except:
        pass

    common = {key: {**builtin[key], **json_data.get(key, {})} for key in builtin}

    scene_props = scene.a3ob_commons
    scene_props.items.clear()
    for category, items in common.items():
        for name, value in items.items():
            item = scene_props.items.add()
            item.name = name
            item.value = value
            item.type = category.upper()
    
    scene_props.items_index = 0


preview_collection = {}


def get_icon(name):
    icon = 0
    try:
        icon = preview_collection[get_addon_preferences().icon_theme.lower()][name].icon_id
    except:
        pass
        
    return icon


def register_icons():
    import bpy.utils.previews
    
    themes_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../icons"))
    for theme in os.listdir(themes_dir):
        theme_icons = bpy.utils.previews.new()
        
        icons_dir = os.path.join(themes_dir, theme)
        for filename in os.listdir(icons_dir):
            theme_icons.load(os.path.splitext(os.path.basename(filename))[0].lower(), os.path.join(icons_dir, filename), 'IMAGE')
        
        preview_collection[theme.lower()] = theme_icons
    

def unregister_icons():
    import bpy.utils.previews
    
    for icon in preview_collection.values():
        bpy.utils.previews.remove(icon)
    
    preview_collection.clear()