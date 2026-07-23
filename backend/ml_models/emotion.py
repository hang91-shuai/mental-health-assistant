"""
模型管理 — BERT 情绪分类已移除，仅保留 Embedding 模型（用于 RAG）

改为 BAAI/bge-small-zh-v1.5，中文向量化效果优于 multilingual-MiniLM。
"""
import logging
import os

from config.settings import settings

logger = logging.getLogger(__name__)

# sentence-transformers 模型（懒加载）
_embedding_model = None


def get_embedding_model():
    """
    获取 Sentence-Transformers 向量化模型（懒加载 + 单例）。

    返回:
        模型实例，或 None（导入失败时）
    """
    global _embedding_model
    if _embedding_model is None:
        try:
            # 设置 Hugging Face 镜像源，国内下载不卡
            os.environ['HF_ENDPOINT'] = settings.HF_ENDPOINT

            from sentence_transformers import SentenceTransformer
            model_name = getattr(settings, 'EMBEDDING_MODEL', 'BAAI/bge-small-zh-v1.5')
            _embedding_model = SentenceTransformer(model_name)
            logger.info("Embedding 模型加载完成: %s", model_name)
        except Exception:
            logger.exception("Embedding 模型加载失败")
            _embedding_model = False  # 标记不可用
    return _embedding_model if _embedding_model is not False else None


def ping_embedding() -> tuple:
    """检测 Embedding 模型是否就绪"""
    try:
        model = get_embedding_model()
        if model is None:
            return False, "模型未加载"
        # 测试编码
        model.encode("测试")
        return True, "ready"
    except Exception as e:
        return False, str(e)
