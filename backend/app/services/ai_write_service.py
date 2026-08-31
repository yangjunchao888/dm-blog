import json
import logging
import urllib.request
from typing import Optional

from backend.app.core.config import settings

logger = logging.getLogger("dm-blog.ai_write")


def _call_deepseek(prompt: str, user_msg: str) -> str:
    if not settings.DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY 未配置")

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.7,
    }

    req = urllib.request.Request(
        url=f"{settings.DEEPSEEK_BASE_URL.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]


def ai_write(action: str, *, title: Optional[str] = None, content: Optional[str] = None, instruction: Optional[str] = None) -> str:
    if action == "generate":
        prompt = "你是一个技术博客写作助手。根据用户提供的标题或主题，生成一篇结构完整的技术文章（Markdown 格式）。包含引言、正文（带小标题）、总结。内容专业、简洁、有深度。"
        user_msg = instruction or f"请根据以下标题生成文章：{title}"
        return _call_deepseek(prompt, user_msg)

    if action == "polish":
        prompt = "你是一个技术博客写作助手。对用户提供的内容进行润色改写，保持原意但提升表达质量。输出纯 Markdown，不要解释。"
        user_msg = f"请润色以下内容：\n\n{content}"
        if instruction:
            user_msg += f"\n\n额外要求：{instruction}"
        return _call_deepseek(prompt, user_msg)

    if action == "summary":
        prompt = "你是一个技术博客摘要生成器。用一句自然、精炼的话概括文章核心内容，不超过50字。像给朋友介绍这篇文章一样，不要用**本文介绍了**这类套话。只输出摘要，不要解释。"
        user_msg = f"请生成摘要：\n\n{content}"
        return _call_deepseek(prompt, user_msg)

    raise ValueError(f"不支持的操作：{action}")
