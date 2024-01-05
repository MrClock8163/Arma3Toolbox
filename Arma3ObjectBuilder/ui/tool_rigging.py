

import bpy

from ..utilities import generic as utils
from ..utilities import rigging as riggingutils


class A3OB_UL_rigging_skeletons(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", icon='ARMATURE_DATA', emboss=False)
    
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        
        sorter = getattr(data, propname)
        flt_neworder = helper_funcs.sort_items_by_name(sorter, "name")
        
        return flt_flags, flt_neworder


class A3OB_UL_rigging_bones(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.alignment = 'LEFT'
        layout.prop(item, "name", text="", icon='BONE_DATA', emboss=False)
        layout.label(text=":")
        layout.prop(item, "parent", text="", emboss=False)
    
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        
        sorter = getattr(data, propname)
        flt_neworder = helper_funcs.sort_items_by_name(sorter, "name")
        
        return flt_flags, flt_neworder


class A3OB_OT_skeletons_add(bpy.types.Operator):
    """Add new skeleton definition"""

    bl_idname = "a3ob.skeletons_add"
    bl_label = "Add Skeleton"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        scene_props = context.scene.a3ob_rigging
        skeleton = scene_props.skeletons.add()
        skeleton.name = "New Skeleton"
    
        return {'FINISHED'}


class A3OB_OT_skeletons_remove(bpy.types.Operator):
    """Remove skeleton definition"""

    bl_idname = "a3ob.skeletons_remove"
    bl_label = "Remove Skeleton"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.a3ob_rigging
        return scene_props.skeletons_index in range(len(scene_props.skeletons))
    
    def execute(self, context):
        scene_props = context.scene.a3ob_rigging
        scene_props.skeletons.remove(scene_props.skeletons_index)
    
        return {'FINISHED'}


class A3OB_OT_skeletons_from_armature(bpy.types.Operator):
    """Create skeleton definition from active armature object"""

    bl_idname = "a3ob.skeletons_from_armature"
    bl_label = "Skeleton From Armature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE'
    
    def execute(self, context):
        obj = context.active_object
        obj.update_from_editmode()
        scene_props = context.scene.a3ob_rigging

        bones = riggingutils.bones_from_armature(obj)
        skeleton = scene_props.skeletons.add()
        skeleton.name = obj.name
        for name, parent in bones:
            bone = skeleton.bones.add()
            bone.name = name
            bone.parent = parent
        
        return {'FINISHED'}


class A3OB_OT_skeletons_clear(bpy.types.Operator):
    """Clear skeletons list"""

    bl_idname = "a3ob.skeletons_clear"
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


class A3OB_OT_skeletons_bones_add(bpy.types.Operator):
    """Add new bone to skeleton definition"""

    bl_idname = "a3ob.skeletons_bones_add"
    bl_label = "Add Bone"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.a3ob_rigging
        return scene_props.skeletons_index in range(len(scene_props.skeletons))
    
    def execute(self, context):
        scene_props = context.scene.a3ob_rigging
        skeleton = scene_props.skeletons[scene_props.skeletons_index]
        bone = skeleton.bones.add()
        bone.name = "Bone"
    
        return {'FINISHED'}


class A3OB_OT_skeletons_bones_remove(bpy.types.Operator):
    """Remove bone from skeleton definition"""

    bl_idname = "a3ob.skeletons_bones_remove"
    bl_label = "Remove Bone"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.a3ob_rigging
        if scene_props.skeletons_index not in range(len(scene_props.skeletons)):
            return False
        
        skeleton = scene_props.skeletons[scene_props.skeletons_index]
        
        return skeleton.bones_index in range(len(skeleton.bones))
    
    def execute(self, context):
        scene_props = context.scene.a3ob_rigging
        skeleton = scene_props.skeletons[scene_props.skeletons_index]
        skeleton.bones.remove(skeleton.bones_index)
    
        return {'FINISHED'}


class A3OB_OT_skeletons_bones_clear(bpy.types.Operator):
    """Clear bones from skeleton definition"""

    bl_idname = "a3ob.skeletons_bones_clear"
    bl_label = "Clear Bones"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.a3ob_rigging
        if scene_props.skeletons_index not in range(len(scene_props.skeletons)):
            return False
        
        skeleton = scene_props.skeletons[scene_props.skeletons_index]
        
        return len(skeleton.bones) > 0
    
    def execute(self, context):
        scene_props = context.scene.a3ob_rigging
        skeleton = scene_props.skeletons[scene_props.skeletons_index]
        skeleton.bones.clear()
        skeleton.bones_index = -1
    
        return {'FINISHED'}


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

        row_skeletons = layout.row()
        col_skeletons_list = row_skeletons.column()

        col_skeletons_list.template_list("A3OB_UL_rigging_skeletons", "A3OB_rigging_skeletons", scene_props, "skeletons", scene_props, "skeletons_index", rows=4)

        col_skeletons_operators = row_skeletons.column(align=True)
        col_skeletons_operators.operator("a3ob.skeletons_add", text="", icon='ADD')
        col_skeletons_operators.operator("a3ob.skeletons_remove", text="", icon='REMOVE')
        col_skeletons_operators.separator()
        col_skeletons_operators.operator("a3ob.skeletons_from_armature", text="", icon='OUTLINER_OB_ARMATURE')
        col_skeletons_operators.separator()
        col_skeletons_operators.operator("a3ob.skeletons_clear", text="", icon='TRASH')

        row_bones = layout.row()
        col_bones_list = row_bones.column()

        if scene_props.skeletons_index in range(len(scene_props.skeletons)):
            # layout.label(text="Compiled Bones (%d):" % len(scene_props.skeletons[scene_props.skeletons_index].bones))
            col_bones_list.template_list("A3OB_UL_rigging_bones", "A3OB_rigging_bones", scene_props.skeletons[scene_props.skeletons_index], "bones", scene_props.skeletons[scene_props.skeletons_index], "bones_index", rows=4)
        else:
            # layout.label(text="Compiled Bones (0):")
            col_bones_list.template_list("A3OB_UL_rigging_bones", "A3OB_rigging_bones", scene_props, "bones", scene_props, "bones_index", rows=4)

        col_bones_operators = row_bones.column(align=True)
        col_bones_operators.operator("a3ob.skeletons_bones_add", text="", icon='ADD')
        col_bones_operators.operator("a3ob.skeletons_bones_remove", text="", icon='REMOVE')
        col_bones_operators.separator()
        col_bones_operators.operator("a3ob.skeletons_bones_clear", text="", icon='TRASH')


classes = (
    A3OB_UL_rigging_skeletons,
    A3OB_UL_rigging_bones,
    A3OB_OT_skeletons_add,
    A3OB_OT_skeletons_remove,
    A3OB_OT_skeletons_clear,
    A3OB_OT_skeletons_from_armature,
    A3OB_OT_skeletons_bones_add,
    A3OB_OT_skeletons_bones_remove,
    A3OB_OT_skeletons_bones_clear,
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