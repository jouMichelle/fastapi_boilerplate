"""用户 Service"""

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.logger import get_service_logger
from app.core.security import hash_password, verify_password
from app.dal.user.repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserPasswordUpdate, UserUpdate

logger = get_service_logger("user")


class UserService:
    """用户业务逻辑层"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = UserRepository(session)

    async def create_user(self, data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if await self.repo.username_exists(data.username):
            raise BadRequestError(detail="用户名已存在")

        # 检查邮箱是否已存在
        if await self.repo.email_exists(data.email):
            raise BadRequestError(detail="邮箱已被注册")

        # 创建用户（密码加密）
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            nickname=data.nickname,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        logger.info("User created: {}", user.username)
        return user

    async def get_user(self, user_id: int) -> User:
        """获取用户"""
        user = await self.repo.get(user_id)
        if not user:
            raise NotFoundError(detail="用户不存在")
        return user

    async def get_user_by_username(self, username: str) -> User:
        """根据用户名获取用户"""
        user = await self.repo.get_by_username(username)
        if not user:
            raise NotFoundError(detail="用户不存在")
        return user

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[User], int]:
        """获取用户列表"""
        users = await self.repo.get_multi(skip=skip, limit=limit)
        total = await self.repo.count()
        return users, total

    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        """更新用户"""
        user = await self.get_user(user_id)
        user = await self.repo.update(user, data)
        logger.info("User updated: {}", user.username)
        return user

    async def update_password(
        self,
        user_id: int,
        data: UserPasswordUpdate,
    ) -> User:
        """修改密码"""
        user = await self.get_user(user_id)

        # 验证旧密码
        if not verify_password(data.old_password, user.hashed_password):
            raise BadRequestError(detail="旧密码错误")

        # 更新密码
        user.hashed_password = hash_password(data.new_password)
        await self.session.flush()
        await self.session.refresh(user)

        logger.info("User password updated: {}", user.username)
        return user

    async def delete_user(self, user_id: int) -> bool:
        """删除用户（软删除）"""
        user = await self.get_user(user_id)
        await self.repo.delete(user_id, soft=True)
        logger.info("User deleted: {}", user.username)
        return True
