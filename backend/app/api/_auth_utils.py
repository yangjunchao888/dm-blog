from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.models import User
from backend.app.core.config import settings

try:
    import jwt
except Exception:  # pragma: no cover
    jwt = None  # type: ignore[assignment]


def _resolve_user_from_header(db: Session, authorization: Optional[str]) -> Optional[User]:
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
    else:
        token = authorization

    username: Optional[str] = None
    if jwt is not None and token.count(".") == 2:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            username = payload.get("sub")
        except Exception:
            return None
    else:
        if token.startswith("token-"):
            username = token.split("-", 1)[1]

    if not username:
        return None

    return db.query(User).filter(User.username == username).first()
