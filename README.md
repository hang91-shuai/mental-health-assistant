# 心理健康助手 Mental Health Assistant

一个基于 AI 的大学生心理健康辅助平台。

- **前端**：微信小程序（TDesign 组件库）
- **后端**：Flask + 千问情绪分析 + Ollama 对话 + ChromaDB RAG（bge-small-zh 向量化）

---

## 项目结构

```
mental-health-assistant/
├── backend/           # Flask 后端（邢子行）
│   ├── app.py
│   ├── config/        # 配置
│   ├── routes/        # API 接口
│   ├── ml_models/     # Embedding 模型（RAG 向量化）
│   ├── services/      # 业务逻辑（LLM/情绪/RAG/会话）
│   ├── prompts/       # Prompt 模板
│   ├── scripts/       # 工具脚本
│   └── utils/         # 工具函数
├── data/              # 数据（王兴国）
│   └── psychology_kb/ # 心理学知识库 txt
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
| Ollama + Qwen2.5 | 对话生成 + 情绪分析 |
| ChromaDB | 向量知识库 |
| BAAI/bge-small-zh-v1.5 | 中文文本嵌入 |

## 今日任务

| 成员 | 任务 |
|------|------|
| **邢子行**（后端） | ① 后端代码已全部写完（情绪分析 + 对话 + RAG + 会话） ② 等尉文清装好 Ollama 后联调 `/api/analyze` 和 `/api/chat` ③ 等王兴国知识库到位后跑 build_kb.py |
| **王兴国**（数据） | ① 从壹心理/简单心理收集 ≥10 篇心理科普文章 ② 按 `docs/KB_FORMAT.md` 格式整理成 txt ③ 放入 `data/psychology_kb/` |
| **尹天浩**（前端） | ① 初始化微信小程序项目于 `frontend/` ② 调通 `/api/ping` 和 `/api/health` |
| **尉文清**（LLM） | ① 安装 Ollama → 拉取 `qwen2.5:7b`（这是千问运行的前提） ② 终端测试千问能对话 ③ 确认 `/api/health` 显示 ollama: connected |

## 团队

- **邢子行**（组长）：后端开发
- **王兴国**：数据收集 & 知识库
- **尹天浩**：微信小程序前端
- **尉文清**：LLM 部署 & Prompt
