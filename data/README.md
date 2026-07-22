# 数据目录

## 结构

```
data/
├── datasets/        # BERT 微调用情绪分类数据集（王兴国收集）
├── psychology_kb/   # 心理学知识库 txt 文件（王兴国收集）
└── chroma_db/       # ChromaDB 持久化向量索引（自动生成，不提交）
```

## 数据集来源（参考）

- HuggingFace: 搜索 "chinese emotion dataset"
- NLPCC 情感分析评测数据
- SMP 中文情感分析评测

## 知识库来源（参考）

- 壹心理 (xinli001.com)
- 丁香园心理学板块 (dxy.cn)
- 简单心理 (jiandanxinli.com)
- WHO 心理健康手册

## 注意

- `chroma_db/` 已在 `.gitignore` 中排除
- 知识库 txt 格式见 `docs/KB_FORMAT.md`
