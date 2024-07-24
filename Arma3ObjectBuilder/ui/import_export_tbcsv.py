import traceback
import struct

import bpy
import bpy_extras


from ..io import import_tbcsv, export_tbcsv
from ..utilities import generic as utils


class A3OB_OP_import_tbcsv(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Arma 3 map object positions"""
    
    bl_idname = "a3ob.import_tbcsv"
    bl_label = "Import Positions"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    filename_ext = ".txt"
    
    filter_glob: bpy.props.StringProperty(
        default = "*.txt",
        options = {'HIDDEN'}
    )
    targets: bpy.props.EnumProperty(
        name = "Objects",
        description = "Scope of objects to set positions on",
        items = (
            ('ALL', "All", "All objects in the project"),
            ('SCENE', "Scene", "Objects in active scene"),
            ('SELECTION', "Selection", "Objects in active selection"),
        ),
        default = 'SCENE'
    )
    elevations: bpy.props.EnumProperty(
        name = "Elevations",
        description = "Elevation type",
        items = (
            ('RELATIVE', "Relative", "Relative to ground level"),
            ('ABSOLUTE', "Absolute", "Relative to sea level")
        ),
        default = 'ABSOLUTE'
    )
    
    def draw(self, context):
        pass

    def execute(self, context):
        with open(self.filepath, "rt") as file:
            try:
                count_read, count_found = import_tbcsv.read_file(self, context, file)
                utils.op_report(self, {'INFO'}, "Successfully imported %d/%d object positions (check the logs in the system console)" % (count_found, count_read))
            except import_tbcsv.tb.TBCSV_Error as ex:
                utils.op_report(self, {'ERROR'}, "%s (check the system console)" % ex)
            except Exception as ex:
                utils.op_report(self, {'ERROR'}, "%s (check the system console)" % ex)
                traceback.print_exc()

        return {'FINISHED'}


class A3OB_PT_import_tbcsv_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Main"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_tbcsv"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator

        col = layout.column(align=True)
        col.prop(operator, "targets", expand=True)
        layout.prop(operator, "elevations")


class A3OB_OP_export_tbcsv(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Arma 3 map object positions"""
    
    bl_idname = "a3ob.export_tbcsv"
    bl_label = "Export Positions"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    filename_ext = ".txt"
    
    filter_glob: bpy.props.StringProperty(
        default = "*.txt",
        options = {'HIDDEN'}
    )
    collection: bpy.props.StringProperty(
        name = "Source Collection",
        description = "Export only objects from this collection (and its children)",
        default = "",
    )
    targets: bpy.props.EnumProperty(
        name = "Objects",
        description = "Scope of objects to set positions on",
        items = (
            ('ALL', "All", "All objects in the project"),
            ('SCENE', "Scene", "Objects in active scene"),
            ('SELECTION', "Selection", "Objects in active selection"),
        ),
        default = 'SCENE'
    )
    
    def draw(self, context):
        pass

    def execute(self, context):
        if not utils.OutputManager.can_access_path(self.filepath):
            utils.op_report(self, {'ERROR'}, "Cannot write to target file (file likely in use by another blocking process)")
            return {'FINISHED'}
        
        output = utils.OutputManager(self.filepath, "wt")
        with output as file:
            try:
                count = export_tbcsv.write_file(self, context, file)
                utils.op_report(self, {'INFO'}, "Successfully exported %d object positions (check the logs in the system console)" % count)
                output.success = True
            except import_tbcsv.tb.TBCSV_Error as ex:
                utils.op_report(self, {'ERROR'}, "%s (check the system console)" % ex)
            except Exception as ex:
                utils.op_report(self, {'ERROR'}, "%s (check the system console)" % ex)
                traceback.print_exc()

        return {'FINISHED'}


class A3OB_PT_export_tbcsv_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Main"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_export_tbcsv"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator

        col = layout.column(align=True)
        col.prop(operator, "targets", expand=True)



classes = (
    A3OB_OP_import_tbcsv,
    A3OB_PT_import_tbcsv_main,
    A3OB_OP_export_tbcsv,
    A3OB_PT_export_tbcsv_main
)

if bpy.app.version >= (4, 1, 0):
    class A3OB_FH_tbcsv(bpy.types.FileHandler):
        bl_label = "Arma 3 map objects list"
        bl_import_operator = "a3ob.import_tbcsv"
        bl_export_operator = "a3ob.export_tbcsv"
        bl_file_extensions = ".txt"
    
        @classmethod
        def poll_drop(cls, context):
            return context.area and context.area.type == 'VIEW_3D'

    classes = (*classes, A3OB_FH_tbcsv)


def menu_func_import(self, context):
    self.layout.operator(A3OB_OP_import_tbcsv.bl_idname, text="Arma 3 map objects (.txt)")


def menu_func_export(self, context):
    self.layout.operator(A3OB_OP_export_tbcsv.bl_idname, text="Arma 3 map objects (.txt)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    print("\t" + "UI: TB TXT Import / Export")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    
    print("\t" + "UI: TB TXT Import / Export")
