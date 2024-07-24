import bpy

from ..utilities import generic as utils


class A3OB_PT_maps(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Maps"
    bl_options = {'DEFAULT_CLOSED'}

    doc_url = "https://mrcmodding.gitbook.io/arma-3-object-builder/tools/maps"
    
    def draw_header(self, context):
        utils.draw_panel_header(self)

    def draw(self, context):
        pass


class A3OB_PT_maps_objects(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Objects"
    bl_parent_id = "A3OB_PT_maps"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout


classes = (
    A3OB_PT_maps,
    A3OB_PT_maps_objects
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    print("\t" + "UI: Maps")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    print("\t" + "UI: Maps")