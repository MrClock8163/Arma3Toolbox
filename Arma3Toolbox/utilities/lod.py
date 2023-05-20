import re

import bmesh

from . import generic as utils
from . import data
from .logger import ProcessLogger


def get_lod_id(value):
    fraction, exponent = utils.normalize_float(value)

    if exponent < 3: # Escape at resolutions
        return 0, round(value)

    base_value = utils.floor(fraction)

    if exponent in [3, 16]: # LODs in these ranges have identifier values in the X.X positions not just X.0
        base_value = utils.floor(fraction, 1)

    index = data.lod_type_index.get((base_value, exponent), 30)
    resolution_position = data.lod_resolution_position.get(index, None)
    
    resolution = 0
    if resolution_position is not None:
        resolution = int(round((fraction - base_value) * 10**resolution_position, resolution_position))

    return index, resolution


def get_lod_signature(index, resolution):    
    if index == 0:
        return resolution
    
    index = list(data.lod_type_index.values()).index(index, 0)
    fraction, exponent = list(data.lod_type_index.keys())[index]
    
    resolution_position = data.lod_resolution_position.get(index, None)
    resolution_signature = 0
    if resolution_position is not None:
        resolution_signature = resolution * 10**(exponent - resolution_position)
    
    return fraction * 10**exponent + resolution_signature


def get_lod_name(index):
    return data.lod_type_names.get(index,data.lod_type_names[30])[0]


def format_lod_name(index, resolution):
    if data.lod_resolution_position.get(index, None) is not None:
        return f"{get_lod_name(index)} {resolution}"
        
    return get_lod_name(index)
    
    
def is_contiguous_mesh(bm):
    for edge in bm.edges:
        if not edge.is_contiguous:
            return False
            
    return True
    

def is_triangulated(bm):
    for face in bm.faces:
        if len(face.verts) > 3:
            return False
            
    return True

    
def validate_lod(obj, wm_props):
    is_valid = False
    
    if wm_props.lod in ('4', '26', '27', '28'):
        is_valid = validate_shadow(obj, wm_props)
        
    elif wm_props.lod == '6':
        is_valid = validate_geometry(obj, wm_props)
        
    elif wm_props.lod in ('7', '8', '14', '15', '16', '17', '19', '20', '21', '22', '23', '24'):
        is_valid = validate_geometry(obj, wm_props, True)
        
    return is_valid
    
    
def validate_geometry(obj, wm_props, sub_type = False):
    logger = ProcessLogger()
    logger.step(f"Validating {obj.name} as Geometry")
    logger.level_up()
    is_valid = True
    
    bm = bmesh.new()
    if obj.mode == 'EDIT':
        bm.from_edit_mesh(obj.data)
    else:
        bm.from_mesh(obj.data)
    
    # Closed -> error
    if not is_contiguous_mesh(bm):
        logger.step("ERROR: geometry is not contiguous")
        is_valid = False
    
    # Convexity -> error
    count_concave = 0
    for edge in bm.edges:
        if not edge.is_convex:
            face1 = edge.link_faces[0]
            face2 = edge.link_faces[1]
            dot = face1.normal.dot(face2.normal)
            
            if not (0.9999 <= dot and dot <=1.0001):
                count_concave += 1
                is_valid = False
    
    if count_concave > 0:
        logger.step(f"ERROR: {count_concave} concave edge(s)")
        is_valid = False
        
    # Component selections -> error
    has_components = False
    for group in obj.vertex_groups:
        if re.match("component\d+", group.name, re.IGNORECASE):
            has_components = True
            break
            
    if not has_components:
        logger.step("ERROR: component selections are not defined")
        is_valid = False
        
    # Mass -> error, warning
    if not sub_type:
        layer = bm.verts.layers.float.get("a3ob_mass")
        
        mass = 0
        has_undefined = False
        if layer:
            for vertex in bm.verts:
                vertex_mass = vertex[layer]
                if vertex_mass < 0.001:
                    has_undefined = True
                mass += vertex_mass
            
        if mass < 0.001:
            logger.step("ERROR: vertex masses are not defined")
            is_valid = False
            
        if has_undefined:
            logger.step("WARNING: vertex mass is not defined for all vertices")
            if wm_props.warning_errors:
                is_valid = False
        
    # Triangulated -> warning
    if not is_triangulated(bm):
        logger.step("WARNING: geometry is not triangulated, convexity is not definite")
        if wm_props.warning_errors:
            is_valid = False
    
    # Distance from center -> info
    max_distance = 0
    for vertex in bm.verts:
        if vertex.co.length > max_distance:
            max_distance = vertex.co.length
            
    logger.step("INFO: distance of farthest point from origin is %.3f meters" % max_distance)
    
    logger.step("RESULT: validation %s" % ("succeeded" if is_valid else "failed"))
        
    logger.level_down()
    logger.step("Finished validation")
    
    return is_valid

    
def validate_shadow(obj, wm_props):
    logger = ProcessLogger()
    logger.step(f"Validating {obj.name} as Shadow Volume")
    logger.level_up()
    is_valid = True
    
    bm = bmesh.new()
    if obj.mode == 'EDIT':
        bm.from_edit_mesh(obj.data)
    else:
        bm.from_mesh(obj.data)
    
    # Contiguous -> error
    if not is_contiguous_mesh(bm):
        logger.step("ERROR: geometry is not contiguous")
        is_valid = False
        
    # Triangulated -> error
    if not is_triangulated(bm):
        logger.step("ERROR: geometry is not triangulated")
        is_valid = False
        
    # Materials -> error
    for slot in obj.material_slots:
        if slot.material:
            logger.step("ERROR: object has material(s) assigned")
            is_valid = False
            break
    
    # Sharp edges -> error
    for edge in bm.edges:
        smooths = [not face.smooth for face in edge.link_faces]
        
        if sum(smooths) > 0:
            continue
                    
        if edge.smooth:
            logger.step("ERROR: not all edges are sharp")
            is_valid = False
            break
    
    logger.level_down()
    logger.step("Finished validation")
    
    return is_valid