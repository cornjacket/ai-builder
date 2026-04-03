"""Unit tests for build_master_index.py"""

import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ai-builder" / "orchestrator"))

from build_master_index import (
    build_master_index,
    _collect_entries,
    _extract_header,
    _extract_user_blocks,
)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


class TestExtractHeader(unittest.TestCase):
    def test_extracts_purpose_and_tags(self):
        with tempfile.TemporaryDirectory() as d:
            f = _write(Path(d) / "doc.md",
                "Purpose: Handles user authentication.\nTags: auth, security\n")
            purpose, tags = _extract_header(f)
            self.assertEqual(purpose, "Handles user authentication.")
            self.assertEqual(tags, "auth, security")

    def test_purpose_first_sentence_only(self):
        with tempfile.TemporaryDirectory() as d:
            f = _write(Path(d) / "doc.md",
                "Purpose: First sentence. Second sentence.\nTags: foo\n")
            purpose, _ = _extract_header(f)
            self.assertEqual(purpose, "First sentence.")

    def test_missing_purpose_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            f = _write(Path(d) / "doc.md", "Tags: foo\n")
            purpose, tags = _extract_header(f)
            self.assertEqual(purpose, "")
            self.assertEqual(tags, "foo")

    def test_missing_tags_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            f = _write(Path(d) / "doc.md", "Purpose: Something.\n")
            purpose, tags = _extract_header(f)
            self.assertEqual(purpose, "Something.")
            self.assertEqual(tags, "")

    def test_no_headers_returns_empty_pair(self):
        with tempfile.TemporaryDirectory() as d:
            f = _write(Path(d) / "doc.md", "Just some prose.\n")
            self.assertEqual(_extract_header(f), ("", ""))

    def test_nonexistent_file_returns_empty_pair(self):
        purpose, tags = _extract_header(Path("/nonexistent/file.md"))
        self.assertEqual((purpose, tags), ("", ""))


class TestCollectEntries(unittest.TestCase):
    def test_collects_files_with_headers(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "auth" / "README.md",
                "Purpose: Auth module.\nTags: auth\n")
            entries = _collect_entries(root)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["purpose"], "Auth module.")

    def test_skips_root_readme(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "README.md", "Purpose: Root.\nTags: root\n")
            _write(root / "sub" / "doc.md", "Purpose: Sub.\nTags: sub\n")
            entries = _collect_entries(root)
            names = [e["path"].name for e in entries]
            self.assertNotIn("README.md", names)
            self.assertIn("doc.md", names)

    def test_skips_master_index(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "master-index.md", "Purpose: Index.\nTags: index\n")
            entries = _collect_entries(root)
            self.assertEqual(entries, [])

    def test_skips_files_without_headers(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "notes.md", "Just some notes.\n")
            entries = _collect_entries(root)
            self.assertEqual(entries, [])

    def test_depth_calculation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "a" / "doc.md", "Purpose: A.\nTags: a\n")
            _write(root / "a" / "b" / "doc.md", "Purpose: B.\nTags: b\n")
            entries = {str(e["path"]): e["depth"] for e in _collect_entries(root)}
            self.assertEqual(entries["a/doc.md"], 1)
            self.assertEqual(entries["a/b/doc.md"], 2)


class TestExtractUserBlocks(unittest.TestCase):
    def test_extracts_user_block(self):
        with tempfile.TemporaryDirectory() as d:
            f = _write(Path(d) / "master-index.md", "\n".join([
                "# myproject",
                "",
                "## auth",
                "",
                "<!-- user-doc-start -->",
                "My custom notes.",
                "<!-- user-doc-end -->",
                "",
            ]))
            blocks = _extract_user_blocks(f)
            self.assertIn("auth", blocks)
            self.assertEqual(blocks["auth"], "My custom notes.")

    def test_returns_empty_when_file_missing(self):
        blocks = _extract_user_blocks(Path("/nonexistent/master-index.md"))
        self.assertEqual(blocks, {})

    def test_returns_empty_when_no_sentinels(self):
        with tempfile.TemporaryDirectory() as d:
            f = _write(Path(d) / "master-index.md", "# title\n\n## section\n\nContent.\n")
            blocks = _extract_user_blocks(f)
            self.assertEqual(blocks, {})


class TestBuildMasterIndex(unittest.TestCase):
    def test_writes_index_file(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "auth" / "README.md", "Purpose: Auth.\nTags: auth\n")
            build_master_index(root)
            self.assertTrue((root / "master-index.md").exists())

    def test_index_contains_entry(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "auth" / "README.md", "Purpose: Auth module.\nTags: auth\n")
            build_master_index(root)
            content = (root / "master-index.md").read_text()
            self.assertIn("Auth module.", content)
            self.assertIn("auth", content)

    def test_custom_dest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            dest = Path(d) / "index.md"
            _write(root / "x" / "doc.md", "Purpose: X.\nTags: x\n")
            build_master_index(root, dest)
            self.assertTrue(dest.exists())

    def test_preserves_user_blocks_on_rebuild(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "auth" / "README.md", "Purpose: Auth.\nTags: auth\n")
            # First build
            build_master_index(root)
            # Inject user block
            dest = root / "master-index.md"
            original = dest.read_text()
            with_block = original.replace(
                "## auth",
                "## auth\n\n<!-- user-doc-start -->\nMy notes.\n<!-- user-doc-end -->",
            )
            dest.write_text(with_block)
            # Second build — user block must survive
            build_master_index(root)
            result = dest.read_text()
            self.assertIn("My notes.", result)

    def test_idempotent_rebuild(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            _write(root / "x" / "doc.md", "Purpose: X.\nTags: x\n")
            build_master_index(root)
            first = (root / "master-index.md").read_text()
            build_master_index(root)
            second = (root / "master-index.md").read_text()
            self.assertEqual(first, second)

    def test_title_uses_directory_name(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "my-output"
            _write(root / "x" / "doc.md", "Purpose: X.\nTags: x\n")
            build_master_index(root)
            content = (root / "master-index.md").read_text()
            self.assertIn("# my-output", content)

    def test_empty_output_dir_produces_minimal_index(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "output"
            root.mkdir()
            build_master_index(root)
            content = (root / "master-index.md").read_text()
            # Should at least have the title
            self.assertIn("# output", content)


if __name__ == "__main__":
    unittest.main()
