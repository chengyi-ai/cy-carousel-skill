"""手工排的 3 页（P5、P10、P11），照对标账号「帝国皇子」那篇的手法：
整页压暗的照片当底，正文放在黑色方块里，人物抠图加白色贴纸边，椭圆头像，撕边照片，手绘圈，人名标签。
坐标全部手写；断行和字高借排版器的函数算。输出 内容-手排.json（其余页和 内容.json 一样）。"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'skills/cy-carousel/scripts'))
import build as T
import layouts_v2 as V

W, H = 1440, 1920
c = json.loads((HERE / '内容.json').read_text())
ACC = c['accent']
T.CFG['accent'] = ACC
if c.get('title_font'):
    T.CFG['fonts'] = {'title-display': {'path': c['title_font'], 'weight': None}}
    from io_paths import set_assets_root
    set_assets_root(HERE)
PROTECT = c['protect']
ROOT, WORK = HERE, HERE / '_build'


def text(role, s, x, y, w, size=None, align='left'):
    size = size or {'body': 54, 'emphasis': 84, 'title': 116}[role]
    e = V.measure(V.tx(role, s, x, y, w, size, ACC, align), T, PROTECT)
    return e


def boxed(s, x, y, w, size=52, pad=22):
    """正文放进黑色方块：方块按实际字宽收紧。返回 [方块, 文字] 和底边 y。"""
    e = text('body', s, x + pad / W, y + pad / H, w - 2 * pad / W, size)
    e.pop('soft_shadow', None)
    b = V.ink_bounds(e, {'accent': ACC, 'background': '#000000'})
    x1 = (b[2] + pad) / W if b else x + w
    rect = {'kind': 'rect', 'box': [round(x, 4), round(y, 4), round(x1 - x, 4), round(e['box'][3] + 2 * pad / H - 8 / H, 4)],
            'fill': '#000000'}
    return [rect, e], rect['box'][1] + rect['box'][3]


def label(s, x, y):
    return {'kind': 'text', 'text': s, 'box': [x, y, len(s) * 34 / W + 0.02, 44 / H], 'size': 32, 'font': 'sans-bold',
            'fill': '#FFFFFF', 'bg': '#000000', 'lineheight': 44, 'spacing': 1, 'tight_punctuation': 'all', 'text_role': 'label'}


def photo(path, box, crop=None, focus=(0.5, 0.4), faces=(), effects=(), outline=None, sid=None, glow=False):
    e = {'kind': 'image', 'path': path, 'box': [round(v, 4) for v in box], 'fit': 'cover', 'focus': list(focus),
         'effects': list(effects), 'source_id': sid or Path(path).stem, 'face_boxes': [list(f) for f in faces],
         'face_detection_method': 'manual-verified', 'face_verified': bool(faces), 'face_review': '人工目检',
         'soft_shadow': {'color': ACC if glow else '#000000', 'offset': [0, 0] if glow else [10, 12], 'blur': 20 if glow else 16,
                         'opacity': 0.9 if glow else 0.6}}
    if crop:
        e['crop'] = list(crop)
    if outline:
        e['outline'] = outline; e['outline_width'] = 16
    return e


def bg(path, darken, focus=(0.5, 0.4), crop=None, faces=()):
    e = {'kind': 'dark_backdrop', 'path': path, 'box': [0, 0, 1, 1], 'fit': 'cover', 'darken': darken, 'role': 'background',
         'fade_fraction': 0, 'cover_only': True, 'focus': list(focus), 'source_id': Path(path).stem,
         'face_boxes': [list(f) for f in faces], 'face_detection_method': 'manual-verified'}
    if crop:
        e['crop'] = list(crop)
    return e


def cutout(spec, side, height, max_w, bottom=1.0, edge=None):
    e, _ = V.place_cutout(spec, ROOT, WORK, side, height, max_w, bottom=bottom, edge=edge)
    for k in [k for k in e if k.startswith('_')]:
        e.pop(k)
    e['outline'] = '#FFFFFF'; e['outline_width'] = 15
    return e


def mid(e):
    return e['box'][1] + e['box'][3]


# ---------------------------------------------------------------- P5 摄影师是自己人
els = [bg('assets/paiyunmen-derling.jpg', 0.62, focus=(0.55, 0.5))]
t = text('title', '摄影师是自己人', 0.056, 0.035, 0.888, 112)
blk1, y = boxed('拍照的裕勋龄，父亲裕庚是驻法国公使。1899年到1902年，他在巴黎使馆当二等秘书，就是在那里学会了[[摄影]]。',
                0.056, 0.135, 0.50)
oval = photo('assets/xunling-1902.jpg', [0.60, 0.125, 0.34, 0.34 * W * 1.25 / H], crop=(0.15, 0.0, 0.9, 0.4),
             focus=(0.5, 0.3), faces=[(0.41, 0.085, 0.243, 0.099)], effects=['circle'], outline='#FFFFFF', sid='commons-xunling-1902')
ball = photo('assets/yu-fancy-ball-1901.jpg', [0.035, y + 0.035, 0.50, 0.50 * W * 800 / 844 / H], focus=(0.5, 0.5),
             faces=[(0.23, 0.129, 0.08, 0.084), (0.33, 0.353, 0.063, 0.066), (0.519, 0.188, 0.059, 0.062)],
             effects=['torn'], sid='commons-yu-fancy-dress-ball-1901')
blk2, y2 = boxed('他的妹妹德龄回国后，进宫做了女官。慈禧接见外国客人时，德龄在一旁翻译。', 0.56, mid(oval) + 0.03, 0.40)
print('P5 blk2 bottom', round(y2, 3))
cx = cutout({'path': 'assets/portrait-h1d1-fig.jpg', 'cut': 'assets/cut/portrait-h1d1-cut.png', 'id': 'si-fsa-a13-portrait-h1d1',
             'face': [[0.428, 0.119, 0.175, 0.087]]}, 'right', min(0.40, 1 - y2 - 0.015), 0.30, bottom=1.0)
emp = text('emphasis', '这一家人，\n既懂宫里，也懂洋人。', 0.056, mid(ball) + 0.03, 0.56, 76)
els += [ball, oval, cx] + blk1 + blk2 + [t, emp,
        label('裕勋龄，1902年', 0.62, mid(oval) - 0.03),
        label('1901年，巴黎使馆的化装舞会', 0.05, mid(ball) - 0.035),
        label('慈禧', cx['box'][0] + 0.02, 0.86)]
P5 = {'layout': '手排', 'elements': els}

# ---------------------------------------------------------------- P10 不能有阴影
els = [bg('assets/envoys-wives.png', 0.55, focus=(0.42, 0.4),
          faces=[(0.629, 0.286, 0.044, 0.059), (0.447, 0.347, 0.044, 0.058), (0.283, 0.518, 0.044, 0.058), (0.277, 0.271, 0.045, 0.06)])]
blk1, y = boxed('1903年，美国公使夫人康格请画家凯瑟琳·卡尔进宫，给慈禧画像，送去1904年的圣路易斯博览会。卡尔在宫里住了9个月，画了4幅。',
                0.056, 0.035, 0.86)
robe = photo('assets/court-robe-portrait.jpg', [0.60, 0.42, 0.36, 0.36 * W / 0.84 / H], crop=(0.0, 0.0, 1.0, 0.62),
             focus=(0.5, 0.2), faces=[(0.43, 0.161, 0.14, 0.073)], effects=['torn'], sid='commons-xiaoqinxian-court-robe-portrait')
blk2, y2 = boxed('她后来写：宫里的规矩是不能有阴影，几乎不要透视，一切都画在全光底下。宫里的老画像就是这样：脸上平平的，没有一点阴影。',
                 0.056, 0.42, 0.50)
emp = text('emphasis', '画家想画她本人，\n宫里要的是太后。', 0.50, mid(robe) + 0.03, 0.444, 70, align='right')
t = text('title', '不能有阴影', 0.056, 0.85, 0.62, 132)
els += [robe] + blk1 + blk2 + [emp, t, label('宫廷画师画的朝服像', 0.62, mid(robe) - 0.035),
                               {'kind': 'hand_circle', 'target_text': '不能有阴影，', 'fill': ACC, 'width': 6, 'padding': 10}]
P10 = {'layout': '手排', 'elements': els}

# ---------------------------------------------------------------- P11 镜头后面的她
els = [bg('assets/portrait-h2d3.jpg', 0.66, focus=(0.3, 0.5), faces=[(0.41, 0.396, 0.062, 0.046)])]
fig = cutout({'path': 'assets/portrait-h2d3-fig.jpg', 'cut': 'assets/cut/portrait-h2d3-cut.png', 'id': 'si-fsa-a13-portrait-h2d3',
              'face': [[0.370, 0.192, 0.135, 0.092]]}, 'right', 0.80, 0.46, bottom=1.0)
t = text('title', '镜头后面的她', 0.056, 0.03, 0.6, 100)
blk1, y = boxed('也有不那么正式的照片：她手里拿着一面小镜子，鬓边插着花。照镜子、跷腿，在当时都算不上体面的姿势。',
                0.056, 0.12, 0.50, 50)
snow = photo('assets/snow.jpg', [0.035, y + 0.02, 0.36, 0.36 * W * 766 / 1060 / H], focus=(0.4, 0.3),
             faces=[(0.37, 0.12, 0.065, 0.091), (0.519, 0.086, 0.06, 0.083), (0.704, 0.228, 0.049, 0.068),
                    (0.858, 0.222, 0.045, 0.062), (0.317, 0.11, 0.052, 0.072)], effects=['torn'], sid='commons-cixi-snow-1903')
blk2, y2 = boxed('有研究者认为，快70岁的她并不在乎：对外，她是太后；在这几张里，她也是一个女人。', 0.056, mid(snow) + 0.02, 0.50, 50)
emp = text('emphasis', '这几张，\n也许是拍给自己的。', 0.056, y2 + 0.02, 0.42, 66)
els += [snow, fig] + blk1 + blk2 + [t, emp, label('雪地里', 0.05, mid(snow) - 0.035), label('手里拿着镜子', 0.66, 0.56),
                                     {'kind': 'hand_circle', 'target_text': '照镜子、跷腿', 'fill': ACC, 'width': 6, 'padding': 10}]
P11 = {'layout': '手排', 'elements': els}

for name, pg in (('P5', P5), ('P10', P10), ('P11', P11)):
    low = max(e['box'][1] + e['box'][3] for e in pg['elements'] if e['kind'] == 'text' and e.get('text_role') != 'label')
    print(name, '文字最低到', round(low, 3))
    assert low < 0.955, f'{name} 文字出了下边'
out = json.loads(json.dumps(c))
out['pages'][4], out['pages'][9], out['pages'][10] = P5, P10, P11
(HERE / '内容-手排.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
print('ok')
