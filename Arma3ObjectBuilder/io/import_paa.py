import os
import time
from io import BytesIO, BufferedReader
from copy import deepcopy

import bpy

from .compression import dxt1_decompress, dxt5_decompress, lzo1x_decompress
from . import data_paa as paa
from ..utilities.logger import ProcessLogger


def swizzle(r, g, b, a, code):
    src = [deepcopy(a), deepcopy(r), deepcopy(g), deepcopy(b)]
    trg = [a, r, g, b]

    for op, frm, ch_idx in zip(code, src, [0, 1, 2, 3]):
        if op == ch_idx:
            continue
        
        target = trg[op & 3]
        if op >> 3 & 1:
            for i in range(len(target)):
                target[i] = 1
        elif op >> 2 & 1:
            for i in range(len(target)):
                target[i] = 1 - frm[i]
    
    return r, g, b, a


def decompress_mip(mip, format):
    if format == paa.PAA_Type.DXT1:
        decompressor = dxt1_decompress
        lzo_expected = mip.width * mip.height // 2
    elif format == paa.PAA_Type.DXT5:
        decompressor = dxt5_decompress
        lzo_expected = mip.width * mip.height
    else:
        return None
    
    if mip.lzo_compressed:
        stream_lzo = BytesIO(mip.data_raw)
        reader_lzo = BufferedReader(stream_lzo)
        consumed, data = lzo1x_decompress(reader_lzo, lzo_expected)
    else:
        data = mip.data_raw
    
    stream_dxt = BytesIO(data)
    reader_dxt = BufferedReader(stream_dxt)
    return decompressor(reader_dxt, mip.width, mip.height)


def import_file(operator, context, file):
    logger = ProcessLogger()
    logger.step("PAA import from %s" % operator.filepath)
    wm = context.window_manager
    wm.progress_begin(0, 1000)
    wm.progress_update(0)

    time_start = time.time()
    tex = paa.PAA_File.read(file)
    alpha = tex.type == paa.PAA_Type.DXT5

    logger.log("File report:")
    logger.level_up()
    logger.log("Format: %s" % tex.type.name)
    logger.log("Taggs: %d" % len(tex.taggs))
    for i, mip in enumerate(tex.mips):
        wm.progress_update(i + 1)
        logger.log("MIPMAP %d: %d x %d" % (i + 1, mip.width, mip.height))
    logger.level_down()

    if tex.type not in [paa.PAA_Type.DXT1, paa.PAA_Type.DXT5]:
        logger.log("Unsupported texture format")
        logger.step("PAA import terminated")
        return None, tex

    logger.log("Porcessing 1st mipmap")
    mip = tex.mips[0]
    r, g, b, a = decompress_mip(mip, tex.type)
    for tagg in tex.taggs:
        if tagg.name != "SWIZ":
            continue
        r, g, b, a = swizzle(r, g, b, a, tagg.data)

    data = []
    for i in range(mip.height):
        rows = []
        idx = i * mip.width
        idx_end = idx + mip.width
        for c in zip(r[idx:idx_end], g[idx:idx_end], b[idx:idx_end], a[idx:idx_end]):
            rows.extend(c)

        data.append(rows)

    img = bpy.data.images.new(os.path.basename(operator.filepath), mip.width, mip.height, alpha=alpha)
    img.filepath_raw = operator.filepath
    if alpha:
        img.alpha_mode = 'PREMUL'
    img.pixels[:] = [value for row in reversed(data) for value in row][:]
    img.update()
    img.pack()

    wm.progress_end()
    logger.step("PAA import finished in %f sec" % (time.time() - time_start))

    return img, tex
