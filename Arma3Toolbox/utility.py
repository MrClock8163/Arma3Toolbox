import bpy
import math
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

def getLODid(value):
    fraction, exponent = floatNormalize(value)

    if exponent < 3: # Escape at resolutions
        return 0, round(value)

    baseValue = floor(fraction)

    if exponent in [3,16]: # LODs in these ranges have identifier values in the X.X positions not just X.0
        baseValue = floor(fraction,1)

    index = data.LODtypeIndex.get((baseValue,exponent),30)

    resPosition = data.LODtypeResolutionPosition.get(index,None)
    resolution = 0

    if resPosition is not None:
        resolution = int(round((fraction-baseValue)* 10**resPosition,resPosition))

    return index,resolution
    
def getLODname(index):
    return data.LODdata.get(index,data.LODdata[30])[0]
    
def getLODinfo(index):
    return data.LODdata.get(index,data.LODdata[30])
    
def formatLODname(index,res):
    if data.LODtypeResolutionPosition.get(index,None) is not None:
        return f"{getLODname(index)} {res}"
        
    return getLODname(index)