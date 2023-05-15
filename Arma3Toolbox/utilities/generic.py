import bpy
import math

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