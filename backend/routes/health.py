"""
健康检查接口 — GET /api/health
前端启动时调用，诊断所有依赖是否正常
"""

from flask import Blueprint

from utils.response import success, error

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    components = {}

    # 1. BERT
    try:
        from ml_models.emotion import get_emotion_model
        model, tokenizer = get_emotion_model()
        components["bert_model"] = "loaded" if model else "not_loaded"
    except Exception as e:
        components["bert_model"] = f"error: {str(e)}"

    # 2. Ollama
    try:
        from services.llm_service import ping_ollama
        ok, msg = ping_ollama()
        components["ollama"] = "connected" if ok else f"disconnected: {msg}"
    except Exception as e:
        components["ollama"] = f"error: {str(e)}"

    # 3. ChromaDB
    try:
        from services.rag_service import ping_chromadb
        ok, msg = ping_chromadb()
        components["chromadb"] = "connected" if ok else f"disconnected: {msg}"
    except Exception as e:
        components["chromadb"] = f"error: {str(e)}"

    # 4. 会话数
    try:
        from services.session_service import get_session_count
        components["session_count"] = get_session_count()
    except Exception:
        components["session_count"] = 0

    all_ok = all(
        v in ("connected", "loaded")
        for v in [components.get("ollama", ""), components.get("chromadb", ""), components.get("bert_model", "")]
    )

    return success(data={
        "healthy": all_ok,
        "components": components,
    })
