import os

import bpy

from ..utilities import generic as utils
from ..utilities import lod as lodutils


def update_outliner(scene):
    scene_props = scene.a3ob_outliner
    
    scene_props.lods.clear()

    for obj in [obj for obj in scene.objects if obj.visible_get() or scene_props.show_hidden]:
        if obj.type != 'MESH' or not obj.a3ob_properties_object.is_a3_lod or obj.parent != None:
            continue
        
        item = scene_props.lods.add()
        item.obj = obj.name
        item.name = obj.a3ob_properties_object.get_name()
        item.signature = obj.a3ob_properties_object.get_signature()

        for child in obj.children:
            if child.type != 'MESH':
                continue
                
            if child.a3ob_properties_object_proxy.is_a3_proxy:
                item.proxy_count += 1
            else:
                item.subobject_count += 1


def identify_lod(context):
    obj = context.active_object
    scene_props = context.scene.a3ob_outliner

    if not obj:
        return

    for i, item in enumerate(scene_props.lods):
        if obj.name == item.obj:
            scene_props.lods_index = i
            return
    
    scene_props.lods_index = -1