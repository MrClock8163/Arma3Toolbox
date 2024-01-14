import bpy


class A3OB_PG_properties_keyframe(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty(name="Frame Index", description="Index of the keyframe to export")


class A3OB_PG_properties_action(bpy.types.PropertyGroup):
    motion_source: bpy.props.EnumProperty(
        name = "Motion Source",
        description = "Source of motion vector",
        items = (
            ('MANUAL', "Manual", "The motion vector is explicitly set"),
            ('CALCULATED', "Calculated", "The motion vector is calculated from the motion of a specific bone during the animation")
        ),
        default = 'MANUAL'
    )
    motion_vector: bpy.props.FloatVectorProperty(
        name = "Motion Vector",
        description = "Total motion done during the animation",
        default = (0, 0, 0),
        subtype = 'XYZ',
        unit = 'LENGTH'
    )
    motion_bone: bpy.props.StringProperty(name="Reference Bone", description="Bone to track for motion calculation")
    frames: bpy.props.CollectionProperty(
        name = "RTM keyframes",
        description = "List of keyframes to export to RTM",
        type = A3OB_PG_properties_keyframe
    )
    frames_index: bpy.props.IntProperty(name="Active Keyrame Index")


classes = (
    A3OB_PG_properties_keyframe,
    A3OB_PG_properties_action
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Action.a3ob_properties_action = bpy.props.PointerProperty(type=A3OB_PG_properties_action)

    print("\t" + "Properties: action")


def unregister():
    del bpy.types.Action.a3ob_properties_action

    print("\t" + "Properties: action")