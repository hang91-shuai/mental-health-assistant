"""
健康检查接口 — GET /api/health
前端启动时调用，诊断所有依赖是否正常
"""
from flask import Blueprint

from services.llm_service import ping_ollama
from services.rag_service import ping_chromadb
from services.session_service import get_session_count
from ml_models.emotion import ping_embedding
from utils.response import success

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    components = {}

    # 1. Embedding 模型
    ok, msg = ping_embedding()
    components["embedding_model"] = "ready" if ok else f"error: {msg}"

    # 2. Ollama（千问）
    ok, msg = ping_ollama()
    components["ollama"] = "connected" if ok else f"disconnected: {msg}"

    # 3. ChromaDB
    ok, msg = ping_chromadb()
    components["chromadb"] = "connected" if ok else f"disconnected: {msg}"

    # 4. 会话数
    try:
        components["session_count"] = get_session_count()
    except Exception:
        components["session_count"] = 0

    all_ok = all(
        v in ("connected", "ready")
        for v in [components.get("ollama", ""), components.get("chromadb", ""), components.get("embedding_model", "")]
    )

    return success(data={
        "healthy": all_ok,
        "components": components,
    })
