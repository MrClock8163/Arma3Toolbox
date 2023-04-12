import struct
    
def readByte(file):
    return struct.unpack('B',file.read(1))[0]
    
def readBytes(file,count = 1):
    return [readByte(file) for i in range(count)]

def readBool(file):
    return readByte(file) != 0
    
def readShort(file):
    return struct.unpack('<h',file.read(2))[0]
    
def readUShort(file):
    return struct.unpack('<H',file.read(2))[0]

def readLong(file):
    return struct.unpack('<i',file.read(4))[0]

def readULong(file):
    return struct.unpack('<I',file.read(4))[0]
    
def readFloat(file):
    return struct.unpack('<f',file.read(4))[0]
    
def readDouble(file):
    return struct.unpack('<d',file.read(8))[0]
    
def readChar(file,count = 1):
    chars = struct.unpack(f'{count}s',file.read(count))[0]
    return chars.decode('utf-8')
    
def readAsciiz(file):
    string = ""
    while file.peek(1)[:1] != b'\000':
        string += readChar(file)
        
    readByte(file)
    return string