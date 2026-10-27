"""Observable migration and packaged offline-writer contracts, not prose-quality tests."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import install


class WriterUpdateTests(unittest.TestCase):
    def test_old_writer_blocks_all_before_any_install(self):
        with tempfile.TemporaryDirectory() as t:
            dest = Path(t)/'skills'
            (dest/'repo-to-book').mkdir(parents=True)
            marker = dest/'repo-to-book/user-file.md'
            marker.write_text('preserve user work', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, '旧写作技能'):
                install.install(dest)
            self.assertFalse((dest/'repo-to-write').exists())
            self.assertFalse((dest/'repo-to-research').exists())
            self.assertEqual(marker.read_text(encoding='utf-8'), 'preserve user work')

    def test_research_only_can_coexist_with_old_writer(self):
        with tempfile.TemporaryDirectory() as t:
            dest = Path(t)/'skills'
            (dest/'repo-to-book').mkdir(parents=True)
            install.install(dest, ('repo-to-research',))
            self.assertTrue((dest/'repo-to-research/SKILL.md').is_file())
            self.assertFalse((dest/'repo-to-write').exists())

    def test_old_name_rejected_without_creating_destination(self):
        with tempfile.TemporaryDirectory() as t:
            dest = Path(t)/'skills'
            with self.assertRaises(ValueError):
                install.install(dest, ('repo-to-book',))
            self.assertFalse(dest.exists())

    def test_release_cli_and_extracted_writer_work_without_researcher(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)/'archives'
            result = subprocess.run([sys.executable, str(ROOT/'scripts/package.py'), '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in out.iterdir()}, {'repo-to-book-project.zip', 'repo-to-research-skill.zip', 'repo-to-write-skill.zip'})
            with ZipFile(out/'repo-to-write-skill.zip') as z:
                self.assertTrue(all(n.startswith('repo-to-write/') for n in z.namelist()))
                self.assertIn('repo-to-write/references/writing.md', z.namelist())
                self.assertIn('repo-to-write/THIRD_PARTY_NOTICES.md', z.namelist())
                z.extractall(Path(t)/'isolated')
            writer = Path(t)/'isolated/repo-to-write'
            for args in [('prepare', str(ROOT/'examples/mini-pipeline/research'), str(Path(t)/'pub')),
                         ('check', str(ROOT/'examples/priority-queue/publication'), '--delivery')]:
                result = subprocess.run([sys.executable, str(writer/'scripts/book.py'), *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('repo-to-write', (Path(t)/'pub/START_HERE.md').read_text(encoding='utf-8'))

    def test_discovery_metadata_and_no_legacy_folder(self):
        writer = ROOT/'skills/repo-to-write'
        frontmatter = (writer/'SKILL.md').read_text(encoding='utf-8').split('---', 2)[1]
        metadata = (writer/'agents/openai.yaml').read_text(encoding='utf-8')
        self.assertIn('name: '+writer.name, frontmatter.splitlines())
        self.assertIn('$repo-to-write', metadata)
        self.assertIn('allow_implicit_invocation: false', metadata)
        self.assertFalse((ROOT/'skills/repo-to-book').exists())


if __name__ == '__main__':
    unittest.main()
