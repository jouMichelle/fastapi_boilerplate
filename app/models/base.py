"""SQLAlchemy ORM 基类"""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 声明基类"""

    pass


class TimestampMixin:
    """时间戳 Mixin"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


class SoftDeleteMixin:
    """软删除 Mixin"""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="是否已删除",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        comment="删除时间",
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """业务模型基类，包含 ID、时间戳和软删除"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID",
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """自动生成表名：类名转蛇形命名"""
        import re

        name = cls.__name__
        # UserProfile -> user_profile
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """转换为字典"""
        exclude = exclude or set()
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in exclude
        }

    def soft_delete(self) -> None:
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        """恢复软删除"""
        self.is_deleted = False
        self.deleted_at = None
