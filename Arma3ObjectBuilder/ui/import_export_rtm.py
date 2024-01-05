import traceback
import os

import bpy
import bpy_extras

from ..io import export_rtm, import_rtm
from ..utilities import generic as utils


class A3OB_OP_export_rtm(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export keyframes to Arma 3 RTM"""
    
    bl_idname = "a3ob.export_rtm"
    bl_label = "Export RTM"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    filename_ext = ".rtm"
    
    filter_glob: bpy.props.StringProperty(
        default = "*.rtm",
        options = {'HIDDEN'}
    )
    static_pose: bpy.props.BoolProperty(
        name = "Static Pose",
        description = "Export current frame as static pose"
    )
    clamp: bpy.props.BoolProperty(
        name = "Clamp To Range",
        description = "Do not export frames outside of the animation start-end range",
        default = True
    )
    frame_start: bpy.props.IntProperty(
        name = "Start",
        description = "Starting frame of animation",
        min = 0
    )
    frame_end: bpy.props.IntProperty(
        name = "End",
        description = "Ending frame of animation",
        default = 100,
        min = 0
    )
    force_lowercase: bpy.props.BoolProperty(
        name = "Force Lowercase",
        description = "Export all bone names as lowercase",
        default = True
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and len(obj.pose.bones) > 0
        
    def draw(self, context):
        pass
        
    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        
        return super().invoke(context, event)
        
    def execute(self, context):
        obj = context.active_object
        temppath = self.filepath + ".temp"
        success = False
                
        with open(temppath, "wb") as file:
            try:
                static, frame_count = export_rtm.write_file(self, context, file, obj)
            
                if not self.static_pose and static:
                    self.report({'INFO'}, "No frames were added for export, exported as static pose")
                else:
                    self.report({'INFO'}, "Exported %d frame(s)" % frame_count)
                
                success = True
                    
            except Exception as ex:
                self.report({'ERROR'}, "%s (check the system console)" % str(ex))
                traceback.print_exc()
        
        if success:
            if os.path.isfile(self.filepath):
                os.remove(self.filepath)
                
            os.rename(temppath, os.path.splitext(temppath)[0])
        elif not success and not utils.get_addon_preferences().preserve_faulty_output:
            os.remove(temppath)
            
        return {'FINISHED'}
        

class A3OB_PT_export_rtm_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Main"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_export_rtm"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator, "static_pose")
        layout.prop(operator, "force_lowercase")


class A3OB_PT_export_rtm_frames(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Frames"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_export_rtm"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.enabled = not operator.static_pose
        layout.prop(operator, "clamp")
        col = layout.column(align=True)
        col.prop(operator, "frame_start")
        col.prop(operator, "frame_end")
        col.enabled = operator.clamp


class A3OB_OP_import_rtm(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import action from Arma 3 RTM"""

    bl_idname = "a3ob.import_rtm"
    bl_label = "Import RTM"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    filename_ext = '*.rtm'

    filter_glob: bpy.props.StringProperty(
        default = "*.rtm",
        options = {'HIDDEN'}
    )
    frame_start: bpy.props.IntProperty(
        name = "Start",
        description = "Starting frame of animation",
        min = 0
    )
    frame_end: bpy.props.IntProperty(
        name = "End",
        description = "Ending frame of animation",
        default = 100,
        min = 0
    )
    round_frames: bpy.props.BoolProperty(
        name = "Round Frames",
        description = "Round fractional frames to the nearest whole number",
        default = True
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and len(obj.pose.bones) > 0
    
    def draw(self, context):
        pass

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        
        return super().invoke(context, event)
    
    def execute(self, context):
        obj = context.active_object

        count_frames = 0
        try:
            count_frames = import_rtm.import_file(self, obj)
        except Exception as ex:
            self.report({'ERROR'}, "%s (check the system console)" % str(ex))
            traceback.print_exc()
        
        if count_frames > 0:
            self.report({'INFO'}, "Successfully imported %d frame(s)" % count_frames)

        return {'FINISHED'}


class A3OB_PT_import_rtm_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Main"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_rtm"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "frame_start")
        layout.prop(operator, "frame_end")
        layout.prop(operator, "round_frames")


classes = (
    A3OB_OP_export_rtm,
    A3OB_PT_export_rtm_main,
    A3OB_PT_export_rtm_frames,
    A3OB_OP_import_rtm,
    A3OB_PT_import_rtm_main
)


def menu_func_export(self, context):
    self.layout.operator(A3OB_OP_export_rtm.bl_idname, text="Arma 3 animation (.rtm)")


def menu_func_import(self, context):
    self.layout.operator(A3OB_OP_import_rtm.bl_idname, text="Arma 3 animation (.rtm)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    
    print("\t" + "UI: RTM Import / Export")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
    print("\t" + "UI: RTM Import / Export")