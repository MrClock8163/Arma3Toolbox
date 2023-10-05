import bpy
from bpy.app.handlers import persistent

from ..utilities import generic as utils
from ..utilities import outliner as linerutils


class A3OB_UL_outliner_lods(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.operator("a3ob.select_object", text="", icon='VIEWZOOM').object_name = item.name
        row.label(text=item.lod)
        # row.label(text=item.name)


class A3OB_UL_outliner_proxies(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        # row.label(text=item.path, icon='EMPTY_ARROWS')
        # row.label(text=item.name)
        # row.label(text=str(item.index))
        row.operator("a3ob.select_object", text="", icon='VIEWZOOM').object_name = item.name
        row.label(text="%s %d" % (item.path if item.path != "" else "Unknown", item.index))


class A3OB_UL_outliner_sublods(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.operator("a3ob.select_object", text="", icon='VIEWZOOM').object_name = item.name
        row.label(text=item.name)


class A3OB_OT_select_object(bpy.types.Operator):
    """Select object in scene"""
    
    bl_idname = "a3ob.select_object"
    bl_label = "Select Object"
    bl_options = {'UNDO'}
    
    object_name: bpy.props.StringProperty (
        name = "Object Name"
    )
    
    @classmethod
    def poll(cls, context):
        # return cls.object_name in context.scene.objects
        return True
    
    def execute(self, context):
        if self.object_name in context.scene.objects:
        
            bpy.ops.object.select_all(action='DESELECT')
            
            obj = context.scene.objects[self.object_name]
            obj.select_set(True)
            # context.view_layer.objects.selected_objects = [obj]
            context.view_layer.objects.active = obj
        
        return {'FINISHED'}


class A3OB_PT_outliner(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Outliner"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw_header(self, context):
        if not utils.get_addon_preferences().show_info_links:
            return
            
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://mrcmodding.gitbook.io/arma-3-object-builder/tools/proxies"
    
    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.a3ob_outliner
        layout.prop(scene_props, "show_hidden")
        
        layout.template_list("A3OB_UL_outliner_lods", "A3OB_outliner_lods", scene_props, "lods", scene_props, "lods_index")
        
        # if scene_props.lods_index not in range(len(scene_props.lods)):
            # return
        
        # lod_object = context.scene.objects[scene_props.lods[scene_props.lods_index].name]
        
        # layout.label(text=lod_object.name)
        
        
        


class A3OB_PT_outliner_sublods(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Sub-Objects"
    bl_parent_id = "A3OB_PT_outliner"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.a3ob_outliner
        
        layout.template_list("A3OB_UL_outliner_sublods", "A3OB_outliner_sublods", scene_props, "sub_objects", scene_props, "sub_objects_index")


class A3OB_PT_outliner_proxies(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Builder"
    bl_label = "Proxies"
    bl_parent_id = "A3OB_PT_outliner"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.a3ob_outliner
        
        layout.template_list("A3OB_UL_outliner_proxies", "A3OB_outliner_proxy", scene_props, "proxies", scene_props, "proxies_index")
        
        # if scene_props.proxies_index not in range(len(scene_props.proxies)):
            # return
        
        # proxy_props = scene_props.proxies[scene_props.proxies_index]
        
        
        # col = layout.column(align=True)
        # box = col.box()
        # box.label(text=proxy_props.name)
        # col.operator("a3ob.select_object", text="Select").object_name = proxy_props.name
        
        # layout.prop(proxy_props, "proxy_path")
        # layout.prop(proxy_props, "proxy_index")
        

@persistent
def depsgraph_update_post_handler(scene, depsgraph):
    # print("Depsgraph handler", scene, depsgraph)
    
    linerutils.update_outliner(scene)
    

classes = (
    A3OB_UL_outliner_lods,
    A3OB_UL_outliner_proxies,
    A3OB_UL_outliner_sublods,
    A3OB_OT_select_object,
    A3OB_PT_outliner,
    A3OB_PT_outliner_sublods,
    A3OB_PT_outliner_proxies
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post_handler)
    
    print("\t" + "UI: Outliner")


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post_handler)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("\t" + "UI: Outliner")