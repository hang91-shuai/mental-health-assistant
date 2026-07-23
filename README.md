<<<<<<< HEAD
# 心理健康助手 Mental Health Assistant

一个基于 AI 的大学生心理健康辅助平台。

- **前端**：微信小程序（TDesign 组件库）
- **后端**：Flask + BERT 情绪识别 + Ollama 千问 + ChromaDB RAG

---

## 项目结构

```
mental-health-assistant/
├── backend/           # Flask 后端（邢子行）
│   ├── app.py
│   ├── config/        # 配置
│   ├── routes/        # API 接口
│   ├── ml_models/     # BERT 情绪识别
│   ├── services/      # 业务逻辑（LLM/RAG/会话）
│   ├── prompts/       # Prompt 模板
│   ├── scripts/       # 工具脚本
│   └── utils/         # 工具函数
├── data/              # 数据（王兴国）
│   ├── datasets/      # 训练数据集
│   └── psychology_kb/ # 心理学知识库
├── frontend/          # 前端小程序（尹天浩）
└── docs/              # 文档
    ├── API.md         # 接口约定
    └── KB_FORMAT.md   # 知识库格式
```

---

## 快速启动

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 配置（复制 .env.example 为 .env 并修改）
cp .env.example .env

# 3. 启动服务
python app.py

# 4. 测试
# 浏览器打开 http://localhost:5000/api/ping
```

---

## 技术栈

| 技术 | 用途 |
|------|------|
| Flask 3.0 | Web 框架 |
| BERT-base-chinese | 情绪识别 |
| Ollama + Qwen2.5 | 对话生成 |
| ChromaDB | 向量知识库 |
| Sentence Transformers | 文本嵌入 |

## 团队

- **邢子行**（组长）：后端开发
- **王兴国**：数据收集 & 知识库
- **尹天浩**：微信小程序前端
- **尉文清**：LLM 部署 & Prompt
=======
# 前端目录

小程序代码由 **尹天浩** 负责。

技术栈：微信小程序 + TDesign 组件库

## 接口约定

所有接口以 `docs/API.md` 为准。
>>>>>>> ec4386650a3b961a17f21b98da2cd748551e5c33
