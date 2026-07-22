"""
情绪分析服务 — 封装 BERT 模型的推理流程
"""

from ml_models.emotion import predict_emotion
from ml_models.emotion_config import EMOTION_LABELS, LABEL_INDEX


def analyze_emotion(text: str) -> dict:
    """
    对一段中文文本做情绪分类，返回情绪标签和置信度。

    返回格式:
    {
        "emotion": "焦虑",       # 中文标签
        "label": "anxiety",      # 英文标签
        "score": 0.87,           # 最高分
        "confidence": 0.92,      # softmax 置信度
        "top3": [
            {"label": "焦虑", "score": 0.87},
            {"label": "悲伤", "score": 0.06},
            {"label": "愤怒", "score": 0.03},
        ]
    }
    """
    # 调用 BERT 模型做预测
    probs = predict_emotion(text)

    # 取 top3
    indexed = [(i, score) for i, score in enumerate(probs)]
    indexed.sort(key=lambda x: x[1], reverse=True)
    top3 = indexed[:3]

    top_label_idx = top3[0][0]

    result = {
        "emotion": EMOTION_LABELS.get(top_label_idx, "未知"),
        "label": LABEL_INDEX.get(top_label_idx, "unknown"),
        "score": round(float(top3[0][1]), 4),
        "confidence": round(float(top3[0][1]), 4),
        "top3": [
            {
                "label": EMOTION_LABELS.get(idx, "未知"),
                "score": round(float(score), 4),
            }
            for idx, score in top3
        ],
    }
    return result
