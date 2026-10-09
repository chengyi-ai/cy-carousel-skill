import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_all  # noqa: E402
import package  # noqa: E402


def make_note(td):
    from PIL import Image

    td = Path(td)
    note, pages = td / "note", td / "pages"
    note.mkdir()
    pages.mkdir()
    (note / "页面脚本.json").write_text(json.dumps({"topic": "测试", "pages": [{}]}), encoding="utf-8")
    for name in ("标题.txt", "正文.txt", "置顶评论.txt", "来源.md"):
        (note / name).write_text("内容", encoding="utf-8")
    Image.new("RGB", (1440, 1920), "white").save(pages / "p01.png")
    return note, pages, td / "out"


def fake_result(blockers):
    return dict(passed=True, errors=[], scope="t", visual_acceptance="未验收", advisories=[],
                strict_visual=bool(blockers), visual_blockers=blockers)


class StrictVisualTests(unittest.TestCase):
    def test_only_whitespace_and_same_skeleton_block(self):
        self.assertTrue(check_all.visual_blocking("whitespace", "暗篇空格子均值30.0%>20%"))
        self.assertTrue(check_all.visual_blocking("alternation", "P03与前页骨架相同"))
        self.assertFalse(check_all.visual_blocking("alternation", "全篇强调色均值3.000%不在1.2–2.0%"))
        for name in ("richness", "color_area", "variation"):
            self.assertFalse(check_all.visual_blocking(name, "与前页骨架相同"))

    def test_blockers_refuse_without_reason(self):
        with tempfile.TemporaryDirectory() as td:
            note, pages, out = make_note(td)
            with mock.patch.object(package, "check_note", return_value=fake_result(["留白"])):
                with self.assertRaisesRegex(ValueError, "accept-visual"):
                    package.deliver(note, pages, out, strict_visual=True)
                with self.assertRaisesRegex(ValueError, "理由"):
                    package.deliver(note, pages, out, strict_visual=True, accept_visual="  ")
            self.assertFalse(out.exists())

    def test_accept_reason_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            note, pages, out = make_note(td)
            with mock.patch.object(package, "check_note", return_value=fake_result(["留白"])):
                package.deliver(note, pages, out, strict_visual=True, accept_visual="目检后确认")
            saved = json.loads((out / "交付清单.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["visual_accepted"], {"reason": "目检后确认", "blockers": ["留白"]})

    def test_default_off_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            note, pages, out = make_note(td)
            res = dict(passed=True, errors=[], scope="t", advisories=["留白"])
            with mock.patch.object(package, "check_note", return_value=res):
                m = package.deliver(note, pages, out)
            self.assertIsNone(m["visual_accepted"])


if __name__ == "__main__":
    unittest.main()
