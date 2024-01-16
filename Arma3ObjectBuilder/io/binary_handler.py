# Wrapper functions to simplify the reading/writing of simple binary data types
# used in the BI file formats, as outlined on the community wiki:
# https://community.bistudio.com/wiki/Generic_FileFormat_Data_Types


import struct


def read_byte(file):
    return struct.unpack('B', file.read(1))[0]
    
def read_bytes(file, count = 1):
    return [read_byte(file) for i in range(count)]

def read_bool(file):
    return read_byte(file) != 0
    
def read_short(file):
    return struct.unpack('<h', file.read(2))[0]

def read_shorts(file, count = 1):
    return struct.unpack('<%dh' % count, file.read(2 * count))
    
def read_ushort(file):
    return struct.unpack('<H', file.read(2))[0]

def read_shorts(file, count = 1):
    return struct.unpack('<%dH' % count, file.read(2 * count))

def read_long(file):
    return struct.unpack('<i', file.read(4))[0]

def read_longs(file, count = 1):
    return struct.unpack('<%di' % count, file.read(4 * count))

def read_ulong(file):
    return struct.unpack('<I', file.read(4))[0]

def read_ulongs(file, count = 1):
    return struct.unpack('<%dI' % count, file.read(4 * count))

def read_compressed_uint(file):
    output = 0
    extra = 0
    
    output = read_byte(file)
    extra = output
    
    while extra & 0x80:
        extra = read_byte(file)
        output += (extra - 1) * 0x80
    
    return output
    
def read_float(file):
    return struct.unpack('<f', file.read(4))[0]

def read_floats(file, count = 1):
    return struct.unpack('<%df' % count, file.read(4 * count))
    
def read_double(file):
    return struct.unpack('<d', file.read(8))[0]

def read_doubles(file, count = 1):
    return struct.unpack('<%dd' % count, file.read(8 * count))
    
def read_char(file, count = 1):
    chars = struct.unpack('%ds' % count, file.read(count))[0]
    return chars.decode('ascii')
    
def read_asciiz(file):
    res = b''
    
    while True:
        a = file.read(1)
        if a == b'\x00':
            break
            
        res += a
    
    return res.decode('ascii')

def read_lascii(file):
    return file.read(read_byte(file)).decode('ascii')

def read_asciiz_padded(file, max_len = 0):
    value = read_asciiz(file)

    diff = max_len - (len(value) + 1)
    if diff > 0:
        file.read(diff)

    return value
    
def write_byte(file, value):
    file.write(struct.pack('B', value))
    
def write_bytes(file, values):
    file.write(struct.pack('%dB' % len(values), *values))
    
def write_bool(file, value):
    write_byte(file, value)
    
def write_short(file, *args):
    file.write(struct.pack('<%dh' % len(args), *args))
    
def write_ushort(file, *args):
    file.write(struct.pack('<%dH' % len(args), *args))
    
def write_long(file, *args):
    file.write(struct.pack('<%di' % len(args), *args))
    
def write_ulong(file, *args):
    file.write(struct.pack('<%dI' % len(args), *args))
    
def write_float(file, *args):
    file.write(struct.pack('<%df' % len(args), *args))
    
def write_double(file, *args):
    file.write(struct.pack('<%dd' % len(args), *args))
    
def write_chars(file, values):
    file.write(struct.pack('<%ds' % len(values), values.encode('ascii')))
    
def write_asciiz(file, value):
    file.write(struct.pack('<%ds' % (len(value) + 1), value.encode('ascii')))

def write_lascii(file, value):
    file.write(struct.pack('b'))