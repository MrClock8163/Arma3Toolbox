import bpy


class A3OB_PG_rigging(bpy.types.PropertyGroup):
    prune_threshold: bpy.props.FloatProperty(
        name = "Threshold",
        description = "Weight threshold for pruning selections",
        min = 0.0,
        max = 1.0,
        default = 0.001,
        precision = 3
    )


classes = (
    A3OB_PG_rigging,
)


def register_props():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.a3ob_rigging = bpy.props.PointerProperty(type=A3OB_PG_rigging)


def unregister_props():
    del bpy.types.Scene.a3ob_rigging

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
