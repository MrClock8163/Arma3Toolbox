import os
import tempfile
import subprocess

import bpy
import bmesh

from ..utilities import generic as utils
from ..io import import_rap as rap


class Bone():
    def __init__(self):
        self.name = ""
        self.parent = ""
    
    def __eq__(self, other):
        return isinstance(other, Bone) and self.name.lower() == other.name.lower()
    
    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return "\"%s\"" % self.name


def cfgconvert(filepath, exepath):
    current_dir = os.getcwd()
    
    if os.path.exists("P:\\"):
        os.chdir("P:\\")
    
    destfile = tempfile.NamedTemporaryFile(mode="w+b", prefix="mcfg_", delete=False)
    destfile.close()
    
    try:
        results = subprocess.run([exepath, "-bin", "-dst", destfile.name, filepath], capture_output=True)
        results.check_returncode()
    except:
        os.chdir(current_dir)
        os.remove(destfile.name)
        return ""
        
    os.chdir(current_dir)
    
    return destfile.name

def read_mcfg(filepath, exepath):
    temppath = cfgconvert(filepath, exepath)
    
    if temppath == "":
        return None
    
    data = rap.CFGReader.derapify(temppath)
    
    os.remove(temppath)
    
    return data


def get_prop_compiled(mcfg, classname, propname):
    entry = mcfg.body.find(classname)
    if not entry or entry.type != rap.Cfg.EntryType.CLASS:
        return None
    
    prop = entry.body.find(propname)
    if prop:
        return prop.value
    
    if entry.body.inherits == "":
        return None
        
    return get_prop_compiled(mcfg, entry.body.inherits, propname)


def get_bones_compiled(mcfg, skeleton_name):
    cfg_skeletons = mcfg.body.find("CfgSkeletons")
    output = []
    
    if not cfg_skeletons or cfg_skeletons.type != rap.Cfg.EntryType.CLASS:
        return []
        
    skeleton = cfg_skeletons.body.find(skeleton_name)
    if not skeleton or skeleton.type != rap.Cfg.EntryType.CLASS:
        return []
    
    inherit_bones = get_prop_compiled(cfg_skeletons, skeleton_name, "skeletonInherit")
    if not inherit_bones:
        inherit_bones = ""
    
    bones_self = get_bones(skeleton)
    bones_inherit = []
    
    if not skeleton.body.find("skeletonBones") and skeleton.body.inherits != "":
        parent = cfg_skeletons.body.find(skeleton.body.inherits)
        if parent:
            bones_self = get_bones(parent)
        
    if inherit_bones != "":
        bones_inherit = get_bones_compiled(mcfg, inherit_bones)
    
    output = bones_self + bones_inherit
        
    return list(set(output))


def get_bones(skeleton):
    if skeleton.type == rap.Cfg.EntryType.EXTERN:
        return []
    
    bones = skeleton.body.find("skeletonBones")
    if not bones:
        return []

    output = []
    for i in range(0, bones.body.element_count, 2):
        new_bone = Bone()
        new_bone.name = bones.body.elements[i].value
        new_bone.parent = bones.body.elements[i + 1].value
        output.append(new_bone)
        
    return output
    

def get_skeletons(mcfg):
    skeletons = mcfg.body.find("CfgSkeletons")
    if skeletons:
        return skeletons.body.entries
    
    return []


def get_bone_group_indices(obj, cfgbones):
    cfgbones_names = [item.name.lower() for item in cfgbones]    
    return [group.index for group in obj.vertex_groups if group.name.lower() in cfgbones_names]


def select_vertices_unnormalized(obj, bone_indices):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    deform = bm.verts.layers.deform.active
    
    if deform:
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            weights = 0
            for key in vert[deform].keys():
                if key not in bone_indices:
                    continue
                
                weights += vert[deform][key]
            
            vert.select_set(abs(weights-1) > 0.01)
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def normalize_weights(obj, bone_indices):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    deform = bm.verts.layers.deform.active
    
    normalized = 0
    
    if deform:
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            weights = 0
            for key in vert[deform].keys():
                if key not in bone_indices:
                    continue
                
                weights += vert[deform][key]
                
            if abs(weights-1) > 0.01:
                normalized += 1
            
            for key in vert[deform].keys():
                if key not in bone_indices:
                    continue
                
                vert[deform][key] /= weights
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
    
    return normalized


def select_vertices_overdetermined(obj, bone_indices):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    deform = bm.verts.layers.deform.active
    
    if deform:
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            bones = 0
            for key in vert[deform].keys():
                if key not in bone_indices:
                    continue
                
                bones += 1
            
            vert.select_set(bones > 3)
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


def prune_overdetermined(obj, bone_indices):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    deform = bm.verts.layers.deform.active
    
    pruned = 0
    
    if deform:
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            bones = []
            sections = []
            for key in vert[deform].keys():
                if key not in bone_indices:
                    sections.append((key, vert[deform][key]))
                    continue
                
                bones.append((key, vert[deform][key]))
            
            if len(bones) <= 3:
                continue
            
            pruned += 1
            bones.sort(reverse=True, key=lambda item: item[1])
            
            vert[deform].clear()
            for id, weight in (bones[0:3] + sections):
                vert[deform][id] = weight
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
    
    return pruned


def prune_weights(obj, threshold):
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    deform = bm.verts.layers.deform.active
    
    pruned = 0
    
    if deform:
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            weights = []
            for key in vert[deform].keys():
                if vert[deform][key] > threshold:
                    weights.append((key, vert[deform][key]))
            
            if len(vert[deform].keys()) > len(weights):
                pruned += 1
            
            vert[deform].clear()
            for id, weight in weights:
                vert[deform][id] = weight
        
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
    
    return pruned


def cleanup(obj, bone_indices, threshold):
    verts_prune_selection = prune_weights(obj, threshold)
    verts_prune_overdetermined = prune_overdetermined(obj, bone_indices)
    verts_normalized = normalize_weights(obj, bone_indices)
    
    return max(verts_prune_selection, verts_prune_overdetermined, verts_normalized)