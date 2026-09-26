"""Cosmetic, client-only drifting wisps, selected exclusively by Halloween."""
import copy
import json
import math
from texture_pixels import encode_png

PLAYER = 'entity/player.entity.json'
CONTROLLER = 'animation_controllers/lumen_fog.animation_controllers.json'
PARTICLE = 'particles/lumen_fog.json'
TEXTURE = 'textures/lumen/fog_wisp'
TEXTURE_LIST = 'textures/textures_list.json'
JSON_PATHS = {PLAYER, CONTROLLER, PARTICLE, TEXTURE_LIST}
ALIAS = 'lumen_halloween_fog'
CONTROLLER_ID = 'controller.animation.lumen.halloween_fog'
PARTICLE_ID = 'lumen:halloween_fog'


def player_with_fog(original, biome_names):
    player = copy.deepcopy(original)
    description = player['minecraft:client_entity']['description']
    biomes = ', '.join(f"'minecraft:{name}'" for name in sorted(biome_names))
    # The biome query is evaluated in this 1.26.0 client entity (>=1.21.130),
    # not the older animation-controller format. The vanilla root is retained.
    description['scripts']['pre_animation'].append(
        f'variable.{ALIAS} = query.is_local_player && query.is_alive '
        '&& !query.is_in_water && !query.is_sleeping && !query.is_spectator '
        '&& !query.is_in_ui && !variable.map_face_icon '
        f'&& query.entity_biome_has_any_identifier({biomes});')
    description['scripts']['animate'].append(ALIAS)
    description['animations'][ALIAS] = CONTROLLER_ID
    description.setdefault('particle_effects', {})[ALIAS] = PARTICLE_ID
    return player


def controller():
    return {
        'format_version': '1.10.0',
        'animation_controllers': {CONTROLLER_ID: {
            'initial_state': 'default',
            'states': {
                'default': {'transitions': [{'drifting': f'variable.{ALIAS}'}]},
                'drifting': {
                    'particle_effects': [{'effect': ALIAS, 'bind_to_actor': True}],
                    'transitions': [{'default': f'!variable.{ALIAS}'}],
                },
            },
        }},
    }


def particle():
    return {
        'format_version': '1.10.0',
        'particle_effect': {
            'description': {
                'identifier': PARTICLE_ID,
                'basic_render_parameters': {'material': 'particles_alpha', 'texture': TEXTURE},
            },
            'components': {
                'minecraft:emitter_local_space': {'position': False, 'rotation': False, 'velocity': False},
                'minecraft:emitter_rate_steady': {'spawn_rate': 2, 'max_particles': 16},
                'minecraft:emitter_lifetime_expression': {'activation_expression': 1, 'expiration_expression': 0},
                # Spawn 4–8 blocks around the player, not directly on the lens.
                'minecraft:emitter_shape_custom': {
                    'offset': [
                        '(4 + 4 * variable.particle_random_1) * math.cos(360 * variable.particle_random_2)',
                        '0.8 + 1.4 * variable.particle_random_3',
                        '(4 + 4 * variable.particle_random_1) * math.sin(360 * variable.particle_random_2)',
                    ],
                    'direction': [1, .015, .25],
                },
                'minecraft:particle_initial_speed': .35,
                'minecraft:particle_lifetime_expression': {'max_lifetime': 8},
                'minecraft:particle_motion_dynamic': {'linear_acceleration': [0, 0, 0]},
                'minecraft:particle_appearance_billboard': {
                    'size': ['2.4 + variable.particle_random_4', '.55 + .2 * variable.particle_random_4'],
                    'facing_camera_mode': 'lookat_y',
                    'uv': {'texture_width': 128, 'texture_height': 64, 'uv': [0, 0], 'uv_size': [128, 64]},
                },
                'minecraft:particle_appearance_tinting': {'color': {
                    'gradient': {
                        '0.0': [.70, .66, .76, 0],
                        '0.2': [.70, .66, .76, .16],
                        '0.7': [.70, .66, .76, .16],
                        '1.0': [.70, .66, .76, 0],
                    },
                    'interpolant': 'variable.particle_age / variable.particle_lifetime',
                }},
                # Lit alpha blending: no additive glow or fullbright veil.
                'minecraft:particle_appearance_lighting': {},
            },
        },
    }


def texture_png():
    """Authored soft strands, with transparent edges; no external artwork.

    A stored DEFLATE block avoids zlib-version-dependent PNG encoding.
    """
    width, height = 128, 64
    rgba = bytearray()
    for y in range(height):
        v = 2 * y / (height - 1) - 1
        for x in range(width):
            u = 2 * x / (width - 1) - 1
            taper = max(0, 1 - u*u)**2 * max(0, 1 - v*v)**2
            strands = sum(math.exp(-((v - center - .12 * math.sin(u * frequency + phase)) / spread)**2)
                          for center, frequency, phase, spread in
                          [(-.25, 5, 0, .16), (.03, 7, 1, .20), (.27, 4, 2, .14)])
            alpha = round(180 * min(1, strands * .65) * taper)
            rgba.extend((255, 255, 255, alpha))
    return encode_png(width, height, bytes(rgba))


def generate(root, pack, write, biome_names):
    target = pack / 'subpacks/halloween'
    original = json.loads((root / 'reference/resource_pack' / PLAYER).read_text(encoding='utf-8'))
    write(target / PLAYER, player_with_fog(original, biome_names))
    write(target / CONTROLLER, controller())
    write(target / PARTICLE, particle())
    textures = json.loads((pack / TEXTURE_LIST).read_text(encoding='utf-8'))
    write(target / TEXTURE_LIST, [*textures, TEXTURE])
    path = target / (TEXTURE + '.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(texture_png())


def validate_resources(files, style, root, pack):
    special = {name for name in files if name.split('/')[0] in
               {'entity', 'particles', 'animation_controllers'}}
    if style != 'halloween':
        if special or TEXTURE in files[TEXTURE_LIST]:
            raise ValueError(f'Halloween fog leaked into {style}')
        return
    if special != JSON_PATHS - {TEXTURE_LIST}:
        raise ValueError('Incomplete Halloween fog resources')
    original = json.loads((root / 'reference/resource_pack' / PLAYER).read_text(encoding='utf-8'))
    biomes = {
        value['minecraft:client_biome']['description']['identifier'].split(':')[-1]
        for name, value in files.items() if name.startswith('biomes/')
        and value['minecraft:client_biome']['components'].get('minecraft:lighting_identifier', {})
        .get('lighting_identifier', '').startswith('lumen:')
    }
    if files[PLAYER] != player_with_fog(original, biomes):
        raise ValueError('Halloween must preserve the vanilla player and use the scoped fog trigger')
    if files[CONTROLLER] != controller() or files[PARTICLE] != particle():
        raise ValueError('Invalid Halloween fog controller or particle definition')
    base_textures = json.loads((pack / TEXTURE_LIST).read_text(encoding='utf-8'))
    if files[TEXTURE_LIST] != [*base_textures, TEXTURE]:
        raise ValueError('Halloween fog must retain all base texture registrations')
    if (pack / 'subpacks/halloween' / (TEXTURE + '.png')).read_bytes() != texture_png():
        raise ValueError('Halloween fog texture differs from authored source')
