import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# 加载 backend/.env
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)

logger = logging.getLogger("dm-blog.config")


class Settings:
    PROJECT_NAME: str = "dm-blog"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def _validate():
    errors = []
    warnings = []

    if not Settings.SECRET_KEY:
        errors.append("SECRET_KEY 未配置")
    elif Settings.SECRET_KEY == "dev-secret-change-me":
        warnings.append("SECRET_KEY 使用了占位值，生产环境请更换")

    if not Settings.ADMIN_PASSWORD:
        errors.append("ADMIN_PASSWORD 未配置（无默认值，必须显式设置）")

    if not Settings.DEEPSEEK_API_KEY:
        warnings.append("DEEPSEEK_API_KEY 未配置，AI 聊天将使用规则兜底")

    for w in warnings:
        logger.warning(w)

    if errors:
        for e in errors:
            logger.error(e)
        raise ValueError(f"启动配置校验失败，请检查 backend/.env：{', '.join(errors)}")


_validate()
settings = Settings()
