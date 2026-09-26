"""Export failures must preserve the previously usable sky and its manifest.

FFmpeg is simulated with existing valid faces; these are transaction tests,
not proof of the projection or a renderer test.
"""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import hashlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import convert_sky


class SkyExportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.assets = Path(temporary.name) / 'night_sky'
        shutil.copytree(convert_sky.ASSETS, self.assets)
        self.original = {path.name: path.read_bytes() for path in self.assets.iterdir()}
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(convert_sky, 'ASSETS', self.assets))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))

    def export(self, command, **kwargs):
        target = Path(command[-1])
        index = int(target.stem.removeprefix('cubemap_'))
        target.write_bytes(self.original[f'cubemap_{(index + 1) % 6}.png'])

    def assert_unchanged(self):
        self.assertEqual({p.name: p.read_bytes() for p in self.assets.iterdir()}, self.original)

    def test_ffmpeg_failure_after_two_faces_preserves_old_files(self):
        def fail(command, **kwargs):
            if Path(command[-1]).name == 'cubemap_2.png':
                raise subprocess.CalledProcessError(1, command)
            self.export(command, **kwargs)
        with patch.object(convert_sky.subprocess, 'run', side_effect=fail):
            with self.assertRaises(subprocess.CalledProcessError):
                convert_sky.main()
        self.assert_unchanged()

    def test_truncated_successful_output_is_not_installed(self):
        def truncated(command, **kwargs):
            self.export(command, **kwargs)
            path = Path(command[-1])
            path.write_bytes(path.read_bytes()[:-12])
        with patch.object(convert_sky.subprocess, 'run', side_effect=truncated):
            with self.assertRaisesRegex(ValueError, 'Incomplete exported sky PNG'):
                convert_sky.main()
        self.assert_unchanged()

    def test_install_failure_rolls_back_faces_and_manifest(self):
        replace = convert_sky.os.replace
        failed = False
        def fail_once(source, target):
            nonlocal failed
            if Path(target).name == 'cubemap_3.png' and not failed:
                failed = True
                raise OSError('simulated write error')
            replace(source, target)
        with patch.object(convert_sky.subprocess, 'run', side_effect=self.export), \
                patch.object(convert_sky.os, 'replace', side_effect=fail_once):
            with self.assertRaisesRegex(OSError, 'simulated write error'):
                convert_sky.main()
        self.assert_unchanged()

    def test_failed_rollback_retains_original_files_for_recovery(self):
        replace = convert_sky.os.replace
        calls = 0
        def fail_persistently(source, target):
            nonlocal calls
            calls += 1
            if calls > 2:
                raise OSError('filesystem became read-only')
            replace(source, target)
        with patch.object(convert_sky.subprocess, 'run', side_effect=self.export), \
                patch.object(convert_sky.os, 'replace', side_effect=fail_persistently):
            with self.assertRaises(convert_sky.SkyRecoveryError) as caught:
                convert_sky.main()
        backup = caught.exception.backup
        self.assertTrue(backup.is_dir())
        for name in (*convert_sky.FACE_NAMES, 'source.json'):
            self.assertEqual((backup / name).read_bytes(), self.original[name])
        self.assertIn(str(backup), str(caught.exception))

    def test_extra_preview_is_preserved_but_not_registered(self):
        preview = self.assets / 'preview.png'
        preview.write_bytes(b'local preview')
        with patch.object(convert_sky.subprocess, 'run', side_effect=self.export):
            convert_sky.main()
        manifest = json.loads((self.assets / 'source.json').read_text(encoding='utf-8'))
        expected = {'source.png', 'source-v2.png', *(f'cubemap_{i}.png' for i in range(6))}
        self.assertEqual(set(manifest['sha256']), expected)
        for name, digest in manifest['sha256'].items():
            self.assertEqual(hashlib.sha256((self.assets / name).read_bytes()).hexdigest(), digest)
        self.assertNotEqual((self.assets / 'cubemap_0.png').read_bytes(), self.original['cubemap_0.png'])
        self.assertEqual(preview.read_bytes(), b'local preview')
        self.assertFalse(list(self.assets.glob('.sky-export-*')))

    def test_missing_original_artwork_fails_before_any_conversion(self):
        (self.assets / 'source.png').unlink()
        self.original.pop('source.png')
        with patch.object(convert_sky.subprocess, 'run') as export:
            with self.assertRaises(FileNotFoundError):
                convert_sky.main()
        export.assert_not_called()
        self.assert_unchanged()


if __name__ == '__main__':
    unittest.main()
