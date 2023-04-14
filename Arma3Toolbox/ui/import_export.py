import bpy
import bpy_extras
import os

from ..io import import_p3d
from .. import utility as utils

class A3OB_OP_import_P3D(bpy.types.Operator,bpy_extras.io_utils.ImportHelper):
    '''Import Arma 3 MLOD P3D'''
    bl_idname = "a3ob.importp3d"
    bl_label = "Import P3D"
    
    filename_ext = ".p3d"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.p3d",
        options = {'HIDDEN'}
    )
    
    # lods: bpy.props.EnumProperty (
        # name = "LODs",
        # description = "Import the selected LOD(s)",
        # default = 'ALL',
        # items = (
            # ('ALL',"All","All LODs"),
            # ('VISUAL',"Visuals","Visual LODs only"),
            # ('SHADOW',"Shadows","Visual LODs only"),
            # ('GEO',"Geometry","Geometry LOD only")
        # )
    # )
    enclose: bpy.props.BoolProperty (
        name = "Enclose in collection",
        description = "Enclose LODs in collection named after the original file name",
        default = True
    )
    
    groupby: bpy.props.EnumProperty (
        name = "Group by",
        description = "Include LODs in collections according to the selection",
        default = 'TYPE',
        items = (
            ('NONE',"None","Import LODs without collections"),
            ('TYPE',"Type","Group LODs by logical type (eg.: visuals, geometries, etc.)")
            # ('CONTEXT',"Context","Group LODs by context")
        )
    )
    
    preserveNormals: bpy.props.BoolProperty (
        name = "Custom normals",
        description = "Attempt to import the split vertex normals of visual LODs (may not work with certain files)",
        default = True
    )
    
    validateMeshes: bpy.props.BoolProperty (
        name = "Validate meshes",
        description = "Validate LOD meshes after creation, and clean up duplicate faces and other problematic geometry",
        default = True
    )
    
    def execute(self,context):
        print(self.filepath)
        
        file = open(self.filepath,'rb')
        filename = os.path.basename(self.filepath)
        
        if not self.enclose:
            filename = ""
        
        # try:
            # import_p3d.import_file(context,file,self.groupby,filename.strip())
        # except IOError as e:
            # utils.show_infoBox(str(e),"I/O error",'INFO')
        # except Exception as e:
            # utils.show_infoBox(str(e),"Unexpected I/O error",'ERROR')
            
        import_p3d.import_file(context,file,self.groupby,self.preserveNormals,self.validateMeshes,filename.strip()) # Allow exceptions for testing
        
        file.close()
        
        return {'FINISHED'}
        
class A3OB_OP_export_P3D(bpy.types.Operator,bpy_extras.io_utils.ExportHelper):
    '''Export to Arma 3 MLOD P3D'''
    bl_idname = "a3ob.exportp3d"
    bl_label = "Export P3D"
    
    filename_ext = ".p3d"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.p3d",
        options = {'HIDDEN'}
    )
    
    use_selection: bpy.props.BoolProperty (
        name = "Selected only",
        description = "Export only selected objects",
        default = True
    )
    
    apply_transforms: bpy.props.BoolProperty (
        name = "Apply transforms",
        description = "Apply space transformations to the exported model data",
        default = True
    )
    
    def execute(self,context):
        pass
        return {'FINISHED'}
        
classes = (
    A3OB_OP_import_P3D,
    A3OB_OP_export_P3D
)
        
def menu_func_import(self,context):
    self.layout.operator(A3OB_OP_import_P3D.bl_idname,text="Arma 3 model (.p3d)")
        
def menu_func_export(self,context):
    self.layout.operator(A3OB_OP_export_P3D.bl_idname,text="Arma 3 model (.p3d)")
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)