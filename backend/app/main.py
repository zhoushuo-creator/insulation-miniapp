import sys
import asyncio
from contextlib import asynccontextmanager

# Windows 上 psycopg 需要使用 SelectorEventLoop
if sys.platform == "win32":
    from selectors import SelectSelector
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.set_event_loop(asyncio.SelectorEventLoop(SelectSelector()))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException

from app.core.config import settings
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.api.v1.router import api_v1_router
from app.db.database import engine
from app.utils.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger = setup_logger()

    # 启动时：创建 pgvector 扩展
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: sync_conn.execute(
            __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector")
        ))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(
            __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        ))
    logger.info("pgvector extension verified")

    # 创建所有表（开发环境用；生产用 alembic 迁移）
    from app.db.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

    # 种子数据：分类和应用场景
    from app.db.database import AsyncSessionLocal
    from app.services.seed import run_seed
    async with AsyncSessionLocal() as session:
        await run_seed(session)
        await session.commit()
    logger.info("Seed data completed")

    yield

    # 关闭时：释放数据库连接池
    await engine.dispose()
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="保温材料智能推荐系统 API — 小程序 + 管理后台后端服务",
    lifespan=lifespan,
)

# Static files (uploads)
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册 v1 路由
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }
