"""Failures must leave readers on the previous, complete artifact set."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import artifacts
import build
from verify_build import compare_bundles, extract_source


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.dist = self.root / 'dist'
        self.version = '1.2.3'

    def bundle(self, name, content=b'first'):
        directory = self.root / name
        directory.mkdir()
        sums = []
        for filename in sorted(artifacts.expected_names(self.version)):
            path = directory / filename
            build.archive(path, {'manifest.json': content})
            sums.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {filename}\n')
        (directory / 'SHA256SUMS.txt').write_text(''.join(sums), encoding='utf-8', newline='\n')
        return directory

    def test_failed_pointer_switch_preserves_previous_complete_set(self):
        old = artifacts.publish_bundle(self.bundle('first'), self.dist, self.version)
        before = (self.dist / 'current.json').read_bytes()
        with patch.object(artifacts.os, 'replace', side_effect=OSError('interrupted switch')):
            with self.assertRaisesRegex(OSError, 'interrupted'):
                artifacts.publish_bundle(self.bundle('second', b'new'), self.dist, self.version)
        self.assertEqual((self.dist / 'current.json').read_bytes(), before)
        self.assertEqual(artifacts.current_bundle(self.dist), old)
        self.assertFalse(list(self.dist.glob('.current-*')))
        # An unused complete directory can safely be reused on retry.
        retried = artifacts.publish_bundle(self.bundle('retry', b'new'), self.dist, self.version)
        self.assertNotEqual(retried, old)
        self.assertEqual(artifacts.current_bundle(self.dist), retried)
        artifacts.verify_bundle(old, self.version)

    def test_incomplete_and_corrupted_bundles_cannot_replace_current(self):
        old = artifacts.publish_bundle(self.bundle('first'), self.dist, self.version)
        broken = self.bundle('missing')
        next(broken.glob('*.mcpack')).unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            artifacts.publish_bundle(broken, self.dist, self.version)
        broken = self.bundle('corrupt')
        next(broken.glob('*.mcpack')).write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
            artifacts.publish_bundle(broken, self.dist, self.version)
        self.assertEqual(artifacts.current_bundle(self.dist), old)

    def test_repeated_bundle_is_reused_but_corrupt_existing_data_is_rejected(self):
        first = artifacts.publish_bundle(self.bundle('first'), self.dist, self.version)
        self.assertEqual(artifacts.publish_bundle(self.bundle('repeat'), self.dist, self.version), first)
        next(first.glob('*.mcpack')).write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
            artifacts.publish_bundle(self.bundle('retry'), self.dist, self.version)

    def test_rebuild_comparison_rejects_valid_but_different_archives(self):
        with self.assertRaisesRegex(ValueError, 'archives differ'):
            compare_bundles(self.bundle('first'), self.bundle('second', b'changed'), self.version)

    def test_source_extraction_rejects_traversal_before_writing_any_file(self):
        archive = self.root / 'source.zip'
        with zipfile.ZipFile(archive, 'w') as handle:
            handle.writestr('lumen-bedrock/README.md', 'safe')
            handle.writestr('lumen-bedrock/../escaped.txt', 'unsafe')
        target = self.root / 'extracted'
        target.mkdir()
        with self.assertRaisesRegex(ValueError, 'Invalid source archive member'):
            extract_source(archive, target)
        self.assertEqual(list(target.iterdir()), [])

    def test_current_pointer_cannot_escape_dist(self):
        self.dist.mkdir()
        (self.dist / 'current.json').write_text(json.dumps({'version': '../outside', 'sha256': '0' * 64}))
        with self.assertRaisesRegex(ValueError, 'Invalid current artifact version'):
            artifacts.current_bundle(self.dist)


if __name__ == '__main__':
    unittest.main()
