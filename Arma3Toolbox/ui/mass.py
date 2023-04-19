import bpy
from ..utilities import properties as proputils

class A3OB_OT_vertex_mass_set(bpy.types.Operator):
    '''Set same mass on all selected vertices'''
    
    bl_idname = "a3ob.vertex_mass_set"
    bl_label = "Set Mass On Each"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls,context):
        return proputils.canEditMass(context)
        
    def execute(self,context):
        activeObj = context.active_object
        
        proputils.selectionMassSetEach(activeObj,activeObj.a3ob_selectionMassTarget)
        
        return {'FINISHED'}

class A3OB_OT_vertex_mass_distribute(bpy.types.Operator):
    '''Distribute mass equally to selected vertices'''
    
    bl_idname = "a3ob.vertex_mass_distribute"
    bl_label = "Distribute Mass"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls,context):
        return proputils.canEditMass(context)
        
    def execute(self,context):
        activeObj = context.active_object
        
        proputils.selectionMassDistribute(activeObj,activeObj.a3ob_selectionMassTarget)
        return {'FINISHED'}

class A3OB_PT_vertex_mass(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Vertex Mass Editing"
    
    @classmethod
    def poll(cls,context):
        return proputils.canEditMass(context)
        
    def draw_header(self,context):
        self.layout.prop(context.window_manager,"a3ob_enableVertexMass",text="")
        
    def draw(self,context):
        layout = self.layout
        
        if not context.window_manager.a3ob_enableVertexMass:
            layout.label(text="The tools are currently disabled")
            layout.enabled = False
            return 
        
        activeObj = context.active_object
        
        layout.prop(activeObj,"a3ob_selectionMass")
        layout.separator()
        layout.label(text="Overwrite Mass:")
        col = layout.column(align=True)
        col.prop(activeObj,"a3ob_selectionMassTarget")
        col.operator("a3ob.vertex_mass_set")
        col.operator("a3ob.vertex_mass_distribute")

classes = (
    A3OB_PT_vertex_mass,
    A3OB_OT_vertex_mass_set,
    A3OB_OT_vertex_mass_distribute
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)