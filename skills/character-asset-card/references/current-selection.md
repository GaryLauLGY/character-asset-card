# 当前采用索引

当资产库已有当前索引，或用户要求“只保留最新最终版本”时，当前索引是取图入口。按人物＋造型精确匹配，不以最高版本号、最近修改时间、旧项目记录或目录搜索代替选择。不同服装／画风分别登记；未指定造型且没有明确默认值时报告候选，不能混用原图。

`scripts/find_current_asset.py` 读取以下格式，验证采用图片仍在当前库内且SHA一致。找不到、歧义或字节变化均报错，不搜索旧目录补位。

```json
{
  "schema": "character-asset-current/1",
  "library_root": "/absolute/path/to/current-library",
  "defaults": {"人物别名": "asset-example"},
  "entries": [{
    "id": "asset-example",
    "name": "人物名称",
    "aliases": ["人物别名"],
    "style": "黑T紧身牛仔裤",
    "folder": "人物_黑T紧身牛仔裤_v002",
    "selectable": true,
    "format": "complete_card",
    "primary": {"path": "人物_黑T紧身牛仔裤_v002/完整卡.png", "sha256": "实际64位SHA256"},
    "sources": [{"path": "人物_黑T紧身牛仔裤_v002/01_正面头部.png", "sha256": "实际64位SHA256"}]
  }]
}
```

`primary` 是当前图片入口；只有确有整卡时标记 `complete_card`。仅有原图集合或单图时分别标 `original_set`、`single_view`，不能将单格冒称完整卡。`sources` 列全部采用的独立原图；可选 `boards` 列同套资产的其他现用展示板。图片路径可相对于 `library_root`，或用该根内的绝对路径。

```sh
python3 scripts/find_current_asset.py /path/to/当前采用.json --name 人物别名
python3 scripts/find_current_asset.py /path/to/当前采用.json --name 人物名称 --style 黑T紧身牛仔裤
```

发布同造型新版本时先核对完整卡、全部采用原图与原始输入引用，再更新索引。用户已授权清理旧版本时，先将最新版仍依赖的原图保为不依赖旧目录的原字节文件，原始身份／服装输入留在制作项目，然后把退役版本移出可选库。核对索引、别名、启明等管理目录和旧交付入口，不在旧资产路径重建指向旧图或废纸篓的兼容链接。生成记录可留作追溯，不能作为默认素材候选。未获清理授权不自动删除历史。索引的当前选择状态不替代用户视觉验收。
