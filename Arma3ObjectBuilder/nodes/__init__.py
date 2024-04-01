
import bpy
import nodeitems_utils
from nodeitems_utils import NodeItem


class A3OB_MCFG_N_Tree(bpy.types.NodeTree):
    """Arma 3 Object Builder model config editor"""

    bl_label = "Model Config Editor"
    bl_icon = 'MESH_CUBE'


class A3OB_MCFG_N_base:
    @classmethod
    def poll(cls, node_tree):
        return node_tree.bl_idname == 'A3OB_MCFG_N_Tree'


classes = (
    A3OB_MCFG_N_Tree,
)


modules = (
    
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for mod in modules:
        mod.register()
    
    print("\t" + "Nodes")


def unregister():
    for mod in reversed(modules):
        mod.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "Nodes")