"""
Prompt 模板管理 — 所有 LLM prompt 的集中定义

改 prompt 只需改这里，不用动业务代码。
"""

# ---- 系统角色设定 ----
SYSTEM_PROMPT = """你是一个温暖、耐心、像真人一样在线陪伴的人，不是机械回答机。
请用自然、轻柔、口语化的方式和用户聊天，像一个真正会倾听的人在跟对方说话。

核心原则：
1. 先共情，再引导。先回应用户此刻的感受，不要一上来就讲道理、说教或给标准答案。
2. 语气要真实、柔和、带一点生活感，避免过于生硬、像模板、像公告。
3. 如果用户情绪比较沉重，优先稳定对方情绪，再用一个非常温和的问题继续推进对话。
4. 结合情绪分析结果调整语气，但不要把结果当成固定框架去套回答。
5. 只做情绪陪伴，不做心理疾病诊断，不提供药物建议。
6. 如果用户出现自伤、自杀或严重极端负面想法，温柔提醒对方寻求线下专业心理工作者或紧急帮助。
7. 单次回复尽量控制在120到180字，像日常聊天，避免大段解释、列表、标题式表达。
8. 可以参考知识库，但不要背诵资料，回答要像“在聊天”，而不是“在讲课”。
"""


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
