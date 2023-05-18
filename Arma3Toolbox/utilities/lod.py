from . import generic as utils
from . import data

def get_lod_id(value):
    fraction, exponent = utils.normalize_float(value)

    if exponent < 3: # Escape at resolutions
        return 0, round(value)

    base_value = utils.floor(fraction)

    if exponent in [3, 16]: # LODs in these ranges have identifier values in the X.X positions not just X.0
        base_value = utils.floor(fraction, 1)

    index = data.lod_type_index.get((base_value, exponent), 30)

    resolution_position = data.lod_resolution_position.get(index, None)
    resolution = 0

    if resolution_position is not None:
        resolution = int(round((fraction - base_value) * 10**resolution_position, resolution_position))

    return index, resolution
    
def get_lod_signature(index, resolution):    
    if index == 0:
        return resolution
    
    index = list(data.lod_type_index.values()).index(index, 0)
    fraction, exponent = list(data.lod_type_index.keys())[index]
    
    resolution_position = data.lod_resolution_position.get(index, None)
    res = 0
    
    if resolution_position is not None:
        res = resolution * 10**(exponent - resolution_position)
    
    return fraction * 10**exponent + res
    
def get_lod_name(index):
    return data.lod_type_names.get(index,data.lod_type_names[30])[0]
    
def format_lod_name(index, resolution):
    if data.lod_resolution_position.get(index, None) is not None:
        return f"{get_lod_name(index)} {resolution}"
        
    return get_lod_name(index)