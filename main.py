"""FastAPI 应用入口（简化版）"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import init_logger, logger
from app.database import init_db, close_db
from client.redis import get_redis_client, close_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    init_logger()
    logger.info(f"启动应用: {settings.APP_NAME}")

    # 初始化数据库
    await init_db()

    # 初始化 Redis（可选）
    if settings.REDIS_URL:
        await get_redis_client()

    yield

    # 关闭时
    logger.info("关闭应用...")
    await close_db()
    await close_redis_client()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    # 健康检查
    @app.get("/health", tags=["Health"])
    async def health_check():
        """健康检查"""
        return {"status": "healthy", "app": settings.APP_NAME}

    # 注册路由
    from app.api import router as api_router

    app.include_router(api_router, prefix="/api")

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
