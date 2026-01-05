"""Repository 基类"""

from datetime import datetime
from typing import Any, Generic, Sequence, TypeVar

from pydantic import BaseModel as PydanticModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Repository 基类，提供通用 CRUD 操作"""

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    def _base_query(self, include_deleted: bool = False) -> Select[tuple[ModelType]]:
        """基础查询（默认排除软删除记录）"""
        query = select(self.model)
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)  # noqa: E712
        return query

    async def get(
        self,
        id: int,
        include_deleted: bool = False,
    ) -> ModelType | None:
        """根据 ID 获取单条记录"""
        query = self._base_query(include_deleted).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(
        self,
        ids: list[int],
        include_deleted: bool = False,
    ) -> Sequence[ModelType]:
        """根据 ID 列表获取多条记录"""
        query = self._base_query(include_deleted).where(self.model.id.in_(ids))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[ModelType]:
        """获取多条记录（分页）"""
        query = (
            self._base_query(include_deleted)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(
        self,
        include_deleted: bool = False,
    ) -> Sequence[ModelType]:
        """获取所有记录"""
        query = self._base_query(include_deleted).order_by(self.model.id.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count(
        self,
        include_deleted: bool = False,
    ) -> int:
        """统计记录数"""
        query = select(func.count()).select_from(self.model)
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)  # noqa: E712
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """创建记录"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def create_many(self, objs_in: list[CreateSchemaType]) -> list[ModelType]:
        """批量创建记录"""
        db_objs = [
            self.model(**obj_in.model_dump(exclude_unset=True)) for obj_in in objs_in
        ]
        self.session.add_all(db_objs)
        await self.session.flush()
        for obj in db_objs:
            await self.session.refresh(obj)
        return db_objs

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """更新记录"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int, soft: bool = True) -> bool:
        """删除记录（默认软删除）"""
        db_obj = await self.get(id)
        if db_obj is None:
            return False

        if soft:
            db_obj.is_deleted = True
            db_obj.deleted_at = datetime.now()
            await self.session.flush()
        else:
            await self.session.delete(db_obj)
            await self.session.flush()

        return True

    async def restore(self, id: int) -> ModelType | None:
        """恢复软删除的记录"""
        db_obj = await self.get(id, include_deleted=True)
        if db_obj is None or not db_obj.is_deleted:
            return None

        db_obj.is_deleted = False
        db_obj.deleted_at = None
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def exists(self, id: int, include_deleted: bool = False) -> bool:
        """检查记录是否存在"""
        query = select(func.count()).select_from(self.model).where(self.model.id == id)
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)  # noqa: E712
        result = await self.session.execute(query)
        return (result.scalar() or 0) > 0

    async def filter_by(
        self,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> Sequence[ModelType]:
        """根据条件过滤"""
        query = self._base_query(include_deleted)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def first_by(
        self,
        include_deleted: bool = False,
        **kwargs: Any,
    ) -> ModelType | None:
        """根据条件获取第一条记录"""
        query = self._base_query(include_deleted)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none()
