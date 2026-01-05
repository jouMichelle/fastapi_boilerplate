"""请求 ID 中间件"""

from uuid import uuid4

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.deps.context import set_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求生成唯一 ID，用于分布式追踪"""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # 从请求头获取或生成新的请求 ID
        request_id = request.headers.get("X-Request-ID", str(uuid4()))

        # 设置到上下文变量
        set_request_id(request_id)

        # 存储到 request.state
        request.state.request_id = request_id

        # 使用 loguru contextualize 绑定 request_id 到整个请求生命周期
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)

        # 添加请求 ID 到响应头
        response.headers["X-Request-ID"] = request_id

        return response
