"""安全相关功能：JWT、密码哈希等"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import UnauthorizedError

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """解码令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise UnauthorizedError(detail=f"Invalid token: {e}") from e


def verify_access_token(token: str) -> dict[str, Any]:
    """验证访问令牌"""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedError(detail="Invalid access token")
    return payload


def verify_refresh_token(token: str) -> dict[str, Any]:
    """验证刷新令牌"""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError(detail="Invalid refresh token")
    return payload


class TokenPayload:
    """令牌载荷"""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.sub: str | None = payload.get("sub")
        self.exp: datetime | None = None
        self.token_type: str | None = payload.get("type")

        if exp := payload.get("exp"):
            self.exp = datetime.fromtimestamp(exp, tz=timezone.utc)

    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        if self.exp is None:
            return True
        return datetime.now(timezone.utc) > self.exp
