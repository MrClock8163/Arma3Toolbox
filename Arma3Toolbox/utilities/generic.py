import bpy
import math
import os
import json
from . import data

def show_infoBox(message,title = "",icon = 'INFO'):
    def draw(self,context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw,title = title,icon = icon)
    
def floatNormalize(number,precision = 4):
    if number == 0:
        return 0.0,1
    
    base10 = math.log10(abs(number))
    exponent = abs(math.floor(base10))
    fraction = number / 10**exponent

    fraction = round(fraction,precision)
    exponentCorrection = 0
    
    if fraction >= 10.0: # Rounding after normalization may break the normalization (eg: 9.99999 -> 10.0000)
        fraction, exponentCorrection = floatNormalize(fraction,precision)

    return round(fraction,precision), exponent + exponentCorrection

def floor(number,precision = 0):
    return round(math.floor(number*10**precision)/10**precision,precision)

def forceObjectMode():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

def forceEditMode():
    forceObjectMode()
    bpy.ops.object.mode_set(mode='EDIT')
    
def createSelection(obj,selection):
    group = obj.vertex_groups.get(selection,None)
    
    if not group:
        group = obj.vertex_groups.new(name=selection.strip())

    group.add([vert.index for vert in obj.data.vertices],1,'REPLACE')

def replace_slashes(path):
    return path.replace("/","\\")

def make_relative(path,root):
    path = path.lower()
    root = root.lower()
    
    if root != "" and path.startswith(root):
        return os.path.relpath(path,root)
    
    drive = os.path.splitdrive(path)[0]
    if drive:
       path = os.path.relpath(path,drive)
    
    return path

def strip_extension(path):
    return os.path.splitext(path)[0]
    
def get_addon_preferences(context):
    name = __name__.split(".")[0]
    return context.preferences.addons[name].preferences
    
def get_common_proxies(context):
    prefs = get_addon_preferences(context)
    customPath = prefs.customDataPath
    
    proxies = data.common_proxies
    
    if not os.path.exists(customPath):
        return proxies
    
    customProxies = {}
    
    try:
        jsonfile = open(customPath)
        customs = json.loads(jsonfile.read().replace("\\","/"))
        jsonfile.close()

        customProxies = customs["proxies"]
    except:
        pass
        
    return {**proxies,**customProxies}
    
def get_common_namedprops(context):
    prefs = get_addon_preferences(context)
    customPath = prefs.customDataPath
    
    namedprops = data.common_namedprops
    
    if not os.path.exists(customPath):
        return namedprops
    
    customNamedprops = {}
    
    try:
        jsonfile = open(customPath)
        customs = json.loads(jsonfile.read().replace("\\","/"))
        jsonfile.close()
        
        customNamedprops = customs["namedprops"]
    except:
        pass
        
    return {**namedprops,**customNamedprops}