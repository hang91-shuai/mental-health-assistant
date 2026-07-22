"""
对话接口 — POST /api/chat
一次请求完成：情绪分析 + RAG检索 + 千问回复
"""

from flask import Blueprint, request

from utils.response import success, bad_request

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True)
    if not body or "message" not in body:
        return bad_request("缺少 message 字段")

    message = body["message"].strip()
    if not message:
        return bad_request("message 不能为空")
    if len(message) > 1000:
        return bad_request("message 不能超过 1000 字")

    session_id = body.get("session_id", "")

    try:
        # 1. 情绪分析
        from services.emotion_service import analyze_emotion
        emotion_result = analyze_emotion(message)

        # 2. RAG 检索
        from services.rag_service import search_knowledge
        knowledge = search_knowledge(message)

        # 3. 对话历史
        from services.session_service import get_or_create_session, add_message
        session = get_or_create_session(session_id)
        context = session["history"]

        # 4. 调用千问
        from services.llm_service import chat_with_qwen
        reply = chat_with_qwen(
            message=message,
            emotion=emotion_result,
            knowledge=knowledge,
            history=context,
        )

        # 5. 保存对话
        session_id, _ = add_message(session_id, "user", message)
        _, _ = add_message(session_id, "assistant", reply)

        return success(data={
            "reply": reply,
            "emotion": emotion_result,
            "session_id": session_id,
            "knowledge_refs": [k.get("title", "") for k in knowledge],
        })

    except Exception as e:
        from utils.response import error
        return error(f"对话处理失败: {str(e)}")
