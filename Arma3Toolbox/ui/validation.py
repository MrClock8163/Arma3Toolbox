import bpy

from ..utilities import lod as lodutils


class A3OB_OT_validate_lod(bpy.types.Operator):
    """Validate the selected object for the requirements of the set LOD type"""
    
    bl_idname = "a3ob.validate_for_lod"
    bl_label = "Validate LOD"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        wm_props = context.window_manager.a3ob_validation
        obj = context.active_object
        return obj and obj.type == 'MESH' and (not wm_props.detect or obj.a3ob_properties_object.is_a3_lod)
        
    def execute(self, context):
        wm_props = context.window_manager.a3ob_validation
        obj = context.active_object
        
        if wm_props.detect:
            try:
                wm_props.lod = obj.a3ob_properties_object.lod
            except:
                self.report({'INFO'}, "No validation rules for detected LOD type")
                return {'FINISHED'}
        
        valid = lodutils.validate_lod(obj, wm_props)
        if valid:
            self.report({'INFO'}, "Validation succeeded")
        else:
            self.report({'ERROR'}, "Validation failed (see the System Console for more info)")

        return {'FINISHED'}


class A3OB_PT_validation(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Validation"
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw_header(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3ObjectBuilder/wiki/Tool:-Validation"
        
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        wm_props = wm.a3ob_validation
        
        layout.prop(wm_props, "detect")
        row_type = layout.row()
        row_type.prop(wm_props, "lod")
        if wm_props.detect:
            row_type.enabled = False
        layout.prop(wm_props, "warning_errors")
            
        layout.separator()
        layout.operator("a3ob.validate_for_lod", text="Validate", icon='CHECKMARK')
        

classes = (
    A3OB_OT_validate_lod,
    A3OB_PT_validation,
)


def register():
    from bpy.utils import register_class
    
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)