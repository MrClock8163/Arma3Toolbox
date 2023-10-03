import bpy
from bpy.app.handlers import persistent

from ..utilities import generic as utils
from ..utilities import outliner as linerutils


class A3OB_UL_outliner_lods(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.label(text=item.lod, icon='MESH_CUBE')
        row.label(text=item.name)


class A3OB_UL_outliner_proxies(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        # row.label(text=item.path, icon='EMPTY_ARROWS')
        # row.label(text=item.name)
        # row.label(text=str(item.index))
        row.label(text="%s %d" % (item.path if item.path != "" else "Unknown", item.index), icon='EMPTY_ARROWS')


class A3OB_UL_outliner_sublods(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.label(text=item.name, icon='MESH_PLANE')


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
        layout.template_list("A3OB_UL_outliner_lods", "A3OB_outliner_lods", scene_props, "lods", scene_props, "lods_index")
        
        # if scene_props.lods_index not in range(len(scene_props.lods)):
            # return
        
        # lod_props = scene_props.lods[scene_props.lods_index]
        
        layout.template_list("A3OB_UL_outliner_sublods", "A3OB_outliner_sublods", scene_props, "sub_objects", scene_props, "sub_objects_index")
        layout.template_list("A3OB_UL_outliner_proxies", "A3OB_outliner_proxy", scene_props, "proxies", scene_props, "proxies_index")


@persistent
def depsgraph_update_post_handler(scene, depsgraph):
    print("Depsgraph handler", scene, depsgraph)
    
    linerutils.update_outliner(scene)
    

classes = (
    A3OB_UL_outliner_lods,
    A3OB_UL_outliner_proxies,
    A3OB_UL_outliner_sublods,
    A3OB_PT_outliner
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