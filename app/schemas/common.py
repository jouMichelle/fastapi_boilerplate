"""通用 Pydantic Schema"""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Schema 基类"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class IDMixin(BaseModel):
    """ID Mixin"""

    id: int = Field(description="主键ID")


class TimestampMixin(BaseModel):
    """时间戳 Mixin"""

    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class SoftDeleteMixin(BaseModel):
    """软删除 Mixin"""

    is_deleted: bool = Field(default=False, description="是否已删除")
    deleted_at: datetime | None = Field(default=None, description="删除时间")


class PageRequest(BaseModel):
    """分页请求"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页大小")

    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size


class PageInfo(BaseModel):
    """分页信息"""

    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total_pages: int = Field(description="总页数")

    @classmethod
    def create(cls, total: int, page: int, page_size: int) -> "PageInfo":
        """创建分页信息"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(total=total, page=page, page_size=page_size, total_pages=total_pages)


class PageData(BaseModel, Generic[T]):
    """分页数据"""

    items: list[T] = Field(description="数据列表")
    page_info: PageInfo = Field(description="分页信息")


class IDResponse(IDMixin, TimestampMixin, BaseSchema):
    """包含 ID 和时间戳的响应基类"""

    pass


class SuccessResponse(BaseModel):
    """成功响应"""

    code: int = Field(default=0, description="状态码")
    message: str = Field(default="success", description="消息")


class DeleteResponse(SuccessResponse):
    """删除响应"""

    deleted_id: int = Field(description="被删除的ID")
