"""
情绪分析服务 — 使用千问做情绪识别（已移除 BERT 方案）
"""
import logging

from services.llm_service import analyze_emotion_with_qwen
from prompts.templates import ZH_TO_EN

logger = logging.getLogger(__name__)


def analyze_emotion(text: str) -> dict:
    """
    对一段中文文本做情绪分类。

    返回格式（与旧 BERT 方案完全兼容）:
    {
        "emotion": "焦虑",
        "label": "anxiety",
        "score": 0.87,
        "confidence": 0.87,     ← 与 score 同值，保留兼容
        "top3": [
            {"label": "焦虑", "score": 0.87},
            {"label": "悲伤", "score": 0.87},
            {"label": "愤怒", "score": 0.87},
        ]
    }
    """
    result = analyze_emotion_with_qwen(text)

    emo_zh = result.get("emotion", "平静")
    score = result.get("score", 0.5)
    label_en = ZH_TO_EN.get(emo_zh, "calm")

    # 千问只返回一个情绪，top3 用同一结果填充以保持接口兼容
    single = {"label": emo_zh, "score": score}

    return {
        "emotion": emo_zh,
        "label": label_en,
        "score": score,
        "confidence": score,
        "top3": [single, single, single],
    }
