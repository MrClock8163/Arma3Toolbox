import bpy
from ..utilities import properties as proputils

def register():
    bpy.types.Scene.a3ob_enableVertexMass = bpy.props.BoolProperty (
        name = "Enable vertex mass tools",
        description = "Dynamic calculation of the vertex masses can be performace heavy on large meshes",
        default = False
    )
    
def unregister():
    del bpy.types.Scene.a3ob_enableVertexMass