"""Resource wiring and bounded cosmetic effects; no substitute for Bedrock QA."""
import copy
import json
from pathlib import Path
import re
import struct
import sys
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import halloween_fog as fog
import validate
from night_sky import SKY_ONLY_BIOMES, EXCLUDED_BIOMES


class HalloweenFogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {p.relative_to(validate.PACK).as_posix(): validate.load(p)
                     for p in validate.PACK.rglob('*.json')}
        cls.base = {n: v for n, v in cls.files.items() if not n.startswith('subpacks/')}

    def selected(self, style):
        prefix = f'subpacks/{style}/'
        return copy.deepcopy({**self.base, **{n[len(prefix):]: v for n, v in self.files.items()
                                           if n.startswith(prefix)}})

    def test_only_halloween_extends_player_and_preserves_all_vanilla_animation_data(self):
        for style in ('natural', 'mysterious', 'autumn'):
            selected = self.selected(style)
            self.assertFalse(fog.JSON_PATHS.intersection(selected) - {fog.TEXTURE_LIST})
            self.assertNotIn(fog.TEXTURE, selected[fog.TEXTURE_LIST])
        selected = self.selected('halloween')
        player = copy.deepcopy(selected[fog.PLAYER])
        original = validate.load(validate.ROOT / 'reference/resource_pack' / fog.PLAYER)
        description = player['minecraft:client_entity']['description']
        self.assertEqual(description['scripts']['animate'].pop(), fog.ALIAS)
        condition = description['scripts']['pre_animation'].pop()
        for query in ('query.is_local_player', 'query.is_alive', '!query.is_in_water',
                      '!query.is_sleeping', '!query.is_spectator', '!query.is_in_ui', '!variable.map_face_icon'):
            self.assertIn(query, condition)
        biomes = set(re.findall("'minecraft:([^']+)'", condition))
        self.assertEqual(len(biomes), 78)
        self.assertFalse(biomes & (SKY_ONLY_BIOMES | EXCLUDED_BIOMES))
        self.assertIn('plains', biomes)
        self.assertEqual(description['animations'].pop(fog.ALIAS), fog.CONTROLLER_ID)
        self.assertEqual(description['particle_effects'].pop(fog.ALIAS), fog.PARTICLE_ID)
        if 'particle_effects' not in original['minecraft:client_entity']['description']:
            self.assertEqual(description.pop('particle_effects'), {})
        self.assertEqual(player, original)
        states = selected[fog.CONTROLLER]['animation_controllers'][fog.CONTROLLER_ID]['states']
        self.assertNotIn('particle_effects', states['default'])
        self.assertEqual(states['drifting']['transitions'], [{'default': f'!variable.{fog.ALIAS}'}])
        self.assertEqual(states['drifting']['particle_effects'][0]['effect'], fog.ALIAS)

    def test_wisps_drift_in_world_space_and_fade_without_additive_glow(self):
        effect = self.selected('halloween')[fog.PARTICLE]['particle_effect']
        self.assertEqual(effect['description']['identifier'], fog.PARTICLE_ID)
        self.assertEqual(effect['description']['basic_render_parameters'], {
            'material': 'particles_alpha', 'texture': fog.TEXTURE})
        components = effect['components']
        local = components['minecraft:emitter_local_space']
        self.assertFalse(local['position'] or local['rotation'] or local['velocity'])
        rate = components['minecraft:emitter_rate_steady']
        self.assertLessEqual(rate['max_particles'], 16)
        self.assertGreater(rate['spawn_rate'], 0)
        self.assertLessEqual(rate['spawn_rate'], 2)
        self.assertGreater(components['minecraft:particle_initial_speed'], .1)
        self.assertLessEqual(components['minecraft:particle_initial_speed'], .5)
        self.assertLessEqual(components['minecraft:particle_lifetime_expression']['max_lifetime'], 8)
        self.assertIn('minecraft:particle_appearance_lighting', components)
        gradient = components['minecraft:particle_appearance_tinting']['color']['gradient']
        self.assertEqual(gradient['0.0'][3], 0)
        self.assertEqual(gradient['1.0'][3], 0)
        self.assertTrue(all(0 <= color[3] <= .2 for color in gradient.values()))

    def test_texture_has_soft_transparency_and_fully_transparent_edges(self):
        raw = (validate.PACK / 'subpacks/halloween' / (fog.TEXTURE + '.png')).read_bytes()
        self.assertEqual(struct.unpack('>IIBB', raw[16:26]), (128, 64, 8, 6))
        position, compressed = 8, bytearray()
        while position < len(raw):
            length = struct.unpack('>I', raw[position:position+4])[0]
            kind, data = raw[position+4:position+8], raw[position+8:position+8+length]
            self.assertEqual(zlib.crc32(kind+data), struct.unpack('>I', raw[position+8+length:position+12+length])[0])
            if kind == b'IDAT':
                compressed.extend(data)
            position += length + 12
        scanlines = zlib.decompress(compressed)
        rows = [scanlines[y*513:(y+1)*513] for y in range(64)]
        self.assertTrue(all(row[0] == 0 for row in rows))
        alpha = [list(row[4::4]) for row in rows]
        self.assertGreater(len(set(a for row in alpha for a in row)), 50)
        self.assertTrue(all(a == 0 for a in alpha[0]+alpha[-1]))
        self.assertTrue(all(row[0] == row[-1] == 0 for row in alpha))

    def test_broken_trigger_and_effect_leak_are_rejected(self):
        files = self.selected('halloween')
        files[fog.PLAYER]['minecraft:client_entity']['description']['scripts']['animate'].remove(fog.ALIAS)
        with self.assertRaisesRegex(ValueError, 'scoped fog trigger'):
            validate.validate_data(files, 'halloween')
        files = self.selected('natural')
        files[fog.PARTICLE] = self.selected('halloween')[fog.PARTICLE]
        with self.assertRaisesRegex(ValueError, 'Halloween fog leaked'):
            validate.validate_data(files, 'natural')


if __name__ == '__main__':
    unittest.main()
