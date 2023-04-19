from . import generic as utils
from . import data

def getLODid(value):
    fraction, exponent = utils.floatNormalize(value)

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
    
def getLODname(index):
    return data.LODdata.get(index,data.LODdata[30])[0]
    
def formatLODname(index,res):
    if data.LODtypeResolutionPosition.get(index,None) is not None:
        return f"{getLODname(index)} {res}"
        
    return getLODname(index)