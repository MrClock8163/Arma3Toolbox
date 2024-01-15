from math import floor, ceil

import bpy

from ..utilities import generic as utils


class A3OB_OT_rtm_frames_add(bpy.types.Operator):
    """Add current frame to list of RTM frames"""
    
    bl_idname = "a3ob.rtm_frames_add"
    bl_label = "Add Frame"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_action
        
    def execute(self, context):
        action = context.active_action
        action_props = action.a3ob_properties_action
        
        for frame in action_props.frames:
            if frame.index == context.scene.frame_current:
                self.report({'INFO'}, "The current frame is already in the list")
                return {'FINISHED'}
        
        item = action_props.frames.add()
        item.index = context.scene.frame_current
            
        return {'FINISHED'}


class A3OB_OT_rtm_frames_remove(bpy.types.Operator):
    """Remove selected frame from list of RTM frames"""
    
    bl_idname = "a3ob.rtm_frames_remove"
    bl_label = "Remove Frame"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if not context.active_action:
            return False
        
        action_props = context.active_action.a3ob_properties_action
        return utils.is_valid_idx(action_props.frames_index, action_props.frames)
        
    def execute(self, context):
        action_props = context.active_action.a3ob_properties_action
        
        action_props.frames.remove(action_props.frames_index)
        if len(action_props.frames) == 0:
            action_props.frames_index = -1
        else:
            action_props.frames_index = len(action_props.frames) - 1
            
        return {'FINISHED'}


class A3OB_OT_rtm_frames_clear(bpy.types.Operator):
    """Clear all frames from list of RTM frames"""
    
    bl_idname = "a3ob.rtm_frames_clear"
    bl_label = "Clear Frames"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_action and len(context.active_action.a3ob_properties_action.frames) > 0
        
    def execute(self, context):
        action_props = context.active_action.a3ob_properties_action
        
        action_props.frames.clear()
        action_props.frames_index = -1
            
        return {'FINISHED'}


class A3OB_OT_rtm_frames_add_range(bpy.types.Operator):
    """Add range of frames to list of RTM frames"""
    
    bl_idname = "a3ob.rtm_frames_add_range"
    bl_label = "Add Frame Range"
    bl_options = {'REGISTER', 'UNDO'}

    clear: bpy.props.BoolProperty(
        name = "Clear Existing",
        description = "Clear existing frames before adding the range",
        default = True
    )
    start: bpy.props.IntProperty(
        name = "Start",
        description = "First frame to add",
        default = 1,
        min = 0
    )
    step: bpy.props.IntProperty(
        name = "Step",
        description = "Step between frames",
        default = 5,
        min = 1
    )
    end: bpy.props.IntProperty(
        name = "End",
        description = "Last frame to add",
        default = 10,
        min = 0
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_action

    def invoke(self, context, event):
        action = context.active_action
        frame_range = action.frame_range
        self.start = floor(frame_range[0])
        self.end = ceil(frame_range[1])

        return self.execute(context)
        
    def execute(self, context):
        action = context.active_action
        action_props = action.a3ob_properties_action

        current_frames = [frame.index for frame in action_props.frames]

        action_props.frames.clear()

        new_frames = list(range(self.start, self.end + 1, self.step))
        if not self.clear:
            new_frames.extend(current_frames)

        new_frames.append(self.end)
        new_frames = list(set(new_frames))
        
        for idx in new_frames:
            item = action_props.frames.add()
            item.index = idx
            
        return {'FINISHED'}

 
class A3OB_UL_rtm_frames(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        index = item.index
        split = layout.split(factor=0.3)
        split.label(text=str(index))
        
        frame_range = context.scene.frame_end - context.scene.frame_start
        if frame_range > 0:
            phase = (index - context.scene.frame_start) / frame_range
            split.label(text="{:.6f}".format(phase))
        
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        
        sorter = [(index, frame) for index, frame in enumerate(getattr(data, propname))]
        flt_neworder = helper_funcs.sort_items_helper(sorter, lambda f: f[1].index, False)
        
        return flt_flags, flt_neworder


class A3OB_PT_action(bpy.types.Panel):
    bl_region_type = 'UI'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_label = "RTM Properties"
    bl_context = "data"
    bl_category = "Object Builder"
    
    @classmethod
    def poll(cls, context):
        return context.active_action
        
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/rtm"
        
    def draw(self, context):
        action = context.active_action
        action_props = action.a3ob_properties_action
        
        layout = self.layout
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        row_enum = col.row()
        row_enum.prop(action_props, "motion_source", expand=True)
        
        if action_props.motion_source == 'MANUAL':
            col.prop(action_props, "motion_vector", text=" ")
        else:
            obj = context.object
            if obj and obj.type == 'ARMATURE':
                col.prop_search(action_props, "motion_bone", obj.data, "bones",  text="Reference", results_are_suggestions=True)
            else:
                col.prop(action_props, "motion_bone", icon='BONE_DATA')


class A3OB_PT_action_frames(bpy.types.Panel):
    bl_region_type = 'UI'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_label = "Frames"
    bl_context = "data"
    bl_parent_id = "A3OB_PT_action"
    
    @classmethod
    def poll(cls, context):
        return context.active_action
        
    def draw(self, context):
        action = context.active_action
        action_props = action.a3ob_properties_action
        
        layout = self.layout
        
        row = layout.row()
        col_list = row.column()
        split_header = col_list.split(factor=0.3)
        split_header.label(text="Index")
        split_header.label(text="Phase")
        col_list.template_list("A3OB_UL_rtm_frames", "A3OB_frames", action_props, "frames", action_props, "frames_index")
        
        col_operators = row.column(align=True)
        col_operators.operator("a3ob.rtm_frames_add", text="", icon = 'ADD')
        col_operators.operator("a3ob.rtm_frames_remove", text="", icon = 'REMOVE')
        col_operators.separator()
        col_operators.operator("a3ob.rtm_frames_add_range", text="", icon = 'ARROW_LEFTRIGHT')
        col_operators.separator()
        col_operators.operator("a3ob.rtm_frames_clear", text="", icon = 'TRASH')


classes = (
    A3OB_OT_rtm_frames_add,
    A3OB_OT_rtm_frames_remove,
    A3OB_OT_rtm_frames_clear,
    A3OB_OT_rtm_frames_add_range,
    A3OB_UL_rtm_frames,
    A3OB_PT_action,
    A3OB_PT_action_frames
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: action properties")


def unregister():    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: action properties")