import math
import re

import bpy
import bmesh
import mathutils

from . import structure as structutils
from . import lod as lodutils
from .logger import ProcessLogger
from ..io import import_p3d


lod_conversion = {
    '-1.0': '0',
    '1.000e+3': '1',
    '1.200e+3': '3',
    '1.100e+3': '2',
    '1.000e+4': '4',
    '1.001e+4': '4',
    '1.100e+4': '4',
    '1.101e+4': '4',
    '1.000e+13': '6',
    '1.000e+15': '9',
    '2.000e+15': '10',
    '3.000e+15': '11',
    '4.000e+15': '12',
    '5.000e+15': '13',
    '6.000e+15': '14',
    '7.000e+15': '15',
    '8.000e+15': '16',
    '9.000e+15': '17',
    '1.000e+16': '18',
    '1.100e+16': '19',
    '1.200e+16': '20',
    '1.300e+16': '21',
    '1.400e+16': '22',
    '1.500e+16': '23',
    '1.600e+16': '24',
    '1.700e+16': '25',
    '1.800e+16': '26',
    '1.900e+16': '27',
    '2.000e+16': '28',
    '2.100e+16': '29',
    '2.000e+13': '7',
    '4.000e+13': '8',
    '2.000e+4': '5'
}


def convert_materials_item(material, cleanup):
    atbx_props = material.armaMatProps
    a3ob_props = material.a3ob_properties_material
    
    texture_type = atbx_props.texType
    
    if texture_type == 'Texture':
        a3ob_props.texture_type = 'TEX'
        a3ob_props.texture_path = atbx_props.texture
    elif texture_type == 'Color':
        a3ob_props.texture_type = 'COLOR'
        try:
            a3ob_props.color_type = a3ob_props.colorType
        except:
            pass
        
        a3ob_props.color_value = (*a3ob_props.colorValue, 1.0)
    elif texture_type == 'Custom':
        a3ob_props.texture_type = 'CUSTOM'
        a3ob_props.color_raw = atbx_props.colorString
        
    a3ob_props.material_path = atbx_props.rvMat
    
    if cleanup:
        atbx_props.texType = 'Texture'
        atbx_props.texture = ""
        atbx_props.colorString = ""
        a3ob_props.colorValue = (1.0, 1.0, 1.0)
        atbx_props.rvMat = ""


def convert_materials(obj, converted_materials, cleanup, logger):
    count = 0
    for slot in obj.material_slots:
        mat = slot.material
        if not mat or mat and mat.name in converted_materials:
            continue
        
        converted_materials.add(mat.name)        
        convert_materials_item(mat, cleanup)
        count += 1
        
    if count > 0:
        logger.step("Materials: %s" % count)
    
    return converted_materials


def convert_proxy_item(obj, selections, dynamic_naming, cleanup):
    import_p3d.transform_proxy(obj)
    structutils.cleanup_vertex_groups(obj)
    a3ob_props = obj.a3ob_properties_object_proxy
    atbx_props = obj.armaObjProps
    
    a3ob_props.dynamic_naming = dynamic_naming
    atbx_props.isArmaObject = False
    atbx_props.namedProps.clear()
    
    for group in obj.vertex_groups:
        if not group.name in selections:
            continue
        
        proxy_data = selections[group.name]
        a3ob_props.proxy_path = proxy_data[0]
        a3ob_props.proxy_index = proxy_data[1]
        
        if cleanup:
            obj.vertex_groups.remove(group)
            
    a3ob_props.is_a3_proxy = True


def convert_proxies(obj, dynamic_naming, cleanup, logger):
    regex_proxy_placeholder = "@@armaproxy(\.\d+)?"
    proxy_selections = {proxy.name: (proxy.path, proxy.index) for proxy in obj.armaObjProps.proxyArray}
    if cleanup:
        obj.armaObjProps.proxyArray.clear()
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    for group in obj.vertex_groups:
        selection = group.name
        if not re.match(regex_proxy_placeholder, selection):
            continue
            
        obj.vertex_groups.active = group
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.separate(type='SELECTED')
        obj.vertex_groups.remove(group)
        
    bpy.ops.object.mode_set(mode='OBJECT')
    
    proxy_objects = [proxy for proxy in bpy.context.selected_objects if proxy != obj]
    
    for proxy in proxy_objects:
        proxy.parent = obj
        convert_proxy_item(proxy, proxy_selections, dynamic_naming, cleanup)
        
    bpy.ops.object.select_all(action='DESELECT')
    
    if len(proxy_objects) > 0:
        logger.step("Proxies: %s" % len(proxy_objects))


def convert_namedprops(a3ob_props, atbx_props, logger):
    count = 0
    for namedprop in atbx_props.namedProps:
        new_item = a3ob_props.properties.add()
        new_item.name = namedprop.name
        new_item.value = namedprop.value
        count += 1
        
    if count > 0:
        logger.step("Named properties: %d" % count)


def convert_lod_properties(obj, dynamic_naming, cleanup, logger):
    a3ob_props = obj.a3ob_properties_object
    atbx_props = obj.armaObjProps
    a3ob_props.dynamic_naming = dynamic_naming
    
    try:
        a3ob_props.lod = lod_conversion[atbx_props.lod]
    except:
        a3ob_props.lod = '30'
        
    a3ob_props.resolution = math.floor(atbx_props.lodDistance)
    a3ob_props.is_a3_lod = True
    
    logger.step("LOD name: %s" % lodutils.format_lod_name(int(a3ob_props.lod), a3ob_props.resolution))
    
    convert_namedprops(a3ob_props, atbx_props, logger)
    
    if cleanup:
        atbx_props.isArmaObject = False
        atbx_props.lod = '-1.0'
        atbx_props.lodDistance = 1.0
        atbx_props.namedProps.clear()


def convert_vertex_masses(obj, cleanup, logger):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    layer_atbx = bm.verts.layers.float.get("FHQWeights")
    if layer_atbx:
        layer_a3ob = bm.verts.layers.float.get("a3ob_mass")
        if not layer_a3ob:
            layer_a3ob = bm.verts.layers.float.new("a3ob_mass")
            
        for vertex in bm.verts:
            vertex[layer_a3ob] = vertex[layer_atbx]
            
        if cleanup:
            bm.verts.layers.float.remove(layer_atbx)
            
        logger.step("Vertex masses")
    
    bm.to_mesh(obj.data)
    bm.free()


def convert_mesh(obj, converted_materials, dynamic_naming, cleanup, logger):
    converted_materials = convert_materials(obj, converted_materials, cleanup, logger)        
    convert_proxies(obj, dynamic_naming, cleanup, logger)
    convert_lod_properties(obj, dynamic_naming, cleanup, logger)
    convert_vertex_masses(obj, cleanup, logger)


def convert_motion(obj, cleanup, logger):
    if obj.armaObjProps.centerBone == "":
        obj.a3ob_properties_object_armature.motion_source = 'MANUAL'
    else:
        obj.a3ob_properties_object_armature.motion_source = 'CALCULATED'
        
    obj.a3ob_properties_object_armature.motion_bone = obj.armaObjProps.centerBone
    obj.a3ob_properties_object_armature.motion_vector = obj.armaObjProps.motionVector
    
    if cleanup:
        obj.armaObjProps.motionVector = (0, 0, 0)
        obj.armaObjProps.centerBone = ""
        
    logger.step("Motion vector")


def convert_frames(obj, cleanup, logger):
    frames = [frame.timeIndex for frame in obj.armaObjProps.keyFrames]
    frames.sort()
    
    object_props = obj.a3ob_properties_object_armature
    for index in frames:
        item = object_props.frames.add()
        item.index = index
        
    if cleanup:
        obj.armaObjProps.keyFrames.clear()
        
    logger.step("Frames: %d" % len(frames))


def convert_armature(obj, cleanup, logger):
    convert_motion(obj, cleanup, logger)
    convert_frames(obj, cleanup, logger)
    
    if cleanup:
        obj.armaObjProps.isArmaObject = False


def convert_dtm(obj, cleanup, logger):
    atbx_props = obj.armaHFProps
    a3ob_props = obj.a3ob_properties_object_dtm
    
    a3ob_props.cellsize_source = 'MANUAL'
    a3ob_props.cellsize = atbx_props.cellSize
    a3ob_props.origin = 'CORNER'
    a3ob_props.easting = atbx_props.easting
    a3ob_props.northing = atbx_props.northing
    a3ob_props.nodata = atbx_props.undefVal
    
    if cleanup:
        atbx_props.cellSize = 4
        atbx_props.easting = 0
        atbx_props.northing = 200_000
        atbx_props.undefVal = -9999
        atbx_props.isHeightfield = False


def convert_objects_item(obj, object_type, converted_materials, dynamic_naming, cleanup, logger):
    logger.level_up()
    
    if object_type == 'LOD':
        convert_materials = convert_mesh(obj, converted_materials, dynamic_naming, cleanup, logger)
    elif object_type == 'ARMATURE':
        convert_armature(obj, cleanup, logger)
    elif object_type == 'DTM':
        convert_dtm(obj, cleanup, logger)
        
    logger.level_down()
        
    return converted_materials


def convert_objects(objects, dynamic_naming, cleanup):
    logger = ProcessLogger()
    logger.step("Converting ATBX setup to A3OB")
    logger.level_up()
    categories = ('LOD', 'DTM', 'ARMATURE')
    
    converted_materials = set()
    for i, category in enumerate(objects):
        logger.step("Category: %s" % categories[i])
        logger.level_up()
        
        for obj in category:
            logger.step(str(obj.name))
            converted_materials = convert_objects_item(obj, categories[i], converted_materials, dynamic_naming, cleanup, logger)
            logger.step("")
            
        logger.level_down()
    
    logger.level_down()
    logger.step("Conversion finished")