import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate
import build

class PackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files=validate.validate()

    def test_reproducible_archive_has_importable_root(self):
        with tempfile.TemporaryDirectory() as d:
            entries={'manifest.json':json.dumps(self.files['manifest.json']).encode(),'water/lake.json':json.dumps(self.files['water/lake.json']).encode()}
            a,b=Path(d)/'a.mcpack',Path(d)/'b.mcpack'
            build.archive(a,entries)
            build.archive(b,dict(reversed(list(entries.items()))))
            self.assertEqual(a.read_bytes(),b.read_bytes())
            with zipfile.ZipFile(a) as z:
                self.assertIn('manifest.json',z.namelist())
                self.assertIsNone(z.testzip())

    def test_daylight_wrap_and_positive_night_light(self):
        for name,value in self.files.items():
            if name.startswith('lighting/'):
                lights=value['minecraft:lighting_settings']['directional_lights']['orbital']
                self.assertGreater(lights['moon']['illuminance']['0.5'],0)
                self.assertEqual(lights['sun']['illuminance']['0'],lights['sun']['illuminance']['1'])

    def test_unresolved_references_fail_before_packaging(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            shutil.copytree(validate.ROOT/'reference',root/'reference')
            shutil.copytree(validate.PACK,root/'pack')
            shutil.copytree(validate.ROOT/'assets',root/'assets')
            p=root/'pack/biomes/plains.client_biome.json'
            data=json.loads(p.read_text())
            data['minecraft:client_biome']['components']['minecraft:water_identifier']['water_identifier']='lumen:missing'
            p.write_text(json.dumps(data))
            old_root,old_pack=validate.ROOT,validate.PACK
            validate.ROOT,validate.PACK=root,root/'pack'
            try:
                with self.assertRaisesRegex(ValueError,'Broken graphic reference'):
                    validate.validate()
            finally:
                validate.ROOT,validate.PACK=old_root,old_pack

    def test_invalid_numeric_and_duplicate_json_are_rejected(self):
        with self.assertRaises(ValueError):
            validate.numeric(float('nan'),0,30,'waves')
        with self.assertRaises(ValueError):
            validate.numeric(31,1,30,'waves')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'duplicate.json'
            p.write_text('{"format_version":2,"format_version":1}')
            with self.assertRaisesRegex(ValueError,'Duplicate JSON key'):
                validate.load(p)

if __name__=='__main__':
    unittest.main()
