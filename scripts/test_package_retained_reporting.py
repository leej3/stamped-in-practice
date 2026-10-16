"""Regression checks for additive extraction and portable evidence packaging."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "packaging", Path(__file__).with_name("package_retained_reporting.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PackagingTest(unittest.TestCase):
    def test_unique_whitespace_link_retains_exact_receipt(self):
        text = "[Response JSON]( /recorded/judge/response.json)"
        path, receipt = MODULE.selected_link(text, Path("/recorded/judge"), "response", ".json")
        self.assertEqual(path, Path("response.json"))
        self.assertEqual(receipt["quote"], text)
        self.assertEqual(receipt["original_target"], " /recorded/judge/response.json")

    def test_ambiguous_or_escaping_links_fail(self):
        for text in ("[Response]( /elsewhere/response.json)",
                     "[Response]( ../response.json)",
                     "[Response]( a.json) [Response]( b.json)"):
            with self.assertRaises(ValueError):
                MODULE.selected_link(text, Path("/recorded/judge"), "response", ".json")

    def test_copies_are_independent_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            snapshot = root / "snapshot"
            snapshot.mkdir()
            (snapshot / "source-manifest.json").write_text("[]")
            source = snapshot / "source.json"
            source.write_text('{"evidence": true}')
            package = MODULE.Package(snapshot, root / "portable")
            package.capture(source, "index.json")
            package.finish({})
            self.assertNotEqual(source.stat().st_ino, (package.output / "index.json").stat().st_ino)
            self.assertTrue(MODULE.verify_package(package.output)["verified"])
            (package.output / "index.json").write_text("tampered")
            with self.assertRaises(ValueError):
                MODULE.verify_package(package.output)

    def test_source_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            snapshot = root / "snapshot"
            snapshot.mkdir()
            (snapshot / "source-manifest.json").write_text("[]")
            source = snapshot / "source.json"
            source.write_text("{}")
            package = MODULE.Package(snapshot, root / "portable")
            with self.assertRaises(ValueError):
                package.capture(source, expected="0" * 64)

    def test_normalization_handles_whitespace_delimiters_and_url_encoding(self):
        for target in (" /recorded/judge/response%20one.json ",
                       "< /recorded/judge/response%20one.json >", "response%20one.json "):
            relative, _ = MODULE.normalize_output_link(target, Path("/recorded/judge"))
            self.assertEqual(relative, Path("response one.json"))
        for target in ("%2e%2e/response.json", "https://example.org/response.json"):
            with self.assertRaises(ValueError):
                MODULE.normalize_output_link(target, Path("/recorded/judge"))


if __name__ == "__main__":
    unittest.main()
