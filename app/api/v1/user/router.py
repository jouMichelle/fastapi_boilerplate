"""用户 API 路由"""

from fastapi import APIRouter, Query

from app.core.exceptions import ForbiddenError
from app.core.response import success
from app.deps.auth import CurrentUserId
from app.deps.db import DbSession
from app.schemas.common import DeleteResponse, PageData, PageInfo
from app.schemas.user import (
    UserBrief,
    UserCreate,
    UserPasswordUpdate,
    UserResponse,
    UserUpdate,
)
from app.services.user.service import UserService

router = APIRouter()


@router.post("", response_model=dict, summary="创建用户")
async def create_user(
    data: UserCreate,
    session: DbSession,
):
    """创建新用户（注册，公开接口）"""
    service = UserService(session)
    user = await service.create_user(data)
    await session.commit()
    return success(data=UserResponse.model_validate(user))


@router.get("", response_model=dict, summary="获取用户列表")
async def list_users(
    session: DbSession,
    current_user_id: CurrentUserId,  # 需要登录
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
):
    """获取用户列表（分页，需要登录）"""
    service = UserService(session)
    skip = (page - 1) * page_size
    users, total = await service.list_users(skip=skip, limit=page_size)

    items = [UserBrief.model_validate(u) for u in users]
    page_info = PageInfo.create(total=total, page=page, page_size=page_size)

    return success(data=PageData(items=items, page_info=page_info))


@router.get("/me", response_model=dict, summary="获取当前用户信息")
async def get_current_user(
    session: DbSession,
    current_user_id: CurrentUserId,  # 需要登录
):
    """获取当前登录用户信息"""
    service = UserService(session)
    user = await service.get_user(current_user_id)
    return success(data=UserResponse.model_validate(user))


@router.get("/{user_id}", response_model=dict, summary="获取用户详情")
async def get_user(
    user_id: int,
    session: DbSession,
    current_user_id: CurrentUserId,  # 需要登录
):
    """获取单个用户详情（需要登录）"""
    service = UserService(session)
    user = await service.get_user(user_id)
    return success(data=UserResponse.model_validate(user))


@router.put("/{user_id}", response_model=dict, summary="更新用户")
async def update_user(
    user_id: int,
    data: UserUpdate,
    session: DbSession,
    current_user_id: CurrentUserId,  # 需要登录
):
    """更新用户信息（只能修改自己）"""
    # 权限检查：只能修改自己
    if user_id != current_user_id:
        raise ForbiddenError(detail="只能修改自己的信息")

    service = UserService(session)
    user = await service.update_user(user_id, data)
    await session.commit()
    return success(data=UserResponse.model_validate(user))


@router.put("/{user_id}/password", response_model=dict, summary="修改密码")
async def update_password(
    user_id: int,
    data: UserPasswordUpdate,
    session: DbSession,
    current_user_id: CurrentUserId,  # 需要登录
):
    """修改用户密码（只能修改自己）"""
    # 权限检查：只能修改自己的密码
    if user_id != current_user_id:
        raise ForbiddenError(detail="只能修改自己的密码")

    service = UserService(session)
    await service.update_password(user_id, data)
    await session.commit()
    return success(message="密码修改成功")


@router.delete("/{user_id}", response_model=dict, summary="删除用户")
async def delete_user(
    user_id: int,
    session: DbSession,
    current_user_id: CurrentUserId,  # 需要登录
):
    """删除用户（只能删除自己，软删除）"""
    # 权限检查：只能删除自己
    if user_id != current_user_id:
        raise ForbiddenError(detail="只能删除自己的账号")

    service = UserService(session)
    await service.delete_user(user_id)
    await session.commit()
    return success(data=DeleteResponse(deleted_id=user_id))
