from pathlib import Path
import importlib.util
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('extractor', Path(__file__).with_name('extract-stopped-judgment.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ExtractionTests(unittest.TestCase):
    def test_distinguishes_hypothesis(self):
        got = m.extract_adequacy('**Scientific adequacy: supported.** The hypothesis is not supported.\n')
        self.assertEqual(got['category'], 'supported')
        self.assertEqual(got['excerpt']['start_line'], 1)
    def test_conflicting_labels_unavailable(self):
        self.assertEqual(m.extract_adequacy('Scientific adequacy: supported\nScientific adequacy: qualified')['extraction_status'], 'ambiguous')
    def test_unknown_label_unavailable(self):
        self.assertIsNone(m.extract_adequacy('Scientific adequacy: supported\nScientific adequacy: uncertain')['category'])
    def test_ordinary_prose_not_label(self):
        self.assertEqual(m.extract_adequacy('The phrase Scientific adequacy: supported is an example.')['extraction_status'], 'missing')
    def test_unsupported_category_retained(self):
        self.assertEqual(m.extract_adequacy('## Scientific adequacy: not supported')['category'], 'not supported')
    def test_missing_label_unavailable(self):
        self.assertIsNone(m.extract_adequacy('This analysis supports its negative finding.')['category'])
    def test_unique_final_link_and_alias(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve(); (root/'report.md').write_text('x')
            text = f'[Report](<{root}/report.md>) [Full report](report.md)'
            self.assertEqual(m.select_output(text, root, 'report', '.md'), root/'report.md')
    def test_multiple_reports_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            for n in ['a.md','b.md']:(root/n).write_text('x')
            with self.assertRaises(ValueError):m.select_output('[report](a.md) [report](b.md)',root,'report','.md')
    def test_external_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve(); workspace=root/'workspace'; workspace.mkdir()
            (root/'outside.md').write_text('x'); (workspace/'report.md').symlink_to(root/'outside.md')
            with self.assertRaises(ValueError):m.select_output('[report](report.md)',workspace,'report','.md')

if __name__ == '__main__':unittest.main()
