"""Gentle four-second texture sway; no geometry or palette modification."""
import json
from texture_pixels import encode_png, read_rgba

FLIPBOOK = 'textures/flipbook_textures.json'
PREFIX = 'textures/lumen/leaves/'


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
    # The first frame is the original. A cyclic row permutation conserves every
    # RGBA pixel, including alpha, in every frame. No filtering or recoloring.
    for direction in (0, 1, 0, -1):
        for y in range(height):
            shift = direction if height//4 <= y < 3*height//4 else 0
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
        path.write_bytes(encode_png(width, height*4, leaf_frames(width, height, rgba)))
        generated.append(name)
    animations = []
    for tile, names in entries.items():
        for variant, name in enumerate(names):
            animations.append({
                'flipbook_texture': PREFIX + name.rsplit('/', 1)[1],
                'atlas_tile': tile,
                'atlas_index': variant,
                'atlas_tile_variant': variant,
                'ticks_per_frame': 20,
                'frames': [0, 1, 2, 3],
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
        if (item['atlas_index'] != item['atlas_tile_variant'] or item['frames'] != [0, 1, 2, 3]
                or item['ticks_per_frame'] != 20 or item['blend_frames'] is not True):
            raise ValueError('Leaf animation must retain the gentle seamless cycle')
    for name in set(expected.values()):
        source = root / 'reference/resource_pack/textures/blocks' / (name.rsplit('/', 1)[1] + '.tga')
        if not source.is_file():
            source = source.with_suffix('.png')
        width, height, rgba = read_rgba(source)
        actual_png = (pack / (name + '.png')).read_bytes()
        if actual_png != encode_png(width, height*4, leaf_frames(width, height, rgba)):
            raise ValueError(f'Leaf animation differs from original palette/motion: {name}')
