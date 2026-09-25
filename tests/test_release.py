"""Release metadata failures tested against minimal isolated fixtures."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write("scripts/create_pack.py", "raise RuntimeError('must not import')\nVERSION = [1, 2, 3]\n")
        manifest = {"header": {"version": [1, 2, 3], "uuid": "lumen"},
                    "modules": [{"version": [1, 2, 3]}]}
        self.write("pack/manifest.json", json.dumps(manifest))
        self.write("CHANGELOG.md", "# Changes\n\n## [1.2.3]\n")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def change_json(self, relative, edit):
        path = self.root / relative
        value = json.loads(path.read_text(encoding="utf-8"))
        edit(value)
        self.write(relative, json.dumps(value))

    def test_version_and_tag_without_importing_generator_or_requiring_addon_files(self):
        for tag in (None, "v1.2.3"):
            with self.subTest(tag=tag):
                self.assertEqual(check_release.check_release(self.root, tag),
                                 {"lumen": "1.2.3"})

    def test_branch_check_does_not_require_release_changelog(self):
        (self.root / "CHANGELOG.md").unlink()
        check_release.check_release(self.root)
        with self.assertRaises(FileNotFoundError):
            check_release.check_release(self.root, "v1.2.3")

    def test_nonliteral_ambiguous_and_invalid_source_versions_fail(self):
        for assignment in ("VERSION = list((1, 2, 3))", "VERSION = [1, 2, 3]\nVERSION = [1, 2, 3]",
                           "VERSION = [1, 2]", "VERSION = [1, -1, 3]", "VERSION = [1, True, 3]"):
            with self.subTest(assignment=assignment):
                self.write("scripts/create_pack.py", assignment)
                with self.assertRaises(ValueError):
                    check_release.check_release(self.root)

    def test_manifest_header_and_every_module_must_match_generator(self):
        relative = "pack/manifest.json"
        self.change_json(relative, lambda manifest: manifest["modules"].append({"version": [1, 2, 3]}))
        original = (self.root / relative).read_text(encoding="utf-8")
        for section in ("header", 0, 1):
            with self.subTest(section=section):
                def edit(manifest):
                    entry = manifest["header"] if section == "header" else manifest["modules"][section]
                    entry["version"] = [9, 9, 9]
                self.change_json(relative, edit)
                with self.assertRaisesRegex(ValueError, "version differs"):
                    check_release.check_release(self.root)
                self.write(relative, original)

    def test_manifest_requires_modules(self):
        for modules in ([], None, {}):
            with self.subTest(modules=modules):
                self.change_json("pack/manifest.json", lambda manifest: manifest.update(modules=modules))
                with self.assertRaisesRegex(ValueError, "missing modules"):
                    check_release.check_release(self.root)

    def test_malformed_or_mismatched_tags_fail(self):
        for tag in ("v01.2.3", "v1.2", "v1.2.3-rc.1", "v1.2.3+build", "v1.2.3\n",
                    "refs/tags/v1.2.3", "birds-0.2.0", "birds-v0.2.0", "birds-v1.2.3",
                    "addons-v1.2.3", "v0.2.0", "xv1.2.3", ""):
            with self.subTest(tag=tag):
                with self.assertRaises(ValueError):
                    check_release.check_release(self.root, tag)

    def test_release_heading_allows_date_or_status_suffix(self):
        for content in ("## [1.2.3] - 2026-09-25\n", "## [1.2.3] - Kandidat\n"):
            with self.subTest(content=content):
                self.write("CHANGELOG.md", content)
                check_release.check_release(self.root, "v1.2.3")

    def test_release_requires_exact_version_heading_in_root_changelog(self):
        for content in ("## [1.2.30]\n", "## [1.2.3] extra\n", "### [1.2.3]\n"):
            with self.subTest(content=content):
                self.write("CHANGELOG.md", content)
                with self.assertRaisesRegex(ValueError, "missing release heading"):
                    check_release.check_release(self.root, "v1.2.3")


if __name__ == "__main__":
    unittest.main()
