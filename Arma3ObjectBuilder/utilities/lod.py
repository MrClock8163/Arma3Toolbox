# Backend functions mainly used by the P3D I/O.


from . import data


def has_ngons(mesh):
    for face in mesh.polygons:
        if len(face.vertices) > 4:
            return True
    
    return False


def is_contiguous_mesh(bm):
        for edge in bm.edges:
            if not edge.is_contiguous:
                return False
                
        return True


def get_lod_name(index):
    return data.lod_type_names.get(index, data.lod_type_names[30])


def format_lod_name(index, resolution):
    if index in data.lod_resolution is not None:
        return "%s %d" % (get_lod_name(index), resolution)
        
    return get_lod_name(index)