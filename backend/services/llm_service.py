"""
LLM 服务 — 封装 Ollama 千问模型调用
"""
import logging
import requests

from config.settings import settings

logger = logging.getLogger(__name__)


def _call_ollama(prompt: str, system: str = "", temperature: float = 0.7, max_tokens: int = 512) -> str:
    """
    底层 Ollama 调用，所有上层方法共用。
    返回原始文本，出错返回空字符串。
    """
    try:
        resp = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "num_predict": max_tokens,
                },
            },
            timeout=settings.OLLAMA_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
        logger.error("Ollama 返回错误状态码 %d", resp.status_code)
        return ""
    except requests.exceptions.ConnectionError:
        logger.error("无法连接 Ollama (%s)", settings.OLLAMA_BASE_URL)
        return ""
    except requests.exceptions.Timeout:
        logger.error("Ollama 请求超时")
        return ""
    except Exception:
        logger.exception("Ollama 调用异常")
        return ""


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
    调用千问模型生成心理咨询回复。
    """
    from prompts.templates import SYSTEM_PROMPT, build_chat_prompt

    prompt = build_chat_prompt(
        user_message=message,
        emotion=emotion,
        knowledge=knowledge,
        history=history,
    )

    result = _call_ollama(
        prompt=prompt,
        system=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=512,
    )

    if not result:
        return "抱歉，AI 服务暂时不可用，请稍后再试。"
    return result


def analyze_emotion_with_qwen(text: str) -> dict:
    """
    用千问分析用户情绪，返回解析后的情绪结果。
    """
    from prompts.templates import build_emotion_analysis_prompt, parse_emotion_response

    prompt = build_emotion_analysis_prompt(text)

    raw = _call_ollama(
        prompt=prompt,
        system="你是一个精准的情绪分析工具。只返回 JSON，不要任何解释。",
        temperature=0.1,
        max_tokens=128,
    )

    if not raw:
        # 千问不可用时返回默认值
        return {"emotion": "平静", "score": 0.5}

    return parse_emotion_response(raw)
