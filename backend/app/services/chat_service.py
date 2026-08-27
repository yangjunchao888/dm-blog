import logging
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import urllib.request
import urllib.error

from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.models import User
from backend.app.services import article_service


@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    message: str = ""


def _keyword_intent(message: str) -> Optional[Dict[str, Any]]:
    text = message.strip()

    m = re.search(r"(?:查找|搜索|搜一下|查一下)\s*(?:文章\s*)?(.+)", text)
    if m:
        return {"action": "search_articles", "params": {"query": m.group(1).strip()}}

    if re.search(r"(?:新建|创建|新增)\s*文章", text):
        title_m = re.search(r"标题[：:]\s*(.+)", text)
        tags_m = re.search(r"标签[：:]\s*(.+)", text)
        return {
            "action": "create_article",
            "params": {
                "title": title_m.group(1).strip() if title_m else "未命名文章",
                "tags": [t.strip() for t in tags_m.group(1).split(",") if t.strip()] if tags_m else [],
            },
        }

    m = re.search(r"(?:修改|更新)\s*文章\s*(\d+)\s*(.+)?", text)
    if m:
        return {"action": "update_article", "params": {"id": int(m.group(1)), "patch_text": (m.group(2) or "").strip()}}

    return None


def _call_deepseek_chat(user_message: str) -> Optional[Dict[str, Any]]:
    if not settings.DEEPSEEK_API_KEY:
        return None

    system_prompt = (
        "你是一个博客助手。只输出JSON，不要解释。\n"
        "可选动作：search_articles, create_article, update_article, chat。\n"
        "输出格式：{\"action\":\"...\",\"params\":{...}}\n"
        "search_articles 参数：query\n"
        "create_article 参数：title,tags(数组),content_md\n"
        "update_article 参数：id,title?,tags?,content_md?\n"
        "如果没有明确操作，就返回 {\"action\":\"chat\",\"params\":{\"reply\":\"...\"}}"
    )

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.2,
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

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception as e:
        logger.warning("DeepSeek 调用失败，已回退规则解析: %s", e)
        return None


def _apply_patch_text(patch_text: str) -> Dict[str, Any]:
    patch: Dict[str, Any] = {}
    title_m = re.search(r"标题[：:]\s*(.+)", patch_text)
    tags_m = re.search(r"标签[：:]\s*(.+)", patch_text)
    content_m = re.search(r"内容[：:]\s*(.+)", patch_text, re.S)

    if title_m:
        patch["title"] = title_m.group(1).strip()
    if tags_m:
        patch["tags"] = [t.strip() for t in tags_m.group(1).split(",") if t.strip()]
    if content_m:
        patch["content_md"] = content_m.group(1).strip()
    return patch


def handle_chat_message(db: Session, current_user: User, message: str) -> Dict[str, Any]:
    intent = _call_deepseek_chat(message) or _keyword_intent(message) or {"action": "chat", "params": {"reply": "收到，我先记录你的问题。"}}

    action = intent.get("action")
    params = intent.get("params") or {}

    if action == "search_articles":
        query = params.get("query", "")
        items, total = article_service.list_articles(db, keyword=query, page=1, size=5)
        data = [
            {"id": a.id, "title": a.title, "tags": [t.name for t in a.tags]}
            for a in items
        ]
        return {"type": "tool", "action": action, "result": {"total": total, "items": data}}

    if action == "create_article":
        article = article_service.create_article(
            db,
            title=params.get("title", "未命名文章"),
            content_md=params.get("content_md", ""),
            author_id=current_user.id,
            tags=params.get("tags"),
        )
        return {
            "type": "tool",
            "action": action,
            "result": {"id": article.id, "title": article.title, "tags": [t.name for t in article.tags]},
        }

    if action == "update_article":
        article = article_service.get_article(db, int(params.get("id", 0)))
        if not article:
            return {"type": "tool", "action": action, "result": {"ok": False, "message": "文章不存在"}}
        patch = params if any(k in params for k in ("title", "content_md", "tags")) else _apply_patch_text(params.get("patch_text", ""))
        updated = article_service.update_article(
            db,
            article,
            title=patch.get("title"),
            content_md=patch.get("content_md"),
            tags=patch.get("tags"),
        )
        return {
            "type": "tool",
            "action": action,
            "result": {"id": updated.id, "title": updated.title, "updated": True},
        }

    return {"type": "chat", "reply": params.get("reply", "我在，有什么可以帮你？")}
logger = logging.getLogger("dm-blog.chat")
