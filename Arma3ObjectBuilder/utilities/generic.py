import math
import os
import json

import bpy

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


def normalize_float(number, precision = 4):
    if number == 0:
        return 0.0,1
    
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


def make_relative(path, root):
    path = path.lower()
    root = root.lower()
    
    if root != "" and path.startswith(root):
        return os.path.relpath(path, root)
    
    drive = os.path.splitdrive(path)[0]
    if drive:
       path = os.path.relpath(path, drive)
    
    return path


def strip_extension(path):
    return os.path.splitext(path)[0]


def get_addon_preferences():
    return bpy.context.preferences.addons["Arma3ObjectBuilder"].preferences


def get_common_proxies():
    prefs = get_addon_preferences()
    custom_path = abspath(prefs.custom_data)
    proxies = data.common_proxies
    
    if not os.path.exists(custom_path):
        return proxies
    
    custom_proxies = {}
    
    try:
        jsonfile = open(custom_path)
        customs = json.loads(jsonfile.read().replace("\\", "/"))
        jsonfile.close()
        custom_proxies = customs["proxies"]
    except:
        pass
        
    return {**proxies, **custom_proxies}


def get_common_namedprops():
    prefs = get_addon_preferences()
    custom_path = abspath(prefs.custom_data)
    namedprops = data.common_namedprops
    
    if not os.path.exists(custom_path):
        return namedprops
    
    custom_namedprops = {}
    
    try:
        jsonfile = open(custom_path)
        customs = json.loads(jsonfile.read().replace("\\", "/"))
        jsonfile.close()
        custom_namedprops = customs["namedprops"]
    except:
        pass
        
    return {**namedprops, **custom_namedprops}


def abspath(path):
    if not path.startswith("//"):
        return path
    
    return os.path.abspath(bpy.path.abspath(path))


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
    
    for icon in preview_collection:
        bpy.utils.previews.remove(icon)
    
    preview_collection.clear()