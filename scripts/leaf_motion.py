"""Gentle five-second leaf sway; no geometry or palette modification."""
import hashlib
import json
from texture_pixels import encode_png, read_rgba

FLIPBOOK = 'textures/flipbook_textures.json'
PREFIX = 'textures/lumen/leaves/'
TICKS_PER_FRAME = 10
# Two adjacent bands move in succession, like a small gust passing through the
# leaves. A short hold at the positive peak and a quicker return break the
# regular left/right pendulum of the old four-frame animation.
FRAME_SHIFTS = (
    (0, 0), (1, 0), (1, 1), (1, 1), (0, 1),
    (0, 0), (-1, 0), (-1, -1), (0, -1), (0, 0),
)
FRAMES = tuple(range(len(FRAME_SHIFTS)))


def animation_frames(texture):
    # A stable per-texture phase prevents every tree species from swaying in
    # lockstep. Rotating the order keeps the same seamless loop and sprite strip.
    name = texture.rsplit('/', 1)[1]
    phase = int.from_bytes(hashlib.sha256(name.encode('utf-8')).digest()[:2], 'big') % len(FRAMES)
    return list(FRAMES[phase:] + FRAMES[:phase])


def atlas_entries(root):
    # The pinned file has one introductory // comment; retain the original bytes
    # in reference and parse only its JSON body, without copying the full atlas.
    text = (root / 'reference/resource_pack/textures/terrain_texture.json').read_text(encoding='utf-8')
    terrain = json.loads(text[text.index('{'):])['texture_data']
    return {key: value['textures'] for key, value in terrain.items()
            if 'leaves' in key and 'carried' not in key}


def leaf_frames(width, height, rgba):
    if width != height or len(rgba) != width * height * 4:
        raise ValueError('Leaf input must be a square RGBA texture')
    result = bytearray()
    # The first frame is the original. Cyclic row permutations conserve every
    # RGBA pixel, including alpha, in every frame. No filtering or recoloring.
    for upper_shift, lower_shift in FRAME_SHIFTS:
        for y in range(height):
            if height//4 <= y < height//2:
                shift = upper_shift
            elif height//2 <= y < 3*height//4:
                shift = lower_shift
            else:
                shift = 0
            for x in range(width):
                start = (y*width + (x-shift) % width)*4
                result.extend(rgba[start:start+4])
    return bytes(result)


def generate(root, pack, write):
    entries = atlas_entries(root)
    textures = sorted({name for names in entries.values() for name in names})
    generated = []
    for texture in textures:
        source = root / 'reference/resource_pack' / (texture + '.tga')
        if not source.is_file():
            source = source.with_suffix('.png')
        width, height, rgba = read_rgba(source)
        name = PREFIX + source.stem
        path = pack / (name + '.png')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encode_png(width, height*len(FRAME_SHIFTS), leaf_frames(width, height, rgba)))
        generated.append(name)
    animations = []
    for tile, names in entries.items():
        for variant, name in enumerate(names):
            animations.append({
                'flipbook_texture': PREFIX + name.rsplit('/', 1)[1],
                'atlas_tile': tile,
                'atlas_index': variant,
                'atlas_tile_variant': variant,
                'ticks_per_frame': TICKS_PER_FRAME,
                'frames': animation_frames(name),
                'blend_frames': True,
            })
    write(pack / FLIPBOOK, animations)
    return generated


def validate_resources(files, root, pack):
    entries = atlas_entries(root)
    expected = {(tile, i): PREFIX + name.rsplit('/', 1)[1]
                for tile, names in entries.items() for i, name in enumerate(names)}
    animations = files.get(FLIPBOOK, [])
    actual = {(item['atlas_tile'], item['atlas_tile_variant']): item['flipbook_texture'] for item in animations}
    if actual != expected or len(animations) != len(expected):
        raise ValueError('Missing, duplicate or unexpected leaf animation binding')
    if not set(expected.values()).issubset(files['textures/textures_list.json']):
        raise ValueError('Leaf textures not registered')
    for item in animations:
        if (item['atlas_index'] != item['atlas_tile_variant']
                or item['frames'] != animation_frames(item['flipbook_texture'])
                or item['ticks_per_frame'] != TICKS_PER_FRAME or item['blend_frames'] is not True):
            raise ValueError('Leaf animation must retain the gentle seamless cycle')
    for name in set(expected.values()):
        source = root / 'reference/resource_pack/textures/blocks' / (name.rsplit('/', 1)[1] + '.tga')
        if not source.is_file():
            source = source.with_suffix('.png')
        width, height, rgba = read_rgba(source)
        actual_png = (pack / (name + '.png')).read_bytes()
        if actual_png != encode_png(width, height*len(FRAME_SHIFTS), leaf_frames(width, height, rgba)):
            raise ValueError(f'Leaf animation differs from original palette/motion: {name}')
