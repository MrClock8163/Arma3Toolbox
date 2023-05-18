import bpy
from ..utilities import clouds as cloudutils

class A3OB_OT_hitpoints_generate(bpy.types.Operator):
    '''Create hit points cloud from shape'''
    
    bl_idname = "a3ob.hitpoints_generate"
    bl_label = "Generate Hit Point Cloud"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls,context):
        OBprops = context.window_manager.a3ob_hitpoint_generator
        return OBprops.source and (OBprops.source != OBprops.target) and OBprops.source.type == 'MESH' and (not OBprops.target or OBprops.target.type == 'MESH')
        
    def execute(self,context):        
        cloudutils.generate_hitpoints(self,context)
        return {'FINISHED'}
        
class A3OB_PT_hitpoints(bpy.types.Panel):   
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Hit Point Cloud"
    
    @classmethod
    def poll(cls,context):
        return True
        
    def draw_header(self,context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3Toolbox/wiki/Tool:-Hit-point-cloud-generator"
        
    def draw(self,context):
        OBprops = context.window_manager.a3ob_hitpoint_generator
        scene = context.scene
        
        # SUPER hacky way to get rid of the object if it's only retained in memory because of this property
        if OBprops.source or OBprops.target:
            cloudutils.validate_references(OBprops.source,OBprops.target)
        
        layout = self.layout
        layout.prop_search(OBprops,"source",bpy.context.scene,"objects")
        layout.prop_search(OBprops,"target",bpy.context.scene,"objects")
        col = layout.column(align=True)
        col.prop(OBprops,"spacing")
        colBevel = layout.column(align=True,heading="Bevel:")
        colBevel.prop(OBprops,"bevel_offset",text="Offset")
        colBevel.prop(OBprops,"bevel_segments",text="Segments")
        colBevel.separator()
        row = colBevel.row(align=True)
        row.use_property_split = True
        row.use_property_decorate = False
        row.prop(OBprops,"triangulate",text="Triangulate",expand=True)
        
        colSelection = layout.column(align=True,heading="Selection:")
        colSelection.prop(OBprops,"selection",icon='MESH_DATA',text="")
        
        layout.operator('a3ob.hitpoints_generate',text="Generate",icon='LIGHTPROBE_GRID')
        
classes = (
    A3OB_OT_hitpoints_generate,
    A3OB_PT_hitpoints
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)