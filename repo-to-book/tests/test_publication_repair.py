"""Recovery and scope checks using a real registered example bundle."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/repo-to-book/scripts'))
import book


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.research = self.root / 'research'
        self.pub = self.root / 'publication'
        shutil.copytree(ROOT / 'examples/mini-pipeline/research', self.research)
        book.prepare_book(self.research, self.pub)
        for p in (ROOT / 'examples/mini-pipeline/publication/manuscript').glob('*.md'):
            shutil.copy2(p, self.pub / 'manuscript' / p.name)
        self.cfg = json.loads((self.pub / 'book.json').read_text())
        self.cfg['chapter_reviews'] = {p: 'approved' for p in self.cfg['chapters']}
        self.cfg['visual_review'] = 'passed'
        self.save()
        (self.pub / 'writing-review.md').write_text('# Review\n<!-- r2b:reviewed -->\nVerified example.\n')

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        (self.pub / 'book.json').write_text(json.dumps(self.cfg))

    def change(self):
        p = self.research / 'chapters/02-trace/materials.md'
        p.write_text(p.read_text() + '\nCorrection: add precise execution evidence.\n')

    def test_delivery_records_can_pass(self):
        self.assertEqual(book.main(['check', str(self.pub), '--delivery']), 0)

    def test_preview_allowed_but_scope_reduction_rejected(self):
        # A self-contained chapter can be previewed without claiming complete delivery.
        self.cfg['chapters'] = [self.cfg['chapters'][2]]
        self.save()
        self.assertEqual(book.main(['check', str(self.pub)]), 0)
        self.assertEqual(book.main(['check', str(self.pub), '--delivery']), 2)

    def test_merged_and_split_scope_with_reason_allowed(self):
        targets = self.cfg['chapters']
        self.cfg['coverage'] = {
            '01-overview': {'chapters': targets[:2], 'reason': 'split introduction and walkthrough'},
            '02-trace': {'chapters': targets[1:2], 'reason': 'merged into walkthrough'},
            '03-boundaries': {'chapters': targets[2:], 'reason': ''}}
        book.check_delivery(self.pub, self.cfg)
        self.cfg['coverage']['01-overview']['reason'] = ''
        with self.assertRaisesRegex(book.BookError, '理由'):
            book.check_delivery(self.pub, self.cfg)

    def test_pending_review_and_core_gap_block_delivery(self):
        (self.pub / 'writing-review.md').write_text('<!-- r2b:pending -->')
        with self.assertRaisesRegex(book.BookError, '统稿'):
            book.check_delivery(self.pub, self.cfg)
        self.cfg['core_gaps'] = [{'id': 'gap-1', 'status': 'open', 'chapters': ['02-trace']}]
        with self.assertRaisesRegex(book.BookError, '核心缺口'):
            book.check_delivery(self.pub, self.cfg)

    def test_refresh_retains_prose_and_invalidates_only_local_review(self):
        self.change()
        before = {p.name: p.read_bytes() for p in (self.pub / 'manuscript').glob('*.md')}
        (self.pub / 'dist').mkdir()
        (self.pub / 'dist/book.html').write_text('old book')
        diff = book.refresh_book(self.research, self.pub)
        self.assertFalse(diff['applied'])
        self.assertEqual(diff['review_chapters'], ['manuscript/02-trace.md'])
        self.assertNotIn('Correction', (self.pub / 'chapters/02-trace/materials.md').read_text())
        self.assertTrue(book.refresh_book(self.research, self.pub, True)['applied'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.pub / 'manuscript').glob('*.md')})
        cfg = json.loads((self.pub / 'book.json').read_text())
        self.assertEqual(cfg['chapter_reviews']['manuscript/02-trace.md'], 'pending')
        self.assertEqual(cfg['chapter_reviews']['manuscript/01-overview.md'], 'approved')
        self.assertFalse((self.pub / 'dist').exists())
        with self.assertRaises(book.BookError):
            book.check_delivery(self.pub, cfg)
        cfg['chapter_reviews']['manuscript/02-trace.md'] = 'approved'
        cfg['visual_review'] = 'passed'
        (self.pub / 'writing-review.md').write_text('# Review\n<!-- r2b:reviewed -->\nRechecked correction.\n')
        book.check_delivery(self.pub, cfg)

    def test_shared_evidence_invalidates_all(self):
        p = self.research / 'evidence/run-results.json'
        p.write_text(p.read_text() + '\n')
        self.assertEqual(set(book.refresh_book(self.research, self.pub)['review_chapters']), set(self.cfg['chapters']))

    def test_copy_failure_preserves_original(self):
        self.change()
        before = {p.relative_to(self.pub).as_posix(): p.read_bytes() for p in self.pub.rglob('*') if p.is_file()}
        with patch('book.shutil.copy2', side_effect=OSError('injected copy failure')):
            with self.assertRaises(OSError):
                book.refresh_book(self.research, self.pub, True)
        self.assertEqual(before, {p.relative_to(self.pub).as_posix(): p.read_bytes() for p in self.pub.rglob('*') if p.is_file()})

    def test_double_rename_failure_keeps_recoverable_original(self):
        self.change()
        before = {p.relative_to(self.pub).as_posix(): p.read_bytes() for p in self.pub.rglob('*') if p.is_file()}
        real_rename = Path.rename
        calls = []
        def fail_swap_and_rollback(path, target):
            calls.append((path, target))
            if len(calls) > 1:
                raise OSError('injected rename failure')
            return real_rename(path, target)
        with patch.object(Path, 'rename', fail_swap_and_rollback):
            with self.assertRaisesRegex(book.BookError, '原稿完整保留') as failure:
                book.refresh_book(self.research, self.pub, True)
        self.assertEqual(len(calls), 3)
        backup = calls[0][1]
        self.assertTrue(backup.is_dir())
        self.assertIn(str(backup), str(failure.exception))
        self.assertIn(str(self.pub), str(failure.exception))
        self.assertEqual(before, {p.relative_to(backup).as_posix(): p.read_bytes() for p in backup.rglob('*') if p.is_file()})
        backup.rename(self.pub)
        self.assertEqual(book.main(['check', str(self.pub), '--delivery']), 0)

    def test_pending_visual_review_blocks_delivery_but_not_build(self):
        self.cfg['visual_review'] = 'pending'
        self.save()
        self.assertEqual(book.main(['build', str(self.pub)]), 0)
        with self.assertRaisesRegex(book.BookError, '视觉验收'):
            book.check_delivery(self.pub, self.cfg)

    def test_deliberate_scope_omission_requires_reason(self):
        self.cfg['chapters'] = [self.cfg['chapters'][2]]
        for cid in ('01-overview', '02-trace'):
            self.cfg['coverage'][cid] = {'chapters': [], 'reason': 'Scope changed to failure-boundary booklet.'}
        book.check_delivery(self.pub, self.cfg)
        self.cfg['coverage']['01-overview']['reason'] = ''
        with self.assertRaisesRegex(book.BookError, '理由'):
            book.check_delivery(self.pub, self.cfg)

    def test_reject_mixed_or_unregistered_material(self):
        p = self.pub / 'chapters/02-trace/materials.md'
        p.write_text(p.read_text() + '\nlocal edit\n')
        with self.assertRaisesRegex(book.BookError, '快照'):
            book.refresh_book(self.research, self.pub, True)
        with self.assertRaisesRegex(book.BookError, '快照'):
            book.check_delivery(self.pub, self.cfg)

    def test_repaired_bundle_cannot_silently_shrink_original_scope(self):
        manifest = self.research / 'research.json'
        data = json.loads(manifest.read_text())
        data['chapters'] = data['chapters'][2:]
        manifest.write_text(json.dumps(data))
        book.refresh_book(self.research, self.pub, True)
        cfg = json.loads((self.pub / 'book.json').read_text())
        self.assertEqual(set(cfg['research_scope']), {'01-overview', '02-trace', '03-boundaries'})
        cfg['chapter_reviews'] = {p: 'approved' for p in cfg['chapters']}
        cfg['visual_review'] = 'passed'
        (self.pub / 'writing-review.md').write_text('# Review\n<!-- r2b:reviewed -->\n')
        # Even retained manuscript mappings need a rationale when their source chapter disappears.
        with self.assertRaisesRegex(book.BookError, '理由'):
            book.check_delivery(self.pub, cfg)
        original_coverage = dict(cfg['coverage'])
        cfg['chapters'] = cfg['chapters'][2:]
        cfg['coverage'] = {'03-boundaries': original_coverage['03-boundaries']}
        with self.assertRaisesRegex(book.BookError, 'coverage'):
            book.check_delivery(self.pub, cfg)
        for cid in ('01-overview', '02-trace'):
            cfg['coverage'][cid] = {'chapters': [], 'reason': 'Agreed scope revision: publish failure boundaries only.'}
        book.check_delivery(self.pub, cfg)

    def test_removed_evidence_is_not_left_behind(self):
        r = self.research / 'research.json'
        data = json.loads(r.read_text())
        removed = data['evidence_files'].pop()
        r.write_text(json.dumps(data))
        book.refresh_book(self.research, self.pub, True)
        self.assertFalse((self.pub / removed).exists())


if __name__ == '__main__':
    unittest.main()
