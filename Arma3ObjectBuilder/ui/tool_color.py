import bpy

from ..utilities import generic as utils
from ..utilities import colors as colorutils


class A3OB_PT_colors(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Colors"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    # def draw_header(self, context):
        # if not utils.get_addon_preferences(context).show_info_links:
            # return
            
        # layout = self.layout
        # row = layout.row(align=True)
        # row.operator("wm.url_open", text="", icon='HELP').url = "https://github.com/MrClock8163/Arma3Toolbox/wiki/Tool:-Conversion"
        
    def draw(self, context):
        layout = self.layout
        wm_props = context.window_manager.a3ob_colors
        
        layout.label(text="Input:")
        
        row_input_type = layout.row(align=True)
        row_input_type.prop(wm_props, "input_type", expand=True)
        
        col_input = layout.column(align=True)
        if wm_props.input_type == 'S8':
            col_input.prop(wm_props, "input_red_int")
            col_input.prop(wm_props, "input_green_int")
            col_input.prop(wm_props, "input_blue_int")
        else:
            col_input.prop(wm_props, "input_red_float")
            col_input.prop(wm_props, "input_green_float")
            col_input.prop(wm_props, "input_blue_float")
            
        layout.label(text="Output:")
            
        row_output_type = layout.row(align=True)
        row_output_type.prop(wm_props, "output_type", expand=True)
        
        col_output = layout.column(align=True)
        
        if wm_props.output_type == 'S8':
            col_output.prop(wm_props, "output_red_int")
            col_output.prop(wm_props, "output_green_int")
            col_output.prop(wm_props, "output_blue_int")
        else:
            col_output.prop(wm_props, "output_red_float")
            col_output.prop(wm_props, "output_green_float")
            col_output.prop(wm_props, "output_blue_float")
        
        if wm_props.output_type in {'S8', 'S'}:
            layout.prop(wm_props, "output_srgb", text="")
        else:
            layout.prop(wm_props, "output_linear", text="")


classes = (
    A3OB_PT_colors,
)


def register():
    from bpy.utils import register_class
    
    for cls in classes:
        register_class(cls)
    
    print("\t" + "UI: Colors")


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    
    print("\t" + "UI: Colors")