import bpy

from . import props
from . import clouds
from .. import get_icon
from .. import utils


class A3OB_OT_hitpoints_generate(bpy.types.Operator):
    """Create hit points cloud from shape"""
    
    bl_idname = "a3ob.hitpoints_generate"
    bl_label = "Generate Hit Point Cloud"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        scene_props = context.scene.a3ob_hitpoint_generator
        return scene_props.source and (scene_props.source != scene_props.target) and scene_props.source.type == 'MESH' and (not scene_props.target or scene_props.target.type == 'MESH')
        
    def execute(self, context):        
        clouds.generate_hitpoints(self, context)
        return {'FINISHED'}


class A3OB_PT_hitpoints(bpy.types.Panel, utils.PanelHeaderLinkMixin):   
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Hit Point Cloud"
    bl_options = {'DEFAULT_CLOSED'}

    doc_url = "https://mrcmodding.gitbook.io/arma-3-object-builder/tools/hit-point-cloud"
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw(self, context):
        scene_props = context.scene.a3ob_hitpoint_generator
        scene = context.scene
        
        # SUPER hacky way to get rid of the object if it's only retained in memory because of this property
        if scene_props.source or scene_props.target:
            clouds.validate_references(scene_props.source, scene_props.target)
        
        layout = self.layout
        
        layout.prop_search(scene_props, "source", scene, "objects")
        layout.prop_search(scene_props, "target", scene, "objects")
        
        col = layout.column(align=True)
        col.prop(scene_props,"spacing")
        
        col_selection = layout.column(align=True, heading="Selection:")
        col_selection.prop(scene_props, "selection", text="", icon='MESH_DATA')
        
        layout.operator("a3ob.hitpoints_generate", text="Generate", icon_value=get_icon("op_hitpoints_generate"))


classes = (
    A3OB_OT_hitpoints_generate,
    A3OB_PT_hitpoints
)


def register():
    props.register_props()

    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("\t" + "Tool: Hit Point Cloud")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    props.unregister_props()
    
    print("\t" + "Tool: Hit Point Cloud")
