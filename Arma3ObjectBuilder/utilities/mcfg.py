# Backend functions of the weight painting tools.


from . import generic as utils


# It's easier to prepare a list of the vertex group indices that
# correspond to bones defined in the model.cfg, than to try matching
# everything by name every time.
def get_bone_group_indices(obj, cfgbones):
    cfgbones_names = [item.name.lower() for item in cfgbones]    
    return [group.index for group in obj.vertex_groups if group.name.lower() in cfgbones_names]


def select_vertices_unnormalized(obj, bone_indices):
    with utils.edit_bmesh(obj) as bm:
        bm.verts.ensure_lookup_table()
        deform = bm.verts.layers.deform.verify()
        
        for vert in bm.verts:
            weights = 0
            for key in vert[deform].keys():
                if key not in bone_indices:
                    continue
                
                weights += vert[deform][key]
            
            vert.select_set(abs(weights-1) > 0.01)


def normalize_weights(obj, bone_indices):
    with utils.edit_bmesh(obj) as bm:
        deform = bm.verts.layers.deform.verify()
        bm.verts.ensure_lookup_table()
        
        normalized = 0
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
    
    return normalized


def select_vertices_overdetermined(obj, bone_indices):
    with utils.edit_bmesh(obj) as bm:
        bm.verts.ensure_lookup_table()
        deform = bm.verts.layers.deform.verify()
        
        for vert in bm.verts:
            bones = 0
            for key in vert[deform].keys():
                if key not in bone_indices:
                    continue
                
                bones += 1
            
            vert.select_set(bones > 3)


# If a vertex has overdetermined weighting (more than 3 bones affecting it),
# we might want to prune the excess bones. For each vertex of the mesh,
# the weights of bone selections are summed up, and the groups are sorted.
# Only the groups with the top 3 influence sum are left, rest are removed.
def prune_overdetermined(obj, bone_indices):
    with utils.edit_bmesh(obj) as bm:
        bm.verts.ensure_lookup_table()
        deform = bm.verts.layers.deform.verify()
        
        pruned = 0
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
    
    return pruned


# Weights are summed for every group for every vertex. Then all groups
# are removed, and only those readded that are above the threshold.
def prune_weights(obj, threshold):
    with utils.edit_bmesh(obj) as bm:
        bm.verts.ensure_lookup_table()
        deform = bm.verts.layers.deform.verify()
        
        pruned = 0
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

    return pruned


def cleanup(obj, bone_indices, threshold):
    verts_prune_selection = prune_weights(obj, threshold)
    verts_prune_overdetermined = prune_overdetermined(obj, bone_indices)
    verts_normalized = normalize_weights(obj, bone_indices)
    
    return max(verts_prune_selection, verts_prune_overdetermined, verts_normalized)