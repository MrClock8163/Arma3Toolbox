import bpy

from ..utilities import properties as proputils


class A3OB_OT_vertex_mass_set(bpy.types.Operator):
    """Set same mass on all selected vertices"""
    
    bl_idname = "a3ob.vertex_mass_set"
    bl_label = "Set Mass On Each"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return proputils.can_edit_mass(context) and context.window_manager.a3ob_mass_editor.source == 'MASS'
        
    def execute(self, context):
        obj = context.active_object
        wm = context.window_manager
        proputils.set_selection_mass_each(obj, wm.a3ob_mass_editor.mass)
        return {'FINISHED'}


class A3OB_OT_vertex_mass_distribute(bpy.types.Operator):
    """Distribute mass equally to selected vertices"""
    
    bl_idname = "a3ob.vertex_mass_distribute"
    bl_label = "Distribute Mass"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return proputils.can_edit_mass(context) and context.window_manager.a3ob_mass_editor.source == 'MASS'
        
    def execute(self, context):
        obj = context.active_object
        wm = context.window_manager
        proputils.set_selection_mass_distribute(obj, wm.a3ob_mass_editor.mass)
        return {'FINISHED'}


class A3OB_OT_vertex_mass_set_density(bpy.types.Operator):
    """Calculate mass distribution from volumetric density (operates on the entire mesh)"""
    
    bl_idname = "a3ob.vertex_mass_set_density"
    bl_label = "Mass From Density"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return proputils.can_edit_mass(context) and context.window_manager.a3ob_mass_editor.source == 'DENSITY'
        
    def execute(self, context):
        obj = context.active_object
        wm = context.window_manager
        contiguous = proputils.set_selection_mass_density(obj, wm.a3ob_mass_editor.density)
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
        return proputils.can_edit_mass(context)
        
    def execute(self, context):
        obj = context.active_object
        proputils.clear_selection_masses(obj)
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
        row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3ObjectBuilder/wiki/Tool:-Vertex-Mass-Editing"
        row.separator()
        row.prop(context.window_manager.a3ob_mass_editor, "enabled", text="")
        
    def draw(self, context):
        layout = self.layout
        if not proputils.can_edit_mass(context):
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
            col.operator("a3ob.vertex_mass_set")
            col.operator("a3ob.vertex_mass_distribute")
        elif wm_props.source == 'DENSITY':
            col.prop(wm_props, "density")
            col.operator("a3ob.vertex_mass_set_density")
        
        col.separator()
        col.operator("a3ob.vertex_mass_clear")


classes = (
    A3OB_PT_vertex_mass,
    A3OB_OT_vertex_mass_set,
    A3OB_OT_vertex_mass_distribute,
    A3OB_OT_vertex_mass_set_density,
    A3OB_OT_vertex_mass_clear
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: Vertex Mass Editing")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: Vertex Mass Editing")