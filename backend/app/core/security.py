from datetime import datetime, timedelta
from typing import Optional

import hashlib
import hmac
import os

from backend.app.core.config import settings

try:
    import jwt  # PyJWT
except Exception:  # pragma: no cover
    jwt = None  # type: ignore[assignment]


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return salt.hex() + ":" + dk.hex()


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt_hex, dk_hex = hashed_password.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        return hmac.compare_digest(_hash_password(password, salt), hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return _hash_password(password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    if jwt is None:
        # fallback for environments without PyJWT
        return f"token-{subject}"

    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
