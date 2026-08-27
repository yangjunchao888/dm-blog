from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.deps import get_current_user
from backend.app.api._auth_utils import _resolve_user_from_header
from backend.app.core.config import settings
from backend.app.models.models import User
from backend.app.schemas.schemas import ArticleCreate, ArticleOut, ArticleUpdate
from backend.app.services import article_service

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=dict)
def list_articles(
    keyword: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    mine: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    author_id: Optional[int] = None
    if mine:
        user = _resolve_user_from_header(db, authorization)
        if not user:
            raise HTTPException(status_code=401, detail="未登录")
        author_id = user.id

    items, total = article_service.list_articles(db, keyword=keyword, tag=tag, page=page, size=size, author_id=author_id)
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": [ArticleOut.model_validate(i).model_dump() for i in items],
    }


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ArticleOut.model_validate(article)


@router.post("", response_model=ArticleOut, status_code=201)
def create_article(body: ArticleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    article = article_service.create_article(
        db, title=body.title, content_md=body.content_md, author_id=current_user.id, tags=body.tags
    )
    return ArticleOut.model_validate(article)


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(article_id: int, body: ArticleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    updated = article_service.update_article(db, article, title=body.title, content_md=body.content_md, tags=body.tags)
    return ArticleOut.model_validate(updated)


@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该文章")
    article_service.delete_article(db, article)
    return {"ok": True}
