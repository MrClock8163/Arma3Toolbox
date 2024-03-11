# Class structure, read-write methods and conversion functions for handling
# the MLOD P3D binary data structure. Format specifications
# can be found on the community wiki (although not withoug errors):
# https://community.bistudio.com/wiki/P3D_File_Format_-_MLOD


import struct
import math
import re
from decimal import Decimal, Context

from . import binary_handler as binary


class P3D_Error(Exception):
    def __str__(self):
        return "P3D - %s" % super().__str__()


# Generic class to consume unneeded TAGG types (eg.: #Hidden#, #Selected#).
# The class is needed because the data field of the TAGG object must not be none.
class P3D_TAGG_DataEmpty():
    @classmethod
    def read(cls, file, length):
        file.read(length)
        return cls()
    
    def length(self):
        return 0
    
    def write(self, file):
        pass


class P3D_TAGG_DataSharpEdges():
    def __init__(self):
        self.edges = []
    
    @classmethod
    def read(cls, file, length = 0):
        output = cls()
        
        for i in range(length // 8):
            point_1, point_2 = binary.read_ulongs(file, 2)
            
            if point_1 == point_2:
                continue
            
            output.edges.append((point_1, point_2))
        
        return output
    
    def length(self):
        return len(self.edges) * 8
    
    def write(self, file):
        for edge in self.edges:
            if edge[0] == edge[1]:
                continue
            
            binary.write_ulong(file, *edge)


class P3D_TAGG_DataProperty():
    def __init__(self):
        self.key = ""
        self.value = ""
    
    @classmethod
    def read(cls, file):
        output = cls()
        
        output.key = binary.read_asciiz_field(file, 64)
        output.value = binary.read_asciiz_field(file, 64)
        
        return output
    
    def length(self):
        return 128
    
    def write(self, file):
        binary.write_asciiz_field(file, self.key, 64)
        binary.write_asciiz_field(file, self.value, 64)


class P3D_TAGG_DataMass():
    def __init__(self):
        self.masses = {}
    
    @classmethod
    def read(cls, file, count_verts):
        output = cls()
        output.masses = {i: value for i, value in enumerate(binary.read_floats(file, count_verts))}
        
        return output
    
    def length(self):
        return len(self.masses) * 4
    
    def write(self, file):
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
        data = binary.read_floats(file, count_values)
        output.uvs = {i: (data[i * 2], 1 - data[i * 2 + 1]) for i in range(count_values // 2)}

        return output
    
    def length(self):
        return len(self.uvs) * 8 + 4
    
    def write(self, file):
        binary.write_ulong(file, self.id)
        for value in self.uvs.values():
            binary.write_float(file, value[0], 1 - value[1])


class P3D_TAGG_DataSelection():
    def __init__(self):
        self.count_verts = 0
        self.count_faces = 0
        self.weight_verts = {}
        self.weight_faces = {}
    
    @classmethod
    def decode_weight(cls, weight):
        if weight == 0 or weight == 1:
            return weight
            
        value = (256 - weight) / 255
        
        if value > 1:
            return 0
            
        return value
    
    @classmethod
    def encode_weight(cls, weight):
        if weight == 0 or weight == 1:
            return int(weight)
            
        value = round(256 - 255 * weight)
        
        if value == 256:
            return 0
            
        return value
    
    @classmethod
    def read(cls, file, count_verts, count_faces):
        output = cls()
        
        output.count_verts = count_verts
        output.count_faces = count_faces
        
        data_verts = bytearray(file.read(count_verts))

        output.weight_verts = {i: cls.decode_weight(value) for i, value in enumerate(data_verts) if value > 0}
        file.read(count_faces)

        return output
    
    def length(self):
        return self.count_verts + self.count_faces
    
    def write(self, file):        
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
        self.data = P3D_TAGG_DataEmpty()

    def __repr__(self):
        return self.name
    
    def __eq__(self, other):        
        return type(other) is type(self) and self.name == other.name
    
    # Read

    @classmethod
    def read(cls, file, count_verts, count_faces):
        output = cls()
        
        output.active = binary.read_bool(file)
        output.name = binary.read_asciiz(file)
        length = binary.read_ulong(file)
        
        
        if output.name == "#EndOfFile#":
            if length != 0:
                raise P3D_Error("Invalid EOF")
            
            output.active = False
        elif output.name == "#SharpEdges#":
            output.data = P3D_TAGG_DataSharpEdges.read(file, length)
        elif output.name == "#Property#":
            if length != 128:
                raise P3D_Error("Invalid name property length: %d" % length)
            
            output.data = P3D_TAGG_DataProperty.read(file)
        elif output.name == "#Mass#":
            output.data = P3D_TAGG_DataMass.read(file, count_verts)
        elif output.name == "#UVSet#":
            output.data = P3D_TAGG_DataUVSet.read(file, length)
        elif not output.name.startswith("#") and not output.name.endswith("#"):
            output.data = P3D_TAGG_DataSelection.read(file, count_verts, count_faces)
        else:
            # Consume unneeded TAGGs
            file.read(length)
            output.active = False
        
        return output
    
    # Write

    def write(self, file):
        if not self.active:
            return 
            
        binary.write_bool(file, self.active)
        binary.write_asciiz(file, self.name)
        binary.write_ulong(file, self.data.length())
        self.data.write(file)
    
    # Operations

    def is_proxy(self):
        if not self.name.startswith("proxy:"):
            return False
        
        regex_proxy = "proxy:.*\.\d+"
        return re.match(regex_proxy, self.name)
    
    def is_selection(self):
        return not self.name.startswith("#") and not self.name.endswith("#")


class P3D_LOD_Resolution():
    VISUAL = 0
    VIEW_GUNNER = 1
    VIEW_PILOT = 2
    VIEW_CARGO = 3
    SHADOW = 4
    EDIT = 5
    GEOMETRY = 6
    GEOMETRY_BUOY = 7
    GEOMETRY_PHYSX = 8
    MEMORY = 9
    LANDCONTACT = 10
    ROADWAY = 11
    PATHS = 12
    HITPOINTS = 13
    VIEW_GEOMETRY = 14
    FIRE_GEOMETRY = 15
    VIEW_CARGO_GEOMERTRY = 16
    VIEW_CARGO_FIRE_GEOMETRY = 17
    VIEW_COMMANDER = 18
    VIEW_COMMANDER_GEOMETRY = 19
    VIEW_COMMANDER_FIRE_GEOMETRY = 20
    VIEW_PILOT_GEOMETRY = 21
    VIEW_PILOT_FIRE_GEOMETRY = 22
    VIEW_GUNNER_GEOMETRY = 23
    VIEW_GUNNER_FIRE_GEOMETRY = 24
    SUBPARTS = 25
    SHADOW_VIEW_CARGO = 26
    SHADOW_VIEW_PILOT = 27
    SHADOW_VIEW_GUNNER = 28
    WRECKAGE = 29
    UNDERGROUND = 30 # Geometry PhysX Old for Arma 3
    UNKNOWN = 31

    INDEX_MAP = {
        (0.0, 0): VISUAL, # Visual
        (1.0, 3): VIEW_GUNNER, # View Gunner
        (1.1, 3): VIEW_PILOT, # View Pilot
        (1.2, 3): VIEW_CARGO, # View Cargo
        (1.0, 4): SHADOW, # Shadow
        (2.0, 4): EDIT, # Edit
        (1.0, 13): GEOMETRY, # Geometry
        (2.0, 13): GEOMETRY_BUOY, # Geometry Buoyancy
        (3.0, 13): UNDERGROUND, # Underground for VBS, Geometry PhysX (old) for Arma 3
        (4.0, 13): GEOMETRY_PHYSX, # Geometry PhysX
        (1.0, 15): MEMORY, # Memory
        (2.0, 15): LANDCONTACT, # Land Contact
        (3.0, 15): ROADWAY, # Roadway
        (4.0, 15): PATHS, # Paths
        (5.0, 15): HITPOINTS, # Hit Points
        (6.0, 15): VIEW_GEOMETRY, # View Geometry
        (7.0, 15): FIRE_GEOMETRY, # Fire Geometry
        (8.0, 15): VIEW_CARGO_GEOMERTRY, # View Cargo Geometry
        (9.0, 15): VIEW_CARGO_FIRE_GEOMETRY, # View Cargo Fire Geometry
        (1.0, 16): VIEW_COMMANDER, # View Commander
        (1.1, 16): VIEW_COMMANDER_GEOMETRY, # View Commander Geometry
        (1.2, 16): VIEW_COMMANDER_FIRE_GEOMETRY, # View Commander Fire Geometry
        (1.3, 16): VIEW_PILOT_GEOMETRY, # View Pilot Geometry
        (1.4, 16): VIEW_PILOT_FIRE_GEOMETRY, # View Pilot Fire Geometry
        (1.5, 16): VIEW_GUNNER_GEOMETRY, # View Gunner Geometry
        (1.6, 16): VIEW_GUNNER_FIRE_GEOMETRY, # View Gunner Fire Geometry
        (1.7, 16): SUBPARTS, # Sub Parts
        (1.8, 16): SHADOW_VIEW_CARGO, # Cargo View Shadow Volume
        (1.9, 16): SHADOW_VIEW_PILOT, # Pilot View Shadow Volume
        (2.0, 16): SHADOW_VIEW_GUNNER, # Gunner View Shadow Volume
        (2.1, 16): WRECKAGE, # Wreckage
        (-1.0, 0): UNKNOWN # Unknown
    }

    RESOLUTION_POS = { # decimal places in normalized format
        VIEW_CARGO: 3,
        SHADOW: 4,
        EDIT: 4,
        VIEW_CARGO_GEOMERTRY: 2,
        SHADOW_VIEW_CARGO: 3
    }

    def __init__(self, lod = 0, res = 0):
        self.lod = lod
        self.res = res
        self.source = None # field to store the originally read float value for debug purposes
    
    def __eq__(self, other):
        return type(self) is type(other) and self.get() == other.get()
    
    def __float__(self):
        return float(self.encode(self.lod, self.res))

    @classmethod
    def encode(cls, lod, resolution):
        if lod == cls.VISUAL or lod == cls.UNKNOWN:
            return resolution 
        
        lookup = {v: k for k, v in cls.INDEX_MAP.items()}

        coef, exp = lookup[lod]
        pos = cls.RESOLUTION_POS.get(lod, None)

        resolution_sign = (resolution * 10**(exp - pos)) if pos is not None else 0
        
        return coef * 10**exp + resolution_sign

    @classmethod
    def decode(cls, signature):
        if signature < 1e3:
            return cls.VISUAL, round(signature)
        elif 1e4 <= signature < 2e4:
            return cls.SHADOW, round(signature - 1e4)
        
        num = Decimal(signature)
        exp = num.normalize(Context(2)).adjusted()
        
        coef = float((num / 10**exp))
        base = round(coef, 1) if exp in (3, 16) else round(coef)

        lod = cls.INDEX_MAP.get((base, exp), cls.UNKNOWN)
        pos = cls.RESOLUTION_POS.get(lod, None)

        if lod == cls.UNKNOWN:
            return lod, round(signature)

        resolution = int(round((coef - base) * 10**pos, pos)) if pos is not None else 0
        
        return lod, resolution
    
    @classmethod
    def from_float(cls, value):
        output = cls(*cls.decode(value))
        output.source = value
        return output
    
    def set_from_float(self, value):
        self.lod, self.res = self.decode(value)
        self.source = value
    
    def set(self, lod, res):
        self.lod = lod
        self.res = res
    
    def get(self):
        return self.lod, self.res


class P3D_LOD():
    def __init__(self):
        self.signature = b"P3DM"
        self.version = (28, 256)
        self.flags = 0x00000000
        self.resolution = P3D_LOD_Resolution()

        self.verts = {}
        self.normals = {}
        self.faces = {}
        self.taggs = []
    
    def __eq__(self, other):
        return type(other) is type(self) and other.resolution == self.resolution
    
    # Reading

    @staticmethod
    def read_vert(file):
        x, z, y, flag = struct.unpack('<fffI', file.read(16))
        return x, y, z, flag
    
    def read_verts(self, file, count_verts):
        self.verts = {i: self.read_vert(file) for i in range(count_verts)}

    @staticmethod
    def read_normal(file):
        x, z, y = struct.unpack('<fff', file.read(12))
        return -x, -y, -z
    
    def read_normals(self, file, count_normals):
        self.normals = {i: self.read_normal(file) for i in range(count_normals)}
    
    @staticmethod
    def read_face(file):
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

        return [vertices, normals, uvs, texture, material, flag]

    def read_faces(self, file, count_faces):
        self.faces = {i: self.read_face(file) for i in range(count_faces)}

    @classmethod
    def read(cls, file):

        signature = file.read(4)
        if signature != b"P3DM":
            raise P3D_Error("Unsupported LOD type: %s" % str(signature))
        
        version = binary.read_ulongs(file, 2)
        if version != (0x1c, 0x100):
            raise P3D_Error("Unsupported LOD version: %d.%d" % (version[0], version[1]))

        output = cls()
        output.version = version
        
        count_verts, count_normals, count_faces, flags = binary.read_ulongs(file, 4)
        output.flags = flags

        output.read_verts(file, count_verts)
        output.read_normals(file, count_normals)
        output.renormalize_normals()
        output.read_faces(file, count_faces)

        tagg_signature = binary.read_char(file, 4)
        if tagg_signature != "TAGG":
            raise P3D_Error("Invalid TAGG section signature: %s" % tagg_signature)
        
        while True:
            tagg = P3D_TAGG.read(file, count_verts, count_faces)
            if tagg.name == "#EndOfFile#":
                break
            
            if tagg.active:
                output.taggs.append(tagg)
        
        output.resolution.set_from_float(binary.read_float(file))
        
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
        file.write(self.signature)
        binary.write_ulong(file, *self.version)
        
        count_verts = len(self.verts)
        count_normals = len(self.normals)
        count_faces = len(self.faces)
        
        binary.write_ulong(file, count_verts, count_normals, count_faces, self.flags)

        self.write_verts(file)
        self.write_normals(file)
        self.write_faces(file)
        
        binary.write_chars(file, "TAGG")
        
        for tagg in self.taggs:
            tagg.write(file)
        
        eof = P3D_TAGG()
        eof.name = "#EndOfFile#"
        eof.write(file)
            
        binary.write_float(file, float(self.resolution))
    
    # Operations

    # The normals are stored as triplets of IEEE-754 32bit floating numbers,
    # which potentially result in a not normalized vector, which causes issues
    # in Blender, so the vectors need to be renormalized before usage.
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
        self.taggs = [tagg for tagg in self.taggs if tagg.active]
    
    # Generate lookup dictionary for all unique materials. Primarily called
    # from the parent MLOD object, so the dictionary is edited in place, not 
    # returned.
    def get_materials(self, materials = {}):
        for item in self.faces:
            face = self.faces[item]
            texture = face[3]
            material = face[4]

            if (texture, material) not in materials:
                materials[(texture, material)] = len(materials)
    
    # Generate the necessary material index for each face, as well
    # as the indices of the used materials in each material slot.
    def get_sections(self, materials):
        slot_indices = []
        slot_material_indices = []

        last_idx = None
        face_idx = 0

        for i in self.faces:
            face = self.faces[i]
            texture = face[3]
            material = face[4]
            
            idx = materials[(texture, material)]
            if last_idx is None:
                last_idx = idx
                slot_material_indices.append(idx)

            if idx != last_idx:
                slot_material_indices.append(idx)
                face_idx += 1
                last_idx = idx

            slot_indices.append(face_idx)

        return slot_indices, slot_material_indices
    
    def get_sections_merged(self, materials):
        slot_indices = []
        material_slot_indices = {}

        for i in self.faces:
            face = self.faces[i]
            texture = face[3]
            material = face[4]

            material_idx = materials[(texture, material)]
            slot_idx = material_slot_indices.get(material_idx)
            if slot_idx is None:
                slot_idx = len(material_slot_indices)
                material_slot_indices[material_idx] = slot_idx
            
            slot_indices.append(slot_idx)

        return slot_indices, list(material_slot_indices.keys())

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
        regex_proxy = "proxy:(.*)\.(\d+)"

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
    
    # Extract the UVSet 0 embedded into the face data, and return a dictionary
    # of all UVSets, unique by ID. If UVSet 0 is also found as a TAGG, the TAGG
    # data takes precedence over the embedded values.
    def uvsets(self):
        sets = {0: [uv for idx in self.faces for uv in self.faces[idx][2]]}
        for tagg in self.taggs:
            if tagg.name != "#UVSet#":
                continue

            sets[tagg.data.id] = tagg.data.uvs

        return sets

    # Generate loop normals list that can be directly used by the Blender API
    # mesh.normals_split_custom_set() function
    def loop_normals(self):
        return [self.normals[item] for face in self.faces.values() for item in face[1]]
    
    # Collect and group the used vertex flag values for setting up
    # the flag data layer and flag groups object data.
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
    
    # Collect and group the used face flag values for setting up
    # the flag data layer and flag groups object data.
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
    
    # Change every file path, and selection name to lower case for a uniform output.
    def force_lowercase(self):
        for idx in self.faces:
            face = self.faces[idx]
            face[3] = face[3].lower()
            face[4] = face[4].lower()
        
        for tagg in self.taggs:
            if tagg.is_selection():
                tagg.name = tagg.name.lower()


class P3D_MLOD():
    def __init__(self):
        self.source = ""
        self.version = 257
        self.signature = b"MLOD"
        
        self.lods = []
    
    @classmethod
    def read(cls, file, first_lod_only = False):
        
        signature = file.read(4)
        if signature != b"MLOD":
            raise P3D_Error("Invalid MLOD signature: %s" % str(signature))

        version = binary.read_ulong(file)
        if version != 257:
            raise P3D_Error("Unsupported MLOD version: %d" % version)

        output = cls()
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
        if len(self.lods) == 0:
            raise P3D_Error("Cannot write file with no LODs")
        
        file.write(self.signature)
        binary.write_ulong(file, self.version)
        binary.write_ulong(file, len(self.lods))
        for lod in self.lods:
            lod.write(file)
    
    def write_file(self, filepath):
        with open(filepath, "wb") as file:
            self.write(file)
    
    def get_materials(self):
        materials = {("", ""): 0}

        for lod in self.lods:
            lod.get_materials(materials)

        return materials

    # Function to ensure uniform format in the output files regardless
    # of the casing in Blender.
    def force_lowercase(self):
        for lod in self.lods:
            lod.force_lowercase()
    
    def find_lod(self, index = 0, resolution = 0):
        for lod in self.lods:
            if lod.resolution.get() == (index, resolution):
                return lod
        
        return None
    
    def get_duplicate_lods(self):
        signatures = set()
        duplicates = []

        for i, lod in enumerate(self.lods):
            sign = float(lod.resolution)
            if sign in signatures:
                duplicates.append(i)
            else:
                signatures.add(sign)

        return duplicates
