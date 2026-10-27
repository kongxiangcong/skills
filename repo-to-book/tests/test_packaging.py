"""Release allowlist tests use synthetic files, never real credentials."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release_package', ROOT/'scripts/package.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'source'
        self.root.mkdir()
        (self.root/'README.md').write_text('release source', encoding='utf-8')
        self.manifest = self.root/'release-files.txt'
        self.manifest.write_text('README.md\n', encoding='utf-8')
        self.out = Path(self.tmp.name)/'release.zip'
        self.patcher = patch.object(package, 'ROOT', self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_only_explicit_release_files_ship(self):
        for name in ('.env.local', 'credentials.json', 'unrelated-notes.md'):
            (self.root/name).write_text('synthetic secret or unrelated text', encoding='utf-8')
        outside = Path(self.tmp.name)/'outside.txt'
        outside.write_text('synthetic outside content', encoding='utf-8')
        try:
            (self.root/'outside-link.txt').symlink_to(outside)
        except OSError:
            pass  # Windows without symlink permission still tests ordinary exclusions.
        self.assertEqual(package.archive(self.root, self.out, 'project'), 1)
        with ZipFile(self.out) as archive:
            self.assertEqual(archive.namelist(), ['project/README.md'])
            self.assertNotIn(b'synthetic', archive.read('project/README.md'))

    def test_listed_external_symlink_is_rejected_before_archive_created(self):
        outside = Path(self.tmp.name)/'outside.txt'
        outside.write_text('synthetic', encoding='utf-8')
        try:
            (self.root/'link.md').symlink_to(outside)
        except OSError:
            self.skipTest('symlink creation unavailable')
        self.manifest.write_text('README.md\nlink.md\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '符号链接'):
            package.archive(self.root, self.out, 'project')
        self.assertFalse(self.out.exists())

    def test_symlink_directory_and_internal_symlink_rejected(self):
        directory = self.root/'real'
        directory.mkdir()
        (directory/'file.md').write_text('synthetic', encoding='utf-8')
        try:
            (self.root/'linked').symlink_to(directory, target_is_directory=True)
        except OSError:
            self.skipTest('symlink creation unavailable')
        self.manifest.write_text('linked/file.md\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '符号链接'):
            package.archive(self.root, self.out, 'project')

    def test_invalid_or_missing_manifest_paths_fail(self):
        for entry in ('../outside.txt', '/absolute.txt', '*.md', 'README.md\nREADME.md', 'missing.md', './README.md'):
            with self.subTest(entry=entry):
                self.manifest.write_text(entry+'\n', encoding='utf-8')
                with self.assertRaises(ValueError):
                    package.archive(self.root, self.out, 'project')
                self.assertFalse(self.out.exists())

    def test_skill_archive_is_exact_subtree_of_manifest(self):
        skill = self.root/'skills/example'
        skill.mkdir(parents=True)
        (skill/'SKILL.md').write_text('skill', encoding='utf-8')
        (skill/'private.md').write_text('not released', encoding='utf-8')
        self.manifest.write_text('README.md\nskills/example/SKILL.md\n', encoding='utf-8')
        package.archive(skill, self.out, 'example')
        with ZipFile(self.out) as archive:
            self.assertEqual(archive.namelist(), ['example/SKILL.md'])

    def test_real_project_and_both_skill_archives(self):
        with patch.object(package, 'ROOT', ROOT):
            for source in (ROOT, ROOT/'skills/repo-to-research', ROOT/'skills/repo-to-write'):
                target = Path(self.tmp.name)/(source.name + str(len(source.parts))+'.zip')
                self.assertGreater(package.archive(source, target, source.name), 0)
                with ZipFile(target) as archive:
                    self.assertEqual(archive.testzip(), None)


if __name__ == '__main__':
    unittest.main()
