"""Distribution inputs must exclude local files without needing Git."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from source_archive import source_entries


class SourceArchiveTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def write(self, name):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('fixture')
        return path

    def test_project_sources_and_skills_survive_without_git(self):
        names = ['LICENSE', '.gitattributes', '.gitignore', 'README.md', 'scripts/build.py',
                 'tests/test_package.py', 'pack/manifest.json', 'reference/source.json',
                 'assets/night_sky/source.json', 'docs/benchmark.csv',
                 '.agents/skills/lumen-release/SKILL.md', '.github/workflows/build.yml']
        for name in names:
            self.write(name)
        self.assertEqual(set(source_entries(self.root)), {'lumen-bedrock/' + name for name in names})

    def test_credentials_environments_caches_and_scratch_files_are_excluded(self):
        for name in ['.env', '.env.local', 'notes.md', 'private/config.json',
                     '.git/config', '.venv/lib/site.py', 'venv/site.py',
                     'node_modules/package/index.json', 'dist/old.zip',
                     'scripts/__pycache__/cache.py', 'scripts/.env',
                     'docs/.DS_Store', 'docs/output.log', 'docs/.local/credentials.json',
                     'scripts/venv/lib.py', 'tests/node_modules/package.json']:
            self.write(name)
        self.assertEqual(source_entries(self.root), {})

    def test_file_symlinks_are_rejected(self):
        secret = self.write('local/private.md')
        (self.root / 'docs').mkdir()
        (self.root / 'docs/leak.md').symlink_to(secret)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            source_entries(self.root)

    def test_directory_symlinks_are_rejected(self):
        self.write('local/private.md')
        (self.root / 'docs').symlink_to(self.root / 'local', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            source_entries(self.root)


if __name__ == '__main__':
    unittest.main()
