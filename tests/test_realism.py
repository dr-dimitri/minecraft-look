"""Numerical/content regressions; these are not image-quality or FPS tests."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate


class RealismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = validate.validate()
        cls.base = {n:v for n,v in cls.files.items() if not n.startswith('subpacks/')}

    def test_lighting_tracks_the_pinned_mojang_preset_in_every_style(self):
        reference = validate.load(validate.ROOT / 'reference/resource_pack/lighting/global.json')['minecraft:lighting_settings']
        expected = reference['directional_lights']['orbital']
        scales = {'natural': 1, 'mysterious': .82, 'autumn': 1, 'halloween': .72}
        lights = {n:v for n,v in self.files.items() if Path(n).parent.name == 'lighting'}
        self.assertEqual(len(lights), 20)
        self.assertEqual(max(expected['sun']['illuminance'].values()), 100)
        for name, data in lights.items():
            with self.subTest(name=name):
                style = name.split('/')[1] if name.startswith('subpacks/') else 'natural'
                light = data['minecraft:lighting_settings']
                orbital = light['directional_lights']['orbital']
                for source in ('sun', 'moon'):
                    scale = scales[style] if source == 'sun' else 1
                    wanted = {float(t):round(v*scale,5) for t,v in expected[source]['illuminance'].items()}
                    actual = {float(t):v for t,v in orbital[source]['illuminance'].items()}
                    self.assertEqual(actual, wanted)
                self.assertEqual(orbital['sun']['illuminance']['0.292'], 0)
                self.assertEqual(orbital['sun']['illuminance']['0.709'], 0)
                self.assertEqual(max(orbital['moon']['illuminance'].values()), .4)
                self.assertEqual(orbital['orbital_offset_degrees'], expected['orbital_offset_degrees'])
                self.assertEqual(light['ambient']['illuminance'], reference['ambient']['illuminance'])
                self.assertEqual(light['emissive'], reference['emissive'])
                self.assertLessEqual(light['sky']['intensity'], reference['sky']['intensity'])

    def test_exported_biomes_distinguish_shores_warm_and_lukewarm_water(self):
        expected = {
            'beach':'coastal', 'stone_beach':'coastal',
            'mushroom_island_shore':'coastal', 'cold_beach':'cold_ocean',
            'ocean':'ocean', 'deep_ocean':'ocean',
            'lukewarm_ocean':'ocean', 'deep_lukewarm_ocean':'ocean',
            'warm_ocean':'tropical', 'deep_warm_ocean':'tropical',
            'cold_ocean':'cold_ocean', 'deep_frozen_ocean':'cold_ocean',
            'river':'river', 'frozen_river':'clear_lake',
            'swampland':'swamp', 'mangrove_swamp':'swamp',
            'plains':'lake', 'snowy_slopes':'clear_lake',
        }
        for style in ['', 'subpacks/natural/', 'subpacks/autumn/',
                      'subpacks/mysterious/', 'subpacks/halloween/']:
            for biome, profile in expected.items():
                data = self.files[f'{style}biomes/{biome}.client_biome.json']
                ref = data['minecraft:client_biome']['components']['minecraft:water_identifier']['water_identifier']
                self.assertEqual(ref, f'lumen:{profile}', style+biome)
            # "mangrove" contains "grove", but belongs to the wet climate.
            for biome, climate in [('mangrove_swamp','wet'), ('grove','cold'), ('cherry_grove','temperate')]:
                components = self.files[f'{style}biomes/{biome}.client_biome.json']['minecraft:client_biome']['components']
                self.assertEqual(components['minecraft:lighting_identifier']['lighting_identifier'], f'lumen:light_{climate}')

    def test_water_retains_environmental_differences_without_theme_dye(self):
        waters = {Path(n).stem:v['minecraft:water_settings']
                  for n,v in self.base.items() if n.startswith('water/')}
        self.assertEqual(len(waters), 8)
        self.assertGreater(waters['ocean']['waves']['depth'], waters['lake']['waves']['depth'])
        self.assertLess(waters['ocean']['waves']['frequency'], waters['lake']['waves']['frequency'])
        self.assertGreater(waters['river']['waves']['speed'], waters['lake']['waves']['speed'])
        self.assertLess(waters['swamp']['waves']['depth'], waters['lake']['waves']['depth'])
        for component in ('cdom', 'chlorophyll', 'suspended_sediment'):
            self.assertLess(waters['tropical']['particle_concentrations'][component],
                            waters['swamp']['particle_concentrations'][component])
        for name, data in self.files.items():
            if Path(name).parent.name == 'water':
                body = data['minecraft:water_settings']
                self.assertEqual(body['biome_water_color_contribution'], 0, name)
                self.assertEqual(body, waters[Path(name).stem], name)

    def test_water_darkening_only_increases_absorbing_constituents(self):
        # Independent 0.4.3 values; a 10% concentration increase is an authored
        # approximation, never proof of a 10% reduction in rendered luminance.
        approved = {
            'lake': (.080, .015, .035), 'clear_lake': (.035, .008, .015),
            'river': (.350, .070, .350), 'coastal': (.075, .035, .150),
            'ocean': (.035, .025, .025), 'cold_ocean': (.025, .020, .025),
            'tropical': (.008, .007, .015), 'swamp': (1.600, .450, 1.200),
        }
        for name, data in self.files.items():
            if Path(name).parent.name != 'water':
                continue
            cdom, chlorophyll, sediment = approved[Path(name).stem]
            water = data['minecraft:water_settings']
            self.assertEqual(water['particle_concentrations'], {
                'cdom': round(cdom * 1.1, 6),
                'chlorophyll': round(chlorophyll * 1.1, 6),
                'suspended_sediment': sediment,
            }, name)
            self.assertEqual(water['biome_water_color_contribution'], 0)
            self.assertEqual(water['caustics'], {
                'enabled': True, 'frame_length': .09, 'power': 1, 'scale': .5})

    def test_all_water_profiles_use_gentle_moving_ripples(self):
        for name, data in self.files.items():
            if Path(name).parent.name != 'water':
                continue
            with self.subTest(name=name):
                waves = data['minecraft:water_settings']['waves']
                self.assertTrue(waves['enabled'])
                self.assertGreaterEqual(waves['depth'], .04)
                self.assertLessEqual(waves['depth'], .20)
                self.assertGreaterEqual(waves['speed'], .30)
                self.assertLessEqual(waves['speed'], .70)
                self.assertGreaterEqual(waves['shape'], 1)
                self.assertLessEqual(waves['shape'], 1.15)
                self.assertLessEqual(waves['frequency_scaling'], 1.16)
                self.assertLessEqual(waves['speed_scaling'], 1.01)
                self.assertLessEqual(waves['pull'], .10)

    def test_incompatible_caustics_across_a_biome_boundary_are_rejected(self):
        files = copy.deepcopy(self.base)
        files['water/coastal.json']['minecraft:water_settings']['caustics']['scale'] = .9
        with self.assertRaisesRegex(ValueError, 'Non-blendable water settings differ'):
            validate.validate_data(files, 'natural')

    def test_all_styles_retain_mojang_grading_without_channel_amplification(self):
        reference = validate.load(validate.ROOT / 'reference/resource_pack/color_grading/color_grading.json')['minecraft:color_grading_settings']
        reference.pop('description')
        tints = {'natural': [1,1,1], 'mysterious': [.985,1,1.015],
                 'autumn': [1.015,1,.99], 'halloween': [1.015,.98,1.015]}
        grades = {n:v for n,v in self.files.items() if Path(n).parent.name == 'color_grading'}
        self.assertEqual(len(grades), 5)
        for name, data in grades.items():
            with self.subTest(name=name):
                style = name.split('/')[1] if name.startswith('subpacks/') else 'natural'
                body = data['minecraft:color_grading_settings']
                self.assertEqual(body['tone_mapping'], reference['tone_mapping'])
                grading = body['color_grading']
                self.assertEqual(set(grading), set(reference['color_grading']))
                self.assertEqual(grading['temperature'], reference['color_grading']['temperature'])
                midtones = grading['midtones']
                for field in ('contrast', 'gamma', 'offset'):
                    self.assertEqual(midtones[field], reference['color_grading']['midtones'][field])
                gain = midtones['gain']
                self.assertEqual(max(gain), 1)
                for actual, tint in zip(gain, tints[style]):
                    self.assertAlmostEqual(actual, tint/max(tints[style]), places=5)
                if style == 'natural':
                    self.assertEqual({k:v for k,v in body.items() if k != 'description'}, reference)

    def test_validator_rejects_the_previous_110000_sunlight(self):
        files = copy.deepcopy(self.base)
        sun = files['lighting/light_temperate.json']['minecraft:lighting_settings']['directional_lights']['orbital']['sun']['illuminance']
        sun['0'] = sun['1'] = 110000
        with self.assertRaisesRegex(ValueError, 'Mojang preset illuminance'):
            validate.validate_data(files, 'natural')

    def test_validator_rejects_the_previous_aces_tone_mapping(self):
        files = copy.deepcopy(self.base)
        files['color_grading/natural.json']['minecraft:color_grading_settings']['tone_mapping']['operator'] = 'aces'
        with self.assertRaisesRegex(ValueError, 'Mojang Generic'):
            validate.validate_data(files, 'natural')

    def test_neutral_grading_and_non_emissive_materials(self):
        grading = self.base['color_grading/natural.json']['minecraft:color_grading_settings']
        self.assertEqual(grading['tone_mapping']['operator'], 'generic')
        self.assertEqual(grading['color_grading']['midtones']['saturation'], [1.05]*3)
        for block in ('iron_block', 'gold_block', 'copper_block', 'diamond_block'):
            material = self.base[f'textures/blocks/{block}.texture_set.json']['minecraft:texture_set']
            metal, emission, roughness, subsurface = material['metalness_emissive_roughness_subsurface']
            self.assertEqual(metal, 0 if block == 'diamond_block' else 255)
            self.assertEqual(emission, 0)
            self.assertEqual(subsurface, 0)
            self.assertGreater(roughness, 0)


if __name__ == '__main__':
    unittest.main()
