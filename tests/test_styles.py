import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build
import validate

class StyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files=validate.validate()
        cls.base={n:v for n,v in cls.files.items() if not n.startswith('subpacks/')}

    def selected(self,style):
        prefix=f'subpacks/{style}/'
        return {**self.base, **{n[len(prefix):]:v for n,v in self.files.items() if n.startswith(prefix)}}

    def test_four_visible_choices_natural_default_and_no_hardware_gate(self):
        choices=self.base['manifest.json']['subpacks']
        self.assertEqual({x['name'] for x in choices},{'Natürlich','Geheimnisvoll','Herbst','Halloween'})
        self.assertEqual(choices[-1]['folder_name'],'natural')
        self.assertTrue(all(x['memory_tier']==0 for x in choices))
        grades=[self.selected(x['folder_name'])['color_grading/natural.json'] for x in choices]
        self.assertEqual(len({json.dumps(x,sort_keys=True) for x in grades}),4)

    def test_autumn_tint_can_be_fully_reversed_without_touching_weather_or_gameplay(self):
        key='biomes/forest.client_biome.json'
        def components(style):
            return self.selected(style)[key]['minecraft:client_biome']['components']
        autumn=components('autumn')
        natural=components('natural')
        self.assertNotEqual(autumn.get('minecraft:foliage_appearance'),natural.get('minecraft:foliage_appearance'))
        for name,value in natural.items():
            if name != 'minecraft:foliage_appearance':
                self.assertEqual(autumn[name],value)
        self.assertEqual(self.selected('natural'),self.base)
        self.assertEqual(components('mysterious').get('minecraft:foliage_appearance'),natural.get('minecraft:foliage_appearance'))

    def test_each_style_keeps_wave_budget_and_positive_night_light(self):
        for choice in self.base['manifest.json']['subpacks']:
            selected=self.selected(choice['folder_name'])
            for name in self.base:
                if name.startswith('water/'):
                    self.assertEqual(selected[name]['minecraft:water_settings']['waves'],self.base[name]['minecraft:water_settings']['waves'])
                elif name.startswith('lighting/'):
                    light=selected[name]['minecraft:lighting_settings']
                    self.assertGreater(light['ambient']['illuminance'],0)
                    self.assertGreater(light['directional_lights']['orbital']['moon']['illuminance']['0.5'],0)

    def test_both_installers_contain_all_choices_and_balanced_covers_every_style(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            shutil.copytree(validate.PACK,root/'pack')
            shutil.copytree(validate.ROOT/'reference',root/'reference')
            shutil.copytree(validate.ROOT/'assets',root/'assets')
            (root/'scripts').mkdir()
            shutil.copy2(validate.ROOT/'scripts/create_pack.py',root/'scripts/create_pack.py')
            with patch.object(validate,'ROOT',root),patch.object(validate,'PACK',root/'pack'),patch.object(build,'ROOT',root),patch.object(build,'PACK',root/'pack'),contextlib.redirect_stdout(io.StringIO()):
                build.main()
            version='.'.join(map(str,self.base['manifest.json']['header']['version']))
            pack_ids=[]
            for variant,count,sample_width in [('Quality',16,.055),('Balanced',8,.11)]:
                with zipfile.ZipFile(root/'dist'/f'Lumen-WQHD-{variant}-{version}.mcpack') as z:
                    manifest=json.loads(z.read('manifest.json'))
                    pack_ids.append(manifest['header']['uuid'])
                    self.assertEqual(manifest['subpacks'],self.base['manifest.json']['subpacks'])
                    for face in range(6):
                        name=f'textures/environment/overworld_cubemap/cubemap_{face}.png'
                        self.assertEqual(z.read(name),(validate.PACK/name).read_bytes())
                    water=[n for n in z.namelist() if Path(n).parent.name=='water' and n.endswith('.json')]
                    self.assertEqual(len(water),40)
                    for name in water:
                        packaged=json.loads(z.read(name))
                        waves=packaged['minecraft:water_settings']['waves']
                        self.assertEqual(waves['octaves'],count)
                        self.assertEqual(waves['sampleWidth'],sample_width)
                        # Changing quality must preserve the complete optical
                        # profile and motion, including every subpack overlay.
                        waves['octaves']=16
                        waves['sampleWidth']=.055
                        self.assertEqual(packaged,self.files[name])
                    for choice in manifest['subpacks']:
                        self.assertIn(f"subpacks/{choice['folder_name']}/biomes/forest.client_biome.json",z.namelist())
            self.assertEqual(len(set(pack_ids)),2)

if __name__=='__main__':
    unittest.main()
