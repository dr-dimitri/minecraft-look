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

    def test_daylight_uses_lux_and_night_retains_a_low_light_floor(self):
        # Catch the previous 115-lux noon setting in every exported style.
        for name, data in self.files.items():
            if Path(name).parent.name != 'lighting':
                continue
            light = data['minecraft:lighting_settings']
            orbital = light['directional_lights']['orbital']
            noon = orbital['sun']['illuminance']['0']
            midnight = orbital['moon']['illuminance']['0.5']
            self.assertGreaterEqual(noon, 70000, name)
            self.assertLessEqual(noon, 130000, name)
            self.assertGreater(midnight, .05, name)
            self.assertLessEqual(midnight, .5, name)
            self.assertGreater(noon / midnight, 100000, name)
            self.assertEqual(orbital['sun']['illuminance']['0.42'], 0, name)
            self.assertGreater(light['ambient']['illuminance'], 0, name)
            self.assertLessEqual(light['ambient']['illuminance'], .05, name)
            self.assertGreaterEqual(light['sky']['intensity'], .8, name)

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

    def test_incompatible_caustics_across_a_biome_boundary_are_rejected(self):
        files = copy.deepcopy(self.base)
        files['water/coastal.json']['minecraft:water_settings']['caustics']['scale'] = .9
        with self.assertRaisesRegex(ValueError, 'Non-blendable water settings differ'):
            validate.validate_data(files, 'natural')

    def test_every_style_keeps_the_reduced_brightness_and_relative_color_tint(self):
        # Each overlay replaces the base file, so an unscaled theme gain would
        # silently restore the excessive brightness as soon as a style is chosen.
        expected_gain = {
            'color_grading/natural.json': [.65, .65, .65],
            'subpacks/natural/color_grading/natural.json': [.65, .65, .65],
            'subpacks/mysterious/color_grading/natural.json': [.64025, .65, .65975],
            'subpacks/autumn/color_grading/natural.json': [.65975, .65, .6435],
            'subpacks/halloween/color_grading/natural.json': [.65975, .637, .65975],
        }
        exported = {name for name in self.files if Path(name).parent.name == 'color_grading'}
        self.assertEqual(exported, set(expected_gain))
        for name, gain in expected_gain.items():
            with self.subTest(name=name):
                body = self.files[name]['minecraft:color_grading_settings']
                self.assertEqual(body['tone_mapping']['operator'], 'aces')
                grading = body['color_grading']
                # With no shadow/highlight overrides, midtones cover the image.
                self.assertEqual(set(grading), {'midtones'})
                midtones = grading['midtones']
                self.assertEqual(midtones['gain'], gain)
                self.assertEqual(midtones['gamma'], [2.2, 2.2, 2.2])
                self.assertEqual(midtones['offset'], [0, 0, 0])
                if name in ('color_grading/natural.json',
                            'subpacks/natural/color_grading/natural.json'):
                    self.assertEqual(midtones['contrast'], [1, 1, 1])

    def test_neutral_grading_and_non_emissive_materials(self):
        grading = self.base['color_grading/natural.json']['minecraft:color_grading_settings']
        self.assertEqual(grading['tone_mapping']['operator'], 'aces')
        self.assertEqual(grading['color_grading']['midtones']['saturation'], [1,1,1])
        for block in ('iron_block', 'gold_block', 'copper_block', 'diamond_block'):
            material = self.base[f'textures/blocks/{block}.texture_set.json']['minecraft:texture_set']
            metal, emission, roughness, subsurface = material['metalness_emissive_roughness_subsurface']
            self.assertEqual(metal, 0 if block == 'diamond_block' else 255)
            self.assertEqual(emission, 0)
            self.assertEqual(subsurface, 0)
            self.assertGreater(roughness, 0)


if __name__ == '__main__':
    unittest.main()
