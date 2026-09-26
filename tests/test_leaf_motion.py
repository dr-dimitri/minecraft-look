"""Leaf motion must retain the exact color/alpha population of each source."""
from collections import Counter
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import leaf_motion
from texture_pixels import read_rgba
import validate


class LeafMotionTests(unittest.TestCase):
    def test_every_leaf_variant_is_bound_without_overriding_other_animations(self):
        entries = leaf_motion.atlas_entries(validate.ROOT)
        self.assertEqual(len(entries), 16)  # 14 current atlas entries + 2 legacy arrays.
        definitions = validate.load(validate.PACK / leaf_motion.FLIPBOOK)
        self.assertEqual(len(definitions), 40)
        starting_frames = set()
        phases_by_texture = {}
        for definition in definitions:
            tile, index = definition['atlas_tile'], definition['atlas_index']
            self.assertIn('leaves', tile)
            self.assertNotIn('carried', tile)
            texture = entries[tile][index]
            self.assertEqual(definition['flipbook_texture'].rsplit('/', 1)[1], texture.rsplit('/', 1)[1])
            frames = definition['frames']
            self.assertEqual(sorted(frames), list(range(10)))
            self.assertTrue(all(next_frame == (frame+1) % 10
                                for frame, next_frame in zip(frames, frames[1:] + frames[:1])))
            starting_frames.add(frames[0])
            old_phase = phases_by_texture.setdefault(definition['flipbook_texture'], frames[0])
            self.assertEqual(old_phase, frames[0])
            self.assertEqual(definition['ticks_per_frame'] * len(definition['frames']), 100)
            self.assertTrue(definition['blend_frames'])
        self.assertGreaterEqual(len(starting_frames), 5)

    def test_all_frames_preserve_pixels_alpha_and_gentle_seamless_motion(self):
        sources = {name for names in leaf_motion.atlas_entries(validate.ROOT).values() for name in names}
        self.assertEqual(len(sources), 28)
        for name in sources:
            with self.subTest(texture=name):
                source = validate.ROOT / 'reference/resource_pack' / (name + '.tga')
                if not source.exists():
                    source = source.with_suffix('.png')
                width, height, original = read_rgba(source)
                path = validate.PACK / (leaf_motion.PREFIX + source.stem + '.png')
                w, h, frames = read_rgba(path)
                self.assertEqual((w, h), (width, height*10))
                size = width * height * 4
                self.assertEqual(frames[:size], original)
                self.assertEqual(frames[9*size:10*size], original)
                self.assertEqual(frames[2*size:3*size], frames[3*size:4*size])
                self.assertNotEqual(frames[size:2*size], original)
                for frame in range(10):
                    pixels = frames[frame*size:(frame+1)*size]
                    for y in range(height):
                        row = [original[(y*width+x)*4:(y*width+x+1)*4] for x in range(width)]
                        animated = [pixels[(y*width+x)*4:(y*width+x+1)*4] for x in range(width)]
                        self.assertEqual(Counter(animated), Counter(row))
                        for x, pixel in enumerate(animated):
                            self.assertIn(pixel, [row[(x+offset) % width] for offset in (-1, 0, 1)])
                        if y < height//4 or y >= 3*height//4:
                            self.assertEqual(animated, row)

    def test_wind_passes_through_upper_and_lower_leaf_bands(self):
        width = height = 16
        original = bytes(channel for y in range(height) for x in range(width)
                         for channel in (x, y, x ^ y, (x * 17 + y * 13) % 256))
        frames = leaf_motion.leaf_frames(width, height, original)
        size = width * height * 4

        def pixel(frame, x, y):
            start = frame*size + (y*width+x)*4
            return frames[start:start+4]

        # The upper band bends first; the lower band follows. Both return to
        # the source between gusts, while the outer rows stay anchored.
        self.assertNotEqual(pixel(1, 4, 5), pixel(0, 4, 5))
        self.assertEqual(pixel(1, 4, 9), pixel(0, 4, 9))
        self.assertNotEqual(pixel(2, 4, 9), pixel(0, 4, 9))
        self.assertEqual(frames[5*size:6*size], original)
        self.assertNotEqual(pixel(7, 4, 5), pixel(0, 4, 5))
        self.assertNotEqual(pixel(7, 4, 9), pixel(0, 4, 9))
        self.assertEqual(frames[9*size:10*size], original)

    def test_duplicate_or_missing_animation_binding_is_rejected(self):
        files = {p.relative_to(validate.PACK).as_posix(): validate.load(p)
                 for p in validate.PACK.rglob('*.json') if 'subpacks' not in p.parts}
        for duplicate in (False, True):
            changed = copy.deepcopy(files)
            if duplicate:
                changed[leaf_motion.FLIPBOOK].append(changed[leaf_motion.FLIPBOOK][0])
            else:
                changed[leaf_motion.FLIPBOOK].pop()
            with self.assertRaisesRegex(ValueError, 'leaf animation binding'):
                leaf_motion.validate_resources(changed, validate.ROOT, validate.PACK)

    def test_missing_leaf_texture_registration_is_rejected(self):
        files = {p.relative_to(validate.PACK).as_posix(): validate.load(p)
                 for p in validate.PACK.rglob('*.json') if 'subpacks' not in p.parts}
        files['textures/textures_list.json'].remove(leaf_motion.PREFIX + 'leaves_oak')
        with self.assertRaisesRegex(ValueError, 'Leaf textures not registered'):
            leaf_motion.validate_resources(files, validate.ROOT, validate.PACK)

    def test_disrupted_phase_order_is_rejected(self):
        files = {p.relative_to(validate.PACK).as_posix(): validate.load(p)
                 for p in validate.PACK.rglob('*.json') if 'subpacks' not in p.parts}
        files[leaf_motion.FLIPBOOK][0]['frames'][1:3] = reversed(files[leaf_motion.FLIPBOOK][0]['frames'][1:3])
        with self.assertRaisesRegex(ValueError, 'gentle seamless cycle'):
            leaf_motion.validate_resources(files, validate.ROOT, validate.PACK)


if __name__ == '__main__':
    unittest.main()
