from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.models.models import Article, Tag


def _ensure_tags(db: Session, names: Optional[List[str]]) -> List[Tag]:
    if not names:
        return []
    tags: List[Tag] = []
    for name in {n.strip() for n in names if n.strip()}:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def list_articles(
    db: Session,
    *,
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    author_id: Optional[int] = None,
    page: int = 1,
    size: int = 10,
) -> Tuple[List[Article], int]:
    q = db.query(Article)

    if keyword:
        like = f"%{keyword}%"
        q = q.filter(or_(Article.title.like(like), Article.content_md.like(like)))

    if tag:
        q = q.filter(Article.tags.any(Tag.name == tag))

    if author_id is not None:
        q = q.filter(Article.author_id == author_id)

    total = q.count()
    items = (
        q.order_by(Article.updated_at.desc(), Article.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return items, total


def get_article(db: Session, article_id: int) -> Optional[Article]:
    return db.query(Article).filter(Article.id == article_id).first()


def create_article(db: Session, *, title: str, content_md: str, author_id: int, tags: Optional[List[str]] = None, summary: Optional[str] = None) -> Article:
    article = Article(title=title, content_md=content_md, author_id=author_id, summary=summary or content_md[:180])
    article.tags = _ensure_tags(db, tags)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def update_article(
    db: Session,
    article: Article,
    *,
    title: Optional[str] = None,
    content_md: Optional[str] = None,
    summary: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Article:
    if title is not None:
        article.title = title
    if content_md is not None:
        article.content_md = content_md
    if summary is not None:
        article.summary = summary
    elif content_md is not None and not summary:
        article.summary = content_md[:180]
    if tags is not None:
        article.tags = _ensure_tags(db, tags)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: Article) -> None:
    db.delete(article)
    db.commit()
