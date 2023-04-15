import bpy
from ..utilities import properties as proputils

def register():
    bpy.types.Object.a3ob_selectionMass = bpy.props.FloatProperty (
        name = "Current mass",
        description = "Total mass of current selection",
        default = 0.0,
        min = 0,
        max = 1000000,
        step = 10,
        soft_max = 100000,
        precision = 3,
        unit = 'MASS',
        get = proputils.selectionMassGet,
        set = proputils.selectionMassSet
    )
    
    bpy.types.Object.a3ob_selectionMassTarget = bpy.props.FloatProperty (
        name = "Mass",
        description = "Mass to set equally or distribute",
        default = 0.0,
        unit = 'MASS',
        min = 0,
        max = 1000000,
        soft_max = 100000,
        step = 10,
        precision = 3
    )
    
def unregister():
    del bpy.types.Object.a3ob_selectionMassTarget
    del bpy.types.Object.a3ob_selectionMass