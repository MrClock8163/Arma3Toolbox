from . import generic as utils
from . import data

def get_lod_id(value):
    fraction, exponent = utils.normalize_float(value)

    if exponent < 3: # Escape at resolutions
        return 0, round(value)

    baseValue = utils.floor(fraction)

    if exponent in [3,16]: # LODs in these ranges have identifier values in the X.X positions not just X.0
        baseValue = utils.floor(fraction,1)

    index = data.LODtypeIndex.get((baseValue,exponent),30)

    resPosition = data.LODtypeResolutionPosition.get(index,None)
    resolution = 0

    if resPosition is not None:
        resolution = int(round((fraction-baseValue)* 10**resPosition,resPosition))

    return index,resolution
    
def get_lod_value(LODindex,resolution):    
    if LODindex == 0:
        return resolution
    
    index = list(data.LODtypeIndex.values()).index(LODindex,0)
    fraction, exponent = list(data.LODtypeIndex.keys())[LODindex]
    
    resPosition = data.LODtypeResolutionPosition.get(index,None)
    res = 0
    
    if resPosition is not None:
        res = resolution*10**(exponent-resPosition)
    
    return fraction*10**exponent + res
    
def get_lod_name(index):
    return data.LODdata.get(index,data.LODdata[30])[0]
    
def format_lod_name(index,res):
    if data.LODtypeResolutionPosition.get(index,None) is not None:
        return f"{get_lod_name(index)} {res}"
        
    return get_lod_name(index)