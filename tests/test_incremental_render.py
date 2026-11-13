"""增量渲染（render.py --changed-only）：只重渲变了的页，结果与全量渲染一致。"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import render  # noqa: E402
import 手排 as S  # noqa: E402


class IncrementalRenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.note = Path(self.tmp.name)
        Image.new('RGB', (1440, 1920), '#305880').save(self.note / 'a.png')
        Image.new('RGB', (1440, 1920), '#803058').save(self.note / 'b.png')
        self.data = {'mode': 'sample', 'tone': '暗', 'config': {}, 'pages': [
            S.page(None, [S.headline('增量渲染', .05, .10, 110)], layout='cover'),
            S.page(None, [S.body('第二页用素材 a。', .05, .20, .90, 56)], backdrop=S.backdrop('a.png', .5)),
            S.page(None, [S.body('第三页用素材 b。', .05, .20, .90, 56)], backdrop=S.backdrop('b.png', .5)),
        ]}
        self.write()
        self.render()

    def write(self):
        (self.note / '页面脚本.json').write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')

    def render(self, changed_only=False):
        reports = render.render(self.note / '页面脚本.json', self.note / 'pages',
                                assets_root=self.note, changed_only=changed_only)
        return [r['page'] for r in reports if not r['reused']]

    def test_unchanged_pages_are_reused(self):
        self.assertEqual(self.render(changed_only=True), [])
        saved = json.loads((self.note / 'pages/render-report.json').read_text(encoding='utf-8'))
        self.assertEqual(len(saved), 3)
        self.assertTrue(all(r['reused'] for r in saved))

    def test_default_render_is_full(self):
        self.assertEqual(self.render(), [1, 2, 3])

    def test_only_edited_page_is_rendered(self):
        self.data['pages'][1]['elements'][-1]['text'] = '第二页改了一句。'
        self.write()
        self.assertEqual(self.render(changed_only=True), [2])
        full = self.note / 'full'
        render.render(self.note / '页面脚本.json', full, assets_root=self.note)
        for n in (1, 2, 3):
            self.assertEqual((self.note / f'pages/p{n:02}.png').read_bytes(), (full / f'p{n:02}.png').read_bytes())

    def test_config_change_renders_every_page(self):
        self.data['config']['account_name'] = '新账号'
        self.write()
        self.assertEqual(self.render(changed_only=True), [1, 2, 3])

    def test_replaced_asset_renders_pages_using_it(self):
        path = self.note / 'b.png'
        Image.new('RGB', (1440, 1920), '#308058').save(path)
        stat = path.stat()
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000))
        self.assertEqual(self.render(changed_only=True), [3])

    def test_replaced_config_font_renders_every_page(self):
        font = self.note / 'title.ttf'
        font.write_bytes((ROOT / 'assets/fonts/MaShanZheng-Regular.ttf').read_bytes())
        self.data['config']['fonts'] = {'licensed_headline': {'path': str(font)}}
        self.write()
        self.assertEqual(self.render(changed_only=True), [1, 2, 3])
        self.assertEqual(self.render(changed_only=True), [])
        stat = font.stat()
        os.utime(font, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000))
        self.assertEqual(self.render(changed_only=True), [1, 2, 3])

    def test_replaced_page_font_renders_that_page(self):
        # 不传素材根目录时，字库按当前目录解析、素材按脚本目录解析；字库放在另一个目录里，
        # 才能测出页面级 config.fonts 有没有进指纹（只扫页面里的 path 会找错目录）
        fonts = self.note / 'fonts'
        fonts.mkdir()
        font = fonts / 'page.ttf'
        font.write_bytes((ROOT / 'assets/fonts/MaShanZheng-Regular.ttf').read_bytes())
        cwd = os.getcwd()
        os.chdir(fonts)
        self.addCleanup(os.chdir, cwd)
        self.data['pages'][0]['config'] = {'fonts': {'licensed_headline': {'path': 'page.ttf'}}}
        self.write()

        def changed():
            reports = render.render(self.note / '页面脚本.json', self.note / 'pages', changed_only=True)
            return [r['page'] for r in reports if not r['reused']]

        self.assertEqual(changed(), [1])
        self.assertEqual(changed(), [])
        stat = font.stat()
        os.utime(font, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000))
        self.assertEqual(changed(), [1])

    def test_tampered_output_is_rendered_again(self):
        Image.new('RGB', (1440, 1920)).save(self.note / 'pages/p02.png')
        self.assertEqual(self.render(changed_only=True), [2])

    def test_missing_report_falls_back_to_full_render(self):
        (self.note / 'pages/render-report.json').unlink()
        self.assertEqual(self.render(changed_only=True), [1, 2, 3])

    def test_removed_page_drops_stale_output(self):
        del self.data['pages'][2]
        self.write()
        self.assertEqual(self.render(changed_only=True), [])
        self.assertFalse((self.note / 'pages/p03.png').exists())


if __name__ == '__main__':
    unittest.main()
