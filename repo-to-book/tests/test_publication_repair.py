"""In-place topic-directory delivery and outline chapter alignment checks."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/repo-to-write/scripts'))
import book


def adapt_manuscript_to_chapter_dir(text: str, cid: str) -> str:
    text = text.replace(f'../chapters/{cid}/assets/', 'assets/')
    text = text.replace('(../sources.md#', '(../../sources.md#')
    text = text.replace('(03-boundaries.md#', '(../03-boundaries/manuscript.md#')
    return text


class InPlaceDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.topic = self.root / 'topic'
        shutil.copytree(ROOT / 'examples/mini-pipeline/research', self.topic)
        book.prepare_book(self.topic)
        for p in (ROOT / 'examples/mini-pipeline/publication/manuscript').glob('*.md'):
            cid = p.stem
            adapted = adapt_manuscript_to_chapter_dir(p.read_text(encoding='utf-8'), cid)
            (self.topic / 'chapters' / cid / 'manuscript.md').write_text(adapted, encoding='utf-8')
        self.cfg = json.loads((self.topic / 'book.json').read_text(encoding='utf-8'))
        self.cfg['chapter_reviews'] = {p: 'approved' for p in self.cfg['chapters']}
        self.cfg['visual_review'] = 'passed'
        self.save()
        (self.topic / 'writing-review.md').write_text('# Review\n<!-- r2b:reviewed -->\nVerified example.\n', encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        (self.topic / 'book.json').write_text(json.dumps(self.cfg, ensure_ascii=False), encoding='utf-8')

    def test_delivery_records_can_pass(self):
        self.assertEqual(book.main(['check', str(self.topic), '--delivery']), 0)

    def test_preview_allowed_but_chapter_dropping_or_reordering_rejected_on_delivery(self):
        # Single-chapter preview check passes, but delivery check rejects diverging from confirmed outline
        self.cfg['chapters'] = [self.cfg['chapters'][2]]
        self.save()
        self.assertEqual(book.main(['check', str(self.topic)]), 0)
        self.assertEqual(book.main(['check', str(self.topic), '--delivery']), 2)

    def test_chapter_reordering_rejected_on_delivery(self):
        self.cfg['chapters'] = list(reversed(self.cfg['chapters']))
        self.save()
        with self.assertRaisesRegex(book.BookError, '严格一致'):
            book.check_delivery(self.topic, self.cfg)

    def test_updating_materials_in_place_preserves_manuscript(self):
        manuscript_path = self.topic / 'chapters/02-trace/manuscript.md'
        original_prose = manuscript_path.read_text(encoding='utf-8')
        materials_path = self.topic / 'chapters/02-trace/materials.md'
        materials_path.write_text(materials_path.read_text(encoding='utf-8') + '\n补充事实细化：位宽 32-bit。\n', encoding='utf-8')
        book.prepare_book(self.topic)
        self.assertEqual(manuscript_path.read_text(encoding='utf-8'), original_prose)
        self.assertEqual(book.main(['build', str(self.topic)]), 0)
        self.assertTrue((self.topic / 'dist/book.html').is_file())

    def test_pending_review_and_core_gap_block_delivery(self):
        (self.topic / 'writing-review.md').write_text('<!-- r2b:pending -->', encoding='utf-8')
        with self.assertRaisesRegex(book.BookError, '统稿'):
            book.check_delivery(self.topic, self.cfg)
        (self.topic / 'writing-review.md').write_text('<!-- r2b:reviewed -->', encoding='utf-8')
        self.cfg['core_gaps'] = [{'id': 'gap-1', 'status': 'open', 'chapters': ['chapters/02-trace/manuscript.md']}]
        with self.assertRaisesRegex(book.BookError, '核心缺口'):
            book.check_delivery(self.topic, self.cfg)

    def test_pending_visual_review_blocks_delivery_but_not_build(self):
        self.cfg['visual_review'] = 'pending'
        self.save()
        self.assertEqual(book.main(['build', str(self.topic)]), 0)
        with self.assertRaisesRegex(book.BookError, '视觉验收'):
            book.check_delivery(self.topic, self.cfg)


if __name__ == '__main__':
    unittest.main()
