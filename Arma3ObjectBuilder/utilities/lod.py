import re

import bmesh

from . import generic as utils
from . import data
from . import errors
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
        return "%s %d" % (get_lod_name(index), resolution)
        
    return get_lod_name(index)
    
    
# def is_contiguous_mesh(bm):
    # for edge in bm.edges:
        # if not edge.is_contiguous:
            # return False
            
    # return True
    

# def is_triangulated(bm):
    # for face in bm.faces:
        # if len(face.verts) > 3:
            # return False
            
    # return True


def has_ngons(mesh):
    for face in mesh.polygons:
        if len(face.vertices) > 4:
            return True
    
    return False


# def is_all_sharp(bm):
    # for edge in bm.edges:
        # smooths = [not face.smooth for face in edge.link_faces]
        
        # if sum(smooths) > 0:
            # continue
                    
        # if edge.smooth:
            # return False
    
    # return True

    
class Validator():    
    def __init__(self, obj, warning_errors, lazy = False):
        self.obj = obj
        self.logger = ProcessLogger()
        self.warning_errors = warning_errors
        self.lazy = lazy
    
    @classmethod
    def is_contiguous_mesh(cls, bm):
        for edge in bm.edges:
            if not edge.is_contiguous:
                return False
                
        return True
        
    @classmethod
    def is_triangulated(cls, bm):
        for face in bm.faces:
            if len(face.verts) > 3:
                return False
                
        return True

    @classmethod
    def has_ngons(cls, mesh):
        for face in mesh.polygons:
            if len(face.vertices) > 4:
                return True
        
        return False

    @classmethod
    def is_all_sharp(cls, bm):
        for edge in bm.edges:
            smooths = [not face.smooth for face in edge.link_faces]
            
            if sum(smooths) > 0:
                continue
                        
            if edge.smooth:
                return False
        
        return True
    
    def validate_geometry(self, bm, sub_type = False):
        logger = self.logger
            
        if not self.lazy:
            logger.step("RULESET: Geometry")
            
        count_invalid = 0
        is_valid = True
        try:
            # Closed -> warning
            if not Validator.is_contiguous_mesh(bm):
                if self.warning_errors:
                    if self.lazy:
                        raise errors.LODError("LOD is not contiguous")
                        
                    count_invalid += 1
                    
                logger.step("WARNING: geometry is not contiguous")
            
            # Convexity -> error
            count_concave = 0
            for edge in bm.edges:
                if not edge.is_convex:
                    face1 = edge.link_faces[0]
                    face2 = edge.link_faces[1]
                    dot = face1.normal.dot(face2.normal)
                    
                    if not (0.9999 <= dot and dot <=1.0001):
                        if self.lazy:
                            raise errors.LODError("LOD has concave edge(s)")
                            
                        count_concave += 1
            
            if count_concave > 0:
                logger.step("ERROR: %d concave edge(s)" % count_concave)
                count_invalid += 1
                
            # Component selections -> error
            has_components = False
            for group in self.obj.vertex_groups:
                if re.match("component\d+", group.name, re.IGNORECASE):
                    has_components = True
                    break
            else:
                if self.lazy:
                    raise errors.LODError("LOD has no component selection(s)")
                    
            if not has_components:
                logger.step("ERROR: component selections are not defined")
                count_invalid += 1
                
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
                    if self.lazy:
                        raise errors.LODError("LOD has no vertex masses defined")
                        
                    logger.step("ERROR: vertex masses are not defined")
                    count_invalid += 1
                    
                if has_undefined:
                    if self.warning_errors:
                        count_invalid += 1
                        if self.lazy:
                            raise errors.LODError("LOD has vertices with no vertex mass defined")
                            
                    logger.step("WARNING: vertex mass is not defined for all vertices")
                
            # Triangulated -> warning
            if not Validator.is_triangulated(bm):
                if self.warning_errors:
                    count_invalid += 1
                    if self.lazy:
                        raise errors.LODError("LOD is not triangulated")
                    
                logger.step("WARNING: geometry is not triangulated, convexity is not definite")
            
            # Distance from center -> info
            if not self.lazy:
                max_distance = 0
                for vertex in bm.verts:
                    if vertex.co.length > max_distance:
                        max_distance = vertex.co.length
            
                # bm.free()
                    
                logger.step("INFO: distance of farthest point from origin is %.3f meters" % max_distance)
        
        except errors.LODError:
            count_invalid = 1
        
        finally:
            if count_invalid > 0:
                is_valid = False
        
        return is_valid
    
    def validate_shadow(self, bm):
        logger = self.logger
        
        if not self.lazy:
            logger.step("RULESET: Shadow Volume")
            
        is_valid = True
        count_invalid = 0
        
        try:
            # Contiguous -> error
            if not Validator.is_contiguous_mesh(bm):
                if self.lazy:
                    raise errors.LODError("LOD is not contiguous")
                
                logger.step("ERROR: geometry is not contiguous")
                count_invalid += 1
                
            # Triangulated -> error
            if not Validator.is_triangulated(bm):
                if self.lazy:
                    raise errors.LODError("LOD is not triangulated")
                    
                logger.step("ERROR: geometry is not triangulated")
                is_valid = False
                
            # Materials -> error
            for slot in self.obj.material_slots:
                if slot.material:
                    if self.lazy:
                        raise errors.LODError("LOD has material(s) assigned")
                        
                    logger.step("ERROR: object has material(s) assigned")
                    count_invalid += 1
                    break
            
            # Sharp edges -> error
            if not Validator.is_all_sharp(bm):
                if self.lazy:
                    raise errors.LODError("LOD is has smooth edge(s)")
                    
                logger.step("ERROR: not all edges are sharp")
                count_invalid += 1
        
        except errors.LODError:
            count_invalid = 1
        
        finally:
            if count_invalid > 0:
                is_valid = False
        
        return is_valid
    
    def validate_generic(self, bm):
        logger = self.logger
        
        if not self.lazy:
            logger.step("RULESET: Generic")
            
        is_valid = True
        count_invalid = 0
        
        try:
            ngons = 0
            for face in bm.faces:
                if len(face.verts) > 4:
                    if self.lazy:
                        raise errors.LODError("LOD has n-gon(s)")
                    ngons += 1
            
            if ngons > 0:
                logger.step("ERROR: %d n-gon(s)" % ngons)
                count_invalid += 1
        
        except errors.LODError:
            count_invalid = 1
        
        finally:
            if count_invalid > 0:
                is_valid = False
            
        return is_valid
    
    def validate(self, lod):
        logger = self.logger
        
        if not self.lazy:
            logger.step("Validating %s" % self.obj.name)
            logger.level_up()
        
        bm = bmesh.new()
        if self.obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(self.obj.data)
        else:
            bm.from_mesh(self.obj.data)
        
        count_invalid = 0
        if lod in ('4', '26', '27', '28'):
            if not self.validate_shadow(bm):
                count_invalid += 1
            
        elif lod == '6':
            if not self.validate_geometry(bm):
                count_invalid += 1
            
        elif lod in ('7', '8', '14', '15', '16', '17', '19', '20', '21', '22', '23', '24'):
            if not self.validate_geometry(bm, True):
                count_invalid += 1
        
        if not self.validate_generic(bm):
            count_invalid += 1
        
        bm.free()
        
        if not self.lazy:
            logger.level_down()
            logger.step("Finished validation")
        
        return count_invalid == 0