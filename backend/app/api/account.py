from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.deps import get_current_user
from backend.app.models.models import User
from backend.app.schemas.schemas import UserOut
from backend.app.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/api/account", tags=["account"])


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6, max_length=128)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.post("/change-password")
def change_password(body: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.hashed_password = get_password_hash(body.new_password)
    db.commit()
    return {"ok": True, "detail": "密码修改成功"}
