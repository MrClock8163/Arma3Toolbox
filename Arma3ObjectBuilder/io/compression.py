# Algorithms for handling compressed data blocks in Arma 3 file formats.


import struct


class LZO_Error(Exception):
    def __str__(self):
        return "LZO - %s" % super().__str__()


# Decompression algorithm for bit streams compressed with the LZO1X algorithm.
# Implementation is based on the LZO stream format documentation included in the Linux kernel documentations:
# https://docs.kernel.org/staging/lzo.html
# Some inspiration was taken from the C implementation found in the FFMPEG libavutil library:
# https://github.com/FFmpeg/FFmpeg/blob/master/libavutil/lzo.c
# The original LZO implementations as defined by Markus F.X.J. Oberhumer:
# https://www.oberhumer.com/opensource/lzo/
def lzo1x_decompress(file, expected):
    state = 0
    start = file.tell()
    output = bytearray()

    def check_free_space(length):
        output_length = len(output)
        free_space = expected - output_length
        if free_space < length:
            raise LZO_Error("Output overrun (free buffer: %d, match length: %d)" % (expected - output_length, length))

    def read1():
        nonlocal file
        return struct.unpack('B', file.read(1))[0]

    def read(size):
        nonlocal file
        return struct.unpack('%dB' % size, file.read(size))
    
    def read_le16():
        nonlocal file
        return struct.unpack('<H', file.read(2))[0]
    
    def extend(items):
        nonlocal output
        output.extend(items)
    
    def append(item):
        nonlocal output
        output.append(item)

    def copy_literal(length):
        check_free_space(length)
        extend(read(length))
    
    def copy_match(distance, length):
        nonlocal output
        output_length = len(output)

        if output_length < distance:
            raise LZO_Error("Invalid back pointer (buffer: %d, pointer: %d)" % (output_length, -distance))
        
        check_free_space(length)
        
        # It is valid to have length that is longer than the back pointer distance, which creates a repeating pattern,
        # copying the same bytes that were copied in this same command.
        # For this reason, we cannot simply take a slice of the output at the given point with the given length, as
        # some of the bytes might not yet be there. We have to copy 1 by 1, like the C implementations.
        ptr = output_length - distance
        for i in range(length):
            append(output[ptr])
            ptr += 1
    
    def get_length(x, mask):
        nonlocal file

        length = x & mask
        if not length:
            while True:
                x = read1()
                if x:
                    break
                
                length += 255
            length += mask + x
        return length
    
    # # First byte is handled separately, as the output buffer is empty at this point.
    x = read1()
    if x > 17:
        length = x - 17
        copy_literal(length)
        state = min(4, length)
        x = read1()
    
    while True:        
        if x > 127:
            state = x & 3
            length = 5 + ((x >> 5) & 3)
            distance = (read1() << 3) + ((x >> 2) & 7) + 1
            copy_match(distance, length)
            copy_literal(state)
        elif x > 63:
            state = x & 3
            length = 3 + ((x >> 5) & 1)
            distance = (read1() << 3) + ((x >> 2) & 7) + 1
            copy_match(distance, length)
            copy_literal(state)
        elif x > 31:
            length = 2 + get_length(x, 31)
            extra = read_le16()
            distance = (extra >> 2) + 1
            state = extra & 3
            copy_match(distance, length)
            copy_literal(state)
        elif x > 15:
            length = 2 + get_length(x, 7)
            extra = read_le16()
            distance = 16384 + ((x & 8) << 11) + (extra >> 2)
            state = extra & 3
            if distance == 16384:
                if length != 3:
                    raise LZO_Error("Invalid End Of Stream (expected match length: 3, got: %s)" % length)
                # End of Stream reached
                break
            
            copy_match(distance, length)
            copy_literal(state)
        else:
            if not state:
                length = 3 + get_length(x, 15)
                copy_literal(length)
                state = 4
            elif state < 4:
                length = 2
                state = x & 3
                distance = (read1() << 2) + (x >> 2) + 1
                copy_match(distance, length)
                copy_literal(state)
            elif state == 4:
                length = 3
                state = x & 3
                distance = (read1() << 2) + (x >> 2) + 2049
                copy_match(distance, length)
                copy_literal(state)
        
        x = read1()

    if expected - len(output):
        raise LZO_Error("Stream provided shorter output than expected (expected: %d, got: %d)" % (expected, len(output)))
    
    return file.tell() - start, output
