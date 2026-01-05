"""统一响应格式"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ResponseModel(BaseModel, Generic[DataT]):
    """通用响应模型"""

    code: int = Field(default=0, description="业务状态码，0表示成功")
    message: str = Field(default="success", description="响应消息")
    data: DataT | None = Field(default=None, description="响应数据")


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


class PageResponse(ResponseModel[list[DataT]], Generic[DataT]):
    """分页响应模型"""

    page_info: PageInfo = Field(description="分页信息")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    code: int = Field(description="错误码")
    message: str = Field(description="错误消息")
    detail: str | None = Field(default=None, description="详细错误信息")


def success(data: Any = None, message: str = "success") -> dict[str, Any]:
    """成功响应"""
    response = ResponseModel(code=0, message=message, data=data)
    return response.model_dump(mode="json")


def error(code: int, message: str, detail: str | None = None) -> ErrorResponse:
    """错误响应"""
    return ErrorResponse(code=code, message=message, detail=detail)


def paginate(
    data: list[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "success",
) -> PageResponse[Any]:
    """分页响应"""
    page_info = PageInfo.create(total=total, page=page, page_size=page_size)
    return PageResponse(code=0, message=message, data=data, page_info=page_info)
