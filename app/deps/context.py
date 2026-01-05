"""请求上下文依赖"""

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Annotated, Any
from uuid import uuid4

from fastapi import Depends, Request

# 请求上下文变量
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
_user_id_ctx: ContextVar[int | None] = ContextVar("user_id", default=None)


@dataclass
class RequestContext:
    """请求上下文"""

    request_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def set_user_id(self, user_id: int) -> None:
        """设置用户 ID"""
        self.user_id = user_id
        _user_id_ctx.set(user_id)


def get_request_id() -> str:
    """获取当前请求 ID"""
    return _request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    """设置当前请求 ID"""
    _request_id_ctx.set(request_id)


def get_user_id() -> int | None:
    """获取当前用户 ID"""
    return _user_id_ctx.get()


def set_user_id(user_id: int | None) -> None:
    """设置当前用户 ID"""
    _user_id_ctx.set(user_id)


async def get_request_context(request: Request) -> RequestContext:
    """获取请求上下文"""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    set_request_id(request_id)

    context = RequestContext(request_id=request_id)

    # 尝试从 request.state 获取用户信息
    if hasattr(request.state, "user_id"):
        context.user_id = request.state.user_id
        set_user_id(request.state.user_id)

    return context


# 类型别名
Context = Annotated[RequestContext, Depends(get_request_context)]
