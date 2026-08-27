from fastapi import APIRouter, Depends
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.models.models import Tag, article_tags
from backend.app.schemas.schemas import TagOut

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)):
    tags = (
        db.query(Tag)
        .join(article_tags, article_tags.c.tag_id == Tag.id)
        .group_by(Tag.id)
        .order_by(Tag.name)
        .all()
    )
    return [TagOut.model_validate(t) for t in tags]
