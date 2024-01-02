import re
import math

import bmesh
import bpy


class ValidatorComponent():
    def __init__(self, obj, bm, logger):
        self.obj = obj
        self.bm = bm
        self.logger = logger

    def is_contiguous(self):
        result = True, ""

        for edge in self.bm.edges:
            if not edge.is_contiguous:
                result = False, "mesh is not contiguous"
                break
            
        return result

    def is_triangulated(self):
        result = True, ""

        for face in self.bm.faces:
            if len(face.verts) > 3:
                result = False, "mesh is not triangulated"
                break
                
        return result

    def no_ngons(self):
        result = True, ""

        for face in self.bm.faces:
            if len(face.verts) > 4:
                result = False, "mesh has n-gons"
                break
        
        return result

    def has_selection_internal(self, re_selection):
        if len(self.bm.verts) == 0:
            return False
        
        RE_NAME = re.compile(re_selection, re.IGNORECASE)
        groups = [group.index for group in self.obj.vertex_groups if RE_NAME.match(group.name)]
        
        if len(groups) == 0:
            return False
        
        layer = self.bm.verts.layers.deform.verify()
        for vert in self.bm.verts:
            for group in groups:
                if group in vert[layer] and vert[layer][group] == 1:
                    return True
        else:
            return False
    
    ruleset = "Base"
    def conditions(self):
        strict = tuple()
        optional = tuple()
        info = tuple()

        return strict, optional, info
    
    def validate_lazy(self, warns_errs):
        strict, optional, _ = self.conditions()

        for item in strict:
            success, _ = item()
            if not success:
                return False
        
        if warns_errs:
            for item in optional:
                success, _ = item()
                if not success:
                    return False
        
        return True

    def validate_verbose(self, warns_errs):
        strict, optional, info = self.conditions()
        is_valid = True
        self.logger.level_up()

        for item in strict:
            success, comment = item()
            if not success:
                self.logger.step("ERROR: %s" % comment)
                is_valid = False
        
        for item in optional:
            success, comment = item()
            if not success:
                self.logger.step("WARNING: %s" % comment)
                is_valid &= not warns_errs
        
        for item in info:
            _, comment = item()
            self.logger.step("INFO: %s" % comment)

        self.logger.level_down()

        return is_valid

    
    def validate(self, lazy, warns_errs):
        is_valid = True

        if lazy:
            is_valid = self.validate_lazy(warns_errs)
        else:
            self.logger.step("RULESET: %s" % self.ruleset)
            is_valid = self.validate_verbose(warns_errs)

        return is_valid


class ValidatorGeneric(ValidatorComponent):
    ruleset = "Generic"
    def conditions(self):
        strict = (
            self.no_ngons,
        )
        optional = info = tuple()

        return strict, optional, info


class ValidatorGeometry(ValidatorComponent):
    def is_triangulated(self):
        result =  super().is_triangulated()
        if not result[0]:
            result = False, "mesh is not triangulated (convexity is not definite)"
        
        return result
    
    def is_convex_edge(self, edge):
        if edge.is_convex:
            return True
        
        face1 = edge.link_faces[0]
        face2 = edge.link_faces[1]
        dot = face1.normal.dot(face2.normal)

        if not (0.9999 <= dot <= 1.0001):
            return False
        
        return True

    def is_convex(self):
        result = True, ""

        for edge in self.bm.edges:
            if not self.is_convex_edge(edge):
                result = False, "mesh is not convex"
                break
        
        return result
    
    def has_components(self):
        if not self.has_selection_internal("component\d+"):
            return False, "mesh has no component selections"
        
        return True, ""
    
    def has_mass(self):
        result = True, ""

        layer = self.bm.verts.layers.float.get("a3ob_mass")
        if not layer or math.fsum([vert[layer] for vert in self.bm.verts]) < 0.001:
            return False, "mesh has no vertex mass assigned"

        return result
    
    def no_unweighted(self):
        result = True, ""

        layer = self.bm.verts.layers.float.get("a3ob_mass")
        if not layer:
            return False, "mesh has vertices with no vertex mass assigned"
        
        for vert in self.bm.verts:
            if vert[layer] < 0.001:
                return False, "mesh has vertices with no vertex mass assigned"
        
        return result

    def farthest_point(self):
        distance = 0
        for vertex in self.bm.verts:
            if vertex.co.length > distance:
                distance = vertex.co.length
        
        return True, "distance of farthest point from origin is %.3f meters" % distance

    ruleset = "Geometry"
    def conditions(self):
        strict = (
            self.is_convex,
            self.has_mass
        )
        if not self.has_selection_internal("occluder\d+"):
            strict = (
                self.is_contiguous,
                self.has_components,
                *strict
            )
        optional = (
            self.is_triangulated,
            self.no_unweighted
        )
        info = (
            self.farthest_point,
        )

        return strict, optional, info


class ValidatorGeometrySubtype(ValidatorGeometry):
    ruleset = "Geometry subtype"
    def conditions(self):
        strict = (
            self.is_convex,
        )
        if not self.has_selection_internal("occluder\d+"):
            strict = (
                self.is_contiguous,
                self.has_components,
                *strict
            )
        optional = (
            self.is_triangulated,
        )
        info = tuple()

        return strict, optional, info
    

class ValidatorShadow(ValidatorComponent):
    def is_sharp(self):
        result = True, ""

        for face in self.bm.faces:
            if face.smooth:
                break
        else:
            return result

        for edge in self.bm.edges:
            if edge.smooth and edge.is_manifold:
                result = False, "mesh has smooth edges"
                break
        
        return result
    
    def no_materials(self):
        result = True, ""

        materials = {}
        for i, slot in enumerate(self.obj.material_slots):
            mat = slot.material
            if not mat:
                materials[i] = ("", "")
                continue

            materials[i] = mat.a3ob_properties_material.to_p3d()
        
        if len(materials) > 0:
            for face in self.bm.faces:
                if materials[face.material_index] != ("", ""):
                    result = False, "mesh has materials assigned"
                    break
            
        return result
    
    ruleset = "Shadow"
    def conditions(self):
        strict = (
            self.is_contiguous,
            self.is_triangulated,
            self.is_sharp,
            self.no_materials
        )
        optional = info = tuple()

        return strict, optional, info


class ValidatorPointcloud(ValidatorComponent):
    def no_edges(self):
        result = True, ""

        if len(self.bm.edges) > 0:
            result = False, "point cloud contains edges"

        return result
    
    def no_faces(self):
        result = True, ""

        if len(self.bm.faces) > 0:
            result = False, "point cloud contains faces"
        
        return result
    
    ruleset = "Point cloud"
    def conditions(self):
        strict = info = tuple()
        optional = (
            self.no_edges,
            self.no_faces
        )

        return strict, optional, info


class ValidatorRoadway(ValidatorComponent):
    def under_limit(self):
        result = True, ""

        if len(self.bm.verts) > 255:
            result = False, "mesh has more than 255 points (animations will not work properly)"

        return result
    
    def has_faces(self):
        result = True, ""

        if len(self.bm.faces) == 0:
            result = False, "mesh has no faces"

        return result

    def has_sound(self):
        result = True, ""

        textures = {}
        for i, slot in enumerate(self.obj.material_slots):
            mat = slot.material
            if not mat:
                textures[i] = ""
                continue
                
            textures[i] = mat.a3ob_properties_material.to_p3d()[0]
        
        if len(textures) == 0:
            result = False, "mesh has no sound textures assigned"
        else:
            for face in self.bm.faces:
                if textures[face.material_index] == "":
                    result = False, "mesh has faces with no sound texture assigned"
                    break

        return result

    def farthest_point(self):
        distance = 0
        for vertex in self.bm.verts:
            if vertex.co.length > distance:
                distance = vertex.co.length
        
        return True, "distance of farthest point from origin is %.3f meters" % distance
    
    ruleset = "Roadway"
    def conditions(self):
        strict = (
            self.has_faces,
        )
        optional = (
            self.under_limit,
            self.has_sound
        )
        info = (
            self.farthest_point,
        )

        return strict, optional, info


class ValidatorPaths(ValidatorComponent):
    def has_faces(self):
        result = True, ""

        if len(self.bm.faces) == 0:
            result = False, "mesh has no faces"

        return result
    
    def has_entry(self):
        if not self.has_selection_internal("in\d+"):
            return False, "mesh has no entry points assigned"
        
        return True, ""
    
    def has_position(self):
        if not self.has_selection_internal("in\d+"):
            return False, "mesh has no position points assigned"
        
        return True, ""

    ruleset = "Paths"
    def conditions(self):
        strict = (
            self.has_faces,
            self.has_entry,
        )
        optional = (
            self.has_position,
        )
        info = tuple()

        return strict, optional, info


class Validator():
    def __init__(self, logger):
        self.logger = logger
        self.components = {
            **dict.fromkeys(('4', '26', '27', '28'), [ValidatorShadow]),
            **dict.fromkeys(('9', '10', '13'), [ValidatorPointcloud]),
            **dict.fromkeys(('7', '8', '14', '15', '16', '17', '19', '20', '21', '22', '23', '24'), [ValidatorGeometrySubtype]),
            '6': [ValidatorGeometry],
            '11': [ValidatorRoadway],
            '12': [ValidatorPaths]
        }
    
    def validate(self, obj, lod, lazy = False, warns_errs = True):
        self.logger.step("Validating %s" % obj.name)
        self.logger.level_up()
        if warns_errs:
            self.logger.step("Warnings are errors")

        obj.update_from_editmode()
        bm = bmesh.new()
        bm.from_object(obj, bpy.context.evaluated_depsgraph_get())
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        is_valid = True
        for item in [ValidatorGeneric] + self.components.get(lod, []):
            is_valid &= item(obj, bm, self.logger).validate(lazy, warns_errs)

        bm.free()
        self.logger.level_down()
        self.logger.step("Finished validation")

        return is_valid