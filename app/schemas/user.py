"""用户 Schema"""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema, IDMixin, TimestampMixin


# ========== 请求 Schema ==========


class UserCreate(BaseModel):
    """创建用户请求"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: str | None = Field(None, max_length=100, description="昵称")


class UserUpdate(BaseModel):
    """更新用户请求"""

    nickname: str | None = Field(None, max_length=100, description="昵称")
    is_active: bool | None = Field(None, description="是否激活")


class UserPasswordUpdate(BaseModel):
    """修改密码请求"""

    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


# ========== 响应 Schema ==========


class UserResponse(IDMixin, TimestampMixin, BaseSchema):
    """用户响应"""

    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    nickname: str | None = Field(None, description="昵称")
    is_active: bool = Field(..., description="是否激活")
    is_superuser: bool = Field(..., description="是否超级管理员")


class UserBrief(IDMixin, BaseSchema):
    """用户简要信息"""

    username: str = Field(..., description="用户名")
    nickname: str | None = Field(None, description="昵称")
