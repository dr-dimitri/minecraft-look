"""Sky resource/fade checks; no claim of an in-engine render test."""
import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import validate


def interpolate(curve, time):
    frames = sorted((float(t),v) for t,v in curve.items())
    for (a, av), (b, bv) in zip(frames,frames[1:]):
        if a <= time <= b:
            return av+(bv-av)*(time-a)/(b-a)
    raise ValueError('Time outside cycle')


class NightSkyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files=validate.validate()
        cls.base={n:v for n,v in cls.files.items() if not n.startswith('subpacks/')}

    def test_every_style_fades_out_during_day_and_in_at_night(self):
        for name,data in self.files.items():
            if Path(name).parent.name != 'cubemaps':
                continue
            light=data['minecraft:cubemap_settings']['lighting']
            curve=light['ambient_light_illuminance']
            for time in [0,.1,.2,.25,.3,.73,.8,.9,1]:
                self.assertAlmostEqual(interpolate(curve,time),0,places=12,msg=name)
            self.assertGreater(interpolate(curve,.5),0,name)
            self.assertLess(interpolate(curve,.5),2,name)
            evening=[interpolate(curve,t/1000) for t in range(300,501)]
            morning=[interpolate(curve,t/1000) for t in range(580,731)]
            self.assertEqual(evening,sorted(evening))
            self.assertEqual(morning,sorted(morning,reverse=True))
            self.assertEqual(light['sky_light_contribution'],0)
            self.assertEqual(light['directional_light_contribution'],0)

    def test_special_overworld_biomes_change_only_the_sky_binding(self):
        for name in ('pale_garden','deep_dark','lush_caves','dripstone_caves','sulfur_caves'):
            original=validate.load(validate.ROOT/'reference/resource_pack/biomes'/f'{name}.client_biome.json')
            expected=original['minecraft:client_biome']['components']
            for prefix in ('','subpacks/natural/','subpacks/autumn/','subpacks/mysterious/','subpacks/halloween/'):
                data=self.files[f'{prefix}biomes/{name}.client_biome.json']
                actual=copy.deepcopy(data['minecraft:client_biome']['components'])
                self.assertEqual(actual.pop('minecraft:cubemap_identifier'),{'cubemap_identifier':'lumen:galaxy'})
                expected_without_sky={k:v for k,v in expected.items() if k!='minecraft:cubemap_identifier'}
                self.assertEqual(actual,expected_without_sky)

    def test_invalid_sky_reference_is_rejected(self):
        files=copy.deepcopy(self.base)
        files['biomes/plains.client_biome.json']['minecraft:client_biome']['components']['minecraft:cubemap_identifier']['cubemap_identifier']='lumen:missing'
        with self.assertRaisesRegex(ValueError,'Broken graphic reference'):
            validate.validate_data(files,'natural')

    def test_missing_cube_face_prevents_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for folder in ('pack','reference','assets'):
                shutil.copytree(validate.ROOT/folder,root/folder)
            (root/'pack/textures/environment/overworld_cubemap/cubemap_4.png').unlink()
            with patch.object(validate,'ROOT',root),patch.object(validate,'PACK',root/'pack'):
                with self.assertRaisesRegex(ValueError,'Missing sky face'):
                    validate.validate()


if __name__=='__main__':
    unittest.main()
