from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.deps import get_current_user
from backend.app.models.models import User
from backend.app.services.ai_write_service import ai_write

router = APIRouter(prefix="/api/ai", tags=["ai"])


class WriteRequest(BaseModel):
    action: str = Field(pattern="^(generate|polish|summary)$")
    title: Optional[str] = None
    content: Optional[str] = None
    instruction: Optional[str] = None


@router.post("/write")
def write(body: WriteRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if body.action == "generate" and not body.title and not body.instruction:
        raise HTTPException(status_code=400, detail="生成需要提供标题或指令")
    if body.action in ("polish", "summary") and not body.content:
        raise HTTPException(status_code=400, detail="润色和摘要需要提供内容")
    result = ai_write(body.action, title=body.title, content=body.content, instruction=body.instruction)
    return {"ok": True, "result": result}
