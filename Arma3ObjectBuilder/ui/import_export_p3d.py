import traceback
import struct
import os

import bpy
import bpy_extras

from ..io import import_p3d, export_p3d
from ..utilities import generic as utils


class A3OB_OP_import_p3d(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Arma 3 MLOD P3D"""
    
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
            ('NONE', "None", "Import LODs without collections"),
            ('TYPE', "Type", "Group LODs by logical type (eg.: visuals, geometries, etc.)")
        )
    )
    additional_data_allowed: bpy.props.BoolProperty (
        name = "Allow Additinal Data",
        description = "Import data in addition to the LOD geometries themselves",
        default = True
    )
    additional_data: bpy.props.EnumProperty (
        name = "Data",
        options = {'ENUM_FLAG'},
        items = (
            ('NORMALS', "Custom Normals", "WARNING: may not work properly on certain files"),
            ('PROPS', "Named Properties", ""),
            ('MASS', "Vertex Mass", "Mass of individual vertices (in Geometry LODs)"),
            ('SELECTIONS', "Selections", ""),
            ('UV', "UV Sets", ""),
            ('MATERIALS', "Materials", "")
        ),
        description = "Data to import in addition to the LOD meshes themselves",
        default = {'NORMALS', 'PROPS', 'MASS', 'SELECTIONS', 'UV', 'MATERIALS'}
    )
    validate_meshes: bpy.props.BoolProperty (
        name = "Validate Meshes",
        description = "Validate LOD meshes after creation, and clean up duplicate faces and other problematic geometry",
        default = True
    )
    proxy_action: bpy.props.EnumProperty (
        name = "Proxy Action",
        description = "Post-import handling of proxies",
        items = (
            ('NOTHING', "Nothing", "Leave proxies embedded into the LOD meshes\n(the actual file paths will be lost because of Blender limitations)"),
            ('SEPARATE', "Separate", "Separate the proxies into proxy objects parented to the LOD mesh they belong to"),
            ('CLEAR', "Purge", "Remove all proxies")
        ),
        default = 'SEPARATE'
    )
    dynamic_naming: bpy.props.BoolProperty (
        name = "Dynamic Naming",
        description = "Enable Dynamic Object Naming for LOD and proxy objects",
        default = True
    )
    first_lod_only: bpy.props.BoolProperty (
        name = "First LOD Only",
        description = "Import only the first LOD found in the file",
        default = False
    )
    
    def draw(self, context):
        pass
    
    def execute(self, context):        
        with open(self.filepath, "rb") as file:
            try:
                lod_data = import_p3d.read_file(self, context, file, self.first_lod_only)
                self.report({'INFO'}, "Succesfully imported %d LODs (check the logs in the system console)" % len(lod_data))
            except struct.error as ex:
                self.report({'ERROR'}, "Unexpected EndOfFile (check the system console)")
                traceback.print_exc()
            except Exception as ex:
                self.report({'ERROR'}, "%s (check the system console)" % str(ex))
                traceback.print_exc()
        
        return {'FINISHED'}


class A3OB_PT_import_p3d_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Main"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_p3d"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator, "dynamic_naming")
        layout.prop(operator, "first_lod_only")
        layout.prop(operator, "validate_meshes")


class A3OB_PT_import_p3d_collections(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Collections"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_p3d"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator, "enclose")
        layout.prop(operator, "groupby")


class A3OB_PT_import_p3d_data(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Data"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_p3d"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(heading="Additional data")
        col.prop(operator, "additional_data_allowed", text="")
        
        col_enum = col.column()
        col_enum.enabled = operator.additional_data_allowed
        col_enum.prop(operator, "additional_data", text=" ") # text=" " otherwise the enum is stretched accross the panel


class A3OB_PT_import_p3d_proxies(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Proxies"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_import_p3d"
        
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        if 'SELECTIONS' not in operator.additional_data or not operator.additional_data_allowed:
            layout.alert = True
            layout.label(text="Enable selection data")
        
            col = layout.column(align=True)
            col.prop(operator, "proxy_action", expand=True)
            col.enabled = False
        else:
            col = layout.column(align=True)
            col.prop(operator, "proxy_action", expand=True)


class A3OB_OP_export_p3d(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export to Arma 3 MLOD P3D"""
    
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
    validate_lods: bpy.props.BoolProperty (
        name = "Validate LODs",
        description = "Validate LOD objects, and skip the export of invalid ones",
        default = False
    )
    validate_lods_warning_errors: bpy.props.BoolProperty (
        name = "Warnings Are Errors",
        description = "Treat warnings as errors",
        default = True
    )
    
    def draw(self, context):
        pass
    
    def execute(self, context):
        if export_p3d.can_export(self, context):
            temppath = self.filepath + ".temp"
            success = False
            
            with open(temppath, "wb") as file:
                try:
                    lod_count, exported_count = export_p3d.write_file(self, context, file)
                    self.report({'INFO'}, "Succesfully exported %d/%d LODs (check the logs in the system console)" % (exported_count, lod_count))
                    success = True
                except Exception as ex:
                    self.report({'ERROR'}, "%s (check the system console)" % str(ex))
                    traceback.print_exc()
            
            if success:
                if os.path.isfile(self.filepath):
                    os.remove(self.filepath)
                    
                os.rename(temppath, os.path.splitext(temppath)[0])
            elif not success and not utils.get_addon_preferences(context).preserve_faulty_output:
                os.remove(temppath)
                
        else:
            self.report({'INFO'}, "There are no LODs to export")
        
        return {'FINISHED'}


class A3OB_PT_export_p3d_include(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Include"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_export_p3d"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(heading="Limit To", align=True)
        col.prop(operator, "use_selection")


class A3OB_PT_export_p3d_meshes(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Mesh Data"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_export_p3d"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(align=True)
        col.prop(operator, "validate_meshes")
        col.prop(operator, "apply_modifiers")
        col.prop(operator, "apply_transforms")
        col.prop(operator, "preserve_normals")


class A3OB_PT_export_p3d_validate(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "LODs"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        
        return operator.bl_idname == "A3OB_OT_export_p3d"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(align=True)
        col.prop(operator, "validate_lods")
        row = col.row(align=True)
        row.prop(operator, "validate_lods_warning_errors")
        if not operator.validate_lods:
            row.enabled = False


classes = (
    A3OB_OP_import_p3d,
    A3OB_PT_import_p3d_main,
    A3OB_PT_import_p3d_collections,
    A3OB_PT_import_p3d_data,
    A3OB_PT_import_p3d_proxies,
    A3OB_OP_export_p3d,
    A3OB_PT_export_p3d_include,
    A3OB_PT_export_p3d_meshes,
    A3OB_PT_export_p3d_validate
)


def menu_func_import(self, context):
    self.layout.operator(A3OB_OP_import_p3d.bl_idname, text="Arma 3 model (.p3d)")


def menu_func_export(self, context):
    self.layout.operator(A3OB_OP_export_p3d.bl_idname, text="Arma 3 model (.p3d)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    print("\t" + "UI: P3D Import / Export")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    
    print("\t" + "UI: P3D Import / Export")