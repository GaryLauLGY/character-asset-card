# Character Asset Card · 人物资产卡 Skill

把一张或多张人物参考图，组织成可复用的人物资产卡：先独立生成各视角或细节图，再用HTML/CSS与确定性绘图方式排版，最终以原生像素拼合完整PNG。

这是 Gary 从日常AIGC制作中整理的工作流 Skill，支持简单版与复杂版。它提供制作步骤、参考分工、提示词模板和像素校验脚本；不捆绑图像模型、API服务或私有制作项目。另提供 15 套作者选定的已有资产卡示例与下载包。

## 示例与现成资产

**[浏览 15 套人物资产卡](examples/README.md)** · [素材发布与版本](https://github.com/GaryLauLGY/character-asset-card/releases) · [素材使用说明](examples/USAGE.md)

涵盖真人形象、影视角色、动画与 Q 版造型。每套有预览、文件清单和 SHA-256；现有完整卡与各视角图片按套下载，避免重复生成。历史版本及缺失原图会明确说明。

### 成品展示

| 肌肉难梁 · 蓝西装全身四视图 | 大肥鱼少女版 · 女仆装四视图 |
|:---:|:---:|
| [<img src="https://github.com/GaryLauLGY/character-asset-card/releases/download/examples-2026-10-14/muscle-liang-blue-preview.png" alt="肌肉难梁蓝西装全身四视图资产卡" width="420">](https://github.com/GaryLauLGY/character-asset-card/releases/download/examples-2026-10-14/muscle-liang-blue-preview.png) | [<img src="https://github.com/GaryLauLGY/character-asset-card/releases/download/examples-2026-10-14-whale-girl-v003/whale-girl-maid-v003-preview.png" alt="大肥鱼少女版女仆装四视图资产卡" width="420">](https://github.com/GaryLauLGY/character-asset-card/releases/download/examples-2026-10-14-whale-girl-v003/whale-girl-maid-v003-preview.png) |
| [查看示例说明](examples/muscle-liang-blue/README.md) · [下载完整素材包](https://github.com/GaryLauLGY/character-asset-card/releases/download/examples-2026-10-14/muscle-liang-blue.zip) | [查看示例说明](examples/whale-girl-maid/README.md) · [下载完整素材包](https://github.com/GaryLauLGY/character-asset-card/releases/download/examples-2026-10-14-whale-girl-v003/whale-girl-maid-v003.zip) |

点击图片查看原尺寸完整卡；下载包包含完整卡与已有独立视角图片。

## 两种制作方式

| 简单版：四视图 | 复杂版：分模块 |
|---|---|
| 脸部特写、正面全身、侧面全身、背面全身，四张分别生成 | 三视图，加上需要的表情、服装、鞋履或配饰细节 |
| 通常2×2排版 | 按用途与实际模块数安排页面 |
| 完整卡与四张采用原图共同保留 | 完整卡与全部采用原图共同保留 |

正、侧、背默认完整保留头顶至鞋底，并留出边缘余量；只有明确要求半身或膝上时才改变景别。参考没拍到下半身或鞋履时做克制补全并标注，不自动截成半身。

两种方式在生成后都执行 [AI 整套一致性复检](skills/character-asset-card/references/consistency-review.md)：AI 实际对照参考和全部生成图，自行识别应保持的设计与关系；发现明确矛盾则定向修复，再对整套图复检，通过后拼合。参考中没有的背面或鞋履细节明确标为设计补全。

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

> 使用 $character-asset-card，根据我提供的照片制作简单人物资产卡。分别生成脸部特写、正面全身、侧面全身、背面全身，保留指定服装，最终交付完整PNG和四张采用原图。

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

## 仓库结构

```text
skills/character-asset-card/  # 可安装 Skill：流程、模板、像素校验工具
examples/README.md          # 人物资产目录
examples/catalog.json       # 机器可读下载索引
examples/<角色ID>/          # 每套说明与文件清单
GitHub Releases            # 原始图片 ZIP、原尺寸预览、SHA256SUMS.txt
```

图片和下载包保存在 Releases，不进入 Git 历史；安装 Skill 只需要复制 `skills/character-asset-card`。历史示例展示当时的产物，不覆盖当前 Skill 的默认全身规则。新增资产使用新 Release 保留旧版本。

## 文件

- [SKILL.md](skills/character-asset-card/SKILL.md)：完整制作流程。
- [提示词与记录模板](skills/character-asset-card/references/prompt-and-record.md)：参考职责、模块变量和留档方式。
- [制作与拼合示例](skills/character-asset-card/references/project-examples.md)：两种制作级别、HTML拼合及校验映射。
- [像素校验脚本](skills/character-asset-card/scripts/verify_native_pixels.py)：读取成品与原图，不修改图片。

代码与文档采用 [MIT License](LICENSE)。你可以按自己的工具和项目习惯适配。示例图片单独遵循[素材使用说明](examples/USAGE.md)，不将代码的 MIT 许可自动扩展为第三方角色或肖像授权。
