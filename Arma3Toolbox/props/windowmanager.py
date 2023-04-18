import bpy
from ..utilities import properties as proputils

def register():
    bpy.types.WindowManager.a3ob_enableVertexMass = bpy.props.BoolProperty (
        name = "Enable Vertex Mass Tools",
        description = "Dynamic calculation of the vertex masses can be performace heavy on large meshes",
        default = False
    )
    
def unregister():
    del bpy.types.WindowManager.a3ob_enableVertexMass