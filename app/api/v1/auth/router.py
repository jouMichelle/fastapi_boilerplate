"""认证 API 路由"""

from fastapi import APIRouter

from app.core.response import success
from app.deps.db import DbSession
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth.service import AuthService

router = APIRouter()


@router.post("/login", response_model=dict, summary="用户登录")
async def login(
    data: LoginRequest,
    session: DbSession,
):
    """用户登录

    支持用户名或邮箱登录，返回访问令牌和刷新令牌。
    """
    service = AuthService(session)
    tokens = await service.login(data)
    return success(data=tokens)


@router.post("/register", response_model=dict, summary="用户注册")
async def register(
    data: RegisterRequest,
    session: DbSession,
):
    """用户注册

    创建新用户账号，注册成功后需要登录获取令牌。
    """
    service = AuthService(session)
    user = await service.register(data)
    await session.commit()
    return success(data=UserResponse.model_validate(user), message="注册成功")


@router.post("/refresh", response_model=dict, summary="刷新令牌")
async def refresh_token(
    data: RefreshTokenRequest,
    session: DbSession,
):
    """刷新访问令牌

    使用刷新令牌获取新的访问令牌和刷新令牌。
    """
    service = AuthService(session)
    tokens = await service.refresh_tokens(data.refresh_token)
    return success(data=tokens)
