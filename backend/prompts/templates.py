"""
Prompt 模板管理 — 所有 LLM prompt 的集中定义

改 prompt 只需改这里，不用动业务代码。
"""
import json
import re

# ---- 系统角色设定 ----
SYSTEM_PROMPT = """你是一位专业的心理咨询师助手，具备以下能力：
1. 倾听用户的情绪困扰，给予共情回应
2. 基于心理学知识提供科学的建议
3. 在检测到危机信号时，引导用户寻求专业帮助

注意事项：
- 你不是真正的心理医生，严重情况需建议就医
- 回答简洁温暖，不超过 200 字
- 不使用评判性语言
- 如果用户表达自伤/自杀意图，优先建议拨打心理援助热线"""


# ---- 情绪标签（唯一定义处） ----
VALID_EMOTIONS = {"焦虑", "抑郁", "愤怒", "悲伤", "恐惧", "平静", "困惑", "孤独", "压力", "无助"}

ZH_TO_EN = {
    "焦虑": "anxiety",
    "抑郁": "depression",
    "愤怒": "anger",
    "悲伤": "sadness",
    "恐惧": "fear",
    "平静": "calm",
    "困惑": "confusion",
    "孤独": "loneliness",
    "压力": "stress",
    "无助": "helplessness",
}

# ---- 情绪分析专用 prompt ----
EMOTION_ANALYSIS_PROMPT = f"""分析以下用户输入表达的主要情绪，只返回 JSON，不要解释。

情绪类别限定为以下之一：{'、'.join(VALID_EMOTIONS)}。

返回格式（严格 JSON，不要多余文本）：
{{"emotion": "焦虑", "score": 0.85}}

注意：
- score 是 0-1 之间的小数，表示情绪强度
- 只返回 JSON，不要加任何开头或结尾文字"""


def build_emotion_analysis_prompt(text: str) -> str:
    """构造情绪分析请求 prompt"""
    return f"{EMOTION_ANALYSIS_PROMPT}\n\n用户输入：{text}"


def parse_emotion_response(raw_response: str) -> dict:
    """解析千问返回的情绪分析 JSON"""

    # 尝试提取 JSON 部分（千问可能返回多余文字）
    match = re.search(r'\{[^{}]*\}', raw_response)
    if not match:
        return {"emotion": "平静", "score": 0.5, "raw": raw_response}

    try:
        data = json.loads(match.group())
        emo = data.get("emotion", "平静")
        if emo not in VALID_EMOTIONS:
            emo = "平静"
        return {
            "emotion": emo,
            "score": round(float(data.get("score", 0.5)), 4),
        }
    except (json.JSONDecodeError, ValueError):
        return {"emotion": "平静", "score": 0.5}


def build_chat_prompt(user_message: str, emotion: dict, knowledge: list, history: list) -> str:
    """
    构造发给千问的完整 prompt。

    参数:
        user_message: 用户输入文本
        emotion:      情绪分析结果
        knowledge:    RAG 检索到的知识点
        history:      最近 N 轮对话
    """
    parts = []

    # 1. 情绪锚点
    if emotion:
        emo_label = emotion.get("emotion", "")
        emo_score = emotion.get("score", 0)
        if emo_label and emo_score > 0.3:
            parts.append(f"[用户当前情绪]: {emo_label}（置信度 {emo_score:.0%}）")

    # 2. 相关知识
    if knowledge:
        k_text = "\n".join(
            f"- {k.get('title', '')}: {k.get('content', '')[:200]}"
            for k in knowledge[:3]
        )
        if k_text:
            parts.append(f"[心理学参考知识]:\n{k_text}")

    # 3. 对话历史
    if history:
        hist_text = "\n".join(
            f"{'用户' if h['role'] == 'user' else '助手'}: {h['content']}"
            for h in history[-6:]
        )
        if hist_text:
            parts.append(f"[对话历史]:\n{hist_text}")

    # 4. 当前用户消息
    parts.append(f"[用户说]: {user_message}")
    parts.append("请以心理咨询师的身份回复：")

    return "\n\n".join(parts)
