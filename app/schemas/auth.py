"""认证 Schema"""

from pydantic import BaseModel, EmailStr, Field


# ========== 请求 Schema ==========


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., min_length=1, description="用户名或邮箱")
    password: str = Field(..., min_length=1, description="密码")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""

    refresh_token: str = Field(..., description="刷新令牌")


class RegisterRequest(BaseModel):
    """注册请求"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: str | None = Field(None, max_length=100, description="昵称")


# ========== 响应 Schema ==========


class TokenResponse(BaseModel):
    """Token 响应"""

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(..., description="访问令牌过期时间（秒）")


class TokenData(BaseModel):
    """Token 数据（内部使用）"""

    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    is_superuser: bool = Field(default=False, description="是否超级管理员")
