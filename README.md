# lishi-tuwen · 历史图文轮播 Skill

给一个历史选题，按一套已经打磨好的版式，做出一篇能直接发小红书的图文笔记：**封面加 8–12 页内页（1440×1920）、标题、正文、话题标签、置顶评论和来源清单**，全程有事实核查、图片授权记录和自动检查。

适合的选题：历史人物、女性处境、服饰与器物背后的故事，比如有毒的绿色颜料、维多利亚时代的服饰规定、王室秘密婚姻。

可以在 **Claude Code** 和 **Codex** 里当 Skill 用，也可以直接用命令行跑脚本。

| 砷绿假花（暗色） | 情人眼（暗色） | 泳衣量腿（浅色） |
|---|---|---|
| ![砷绿假花](examples/01-砷绿假花/全套预览.jpg) | ![情人眼](examples/02-情人眼/全套预览.jpg) | ![泳衣量腿](examples/03-泳衣量腿/全套预览.jpg) |

---

## 它能做什么

1. **选题与查证**：每个年份、人名、数字都回到原始档案、馆藏或同期报刊核对，写进事实表；流传但没有证据的说法标成「传说」，不给当事人编台词。
2. **文案**：给 3 个标题备选，每页正文都给下一页留钩子，再配 18–22 个话题标签、置顶评论和资料来源。
3. **找图与授权**：优先用公有领域和开放授权的图片，记下原链接、许可、文件 SHA256，以及每张图用在哪一页。
4. **排版与渲染**：
   - 色调：暗色和浅色两条路线，一篇只用一种；
   - 字体：毛笔大标题，彩色和白色大字交替；
   - 图片：人物抠图、圆盘肖像，只等比裁切不拉伸，裁切时保住人脸；
   - 背景：在黑底、压暗整图、亮图之间轮换。
5. **自动检查**：一条命令跑完留白、色彩、标点间距、字和脸有没有碰撞、图片比例、背景类型等多项检查，给出 PASS/FAIL。
6. **盲测**：把新页面和参考页面混在一起，随机编号，答案另存，用来检验「像不像」。
7. **打包**：输出和发布一致的成品文件夹（带标题的主封面、无字封面备选、内页、全套预览和全部文稿）。**脚本不会自动发布。**

---

## 安装

### 环境要求

- Python 3.10 及以上；
- Pillow 12.1+、numpy 2+（见 `requirements.txt`）；
- **macOS**：抠图、OCR、人脸检测用的是系统自带的 Vision。其他系统可以手动提供抠图 mask 和人脸框，其余流程照常运行（见下文「限制」）。

### 装到 Claude Code

```bash
git clone https://github.com/chengyi-ai/lishi-tuwen-skill.git ~/.claude/skills/lishi-tuwen
python3 -m pip install -r ~/.claude/skills/lishi-tuwen/requirements.txt
```

### 装到 Codex

```bash
git clone https://github.com/chengyi-ai/lishi-tuwen-skill.git ~/.codex/skills/lishi-tuwen
python3 -m pip install -r ~/.codex/skills/lishi-tuwen/requirements.txt
```

装好以后**新开一个对话**，Skill 才会被识别。

### 更新

```bash
git -C ~/.claude/skills/lishi-tuwen pull
```

Codex 那份把路径换成 `~/.codex/skills/lishi-tuwen` 即可。

---

## 使用

### 方式一：直接跟 AI 说（推荐）

在 Claude Code 或 Codex 里说：

> 用 lishi-tuwen 做一篇历史图文，选题：维多利亚时代的砷绿墙纸，暗色调，主强调色绿色，账号名填「XXX」

不点名 Skill 也行，比如「帮我做一篇关于 XX 的历史图文」，一般会自动触发。可以附带这些要求：

| 参数 | 说明 | 默认 |
|---|---|---|
| 色调 | `暗` 或 `浅`，一篇只用一种 | 暗 |
| 主强调色 | 例如绿色、粉色、深红 | 按选题 |
| 页数 | 封面加 8–12 页内页 | 10 |
| 账号名 | 写进水印和署名 | 不填时图里显示「账号名」占位 |

### 方式二：命令行

以下命令都在 Skill 目录里运行，`工作/新选题` 换成你自己的工作目录。

**1. 新建一篇**（生成页面脚本、事实表和授权表模板）

```bash
python3 scripts/new_note.py --topic '砷绿墙纸' --tone dark --out 工作/新选题
```

只想先试 3 页小样，加上 `--pages 3 --mode sample`。

**2. 渲染**（素材路径相对页面脚本，或者用 `--assets-root` 指定素材根目录）

```bash
python3 scripts/render.py 工作/新选题/页面脚本.json --out 工作/新选题/rendered
```

**3. 全部检查**（有错误时返回 1，不会改动输入）

```bash
python3 scripts/check_all.py 工作/新选题/页面脚本.json --pages 工作/新选题/rendered --out 工作/新选题/检查.json
```

**4. 盲测**（参考图要自己准备，Skill 不带任何他人作品）

```bash
python3 scripts/blind_test.py --reference-dir 参考/内页 --candidate-dir 工作/新选题/rendered --kind inner --out 工作/新选题/盲测.jpg
```

**5. 打包成品**（会先重新检查一遍，目标目录不为空时拒绝覆盖）

```bash
python3 scripts/package.py --note 工作/新选题 --pages 工作/新选题/rendered --out 工作/新选题/交付
```

成品目录结构：

```
交付/
  01-封面.png          带两行大标题的主封面
  02.png … 11.png      内页
  封面备选-无字版.png   可选，用 --cover-c 传入
  全套预览.jpg
  标题.txt  正文.txt  置顶评论.txt  来源.md
  交付清单.json
```

### macOS Vision 工具

```bash
swift scripts/cutout.swift 输入.jpg 输出透明.png
swift scripts/ocr.swift 图片目录 OCR结果.json
swift scripts/检测人脸.swift 人脸输入.json 人脸结果.json
```

---

## 目录结构

```
lishi-tuwen/
  SKILL.md                 AI 读取的主说明：流程、硬规则、入口
  README.md                本文件
  requirements.txt
  references/
    视觉规范.md             现行版式规则：暗色和浅色、字体、颜色交替、背景、抠图
    文案公式.md             标题、正文、话题标签、置顶评论的写法
    选题规律.md
    自检清单.md
    使用说明.md             各脚本的输入输出与失败行为
    用户偏好与否决记录.md     做过、被否掉的方案和原因（只用来理解规则的来历，不当规则执行）
  scripts/
    new_note.py  render.py  check_all.py  blind_test.py  package.py
    验证*.py               各项检查：排版、留白、交替节奏、标题效果、整篇色调、圆盘肖像、混合背景等
    cutout.swift  ocr.swift  检测人脸.swift
    保脸裁切.py  图像等比.py  浅色排版.py  换标题字体重出.py
  assets/
    fonts/                 Noto Serif SC、Noto Sans SC、Ma Shan Zheng（附 OFL 许可证）
    fonts/licensed/        只有说明文件，商业字体由你自己合法接入
    templates/             暗色和浅色页面脚本模板，标题、正文、置顶评论、来源模板
  examples/
    01-砷绿假花/  02-情人眼/  03-泳衣量腿/
                           页面脚本、文稿、来源、素材清单、渲染基准、缩略预览
  验证报告.md               独立复现、三套成品检查、新选题试跑的结果
  验证/                    验证过程的机器记录
```

---

## 核心版式规则（摘要）

完整规则见 `references/视觉规范.md`。

- **色调**：一篇只用一种，暗色或浅色，不混用。
- **封面**：主封面固定是带两行大标题的版本，无字版只当备选。
- **标题字体**：
  - 彩色大字用 Ma Shan Zheng 清晰版：1px 加粗、7 层斜向挤出、柔和投影；
  - 白色大字用 Noto Serif SC 700；
  - 毛笔字里不写阿拉伯数字。
- **颜色交替**：
  - 大字按「强调色、白色」交替，相邻两块不同色；
  - 页面上方三分之一和下方三分之一都要有强调色；
  - 强调色面积每页 0–3%。
- **图片**：
  - 只等比缩放，3:4 裁切铺满，保住人脸，不拉伸、不留填充边；
  - 同一张源图最多出现 2 次；
  - 封面主图在内页再出现时，必须换一个明显不同的裁切。
- **图层**：文字永远在图片上层；文字压到人物超过 3% 就报错。
- **浅色篇**：纸张底，矩形照片带投影，人名用黑色标签，红色手绘圈每页最多 2 个，空白纸面不超过 38%。

---

## 限制与注意事项

- **抠图、OCR、人脸检测只能在 macOS 上自动完成**。其他系统需要提供人工确认的人脸框和抠图 mask；检测失败时会报错，不会当成「没有人脸」处理。
- **不自带任何他人作品**：Skill 里只有自己写的规则拆解和自有成品；盲测用的参考图要自己准备。
- **示例只带缩略图**：示例的原始图片没有打包，素材清单里有每张图的来源和 SHA256。要完整重现示例，需要按清单取得原图，再用 `--assets-root` 指定素材目录。
- **事实和授权最终要人工确认**：检查脚本只验证技术指标，代替不了事实核查和视觉验收。
- **商业字体**：华康等商业字体不随包提供。拿到正式授权后，按 `assets/fonts/licensed/README.md` 接入；不要用第三方「免费下载」的字体文件。

---

## 许可

- **字体**：Noto Serif SC、Noto Sans SC、Ma Shan Zheng 都采用 SIL Open Font License 1.1，许可证在 `assets/fonts/` 下，可以随 Skill 再分发。
- **示例图片**：以各示例 `来源.md` 和 `素材清单.json` 里记录的原始许可为准（公有领域或开放授权）。
- **代码与文稿**：作者保留所有权利。本仓库为私有仓库，仅供受邀者使用，未经许可请勿公开再分发。
