"""Invalid Balanced edits must never publish an unchecked installer."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build
from artifacts import current_bundle
from source_archive import source_entries


class BalancedBuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name, data in source_entries(build.ROOT, include_generated=False).items():
            target = self.root / name.removeprefix('lumen-bedrock/')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        self.profile = self.root / 'scripts/water_profiles.py'
        self.original = self.profile.read_text(encoding='utf-8')

    def set_balanced(self, expression):
        lines = self.original.splitlines()
        self.profile.write_text('\n'.join(
            'BALANCED = ' + expression if line.startswith('BALANCED = ') else line
            for line in lines) + '\n', encoding='utf-8')

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return build.main(self.root)

    def test_invalid_balanced_edits_preserve_last_successful_artifacts(self):
        previous = self.build()
        pointer = (self.root / 'dist/current.json').read_bytes()
        previous_files = {path.name: path.read_bytes() for path in previous.iterdir()}
        invalid = [
            "{'octaves': 0, 'sampleWidth': .11}",
            "{'octaves': 31, 'sampleWidth': .11}",
            "{'octaves': 7.5, 'sampleWidth': .11}",
            "{'octaves': True, 'sampleWidth': .11}",
            "{'octaves': 8, 'sampleWidth': float('nan')}",
            "{'octaves': 8, 'sampleWidth': float('inf')}",
            "{'octaves': 8, 'sampleWidth': 0}",
            "{'octaves': 8, 'sampleWidth': 1.01}",
            "{'octaves': 8, 'sampleWidth': '.11'}",
            "{'octaves': 8, 'sampleWidth': False}",
            "{'octaves': 8}",
            "{'octaves': 8, 'sampleWidth': .11, 'sample_width': .11}",
            "{'octaves': 8, 'sampleWidth': .11, 'depth': .9}",
            "{'octaves': 8, 'sampleWidth': .11, 'enabled': False}",
        ]
        for expression in invalid:
            with self.subTest(preset=expression):
                self.set_balanced(expression)
                with self.assertRaisesRegex(ValueError, 'Balanced'):
                    self.build()
                self.assertEqual((self.root / 'dist/current.json').read_bytes(), pointer)
                self.assertEqual(current_bundle(self.root / 'dist'), previous)
                self.assertEqual({path.name: path.read_bytes() for path in previous.iterdir()},
                                 previous_files)
                self.assertFalse(list(self.root.glob('.lumen-build-*')))

    def test_valid_custom_balanced_budget_reaches_every_style(self):
        self.set_balanced("{'octaves': 7, 'sampleWidth': .12}")
        output = self.build()
        for variant, octaves, width in [('Quality', 16, .055), ('Balanced', 7, .12)]:
            with zipfile.ZipFile(next(output.glob(f'*{variant}*.mcpack'))) as archive:
                waters = [name for name in archive.namelist()
                          if Path(name).parent.name == 'water' and name.endswith('.json')]
                self.assertEqual(len(waters), 40)
                for name in waters:
                    waves = json.loads(archive.read(name))['minecraft:water_settings']['waves']
                    self.assertEqual(waves['octaves'], octaves, name)
                    self.assertEqual(waves['sampleWidth'], width, name)
                    self.assertTrue(waves['enabled'], name)


if __name__ == '__main__':
    unittest.main()
