import os

import bpy

from ..utilities import generic as utils
from ..utilities import mcfg as mcfgutils


class A3OB_OT_weights_load_cfgskeletons(bpy.types.Operator):
    """Load the list of skeletons from the specified model.cfg file"""
    
    bl_idname = "a3ob.weights_load_cfgskeletons"
    bl_label = "Load/Reload CfgSkeletons"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        filepath = utils.abspath(context.scene.a3ob_weights.filepath)
        exepath = os.path.join(utils.abspath(utils.get_addon_preferences().a3_tools), "cfgconvert/cfgconvert.exe")
        return os.path.isfile(exepath) and filepath != "" and os.path.isfile(filepath) and os.path.splitext(filepath)[1].lower() == ".cfg"
        
    def execute(self, context):
        scene_props = context.scene.a3ob_weights
        exepath = os.path.join(utils.abspath(utils.get_addon_preferences().a3_tools), "cfgconvert/cfgconvert.exe")
        
        scene_props.skeletons.clear()
        
        data = mcfgutils.read_mcfg(utils.abspath(scene_props.filepath), exepath)
        
        if data:
            skeletons = mcfgutils.get_skeletons(data)
            for skelly in skeletons:
                new_skelly = scene_props.skeletons.add()
                new_skelly.name = skelly.name
                
                cfgbones = mcfgutils.get_bones_compiled(data, skelly.name)
                for bone in cfgbones:
                    new_bone = new_skelly.bones.add()
                    new_bone.name = bone.name
                    new_bone.parent = bone.parent
        
        return {'FINISHED'}


class A3OB_OT_weights_select_unnormalized(bpy.types.Operator):
    """Select vertices with not normalized deform weights"""
    
    bl_idname = "a3ob.weights_select_unnormalized"
    bl_label = "Select Unnormalized"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT' and scene_props.skeletons_index in range(len(scene_props.skeletons))
        
    def execute(self, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        cfgbones = scene_props.skeletons[scene_props.skeletons_index].bones
        
        bone_indices = mcfgutils.get_bone_group_indices(obj, cfgbones)
        mcfgutils.select_vertices_unnormalized(obj, bone_indices)
        
        return {'FINISHED'}


class A3OB_OT_weights_select_overdetermined(bpy.types.Operator):
    """Select vertices with more than 3 deform bones assigned"""
    
    bl_idname = "a3ob.weights_select_overdetermined"
    bl_label = "Select Overdetermined"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT' and scene_props.skeletons_index in range(len(scene_props.skeletons))
        
    def execute(self, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        cfgbones = scene_props.skeletons[scene_props.skeletons_index].bones
        
        bone_indices = mcfgutils.get_bone_group_indices(obj, cfgbones)
        mcfgutils.select_vertices_overdetermined(obj, bone_indices)
        
        return {'FINISHED'}


class A3OB_OT_weights_normalize(bpy.types.Operator):
    """Normalize weights to deform bones"""
    
    bl_idname = "a3ob.weights_normalize"
    bl_label = "Normalize Weights"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT' and scene_props.skeletons_index in range(len(scene_props.skeletons))
        
    def execute(self, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        cfgbones = scene_props.skeletons[scene_props.skeletons_index].bones
        
        bone_indices = mcfgutils.get_bone_group_indices(obj, cfgbones)
        normalized = mcfgutils.normalize_weights(obj, bone_indices)
        
        self.report({'INFO'}, "Normalized weights on %d vertices" % normalized)
        
        return {'FINISHED'}


class A3OB_OT_weights_prune_overdetermined(bpy.types.Operator):
    """Prune excess deform bones from vertices with more than 4 assigned bones"""
    
    bl_idname = "a3ob.weights_prune_overdetermined"
    bl_label = "Prune Overdetermined"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT' and scene_props.skeletons_index in range(len(scene_props.skeletons))
        
    def execute(self, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        cfgbones = scene_props.skeletons[scene_props.skeletons_index].bones
        
        bone_indices = mcfgutils.get_bone_group_indices(obj, cfgbones)
        pruned = mcfgutils.prune_overdetermined(obj, bone_indices)
        
        self.report({'INFO'}, "Pruned excess bones from %d vertices" % pruned)
        
        return {'FINISHED'}


class A3OB_OT_weights_prune(bpy.types.Operator):
    """Prune vertex groups below weight threshold"""
    
    bl_idname = "a3ob.weights_prune"
    bl_label = "Prune Selections"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT'
        
    def execute(self, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        pruned = mcfgutils.prune_weights(obj, scene_props.prune_threshold)
        
        self.report({'INFO'}, "Pruned selection(s) from %d vertices" % pruned)
        
        return {'FINISHED'}


class A3OB_OT_weights_cleanup(bpy.types.Operator):
    """General weight painting cleanup"""
    
    bl_idname = "a3ob.weights_cleanup"
    bl_label = "General Cleanup"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT' and scene_props.skeletons_index in range(len(scene_props.skeletons))
        
    def execute(self, context):
        obj = context.active_object
        scene_props = context.scene.a3ob_weights
        cfgbones = scene_props.skeletons[scene_props.skeletons_index].bones
        
        bone_indices = mcfgutils.get_bone_group_indices(obj, cfgbones)
        cleaned = mcfgutils.cleanup(obj, bone_indices, scene_props.prune_threshold)
        
        self.report({'INFO'}, "Cleaned up weight painting on %d vertices" % cleaned)
        
        return {'FINISHED'}


class A3OB_UL_cfgskeletons(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)
    
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        
        sorter = getattr(data, propname)
        flt_neworder = helper_funcs.sort_items_by_name(sorter, "name")
        
        return flt_flags, flt_neworder


class A3OB_UL_cfgbones(bpy.types.UIList):
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


class A3OB_PT_weights(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Weight Painting"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP', emboss=False).url = "https://mrcmodding.gitbook.io/arma-3-object-builder/tools/weight-painting"
        
    def draw(self, context):
        scene_props = context.scene.a3ob_weights
        layout = self.layout
        
        layout.prop(scene_props, "filepath", text="Config")
        layout.operator("a3ob.weights_load_cfgskeletons", icon_value=utils.get_icon("op_refresh"))
        layout.label(text="Skeletons (%d):" % len(scene_props.skeletons))
        layout.template_list("A3OB_UL_cfgskeletons", "A3OB_cfgskeletons", scene_props, "skeletons", scene_props, "skeletons_index", rows=3)

        if scene_props.skeletons_index in range(len(scene_props.skeletons)):
            layout.label(text="Compiled Bones (%d):" % len(scene_props.skeletons[scene_props.skeletons_index].bones))
            layout.template_list("A3OB_UL_cfgbones", "A3OB_cfgbones", scene_props.skeletons[scene_props.skeletons_index], "bones", scene_props.skeletons[scene_props.skeletons_index], "bones_index", rows=3)
        else:
            layout.label(text="Compiled Bones (0):")
            layout.template_list("A3OB_UL_cfgbones", "A3OB_cfgbones", scene_props, "bones", scene_props, "bones_index", rows=2)
        
        col_select = layout.column(align=True)
        col_select.operator("a3ob.weights_select_overdetermined", icon_value=utils.get_icon("op_weights_select_overdetermined"))
        col_select.operator("a3ob.weights_select_unnormalized", icon_value=utils.get_icon("op_weights_select_unnormalized"))
        
        col_edit = layout.column(align=True)
        col_edit.operator("a3ob.weights_prune_overdetermined", icon_value=utils.get_icon("op_weights_prune_overdetermined"))
        col_edit.operator("a3ob.weights_normalize", icon_value=utils.get_icon("op_weights_normalize"))
        col_edit.operator("a3ob.weights_prune", icon_value=utils.get_icon("op_weights_prune"))
        col_edit.prop(scene_props, "prune_threshold")
        
        layout.operator("a3ob.weights_cleanup", icon_value=utils.get_icon("op_weights_cleanup"))

classes = (
    A3OB_OT_weights_load_cfgskeletons,
    A3OB_OT_weights_select_unnormalized,
    A3OB_OT_weights_select_overdetermined,
    A3OB_OT_weights_normalize,
    A3OB_OT_weights_prune_overdetermined,
    A3OB_OT_weights_prune,
    A3OB_OT_weights_cleanup,
    A3OB_UL_cfgskeletons,
    A3OB_UL_cfgbones,
    A3OB_PT_weights
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: Weight Painting")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: Weight Painting")