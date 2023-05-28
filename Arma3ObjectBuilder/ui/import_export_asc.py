import bpy
import bpy_extras

from ..io import import_asc


class A3OB_OP_import_asc(bpy.types.Operator,bpy_extras.io_utils.ImportHelper):
    """Import Esri grid (ASCII)"""
    
    bl_idname = "a3ob.import_asc"
    bl_label = "Import ASC"
    bl_options = {'UNDO', 'PRESET'}
    filename_ext = ".asc"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.asc",
        options = {'HIDDEN'}
    )
    
    # def draw(self, context):
        # pass
    
    def execute(self, context):
        with open(self.filepath) as file:
            success = import_asc.read_file(self, context, file)
            if not success:
                self.report({'ERROR'}, "The Esri grid could not be imported")
        
        return {'FINISHED'}


classes = (
    A3OB_OP_import_asc,
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