import bpy

from ..utilities import keyframes as frameutils


class A3OB_OT_keyframe_add_list(bpy.types.Operator):
    """Add list of keyframes to list of RTM frames"""
    
    bl_idname = "a3ob.keyframe_add_list"
    bl_label = "Add Frames"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and len(obj.pose.bones) > 0 and obj.animation_data and obj.animation_data.action
        
    def execute(self, context):
        obj = context.active_object
        object_props = obj.a3ob_properties_object_armature
        wm_props = context.window_manager.a3ob_keyframes
        
        if wm_props.clear:
            object_props.frames.clear()
            object_props.frames_index = -1
            
        if wm_props.mode == 'TIMELINE':
            count_frames = frameutils.add_frame_timeline(obj)
            self.report({'INFO'}, f"Added {count_frames} frame(s)")
        elif wm_props.mode == 'RANGE':
            count_frames = frameutils.add_frame_range(obj, wm_props)
            self.report({'INFO'}, f"Added {count_frames} frame(s)")
        
        return {'FINISHED'}


class A3OB_PT_keyframes(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "RTM Frames"
    
    @classmethod
    def poll(cls, context):
        return True
        
    # def draw_header(self, context):
        # layout = self.layout
        # row = layout.row(align=True)
        # row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3ObjectBuilder/wiki/Tool:-RTM-Frames"
        
    def draw(self, context):
        wm_props = context.window_manager.a3ob_keyframes
        layout = self.layout
        
        layout.prop(wm_props, "clear")
        layout.prop(wm_props, "mode", text="From", expand=True)
        
        if wm_props.mode == 'RANGE':
            col = layout.column(align=True)
            col.prop(wm_props, "range_start")
            col.prop(wm_props, "range_step")
            col.prop(wm_props, "range_end")
            
        layout.operator("a3ob.keyframe_add_list", icon='KEYFRAME_HLT')


classes = (
    A3OB_OT_keyframe_add_list,
    A3OB_PT_keyframes
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: RTM Frames")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: RTM Frames")