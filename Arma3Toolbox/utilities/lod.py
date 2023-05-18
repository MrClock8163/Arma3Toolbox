from . import generic as utils
from . import data

def get_lod_id(value):
    fraction, exponent = utils.normalize_float(value)

    if exponent < 3: # Escape at resolutions
        return 0, round(value)

    baseValue = utils.floor(fraction)

    if exponent in [3,16]: # LODs in these ranges have identifier values in the X.X positions not just X.0
        baseValue = utils.floor(fraction,1)

    index = data.lod_type_index.get((baseValue,exponent),30)

    resPosition = data.lod_resolution_position.get(index,None)
    resolution = 0

    if resPosition is not None:
        resolution = int(round((fraction-baseValue)* 10**resPosition,resPosition))

    return index,resolution
    
def get_lod_value(LODindex,resolution):    
    if LODindex == 0:
        return resolution
    
    index = list(data.lod_type_index.values()).index(LODindex,0)
    fraction, exponent = list(data.lod_type_index.keys())[LODindex]
    
    resPosition = data.lod_resolution_position.get(index,None)
    res = 0
    
    if resPosition is not None:
        res = resolution*10**(exponent-resPosition)
    
    return fraction*10**exponent + res
    
def get_lod_name(index):
    return data.lod_type_names.get(index,data.lod_type_names[30])[0]
    
def format_lod_name(index,res):
    if data.lod_resolution_position.get(index,None) is not None:
        return f"{get_lod_name(index)} {res}"
        
    return get_lod_name(index)