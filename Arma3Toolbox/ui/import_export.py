import bpy
import bpy_extras
import os

from ..io import import_p3d
from .. import utility as utils

class A3OB_OP_import_P3D(bpy.types.Operator,bpy_extras.io_utils.ImportHelper):
    '''Import Arma 3 MLOD P3D'''
    bl_idname = "a3ob.importp3d"
    bl_label = "Import P3D"
    bl_options = {'UNDO', 'PRESET'}
    
    filename_ext = ".p3d"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.p3d",
        options = {'HIDDEN'}
    )
    
    enclose: bpy.props.BoolProperty (
        name = "Enclose in collection",
        description = "Enclose LODs in collection named after the original file",
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
    
    setupMaterials: bpy.props.BoolProperty (
        name = "Setup materials",
        description = "Create materials for every texture - RVMAT combination in the P3D",
        default = True
    )
    
    allowAdditionalData: bpy.props.BoolProperty (
        name = "Allow additinal data",
        description = "Import data in addition to the LOD geometries themselves",
        default = True
    )
    
    additionalData: bpy.props.EnumProperty (
        name = "Data",
        options = {'ENUM_FLAG'},
        items = (
            ('NORMALS',"Custom normals","WARNING: may not work properly on certain files"),
            ('SELECTIONS',"Selections",""),
            ('UV',"UV sets",""),
            ('MATERIALS',"Materials","")
        ),
        description = "Data to import in addition to the LOD meshes themselves",
        default = {'NORMALS','SELECTIONS','UV','MATERIALS'}
    )
    
    validateMeshes: bpy.props.BoolProperty (
        name = "Validate meshes",
        description = "Validate LOD meshes after creation, and clean up duplicate faces and other problematic geometry",
        default = True
    )
    
    def draw(self,context):
        pass
    
    def execute(self,context):
        print(self.filepath)
        
        file = open(self.filepath,'rb')
        filename = os.path.basename(self.filepath)
        
        if not self.enclose:
            filename = ""
            
        # print(type(self.additionalData))
        
        # try:
            # import_p3d.import_file(context,file,self.groupby,filename.strip())
        # except IOError as e:
            # utils.show_infoBox(str(e),"I/O error",'INFO')
        # except Exception as e:
            # utils.show_infoBox(str(e),"Unexpected I/O error",'ERROR')
            
        # import_p3d.import_file(context,file,self.groupby,self.preserveNormals,self.validateMeshes,self.setupMaterials,filename.strip()) # Allow exceptions for testing
        import_p3d.import_file(self,context,file) # Allow exceptions for testing
        
        file.close()
        
        return {'FINISHED'}
        
class A3OB_PT_import_P3D_collections(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Collections"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls,context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_importp3d"
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator,"enclose")
        layout.prop(operator,"groupby")
        
class A3OB_PT_import_P3D_data(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Data"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls,context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_importp3d"
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(heading="Additional data")
        col.prop(operator,"allowAdditionalData",text="")
        col2 = col.column()
        col2.enabled = operator.allowAdditionalData
        prop = col2.prop(operator,"additionalData")
        # prop.enabled = operator.allowAdditionalData = True
        layout.prop(operator,"validateMeshes")
        
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
    A3OB_PT_import_P3D_collections,
    A3OB_PT_import_P3D_data,
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