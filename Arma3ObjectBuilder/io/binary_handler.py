# Wrapper functions to simplify the reading/writing of simple binary data types
# used in the BI file formats, as outlined on the community wiki:
# https://community.bistudio.com/wiki/Generic_FileFormat_Data_Types


import struct
import io
import os


# def read_byte(file):
#     return struct.unpack('B', file.read(1))[0]
    
# def read_bytes(file, count = 1):
#     return [read_byte(file) for i in range(count)]

# def read_bool(file):
#     return read_byte(file) != 0
    
# def read_short(file):
#     return struct.unpack('<h', file.read(2))[0]

# def read_shorts(file, count = 1):
#     return struct.unpack('<%dh' % count, file.read(2 * count))
    
# def read_ushort(file):
#     return struct.unpack('<H', file.read(2))[0]

# def read_ushorts(file, count = 1):
#     return struct.unpack('<%dH' % count, file.read(2 * count))

# def read_long(file):
#     return struct.unpack('<i', file.read(4))[0]

# def read_longs(file, count = 1):
#     return struct.unpack('<%di' % count, file.read(4 * count))

# def read_ulong(file):
#     return struct.unpack('<I', file.read(4))[0]

# def read_ulongs(file, count = 1):
#     return struct.unpack('<%dI' % count, file.read(4 * count))

# def read_compressed_uint(file):
#     output = read_byte(file)
#     extra = output
    
#     byte_idx = 1
#     while extra & 0x80:
#         extra = read_byte(file)
#         output += (extra - 1) << (byte_idx * 7)
#         byte_idx += 1
    
#     return output
    
# def read_float(file):
#     return struct.unpack('<f', file.read(4))[0]

# def read_floats(file, count = 1):
#     return struct.unpack('<%df' % count, file.read(4 * count))
    
# def read_double(file):
#     return struct.unpack('<d', file.read(8))[0]

# def read_doubles(file, count = 1):
#     return struct.unpack('<%dd' % count, file.read(8 * count))
    
# def read_char(file, count = 1):
#     chars = struct.unpack('%ds' % count, file.read(count))[0]
#     return chars.decode('ascii')
    
# def read_asciiz(file):
#     res = b''
    
#     while True:
#         a = file.read(1)
#         if a == b'\x00' or a == b'':
#             break
            
#         res += a
    
#     return res.decode('ascii')

# def read_asciiz_field(file, field_len):
#     field = file.read(field_len)
#     if len(field) < field_len:
#         raise EOFError("ASCIIZ field ran into unexpected EOF")
    
#     result = bytearray()
#     for value in field:
#         if value == 0:
#             break
            
#         result.append(value)
#     else:
#         raise ValueError("ASCIIZ field length overflow")
    
#     return result.decode('ascii')
        
# def read_lascii(file):
#     length = read_byte(file)
#     value = file.read(length)
#     if len(value) != length:
#         raise EOFError("LASCII string ran into unexpected EOF")
    
#     return value.decode('ascii')

# def read_asciiz_padded(file, max_len = 0):
#     value = read_asciiz(file)

#     diff = max_len - (len(value) + 1)
#     if diff > 0:
#         file.read(diff)

#     return value
    
# def write_byte(file, value):
#     file.write(struct.pack('B', value))
    
# def write_bytes(file, values):
#     file.write(struct.pack('%dB' % len(values), *values))
    
# def write_bool(file, value):
#     write_byte(file, value)
    
# def write_short(file, *args):
#     file.write(struct.pack('<%dh' % len(args), *args))
    
# def write_ushort(file, *args):
#     file.write(struct.pack('<%dH' % len(args), *args))
    
# def write_long(file, *args):
#     file.write(struct.pack('<%di' % len(args), *args))
    
# def write_ulong(file, *args):
#     file.write(struct.pack('<%dI' % len(args), *args))

# def write_compressed_uint(file, value):
#     temp = value
#     while True:
#         if temp < 128:
#             write_byte(file, temp)
#             break

#         write_byte(file, (temp & 127) + 128)
#         temp = temp >> 7
    
# def write_float(file, *args):
#     file.write(struct.pack('<%df' % len(args), *args))
    
# def write_double(file, *args):
#     file.write(struct.pack('<%dd' % len(args), *args))
    
# def write_chars(file, values):
#     file.write(struct.pack('<%ds' % len(values), values.encode('ascii')))
    
# def write_asciiz(file, value):
#     file.write(struct.pack('<%ds' % (len(value) + 1), value.encode('ascii')))

# def write_asciiz_field(file, value, field_len):
#     if (len(value) + 1) > field_len:
#         raise ValueError("ASCIIZ value is longer (%d + 1) than field length (%d)" % (len(value), field_len))

#     file.write(struct.pack('<%ds' % field_len, value.encode('ascii')))

# def write_lascii(file, value):
#     length = len(value)
#     if length > 255:
#         raise OverflowError("LASCII string cannot be longer than 255 characters")
    
#     file.write(struct.pack('B%ds' % length, length, value.encode('ascii')))

# https://github.com/python/cpython/blob/1d7bddd9612bcbaaedbc837e2936de773e855411/Lib/_pyio.py#L74
def open_bis_file(file, mode = "rb", encoding = None):
    buffering = -1
    closefd = True
    opener = None

    if not isinstance(file, int):
        file = os.fspath(file)
    if not isinstance(file, (str, bytes, int)):
        raise TypeError("invalid file: %r" % file)
    if not isinstance(mode, str):
        raise TypeError("invalid mode: %r" % mode)
    if encoding is not None and not isinstance(encoding, str):
        raise TypeError("invalid encoding: %r" % encoding)
    modes = set(mode)
    if modes - set("axrwb") or len(mode) > len(modes):
        raise ValueError("invalid mode: %r" % mode)

    creating = "x" in modes
    reading = "r" in modes
    writing = "w" in modes
    appending = "a" in modes
    binary = "b" in modes

    if creating + reading + writing + appending > 1:
        raise ValueError("can't have read/write/append mode at once")
    if not (creating or reading or writing or appending):
        raise ValueError("must have exactly one of read/write/append mode")
    if binary and encoding is not None:
        raise ValueError("binary mode doesn't take an encoding argument")
    
    raw = io.FileIO(file,
        (creating and "x" or "") +
        (reading and "r" or "") +
        (writing and "w" or "") +
        (appending and "a" or ""),
        closefd, opener=opener)
    
    result = raw
    
    try:
        if buffering < 0:
            buffering = io.DEFAULT_BUFFER_SIZE
            try:
                bs = os.fstat(raw.fileno()).st_blksize
            except (OSError, AttributeError):
                pass
            else:
                if bs > 1:
                    buffering = bs
        if buffering < 0:
            raise ValueError("invalid buffering size")
        if buffering == 0:
            if binary:
                return result
            raise ValueError("can't have unbuffered text I/O")
        if creating or writing or appending:
            buffer = BufferedBISBinaryWriter(raw, buffering)
        elif reading:
            buffer = BufferedBISBinaryReader(raw, buffering)
        else:
            raise ValueError("unknown mode: %r" % mode)
        result = buffer
        
        return result
    except:
        result.close()
        raise


class BufferedBISBinaryReader(io.BufferedReader):
    def read_byte(self):
        return struct.unpack('B', self.read(1))[0]
        
    def read_bytes(self, count = 1):
        return [self.read_byte() for i in range(count)]

    def read_bool(self):
        return self.read_byte() != 0
        
    def read_short(self):
        return struct.unpack('<h', self.read(2))[0]

    def read_shorts(self, count = 1):
        return struct.unpack('<%dh' % count, self.read(2 * count))
        
    def read_ushort(self):
        return struct.unpack('<H', self.read(2))[0]

    def read_ushorts(self, count = 1):
        return struct.unpack('<%dH' % count, self.read(2 * count))

    def read_long(self):
        return struct.unpack('<i', self.read(4))[0]

    def read_longs(self, count = 1):
        return struct.unpack('<%di' % count, self.read(4 * count))

    def read_ulong(self):
        return struct.unpack('<I', self.read(4))[0]

    def read_ulongs(self, count = 1):
        return struct.unpack('<%dI' % count, self.read(4 * count))

    def read_compressed_uint(self):
        output = self.read_byte()
        extra = output
        
        byte_idx = 1
        while extra & 0x80:
            extra = self.read_byte()
            output += (extra - 1) << (byte_idx * 7)
            byte_idx += 1
        
        return output
        
    def read_float(self):
        return struct.unpack('<f', self.read(4))[0]

    def read_floats(self, count = 1):
        return struct.unpack('<%df' % count, self.read(4 * count))
        
    def read_double(self):
        return struct.unpack('<d', self.read(8))[0]

    def read_doubles(self, count = 1):
        return struct.unpack('<%dd' % count, self.read(8 * count))
        
    def read_char(self, count = 1):
        chars = struct.unpack('%ds' % count, self.read(count))[0]
        return chars.decode('ascii')
        
    def read_asciiz(self):
        res = b''
        
        while True:
            a = self.read(1)
            if a == b'\x00' or a == b'':
                break
                
            res += a
        
        return res.decode('ascii')

    def read_asciiz_field(self, field_len):
        field = self.read(field_len)
        if len(field) < field_len:
            raise EOFError("ASCIIZ field ran into unexpected EOF")
        
        result = bytearray()
        for value in field:
            if value == 0:
                break
                
            result.append(value)
        else:
            raise ValueError("ASCIIZ field length overflow")
        
        return result.decode('ascii')
            
    def read_lascii(self):
        length = self.read_byte()
        value = self.read(length)
        if len(value) != length:
            raise EOFError("LASCII string ran into unexpected EOF")
        
        return value.decode('ascii')

    # def read_asciiz_padded(self, max_len = 0):
    #     value = self.read_asciiz()

    #     diff = max_len - (len(value) + 1)
    #     if diff > 0:
    #         self.read(diff)

    #     return value


class BufferedBISBinaryWriter(io.BufferedWriter):
    def write_byte(self, value):
        self.write(struct.pack('B', value))
        
    def write_bytes(self, values):
        self.write(struct.pack('%dB' % len(values), *values))
        
    def write_bool(self, value):
        self.write_byte(value)
        
    def write_short(self, *args):
        self.write(struct.pack('<%dh' % len(args), *args))
        
    def write_ushort(self, *args):
        self.write(struct.pack('<%dH' % len(args), *args))
        
    def write_long(self, *args):
        self.write(struct.pack('<%di' % len(args), *args))
        
    def write_ulong(self, *args):
        self.write(struct.pack('<%dI' % len(args), *args))

    def write_compressed_uint(self, value):
        temp = value
        while True:
            if temp < 128:
                self.write_byte(temp)
                break

            self.write_byte((temp & 127) + 128)
            temp = temp >> 7
        
    def write_float(self, *args):
        self.write(struct.pack('<%df' % len(args), *args))
        
    def write_double(self, *args):
        self.write(struct.pack('<%dd' % len(args), *args))
        
    def write_chars(self, values):
        self.write(struct.pack('<%ds' % len(values), values.encode('ascii')))
        
    def write_asciiz(self, value):
        self.write(struct.pack('<%ds' % (len(value) + 1), value.encode('ascii')))

    def write_asciiz_field(self, value, field_len):
        if (len(value) + 1) > field_len:
            raise ValueError("ASCIIZ value is longer (%d + 1) than field length (%d)" % (len(value), field_len))

        self.write(struct.pack('<%ds' % field_len, value.encode('ascii')))