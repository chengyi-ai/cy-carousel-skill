"""AI 分支第 3 篇 v2：照 ELIZA 那篇的做法手工排。
- 毛笔大标题（米白＋电子青），3D 挤出；大号青色数字；青色问句贴条；
- 论文原文裁 1–4 行放大成白色纸卡（PDF 矢量渲染，清晰），关键词用红色手绘圈；
- 暗底 #080808（红线检查按 ≤8 算纯黑），拼贴图透明底，每页图文密，正文大号宋体。
输出：页面脚本.json、collage/Pxx.png；再用 render.py 渲染到 pages/。"""
import json, math, random, sys
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
NOTE = HERE.parent
SK = NOTE.parents[2] / 'skills/lishi-tuwen/scripts'
sys.path.insert(0, str(SK))
import build as T

W, H = 1440, 1920
BG = (12, 12, 12)
CREAM, CYAN, INK, RED = '#F3F1E9', '#00E5FF', '#10242B', (229, 57, 53)
T.CFG['accent'] = CYAN
OUT = HERE / 'collage'; OUT.mkdir(parents=True, exist_ok=True)
PROTECT = ['Muse Spark', 'meta.ai', 'Nilradical', 'M. Kida', 'GAP', 'Meta', 'Human', 'Dinh']


# ---------------------------------------------------------------- 论文裁片

def pdf_crop(k, pno, rect, zoom=6):
    """rect 是页面 0–1 坐标。返回 RGB 图和一个把页面坐标换成裁片像素的函数。"""
    d = pymupdf.open(NOTE / f'research/{k}.pdf'); p = d[pno]
    pw, ph = p.rect.width, p.rect.height
    clip = pymupdf.Rect(rect[0] * pw, rect[1] * ph, rect[2] * pw, rect[3] * ph)
    pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    def to_px(b):
        return [(b[0] - rect[0]) * pw * zoom, (b[1] - rect[1]) * ph * zoom, (b[2] - rect[0]) * pw * zoom, (b[3] - rect[1]) * ph * zoom]
    return im, to_px


def snap(k, pno, rect):
    """左右边挪到最近的词间空白，不切半个词。"""
    p = pymupdf.open(NOTE / f'research/{k}.pdf')[pno]
    pw, ph = p.rect.width, p.rect.height
    ws = [(w[0] / pw, w[2] / pw) for w in p.get_text('words') if rect[1] < (w[1] + w[3]) / 2 / ph < rect[3]]
    def ok(x):
        return not any(a < x < b for a, b in ws)
    def near(x):                                        # 前后 0.05 内找最近的空白；找不到就不动
        c = [x + d / 1000 for d in range(-50, 51) if ok(x + d / 1000)]
        return min(c, key=lambda v: abs(v - x)) if c else x
    return [near(rect[0]), rect[1], near(rect[2]), rect[3]]


def strip(k, pno, rect, target_w, circles=(), cyan=(), rotate=0.0, pad=18):
    """论文里一两行原文，按目标宽度直接矢量渲染（不放大位图），关键词画红圈，做成白色纸条。"""
    rect = snap(k, pno, rect)
    d = pymupdf.open(NOTE / f'research/{k}.pdf'); pg = d[pno]
    zoom = (target_w - 2 * pad) / ((rect[2] - rect[0]) * pg.rect.width)
    im, f = pdf_crop(k, pno, rect, zoom=zoom)
    dr = ImageDraw.Draw(im)                             # 边上被切开的半个词涂白（两行对齐排版时找不到共同空白）
    for w in pg.get_text('words'):
        b = [w[0] / pg.rect.width, w[1] / pg.rect.height, w[2] / pg.rect.width, w[3] / pg.rect.height]
        if not rect[1] < (b[1] + b[3]) / 2 < rect[3]:
            continue
        x0, y0, x1, y1 = f(b)
        if b[0] < rect[2] < b[2]:
            dr.rectangle([x0 - 4, y0 - 2, im.width, y1 + 2], fill='white')
        if b[0] < rect[0] < b[2]:
            dr.rectangle([0, y0 - 2, x1 + 4, y1 + 2], fill='white')
    for c in circles:
        hand_circle(im, f(find(k, pno, c) if isinstance(c, str) else c))
    for c in cyan:
        hand_circle(im, f(find(k, pno, c) if isinstance(c, str) else c), color=(0, 229, 255))
    im = ImageOps.expand(im, border=pad, fill='white')
    return card(im, im.width, rotate=rotate)


def find(k, pno, phrase, nth=0):
    d = pymupdf.open(NOTE / f'research/{k}.pdf'); p = d[pno]
    r = p.search_for(phrase)[nth]
    return [r.x0 / p.rect.width, r.y0 / p.rect.height, r.x1 / p.rect.width, r.y1 / p.rect.height]


def hand_circle(im, box, color=RED, width=None, pad=0.18):
    """在图上画一个手绘感的红圈（两笔，略有偏移）。box 为像素坐标。"""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    px, py = w * 0.06 + 14, h * 0.32 + 6
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, w / 2 + px, h / 2 + py
    width = width or max(5, round(h * 0.11))
    rng = random.Random(int(x0 + y0))
    for k in range(2):
        pts = []
        start = rng.uniform(-0.4, 0.2)
        for j in range(0, 150):
            t = start + j / 140 * (2 * math.pi + 0.35)
            jr = 1 + 0.025 * math.sin(3 * t + k) + k * 0.02
            pts.append((cx + rx * jr * math.cos(t), cy + ry * jr * math.sin(t)))
        d.line(pts, fill=color, width=width, joint='curve')


def card(im, target_w, rotate=0.0, border=0, shadow=True):
    """论文裁片做成白色纸卡：等比缩放到 target_w，可轻微倾斜，带柔影。"""
    s = target_w / im.width
    if s > 1.25:
        raise ValueError(f'裁片放大 {s:.2f} 倍，超过 1.25：请提高 zoom')
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    if border:
        im = ImageOps.expand(im, border=border, fill='white')
    im = im.convert('RGBA')
    if rotate:
        im = im.rotate(rotate, resample=Image.BICUBIC, expand=True)
    if not shadow:
        return im
    pad = 40
    sh = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad))
    a = Image.new('L', sh.size); a.paste(im.getchannel('A'), (pad + 10, pad + 14))
    a = a.filter(ImageFilter.GaussianBlur(16)).point(lambda v: v * 0.6)
    blk = Image.new('RGBA', sh.size, (0, 0, 0, 255)); blk.putalpha(a)
    sh.alpha_composite(blk); sh.alpha_composite(im, (pad, pad))
    return sh


def figure(path, target_w, rotate=0.0, circle=False, ring=None):
    im = Image.open(NOTE / path).convert('RGB')
    s = min(1.25, target_w / im.width)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS).convert('RGBA')
    if circle:
        side = min(im.size); im = ImageOps.fit(im, (side, side))
        m = Image.new('L', im.size); ImageDraw.Draw(m).ellipse((0, 0, side - 1, side - 1), fill=255); im.putalpha(m)
        if ring:
            ImageDraw.Draw(im).ellipse((4, 4, side - 5, side - 5), outline=ring, width=10)
    if rotate:
        im = im.rotate(rotate, resample=Image.BICUBIC, expand=True)
    return im


class Canvas:
    def __init__(self, bg=None, darken=0.0):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))      # 透明底：页面底色由 render 铺 #0C0C0C
        if bg is not None:
            b = ImageOps.fit(bg.convert('RGB'), (W, H))
            b = Image.eval(b, lambda v: int(v * (1 - darken)))
            self.im.paste(b.convert('RGBA'))

    def put(self, img, x, y, fit=True):
        x = round(x); y = round(y)
        if fit:                                         # 不出页面右边（左边可以出血）
            x = min(x, W - img.width + 30)
        self.im.alpha_composite(img, (x, y))
        return [x / W, y / H, img.width / W, img.height / H]

    def save(self, name):
        p = OUT / f'{name}.png'; self.im.save(p); return f'v2/collage/{name}.png'


# ---------------------------------------------------------------- 文字元素

def headline(text, x, y, size, w=0.92):
    e = {'kind': 'text', 'text': text, 'box': [x, y, w, 0.3], 'size': size, 'font': 'headline', 'fill': CREAM,
         'accent': CYAN, 'spacing': 0, 'lineheight': round(size * 1.26), 'text_role': 'headline',
         'effect': '3d', 'depth': 7, 'bold': 1, 'shadow_color': '#0C0C0C', 'tight_punctuation': 'all'}
    e['box'][3] = round((text.count('\n') + 1) * e['lineheight'] / H + 12 / H, 4)
    return e


def big(text, x, y, size, fill=CYAN, w=0.92, align='left'):
    e = {'kind': 'text', 'text': text, 'box': [x, y, w, 0.3], 'size': size, 'font': 'sans-black', 'fill': fill,
         'spacing': 0, 'lineheight': round(size * 1.22), 'text_role': 'emphasis', 'align': align,
         'effect': '3d', 'depth': 7, 'bold': 1, 'shadow_color': '#0C0C0C'}
    e['box'][3] = round((text.count('\n') + 1) * e['lineheight'] / H + 12 / H, 4)
    return e


def body(text, x, y, w, size=60, fill=CREAM, bg=None):
    e = {'kind': 'text', 'text': text, 'box': [x, y, w, 0.5], 'size': size, 'font': 'serif-bold', 'fill': fill,
         'accent': CYAN, 'stroke': 1, 'spacing': 0, 'lineheight': round(size * 1.3), 'text_role': 'body',
         'tight_punctuation': 'all'}
    if bg:
        e['bg'] = bg
    e['box'][2] = w * 0.97
    e['text'] = T.wrap(e, text, PROTECT)
    e['box'][2] = w
    e['box'][3] = round((e['text'].count('\n') + 1) * e['lineheight'] / H + 10 / H, 4)
    return e


def sticker(text, x, y, size=60):
    """青色问句贴条（底色文字），黑字。"""
    return {'kind': 'text', 'text': text, 'box': [x, y, 0.9, round(size * 1.3 / H + 10 / H, 4)], 'size': size,
            'font': 'sans-black', 'fill': INK, 'bg': CYAN, 'spacing': 0, 'lineheight': round(size * 1.3),
            'text_role': 'note', 'tight_punctuation': 'all'}


def bottom(e):
    return e['box'][1] + e['box'][3]


def page(collage, els, layout='collage'):
    return {'layout': layout, 'background': '#080808', 'watermark': layout != 'cover',
            'elements': [{'kind': 'image', 'path': collage, 'box': [0, 0, 1, 1], 'fit': 'cover', 'role': 'background',
                          'source_id': Path(collage).stem, 'face_boxes': [], 'face_detection_method': 'manual-verified'}] + els}


pages = []

# ---------------------------------------------------------------- 封面
HUMAN_LBL = [0.093, 0.374, 0.108, 0.402]
AI_LBL = [0.088, 0.085, 0.112, 0.105]
AI_LBL_E = [0.089, 0.558, 0.111, 0.576]
AI_STRIP = ('evolution', 1, [0.085, 0.553, 0.53, 0.583])
cv = Canvas()
fig = figure('assets/semiabelian-galois-group-v2.png', 560, circle=True, ring=CYAN)
cv.put(fig, 900, 40)
s1 = cv.put(strip('semiabelian', 1, [0.085, 0.372, 0.62, 0.413], 1250, cyan=[HUMAN_LBL], rotate=-2), 30, 330)
s2 = cv.put(strip(*AI_STRIP, 1150, cyan=[AI_LBL_E], rotate=2), 250, (s1[1] + s1[3]) * H - 20)
s3 = cv.put(strip('semiabelian', 1, [0.112, 0.444, 0.52, 0.463], 1300, circles=['(Human)', '(AI)'], rotate=-1), 60, (s2[1] + s2[3]) * H - 10)
c0 = cv.save('P00')
cover = page(c0, [
    {**headline('AI 帮数学家写论文：', 0.06, 0.755, 112), 'font': 'cover-title'},
    {**headline('[[每段都标了谁写的]]', 0.06, 0.845, 146), 'font': 'cover-title'},
], layout='cover')
cover['border'] = CYAN; cover['border_width'] = 10
pages.append(cover)

# ---------------------------------------------------------------- P1 6 篇论文
cv = Canvas()
papers = ['gaussian', 'biharmonic', 'semiabelian', 'cycle', 'string', 'evolution']
tops = {'gaussian': 0.135, 'biharmonic': 0.13, 'semiabelian': 0.135, 'cycle': 0.13, 'string': 0.13, 'evolution': 0.13}
bots = {'gaussian': 0.215, 'biharmonic': 0.252, 'semiabelian': 0.215, 'cycle': 0.227, 'string': 0.253, 'evolution': 0.227}
y = 540
for n, k in enumerate(papers):
    c = strip(k, 0, [0.12, tops[k], 0.88, bots[k]], 880, circles=['with Muse Spark via meta.ai'], rotate=[-3, 2, -1.5, 2.5, -2, 1][n], pad=10)
    cv.put(c, 540 + (n % 2) * 30, y)
    y += c.height * 0.64
c1 = cv.save('P01')
h = headline('Meta 说，它的 AI\n[[解开了数学难题]]', 0.035, 0.022, 118)
bg_ = big('6 篇论文', 0.035, bottom(h) + 0.005, 176)
els = [h, bg_,
       body('10月2日，Meta 发了6篇数学论文，说其中5篇回答了数学界悬而未决的问题。', 0.035, bottom(bg_) + 0.03, 0.34, 58),
       body('合作者是它的 AI：Muse Spark。', 0.035, bottom(bg_) + 0.32, 0.34, 58),
       sticker('数学家要失业了？', 0.035, 0.85, 64)]
pages.append(page(c1, els))

# ---------------------------------------------------------------- P2 署名那一行
cv = Canvas()
h = headline('先别急，\n[[翻到署名那一行]]', 0.035, 0.022, 124)
sA = cv.put(strip('semiabelian', 0, [0.2, 0.14, 0.8, 0.192], 1000, rotate=1.5), 380, bottom(h) * H + 10)
sB = cv.put(strip('semiabelian', 0, [0.395, 0.196, 0.605, 0.214], 1360, circles=['with Muse Spark via meta.ai'], rotate=-2), 30, (sA[1] + sA[3]) * H - 20)
t1 = body('作者名字下面，还有一行字。', 0.035, bottom(h) + 0.03, 0.25, 58)
t2 = body('AI 没进作者名单，写在「和谁一起」的位置。用的也不是专门搭的研究系统，就是普通的 meta.ai 聊天框。',
          0.035, sB[1] + sB[3] + 0.03, 0.93, 64)
sC = cv.put(strip('semiabelian', 1, [0.112, 0.393, 0.36, 0.411], 1000, circles=['meta.ai chat interface'], rotate=1.5), 330, bottom(t2) * H + 30)
c2 = cv.save('P02')
els = [h, t1, t2, big('不是实验室，\n是聊天框', 0.035, sC[1] + sC[3] + 0.02, 132)]
pages.append(page(c2, els))

# ---------------------------------------------------------------- P3 页边的线
cv = Canvas()
h = headline('再往下翻，\n[[每段旁边都有一条线]]', 0.035, 0.022, 118)
sL = cv.put(strip('semiabelian', 1, [0.112, 0.444, 0.52, 0.463], 1360, circles=['(Human)', '(AI)'], rotate=-1), 30, bottom(h) * H + 10)
sH = cv.put(strip('semiabelian', 1, [0.085, 0.372, 0.5, 0.413], 820, circles=[HUMAN_LBL], rotate=2), 600, (sL[1] + sL[3]) * H + 50)
sAi = cv.put(strip(*AI_STRIP, 820, circles=[AI_LBL_E], rotate=-2), 600, (sH[1] + sH[3]) * H + 50)
c3 = cv.save('P03')
els = [h, big('谁写的，\n页边都标着', 0.035, sAi[1] + sAi[3] + 0.04, 150),
       body('页边标记，分开标出人起草的部分和 AI 协助的部分。', 0.035, sL[1] + sL[3] + 0.005, 0.93, 54),
       big('绿线 Human', 0.035, sH[1] + 0.025, 92, fill='#5BD27A', w=0.42),
       body('人起草的', 0.035, sH[1] + 0.09, 0.38, 70),
       big('蓝线 AI', 0.035, sAi[1] + 0.025, 92, w=0.42),
       body('AI 协助写的', 0.035, sAi[1] + 0.09, 0.38, 70)]
pages.append(page(c3, els))

# ---------------------------------------------------------------- P4 69 vs 8
cv = Canvas()
im, f = pdf_crop('gaussian', 33, [0.06, 0.03, 0.94, 0.62], zoom=4)
for bb in ([0.088, 0.085, 0.112, 0.105], [0.088, 0.35, 0.112, 0.37]):
    hand_circle(im, f(bb), width=9)
cv.put(card(im, 960, rotate=-2), 520, 700)
c4 = cv.save('P04')
h = headline('最长的一篇，\n[[页边标了多少 AI]]', 0.035, 0.022, 118)
els = [h,
       big('69 处 AI', 0.035, bottom(h) + 0.01, 196),
       big('8 处 Human', 0.035, bottom(h) + 0.12, 120, fill=CREAM),
       body('讲高斯椭球拟合的那篇，63页。', 0.035, 0.44, 0.3, 60),
       body('数的是页边标记的段落，不是字数。', 0.035, 0.62, 0.3, 60),
       sticker('AI 写得比人多？', 0.035, 0.86, 64)]
pages.append(page(c4, els))

# ---------------------------------------------------------------- P5 使用声明
cv = Canvas()
h = headline('可每一篇，\n[[都有一段使用声明]]', 0.035, 0.022, 118)
s0 = cv.put(strip('semiabelian', 1, [0.385, 0.334, 0.615, 0.354], 760, rotate=2), 640, bottom(h) * H + 20)
s1_ = cv.put(strip('semiabelian', 1, [0.47, 0.411, 0.885, 0.429], 1360, circles=['checked and corrected the mathematics'], rotate=-1.5), 30, (s0[1] + s0[3]) * H + 20)
s2_ = cv.put(strip('semiabelian', 1, [0.112, 0.428, 0.4, 0.446], 1100, circles=['ownership for the final manuscript'], rotate=1.5), 300, (s1_[1] + s1_[3]) * H + 10)
c5 = cv.save('P05')
t1 = body('AI 帮着探索思路、推演论证、起草文字。', 0.035, s2_[1] + s2_[3] + 0.03, 0.93, 64)
t2 = body('研究者主导，[[检查并改正其中的数学]]，对最终稿件负责。', 0.035, bottom(t1) + 0.02, 0.93, 64)
els = [h, t1, t2, big('AI 出了力，\n账是人担的', 0.035, bottom(t2) + 0.025, 140)]
pages.append(page(c5, els))

# ---------------------------------------------------------------- P6 题是人挑的
cv = Canvas()
h = headline('这道题，\n[[也是人挑的]]', 0.035, 0.022, 130)
cP = cv.put(strip('biharmonic', 0, [0.1, 0.13, 0.9, 0.252], 940, circles=['Leonard Dinh'], rotate=2, pad=10), 460, 300)
tb = body('偏微分方程那篇，题目和关键的证明思路，都是数学家 Dinh 定的。', 0.035, 0.19, 0.29, 56)
fig = figure('assets/biharmonic-nls-blow-up-v3.png', 1360)
cF = cv.put(fig, 40, max((cP[1] + cP[3]), bottom(tb)) * H + 40)
c6 = cv.save('P06')
t2 = body('Muse Spark 帮着算、试论证、改证明。', 0.035, cF[1] + cF[3] + 0.025, 0.93, 64)
els = [h, tb, t2, big('AI 帮着算，\n人来定方向', 0.035, bottom(t2) + 0.03, 124)]
pages.append(page(c6, els))

# ---------------------------------------------------------------- P7 384
cv = Canvas()
fig = figure('assets/semiabelian-galois-group-v2.png', 520, circle=True, ring=CYAN)
cv.put(fig, 880, 290)
h = headline('AI 最漂亮的一招：\n[[找反例]]', 0.035, 0.022, 118)
tb = body('2024年有人猜：一类群一定都有某个性质。数学家让 AI 写了一段搜索程序，查遍元素不超过900个的群，翻出一个384个元素的例外。',
          0.035, 0.355, 0.56, 56)
q1 = cv.put(strip('semiabelian', 5, [0.33, 0.297, 0.885, 0.314], 1360, circles=['we prompted Muse Spark'], rotate=-1.5), 30, bottom(tb) * H + 20)
q2 = cv.put(strip('semiabelian', 5, [0.44, 0.314, 0.885, 0.331], 1250, circles=['up to order 900'], rotate=1.5), 160, (q1[1] + q1[3]) * H)
q3 = cv.put(strip('semiabelian', 5, [0.22, 0.398, 0.79, 0.419], 1300, circles=['SmallGroup(384, 20127)'], rotate=-1), 60, (q2[1] + q2[3]) * H + 10)
c7 = cv.save('P07')
st = sticker('一个例外，就够推翻猜想', 0.035, q3[1] + q3[3] + 0.01, 64)
assert bottom(st) < 0.95, bottom(st)
els = [h, big('384', 0.035, bottom(h) - 0.01, 240), tb, st]
pages.append(page(c7, els))

# ---------------------------------------------------------------- P8 另一个 AI
cv = Canvas()
h = headline('另一个 AI，\n[[也找到了反例]]', 0.035, 0.022, 118)
n1 = cv.put(strip('semiabelian', 1, [0.39, 0.484, 0.61, 0.502], 700, rotate=2), 680, bottom(h) * H + 20)
stk = sticker('撞题了？', 0.035, n1[1] + 0.03, 72)
n2 = cv.put(strip('semiabelian', 1, [0.27, 0.537, 0.72, 0.556], 1360, circles=['September 16, 2026', 'Nilradical'], rotate=-1.5), 30, (n1[1] + n1[3]) * H + 10)
c8 = cv.save('P08')
t1 = body('论文自己写明：快完成时，作者才知道，9月16日，另一个 AI 智能体 Nilradical 也交了一个反例。', 0.035, n2[1] + n2[3] + 0.03, 0.93, 60)
t2 = body('10月3日，有学者在 X 上说，6道里有3道早被别人解决了。Meta 的博客也承认：有几道题，别的团队用不同方法各自公布过解法。',
          0.035, bottom(t1) + 0.03, 0.93, 60)
els = [h, stk, t1, t2, big('「5 道难题」，\n还在吵', 0.035, bottom(t2) + 0.035, 124)]
pages.append(page(c8, els))

# ---------------------------------------------------------------- P9 三个问题
bgim = Image.open(NOTE / 'assets/gaussian-ellipsoid-threshold-v2.png')
cv = Canvas()                                           # 只取两只椭球（下面那条带字的数轴不要），反相压暗铺上半页
top = ImageOps.invert(bgim.convert('RGB').crop((0, 0, bgim.width, 1450)))
top = top.resize((round(top.width * 0.857), round(top.height * 0.857)), Image.LANCZOS)
top = Image.eval(top, lambda v: int(v * 0.2)).crop(((top.width - W) // 2, 0, (top.width - W) // 2 + W, top.height))
fade = Image.linear_gradient('L').resize((W, top.height)).point(lambda v: 255 if v < 150 else int(255 * (255 - v) / 105))
cv.im.paste(top.convert('RGBA'), (0, 0), fade)
c9 = cv.save('P09')
h = headline('读 AI 参与的论文，\n[[先问三个问题]]', 0.035, 0.022, 118)
els = [h]
for n, (q, y0) in enumerate([('题目是谁挑的？', 0.27), ('哪几段是 AI 写的？', 0.49), ('谁核对的、谁负责？', 0.71)]):
    els.append(big(f'0{n + 1}', 0.035, y0, 230, w=0.22))
    els.append(body(q, 0.26, y0 + 0.045, 0.72, 84, bg='#0C0C0C'))
pages.append(page(c9, els))

# ---------------------------------------------------------------- P10 收尾
cv = Canvas()
h = headline('AI 进了论文：\n[[页边那条线，\n比结论还重要]]~', 0.035, 0.022, 118)
t1 = body('6篇论文、139页。AI 能帮着找反例、写证明，有的论文里，它协助写的段落比人还多。', 0.035, bottom(h) + 0.025, 0.93, 62)
t2 = body('可作者栏里没有它。论文写明：数学由研究者检查、改正，[[最终稿件由研究者负责]]。', 0.035, bottom(t1) + 0.02, 0.93, 62)
e1 = cv.put(strip('semiabelian', 1, [0.085, 0.372, 0.62, 0.413], 1300, cyan=[HUMAN_LBL], rotate=-2), 30, bottom(t2) * H + 20)
e2 = cv.put(strip(*AI_STRIP, 1250, cyan=[AI_LBL_E], rotate=2), 160, (e1[1] + e1[3]) * H + 10)
c10 = cv.save('P10')
st = sticker('你能接受 AI 写几成？', 0.035, e2[1] + e2[3] + 0.015, 76)
assert bottom(st) < 0.95, bottom(st)
els = [h, t1, t2, st]
pages.append(page(c10, els))

script = {'schema_version': 1, 'built_by': 'v2/制作v2.py', 'topic': 'Meta 的 AI 和数学家合写 6 篇论文', 'tone': '暗',
          'mode': 'production',
          'config': {'tone': '暗', 'accent': CYAN, 'background': '#080808', 'account_name': '程意', 'watermark_text': '程意',
                     'watermark_style': 'neutral', 'bookmark': False, 'cover_only': False, 'require_face_every_page': False},
          'delivery': {'main_cover': 'D', 'size': [W, H]}, 'pages': pages}
(NOTE / '页面脚本.json').write_text(json.dumps(script, ensure_ascii=False, indent=1))
print('pages', len(pages))
