"""FastAPI 应用工厂"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.bootstrap.lifespan import lifespan
from app.bootstrap.register_middleware import register_middleware
from app.bootstrap.router import register_routers
from app.core.config import settings
from app.core.exceptions import BaseAPIException
from app.core.logger import get_logger
from app.core.response import error

logger = get_logger("bootstrap.app_factory")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="FastAPI Boilerplate with Layered Architecture",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    register_middleware(app)
    register_routers(app)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(
        request: Request,
        exc: BaseAPIException,
    ) -> JSONResponse:
        """处理自定义 API 异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content=error(
                code=exc.code,
                message=exc.detail,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """处理未捕获的异常"""
        logger.exception("Unhandled exception: {}", str(exc))

        detail = str(exc) if settings.DEBUG else "Internal server error"
        return JSONResponse(
            status_code=500,
            content=error(
                code=50000,
                message="Internal server error",
                detail=detail,
            ).model_dump(),
        )
