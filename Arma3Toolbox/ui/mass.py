import bpy

from ..utilities import properties as proputils

class A3OB_OT_vertex_mass_set(bpy.types.Operator):
    '''Set same mass on all selected vertices'''
    
    bl_idname = "a3ob.vertex_mass_set"
    bl_label = "Set Mass On Each"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return proputils.can_edit_mass(context)
        
    def execute(self, context):
        obj = context.active_object
        
        proputils.set_selection_mass_each(obj, obj.a3ob_selection_mass_target)
        
        return {'FINISHED'}

class A3OB_OT_vertex_mass_distribute(bpy.types.Operator):
    '''Distribute mass equally to selected vertices'''
    
    bl_idname = "a3ob.vertex_mass_distribute"
    bl_label = "Distribute Mass"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return proputils.can_edit_mass(context)
        
    def execute(self, context):
        obj = context.active_object
        
        proputils.set_selection_mass_distribute(obj, obj.a3ob_selection_mass_target)
        return {'FINISHED'}
        
class A3OB_OT_vertex_mass_clear(bpy.types.Operator):
    '''Remove vertex mass data layer'''
    
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
    
    @classmethod
    def poll(cls, context):
        return proputils.can_edit_mass(context)
        
    def draw_header(self, context):
        row = self.layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3Toolbox/wiki/Tool:-Vertex-mass-editing"
        row.separator()
        row.prop(context.window_manager, "a3ob_vertex_mass_enabled", text="")
        
    def draw(self, context):
        layout = self.layout
        
        if not context.window_manager.a3ob_vertex_mass_enabled:
            layout.label(text="The tools are currently disabled")
            layout.enabled = False
            return 
        
        obj = context.active_object
        
        layout.prop(obj, "a3ob_selection_mass")
        layout.separator()
        layout.label(text="Overwrite Mass:")
        col = layout.column(align=True)
        col.prop(obj, "a3ob_selection_mass_target")
        col.operator("a3ob.vertex_mass_set")
        col.operator("a3ob.vertex_mass_distribute")
        col.separator()
        col.operator("a3ob.vertex_mass_clear")

classes = (
    A3OB_PT_vertex_mass,
    A3OB_OT_vertex_mass_set,
    A3OB_OT_vertex_mass_distribute,
    A3OB_OT_vertex_mass_clear
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)