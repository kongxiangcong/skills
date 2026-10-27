from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'skills/repo-to-research/scripts'))
sys.path.insert(0, str(ROOT/'skills/repo-to-book/scripts'))
import book
import handoff
import research
import install as installer

EXAMPLE = ROOT/'examples/mini-pipeline/research'
PUBLICATION = ROOT/'examples/mini-pipeline/publication'
# A real tiny bitmap used only as a file-format fixture, not an AI-generated illustration.
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a3eYAAAAASUVORK5CYII=')


def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bundle = self.root/'research 中文 space'
        shutil.copytree(EXAMPLE, self.bundle)

    def tearDown(self):
        self.temp.cleanup()

    def config(self):
        return json.loads((self.bundle/'research.json').read_text(encoding='utf-8'))

    def save(self, obj):
        (self.bundle/'research.json').write_text(json.dumps(obj, ensure_ascii=False), encoding='utf-8')

    def test_ready_package(self):
        obj=handoff.read_bundle(self.bundle)
        self.assertEqual(len(obj['chapters']),3)
        self.assertEqual(sum(len(c['assets']) for c in obj['chapters']),4)

    def test_contract_copies_are_identical(self):
        self.assertEqual((ROOT/'skills/repo-to-research/scripts/handoff.py').read_bytes(),
                         (ROOT/'skills/repo-to-book/scripts/handoff.py').read_bytes())

    def test_init_draft_and_no_overwrite(self):
        new = self.root/'new'
        research.init_research(new,'测试','https://example.org/project')
        self.assertEqual(handoff.read_bundle(new,False)['status'],'draft')
        with self.assertRaisesRegex(handoff.HandoffError,'draft'):
            handoff.read_bundle(new)
        with self.assertRaisesRegex(handoff.HandoffError,'非空'):
            research.init_research(new,'再次')
        self.assertFalse((new/'manuscript').exists())
        self.assertFalse((new/'book.json').exists())
        self.assertFalse((new/'dist').exists())

    def test_stage_two_rejects_draft(self):
        obj=self.config();obj['status']='draft';self.save(obj)
        with self.assertRaisesRegex(book.BookError,'draft'):
            book.prepare_book(self.bundle,self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_missing_chapter_materials(self):
        (self.bundle/self.config()['chapters'][1]['materials']).unlink()
        with self.assertRaisesRegex(handoff.HandoffError,'缺少交接文件'):
            handoff.read_bundle(self.bundle)

    def test_unfinished_chapter(self):
        obj=self.config();obj['chapters'][1]['status']='draft';self.save(obj)
        with self.assertRaisesRegex(handoff.HandoffError,'章节尚未就绪'):
            handoff.read_bundle(self.bundle)

    def test_pending_asset(self):
        obj=self.config();obj['chapters'][0]['assets'][0]['status']='pending';self.save(obj)
        with self.assertRaisesRegex(handoff.HandoffError,'尚未实际生成'):
            handoff.read_bundle(self.bundle)

    def test_missing_actual_asset(self):
        obj=self.config();(self.bundle/obj['chapters'][0]['assets'][0]['file']).unlink()
        with self.assertRaisesRegex(handoff.HandoffError,'缺少交接文件'):
            research.export_bundle(self.bundle,self.root/'out.zip')
        self.assertFalse((self.root/'out.zip').exists())

    def test_source_ids_must_exist(self):
        obj=self.config();obj['chapters'][0]['assets'][0]['evidence']=['not-present'];self.save(obj)
        with self.assertRaisesRegex(handoff.HandoffError,'不存在的来源'):
            handoff.read_bundle(self.bundle)

    def test_duplicate_source_anchor(self):
        p=self.bundle/'sources.md';p.write_text(p.read_text(encoding='utf-8')+'\n## duplicate {#s01}\n',encoding='utf-8')
        with self.assertRaisesRegex(handoff.HandoffError,'重复来源'):
            handoff.read_bundle(self.bundle)

    def test_pending_material_marker(self):
        p=self.bundle/self.config()['chapters'][0]['materials'];p.write_text('<!-- r2b:pending -->\n',encoding='utf-8')
        with self.assertRaisesRegex(handoff.HandoffError,'未完成标记'):
            handoff.read_bundle(self.bundle)

    def test_outside_path_rejected(self):
        (self.root/'outside.md').write_text('private',encoding='utf-8')
        obj=self.config();obj['plan']='../outside.md';self.save(obj)
        with self.assertRaisesRegex(handoff.HandoffError,'越出'):
            handoff.read_bundle(self.bundle)

    def test_machine_specific_path_rejected(self):
        obj=self.config();obj['plan']='C:/Users/me/plan.md';self.save(obj)
        with self.assertRaisesRegex(handoff.HandoffError,'相对路径'):
            handoff.read_bundle(self.bundle)

    def test_export_only_registered_files_and_stops_at_materials(self):
        (self.bundle/'.env').write_text('not-a-real-secret=fixture',encoding='utf-8')
        (self.bundle/'unregistered.txt').write_text('fixture',encoding='utf-8')
        out=self.root/'research.zip';research.export_bundle(self.bundle,out)
        with ZipFile(out) as z:
            names=z.namelist()
            self.assertNotIn('research/.env',names)
            self.assertNotIn('research/unregistered.txt',names)
            self.assertIn('research/START_HERE.md',names)
            self.assertIn('research/evidence/pipeline.py',names)
            self.assertFalse(any('/dist/' in n or '/manuscript/' in n for n in names))
            text=z.read('research/START_HERE.md').decode('utf-8')
            self.assertIn('只有用户另行调用',text)
        with self.assertRaisesRegex(handoff.HandoffError,'已存在'):
            research.export_bundle(self.bundle,out)

    def test_imagegen_requires_raster_and_prompt(self):
        obj=self.config();a=obj['chapters'][0]['assets'][0];a['method']='imagegen';self.save(obj)
        with self.assertRaisesRegex(handoff.HandoffError,'位图'):
            handoff.read_bundle(self.bundle)
        a['file']='chapters/01-overview/assets/generated.png'
        (self.bundle/a['file']).write_bytes(PNG)
        self.save(obj)
        with self.assertRaises(handoff.HandoffError):
            handoff.read_bundle(self.bundle)
        a['prompt']='chapters/01-overview/assets/generated.prompt.md'
        (self.bundle/a['prompt']).write_text('File-format fixture only; no real image generation.',encoding='utf-8')
        self.save(obj)
        self.assertEqual(handoff.read_bundle(self.bundle)['chapters'][0]['assets'][0]['method'],'imagegen')
        out=self.root/'images.zip';research.export_bundle(self.bundle,out)
        with ZipFile(out) as z:
            self.assertIn('research/'+a['file'],z.namelist())
            self.assertIn('research/'+a['prompt'],z.namelist())

    def test_text_renamed_png_rejected(self):
        obj=self.config();a=obj['chapters'][0]['assets'][0];a['method']='provided';a['file']='fake.png'
        (self.bundle/'fake.png').write_text('not an image',encoding='utf-8');self.save(obj)
        with self.assertRaisesRegex(handoff.HandoffError,'扩展名不符'):
            handoff.read_bundle(self.bundle)

    def test_diagram_requires_editable_source(self):
        obj=self.config();a=obj['chapters'][0]['assets'][0];a['method']='diagram-design';del a['editable'];self.save(obj)
        with self.assertRaises(handoff.HandoffError):
            handoff.read_bundle(self.bundle)

    def test_prepare_preserves_original_and_creates_no_prose(self):
        before=hashes(self.bundle);dest=self.root/'publication'
        book.prepare_book(self.bundle,dest)
        self.assertEqual(before,hashes(self.bundle))
        self.assertTrue((dest/'manuscript/01-overview.md').is_file())
        self.assertFalse((dest/'dist').exists())
        for name,digest in before.items():
            if name!='START_HERE.md':
                self.assertEqual(hashlib.sha256((dest/name).read_bytes()).hexdigest(),digest)
        with self.assertRaisesRegex(book.BookError,'模板'):
            book.Book(dest).html()
        with self.assertRaisesRegex(book.BookError,'已存在'):
            book.prepare_book(self.bundle,dest)

    def test_prepare_rejects_overlapping_directories(self):
        with self.assertRaisesRegex(book.BookError,'互相包含'):
            book.prepare_book(self.bundle,self.bundle/'book')

    def test_prepare_rejects_stage_two_reserved_paths(self):
        (self.bundle/'book.json').write_text('{}',encoding='utf-8')
        obj=self.config();obj['evidence_files'].append('book.json');self.save(obj)
        with self.assertRaisesRegex(book.BookError,'写作阶段路径'):
            book.prepare_book(self.bundle,self.root/'out')

    def test_html_is_default_and_needs_no_pdf_call(self):
        dest=self.root/'pub';shutil.copytree(PUBLICATION,dest,ignore=shutil.ignore_patterns('dist'))
        with patch('book.write_pdf',side_effect=AssertionError('must not call PDF')) as pdf:
            self.assertEqual(book.main(['build',str(dest)]),0)
            pdf.assert_not_called()
        self.assertTrue((dest/'dist/book.html').is_file())
        self.assertFalse((dest/'dist/book.pdf').exists())
        self.assertNotIn('playwright',(ROOT/'skills/repo-to-book/requirements.txt').read_text(encoding='utf-8'))

    def test_isolated_writer_without_research_skill_or_network(self):
        # Copy only the writing skill + exported raw materials to another directory.
        isolated=self.root/'isolated';isolated.mkdir()
        skill=isolated/'writer';shutil.copytree(ROOT/'skills/repo-to-book',skill)
        outzip=self.root/'handoff.zip';research.export_bundle(self.bundle,outzip)
        with ZipFile(outzip) as z:z.extractall(isolated)
        # Isolated import path; socket is blocked. No researcher skill is in this directory.
        runner=isolated/'run_offline.py'
        runner.write_text('''import sys, socket
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'writer/scripts'))
def no_network(*a,**k): raise AssertionError('network access forbidden')
socket.socket=no_network
import book
book.prepare_book(root/'research',root/'publication')
''',encoding='utf-8')
        result=subprocess.run([sys.executable,str(runner)],cwd=isolated,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse((isolated/'repo-to-research').exists())
        # Authored chapter fixture simulates files supplied by a separate writer, not an actual model call.
        for p in (PUBLICATION/'manuscript').glob('*.md'):
            shutil.copy2(p,isolated/'publication/manuscript'/p.name)
        runner.write_text('''import sys, socket
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'writer/scripts'))
def no_network(*a,**k): raise AssertionError('network access forbidden')
socket.socket=no_network
import book
raise SystemExit(book.main(['build',str(root/'publication')]))
''',encoding='utf-8')
        result=subprocess.run([sys.executable,str(runner)],cwd=isolated,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((isolated/'publication/dist/book.html').is_file())
        self.assertFalse((isolated/'publication/dist/book.pdf').exists())


class InstallerTests(unittest.TestCase):
    def test_two_independent_skills_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'skills';installer.install(dest)
            for name in installer.NAMES:self.assertTrue((dest/name/'SKILL.md').is_file())
            self.assertFalse((dest/'repo-to-book/scripts/research.py').exists())
            self.assertFalse((dest/'repo-to-research/scripts/book.py').exists())
            with self.assertRaisesRegex(ValueError,'已存在'):installer.install(dest)

    def test_install_writer_only(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'skills';installer.install(dest,('repo-to-book',))
            self.assertTrue((dest/'repo-to-book/scripts/book.py').is_file())
            self.assertFalse((dest/'repo-to-research').exists())

    def test_install_researcher_only(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'skills';installer.install(dest,('repo-to-research',))
            result=subprocess.run([sys.executable,str(dest/'repo-to-research/scripts/research.py'),'check',str(EXAMPLE)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_missing_existing_one_does_not_partially_install(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'skills';(dest/'repo-to-book').mkdir(parents=True)
            with self.assertRaises(ValueError):installer.install(dest)
            self.assertFalse((dest/'repo-to-research').exists())

    def test_writer_requires_explicit_invocation(self):
        self.assertIn('allow_implicit_invocation: false',(ROOT/'skills/repo-to-book/agents/openai.yaml').read_text(encoding='utf-8'))
        self.assertIn('allow_implicit_invocation: false',(ROOT/'skills/repo-to-research/agents/openai.yaml').read_text(encoding='utf-8'))


if __name__=='__main__':
    unittest.main()
