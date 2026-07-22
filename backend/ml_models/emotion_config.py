"""
情绪标签配置 — 所有情绪分类标签的唯一定义处
"""

# 中文标签：索引 → 中文名
EMOTION_LABELS = {
    0: "焦虑",
    1: "悲伤",
    2: "愤怒",
    3: "快乐",
    4: "平静",
    5: "恐惧",
    6: "惊讶",
    7: "厌恶",
    8: "孤独",
    9: "无助",
}

# 英文标签：索引 → 英文名
LABEL_INDEX = {
    0: "anxiety",
    1: "sadness",
    2: "anger",
    3: "joy",
    4: "calm",
    5: "fear",
    6: "surprise",
    7: "disgust",
    8: "loneliness",
    9: "helplessness",
}

# 危机信号标签（检测到这些情绪时系统提示引导就医）
CRISIS_LABELS = {-1, "depression_crisis", "suicidal_ideation"}

# 模型参数
NUM_LABELS = len(EMOTION_LABELS)
BERT_MODEL_NAME = "bert-base-chinese"
MAX_SEQ_LENGTH = 128
