import traceback
import os

import bpy
import bpy_extras

from ..io import import_asc, export_asc
from ..utilities import generic as utils


class A3OB_OP_import_asc(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Esri ASCII grid as DTM"""
    
    bl_idname = "a3ob.import_asc"
    bl_label = "Import ASC"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    filename_ext = ".asc"
    
    filter_glob: bpy.props.StringProperty(
        default = "*.asc",
        options = {'HIDDEN'}
    )
    vertical_scale: bpy.props.FloatProperty(
        name = "Vertical Scaling",
        description = "Vertical scaling coefficient",
        default = 1.0,
        min = -0.001,
        max = 1000.0
    )
    
    def execute(self, context):        
        with open(self.filepath) as file:
            try:
                import_asc.read_file(self, context, file)
                self.report({'INFO'}, "Successfully imported DEM")
            except Exception as ex:
                self.report({'ERROR'}, str(ex))
                traceback.print_exc()
        
        return {'FINISHED'}


class A3OB_OP_export_asc(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export DTM as Esri ASCII grid"""
    bl_idname = "a3ob.export_asc"
    bl_label = "Export ASC"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    filename_ext = ".asc"
    
    filter_glob: bpy.props.StringProperty(
        default = "*.asc",
        options = {'HIDDEN'}
    )
    apply_modifiers: bpy.props.BoolProperty(
        name = "Apply Modifiers",
        description = "Apply the assigned modifiers to the DTM object during export",
        default = True
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and len(obj.data.vertices) > 0
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "apply_modifiers")
    
    def execute(self, context):
        obj = context.active_object
        
        if not export_asc.valid_resolution(self, context, obj):
            self.report({'ERROR'}, "Cannot export irregular raster, raster resolutions must be equal in X and Y directions")
            return {'FINISHED'}
        
        output = utils.OutputManager(self.filepath, "w")
        with output as file:
            try:
                export_asc.write_file(self, context, file, obj)
                output.success = True
            except Exception as ex:
                self.report({'ERROR'}, "%s (check the system console)" % str(ex))
                traceback.print_exc()
        
        return {'FINISHED'}


classes = (
    A3OB_OP_import_asc,
    A3OB_OP_export_asc
)


def menu_func_import(self, context):
    self.layout.operator(A3OB_OP_import_asc.bl_idname, text="Esri Grid ASCII (.asc)")


def menu_func_export(self, context):
    self.layout.operator(A3OB_OP_export_asc.bl_idname, text="Esri Grid ASCII (.asc)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    print("\t" + "UI: ASC Import / Export")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    
    print("\t" + "UI: ASC Import / Export")