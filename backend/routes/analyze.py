"""
情绪分析接口 — POST /api/analyze
"""

from flask import Blueprint, request

from utils.response import success, bad_request

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/api/analyze", methods=["POST"])
def analyze():
    body = request.get_json(silent=True)
    if not body or "text" not in body:
        return bad_request("缺少 text 字段")

    text = body["text"].strip()
    if not text:
        return bad_request("text 不能为空")
    if len(text) > 500:
        return bad_request("text 不能超过 500 字")

    try:
        from services.emotion_service import analyze_emotion
        result = analyze_emotion(text)
        return success(data=result)
    except Exception as e:
        from utils.response import error
        return error(f"情绪分析失败: {str(e)}")
