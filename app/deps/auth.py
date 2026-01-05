"""认证依赖注入"""

from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import verify_access_token

# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


async def get_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """获取并验证 JWT Token，返回 payload"""
    if credentials is None:
        raise UnauthorizedError(detail="Missing authentication token")

    token = credentials.credentials
    payload = verify_access_token(token)
    return payload


async def get_current_user_id(
    payload: dict[str, Any] = Depends(get_token_payload),
) -> int:
    """从 token 获取当前用户 ID"""
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError(detail="Invalid token payload")
    return int(user_id)


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> int | None:
    """可选的用户认证，未登录返回 None"""
    if credentials is None:
        return None

    try:
        payload = verify_access_token(credentials.credentials)
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except Exception:
        return None


class RoleChecker:
    """角色检查器"""

    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        payload: dict[str, Any] = Depends(get_token_payload),
    ) -> dict[str, Any]:
        """检查用户角色"""
        user_role = payload.get("role", "")
        if user_role not in self.allowed_roles:
            raise ForbiddenError(detail="Insufficient permissions")
        return payload


# 类型别名
TokenPayload = Annotated[dict[str, Any], Depends(get_token_payload)]
CurrentUserId = Annotated[int, Depends(get_current_user_id)]
OptionalUserId = Annotated[int | None, Depends(get_optional_user_id)]

# 角色检查器实例
require_admin = RoleChecker(["admin"])
require_user = RoleChecker(["user", "admin"])
