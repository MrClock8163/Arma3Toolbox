import bpy

from ..utilities import atbx_conversion as convertutils


class A3OB_OT_convert_to_a3ob(bpy.types.Operator):
    """Convert setup from ArmaToolbox to Arma 3 Object Builder"""
    
    bl_idname = "a3ob.convert_to_a3ob"
    bl_label = "Convert Setup"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        wm_props = context.window_manager.a3ob_conversion
        object_pool = []
        if wm_props.use_selection:
            object_pool = context.selected_objects
        else:
            object_pool = context.scene.objects
            
        objects = [obj for obj in object_pool if obj.type in wm_props.types and obj.armaObjProps.isArmaObject]
        for obj in objects:
            if obj.mode != 'OBJECT':
                self.report({'ERROR'}, "All objects must be in object mode in order to perform the conversion")
                return {'FINISHED'}
        
        bpy.ops.object.select_all(action='DESELECT')
        
        convertutils.convert_objects(objects, wm_props.cleanup)
        
        return {'FINISHED'}


class A3OB_PT_conversion(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Conversion"
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw_header(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3Toolbox/wiki/Tool:-Conversion"
        
    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.a3ob_conversion
        
        col = layout.column(heading="Limit To", align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(wm_props, "use_selection")
        col.prop(wm_props, "types", text=" ")
        
        layout.prop(wm_props, "cleanup")
        layout.operator("a3ob.convert_to_a3ob", icon='FILE_REFRESH')


classes = (
    A3OB_OT_convert_to_a3ob,
    A3OB_PT_conversion
)


def register():
    from bpy.utils import register_class
    
    for cls in classes:
        register_class(cls)
    
    print("\t" + "UI: Conversion")


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    
    print("\t" + "UI: Conversion")