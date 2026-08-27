import logging
import os
import secrets

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.db import Base, engine, SessionLocal
from backend.app.models.models import User
from backend.app.core.security import get_password_hash
from backend.app.api import auth as auth_api
from backend.app.api import articles as articles_api
from backend.app.api import chat as chat_api
from backend.app.api import tags as tags_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("dm-blog")

app = FastAPI(title=settings.PROJECT_NAME, default_response_class=JSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api.router)
app.include_router(articles_api.router)
app.include_router(tags_api.router)
app.include_router(chat_api.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if not admin:
            password = settings.ADMIN_PASSWORD or secrets.token_urlsafe(12)
            admin = User(
                username=settings.ADMIN_USERNAME,
                nickname="管理员",
                hashed_password=get_password_hash(password),
            )
            db.add(admin)
            db.commit()
            logger.info("已创建默认管理员账号：%s / %s", settings.ADMIN_USERNAME, password)
        else:
            logger.info("默认管理员账号已存在：%s", settings.ADMIN_USERNAME)
    finally:
        db.close()
