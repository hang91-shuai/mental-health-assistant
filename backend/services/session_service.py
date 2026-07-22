"""
会话管理服务 — 内存字典 + 线程锁 + TTL 过期
"""

import threading
import time
import uuid

from config.settings import settings


_EMPTY = object()

_sessions: dict = {}              # { session_id: {"history":[...], "last_active": timestamp} }
_lock = threading.Lock()


def _cleanup_expired():
    """清理过期会话"""
    now = time.time()
    expired = [
        sid for sid, s in _sessions.items()
        if now - s.get("last_active", 0) > settings.SESSION_TTL
    ]
    for sid in expired:
        del _sessions[sid]


def get_or_create_session(session_id: str = "", create_if_missing: bool = True) -> dict:
    """
    获取或创建会话。

    返回:
        {"session_id": "...", "history": [...], "last_active": ...}
    """
    with _lock:
        _cleanup_expired()

        if session_id and session_id in _sessions:
            s = _sessions[session_id]
            s["last_active"] = time.time()
            return {"session_id": session_id, **s}

        if create_if_missing:
            # 检查数量上限
            if len(_sessions) >= settings.SESSION_MAX_COUNT:
                # 删除最旧的
                oldest = min(_sessions.keys(), key=lambda sid: _sessions[sid]["last_active"])
                del _sessions[oldest]

            new_id = str(uuid.uuid4())
            _sessions[new_id] = {
                "history": [],
                "last_active": time.time(),
            }
            return {"session_id": new_id, "history": [], "last_active": time.time()}

        return {"session_id": "", "history": [], "last_active": 0}


def add_message(session_id: str, role: str, content: str) -> tuple:
    """
    向会话中添加一条消息。

    参数:
        session_id: 会话 ID
        role:       "user" 或 "assistant"
        content:    消息内容

    返回:
        (session_id, latest_history)
    """
    session = get_or_create_session(session_id)
    sid = session["session_id"]

    with _lock:
        if sid in _sessions:
            _sessions[sid]["history"].append({"role": role, "content": content})
            _sessions[sid]["last_active"] = time.time()

            # 保留最近 N 轮
            max_len = settings.SESSION_MAX_HISTORY * 2  # 每轮 user + assistant
            if len(_sessions[sid]["history"]) > max_len:
                _sessions[sid]["history"] = _sessions[sid]["history"][-max_len:]

        return sid, _sessions.get(sid, {}).get("history", [])


def get_session_count() -> int:
    """返回当前活跃会话数"""
    with _lock:
        _cleanup_expired()
        return len(_sessions)
