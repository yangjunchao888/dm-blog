import os
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.models.models import User
from backend.app.core.config import settings

try:
    import jwt
except Exception:  # pragma: no cover
    jwt = None  # type: ignore[assignment]

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="未登录")

    token = credentials.credentials

    username: Optional[str] = None
    if jwt is not None and token.count(".") == 2:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            username = payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="登录已过期")
        except Exception:
            raise HTTPException(status_code=401, detail="登录凭证无效")
    else:
        # 兼容简易 token
        if token.startswith("token-"):
            username = token.split("-", 1)[1]

    if not username:
        raise HTTPException(status_code=401, detail="登录凭证无效")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user
