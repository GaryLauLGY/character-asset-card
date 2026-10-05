# Character Asset Card · 人物资产卡 Skill

把一张或多张人物参考图，组织成可复用的人物资产卡：先独立生成各视角或细节图，再用HTML/CSS与确定性绘图方式排版，最终以原生像素拼合完整PNG。

这是 Gary 从日常AIGC制作中整理的工作流 Skill，支持简单版与复杂版。它提供制作步骤、参考分工、提示词模板和像素校验脚本；不捆绑图像模型、API服务、个人照片或私有项目。

## 两种制作方式

| 简单版：四视图 | 复杂版：分模块 |
|---|---|
| 脸部特写、正面、侧面、背面，四张分别生成 | 三视图，加上需要的表情、服装、鞋履或配饰细节 |
| 通常2×2排版 | 按用途与实际模块数安排页面 |
| 完整卡与四张采用原图共同保留 | 完整卡与全部采用原图共同保留 |

两种方式都先检查身份、服装、物品与左右关系，再拼合。参考中没有的背面或鞋履细节明确标为设计补全。

## 安装

把仓库中的 `skills/character-asset-card` 文件夹复制到目标项目的 `.agents/skills/` 下。已有同名 Skill 时先比较版本，保留自己的修改，不直接覆盖。

```bash
git clone https://github.com/GaryLauLGY/character-asset-card.git
mkdir -p /path/to/your-project/.agents/skills
cp -R character-asset-card/skills/character-asset-card /path/to/your-project/.agents/skills/
```

将 `/path/to/your-project` 换成自己的项目路径。在能读取 `SKILL.md` 的环境中使用；生图部分需要该环境实际提供支持参考图的图像生成工具，没有工具时只能准备规划与提示词。

## 使用示例

简单版：

> 使用 $character-asset-card，根据我提供的照片制作简单人物资产卡。分别生成脸部特写、正面、侧面、背面，保留指定服装，最终交付完整PNG和四张采用原图。

复杂版：

> 使用 $character-asset-card，参考A负责人物身份，参考B负责服装。制作三视图、平静和微笑表情、服装材质及鞋履细节。各模块独立生成，原像素拼合，并保留所有采用原图。

输出位置、尺寸、背景与需要的模块都可以在请求中指定。HTML用于布局和预览；独立原图与完整PNG是默认保留的核心资产，按需提供HTML。

## 原像素校验

拼合时采用图按1:1原生尺寸和整数坐标放置，不缩放、不裁切、不调色。PNG使用无损编码；文件大小和“几倍导出”不能证明画质保留。提供的脚本会逐模块比较解码后的RGBA像素。

```bash
python3 -m pip install -r requirements.txt
python3 skills/character-asset-card/scripts/verify_native_pixels.py   完整资产卡.png 像素区域映射.json --report 像素校验结果.json
```

映射格式与制作示例见 [通用示例](skills/character-asset-card/references/project-examples.md)。必须为全部采用图填写准确位置与实际尺寸，报告文件使用新路径。校验通过表示拼合保留像素，人物相似度、表情与设计一致性仍需实际看图判断。

## 文件

- [SKILL.md](skills/character-asset-card/SKILL.md)：完整制作流程。
- [提示词与记录模板](skills/character-asset-card/references/prompt-and-record.md)：参考职责、模块变量和留档方式。
- [制作与拼合示例](skills/character-asset-card/references/project-examples.md)：两种制作级别、HTML拼合及校验映射。
- [像素校验脚本](skills/character-asset-card/scripts/verify_native_pixels.py)：读取成品与原图，不修改图片。

代码与文档采用 [MIT License](LICENSE)。你可以按自己的工具和项目习惯适配。生成图片的使用范围取决于所用工具及输入素材，本仓库未附带任何人物图片。
