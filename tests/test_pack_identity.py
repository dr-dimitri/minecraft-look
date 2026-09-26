"""Released identities must survive updates, not merely remain valid UUIDs."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from pack_identity import check_pack_identity
import validate


# Explicit release values keep the regression independent of implementation
# constants and of whatever IDs a changed generator happens to emit.
RELEASED = {
    'Quality': ('62534bcd-5dc1-47bf-9903-5277eeb54f6a',
                '6e9469ee-631e-48ba-9f79-29de64b4b2ac'),
    'Balanced': ('4813d437-9f63-49c3-8089-5c683d4da180',
                 'b849e35b-dcc4-460c-8f87-33b22070b38e'),
}
REPLACEMENT = '43282e8f-4378-4b54-ae80-2a83494d0887'


class PackIdentityTests(unittest.TestCase):
    def manifest(self, variant):
        header, module = RELEASED[variant]
        return {'header': {'uuid': header},
                'modules': [{'type': 'resources', 'uuid': module}]}

    def test_published_identity_is_accepted_for_each_variant(self):
        for variant in RELEASED:
            with self.subTest(variant=variant):
                check_pack_identity(self.manifest(variant), variant)

    def test_valid_uuid_rotation_is_rejected_for_every_released_identity(self):
        for variant in RELEASED:
            for part in ('header', 'module'):
                with self.subTest(variant=variant, part=part):
                    manifest = self.manifest(variant)
                    target = manifest['header'] if part == 'header' else manifest['modules'][0]
                    target['uuid'] = REPLACEMENT
                    with self.assertRaisesRegex(ValueError, f'{part} UUID differs'):
                        check_pack_identity(manifest, variant)

    def test_variants_cannot_share_the_same_identity(self):
        with self.assertRaisesRegex(ValueError, 'header UUID differs'):
            check_pack_identity(self.manifest('Quality'), 'Balanced')

    def test_resource_module_cannot_be_replaced_or_added(self):
        manifest = self.manifest('Quality')
        for modules in ([], [dict(manifest['modules'][0], type='data')],
                        manifest['modules'] * 2):
            with self.subTest(modules=modules):
                changed = copy.deepcopy(manifest)
                changed['modules'] = modules
                with self.assertRaisesRegex(ValueError, 'single released resource module'):
                    check_pack_identity(changed)

    def test_pack_validator_rejects_valid_uuid_rotation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('pack', 'reference', 'assets'):
                shutil.copytree(validate.ROOT / name, root / name)
            path = root / 'pack/manifest.json'
            manifest = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(manifest['header']['uuid'], RELEASED['Quality'][0])
            self.assertEqual(manifest['modules'][0]['uuid'], RELEASED['Quality'][1])
            manifest['header']['uuid'] = REPLACEMENT
            path.write_text(json.dumps(manifest), encoding='utf-8')
            with patch.object(validate, 'ROOT', root), patch.object(validate, 'PACK', root / 'pack'):
                with self.assertRaisesRegex(ValueError, 'header UUID differs'):
                    validate.validate()


if __name__ == '__main__':
    unittest.main()
