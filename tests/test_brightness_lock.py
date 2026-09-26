"""Small, otherwise valid edits must not silently change approved brightness."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate
from brightness_lock import check_approved_brightness
from themes import STYLES


class BrightnessLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {p.relative_to(validate.PACK).as_posix(): validate.load(p)
                     for p in validate.PACK.rglob('*.json')}
        cls.base = {n: v for n, v in cls.files.items() if not n.startswith('subpacks/')}

    def selected(self, style):
        prefix = f'subpacks/{style}/'
        return copy.deepcopy({**self.base, **{n[len(prefix):]: v for n, v in self.files.items()
                                           if n.startswith(prefix)}})

    def test_small_brightness_changes_are_rejected_in_every_style(self):
        edits = [
            ('lighting/light_temperate.json', ['minecraft:lighting_settings', 'ambient', 'illuminance'], .021),
            ('lighting/light_temperate.json', ['minecraft:lighting_settings', 'sky', 'intensity'], .89),
            ('lighting/light_temperate.json', ['minecraft:lighting_settings', 'directional_lights', 'orbital', 'sun', 'illuminance', '0.05'], 70),
            ('color_grading/natural.json', ['minecraft:color_grading_settings', 'color_grading', 'midtones', 'gain'], [.9, .9, .9]),
            ('color_grading/natural.json', ['minecraft:color_grading_settings', 'color_grading', 'midtones', 'gamma'], [2.1, 2.1, 2.1]),
            ('atmospherics/air_temperate.json', ['minecraft:atmosphere_settings', 'rayleigh_strength'], 1.1),
            ('local_lighting/local_lighting.json', ['minecraft:local_light_settings', 'minecraft:torch', 'light_color'], '#ffffff'),
            ('water/lake.json', ['minecraft:water_settings', 'particle_concentrations', 'cdom'], .079),
            ('biomes/plains.client_biome.json', ['minecraft:client_biome', 'components', 'minecraft:lighting_identifier', 'lighting_identifier'], 'lumen:light_cold'),
            ('textures/blocks/iron_block.texture_set.json', ['minecraft:texture_set', 'metalness_emissive_roughness_subsurface'], [255, 1, 80, 0]),
        ]
        cubemap = next(n for n in self.base if n.startswith('cubemaps/'))
        edits.append((cubemap, ['minecraft:cubemap_settings', 'lighting', 'sky_light_contribution'], .01))
        for style, _ in STYLES:
            for name, keys, value in edits:
                with self.subTest(style=style, file=name, field=keys):
                    selected = self.selected(style)
                    target = selected[name]
                    for key in keys[:-1]:
                        target = target[key]
                    self.assertNotEqual(target[keys[-1]], value)
                    target[keys[-1]] = value
                    with self.assertRaisesRegex(ValueError, 'Approved brightness changed'):
                        validate.validate_data(selected, style)

    def test_wave_tuning_and_both_sampling_budgets_preserve_brightness(self):
        for style, _ in STYLES:
            for count, width in [(16, .055), (8, .11)]:
                selected = self.selected(style)
                for name, value in selected.items():
                    if name.startswith('water/'):
                        value['minecraft:water_settings']['waves'].update(
                            depth=.09, speed=.5, octaves=count, sampleWidth=width)
                validate.validate_data(selected, style)

    def test_added_or_missing_light_resource_is_detected(self):
        for action in ('add', 'remove'):
            selected = self.selected('natural')
            if action == 'add':
                selected['lighting/extra.json'] = selected['lighting/light_temperate.json']
            else:
                del selected['lighting/light_wet.json']
            with self.assertRaisesRegex(ValueError, 'Approved brightness changed.*lighting'):
                check_approved_brightness(selected, 'natural', validate.ROOT)

    def test_baseline_cannot_be_omitted_or_replaced_by_an_empty_style(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                check_approved_brightness(self.base, 'natural', root)
            (root / 'reference').mkdir()
            path = root / 'reference/approved_brightness.json'
            for baseline in ({}, {'schema_version': 1, 'styles': {'natural': {}}}):
                path.write_text(json.dumps(baseline))
                with self.assertRaises(ValueError):
                    check_approved_brightness(self.base, 'natural', root)


if __name__ == '__main__':
    unittest.main()
