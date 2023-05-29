import bpy
import bpy_extras

from ..io import import_asc, export_asc


class A3OB_OP_import_asc(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Esri ASCII grid as DTM"""
    
    bl_idname = "a3ob.import_asc"
    bl_label = "Import ASC"
    bl_options = {'UNDO'}
    filename_ext = ".asc"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.asc",
        options = {'HIDDEN'}
    )
    vertical_scale: bpy.props.FloatProperty (
        name = "Vertical Scaling",
        description = "Vertical scaling coefficient",
        default = 1.0,
        min = -0.001,
        max = 1000.0
    )
    
    # def draw(self, context):
        # pass
    
    def execute(self, context):
        with open(self.filepath) as file:
            import_asc.read_file(self, context, file)
        
        return {'FINISHED'}


class A3OB_OP_export_asc(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export DTM as Esri ASCII grid"""
    bl_idname = "a3ob.export_asc"
    bl_label = "Export ASC"
    bl_options = {'UNDO'}
    filename_ext = ".asc"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.asc",
        options = {'HIDDEN'}
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj
    
    # def draw(self, context):
        # pass
    
    def execute(self, context):
        obj = context.active_object
        
        if not export_asc.valid_resolution(obj.data):
            self.report({'ERROR'}, "Cannot export irregular raster")
            return {'FINISHED'}
            
        with open(self.filepath, "wt") as file:
            export_asc.write_file(self, context, file, obj)
        
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