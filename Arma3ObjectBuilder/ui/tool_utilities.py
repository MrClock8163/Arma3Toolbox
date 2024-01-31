import os

import bpy

from ..utilities import structure as structutils
from ..utilities import generic as utils


class A3OB_OT_check_convexity(bpy.types.Operator):
    """Find concave edges"""
    
    bl_label = "Find Non-Convexities"
    bl_idname = "a3ob.find_non_convexities"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return len(context.selected_objects) == 1 and obj and obj.type == 'MESH'
    
    def execute(self, context):
        name, concaves = structutils.check_convexity()
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='EDGE')
        
        if concaves > 0:
            self.report({'WARNING'}, "%s has %d concave edge(s)" % (name, concaves))
        else:
            self.report({'INFO'}, "%s is convex" % name)
        
        return {'FINISHED'}


class A3OB_OT_check_closed(bpy.types.Operator):
    """Find non-closed parts of model"""
    
    bl_label = "Find Non-Closed"
    bl_idname = "a3ob.find_non_closed"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return len(context.selected_objects) == 1 and obj and obj.type == 'MESH'
    
    def execute(self,context):
        structutils.check_closed()
        return {'FINISHED'}


class A3OB_OT_convex_hull(bpy.types.Operator):
    """Calculate convex hull for entire object"""
    
    bl_label = "Convex Hull"
    bl_idname = "a3ob.convex_hull"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return len(context.selected_objects) == 1 and obj and obj.type == 'MESH'
    
    def execute(self, context):
        mode = bpy.context.object.mode
        structutils.convex_hull()
        bpy.ops.object.mode_set(mode=mode)
        return {'FINISHED'}


class A3OB_OT_component_convex_hull(bpy.types.Operator):
    """Create convex named component selections"""
    
    bl_label = "Component Convex Hull"
    bl_idname = "a3ob.component_convex_hull"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return len(context.selected_objects) == 1 and obj and obj.type == 'MESH'
    
    def execute(self,context):
        mode = bpy.context.object.mode
        obj = context.active_object
        count_components = structutils.component_convex_hull(obj)
        bpy.ops.object.mode_set(mode=mode)
        self.report({'INFO'}, "Created %d component(s) in %s" % (count_components, obj.name))
        return {'FINISHED'}


class A3OB_OT_find_components(bpy.types.Operator):
    """Create named component selections"""
    
    bl_label = "Find Components"
    bl_idname = "a3ob.find_components"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return len(context.selected_objects) == 1 and obj and obj.type == 'MESH'
    
    def execute(self, context):
        mode = bpy.context.object.mode
        obj = context.active_object
        count_components = structutils.find_components(obj)
        bpy.ops.object.mode_set(mode=mode)
        self.report({'INFO'}, "Created %d component(s) in %s" % (count_components, obj.name))
        return {'FINISHED'}


class A3OB_OT_move_top(bpy.types.Operator):
    """Move selected faces to top of face list (relative order of selected faces is maintained)"""
    
    bl_label = "Move Top"
    bl_idname = "a3ob.move_top"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT'
    
    def execute(self, context):
        bpy.ops.mesh.sort_elements(type='SELECTED', elements={'FACE'}, reverse=True)
        return {'FINISHED'}


class A3OB_OT_move_bottom(bpy.types.Operator):
    """Move selected faces to bottom of face list (relative order of selected faces is maintained)"""
    
    bl_label = "Move Bottom"
    bl_idname = "a3ob.move_bottom"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT'
    
    def execute(self, context):
        bpy.ops.mesh.sort_elements(type='SELECTED', elements={'FACE'})
        return {'FINISHED'}


class A3OB_OT_recalculate_normals(bpy.types.Operator):
    """Recalculate face normals"""
    
    bl_label = "Recalculate Normals"
    bl_idname = "a3ob.recalculate_normals"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and len(context.selected_objects) == 1 and obj.type == 'MESH' and obj.mode == 'EDIT'
    
    def execute(self, context):
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        return {'FINISHED'}


class A3OB_OT_cleanup_vertex_groups(bpy.types.Operator):
    """Cleanup vertex groups with no vertices assigned"""
    
    bl_label = "Delete Unused Groups"
    bl_idname = "a3ob.vertex_groups_cleanup"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and len(obj.vertex_groups) > 0
        
    def execute(self, context):
        obj = context.active_object
        mode = obj.mode
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        removed = structutils.cleanup_vertex_groups(obj)
        
        bpy.ops.object.mode_set(mode=mode)
        
        self.report({'INFO'} ,"Removed %d unused vertex group(s) from %s" % (removed, obj.name))
        
        return {'FINISHED'}


class A3OB_OT_redefine_vertex_group(bpy.types.Operator):
    """Remove vertex group and recreate it with the selected verticies assigned"""

    bl_label = "Redefine Vertex Group"
    bl_idname = "a3ob.vertex_group_redefine"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return len(context.selected_objects) == 1 and obj and obj.type == 'MESH' and obj.vertex_groups.active and obj.mode == 'EDIT'
        
    def execute(self, context):
        obj = context.active_object
        structutils.redefine_vertex_group(obj, context.scene.tool_settings.vertex_group_weight)
        return {'FINISHED'}


class A3OB_OT_open_changelog(bpy.types.Operator):
    """Open Arma 3 Object Builder add-on changelog"""

    bl_label = "Open Changelog"
    bl_idname = "a3ob.open_changelog"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        path = os.path.join(utils.get_addon_directory(), "CHANGELOG.md")
        bpy.ops.text.open(filepath=path, internal=True)
        self.report({'INFO'}, "See CHANGELOG.md text block")

        return {'FINISHED'}


class A3OB_MT_object_builder_topo(bpy.types.Menu):
    """Object Builder topology functions"""
    
    bl_label = "Topology"
    
    def draw(self, context):
        self.layout.operator("a3ob.find_non_closed")
        self.layout.operator("a3ob.find_components")


class A3OB_MT_object_builder_convexity(bpy.types.Menu):
    """Object Builder convexity functions"""
    
    bl_label = "Convexity"
    
    def draw(self, context):
        self.layout.operator("a3ob.find_non_convexities")
        self.layout.operator("a3ob.convex_hull")
        self.layout.operator("a3ob.component_convex_hull")


class A3OB_MT_object_builder_faces(bpy.types.Menu):
    """Object Builder face functions"""
    
    bl_label = "Faces"
    
    def draw(self, context):
        self.layout.operator("a3ob.move_top")
        self.layout.operator("a3ob.move_bottom")
        self.layout.operator("a3ob.recalculate_normals")


class A3OB_MT_object_builder_misc(bpy.types.Menu):
    """Object Builder miscellaneous functions"""
    
    bl_label = "Misc"
    
    def draw(self, context):
        self.layout.operator("a3ob.vertex_groups_cleanup")


class A3OB_MT_object_builder(bpy.types.Menu):
    """Arma 3 Object Builder utility functions"""
    
    bl_label = "Object Builder"
    
    def draw(self, context):
        self.layout.menu("A3OB_MT_object_builder_topo")
        self.layout.menu("A3OB_MT_object_builder_convexity")
        self.layout.menu("A3OB_MT_object_builder_faces")
        self.layout.menu("A3OB_MT_object_builder_misc")


class A3OB_MT_vertex_groups(bpy.types.Menu):
    """Object Builder utility functions"""

    bl_label = "Utilities"

    def draw(self, context):
        layout = self.layout
        layout.operator("a3ob.find_components", icon='STICKY_UVS_DISABLE')
        layout.operator("a3ob.vertex_group_redefine", icon='FILE_REFRESH')
        layout.operator("a3ob.vertex_groups_cleanup", icon='TRASH')


class A3OB_MT_help(bpy.types.Menu):
    """Object Builder add-on docs"""

    bl_label = "Object Builder"

    def draw(self, context):
        layout = self.layout

        layout.operator("wm.url_open", text="Documentation", icon='HELP').url = "https://mrcmodding.gitbook.io/arma-3-object-builder/home"
        layout.operator("wm.url_open", text="Quick Start Reference", icon='URL').url = "https://mrcmodding.gitbook.io/arma-3-object-builder/quick-start-reference"
        layout.separator()
        layout.operator("wm.url_open", text="Releases", icon='URL').url = "https://github.com/MrClock8163/Arma3ObjectBuilder/releases"
        layout.operator("wm.url_open", text="Issue Tracker", icon='URL').url = "https://github.com/MrClock8163/Arma3ObjectBuilder/issues"
        layout.operator("a3ob.open_changelog", text="Changelog", icon='TEXT')


classes = (
    A3OB_OT_check_convexity,
    A3OB_OT_check_closed,
    A3OB_OT_convex_hull,
    A3OB_OT_component_convex_hull,
    A3OB_OT_find_components,
    A3OB_OT_move_top,
    A3OB_OT_move_bottom,
    A3OB_OT_recalculate_normals,
    A3OB_OT_cleanup_vertex_groups,
    A3OB_OT_redefine_vertex_group,
    A3OB_OT_open_changelog,
    A3OB_MT_object_builder,
    A3OB_MT_object_builder_topo,
    A3OB_MT_object_builder_faces,
    A3OB_MT_object_builder_convexity,
    A3OB_MT_object_builder_misc,
    A3OB_MT_vertex_groups,
    A3OB_MT_help
)


def menu_func(self, context):
    self.layout.separator()
    col = self.layout.column()
    col.ui_units_x = 5.2
    col.menu("A3OB_MT_object_builder", icon_value=utils.get_icon("addon"))


def vertex_groups_func(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.alignment = 'RIGHT'
    row.menu("A3OB_MT_vertex_groups", text="", icon_value=utils.get_icon("addon"))


def menu_help_func(self, context):
    self.layout.separator()
    self.layout.menu("A3OB_MT_help", icon_value=utils.get_icon("addon"))


def register():
    from bpy.utils import register_class
    
    for cls in classes:
        register_class(cls)
    
    bpy.types.VIEW3D_MT_editor_menus.append(menu_func)
    bpy.types.DATA_PT_vertex_groups.append(vertex_groups_func)
    bpy.types.TOPBAR_MT_help.append(menu_help_func)
    
    print("\t" + "UI: Utility functions")


def unregister():
    from bpy.utils import unregister_class

    bpy.types.TOPBAR_MT_help.remove(menu_help_func)
    bpy.types.DATA_PT_vertex_groups.remove(vertex_groups_func)
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_func)

    for cls in reversed(classes):
        unregister_class(cls)
    
    print("\t" + "UI: Utility functions")