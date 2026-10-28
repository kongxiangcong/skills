from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'skills/repo-to-research/scripts'))
sys.path.insert(0, str(ROOT / 'skills/repo-to-write/scripts'))
import book
import figure
import install as installer


class BookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'book space # 中文'
        shutil.copytree(ROOT / 'examples/mini-pipeline/publication', self.path, ignore=shutil.ignore_patterns('dist'))

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, path, old, new):
        target = self.path / path
        target.write_text(target.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')

    def test_example_builds_offline_html(self):
        b = book.Book(self.path)
        output = b.html()
        self.assertEqual(len(b.figures), 4)
        self.assertEqual(len(b.links), 12)
        self.assertIn('data:image/svg+xml;base64,', output)
        self.assertNotIn('<script', output)
        self.assertIn('id="sources--s01"', output)
        self.assertEqual(output.count('<figure>'), 4)

    def test_approved_layout_and_three_level_directory(self):
        cfgpath = self.path / 'book.json'
        cfg = json.loads(cfgpath.read_text())
        cfg['subtitle'] = 'LEGACY SUBTITLE MUST NOT APPEAR'
        cfgpath.write_text(json.dumps(cfg))
        chapter = self.path / cfg['chapters'][0]
        chapter.write_text(chapter.read_text() + '\n### 三级目录测试 {#third-level}\n\n说明。\n')
        b = book.Book(self.path)
        output = b.html()
        self.assertNotIn('LEGACY SUBTITLE MUST NOT APPEAR', output)
        self.assertNotIn('class="cover"', output)
        self.assertNotIn('阅读路线', output)
        self.assertIn('class="book-title"', output)
        self.assertIn('class="level-3"', output)
        self.assertIn('data-target="ch-01-overview--third-level"></span>', output)
        self.assertLess(output.index('class="book-title"'), output.index('<nav class="toc"'))

    def test_overview_position_and_stale_chapters(self):
        output = book.Book(self.path).html()
        self.assertLess(output.index('class="book-title"'), output.index('<figure class="book-overview"'))
        self.assertLess(output.index('<figure class="book-overview"'), output.index('<nav class="toc"'))
        cfgpath = self.path / 'book.json'
        cfg = json.loads(cfgpath.read_text())
        cfg['chapters'].reverse()
        cfgpath.write_text(json.dumps(cfg))
        with self.assertRaisesRegex(book.BookError, '重审结构图'):
            book.Book(self.path).html()

    def test_overview_requires_source_and_safe_image(self):
        (self.path / 'overview.mmd').unlink()
        with self.assertRaisesRegex(book.BookError, 'Mermaid'):
            book.Book(self.path).html()

    def test_config_controls_order(self):
        cfgpath = self.path / 'book.json'
        cfg = json.loads(cfgpath.read_text(encoding='utf-8'))
        cfg['chapters'].reverse()
        cfg.pop('overview', None)  # This test exercises chapter ordering for a legacy book.
        cfgpath.write_text(json.dumps(cfg), encoding='utf-8')
        output = book.Book(self.path).html()
        self.assertLess(output.index('<section class="chapter" id="ch-03-boundaries"'), output.index('<section class="chapter" id="ch-01-overview"'))

    def test_missing_figure_fails(self):
        (self.path / 'chapters/01-overview/assets/fig-01-01.svg').unlink()
        with self.assertRaisesRegex(book.BookError, '图片缺失'):
            book.Book(self.path).html()

    def test_missing_source_anchor_fails(self):
        self.mutate('manuscript/01-overview.md', '../sources.md#s01', '../sources.md#missing')
        with self.assertRaisesRegex(book.BookError, '锚点不存在'):
            book.Book(self.path).html()

    def test_cross_chapter_anchor_exists(self):
        output = book.Book(self.path).html()
        self.assertIn('href="#ch-03-boundaries--failure"', output)

    def test_missing_chapter_fails(self):
        (self.path / 'manuscript/02-trace.md').unlink()
        with self.assertRaisesRegex(book.BookError, '缺少 Markdown'):
            book.Book(self.path)

    def test_duplicate_chapter_fails(self):
        cfg = self.path / 'book.json'
        data = json.loads(cfg.read_text(encoding='utf-8'))
        data['chapters'].append(data['chapters'][0])
        cfg.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(book.BookError, '重复'):
            book.Book(self.path)

    def test_relative_escape_fails(self):
        self.mutate('manuscript/01-overview.md', '../chapters/01-overview/assets/fig-01-01.svg', '../../outside.svg')
        with self.assertRaisesRegex(book.BookError, '目录内'):
            book.Book(self.path).html()

    def test_remote_image_fails(self):
        self.mutate('manuscript/01-overview.md', '../chapters/01-overview/assets/fig-01-01.svg', 'https://example.com/figure.svg')
        with self.assertRaisesRegex(book.BookError, '本地'):
            book.Book(self.path).html()

    def test_svg_without_description_fails(self):
        p = self.path / 'chapters/01-overview/assets/fig-01-01.svg'
        import re
        p.write_text(re.sub(r'<desc.*?</desc>', '', p.read_text(encoding='utf-8')), encoding='utf-8')
        with self.assertRaisesRegex(book.BookError, 'desc'):
            book.Book(self.path).html()

    def test_svg_remote_font_fails(self):
        self.mutate('chapters/01-overview/assets/fig-01-01.svg', '<defs>', '<defs><style>@import url(https://example.com/font.css);</style>')
        with self.assertRaisesRegex(book.BookError, '字体'):
            book.Book(self.path).html()

    def test_svg_script_fails(self):
        self.mutate('chapters/01-overview/assets/fig-01-01.svg', '</svg>', '<script>alert(1)</script></svg>')
        with self.assertRaisesRegex(book.BookError, 'script'):
            book.Book(self.path).html()

    def test_svg_invalid_viewbox_fails(self):
        self.mutate('chapters/01-overview/assets/fig-01-01.svg', '0 0 960 400', '0 0 -960 400')
        with self.assertRaisesRegex(book.BookError, 'viewBox'):
            book.Book(self.path).html()

    def test_raw_html_not_executed(self):
        p = self.path / 'manuscript/01-overview.md'
        p.write_text(p.read_text(encoding='utf-8') + '\n<script>alert(1)</script>\n', encoding='utf-8')
        self.assertNotIn('<script>', book.Book(self.path).html())

    def test_empty_chapter_fails(self):
        (self.path / 'manuscript/02-trace.md').write_text('', encoding='utf-8')
        with self.assertRaisesRegex(book.BookError, '空稿'):
            book.Book(self.path).html()

    def test_duplicate_explicit_heading_fails(self):
        p = self.path / 'manuscript/01-overview.md'
        p.write_text(p.read_text(encoding='utf-8') + '\n## Duplicate {#contract}\n', encoding='utf-8')
        with self.assertRaisesRegex(book.BookError, '锚点重复'):
            book.Book(self.path).html()

    def test_mermaid_not_silently_printed_as_code(self):
        p = self.path / 'manuscript/01-overview.md'
        p.write_text(p.read_text(encoding='utf-8') + '\n```mermaid\ngraph TD;A-->B\n```\n', encoding='utf-8')
        with self.assertRaisesRegex(book.BookError, '静态 SVG'):
            book.Book(self.path).html()

    def test_init_and_no_overwrite(self):
        p = Path(self.temp.name) / 'new'
        book.init_book(p, '我的书')
        self.assertEqual(json.loads((p/'book.json').read_text(encoding='utf-8'))['title'], '我的书')
        with self.assertRaisesRegex(book.BookError, '模板'):
            book.Book(p).html()
        with self.assertRaisesRegex(book.BookError, '非空'):
            book.init_book(p, '不能覆盖')

    def test_wrap_preserves_svg_content(self):
        p = self.path / 'chapters/01-overview/assets/fig-01-01.svg'
        output = figure.wrap(p)
        self.assertIn(p.read_text(encoding='utf-8'), output.read_text(encoding='utf-8'))
        with self.assertRaises(figure.BookError):
            figure.wrap(p, p)

    def test_upstream_adapter_uses_real_cli_contract(self):
        skill = self.path / 'upstream'
        (skill/'scripts').mkdir(parents=True)
        for name in ['self_check.py','export_svg.py']:
            (skill/'scripts'/name).write_text('# stub used only for argv testing\n', encoding='utf-8')
        source = self.path/'chapters/01-overview/assets/fig-01-01.html'
        with patch('figure.subprocess.run', return_value=subprocess.CompletedProcess([], 0)) as run:
            output = figure.import_upstream(source, skill)
        self.assertEqual(run.call_count, 2)
        self.assertIn('--system-fonts', run.call_args_list[1].args[0])
        self.assertEqual(output.suffix, '.svg')

    def test_upstream_failure_does_not_fallback(self):
        skill = self.path / 'upstream'
        (skill/'scripts').mkdir(parents=True)
        for name in ['self_check.py','export_svg.py']:
            (skill/'scripts'/name).write_text('', encoding='utf-8')
        with patch('figure.subprocess.run', return_value=subprocess.CompletedProcess([], 1)) as run:
            with self.assertRaisesRegex(figure.BookError, '未绕过'):
                figure.import_upstream(self.path/'chapters/01-overview/assets/fig-01-01.html', skill)
        self.assertEqual(run.call_count, 1)

    def test_pdf_error_preserves_html_and_nonzero_status(self):
        with patch('book.write_pdf', side_effect=book.BookError('test missing browser')):
            result = book.main(['build', str(self.path), '--format', 'pdf'])
        self.assertEqual(result, 2)
        self.assertTrue((self.path/'dist/book.html').is_file())
        self.assertFalse((self.path/'dist/book.pdf').exists())

    def test_cli_paths_with_spaces_unicode_hash(self):
        result = subprocess.run([sys.executable, str(ROOT/'skills/repo-to-write/scripts/book.py'), 'check', str(self.path)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))


class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT/'examples/mini-pipeline/source/pipeline.py'
        spec = importlib.util.spec_from_file_location('mini_pipeline_fixture', path)
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_add(self):
        self.assertEqual(self.module.run('ADD 2 3'), 5)

    def test_multiply(self):
        self.assertEqual(self.module.run('MUL 2 3'), 6)

    def test_normalization(self):
        self.assertEqual(self.module.compile_expression('add 02 3'), self.module.Plan('ADD', 2, 3))

    def test_invalid_paths(self):
        for value in ['DIV 2 3', 'ADD two 3', 'ADD 2']:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.module.run(value)
        with self.assertRaises(ValueError):
            self.module.execute(self.module.Plan('DIV', 2, 3))

    def test_evidence_snapshot_matches_code(self):
        source = ROOT/'examples/mini-pipeline/source/pipeline.py'
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertIn(digest, (ROOT/'examples/mini-pipeline/publication/sources.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
