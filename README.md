# Character Asset Card · 人物资产卡 Skill

把人物参考照制作成可复用的六宫格资产卡：**每格独立新生图，整套实际看图复检，再以原像素拼合完整PNG**。

本仓库专门维护可安装 Skill、提示词参考、拼合与像素校验脚本。具体人物制作、原始参考和私人记录留在使用方项目。

## 默认六宫格

| 正面 | 侧面 | 背面 |
|---|---|---|
| 01 正面头部 | 02 侧面头部 | 03 背面头部 |
| 04 正面身体 | 05 侧面身体 | 06 背面身体 |

- 上排是1:1紧凑头部近照：头顶至下巴约占图高80%，完整保留头部与自然脖子，底部只带少量肩根和衣领，减少胸肩占比。
- 下排保留完整脖子至鞋底，头部自然位于画面之外；不是无脖子、空领口或断颈模型。
- 三列两排上下画框等宽，只留六个编号/视图短标签。卡面不加大标题、版本、比例或制作说明。
- 每格分别生成，默认不编辑旧图、不从整张多宫格裁出假原图。复检发现问题时只定向重生相关格子。
- 完整卡和六张采用原图共同保留；PNG无损、原图1:1整数坐标置入。技术检查与人物相似度/观感验收分别记录。

用户明确要四视图时，仍支持“头部肩颈近照＋正侧背完整全身”；复杂版按需增加表情、服装或配饰模块。详情见 [SKILL.md](skills/character-asset-card/SKILL.md)。

## 内置白模构图参考

Skill随附六张原生PNG，见 [参考目录与SHA](skills/character-asset-card/assets/framing/manifest.json)。上排三张已按紧凑头部特写重生，保留自然脖子与少量衣领；下排为保留脖子至鞋底的三个视角。六宫格逐格实际传入对应白模，身份与服装使用各自参考。侧面统一为整个人转满90度，头、颈、肩胸与骨盆同向。

[正面头部](skills/character-asset-card/assets/framing/head-front.png) · [侧面头部](skills/character-asset-card/assets/framing/head-left.png) · [背面头部](skills/character-asset-card/assets/framing/head-back.png)

六宫格每次先用 [单视角请求准备器](skills/character-asset-card/scripts/prepare_six_grid_request.py) 写出本格参数，再用 [生成前检查脚本](skills/character-asset-card/scripts/check_framing_reference.py) 核对单主体／唯一视角、已知歧义和真实白模输入。背视图明确“纯背面、相机在人物正后方”，其他视角、整卡排版和制作备注不进入本次提示词。步骤见 [单次请求模板](skills/character-asset-card/references/prompt-and-record.md)。旧的无单主体开头请求需先重新准备；历史实际请求原样保留，不自动重跑。

身体格首轮先用明确的颈部上边界：画面经过下颌以下的上颈部皮肤，整个头部在画外，保留自然脖子至鞋底；身体提示词只写可见体型／肤色／服装。提交前核对当前单格白模，拒绝夹带退役构图图。后验目检仍保留，软参考不保证一遍必成。

## 安装

将 `skills/character-asset-card` 复制到目标项目的 `.agents/skills/`。已有同名Skill时先比较，保留本地修改。

```bash
git clone https://github.com/GaryLauLGY/character-asset-card.git
mkdir -p /path/to/your-project/.agents/skills
cp -R character-asset-card/skills/character-asset-card /path/to/your-project/.agents/skills/
```

生图需要宿主实际提供支持参考图的图像工具；本仓库不捆绑模型、API或凭据。没有工具时只能准备构图、提示词和记录，不能伪造成图。

## 使用

> 使用 $character-asset-card，根据我的身份与服装参考分别生成六张新图。上排正侧背为1:1头部肩颈近照，下排保留完整脖子至鞋底。上下等宽，只留编号和视图标签，原像素拼合并保留全部原图。

详细构图与参考职责见 [六宫格模板](skills/character-asset-card/references/six-grid-template.md)；生成后按 [AI一致性复检](skills/character-asset-card/references/consistency-review.md) 对照整套图片。未见的背面或鞋履细节标为设计补全，不把低清参考推定当精确还原。

## 原像素等宽拼合

只加画布，不缩放、拉伸、裁切、调色或重采样原图。例如头部1254×1254、身体1024×1536时，身体两侧各补115像素背景，上下外框同宽，原始1024×1536区域完全不变。实际尺寸按输出核对，不依赖提示词中的请求值。

```bash
python3 -m pip install -r requirements.txt
python3 skills/character-asset-card/scripts/compose_six_grid.py 01_正面头部.png 02_侧面头部.png 03_背面头部.png 04_正面身体.png 05_侧面身体.png 06_背面身体.png --output 完整卡.png --mapping 像素区域映射.json
python3 skills/character-asset-card/scripts/verify_native_pixels.py 完整卡.png 像素区域映射.json --report 原像素校验.json
```

脚本自动查找macOS/Linux中文字体；其他环境用 `--font` 指定字体。默认补边复制外侧背景像素，边缘含主体时加 `--padding neutral`。已有输出不会被覆盖。校验逐通道比较六个原图区域，不把文件大小、PNG后缀或几倍导出当画质证明。

## 只取当前版本

已有资产库使用 [当前采用索引](skills/character-asset-card/references/current-selection.md) 按人物和造型取图；[取图脚本](skills/character-asset-card/scripts/find_current_asset.py) 验证路径与SHA，歧义或缺文件时报错。用户授权清旧版本后，将退役卡移出可选库并同步管理入口，保住当前采用原图，不重建旧卡兼容链接。

## 历史示例

[浏览15套历史人物资产卡](examples/README.md) · [已有素材发布](https://github.com/GaryLauLGY/character-asset-card/releases) · [素材使用说明](examples/USAGE.md)

历史示例保留其当时的四视图/分模块规格与既有下载方式，不作为当前六宫格默认。更新Skill不自动重制历史示例，也不默认创建ZIP或上传新的具体人物照片。

## 目录与维护

```text
skills/character-asset-card/  可安装Skill与脚本
examples/                    已有公开示例目录与清单
AGENTS.md                    本仓库维护边界与检查要求
```

可安装源码以本仓库的 `skills/character-asset-card/` 为准。使用方的安装副本按需要比较同步，不将私人项目路径或素材复制进公开源码。

- [构图与提示词记录](skills/character-asset-card/references/prompt-and-record.md)
- [通用制作及映射示例](skills/character-asset-card/references/project-examples.md)
- [原像素拼合脚本](skills/character-asset-card/scripts/compose_six_grid.py)
- [逐像素校验脚本](skills/character-asset-card/scripts/verify_native_pixels.py)

代码与文档采用 [MIT License](LICENSE)；历史示例图片另见[素材使用说明](examples/USAGE.md)。
