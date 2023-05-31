import bpy
import bpy_extras

from ..io import export_rtm


class A3OB_OP_export_rtm(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export keyframes to Arma 3 RTM"""
    
    bl_idname = "a3ob.export_rtm"
    bl_label = "Export RTM"
    bl_options = {'UNDO', 'PRESET'}
    filename_ext = ".rtm"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.rtm",
        options = {'HIDDEN'}
    )
    static_pose: bpy.props.BoolProperty (
        name = "Static Pose",
        description = "Export current frame as static pose",
        default = False
    )
    clamp: bpy.props.BoolProperty (
        name = "Clamp To Range",
        description = "Do not export frames outside of the animation start-end range",
        default = True
    )
    frame_start: bpy.props.IntProperty (
        name = "Start",
        description = "Starting frame of animation",
        default = 0
    )
    frame_end: bpy.props.IntProperty (
        name = "End",
        description = "Ending frame of animation",
        default = 100
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and len(obj.pose.bones) > 0
        
    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        
        return super().invoke(context, event)
        
    def execute(self, context):
        obj = context.active_object
                
        with open(self.filepath, "wb") as file:
            static, frame_count = export_rtm.write_file(self, context, file, obj)
            
        if not self.static_pose and static:
            self.report({'INFO'}, "No frames were added for export, exported as static pose")
        else:
            self.report({'INFO'}, f"Exported {frames} frame(s)")
            
        return {'FINISHED'}


classes = (
    A3OB_OP_export_rtm,
)


# def menu_func_import(self, context):
    # self.layout.operator(A3OB_OP_import_rtm.bl_idname, text="Arma 3 animation (.rtm)")


def menu_func_export(self, context):
    self.layout.operator(A3OB_OP_export_rtm.bl_idname, text="Arma 3 animation (.rtm)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    print("\t" + "UI: RTM Import / Export")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    # bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    
    print("\t" + "UI: RTM Import / Export")