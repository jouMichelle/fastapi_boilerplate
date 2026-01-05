"""路由注册"""

from fastapi import APIRouter, FastAPI

from app.core.config import settings

# 创建 API 路由器
api_router = APIRouter()


def register_routers(app: FastAPI) -> None:
    """注册所有路由"""

    # 健康检查端点
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """健康检查"""
        return {"status": "healthy", "app": settings.APP_NAME}

    # API v1 路由
    from app.api.v1.user.router import router as user_router

    api_router.include_router(user_router, prefix="/users", tags=["Users"])

    # 注册 API 路由
    app.include_router(api_router, prefix="/api/v1")
