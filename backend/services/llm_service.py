"""
LLM 服务 — 封装 Ollama 千问模型调用
"""

import requests

from config.settings import settings


def ping_ollama() -> tuple:
    """检测 Ollama 是否连通，返回 (是否连通, 消息)"""
    try:
        resp = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5,
        )
        if resp.status_code == 200:
            return True, "connected"
        return False, f"status {resp.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "连接被拒绝，Ollama 是否启动？"
    except requests.exceptions.Timeout:
        return False, "连接超时"
    except Exception as e:
        return False, str(e)


def chat_with_qwen(message: str, emotion: dict, knowledge: list, history: list) -> str:
    """
    调用千问模型生成回复。

    参数:
        message:   用户输入
        emotion:   情绪分析结果 {"emotion":"焦虑","score":0.87,...}
        knowledge: RAG 检索到的知识点 [{"title":"...","content":"..."}, ...]
        history:   最近 N 轮对话 [{"role":"user","content":"..."}, ...]

    返回:
        千问的回复文本
    """
    from prompts.templates import SYSTEM_PROMPT, build_chat_prompt

    prompt = build_chat_prompt(
        user_message=message,
        emotion=emotion,
        knowledge=knowledge,
        history=history,
    )

    try:
        resp = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512,
                },
            },
            timeout=settings.OLLAMA_TIMEOUT,
        )

        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", "").strip()

        return f"[Ollama 返回错误: {resp.status_code}]"

    except requests.exceptions.ConnectionError:
        return "抱歉，AI 服务暂时不可用，请稍后再试。"

    except Exception as e:
        return f"抱歉，对话出错了: {str(e)}"
