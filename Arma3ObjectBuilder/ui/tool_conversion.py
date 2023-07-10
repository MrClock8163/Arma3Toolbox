import traceback

import bpy

from ..utilities import generic as utils
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
            
        objects_LOD = [obj for obj in object_pool if obj.visible_get() and obj.type == 'MESH' and 'MESH' in wm_props.types and obj.armaObjProps.isArmaObject]
        objects_DTM = [obj for obj in object_pool if obj.visible_get() and obj.type == 'MESH' and 'DTM' in wm_props.types and obj.armaHFProps.isHeightfield]
        objects_armature = [obj for obj in object_pool if obj.visible_get() and obj.type == 'ARMATURE' and 'ARMATURE' in wm_props.types and obj.armaObjProps.isArmaObject]
        objects = [objects_LOD, objects_DTM, objects_armature]
        
        for category in objects:
            for obj in category:
                if obj.mode != 'OBJECT':
                    self.report({'ERROR'}, "All objects must be in object mode in order to perform the conversion")
                    return {'FINISHED'}
        
        try:
            bpy.ops.object.select_all(action='DESELECT')
            convertutils.convert_objects(objects, wm_props.dynamic_naming, wm_props.cleanup)
            self.report({'INFO'}, "Finished setup conversion (check the logs in the system console)")
        except Exception as ex:
            self.report({'ERROR'}, "%s (check the system console)" % str(ex))
            traceback.print_exc()
        
        return {'FINISHED'}


class A3OB_PT_conversion(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Conversion"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw_header(self, context):
        if not utils.get_addon_preferences(context).show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://mrcmodding.gitbook.io/arma-3-object-builder/tools/conversion"
        
    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.a3ob_conversion
        
        col = layout.column(heading="Limit To", align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(wm_props, "use_selection")
        col.prop(wm_props, "types", text=" ")
        
        layout.prop(wm_props, "dynamic_naming")
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