"""安全响应头中间件"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """添加安全响应头"""

    # 默认安全头配置
    DEFAULT_HEADERS: dict[str, str] = {
        # 防止 MIME 类型嗅探
        "X-Content-Type-Options": "nosniff",
        # 防止点击劫持
        "X-Frame-Options": "DENY",
        # XSS 保护（旧版浏览器）
        "X-XSS-Protection": "1; mode=block",
        # 引用策略
        "Referrer-Policy": "strict-origin-when-cross-origin",
        # 权限策略
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    def __init__(
        self,
        app: object,
        headers: dict[str, str] | None = None,
        enable_hsts: bool = False,
    ) -> None:
        super().__init__(app)
        self.headers = {**self.DEFAULT_HEADERS, **(headers or {})}
        self.enable_hsts = enable_hsts

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)

        # 添加安全头
        for header, value in self.headers.items():
            response.headers[header] = value

        # HTTPS 严格传输安全（仅生产环境启用）
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response
