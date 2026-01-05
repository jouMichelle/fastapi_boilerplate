"""认证 Service"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestError, UnauthorizedError
from app.core.logger import get_service_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.dal.user.repository import UserRepository
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

logger = get_service_logger("auth")


class AuthService:
    """认证业务逻辑层"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def authenticate(self, data: LoginRequest) -> User:
        """验证用户凭证

        支持用户名或邮箱登录
        """
        # 尝试通过用户名查找
        user = await self.user_repo.get_by_username(data.username)

        # 如果用户名未找到，尝试通过邮箱查找
        if not user:
            user = await self.user_repo.get_by_email(data.username)

        if not user:
            logger.warning("Login failed: user not found - {}", data.username)
            raise UnauthorizedError(detail="用户名或密码错误")

        # 验证密码
        if not verify_password(data.password, user.hashed_password):
            logger.warning("Login failed: invalid password - {}", data.username)
            raise UnauthorizedError(detail="用户名或密码错误")

        # 检查用户是否激活
        if not user.is_active:
            logger.warning("Login failed: user inactive - {}", data.username)
            raise UnauthorizedError(detail="用户已被禁用")

        logger.info("User authenticated: {}", user.username)
        return user

    def create_tokens(self, user: User) -> TokenResponse:
        """为用户创建访问令牌和刷新令牌"""
        # Token payload
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "is_superuser": user.is_superuser,
        }

        # 创建令牌
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # 计算过期时间（秒）
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        """用户登录

        验证凭证并返回令牌
        """
        user = await self.authenticate(data)
        tokens = self.create_tokens(user)
        logger.info("User logged in: {}", user.username)
        return tokens

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """刷新访问令牌

        验证刷新令牌并返回新的令牌对
        """
        # 验证刷新令牌
        payload = verify_refresh_token(refresh_token)

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError(detail="Invalid refresh token")

        # 获取用户
        user = await self.user_repo.get(int(user_id))
        if not user:
            raise UnauthorizedError(detail="User not found")

        if not user.is_active:
            raise UnauthorizedError(detail="User is disabled")

        # 创建新令牌
        tokens = self.create_tokens(user)
        logger.info("Tokens refreshed for user: {}", user.username)
        return tokens

    async def register(self, data: RegisterRequest) -> User:
        """用户注册"""
        # 检查用户名是否已存在
        if await self.user_repo.username_exists(data.username):
            raise BadRequestError(detail="用户名已存在")

        # 检查邮箱是否已存在
        if await self.user_repo.email_exists(data.email):
            raise BadRequestError(detail="邮箱已被注册")

        # 创建用户
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            nickname=data.nickname,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        logger.info("User registered: {}", user.username)
        return user
