import bpy

from ..utilities import generic as utils


class A3OB_OT_keyframe_add(bpy.types.Operator):
    """Add current keyframe to list of RTM frames"""
    
    bl_idname = "a3ob.keyframe_add"
    bl_label = "Add Keyframe"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'ARMATURE'
        
    def execute(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_armature
        
        for frame in object_props.frames:
            if frame.index == context.scene.frame_current:
                return {'FINISHED'}
        
        item = object_props.frames.add()
        item.index = context.scene.frame_current
            
        return {'FINISHED'}


class A3OB_OT_keyframe_remove(bpy.types.Operator):
    """Remove selected keyframe from list of RTM frames"""
    
    bl_idname = "a3ob.keyframe_remove"
    bl_label = "Remove Keyframe"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_armature
        return obj and obj.type == 'ARMATURE' and object_props.frames_index in range(len(object_props.frames))
        
    def execute(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_armature
        
        object_props.frames.remove(object_props.frames_index)
        if len(object_props.frames) == 0:
            object_props.frames_index = -1
        else:
            object_props.frames_index = len(object_props.frames) - 1
            
        return {'FINISHED'}


class A3OB_OT_keyframe_clear(bpy.types.Operator):
    """Clear all keyframes from list of RTM frames"""
    
    bl_idname = "a3ob.keyframe_clear"
    bl_label = "Clear Keyframes"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_armature
        return obj and obj.type == 'ARMATURE' and len(object_props.frames) > 0
        
    def execute(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_armature
        
        object_props.frames.clear()
        object_props.frames_index = -1
            
        return {'FINISHED'}


class A3OB_PT_object_armature(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Object Builder: RTM Properties"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'ARMATURE'
        
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://mrcmodding.gitbook.io/arma-3-object-builder/properties/rtm"
        
    def draw(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_armature
        
        layout = self.layout
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        row_enum = col.row()
        row_enum.prop(object_props, "motion_source", expand=True)
        
        if object_props.motion_source == 'MANUAL':
            col.prop(object_props, "motion_vector", text=" ")
        else:
            col.prop_search(object_props, "motion_bone", obj.data, "bones",  text="Reference")


class A3OB_PT_object_armature_frames(bpy.types.Panel):
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "Frames"
    bl_context = "data"
    bl_parent_id = "A3OB_PT_object_armature"
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'ARMATURE'
        
    def draw(self, context):
        obj = context.object
        object_props = obj.a3ob_properties_object_armature
        
        layout = self.layout
        
        row = layout.row()
        col_list = row.column()
        split_header = col_list.split(factor=0.3)
        split_header.label(text="Index")
        split_header.label(text="Phase")
        col_list.template_list("A3OB_UL_keyframes", "A3OB_keyframes", object_props, "frames", object_props, "frames_index")
        
        col_operators = row.column(align=True)
        col_operators.operator("a3ob.keyframe_add", text="", icon = 'ADD')
        col_operators.operator("a3ob.keyframe_remove", text="", icon = 'REMOVE')
        col_operators.separator()
        col_operators.operator("a3ob.keyframe_clear", text="", icon = 'TRASH')

 
class A3OB_UL_keyframes(bpy.types.UIList):
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


classes = (
    A3OB_OT_keyframe_add,
    A3OB_OT_keyframe_remove,
    A3OB_OT_keyframe_clear,
    A3OB_UL_keyframes,
    A3OB_PT_object_armature,
    A3OB_PT_object_armature_frames
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: armature properties")


def unregister():    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: armature properties")