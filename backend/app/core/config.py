from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Project
    PROJECT_NAME: str = "保温材料智能推荐系统"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database (PostgreSQL + pgvector)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/insulation_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # DeepSeek (对话 LLM)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com"
    DEEPSEEK_CHAT_MODEL: str = "deepseek-chat"

    # 通义千问 DashScope (Embedding, 向量嵌入用)
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_EMBED_MODEL: str = "text-embedding-v3"
    DASHSCOPE_EMBED_DIMENSIONS: int = 1024

    # RAG Settings
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7

    # WeChat Mini-Program
    WX_APPID: str = ""
    WX_SECRET: str = ""

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 20

    # JWT (管理后台 + 小程序登录)
    JWT_SECRET_KEY: str = "change-me-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Admin
    ADMIN_WECHAT_IDS: List[str] = []  # 管理员微信 openid 白名单


settings = Settings()
