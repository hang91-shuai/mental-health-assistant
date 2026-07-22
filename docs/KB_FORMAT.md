# 知识库 txt 文件格式约定

每个 `.txt` 文件必须包含以下元数据头部：

## 格式

```
---
title: 文章标题
keywords: 关键词1, 关键词2, 关键词3
---

# 正文内容

段落之间用空行分隔。

每个段落至少 30 字以上，保证 ChromaDB 切割质量。
```

## 规则

| 字段 | 必填 | 说明 |
|------|:--:|------|
| `title` | 是 | 文章标题，用作文档标识 |
| `keywords` | 否 | 逗号分隔，用于元数据过滤 |
| 正文 | 是 | `---` 之后的所有内容，段落间空行分隔 |

## 示例

参见 `data/psychology_kb/anxiety.txt`。

## 构建索引

新增/修改 txt 后，运行：

```
cd backend
python scripts/build_kb.py
```

清空重建：

```
python scripts/build_kb.py --rebuild
```
