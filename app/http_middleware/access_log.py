"""访问日志中间件"""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import get_logger

logger = get_logger("middleware.access_log")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """记录 HTTP 请求访问日志"""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter()

        # 获取请求信息
        request_id = getattr(request.state, "request_id", "-")
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request)

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        duration_ms = (time.perf_counter() - start_time) * 1000

        # 使用 bind 绑定 request_id，记录结构化日志
        logger.bind(
            request_id=request_id,
            client_ip=client_ip,
        ).info(
            "{} {} {} {}ms",
            method,
            path,
            response.status_code,
            round(duration_ms, 2),
        )

        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

        return response

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实 IP"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"
