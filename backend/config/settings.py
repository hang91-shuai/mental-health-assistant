"""
全局配置 — 从环境变量 + .env 文件读取
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 显式指定 .env 路径，避免 CWD 变化导致找不到
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)


class Settings:
    """应用配置"""

    # ---- 服务器 ----
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    # ---- Ollama（千问） ----
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", 60))

    # ---- Embedding 模型（RAG 向量化） ----
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    HF_ENDPOINT: str = os.getenv("HF_ENDPOINT", "https://hf-mirror.com")

    # ---- ChromaDB ----
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "psychology_kb")

    # ---- 会话管理 ----
    SESSION_MAX_COUNT: int = int(os.getenv("SESSION_MAX_COUNT", 10000))
    SESSION_TTL: int = int(os.getenv("SESSION_TTL", 1800))       # 30 分钟过期
    SESSION_MAX_HISTORY: int = int(os.getenv("SESSION_MAX_HISTORY", 10))

    # ---- RAG 检索 ----
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", 3))


settings = Settings()
