import os

import bpy

from ..io import import_mcfg as mcfg
from ..utilities import generic as utils
from ..utilities import mcfg as mcfgutils


class A3OB_UL_rigging_skeletons(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)
    
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        
        sorter = getattr(data, propname)
        flt_neworder = helper_funcs.sort_items_by_name(sorter, "name")
        
        return flt_flags, flt_neworder


class A3OB_OT_clear_skeletons(bpy.types.Operator):
    """Clear skeletons list"""

    bl_idname = "a3ob.clear_skeletons"
    bl_label = "Clear Skeletons"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.a3ob_rigging
        return len(scene_props.skeletons) > 0
    
    def execute(self, context):
        scene_props = context.scene.a3ob_rigging
        scene_props.skeletons.clear()
        scene_props.skeletons_index = -1

        return {'FINISHED'}


class A3OB_UL_rigging_bones(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item.parent != "":
            layout.label(text="%s: %s" % (item.name, item.parent))
        else:
            layout.label(text=item.name)
    
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        
        sorter = getattr(data, propname)
        flt_neworder = helper_funcs.sort_items_by_name(sorter, "name")
        
        return flt_flags, flt_neworder


class A3OB_PT_rigging(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Rigging"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = "https://mrcmodding.gitbook.io/arma-3-object-builder/tools/rigging"
    
    def draw(self, context):
        pass


class A3OB_PT_rigging_skeletons(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Skeletons"
    bl_parent_id = "A3OB_PT_rigging"
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.a3ob_rigging

        layout.operator("a3ob.clear_skeletons", icon='TRASH')

        layout.template_list("A3OB_UL_rigging_skeletons", "A3OB_rigging_skeletons", scene_props, "skeletons", scene_props, "skeletons_index", rows=3)

        if scene_props.skeletons_index in range(len(scene_props.skeletons)):
            layout.label(text="Compiled Bones (%d):" % len(scene_props.skeletons[scene_props.skeletons_index].bones))
            layout.template_list("A3OB_UL_rigging_bones", "A3OB_rigging_bones", scene_props.skeletons[scene_props.skeletons_index], "bones", scene_props.skeletons[scene_props.skeletons_index], "bones_index", rows=3)
        else:
            layout.label(text="Compiled Bones (0):")
            layout.template_list("A3OB_UL_rigging_bones", "A3OB_rigging_bones", scene_props, "bones", scene_props, "bones_index", rows=2)


classes = (
    A3OB_UL_rigging_skeletons,
    A3OB_UL_rigging_bones,
    A3OB_OT_clear_skeletons,
    A3OB_PT_rigging,
    A3OB_PT_rigging_skeletons
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: Rigging")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: Rigging")