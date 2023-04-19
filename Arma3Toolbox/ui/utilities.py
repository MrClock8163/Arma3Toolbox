import bpy
from ..utilities import structure as structutils
from ..utilities import generic as utils

# Menus
class A3OB_MT_ObjectBuilder_Topo(bpy.types.Menu):
    '''Object Builder topology functions'''
    
    bl_label = "Topology"
    
    def draw(self,context):
        self.layout.operator(A3OB_OT_CheckClosed.bl_idname)
        self.layout.operator(A3OB_OT_FindComponents.bl_idname)

class A3OB_MT_ObjectBuilder_Convexity(bpy.types.Menu):
    '''Object Builder convexity functions'''
    
    bl_label = "Convexity"
    
    def draw(self,context):
        self.layout.operator(A3OB_OT_CheckConvexity.bl_idname)
        self.layout.operator(A3OB_OT_ConvexHull.bl_idname)
        self.layout.operator(A3OB_OT_ComponentConvexHull.bl_idname)
        
class A3OB_MT_ObjectBuilder_Misc(bpy.types.Menu):
    '''Object Builder miscellaneous functions'''
    
    bl_label = "Misc"
    
    def draw(self,context):
        self.layout.operator(A3OB_OT_CleanupVertexGroups.bl_idname)

class A3OB_MT_ObjectBuilder(bpy.types.Menu):
    '''Arma 3 Object Builder utility functions'''
    
    bl_label = "Object Builder"
    
    def draw(self,context):
        self.layout.menu('A3OB_MT_ObjectBuilder_Topo')
        self.layout.menu('A3OB_MT_ObjectBuilder_Convexity')
        self.layout.menu('A3OB_MT_ObjectBuilder_Misc')

# Operators
class A3OB_OT_CheckConvexity(bpy.types.Operator):
    '''Find concave edges'''
    
    bl_label = "Find Non-Convexities"
    bl_idname = 'a3ob.find_non_convexities'
    
    @classmethod
    def poll(cls,context):
        return len(bpy.context.selected_objects) == 1 and bpy.context.selected_objects[0].type == 'MESH'
    
    def execute(self,context):
        name, concaves = structutils.checkConvexity()
        
        if concaves > 0:
            self.report({'WARNING'},f'{name} has {concaves} concave edges')
            utils.show_infoBox(f'{name} has {concaves} concave edges','Warning','ERROR')
        else:
            self.report({'INFO'},f'{name} is convex')
            utils.show_infoBox(f'{name} is convex','Info','INFO')
        
        return {'FINISHED'}

class A3OB_OT_CheckClosed(bpy.types.Operator):
    '''Find non-closed parts of model'''
    
    bl_label = "Find Non-Closed"
    bl_idname = 'a3ob.find_non_closed'
    
    @classmethod
    def poll(cls,context):
        return len(bpy.context.selected_objects) == 1 and bpy.context.selected_objects[0].type == 'MESH'
    
    def execute(self,context):
        
        structutils.checkClosed()
        
        return {'FINISHED'}

class A3OB_OT_ConvexHull(bpy.types.Operator):
    '''Calculate convex hull for entire object'''
    
    bl_label = "Convex Hull"
    bl_idname = 'a3ob.convex_hull'
    
    @classmethod
    def poll(cls,context):
        return len(bpy.context.selected_objects) == 1 and bpy.context.selected_objects[0].type == 'MESH'
    
    def execute(self,context):
        mode = bpy.context.object.mode
        structutils.convexHull()
        bpy.ops.object.mode_set(mode=mode)
        
        return {'FINISHED'}
    
class A3OB_OT_ComponentConvexHull(bpy.types.Operator):
    '''Create convex named component selections'''
    
    bl_label = "Component Convex Hull"
    bl_idname = 'a3ob.component_convex_hull'
    
    @classmethod
    def poll(cls,context):
        return len(bpy.context.selected_objects) == 1 and bpy.context.selected_objects[0].type == 'MESH'
    
    def execute(self,context):
        mode = bpy.context.object.mode
        structutils.findComponents(True)
        bpy.ops.object.mode_set(mode=mode)
        
        return {'FINISHED'}

class A3OB_OT_FindComponents(bpy.types.Operator):
    '''Create named component selections'''
    
    bl_label = "Find Components"
    bl_idname = 'a3ob.find_components'
    
    @classmethod
    def poll(cls,context):
        return len(bpy.context.selected_objects) == 1 and bpy.context.selected_objects[0].type == 'MESH'
    
    def execute(self,context):
        mode = bpy.context.object.mode
        structutils.findComponents()
        bpy.ops.object.mode_set(mode=mode)
        
        return {'FINISHED'}
        
class A3OB_OT_CleanupVertexGroups(bpy.types.Operator):
    '''Cleanup vertex groups with no vertices assigned'''
    
    bl_label = "Delete Unused Groups"
    bl_idname = 'a3ob.vertex_groups_cleanup'
    
    @classmethod
    def poll(cls,context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and len(obj.vertex_groups) > 0
        
    def execute(self,context):
        obj = context.active_object
        currentMode = obj.mode
        
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        removed = structutils.cleanupVertexGroups(obj)
        bpy.ops.object.mode_set(mode=currentMode)
        
        self.report({'INFO'},f"Removed {removed} unused vertex group(s) from {obj.name}")
        utils.show_infoBox(f"Removed {removed} unused vertex group(s) from {obj.name}","Info",'INFO')
        
        return {'FINISHED'}

class A3OB_OT_RedefineVertexGroup(bpy.types.Operator):
    '''Remove selected vertex group and recreate it with the selected verticies assigned'''

    bl_label = "Redefine Vertex Group"
    bl_idname = 'a3ob.vertex_group_redefine'
    
    @classmethod
    def poll(cls,context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.vertex_groups.active and obj.mode == 'EDIT'
        
    def execute(self,context):
        obj = context.active_object
        structutils.redefineVertexGroup(obj)
        
        return {'FINISHED'}

classes = (
    A3OB_OT_CheckConvexity,
    A3OB_OT_CheckClosed,
    A3OB_OT_ConvexHull,
    A3OB_OT_ComponentConvexHull,
    A3OB_OT_FindComponents,
    A3OB_OT_CleanupVertexGroups,
    A3OB_OT_RedefineVertexGroup,
    A3OB_MT_ObjectBuilder,
    A3OB_MT_ObjectBuilder_Topo,
    A3OB_MT_ObjectBuilder_Convexity,
    A3OB_MT_ObjectBuilder_Misc
)

def menu_func(self,context):
    self.layout.separator()
    self.layout.menu('A3OB_MT_ObjectBuilder')
    
def vertex_groups_func(self,context):
    layout = self.layout
    row = layout.row(align=True)
    row.alignment = 'RIGHT'
    row.operator(A3OB_OT_FindComponents.bl_idname,icon='STICKY_UVS_DISABLE',text="")
    row.operator(A3OB_OT_RedefineVertexGroup.bl_idname,icon='PASTEDOWN',text="")
    row.operator(A3OB_OT_CleanupVertexGroups.bl_idname,icon='TRASH',text="")

def register():
    from bpy.utils import register_class
    
    for cls in classes:
        register_class(cls)
    
    bpy.types.VIEW3D_MT_editor_menus.append(menu_func)
    bpy.types.DATA_PT_vertex_groups.append(vertex_groups_func)

def unregister():
    from bpy.utils import unregister_class
            
    bpy.types.DATA_PT_vertex_groups.remove(vertex_groups_func)
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_func)

    for cls in reversed(classes):
        unregister_class(cls)