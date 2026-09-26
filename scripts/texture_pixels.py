"""Lossless pixel access for the pinned 8-bit PNG and 32-bit TGA sources.

No image library is needed for normal builds. Unsupported formats fail closed.
"""
import struct
import zlib


def encode_png(width, height, rgba):
    if width <= 0 or height <= 0 or len(rgba) != width * height * 4:
        raise ValueError('Invalid RGBA dimensions')
    rows = b''.join(b'\0' + rgba[y*width*4:(y+1)*width*4] for y in range(height))
    # Stored blocks keep generated PNG bytes independent of the zlib encoder.
    payload = bytearray(b'\x78\x01')
    for start in range(0, len(rows), 65535):
        block = rows[start:start+65535]
        payload.append(int(start + len(block) == len(rows)))
        payload.extend(struct.pack('<HH', len(block), len(block) ^ 0xffff))
        payload.extend(block)
    payload.extend(struct.pack('>I', zlib.adler32(rows)))
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', bytes(payload)) + chunk(b'IEND', b''))


def read_rgba(path):
    raw = path.read_bytes()
    if path.suffix == '.tga':
        if len(raw) < 18 or raw[1:3] != b'\0\x02' or raw[16] != 32 or raw[17] & 0xc0:
            raise ValueError(f'Unsupported TGA: {path}')
        width, height = struct.unpack('<HH', raw[12:16])
        offset = 18 + raw[0]
        pixels = raw[offset:offset+width*height*4]
        if not width or not height or len(pixels) != width*height*4:
            raise ValueError(f'Truncated TGA: {path}')
        rgba = bytearray()
        for y in range(height):
            sy = y if raw[17] & 0x20 else height - 1 - y
            for x in range(width):
                sx = width - 1 - x if raw[17] & 0x10 else x
                b, g, r, a = pixels[(sy*width+sx)*4:(sy*width+sx+1)*4]
                rgba.extend((r, g, b, a))
        return width, height, bytes(rgba)
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Invalid PNG: {path}')
    chunks, data, position = {}, bytearray(), 8
    while position < len(raw):
        length = struct.unpack('>I', raw[position:position+4])[0]
        kind, value = raw[position+4:position+8], raw[position+8:position+8+length]
        crc = struct.unpack('>I', raw[position+8+length:position+12+length])[0]
        if zlib.crc32(kind+value) != crc:
            raise ValueError(f'PNG checksum failed: {path}')
        if kind == b'IDAT':
            data.extend(value)
        else:
            chunks[kind] = value
        position += length + 12
    width, height, depth, kind, compression, filtering, interlace = struct.unpack('>IIBBBBB', chunks[b'IHDR'])
    if depth != 8 or kind not in (2, 3, 6) or compression or filtering or interlace or not width or not height:
        raise ValueError(f'Unsupported PNG: {path}')
    channels = {2: 3, 3: 1, 6: 4}[kind]
    stride = width * channels
    scanlines = zlib.decompress(data)
    if len(scanlines) != (stride+1)*height:
        raise ValueError(f'Invalid PNG scanlines: {path}')
    previous, rgba = bytearray(stride), bytearray()
    for y in range(height):
        mode = scanlines[y*(stride+1)]
        row = bytearray(scanlines[y*(stride+1)+1:(y+1)*(stride+1)])
        if mode not in range(5):
            raise ValueError(f'Invalid PNG filter: {path}')
        for i in range(stride):
            left = row[i-channels] if i >= channels else 0
            up = previous[i]
            corner = previous[i-channels] if i >= channels else 0
            p = left + up - corner
            paeth = min((left, up, corner), key=lambda candidate: abs(p-candidate))
            row[i] = (row[i] + (0, left, up, (left+up)//2, paeth)[mode]) & 255
        for x in range(width):
            pixel = row[x*channels:(x+1)*channels]
            if kind == 3:
                index = pixel[0]
                palette, alpha = chunks[b'PLTE'], chunks.get(b'tRNS', b'')
                pixel = palette[index*3:index*3+3] + bytes([alpha[index] if index < len(alpha) else 255])
            elif kind == 2:
                pixel += b'\xff'
            rgba.extend(pixel)
        previous = row
    return width, height, bytes(rgba)
