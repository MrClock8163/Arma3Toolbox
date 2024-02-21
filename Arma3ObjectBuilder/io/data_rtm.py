# Class structure, read-write methods and conversion functions for handling
# the RTM binary data structure. Format specifications
# can be found on the community wiki:
# https://community.bistudio.com/wiki/Rtm_(Animation)_File_Format
# Largely based on the RTM exporter from the original ArmaToolbox by Alwarren.


import struct

from . import binary_handler as binary


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