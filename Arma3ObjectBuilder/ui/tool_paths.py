import bpy

from ..utilities import generic as utils
from ..utilities import renaming as renameutils


class A3OB_OT_rename_list_refresh(bpy.types.Operator):
    """Refresh list of paths for bulk renaming"""
    
    bl_idname = "a3ob.rename_list_refresh"
    bl_label = "Refresh List"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        renameutils.refresh_rename_list(context)
        
        return {'FINISHED'}


class A3OB_OT_rename_path_item(bpy.types.Operator):
    """Replace selected file path"""
    
    bl_idname = "a3ob.rename_path_item"
    bl_label = "Replace Path"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        wm_props = context.window_manager.a3ob_renaming
        return wm_props.path_list_index in range(len(wm_props.path_list))
        
    def execute(self, context):
        renameutils.rename_path(context)
        return {'FINISHED'}


class A3OB_OT_rename_path_root(bpy.types.Operator):
    """Replace file roots"""
    
    bl_idname = "a3ob.rename_path_root"
    bl_label = "Replace Root"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        wm_props = context.window_manager.a3ob_renaming
        return wm_props.root_old.strip() != ""
        
    def execute(self, context):
        renameutils.rename_root(context)
        return {'FINISHED'}


class A3OB_OT_rename_vertex_groups(bpy.types.Operator):
    """Rename vertex groups of selected objects"""
    
    bl_idname = "a3ob.rename_vertex_groups"
    bl_label = "Rename Groups"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        wm_props = context.window_manager.a3ob_renaming
        return wm_props.vgroup_old.strip() != "" and wm_props.vgroup_new.strip() != "" and len(context.selected_objects) > 0
        
    def execute(self, context):
        renameutils.rename_vertex_groups(context)
        return {'FINISHED'}


class A3OB_PT_renaming(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Renaming"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        if not utils.get_addon_preferences(context).show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3ObjectBuilder/wiki/Tool:-Renaming"

    def draw(self, context):
        pass


class A3OB_UL_renamable_paths(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.path)


class A3OB_PT_renaming_paths_bulk(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Bulk Replace"
    bl_parent_id = "A3OB_PT_renaming"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.a3ob_renaming
        
        col_list = layout.column(align=True)
        
        col_list.template_list("A3OB_UL_renamable_paths", "A3OB_bulk_rename", wm_props, "path_list", wm_props, "path_list_index")
        row_filter = col_list.row(align=True)
        row_filter.operator("a3ob.rename_list_refresh", text="", icon='FILE_REFRESH')
        row_filter.prop(wm_props, "source_filter")
        
        if wm_props.path_list_index in range(len(wm_props.path_list)):
            col_edit = layout.column(align=True)
            col_edit.prop(wm_props.path_list[wm_props.path_list_index], "path", text="")
            col_edit.prop(wm_props, "new_path", text="")
            col_edit.separator()
            col_edit.operator("a3ob.rename_path_item")


class A3OB_PT_renaming_paths_root(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Root Replace"
    bl_parent_id = "A3OB_PT_renaming"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.a3ob_renaming
        
        col_edit = layout.column(align=True)
        col_edit.prop(wm_props, "root_old")
        col_edit.prop(wm_props, "root_new")
        
        row_filter = layout.row(align=True)
        row_filter.prop(wm_props, "source_filter")
        
        layout.operator("a3ob.rename_path_root")


class A3OB_PT_renaming_vertex_groups(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Vertex Groups"
    bl_parent_id = "A3OB_PT_renaming"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.a3ob_renaming
        
        col_edit = layout.column(align=True)
        col_edit.prop(wm_props, "vgroup_old")
        col_edit.prop(wm_props, "vgroup_new")
        layout.prop(wm_props, "vgroup_match_whole")
        layout.operator("a3ob.rename_vertex_groups")


classes = (
    A3OB_OT_rename_list_refresh,
    A3OB_OT_rename_path_item,
    A3OB_OT_rename_path_root,
    A3OB_OT_rename_vertex_groups,
    A3OB_PT_renaming,
    A3OB_UL_renamable_paths,
    A3OB_PT_renaming_paths_bulk,
    A3OB_PT_renaming_paths_root,
    A3OB_PT_renaming_vertex_groups
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: Renaming")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: Renaming")