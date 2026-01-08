"""
HTTP 访问日志中间件

功能：
1. 为每个请求生成唯一的 request_id
2. 记录请求和响应的详细信息
3. 计算请求处理耗时
4. 与现有日志系统无缝集成
"""

from __future__ import annotations

import time
import uuid
from contextvars import ContextVar
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logger import get_logger

# 请求上下文变量（用于在异步环境中传递 request_id）
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

# 访问日志 logger
access_logger = get_logger("access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    HTTP 访问日志中间件

    功能：
    1. 生成唯一的 request_id
    2. 记录请求方法、路径、查询参数
    3. 记录响应状态码
    4. 记录请求处理耗时
    5. 记录客户端 IP 地址
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """处理每个 HTTP 请求"""

        # 1. 生成 request_id
        request_id = self._generate_request_id()

        # 2. 将 request_id 绑定到日志上下文
        # 这样整个请求周期内的所有日志都会自动带上 request_id
        with access_logger.contextualize(request_id=request_id):
            # 同时设置到 contextvar，供业务代码直接访问
            request_id_ctx.set(request_id)

            # 3. 记录请求开始时间
            start_time = time.time()

            # 4. 提取请求信息
            method = request.method
            path = request.url.path
            query_params = str(request.url.query) if request.url.query else ""
            client_ip = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "unknown")

            # 5. 记录请求开始日志
            access_logger.info(
                "Request started | method={} path={} query={} client_ip={} user_agent={}",
                method,
                path,
                query_params,
                client_ip,
                user_agent,
            )

            try:
                # 6. 调用下一个中间件或路由处理器
                response = await call_next(request)

                # 7. 计算处理耗时
                process_time = time.time() - start_time

                # 8. 记录请求完成日志
                access_logger.info(
                    "Request completed | method={} path={} status={} duration={:.3f}ms client_ip={}",
                    method,
                    path,
                    response.status_code,
                    process_time * 1000,  # 转换为毫秒
                    client_ip,
                )

                # 9. 在响应头中返回 request_id
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as e:
                # 10. 异常处理
                process_time = time.time() - start_time

                access_logger.error(
                    "Request failed | method={} path={} error={} duration={:.3f}ms client_ip={} | {}",
                    method,
                    path,
                    type(e).__name__,
                    process_time * 1000,
                    client_ip,
                    str(e),
                )

                # 返回标准错误响应
                return JSONResponse(
                    status_code=500,
                    content={
                        "message": "Internal Server Error",
                        "request_id": request_id,
                    },
                    headers={"X-Request-ID": request_id},
                )

    def _generate_request_id(self) -> str:
        """
        生成唯一的 request_id

        格式：{时间戳前8位}-{UUID前8位}
        例如：20250108-a1b2c3d4
        """
        timestamp_hex = hex(int(time.time()))[2:10]  # 时间戳的后8位
        uuid_str = str(uuid.uuid4()).split("-")[0]    # UUID 的前8位

        return f"{timestamp_hex}-{uuid_str}"

    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实 IP 地址

        优先级：
        1. X-Forwarded-For 头（代理场景）
        2. X-Real-IP 头（Nginx 代理）
        3. 直接连接的客户端 IP
        """
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For 可能包含多个 IP，取第一个
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # 直接连接的客户端 IP
        if request.client:
            return request.client.host

        return "unknown"


# 辅助函数：获取当前请求的 request_id
def get_request_id() -> str:
    """
    获取当前请求的 request_id

    用法：
        from app.core.middleware import get_request_id

        request_id = get_request_id()
    """
    return request_id_ctx.get("")


# 辅助函数：为现有 logger 绑定 request_id
def bind_request_id(logger):
    """
    为现有 logger 绑定当前请求的 request_id

    用法：
        from app.core.logger import get_logger
        from app.core.middleware import bind_request_id

        logger = get_logger("service.user")
        logger = bind_request_id(logger)
        logger.info("这条日志会自动带上 request_id")
    """
    request_id = get_request_id()
    if request_id:
        return logger.bind(request_id=request_id)
    return logger
