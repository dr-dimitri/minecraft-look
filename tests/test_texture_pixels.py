"""Portable decoding of pinned artwork; verifies colors, orientation and alpha."""
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from texture_pixels import encode_png, read_rgba


class TexturePixelTests(unittest.TestCase):
    def test_tga_bottom_origin_and_bgra_are_converted_without_color_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.tga'
            header = bytearray(18)
            header[2] = 2
            header[12:18] = struct.pack('<HHBB', 1, 2, 32, 8)
            path.write_bytes(header + bytes([30, 20, 10, 40, 70, 60, 50, 80]))
            self.assertEqual(read_rgba(path), (1, 2, bytes([50, 60, 70, 80, 10, 20, 30, 40])))

    def test_indexed_png_keeps_palette_and_transparency(self):
        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data))
        data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 1, 8, 3, 0, 0, 0))
                + chunk(b'PLTE', bytes([10, 20, 30, 40, 50, 60])) + chunk(b'tRNS', bytes([0, 123]))
                + chunk(b'IDAT', zlib.compress(bytes([0, 0, 1]))) + chunk(b'IEND', b''))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.png'
            path.write_bytes(data)
            self.assertEqual(read_rgba(path), (2, 1, bytes([10, 20, 30, 0, 40, 50, 60, 123])))

    def test_stored_png_supports_multiple_deflate_blocks_and_rejects_corruption(self):
        pixels = bytes(range(256)) * 512
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'large.png'
            raw = encode_png(256, 128, pixels)
            path.write_bytes(raw)
            self.assertEqual(read_rgba(path), (256, 128, pixels))
            corrupt = bytearray(raw)
            corrupt[100] ^= 1
            path.write_bytes(corrupt)
            with self.assertRaisesRegex(ValueError, 'checksum'):
                read_rgba(path)


if __name__ == '__main__':
    unittest.main()
