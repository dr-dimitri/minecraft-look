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


class BuildGuardTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ('pack', 'reference', 'assets', 'scripts'):
            shutil.copytree(validate.ROOT / name, self.root / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        for module in (validate, build):
            stack.enter_context(patch.object(module, 'ROOT', self.root))
            stack.enter_context(patch.object(module, 'PACK', self.root / 'pack'))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))

    def test_stale_generated_version_cannot_be_built(self):
        (self.root / 'scripts/create_pack.py').write_text('VERSION = [99, 0, 0]\n')
        with self.assertRaisesRegex(ValueError, 'header version differs'):
            build.main()
        self.assertFalse((self.root / 'dist').exists())

    def test_missing_material_definition_cannot_be_built(self):
        (self.root / 'pack/textures/blocks/iron_block.texture_set.json').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing or unexpected block material'):
            build.main()

    def test_damaged_color_texture_cannot_be_built(self):
        path = self.root / 'pack/textures/blocks/iron_block.png'
        data = bytearray(path.read_bytes())
        data[-16] ^= 1  # Header remains intact; the previous validator accepted this.
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'differs from pinned reference'):
            build.main()

    def test_material_cannot_silently_use_another_blocks_color(self):
        path = self.root / 'pack/textures/blocks/iron_block.texture_set.json'
        data = json.loads(path.read_text())
        data['minecraft:texture_set']['color'] = 'gold_block'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Unexpected block color reference'):
            build.main()

    def test_wrong_quality_wave_budget_is_rejected_even_with_python_optimization(self):
        for path in (self.root / 'pack').rglob('*.json'):
            if path.parent.name == 'water':
                data = json.loads(path.read_text())
                data['minecraft:water_settings']['waves']['octaves'] = 12
                path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Unexpected wave budget in Quality'):
            build.main()


if __name__ == '__main__':
    unittest.main()
