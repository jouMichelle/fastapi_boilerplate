"""中间件注册"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.http_middleware.access_log import AccessLogMiddleware
from app.http_middleware.request_id import RequestIDMiddleware
from app.http_middleware.security_headers import SecurityHeadersMiddleware


def register_middleware(app: FastAPI) -> None:
    """注册所有中间件"""

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    # 安全响应头中间件
    app.add_middleware(SecurityHeadersMiddleware)

    # 访问日志中间件
    app.add_middleware(AccessLogMiddleware)

    # 请求 ID 中间件（最先执行，最后响应）
    app.add_middleware(RequestIDMiddleware)
