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
    
    ruleset = "Base"
    def conditions(self):
        errs = tuple()
        warns = tuple()
        info = tuple()

        return errs, warns, info
    
    def validate_lazy(self, warns_errs):
        errs, warns, _ = self.conditions()

        for item in errs:
            success, _ = item()
            if not success:
                return False
        
        if warns_errs:
            for item in warns:
                success, _ = item()
                if not success:
                    return False
        
        return True

    def validate_verbose(self, warns_errs):
        errs, warns, info = self.conditions()
        is_valid = True
        self.logger.level_up()

        for item in errs:
            success, comment = item()
            if not success:
                self.logger.step("ERROR: %s" % comment)
                is_valid = False
        
        for item in warns:
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
        errs = (
            self.no_ngons,
        )
        warns = info = tuple()

        return errs, warns, info


class ValidatorGeometry(ValidatorComponent):
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
        result = True, ""

        if len(self.obj.data.vertices) == 0:
            return result
        
        re_component = re.compile("component\d+", re.IGNORECASE)
        for group in self.obj.vertex_groups:
            if re_component.match(group.name):
                break
        else:
            result = False, "mesh has no component selections"
        
        return result
    
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
        errs = (
            self.is_contiguous,
            self.is_convex,
            self.has_components,
            self.has_mass
        )
        warns = (
            self.is_triangulated,
        )
        info = (
            self.farthest_point,
        )

        return errs, warns, info


class ValidatorGeometrySubtype(ValidatorGeometry):
    ruleset = "Geometry subtype"
    def conditions(self):
        errs = (
            self.is_contiguous,
            self.is_convex,
            self.has_components
        )
        warns = (
            self.is_triangulated,
        )
        info = tuple()

        return errs, warns, info
    

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
        errs = (
            self.is_contiguous,
            self.is_triangulated,
            self.is_sharp,
            self.no_materials
        )
        warns = info = tuple()

        return errs, warns, info


class Validator():
    def __init__(self, logger):
        self.logger = logger
    
    def validate(self, obj, lod, lazy = False, warns_errs = True):
        obj.update_from_editmode()
        bm = bmesh.new()
        bm.from_object(obj, bpy.context.evaluated_depsgraph_get())
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        steps = [
            ValidatorGeneric
        ]

        if lod in ('4', '26', '27', '28'):
            steps.append(ValidatorShadow)
        elif lod == '6':
            steps.append(ValidatorGeometry)
        elif lod in ('7', '8', '14', '15', '16', '17', '19', '20', '21', '22', '23', '24'):
            steps.append(ValidatorGeometrySubtype)
        
        is_valid = True
        for item in steps:
            is_valid &= item(obj, bm, self.logger).validate(lazy, warns_errs)

        bm.free()

        return is_valid