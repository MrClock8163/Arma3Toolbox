import traceback

import bpy
import bpy_extras

from ..io import import_armature as arm


class A3OB_UL_rigging_skeletons_protected(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name, icon='ARMATURE_DATA')
    
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        
        sorter = getattr(data, propname)
        flt_neworder = helper_funcs.sort_items_by_name(sorter, "name")
        
        return flt_flags, flt_neworder


class A3OB_OP_import_armature(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Arma 3 armature"""

    bl_idname = "a3ob.import_armature"
    bl_label = "Import Pivots"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    filename_ext = "*.p3d"
    
    filter_glob: bpy.props.StringProperty(
        default = "*.p3d",
        options = {'HIDDEN'}
    )
    skeleton_index: bpy.props.IntProperty(
        name="Skeleton To Reconstruct",
        default = 0
    )

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.a3ob_rigging
        return len(scene_props.skeletons) > 0

    def draw(self, context):
        pass

    def execute(self, context):
        scene_props = context.scene.a3ob_rigging
        
        try:
            skeleton = scene_props.skeletons[self.skeleton_index]
            arm.import_armature(self, skeleton)
        except Exception as ex:
            self.report({'ERROR'}, "%s (check the system console)" % str(ex))
            traceback.print_exc()

        return {'FINISHED'}


class A3OB_PT_import_armature_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Main"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_armature"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        scene_props = context.scene.a3ob_rigging

        layout.template_list("A3OB_UL_rigging_skeletons_protected", "A3OB_armature_skeletons", scene_props, "skeletons", operator, "skeleton_index", rows=3)


classes = (
    A3OB_UL_rigging_skeletons_protected,
    A3OB_OP_import_armature,
    A3OB_PT_import_armature_main
)


def menu_func_import(self, context):
    self.layout.operator(A3OB_OP_import_armature.bl_idname, text="Arma 3 armature (.p3d)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    
    print("\t" + "UI: Armature Import / Export")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    
    print("\t" + "UI: Armature Import / Export")