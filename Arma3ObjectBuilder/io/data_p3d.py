import struct
import math
import re

# import binary_handler as binary
from . import binary_handler as binary
from ..utilities import errors


class P3D_TAGG_DataEmpty():
    @classmethod
    def read(cls, file, length):
        file.read(length)
        return cls()
    
    def length(self):
        return 0
    
    def write(self, file):
        binary.write_ulong(file, 0)


class P3D_TAGG_DataSharpEdges():
    def __init__(self):
        self.edges = []
    
    @classmethod
    def read(cls, file, length = 0):
        output = cls()
        
        for i in range(length // 8):
            point_1 = binary.read_ulong(file)
            point_2 = binary.read_ulong(file)
            
            if point_1 == point_2:
                continue
            
            output.edges.append((point_1, point_2))
        
        return output
    
    def length(self):
        return len(self.edges) * 8
    
    def write(self, file):
        binary.write_ulong(file, self.length())
        for edge in self.edges:
            if edge[0] == edge[1]:
                continue
            
            binary.write_ulong(file, edge[0])
            binary.write_ulong(file, edge[1])


class P3D_TAGG_DataProperty():
    def __init__(self):
        self.key = ""
        self.value = ""
    
    @classmethod
    def read(cls, file):
        output = cls()
        
        output.key = binary.read_char(file, 64)
        output.value = binary.read_char(file, 64)
        
        return output
    
    def length(self):
        return 128
    
    def write(self, file):
        binary.write_ulong(file, self.length())
        file.write(struct.pack('<64s', self.key.encode('ASCII')))
        file.write(struct.pack('<64s', self.value.encode('ASCII')))


class P3D_TAGG_DataMass():
    def __init__(self):
        self.masses = {}
    
    @classmethod
    def read(cls, file, count_verts):
        output = cls()
        output.masses = {i: value for i, value in enumerate(struct.unpack('<%df' % count_verts, file.read(count_verts * 4)))}
        
        return output
    
    def length(self):
        return len(self.masses) * 4
    
    def write(self, file):
        binary.write_ulong(file, self.length())
        for value in self.masses.values():
            binary.write_float(file, value)


class P3D_TAGG_DataUVSet():
    def __init__(self):
        self.id = 0
        self.uvs = {}
    
    @classmethod
    def read(cls, file, length = 0):
        output = cls()
        count_values = (length - 4) // 4
        output.id = binary.read_ulong(file)
        data = struct.unpack('<%df' % count_values, file.read(length - 4))
        output.uvs = {i: (data[i * 2], 1 - data[i * 2 + 1]) for i in range(count_values // 2)}

        return output
    
    def length(self):
        return len(self.uvs) * 8
    
    def write(self, file):
        binary.write_ulong(file, self.length() + 4)
        binary.write_ulong(file, self.id)
        for value in self.uvs.values():
            binary.write_float(file, value[0])
            binary.write_float(file, 1 - value[1])


class P3D_TAGG_DataSelection():
    def __init__(self):
        self.count_verts = 0
        self.count_faces = 0
        self.weight_verts = {}
        self.weight_faces = {}
    
    @classmethod
    def decode_weight(cls, weight):
        if weight == 0:
            return 0.0
        elif weight == 1:
            return 1.0
            
        value = (256 - weight) / 255
        
        if value > 1:
            return 0
            
        return value
    
    @classmethod
    def encode_weight(cls, weight):
        if weight == 0:
            return 0
        elif weight  == 1:
            return 1
            
        value = round(256 - 255 * weight)
        
        if value == 256:
            return 0
            
        return value
    
    @classmethod
    def read(cls, file, count_verts, count_faces):
        output = cls()
        
        output.count_verts = count_verts
        # output.count_faces = count_faces
        
        data_verts = bytearray(file.read(count_verts))
        # data_faces = bytearray(file.read(count_faces))
        # file.read(count_faces)

        output.weight_verts = {i: cls.decode_weight(value) for i, value in enumerate(data_verts) if value > 0}
        # output.weight_faces = {i: cls.decode_weight(value) for i, value in enumerate(data_faces) if value > 0}
        file.read(count_faces)

        return output
    
    def length(self):
        return self.count_verts + self.count_faces
    
    def write(self, file):
        binary.write_ulong(file, self.length())
        
        bytes_verts = bytearray(self.count_verts)
        for idx in self.weight_verts:
            bytes_verts[idx] = self.encode_weight(self.weight_verts[idx])
        
        bytes_faces = bytearray(self.count_faces)
        for idx in self.weight_faces:
            bytes_faces[idx] = self.encode_weight(self.weight_faces[idx])
        
        file.write(bytes_verts)
        file.write(bytes_faces)


class P3D_TAGG():
    def __init__(self):
        self.active = True
        self.name = ""
        self.data = None

    def __repr__(self):
        return self.name
    
    def __eq__(self, other):        
        return type(other) is type(self) and self.name == other.name
    
    @classmethod
    def read(cls, file, count_verts, count_faces):
        output = cls()
        
        output.active = binary.read_bool(file)
        output.name = binary.read_asciiz(file)
        length = binary.read_ulong(file)
        
        
        if output.name == "#EndOfFile#":
            if length != 0:
                raise errors.P3DError("Invalid EOF")
            
            output.data = P3D_TAGG_DataEmpty.read(file, length)
            output.active = False
        elif output.name == "#SharpEdges#":
            output.data = P3D_TAGG_DataSharpEdges.read(file, length)
        elif output.name == "#Property#":
            if length != 128:
                raise errors.P3DError("Invalid name property length: %d" % length)
            
            output.data = P3D_TAGG_DataProperty.read(file)
        elif output.name == "#Mass#":
            output.data = P3D_TAGG_DataMass.read(file, count_verts)
        elif output.name == "#UVSet#":
            output.data = P3D_TAGG_DataUVSet.read(file, length)
        elif not output.name.startswith("#") and not output.name.endswith("#"):
            output.data = P3D_TAGG_DataSelection.read(file, count_verts, count_faces)
        else:
            output.data = P3D_TAGG_DataEmpty.read(file, length)
            output.active = False
        
        return output
    
    def write(self, file):
        if not self.active:
            return 
            
        binary.write_bool(file, self.active)
        binary.write_asciiz(file, self.name)
        self.data.write(file)
    
    def is_proxy(self):
        if not self.name.startswith("proxy:"):
            return False
        
        regex_proxy = "proxy:.*\.\d{3}"
        return re.match(regex_proxy, self.name)


class P3D_LOD():
    def __init__(self):
        self.signature = ""
        self.version = (-1, -1)
        self.flags = 0x00000000
        self.resolution = -1

        self.verts = {}
        self.normals = {}
        self.faces = {}
        self.taggs = []
    
    def __eq__(self, other):
        return type(other) is type(self) and other.resolution == self.resolution
    
    # Reading
    
    def read_vert(self, file):
        x, z, y, flag = struct.unpack('<fffI', file.read(16))
        return x, y, z, flag
    
    def read_verts(self, file, count_verts):
        self.verts = {i: self.read_vert(file) for i in range(count_verts)}

    def read_normal(self, file):
        x, z, y = struct.unpack('<fff', file.read(12))
        return -x, -y, -z
    
    def read_normals(self, file, count_normals):
        self.normals = {i: self.read_normal(file) for i in range(count_normals)}
    
    def read_face(self, file):
        count_sides = binary.read_ulong(file)
        vertices = []
        normals = []
        uvs = []

        for i in range(count_sides):
            vert, norm, u, v = struct.unpack('<IIff', file.read(16))
            vertices.append(vert)
            normals.append(norm)
            uvs.append((u, 1 - v))

        if count_sides < 4:
            file.read(16)
        
        flag = binary.read_ulong(file)
        texture = binary.read_asciiz(file)
        material = binary.read_asciiz(file)

        return vertices, normals, uvs, texture, material, flag

    def read_faces(self, file, count_faces):
        self.faces = {i: self.read_face(file) for i in range(count_faces)}

    @classmethod
    def read(cls, file):

        signature = binary.read_char(file, 4)
        if signature != "P3DM":
            raise errors.P3DError("Unsupported LOD type: %s" % signature)
        
        version = (binary.read_ulong(file), binary.read_ulong(file))
        if version != (0x1c, 0x100):
            raise errors.P3DError("Unsupported LOD version: %d.%d" % (version[0], version[1]))

        output = cls()
        output.signature = signature
        output.version = version
        
        count_verts = binary.read_ulong(file)
        count_normals = binary.read_ulong(file)
        count_faces = binary.read_ulong(file)
        
        output.flags = binary.read_ulong(file)

        output.read_verts(file, count_verts)
        output.read_normals(file, count_normals)
        output.renormalize_normals()
        output.read_faces(file, count_faces)

        tagg_signature = binary.read_char(file, 4)
        if tagg_signature != "TAGG":
            raise errors.P3DError("Invalid TAGG section signature: %s" % tagg_signature)
        
        while True:
            tagg = P3D_TAGG.read(file, count_verts, count_faces)
            if tagg.name == "#EndOfFile#":
                break

            output.taggs.append(tagg)
        
        output.resolution = binary.read_float(file)
        
        return output
    
    # Writing
    
    def write_vert(self, file, vert):
        file.write(struct.pack('<fffI', vert[0], vert[2], vert[1], vert[3]))
    
    def write_verts(self, file):
        for i in self.verts:
            self.write_vert(file, self.verts[i])
    
    def write_normal(self, file, normal):
        file.write(struct.pack('<fff', -normal[0], -normal[2], -normal[1]))
    
    def write_normals(self, file):
        for i in self.normals:
            self.write_normal(file, self.normals[i])
    
    def write_face(self, file, face):
        count_sides = len(face[0])
        binary.write_ulong(file, count_sides)

        for i in range(count_sides):
            file.write(struct.pack('<IIff', face[0][i], face[1][i], face[2][i][0], face[2][i][1]))
        
        if count_sides < 4:
            file.write(bytearray(16))
        
        binary.write_ulong(file, face[5])
        binary.write_asciiz(file, face[3])
        binary.write_asciiz(file, face[4])
    
    def write_faces(self, file):
        for i in self.faces:
            self.write_face(file, self.faces[i])


    def write(self, file):
        binary.write_chars(file, self.signature)
        binary.write_ulong(file, self.version[0])
        binary.write_ulong(file, self.version[1])
        
        count_verts = len(self.verts)
        count_normals = len(self.normals)
        count_faces = len(self.faces)
        
        binary.write_ulong(file, count_verts)
        binary.write_ulong(file, count_normals)
        binary.write_ulong(file, count_faces)
        binary.write_ulong(file, self.flags)

        self.write_verts(file)
        self.write_normals(file)
        self.write_faces(file)
        
        # for item in self.verts.values():
        #     item.write(file)
        
        # for item in self.normals.values():
        #     item.write(file)
        
        # for item in self.faces.values():
        #     item.write(file)
        
        binary.write_chars(file, "TAGG")
        
        for tagg in self.taggs:
            tagg.write(file)
        
        eof = P3D_TAGG()
        eof.name = "#EndOfFile#"
        eof.data = P3D_TAGG_DataEmpty()
        eof.write(file)
            
        binary.write_float(file, self.resolution)
    
    # Operations

    def renormalize_normals(self):
        for i in self.normals:
            normal = self.normals[i]
            length = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
            
            if length == 0:
                continue
                
            coef = 1 / length
            self.normals[i] = (normal[0] * coef, normal[1] * coef, normal[2] * coef)
    
    def pydata(self):
        verts = [self.verts[i][0:3] for i in self.verts]
        faces = [self.faces[idx][0] for idx in self.faces]

        return verts, [], faces
    
    def clean_taggs(self):
        clean_list = [tagg for tagg in self.taggs if tagg.active]

        self.taggs = clean_list
    
    def get_materials(self, materials = {}):
        for item in self.faces:
            face = self.faces[item]
            texture = face[3]
            material = face[4]

            if (texture, material) not in materials:
                materials[(texture, material)] = len(materials)
    
    def get_sections(self, materials):
        face_indices = []
        material_indices = []

        last_idx = None
        face_idx = 0

        for item in self.faces:
            face = self.faces[item]
            texture = face[3]
            material = face[4]
            
            idx = materials[(texture, material)]
            if last_idx is None:
                last_idx = idx
                material_indices.append(idx)

            if idx != last_idx:
                material_indices.append(idx)
                face_idx += 1
                last_idx = idx

            face_indices.append(face_idx)

        return face_indices, material_indices

    def renumber_components(self):
        counter = 1
        for tagg in self.taggs:
            if not re.match("component\d+", tagg.name, re.IGNORECASE):
                continue
            
            tagg.name = "component%02d" % counter
            counter += 1

        return counter

    # Blender only allows vertex group names to have up to 63 characters.
    # Since proxy selection names (file paths) are often longer than that,
    # they have to be replaced by formatted placeholders and later looked up
    # from a dictionary when needed.
    def proxies_to_placeholders(self):
        regex_proxy = "proxy:(.*)\.(\d{3})"

        lookup = {}

        proxy_idx = 0
        for tagg in self.taggs:
            if not tagg.is_proxy():
                continue

            data = re.match(regex_proxy, tagg.name).groups()
            name = "@proxy_%d" % proxy_idx
            lookup[name] = (data[0], int(data[1]))
            tagg.name = name

            proxy_idx += 1

        return lookup

    def placeholders_to_proxies(self, lookup):
        if len(lookup) == 0:
            return
        
        for tagg in self.taggs:
            if not tagg.name.startswith("@proxy_"):
                continue

            data = lookup.get(tagg.name)
            if not data:
                continue

            tagg.name = "proxy:%s.%03d" % (data[0], data[1])
    
    def uvsets(self):
        sets = {0: [uv for idx in self.faces for uv in self.faces[idx][2]]}
        for tagg in self.taggs:
            if tagg.name != "#UVSet#":
                continue

            sets[tagg.data.id] = tagg.data.uvs

        return sets

    def loop_normals(self):
        return [self.normals[item] for face in self.faces.values() for item in face[1]]
    
    def flag_groups_vertex(self):
        groups = {}
        values = {}

        for idx in self.verts:
            flag = self.verts[idx][3]
            group = groups.get(flag)
            if group is None:
                group = len(groups)
                groups[flag] = group
            
            values[idx] = group
        
        return list(groups.keys()), values
    
    def flag_groups_face(self):
        groups = {}
        values = {}

        for idx in self.faces:
            flag = self.faces[idx][5]
            group = groups.get(flag)
            if group is None:
                group = len(groups)
                groups[flag] = group
            
            values[idx] = group

        return list(groups.keys()), values


class P3D_MLOD():
    def __init__(self):
        self.source = ""
        self.version = None
        self.signature = ""
        
        self.lods = []
    
    @classmethod
    def read(cls, file, first_lod_only = False):
        
        signature = binary.read_char(file, 4)
        if signature != "MLOD":
            raise errors.P3DError("Invalid MLOD signature: %s" % signature)

        version = binary.read_ulong(file)
        if version != 257:
            raise errors.P3DError("Unsupported MLOD version: %d" % version)

        output = cls()
        output.signature = signature
        output.version = version

        count_lods = binary.read_ulong(file)
        if first_lod_only:
            count_lods = 1
        
        output.lods = [P3D_LOD.read(file) for i in range(count_lods)]
        
        return output
    
    @classmethod
    def read_file(cls, filepath, first_lod_only = False):
        output = None
        with open(filepath, "br") as  file:
            output = cls.read(file, first_lod_only)
        
        output.source = filepath
        
        return output
    
    def write(self, file):
        binary.write_chars(file, self.signature)
        binary.write_ulong(file, self.version)

        if len(self.lods) == 0:
            dummy_lod = P3D_LOD()
            dummy_lod.resolution = 0
            dummy_lod.version = (28, 256)
            dummy_lod.signature = "P3DM"

            binary.write_ulong(file, 1)
            dummy_lod.write(file)
        else:
            binary.write_ulong(file, len(self.lods))
            for lod in self.lods:
                lod.write(file)
    
    def write_file(self, filepath):
        with open(filepath, "wb") as file:
            self.write(file)
        
    # def clean_taggs(self):
    #     for lod in self.lods:
    #         lod.clean_taggs()
    
    def get_materials(self):
        materials = {("", ""): 0}

        for lod in self.lods:
            lod.get_materials(materials)

        return materials
    
    # def sections(self, materials):
    #     return [lod.get_sections(materials) for lod in self.lods]

    # def pydata(self):
    #     return [lod.pydata() for lod in self.lods] # generator to conserve memory
    
    # def renumber_components(self):
    #     for lod in self.lods:
    #         lod.renumber_components()
    
    # def proxies_to_placeholderes(self):
    #     return [lod.proxies_to_placeholders() for lod in self.lods]
    
    # def placeholders_to_proxies(self, lookup):
    #     for i, lod in enumerate(self.lods):
    #         lod.placeholders_to_proxies(lookup[i])