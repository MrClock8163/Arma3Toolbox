import bpy

from ..utilities import clouds as cloudutils


class A3OB_OT_hitpoints_generate(bpy.types.Operator):
    """Create hit points cloud from shape"""
    
    bl_idname = "a3ob.hitpoints_generate"
    bl_label = "Generate Hit Point Cloud"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        wm_props = context.window_manager.a3ob_hitpoint_generator
        return wm_props.source and (wm_props.source != wm_props.target) and wm_props.source.type == 'MESH' and (not wm_props.target or wm_props.target.type == 'MESH')
        
    def execute(self, context):        
        cloudutils.generate_hitpoints(self, context)
        return {'FINISHED'}


class A3OB_PT_hitpoints(bpy.types.Panel):   
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Hit Point Cloud"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw_header(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3ObjectBuilder/wiki/Tool:-Hit-Point-Cloud"
        
    def draw(self, context):
        wm_props = context.window_manager.a3ob_hitpoint_generator
        scene = context.scene
        
        # SUPER hacky way to get rid of the object if it's only retained in memory because of this property
        if wm_props.source or wm_props.target:
            cloudutils.validate_references(wm_props.source, wm_props.target)
        
        layout = self.layout
        
        layout.prop_search(wm_props, "source", scene, "objects")
        layout.prop_search(wm_props, "target", scene, "objects")
        
        col = layout.column(align=True)
        col.prop(wm_props,"spacing")
        
        col_bevel = layout.column(align=True, heading="Bevel:")
        col_bevel.prop(wm_props, "bevel_offset", text="Offset")
        col_bevel.prop(wm_props, "bevel_segments", text="Segments")
        col_bevel.separator()
        row_triangulate = col_bevel.row(align=True)
        row_triangulate.use_property_split = True
        row_triangulate.use_property_decorate = False
        row_triangulate.prop(wm_props, "triangulate", text="Triangulate", expand=True)
        
        col_selection = layout.column(align=True, heading="Selection:")
        col_selection.prop(wm_props, "selection", text="", icon='MESH_DATA')
        
        layout.operator("a3ob.hitpoints_generate", text="Generate", icon='LIGHTPROBE_GRID')


classes = (
    A3OB_OT_hitpoints_generate,
    A3OB_PT_hitpoints
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "UI: Hit Point Cloud")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: Hit Point Cloud")