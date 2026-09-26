"""Real-world packaging failures, reproduced in isolated project copies."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build
import validate
from source_archive import source_entries
from artifacts import current_bundle


class BuildGuardTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name, data in source_entries(validate.ROOT).items():
            target = self.root / name.removeprefix('lumen-bedrock/')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        for module in (validate, build):
            stack.enter_context(patch.object(module, 'ROOT', self.root))
        stack.enter_context(patch.object(validate, 'PACK', self.root / 'pack'))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))

    def test_changed_sources_at_same_version_are_built_without_overwriting_local_outputs(self):
        source = self.root / 'scripts/water_profiles.py'
        original = source.read_text()
        changed = original.replace('.300, .50, .55, 1.10', '.300, .50, .56, 1.10')
        self.assertNotEqual(changed, original)
        source.write_text(changed.replace("BALANCED = {'octaves': 8", "BALANCED = {'octaves': 7"))
        stale = self.root / 'pack/water/lake.json'
        before = stale.read_bytes()
        marker = self.root / 'pack/local-notes.md'
        marker.write_text('Local user work')
        biome_map = self.root / 'docs/biome-map.json'
        biome_map.write_text('Local map notes')
        output = build.main()
        self.assertEqual(output, current_bundle(self.root / 'dist'))
        import zipfile
        with zipfile.ZipFile(next(output.glob('*Quality*.mcpack'))) as archive:
            water = json.loads(archive.read('water/lake.json'))['minecraft:water_settings']
            self.assertEqual(water['waves']['speed'], .56)
            self.assertNotIn('local-notes.md', archive.namelist())
        with zipfile.ZipFile(next(output.glob('*Balanced*.mcpack'))) as archive:
            water = json.loads(archive.read('water/lake.json'))['minecraft:water_settings']
            self.assertEqual(water['waves']['octaves'], 7)
        with zipfile.ZipFile(next(output.glob('*Source*.zip'))) as archive:
            self.assertNotIn('lumen-bedrock/pack/local-notes.md', archive.namelist())
            self.assertIn('plains', json.loads(archive.read('lumen-bedrock/docs/biome-map.json')))
            water = json.loads(archive.read('lumen-bedrock/pack/water/lake.json'))['minecraft:water_settings']
            self.assertEqual(water['waves']['speed'], .56)
        self.assertEqual(stale.read_bytes(), before)
        self.assertEqual(marker.read_text(), 'Local user work')
        self.assertEqual(biome_map.read_text(), 'Local map notes')

    def test_no_generated_pack_is_required_to_build(self):
        shutil.rmtree(self.root / 'pack')
        (self.root / 'docs/biome-map.json').unlink()
        output = build.main()
        self.assertEqual(len(list(output.iterdir())), 4)
        self.assertFalse((self.root / 'pack').exists())

    def test_valid_but_unapproved_brightness_change_cannot_replace_bundle(self):
        import subprocess
        output = build.main()
        pointer = (self.root / 'dist/current.json').read_bytes()
        baseline = (self.root / 'reference/approved_brightness.json').read_bytes()
        source = self.root / 'scripts/themes.py'
        original = source.read_text()
        changed = original.replace("'sun_strength': .82", "'sun_strength': .81")
        self.assertNotEqual(original, changed)
        source.write_text(changed)
        with self.assertRaises(subprocess.CalledProcessError):
            build.main()
        self.assertEqual((self.root / 'dist/current.json').read_bytes(), pointer)
        self.assertEqual(current_bundle(self.root / 'dist'), output)
        self.assertEqual((self.root / 'reference/approved_brightness.json').read_bytes(), baseline)

    def test_archive_failure_keeps_previous_bundle_and_pointer(self):
        output = build.main()
        old_pointer = (self.root / 'dist/current.json').read_bytes()
        old_files = {p.name: p.read_bytes() for p in output.iterdir()}
        archive = build.archive

        def fail_on_second(path, entries):
            if 'Balanced' in path.name:
                raise OSError('simulated disk full')
            archive(path, entries)

        with patch.object(build, 'archive', side_effect=fail_on_second):
            with self.assertRaisesRegex(OSError, 'disk full'):
                build.main()
        self.assertEqual((self.root / 'dist/current.json').read_bytes(), old_pointer)
        self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, old_files)
        self.assertFalse(list(self.root.glob('.lumen-build-*')))

    def test_missing_material_definition_cannot_be_built(self):
        (self.root / 'pack/textures/blocks/iron_block.texture_set.json').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing or unexpected block material'):
            validate.validate()

    def test_damaged_color_texture_cannot_be_built(self):
        path = self.root / 'pack/textures/blocks/iron_block.png'
        data = bytearray(path.read_bytes())
        data[-16] ^= 1  # Header remains intact; the previous validator accepted this.
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'differs from pinned reference'):
            validate.validate()

    def test_material_cannot_silently_use_another_blocks_color(self):
        path = self.root / 'pack/textures/blocks/iron_block.texture_set.json'
        data = json.loads(path.read_text())
        data['minecraft:texture_set']['color'] = 'gold_block'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Unexpected block color reference'):
            validate.validate()

    def test_wrong_quality_wave_budget_is_rejected_even_with_python_optimization(self):
        for path in (self.root / 'pack').rglob('*.json'):
            if path.parent.name == 'water':
                data = json.loads(path.read_text())
                data['minecraft:water_settings']['waves']['octaves'] = 12
                path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Unexpected wave budget in Quality'):
            build.stage_archives(self.root, self.root / 'staged')


if __name__ == '__main__':
    unittest.main()
