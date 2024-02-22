# Class structure, read-write methods and conversion functions for handling
# the RTM binary data structure. Format specifications
# can be found on the community wiki:
# https://community.bistudio.com/wiki/Rtm_(Animation)_File_Format
# Largely based on the RTM exporter from the original ArmaToolbox by Alwarren.


import struct
import io
import numpy as np


from . import binary_handler as binary
from . import compression


class RTM_Error(Exception):
    pass


class RTM_Transform():
    def __init__(self):
        self.bone = ""
        self.matrix = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    
    @classmethod
    def read(cls, file):
        output = cls()
        
        output.bone = binary.read_asciiz_field(file, 32)
        data = struct.unpack('<12f', file.read(48))

        output.matrix = [
            [data[0], data[6], data[3], data[9]],
            [data[2], data[8], data[5], data[11]],
            [data[1], data[7], data[4], data[10]],
            [0, 0, 0, 1]
        ]

        return output
    
    def write(self, file):
        file.write(struct.pack('<32s', self.bone.encode('ASCII')))

        data = self.matrix
        mat = [
            [data[0][0], data[2][0], data[1][0]],
            [data[0][2], data[2][2], data[1][2]],
            [data[0][1], data[2][1], data[1][1]],
            [data[0][3], data[2][3], data[1][3]]
        ]

        file.write(struct.pack('<12f', *mat[0], *mat[1], *mat[2], *mat[3]))


class RTM_Frame():
    def __init__(self):
        self.phase = 0
        self.transforms = []
    
    def __repr__(self):
        return "Phase: %f" % self.phase
    
    @classmethod
    def read(cls, file, count_bones):
        output = cls()

        output.phase = binary.read_float(file)
        output.transforms = [RTM_Transform.read(file) for i in range(count_bones)]
        
        return output

    def write(self, file):
        binary.write_float(file, self.phase)
        for item in self.transforms:
            item.write(file)


class RTM_MDAT():
    signature = b"RTM_MDAT"

    def __init__(self):
        self.items = []
    
    @classmethod
    def read(cls, file, skip_signature = False):
        output = cls()

        if not skip_signature:
            signature = file.read(8)
            if signature != b"RTM_MDAT":
                raise RTM_Error("Invalid MDAT signature: %s" % str(signature))

        file.read(4) # padding
        count_items = binary.read_ulong(file)
        for i in range(count_items):
            phase = binary.read_float(file)
            name = binary.read_lascii(file)
            value = binary.read_lascii(file)

            output.items.append((phase, name, value))

        return output

    def write(self, file):
        file.write(self.signature)
        binary.write_ulong(file, 0)
        binary.write_ulong(file, len(self.items))

        for phase, name, value in self.items:
            binary.write_float(file, phase)
            binary.write_lascii(file, name)
            binary.write_lascii(file, value)


class RTM_0101():
    signature = b"RTM_0101"

    def __init__(self):
        self.motion = (0, 0, 0)
        self.frames = []
        self.bones = []
    
    @classmethod
    def read(cls, file, skip_signature = False):
        output = cls()
        if not skip_signature:
            signature = file.read(8)
            if signature != b"RTM_0101":
                raise RTM_Error("Invalid header signature: %s" % signature)

        x, y, z = struct.unpack('<fff', file.read(12))
        output.motion = (x, y, z)
        count_frames = binary.read_ulong(file)
        count_bones = binary.read_ulong(file)
        
        output.bones = [binary.read_asciiz_field(file, 32) for i in range(count_bones)]
        output.frames = [RTM_Frame.read(file, count_bones) for i in range(count_frames)]

        return output
    
    def write(self, file):
        file.write(self.signature)
        file.write(struct.pack('<fff', self.motion[0], self.motion[1], self.motion[2]))
        count_frames = len(self.frames)
        count_bones = len(self.bones)

        binary.write_ulong(file, count_frames)
        binary.write_ulong(file, count_bones)

        for item in self.bones:
            file.write(struct.pack('<32s', item.encode('ASCII')))
        
        for item in self.frames:
            item.write(file)
    
    # While the game engine itself seems to be not case sensitive,
    # some tools (eg.: animation preview in Object Builder, the preview would
    # not work if the case of the selection names in the model and the RTM is not
    # matcing) are. So it's good to have a way to keep everything uniform in the
    # outputs, regardless of how things are called in Blender.
    def force_lowercase(self):
        self.bones = [bone.lower() for bone in self.bones]

        for frame in self.frames:
            for trans in frame.transforms:
                trans.bone = trans.bone.lower()


class RTM_File():
    def __init__(self):
        self.source = ""
        self.props = None
        self.anim = RTM_0101()
    
    @classmethod
    def read(cls, file):
        output = cls()

        while file.peek():
            signature = file.read(8)
            if signature == b"RTM_0101":
                output.anim = RTM_0101.read(file, True)
            elif signature == b"RTM_MDAT":
                output.props = RTM_MDAT.read(file, True)
            else:
                raise RTM_Error("Unknown datablock signature: %s" % str(signature))
        
        return output
    
    @classmethod
    def read_file(cls, filepath):
        output = None
        with open(filepath, "br") as file:
            output = cls.read(file)

        return output
    
    def write(self, file):
        if self.props:
            self.props.write(file)
        
        if not self.anim:
            raise RTM_Error("Cannot export RTM without animation data")
        
        self.anim.write(file)
    
    def write_file(self, filepath):
        with open(filepath, "wb") as file:
            self.write(file)


class BMTR_Error(Exception):
    pass


class BMTR_Prop:
    def __init__(self):
        self.name = ""
        self.value = ""
        self.phase = 0
    
    @classmethod
    def read(cls, file):
        output = cls()

        file.read(4)
        output.name = binary.read_asciiz(file)
        output.phase = binary.read_float(file)
        output.value = binary.read_asciiz(file)

        return output

    def as_rtm(self):
        return (self.phase, self.name, self.value)


class BMTR_Transform:
    def __init__(self):
        self.quaternion = (0, 0, 0, 1)
        self.location = (0, 0, 0)
    
    @classmethod
    def read(cls, file):
        output = cls()

        output.quaternion = tuple([value / 16384 for value in binary.read_shorts(file, 4)])
        x, z, y = binary.read_halfs(file, 3)
        output.location = (-x, -y, z)

        return output

    def as_rtm(self, bone):
        output = RTM_Transform()
        output.bone = bone
        qx, qz, qy, qw = self.quaternion
        x, y, z = self.location

        r00 = 1 - 2*qy**2 - 2*qz**2
        r01 = 2*qx*qy - 2*qz*qw
        r02 = 2*qx*qz + 2*qy*qw

        r10 = 2*qx*qy + 2*qz*qw
        r11 = 1 - 2*qx**2 - 2*qz**2
        r12 = 2*qy*qz - 2*qx*qw

        r20 = 2*qx*qz - 2*qy*qw
        r21 = 2*qy*qz + 2*qx*qw
        r22 = 1 - 2*qx**2 - 2*qy**2
        
        output.matrix = [
            [r00, r01, -r02, x],
            [r10, r11, -r12, y],
            [-r20, -r21, r22, z],
            [0, 0, 0, 1]
        ]

        return output


class BMTR_Frame:
    def __init__(self):
        self.transforms = []

    @classmethod
    def read(cls, file, count_bones):
        output = cls()
        output.transforms = [BMTR_Transform.read(file) for i in range(count_bones)]

        return output

    def as_rtm(self, phase, bones, bone_parents):
        if len(bone_parents) < len(self.transforms):
            raise BMTR_Error("Mismatching bone (%d) - transformation (%d) counts" % (len(bone_parents), len(self.transforms)))
        
        output = RTM_Frame()
        output.phase = phase

        transform_lookup = {}
        for bone, transform in zip(bones, self.transforms):
            rtm_transform = transform.as_rtm(bone)
            output.transforms.append(rtm_transform)
            transform_lookup[bone] = rtm_transform
        
        # The transformations stored in the BMTR format are not absolute like in plain RTM, but relative to the parent
        # bones instead. To get the absolute transformation, the matrix of each bone has to be multiplied with the matrix
        # of its parent. To get the correct results, the multiplication must be done in hierarchical order.
        default = RTM_Transform()
        for bone in bone_parents:
            rtm_transform = transform_lookup[bone]
            rtm_transform_parent = transform_lookup.get(bone_parents[bone], default)
            absolute_matrix = np.matrix(rtm_transform_parent.matrix) @ np.matrix(rtm_transform.matrix)
            rtm_transform.matrix = absolute_matrix.tolist()

        return output


class BMTR_File:
    signature = b"BMTR"
    versions = {3, 4, 5}

    def __init__(self):
        self.source = ""
        self.version = 5
        self.motion = (0, 0, 0)
        self.frames = []
        self.phases = []
        self.bones = []
        self.props = []
    
    def read_frame_phases(self, file, count_frames):
        expected = count_frames * 4
        compressed = expected >= 1024
        if self.version > 4:
            compressed = binary.read_bool(file)
        
        output = []
        if compressed:
            _, uncompressed = compression.lzo1x_decompress(file, expected)
            buffer = io.BufferedReader(io.BytesIO(uncompressed))
            output = [binary.read_float(buffer) for i in range(count_frames)]
            if buffer.read() != b"":
                raise BMTR_Error("Decompressed data is longer than expected")
        else:
            output = [binary.read_float(file) for i in range(count_frames)]
        
        return output

    def read_frames(self, file:io.BufferedReader, count_frames, count_bones):
        output = []
        for i in range(count_frames):
            count_bones = binary.read_ulong(file)

            expected = count_bones * 14
            compressed = expected >= 1024
            if self.version > 4:
                compressed = binary.read_bool(file)

            if compressed:
                _, uncompressed = compression.lzo1x_decompress(file, expected)
                buffer = io.BufferedReader(io.BytesIO(uncompressed))
                output.append(BMTR_Frame.read(buffer, count_bones))
                if buffer.read() != b"":
                    raise BMTR_Error("Decompressed data is longer than expected")
            else:
                output.append(BMTR_Frame.read(file, count_bones))

        return output

    @classmethod
    def read(cls, file):
        signature = file.read(4)
        if signature != cls.signature:
            raise BMTR_Error("Invalid header signature: %s" % signature)
        
        output = cls()
        version = binary.read_ulong(file)
        if version not in cls.versions:
            raise BMTR_Error("Unknown version: %s" % version)

        output.version = version
        file.read(1)
        output.motion = binary.read_floats(file, 3)

        count_frames = binary.read_ulong(file)
        file.read(4)
        count_bones = binary.read_ulong(file)
        count_bones_check = binary.read_ulong(file)
        if count_bones_check != count_bones:
            raise BMTR_Error("Bone count mismatch (expected: %d, got: %d)" % (count_bones, count_bones_check))
        
        output.bones = [binary.read_asciiz(file) for i in range(count_bones)]

        if output.version > 4:
            file.read(4)
            count_props = binary.read_ulong(file)
            output.props = [BMTR_Prop.read(file) for i in range(count_props)]

        count_frames_check = binary.read_ulong(file)
        if count_frames_check != count_frames:
            raise BMTR_Error("Frame count mismatch (expected: %d, got: %d)" % (count_frames, count_frames_check))
        
        output.phases = output.read_frame_phases(file, count_frames)
        output.frames = output.read_frames(file, count_frames, count_bones)
        
        remainder = file.read()
        if remainder != b"":
            raise BMTR_Error("EOF not found")

        return output

    @classmethod
    def read_file(cls, filepath):
        output = None
        with open(filepath, "br") as file:
            output = cls.read(file)
        
        output.source = filepath
        
        return  output
    
    def as_rtm(self, bone_parents):
        output = RTM_File()
        output.source = self.source
        rtm_0101 = output.anim
        rtm_mdat = output.props

        if len(self.props) > 0:
            rtm_mdat = RTM_MDAT()
            rtm_mdat.items = [prop.as_rtm() for prop in self.props]
        
        rtm_0101 = output.anim
        rtm_0101.motion = self.motion
        rtm_0101.bones = self.bones

        bones = set(self.bones)
        parents = {bone: parent for bone, parent in bone_parents.items() if bone.lower() in bones}

        for phase, frame in zip(self.phases, self.frames):
            rtm_0101.frames.append(frame.as_rtm(phase, self.bones, parents))

        return output

    def write(self, file):
        raise BMTR_Error("BMTR output is not supported, use plain RTM instead")

    def write_file(self, filepath):
        self.write(None)