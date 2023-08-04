import bpy

from ..utilities import generic as utils
from ..utilities import masses as massutils


class A3OB_OT_vertex_mass_set(bpy.types.Operator):
    """Set same mass on all selected vertices"""
    
    bl_idname = "a3ob.vertex_mass_set"
    bl_label = "Set Mass On Each"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return massutils.can_edit_mass(context) and context.window_manager.a3ob_mass_editor.source == 'MASS'
        
    def execute(self, context):
        obj = context.active_object
        wm = context.window_manager
        massutils.set_selection_mass_each(obj, wm.a3ob_mass_editor.mass)
        return {'FINISHED'}


class A3OB_OT_vertex_mass_distribute(bpy.types.Operator):
    """Distribute mass equally to selected vertices"""
    
    bl_idname = "a3ob.vertex_mass_distribute"
    bl_label = "Distribute Mass"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return massutils.can_edit_mass(context) and context.window_manager.a3ob_mass_editor.source == 'MASS'
        
    def execute(self, context):
        obj = context.active_object
        wm = context.window_manager
        massutils.set_selection_mass_distribute(obj, wm.a3ob_mass_editor.mass)
        return {'FINISHED'}


class A3OB_OT_vertex_mass_set_density(bpy.types.Operator):
    """Calculate mass distribution from volumetric density (operates on the entire mesh)"""
    
    bl_idname = "a3ob.vertex_mass_set_density"
    bl_label = "Mass From Density"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return massutils.can_edit_mass(context) and context.window_manager.a3ob_mass_editor.source == 'DENSITY'
        
    def execute(self, context):
        obj = context.active_object
        wm = context.window_manager
        contiguous = massutils.set_selection_mass_density(obj, wm.a3ob_mass_editor.density)
        if not contiguous:
            self.report({'WARNING'}, "Mesh is not contiguous, volume calculation gives unreliable result")
        
        return {'FINISHED'}


class A3OB_OT_vertex_mass_clear(bpy.types.Operator):
    """Remove vertex mass data layer"""
    
    bl_idname = "a3ob.vertex_mass_clear"
    bl_label = "Clear Masses"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls,context):
        return massutils.can_edit_mass(context)
        
    def execute(self, context):
        obj = context.active_object
        massutils.clear_selection_masses(obj)
        return {'FINISHED'}


class A3OB_OT_vertex_mass_visualize(bpy.types.Operator):
    """Generate vertex color layer to visualize mass distribution"""
    
    bl_idname = "a3ob.vertex_mass_visualize"
    bl_label = "Visualize"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return massutils.can_edit_mass(context)
    
    def execute(self, context):
        obj = context.active_object
        wm_props = context.window_manager.a3ob_mass_editor
        
        massutils.visualize_mass(obj, wm_props)
        
        return {'FINISHED'}


class A3OB_OT_vertex_mass_stats_refresh(bpy.types.Operator):
    """Refresh vertex mass stats"""
    
    bl_idname = "a3ob.vertex_mass_stats_refresh"
    bl_label = "Refresh Stats"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return massutils.can_edit_mass(context)
    
    def execute(self, context):
        obj = context.active_object
        wm_props = context.window_manager.a3ob_mass_editor
        
        massutils.refresh_stats(obj, wm_props)
        
        return {'FINISHED'}


class A3OB_PT_vertex_mass(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Vertex Mass Editing"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw_header(self, context):
        row = self.layout.row(align=True)
        if utils.get_addon_preferences().show_info_links:
            row.operator("wm.url_open", text="", icon='HELP').url = "https://mrcmodding.gitbook.io/arma-3-object-builder/tools/vertex-mass-editing"
            row.separator()
            
        row.prop(context.window_manager.a3ob_mass_editor, "enabled", text="")
        
    def draw(self, context):
        layout = self.layout
        if not massutils.can_edit_mass(context):
            layout.label(text="Only available in Edit Mode")
            layout.enabled = False
            return 
        
        wm_props = context.window_manager.a3ob_mass_editor
        
        if not wm_props.enabled:
            layout.label(text="The tools are currently disabled")
            layout.enabled = False
            return 
        
        obj = context.active_object
        
        layout.prop(obj, "a3ob_selection_mass")
        layout.separator()
        layout.label(text="Overwrite Mass:")
        layout.prop(wm_props, "source", expand=True)
        
        col = layout.column(align=True)        
        if wm_props.source == 'MASS':
            col.prop(wm_props, "mass")
            col.operator("a3ob.vertex_mass_set", icon_value=utils.get_icon("op_mass_set"))
            col.operator("a3ob.vertex_mass_distribute", icon_value=utils.get_icon("op_mass_distribute"))
        elif wm_props.source == 'DENSITY':
            col.prop(wm_props, "density")
            col.operator("a3ob.vertex_mass_set_density", icon_value=utils.get_icon("op_mass_set_density"))
        
        col.separator()
        col.operator("a3ob.vertex_mass_clear", icon_value=utils.get_icon("op_mass_clear"))


class A3OB_PT_vertex_mass_analyze(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Analyze"
    bl_parent_id = "A3OB_PT_vertex_mass"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return massutils.can_edit_mass(context)
    
    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.a3ob_mass_editor
        
        layout.label(text="Empty Color:")
        layout.prop(wm_props, "color_0", text="")
        
        layout.label(text="Color Ramp:")
        row_colors = layout.row(align=True)
        row_colors.prop(wm_props, "color_1", text="")
        row_colors.prop(wm_props, "color_2", text="")
        row_colors.prop(wm_props, "color_3", text="")
        row_colors.prop(wm_props, "color_4", text="")
        row_colors.prop(wm_props, "color_5", text="")
        
        layout.prop(wm_props, "color_layer_name", text="Layer")
        row_method = layout.row(align=True)
        row_method.prop(wm_props, "method", text="Method", expand=True)
        
        layout.operator("a3ob.vertex_mass_visualize", icon_value=utils.get_icon("op_visualize"))
        
        layout.label(text="Stats:")
        box_stats = layout.box()
        box_stats.enabled = False
        box_stats.prop(wm_props.stats, "mass_min", text="Min")
        box_stats.prop(wm_props.stats, "mass_avg", text="Average")
        box_stats.prop(wm_props.stats, "mass_max", text="Max")
        box_stats.prop(wm_props.stats, "count_loose")
        
        layout.operator("a3ob.vertex_mass_stats_refresh", text="Refresh", icon_value=utils.get_icon("op_refresh"))
        


classes = (
    A3OB_PT_vertex_mass,
    A3OB_PT_vertex_mass_analyze,
    A3OB_OT_vertex_mass_set,
    A3OB_OT_vertex_mass_distribute,
    A3OB_OT_vertex_mass_set_density,
    A3OB_OT_vertex_mass_clear,
    A3OB_OT_vertex_mass_visualize,
    A3OB_OT_vertex_mass_stats_refresh
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: Vertex Mass Editing")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: Vertex Mass Editing")