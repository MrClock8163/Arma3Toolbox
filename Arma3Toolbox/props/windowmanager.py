import bpy
from ..utilities import properties as proputils
from . import object as objectprops

def register():
    bpy.types.WindowManager.a3ob_namedprops_common = bpy.props.CollectionProperty(type=objectprops.A3OB_PG_properties_named_property)
    bpy.types.WindowManager.a3ob_namedprops_common_index = bpy.props.IntProperty(name="Selection index",default = -1)
    bpy.types.WindowManager.a3ob_enableVertexMass = bpy.props.BoolProperty (
        name = "Enable Vertex Mass Tools",
        description = "Dynamic calculation of the vertex masses can be performace heavy on large meshes",
        default = False
    )
    
def unregister():
    del bpy.types.WindowManager.a3ob_enableVertexMass
    del bpy.types.WindowManager.a3ob_namedprops_common_index
    del bpy.types.WindowManager.a3ob_namedprops_common