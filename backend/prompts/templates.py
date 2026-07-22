"""
Prompt 模板管理 — 所有 LLM prompt 的集中定义

改 prompt 只需改这里，不用动业务代码。
"""

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
            f"- {k.get('title', '')}: {k.get('content', '')[:150]}"
            for k in knowledge[:2]
        )
        parts.append(f"[心理学参考知识]:\n{k_text}")

    # 3. 对话历史
    if history:
        hist_text = "\n".join(
            f"{'用户' if h['role']=='user' else '助手'}: {h['content']}"
            for h in history[-6:]  # 最多 6 条
        )
        parts.append(f"[对话历史]:\n{hist_text}")

    # 4. 当前用户消息
    parts.append(f"[用户说]: {user_message}")
    parts.append("请以心理咨询师的身份回复：")

    return "\n\n".join(parts)
