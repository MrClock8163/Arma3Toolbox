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
    res = b''
    
    while True:
        a = file.read(1)
        if a == b'\000':
            break
            
        res += a
    
    return res.decode("utf-8")
    
def writeByte(file,value):
    file.write(struct.pack('B',value))
    
def writeBytes(file,values):
    file.write(struct.pack('%dB' % len(values),*values))
    
def writeBool(file,value):
    writeByte(file,value)
    
def writeShort(file,value):
    file.write(struct.pack('<h',value))
    
def writeShort(file,value):
    file.write(struct.pack('<H',value))
    
def writeLong(file,value):
    file.write(struct.pack('<i',value))
    
def writeULong(file,value):
    file.write(struct.pack('<I',value))
    
def writeFloat(file,value):
    file.write(struct.pack('<f',value))
    
def writeDouble(file,value):
    file.write(struct.pack('<d',value))
    
def writeChars(file,values):
    file.write(struct.pack('<%ds' % len(values),values.encode('ASCII')))
    
def writeAsciiz(file,value):
    file.write(struct.pack('<%ds' % (len(value)+1),value.encode('ASCII')))