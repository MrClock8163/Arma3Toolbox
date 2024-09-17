# Wrapper functions to simplify the reading/writing of simple binary data types
# used in the BI file formats, as outlined on the community wiki:
# https://community.bistudio.com/wiki/Generic_FileFormat_Data_Types


import struct
from io import BufferedReader, BufferedWriter


def read_byte(file: BufferedReader) -> int:
    return struct.unpack('B', file.read(1))[0]
    
def read_bytes(file: BufferedReader, count: int = 1) -> list[int]:
    return [read_byte(file) for i in range(count)]

def read_bool(file: BufferedReader) -> bool:
    return read_byte(file) != 0
    
def read_short(file: BufferedReader) -> int:
    return struct.unpack('<h', file.read(2))[0]

def read_shorts(file: BufferedReader, count: int = 1) -> tuple[int]:
    return struct.unpack('<%dh' % count, file.read(2 * count))
    
def read_ushort(file: BufferedReader) -> int:
    return struct.unpack('<H', file.read(2))[0]

def read_ushorts(file: BufferedReader, count: int = 1) -> tuple[int]:
    return struct.unpack('<%dH' % count, file.read(2 * count))

def read_long(file: BufferedReader) -> int:
    return struct.unpack('<i', file.read(4))[0]

def read_longs(file: BufferedReader, count: int = 1) -> tuple[int]:
    return struct.unpack('<%di' % count, file.read(4 * count))

def read_ulong(file: BufferedReader) -> int:
    return struct.unpack('<I', file.read(4))[0]

def read_ulongs(file: BufferedReader, count: int = 1) -> int:
    return struct.unpack('<%dI' % count, file.read(4 * count))

def read_compressed_uint(file: BufferedReader) -> int:
    output = read_byte(file)
    extra = output
    
    byte_idx = 1
    while extra & 0x80:
        extra = read_byte(file)
        output += (extra - 1) << (byte_idx * 7)
        byte_idx += 1
    
    return output

def read_half(file: BufferedReader) -> int:
    return struct.unpack('<e', file.read(2))[0]

def read_halfs(file: BufferedReader, count: int = 1) -> tuple[int]:
    return struct.unpack('<%de' % count, file.read(2 * count))
    
def read_float(file: BufferedReader) -> float:
    return struct.unpack('<f', file.read(4))[0]

def read_floats(file: BufferedReader, count: int = 1) -> tuple[float]:
    return struct.unpack('<%df' % count, file.read(4 * count))
    
def read_double(file: BufferedReader) -> float:
    return struct.unpack('<d', file.read(8))[0]

def read_doubles(file: BufferedReader, count: int = 1) -> float:
    return struct.unpack('<%dd' % count, file.read(8 * count))
    
def read_char(file: BufferedReader, count: int = 1) -> str:
    chars = struct.unpack('%ds' % count, file.read(count))[0]
    return chars.decode('ascii')

# In theory all strings in BI files should be strictly ASCII,
# but on the off chance that a corrupt character is present, the method would fail.
# Therefore using UTF-8 decoding is more robust, and gives the same result for valid ASCII values.
def read_asciiz(file: BufferedReader) -> str:
    res = b''
    
    while True:
        a = file.read(1)
        if a == b'\x00' or a == b'':
            break
            
        res += a
    
    return res.decode('utf8', errors="replace")

def read_asciiz_field(file: BufferedReader, field_len: int) -> str:
    field = file.read(field_len)
    if len(field) < field_len:
        raise EOFError("ASCIIZ field ran into unexpected EOF")
    
    result = bytearray()
    for value in field:
        if value == 0:
            break
            
        result.append(value)
    else:
        raise ValueError("ASCIIZ field length overflow")
    
    return result.decode('utf8', errors="replace")
        
def read_lascii(file: BufferedReader) -> str:
    length = read_byte(file)
    value = file.read(length)
    if len(value) != length:
        raise EOFError("LASCII string ran into unexpected EOF")
    
    return value.decode('utf8', errors="replace")
    
def write_byte(file: BufferedWriter, *args) -> None:
    file.write(struct.pack('%dB' % len(args), *args))
    
def write_bool(file: BufferedWriter, value: bool) -> None:
    write_byte(file, value)
    
def write_short(file: BufferedWriter, *args: int) -> None:
    file.write(struct.pack('<%dh' % len(args), *args))
    
def write_ushort(file: BufferedWriter, *args: int) -> None:
    file.write(struct.pack('<%dH' % len(args), *args))
    
def write_long(file: BufferedWriter, *args: int) -> None:
    file.write(struct.pack('<%di' % len(args), *args))
    
def write_ulong(file: BufferedWriter, *args: int) -> None:
    file.write(struct.pack('<%dI' % len(args), *args))

def write_compressed_uint(file: BufferedWriter, value: int) -> None:
    temp = value
    while True:
        if temp < 128:
            write_byte(file, temp)
            break

        write_byte(file, (temp & 127) + 128)
        temp = temp >> 7

def write_half(file: BufferedWriter, *args: int) -> None:
    file.write(struct.pack('<%de' % len(args), *args))
    
def write_float(file: BufferedWriter, *args: int) -> None:
    file.write(struct.pack('<%df' % len(args), *args))
    
def write_double(file: BufferedWriter, *args: int) -> None:
    file.write(struct.pack('<%dd' % len(args), *args))
    
def write_chars(file: BufferedWriter, values: str) -> None:
    file.write(struct.pack('<%ds' % len(values), values.encode('ascii')))
    
def write_asciiz(file: BufferedWriter, value: str) -> None:
    file.write(struct.pack('<%ds' % (len(value) + 1), value.encode('ascii')))

def write_asciiz_field(file: BufferedWriter, value: str, field_len: int) -> None:
    if (len(value) + 1) > field_len:
        raise ValueError("ASCIIZ value is longer (%d + 1) than field length (%d)" % (len(value), field_len))

    file.write(struct.pack('<%ds' % field_len, value.encode('ascii')))

def write_lascii(file: BufferedWriter, value: str) -> None:
    length = len(value)
    if length > 255:
        raise ValueError("LASCII string cannot be longer than 255 characters")
    
    file.write(struct.pack('B%ds' % length, length, value.encode('ascii')))
