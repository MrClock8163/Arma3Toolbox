import bpy
import bpy_extras
import os

from ..io import import_p3d, export_p3d

class A3OB_OP_import_p3d(bpy.types.Operator,bpy_extras.io_utils.ImportHelper):
    '''Import Arma 3 MLOD P3D'''
    bl_idname = "a3ob.import_p3d"
    bl_label = "Import P3D"
    bl_options = {'UNDO', 'PRESET'}
    
    filename_ext = ".p3d"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.p3d",
        options = {'HIDDEN'}
    )
    
    enclose: bpy.props.BoolProperty (
        name = "Enclose In Collection",
        description = "Enclose LODs in collection named after the original file",
        default = True
    )
    
    groupby: bpy.props.EnumProperty (
        name = "Group By",
        description = "Include LODs in collections according to the selection",
        default = 'TYPE',
        items = (
            ('NONE',"None","Import LODs without collections"),
            ('TYPE',"Type","Group LODs by logical type (eg.: visuals, geometries, etc.)")
            # ('CONTEXT',"Context","Group LODs by context")
        )
    )
    
    preserveNormals: bpy.props.BoolProperty (
        name = "Custom Normals",
        description = "Attempt to import the split vertex normals of visual LODs (may not work with certain files)",
        default = True
    )
    
    setupMaterials: bpy.props.BoolProperty (
        name = "Setup Materials",
        description = "Create materials for every texture - RVMAT combination in the P3D",
        default = True
    )
    
    allowAdditionalData: bpy.props.BoolProperty (
        name = "Allow Additinal Data",
        description = "Import data in addition to the LOD geometries themselves",
        default = True
    )
    
    additionalData: bpy.props.EnumProperty (
        name = "Data",
        options = {'ENUM_FLAG'},
        items = (
            ('NORMALS',"Custom Normals","WARNING: may not work properly on certain files"),
            ('PROPS',"Named Properties",""),
            ('MASS',"Vertex Mass","Mass of individual vertices (in Geometry LODs)"),
            ('SELECTIONS',"Selections",""),
            ('UV',"UV Sets",""),
            ('MATERIALS',"Materials","")
        ),
        description = "Data to import in addition to the LOD meshes themselves",
        default = {'NORMALS','PROPS','MASS','SELECTIONS','UV','MATERIALS'}
    )
    
    validateMeshes: bpy.props.BoolProperty (
        name = "Validate Meshes",
        description = "Validate LOD meshes after creation, and clean up duplicate faces and other problematic geometry",
        default = True
    )
    
    proxyHandling: bpy.props.EnumProperty (
        name = "Proxy Action",
        description = "Post-import handling of proxies",
        items = (
            ('NOTHING',"Nothing","Leave proxies embedded into the LOD meshes\n(the actual file paths will be lost because of Blender limitations)"),
            ('SEPARATE',"Separate","Separate the proxies into proxy objects parented to the LOD mesh they belong to"),
            ('CLEAR',"Purge","Remove all proxies")
        ),
        default = 'SEPARATE'
    )
    
    def draw(self,context):
        pass
    
    def execute(self,context):
        # print(self.filepath)
        
        file = open(self.filepath,'rb')
        filename = os.path.basename(self.filepath)
        
        if not self.enclose:
            filename = ""
            
        # print(type(self.additionalData))
        
        # try:
            # import_p3d.import_file(context,file,self.groupby,filename.strip())
        # except IOError as e:
            # utils.show_infoBox(str(e),"I/O error",'INFO')
        # except struct.error as e:
            # utils.show_infoBox("Unexpected EnfOfFile","I/O error",'INFO')
        # except Exception as e:
            # utils.show_infoBox(str(e),"Unexpected I/O error",'ERROR')
            
        # import_p3d.import_file(context,file,self.groupby,self.preserveNormals,self.validateMeshes,self.setupMaterials,filename.strip()) # Allow exceptions for testing
        import_p3d.read_file(self,context,file) # Allow exceptions for testing
        
        file.close()
        
        return {'FINISHED'}
        
class A3OB_PT_import_p3d_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Main"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls,context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_p3d"
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator,"validateMeshes")
        
class A3OB_PT_import_p3d_collections(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Collections"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls,context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_p3d"
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator,"enclose")
        layout.prop(operator,"groupby")
        
class A3OB_PT_import_p3d_data(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Data"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls,context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_p3d"
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(heading="Additional data")
        col.prop(operator,"allowAdditionalData",text="")
        col2 = col.column()
        col2.enabled = operator.allowAdditionalData
        prop = col2.prop(operator,"additionalData",text=" ")
        
class A3OB_PT_import_p3d_proxies(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Proxies"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls,context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_p3d"
        
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        if 'SELECTIONS' not in operator.additionalData or not operator.allowAdditionalData:
            layout.alert = True
            layout.label(text="Enable selection data")
        
            col = layout.column(align=True)
            col.prop(operator,"proxyHandling",expand=True)
            col.enabled = False
        else:
            col = layout.column(align=True)
            col.prop(operator,"proxyHandling",expand=True)
        
class A3OB_OP_export_p3d(bpy.types.Operator,bpy_extras.io_utils.ExportHelper):
    '''Export to Arma 3 MLOD P3D'''
    bl_idname = "a3ob.export_p3d"
    bl_label = "Export P3D"
    bl_options = {'UNDO', 'PRESET'}
    
    filename_ext = ".p3d"
    
    filter_glob: bpy.props.StringProperty (
        default = "*.p3d",
        options = {'HIDDEN'}
    )
    
    preserve_normals: bpy.props.BoolProperty (
        name = "Custom Normals",
        description = "Export the custom split edge normals",
        default = True
    )
    
    validate_meshes: bpy.props.BoolProperty (
        name = "Validate Meshes",
        description = "Clean up invalid geometry before export (eg.: duplicate faces, edges, vertices)",
        default = True
    )
    
    use_selection: bpy.props.BoolProperty (
        name = "Selected Only",
        description = "Export only selected objects",
        default = False
    )
    
    apply_transforms: bpy.props.BoolProperty (
        name = "Apply Transforms",
        description = "Apply space transformations to the exported model data",
        default = True
    )
    
    apply_modifiers: bpy.props.BoolProperty (
        name = "Apply Modifiers",
        description = "Apply the assigned modifiers to the LOD objects during export",
        default = True
    )
    
    def draw(self,context):
        pass
    
    def execute(self,context):
        if export_p3d.can_export(self,context):
            
            file = open(self.filepath,'wb')
            filename = os.path.basename(self.filepath)
            
            lod_count,exported_count = export_p3d.write_file(self,context,file)
            
            file.close()
            
            self.report({'INFO'},f"Succesfully exported {exported_count}/{lod_count} LODs")
        else:
            self.report({'INFO'},"There are no LODs to export")
        
        return {'FINISHED'}
        
class A3OB_PT_export_p3d_include(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Include"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls,context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_export_p3d"
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(heading="Limit To",align=True)
        col.prop(operator,"use_selection")
        
class A3OB_PT_export_p3d_meshes(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Mesh Data"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls,context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_export_p3d"
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(align=True)
        col.prop(operator,"validate_meshes")
        col.prop(operator,"apply_modifiers")
        col.prop(operator,"apply_transforms")
        col.prop(operator,"preserve_normals")
        
classes = (
    A3OB_OP_import_p3d,
    A3OB_PT_import_p3d_main,
    A3OB_PT_import_p3d_collections,
    A3OB_PT_import_p3d_data,
    A3OB_PT_import_p3d_proxies,
    A3OB_OP_export_p3d,
    A3OB_PT_export_p3d_include,
    A3OB_PT_export_p3d_meshes
)
        
def menu_func_import(self,context):
    self.layout.operator(A3OB_OP_import_p3d.bl_idname,text="Arma 3 model (.p3d)")
        
def menu_func_export(self,context):
    self.layout.operator(A3OB_OP_export_p3d.bl_idname,text="Arma 3 model (.p3d)")
    
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