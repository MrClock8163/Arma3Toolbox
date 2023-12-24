# Utility functions not exclusively related to a specific tool.


import math
import os
import json

import bpy
import bpy_extras.mesh_utils as meshutils

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


def normalize_float(number, precision = 4):
    if number == 0:
        return 0.0, 1
    
    base10 = math.log10(abs(number))
    exponent = abs(math.floor(base10))
    fraction = round(number / 10**exponent, precision)
    
    correction = 0
    if fraction >= 10.0: # Rounding after normalization may break the normalization (eg: 9.99999 -> 10.0000)
        fraction, correction = normalize_float(fraction, precision)

    return round(fraction, precision), exponent + correction


def floor(number, precision = 0):
    return round(math.floor(number * 10**precision) / 10**precision, precision)


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
    
    if not addon_prefs.import_absolute:
        return path
    
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


def get_common(name):
    prefs = get_addon_preferences()
    custom_path = abspath(prefs.custom_data)
    builtin = data.common_data[name]

    if not os.path.exists(custom_path):
        return builtin, {}
    
    custom = {}
    try:
        with open(custom_path) as file:
            custom = json.load(file)[name]
    except:
        return builtin, None

    return builtin, custom


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
    
    themes_dir = os.path.join(os.path.dirname(__file__), "..\icons")
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