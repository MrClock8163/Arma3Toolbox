import struct

# import binary_handler as binary
from . import binary_handler as binary
from ..utilities import errors


class RTM_Transform():
    def __init__(self):
        self.bone = ""
        self.matrix = []
    
    @classmethod
    def read(cls, file):
        output = cls()
        
        output.bone = binary.read_char(file, 32)
        data = struct.unpack('<12f', file.read(48))

        output.matrix = [
            [data[0][0], data[0][2], data[0][1], 0],
            [data[2][0], data[2][2], data[2][1], 0],
            [data[1][0], data[1][2], data[1][1], 0],
            [data[3][0], data[3][2], data[3][1], 1]
        ]

        return output
    
    def write(self, file):
        file.write(struct.pack('<32s', self.bone.encode('ASCII')))

        data = self.matrix
        mat = [
            [data[0][0], data[0][2], data[0][1]],
            [data[2][0], data[2][2], data[2][1]],
            [data[1][0], data[1][2], data[1][1]],
            [data[3][0], data[3][2], data[3][1]]
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


class RTM_File():
    def __init__(self):
        self.signature = "RTM_0101"
        self.motion = (0, 0, 0)
        self.frames = []
        self.bones = []
    
    @classmethod
    def read(cls, file):
        output = cls()
        signature = binary.read_char(file, 8)
        if signature != "RTM_0101":
            raise errors.RTMError("Invalid header signature: %s" % signature)

        output.signature = signature
        x, z ,y = struct.unpack('<fff', file.read(12))
        output.motion = (x, y, z)
        count_frames = binary.read_ulong(file)
        count_bones = binary.read_ulong(file)
        
        output.bones = [binary.read_char(file, 32) for i in range(count_bones)]
        output.frames = [RTM_Frame.read(file, count_bones) for i in range(count_frames)]

        return output
    
    @classmethod
    def read_file(cls, filepath):
        output = None
        with open(filepath, "br") as file:
            output = cls.read(file)

        return output
    
    def write(self, file):
        binary.write_chars(file, self.signature)
        file.write(struct.pack('<fff', self.motion[0], self.motion[2], self.motion[1]))
        count_frames = len(self.frames)
        count_bones = len(self.bones)

        binary.write_ulong(file, count_frames)
        binary.write_ulong(file, count_bones)

        for item in self.bones:
            file.write(struct.pack('<32s', item.encode('ASCII')))
        
        for item in self.frames:
            item.write(file)
        
    def force_lowercase(self):
        self.bones = [bone.lower() for bone in self.bones]

        for frame in self.frames:
            for trans in frame.transforms:
                trans.bone = trans.bone.lower()