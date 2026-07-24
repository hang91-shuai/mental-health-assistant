"""
Prompt 模板管理 — 所有 LLM prompt 的集中定义

改 prompt 只需改这里，不用动业务代码。
"""
import json
import re

# ---- 系统角色设定 ----
SYSTEM_PROMPT = """你是一个温暖、耐心、像真人一样在线陪伴的人，不是机械回答机。
请用自然、轻柔、口语化的方式和用户聊天，像一个真正会倾听的人在跟对方说话。

核心原则：
1. 先共情，再引导。先回应用户此刻的感受，不要一上来就讲道理、说教或给标准答案。
2. 语气要真实、柔和、带一点生活感，避免像模板、像公告、像标准话术。
3. 如果用户情绪比较沉重，优先稳定对方情绪，再用一个非常温和的问题继续推进对话。
4. 结合情绪分析结果调整语气，但不要把结果当成硬套的框架去回答。
5. 只做情绪陪伴，不做心理疾病诊断，不提供药物建议。
6. 如果用户出现自伤、自杀或严重极端负面想法，温柔提醒对方寻求线下专业心理工作者或紧急帮助。
7. 单次回复尽量控制在120到180字，像日常聊天，避免大段解释、列表、标题式表达。
8. 可以参考知识库，但不要背诵资料，回答要像“在聊天”，而不是“在讲课”。
"""

# ---- 情绪专项系统提示词 ----
EMOTION_SYSTEM_PROMPTS = {
    "焦虑": """你正在陪伴一个焦虑感很强的用户。对方的担心往往不只是“想不明白”，而是心里一直发紧。回应时要先接住这份持续的紧张感，而不是一上来就讲方法。语气要更稳、更慢、更安抚，像一个愿意陪对方把心里的乱慢慢放下的人。先共情，再轻轻把模糊的担心拆成一个小点，让对方感到“我不是一个人扛着”。""",
    "抑郁": """你正在陪伴一个抑郁情绪明显的用户。对方通常更需要被理解、被接住，而不是被催促、被鼓励。回复时要减少急切感、减少推着走的感觉，用更温和、更缓慢、无压力的语气陪伴对方。不要把低落说成“你得振作”，而是先让对方知道：我现在难过，是可以被承认的，我也不是一个人。""",
    "愤怒": """你正在陪伴一个愤怒情绪较高的用户。对方的火气里常常带着委屈、失控或被忽视感，所以先别急着反驳。要先接住这份愤怒，让对方觉得“我被听到了，我不是被否定了”。语气要更克制、更平稳，像一个能帮人把情绪慢慢放下来的人。你可以在不认同对方行为的前提下，帮助对方把自己到底在生气什么说清楚。""",
    "悲伤": """你正在陪伴一个悲伤情绪较强的用户。这里的重点不是马上找答案，而是让对方感到“我现在难过，没关系，我可以慢慢说”。语气要更柔软、温暖、慢一点，允许伤感、失落和沉默。不要一上来就安慰太重，优先让对方有被接住的感觉，像有人愿意陪着他把这份难过放在一边。""",
    "恐惧": """你正在陪伴一个恐惧感很强的用户。对方的核心需求通常是安全感、稳定感和可控感，所以要减少刺激性表达，先稳住对方。语气要更慢、更稳，带一点“我们先一起把这件事缓下来”的感觉。不要直接用“别怕”压缩情绪，先让对方知道：你现在的害怕是被理解的，这件事不会让你一个人硬扛。""",
    "平静": """你正在陪伴一个本身较平静、表达比较稳定的用户。回复时保持轻松、真实、简洁，不要过度包装。更像普通聊天，少一点强烈情绪引导，多一点自然顺畅的回应。重点是让对方觉得你在认真听，而不是在“分析”他。""",
    "困惑": """你正在陪伴一个处在困惑状态的用户。对方往往不是缺答案，而是还没把自己的想法说清楚。所以不要急着定论，而是用更开放、轻柔的方式帮对方把模糊感慢慢拉出来。可以用一个很温和的问题，让对方先有一点方向感，而不是马上被解释淹没。""",
    "孤独": """你正在陪伴一个孤独感很强的用户。这里的重点不是只说“你不孤单”，而是让对方真的感到“我有被看见的空间”。语气要温暖、贴近、有一点连接感。少一点说教，多一点带回应感的陪伴，让对方觉得这段话不是冷冰冰的，而是有人在这里。""",
    "压力": """你正在陪伴一个压力很大的用户。对方往往已经很累了，回应时要有现实感和分担感，避免把复杂问题简化成一句标准话术。可以先帮对方把事情拆开一点，把压迫感降一层，再慢慢往前走。重点是让对方感觉“我不是一个人背着这份重”。""",
    "无助": """你正在陪伴一个无助感很强的用户。这里要更稳、更温柔，先把“现在不一定要自己硬扛完”这件事说出来，再用轻一点的引导帮对方重新找回一点方向感。不要过于强调鼓励词，而是让对方感到“你目前可以先不用自己一个人把所有东西都想明白”。""",
}


# ---- 情绪标签（唯一定义处） ----
VALID_EMOTIONS = (
    "焦虑",
    "抑郁",
    "愤怒",
    "悲伤",
    "恐惧",
    "平静",
    "困惑",
    "孤独",
    "压力",
    "无助",
)

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

# ---- 少样本（few-shot）示例 ----
EMOTION_FEW_SHOT_EXAMPLES = {
    "焦虑": [
        {"text": "我最近总担心明天会出事，心里一直乱，睡不着。", "emotion": "焦虑", "score": 0.90},
        {"text": "我一想事情就开始紧张，手心冒汗，脑子里一直在转。", "emotion": "焦虑", "score": 0.83},
        {"text": "我怕我做错什么，怕别人不高兴，整个人一直绷着。", "emotion": "焦虑", "score": 0.78},
    ],
    "抑郁": [
        {"text": "最近什么都提不起劲，感觉整个人都很沉。", "emotion": "抑郁", "score": 0.85},
        {"text": "我一点都不想说话，也不想面对任何事，心里空空的。", "emotion": "抑郁", "score": 0.88},
        {"text": "我好像已经没什么想要的了，活着都觉得很累。", "emotion": "抑郁", "score": 0.92},
    ],
    "愤怒": [
        {"text": "我现在真的很生气，别人都不理解我，越想越火。", "emotion": "愤怒", "score": 0.84},
        {"text": "我现在心里特别烦，觉得自己被惹火了，想直接爆发。", "emotion": "愤怒", "score": 0.82},
        {"text": "这件事让我很愤怒，明明我已经很不容易了，却还是被说成这样。", "emotion": "愤怒", "score": 0.79},
    ],
    "悲伤": [
        {"text": "我最近很难过，感觉心里一直被压着。", "emotion": "悲伤", "score": 0.86},
        {"text": "这件事让我很失落，明明都过去了，可我还是忍不住想哭。", "emotion": "悲伤", "score": 0.80},
        {"text": "我现在特别难过，像什么都不一样了。", "emotion": "悲伤", "score": 0.83},
    ],
    "恐惧": [
        {"text": "我现在特别害怕，脑子里一直在想最坏的结果。", "emotion": "恐惧", "score": 0.88},
        {"text": "我一想到某些事情就会全身发抖，真的很怕。", "emotion": "恐惧", "score": 0.84},
        {"text": "我心里很慌，感觉自己快控制不住了。", "emotion": "恐惧", "score": 0.82},
    ],
    "平静": [
        {"text": "现在我还挺放松的，心情比较稳定。", "emotion": "平静", "score": 0.42},
        {"text": "我今天状态还可以，没太大波动。", "emotion": "平静", "score": 0.36},
        {"text": "我现在比较平静，没什么特别的压力。", "emotion": "平静", "score": 0.40},
    ],
    "困惑": [
        {"text": "我不是很懂自己为什么会这样，心里很乱。", "emotion": "困惑", "score": 0.76},
        {"text": "我现在有点摸不清楚自己的想法，脑子里很乱。", "emotion": "困惑", "score": 0.74},
        {"text": "我不知道为什么会这样，感觉自己很难理解自己。", "emotion": "困惑", "score": 0.72},
    ],
    "孤独": [
        {"text": "我现在特别孤独，明明身边很多人，却还是一个人。", "emotion": "孤独", "score": 0.87},
        {"text": "我感觉自己很落单，没有人能真正懂我。", "emotion": "孤独", "score": 0.84},
        {"text": "最近总有一种想找人说话，但又不知道说给谁听的感觉。", "emotion": "孤独", "score": 0.78},
    ],
    "压力": [
        {"text": "这几天工作和生活都让我很压抑，感觉一直在被赶。", "emotion": "压力", "score": 0.81},
        {"text": "我现在真的有点喘不过气，对很多事都很疲惫。", "emotion": "压力", "score": 0.80},
        {"text": "我现在压力很大，脑子里一直在转各种事情。", "emotion": "压力", "score": 0.78},
    ],
    "无助": [
        {"text": "我现在真的觉得自己没办法解决这件事，心里很慌。", "emotion": "无助", "score": 0.85},
        {"text": "我不知道该怎么办，感觉自己一筹莫展。", "emotion": "无助", "score": 0.83},
        {"text": "我现在真的很无助，像什么都不靠得住。", "emotion": "无助", "score": 0.86},
    ],
}


# ---- 情绪分析专用 prompt ----
EMOTION_ANALYSIS_PROMPT = f"""分析以下用户输入表达的主要情绪，只返回 JSON，不要解释。

情绪类别限定为以下之一：{'、'.join(VALID_EMOTIONS)}。

少样本示例（few-shot）:
{chr(10).join(
    [
        f"输入：{example['text']} -> {{\"emotion\": \"{example['emotion']}\", \"score\": {example['score']}}}"
        for emotion in VALID_EMOTIONS
        for example in EMOTION_FEW_SHOT_EXAMPLES[emotion][:3]
    ]
)}

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


def get_system_prompt_for_emotion(emotion: dict | None) -> str:
    """根据识别到的情绪，返回更贴合的 system prompt。"""
    if not emotion:
        return SYSTEM_PROMPT

    emo_label = emotion.get("emotion", "")
    if emo_label in EMOTION_SYSTEM_PROMPTS:
        return f"{SYSTEM_PROMPT}\n\n{EMOTION_SYSTEM_PROMPTS[emo_label]}"

    return SYSTEM_PROMPT


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
