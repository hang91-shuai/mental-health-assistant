"""
BERT 情绪识别模型 — 加载 + 推理

模型权重从 HuggingFace 远程下载（首次）或本地缓存加载。
不在此文件中硬编码标签映射，统一从 emotion_config 读取。
"""

import os

from config.settings import settings
from ml_models.emotion_config import BERT_MODEL_NAME, MAX_SEQ_LENGTH, NUM_LABELS

# 懒加载的单例
_bert_model = None
_bert_tokenizer = None
_embedding_model = None


def get_emotion_model() -> tuple:
    """
    获取 BERT 模型和 tokenizer（单例懒加载）。

    返回:
        (model, tokenizer) 或 (None, None)
    """
    global _bert_model, _bert_tokenizer

    if _bert_model is not None:
        return _bert_model, _bert_tokenizer

    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        # 设置 HF 镜像（国内加速）
        if settings.HF_ENDPOINT:
            os.environ["HF_ENDPOINT"] = settings.HF_ENDPOINT

        _bert_tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_NAME)
        _bert_model = AutoModelForSequenceClassification.from_pretrained(
            BERT_MODEL_NAME,
            num_labels=NUM_LABELS,
        )
        _bert_model.eval()
        return _bert_model, _bert_tokenizer

    except Exception as e:
        print(f"[emotion] BERT 模型加载失败: {e}")
        return None, None


def get_embedding_model():
    """
    获取 embedding 模型用于 ChromaDB 向量化（单例懒加载）。
    使用 sentence-transformers 的 paraphrase-multilingual-MiniLM-L12-v2。
    """
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    try:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        return _embedding_model
    except Exception as e:
        print(f"[emotion] Embedding 模型加载失败: {e}")
        return None


def predict_emotion(text: str) -> list:
    """
    对文本做情绪分类推理，返回各标签概率分布。

    返回:
        [0.01, 0.02, ..., 0.87, ...]  # 长度 = NUM_LABELS
    """
    import torch
    import torch.nn.functional as F

    model, tokenizer = get_emotion_model()
    if model is None or tokenizer is None:
        # 模型不可用时返回均匀分布
        return [1.0 / NUM_LABELS] * NUM_LABELS

    inputs = tokenizer(
        text,
        max_length=MAX_SEQ_LENGTH,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1).squeeze(0)

    return probs.tolist()
