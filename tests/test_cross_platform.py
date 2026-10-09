"""跨平台兼容测试：UTF-8 读写、OCR 延迟初始化、清单结构报错、打包缺文稿提示。"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import 手排 as S  # noqa: E402
import check_all  # noqa: E402
import package  # noqa: E402


class Utf8Tests(unittest.TestCase):
    def test_scripts_do_not_use_default_encoding(self):
        for path in (ROOT / "scripts").glob("*.py"):
            self.assertNotIn(".read_text()", path.read_text(encoding="utf-8"), path.name)

    def test_write_script_uses_utf8(self):
        with tempfile.TemporaryDirectory() as td:
            S.init(td)
            S.pages[:] = []
            S.write_script("测试", "手排.py")
            raw = (Path(td) / "页面脚本.json").read_bytes()
            self.assertEqual(json.loads(raw.decode("utf-8"))["topic"], "测试")


class LazyOcrTests(unittest.TestCase):
    def test_init_does_not_call_swiftc(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(S.subprocess, "run") as run:
            S.init(td)
            run.assert_not_called()

    def test_missing_swift_gives_clear_error(self):
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "bin/tool"
            with mock.patch.object(S.sys, "platform", "win32"):
                with self.assertRaisesRegex(RuntimeError, "macOS"):
                    S._ensure_tool(missing, "ocrfind.swift", "OCR 词框")


class ManifestTests(unittest.TestCase):
    def test_array_manifest_gives_friendly_error(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "素材清单.json"
            p.write_text(json.dumps([{"path": "a.png", "sha256": "x"}]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "assets"):
                check_all.load_manifest(p)

    def test_valid_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "素材清单.json"
            p.write_text(json.dumps({"assets": [{"path": "a.png", "sha256": "x"}]}), encoding="utf-8")
            self.assertEqual(check_all.load_manifest(p), [{"path": "a.png", "sha256": "x"}])

    def test_visual_acceptance_never_claims_pass(self):
        self.assertIn("未验收", check_all.visual_acceptance([]))
        self.assertIn("3 条", check_all.visual_acceptance(["a", "b", "c"]))


class PackageTests(unittest.TestCase):
    def test_missing_manuscript_lists_required_files(self):
        with tempfile.TemporaryDirectory() as td:
            note = Path(td) / "note"
            note.mkdir()
            with mock.patch.object(package, "check_note", return_value={"passed": True, "scope": "x"}):
                with self.assertRaisesRegex(ValueError, "标题.txt.*正文.txt.*置顶评论.txt.*来源.md"):
                    package.deliver(note, Path(td) / "pages", Path(td) / "out")


if __name__ == "__main__":
    unittest.main()
