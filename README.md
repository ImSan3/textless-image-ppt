# textless-image-ppt

根据内容和指定画风制作 PowerPoint：生成视觉底图，再叠加可编辑文字。复刻界面截图时，可将清晰重排的界面文字合入底图。适合教学图解、讲解课件和信息图。

## 安装

将仓库克隆到 Codex 的 skills 目录：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/ImSan3/textless-image-ppt.git ~/.codex/skills/textless-image-ppt
```

如果已有同名目录，请先备份或另选位置，避免覆盖原文件。安装后在新会话中使用 `$textless-image-ppt`，并提供内容、画风及需要的页面比例、页数等要求。完整制作要求见 [SKILL.md](SKILL.md)。

## 工作方式

- 使用图像生成工具制作无字视觉底图，并根据实际留白安排内容。
- 界面截图内的文字经识别、核对和重排后默认合入底图；界面外的标题、正文等文字作为 PowerPoint 文本框叠加，支持编辑。也可以要求界面文字可编辑。
- 输出 PPTX、最终底图和页面预览；可在演讲者备注中放讲解词与资料来源。

图像中的人物、插图、色块和其他视觉元素属于底图的一部分。制作时需要可用的图像生成工具，辅助脚本本身不生成图片。风格参考图仅在相应需求下使用。

## 辅助脚本

需要 Python 3，以及 `python-pptx`、Pillow、OpenCV 和 NumPy：

```bash
python -m pip install -r requirements.txt
python scripts/detect_regions.py path/to/background.png
python scripts/build_pptx.py --spec path/to/deck.json --output outputs/deck.pptx --background-dir outputs/backgrounds
```

JSON 格式、字体和画幅要求见 [SKILL.md](SKILL.md)。生成 PPTX 后，还需使用可用的演示文稿渲染工具检查每页效果。
