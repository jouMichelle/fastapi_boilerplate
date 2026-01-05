"""用户 Repository"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.dal.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """用户数据访问层"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        query = self._base_query().where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        query = self._base_query().where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        user = await self.get_by_username(username)
        return user is not None

    async def email_exists(self, email: str) -> bool:
        """检查邮箱是否存在"""
        user = await self.get_by_email(email)
        return user is not None
