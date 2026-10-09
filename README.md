# cy-carousel · AI 科技图文轮播 Skill

给一个 AI 选题（一个概念、一篇论文、一个产品），做出一篇能直接发小红书的图文笔记：**封面加 10 页内页（1440×1920）、标题、正文、置顶评论和来源清单**。暗底或浅色纸底、电子青强调色，毛笔双色大标题，论文原文放大加红圈，真实截图和人物老照片当主角。全程有事实核查、素材授权记录和自动检查。

这套版式是在一组组 AI 选题上反复测试出来的（ELIZA、Dots、AI 幻觉、聪明汉斯等）。

可以在 **Claude Code** 和 **Codex** 里当 Skill 用。

**最好的两篇**（推荐先看）：

| ELIZA 效应（例 01，暗底） | OpenAI Dots（例 02，浅色纸底） |
|---|---|
| ![ELIZA](examples/01-ELIZA/全套预览.jpg) | ![Dots](examples/02-Dots/全套预览.jpg) |

另外两篇：

| 聪明的汉斯 → 聪明汉斯效应（例 03） | 律师问 ChatGPT → AI 幻觉（例 04） |
|---|---|
| ![聪明汉斯](examples/03-聪明汉斯/全套预览.jpg) | ![AI幻觉](examples/04-AI幻觉/全套预览.jpg) |

例 03 用 1904 年的老照片和原书书页讲「马在看提问人的头」，再接到 AI 模型盯着图片角落的标签拿高分；例 04 用一场官司的公开案卷讲清「AI 幻觉」：法院命令、宣誓书里的 ChatGPT 截图、NIST 定义原文。

> 2026-10-09：原来的历史图文线拆成了单独的本地 Skill `lishi-tuwen`，这个仓库只保留 AI 科技线。历史线的旧版本在本仓库的提交历史里。

---

## 它能做什么

1. **选题**：列几个候选，比素材、体裁、事实风险，选一个。
2. **查证**：每个数字、引文回到论文原文或一手史料，写进事实表；单篇论文的案例不写成「AI 都这样」。
3. **找素材**：只用公有领域和开放授权的素材，记原链接、许可、SHA256 和用页。
4. **手排**：`scripts/手排.py` 提供照片卡、论文矢量纸条、扫描书页纸条（macOS Vision 找词框）、红圈/下划线/页边竖线、贴边出血、整页压暗底图、人名标签、问句贴条、毛笔双色标题、电子青大数字。
5. **检查**：`check_all.py` 一条命令查红线（图注、页眉、页码、小字、孤字）、文字出界、背景分类等。
6. **打包**：输出成品文件夹和全套预览。**不会自动发布。**

## 安装

需要 Python 3.10+、Pillow 12.1+、numpy 2+、PyMuPDF（见 requirements.txt）；扫描书页找词要 macOS（Vision）。

```bash
git clone https://github.com/chengyi-ai/cy-carousel-skill.git ~/.claude/skills/cy-carousel
python3 -m pip install -r ~/.claude/skills/cy-carousel/requirements.txt
```

Codex 把路径换成 `~/.codex/skills/cy-carousel`。装好后新开一个对话。

## 使用

在 Claude Code 或 Codex 里说：

> 用 cy-carousel 做一篇 AI 图文，讲「什么是聪明汉斯效应」，素材要有人物老照片和论文原文，照例 01 ELIZA 的节奏、例 03 的手排脚本来做，做完给我看全套预览。

完整的手排写法见 `examples/03-聪明汉斯/制作.py`，流程和红线见 SKILL.md。

## 目录结构

```
cy-carousel/
  SKILL.md            AI 读取的主说明：红线、版式、流程
  README.md
  requirements.txt
  scripts/
    手排.py            手排工具（AI 线的入口）
    render.py          渲染（毛笔标题的英文数字用 latin_font 换黑体）
    check_all.py       红线和技术检查
    package.py         打包成品
    对照.py            参照页 vs 我们的页：并排对照图＋文字行偏差表（Vision OCR＋颜色阈值）
    blind_test.py      盲测拼图
    build.py  layouts_v2.py  …   底层库（断行、字体配置），不直接用来排 AI 选题
    ocrfind.swift  ocr.swift  cutout.swift  检测人脸.swift   macOS Vision 工具
    emoji.swift        组合 emoji 渲染成透明 PNG（AppKit）
  references/
    排字细节.md         正文字体候选、标点混排、两端对齐、横向压缩、图层顺序、对照测量
  assets/
    fonts/             Noto Serif SC、Noto Sans SC、Ma Shan Zheng（附 OFL 许可证）
    templates/         标题、正文、置顶评论、来源模板
  examples/
    01-ELIZA/          暗底样板：全套预览、逐页文案
    02-Dots/           浅色纸底样板：全套预览、逐页文案
    03-聪明汉斯/        全套预览、制作.py（手排脚本写法）
    04-AI幻觉/          全套预览、制作.py、标题/正文
```

示例只带全套预览、文案和制作脚本，原图、论文 PDF 和事实表没有放进仓库。
