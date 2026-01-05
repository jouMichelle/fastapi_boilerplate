"""自定义异常类"""

from typing import Any

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """API 异常基类"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"
    code: int = 50000

    def __init__(
        self,
        detail: str | None = None,
        code: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=headers,
        )
        self.code = code or self.code


class BadRequestError(BaseAPIException):
    """400 错误请求"""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"
    code = 40000


class UnauthorizedError(BaseAPIException):
    """401 未授权"""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Unauthorized"
    code = 40100

    def __init__(
        self,
        detail: str | None = None,
        code: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        headers = headers or {"WWW-Authenticate": "Bearer"}
        super().__init__(detail=detail, code=code, headers=headers)


class ForbiddenError(BaseAPIException):
    """403 禁止访问"""

    status_code = status.HTTP_403_FORBIDDEN
    detail = "Forbidden"
    code = 40300


class NotFoundError(BaseAPIException):
    """404 资源不存在"""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"
    code = 40400


class ConflictError(BaseAPIException):
    """409 资源冲突"""

    status_code = status.HTTP_409_CONFLICT
    detail = "Resource conflict"
    code = 40900


class ValidationError(BaseAPIException):
    """422 验证错误"""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"
    code = 42200

    def __init__(
        self,
        detail: str | None = None,
        code: int | None = None,
        errors: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(detail=detail, code=code, headers=headers)
        self.errors = errors or []


class RateLimitError(BaseAPIException):
    """429 请求过于频繁"""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many requests"
    code = 42900


class InternalServerError(BaseAPIException):
    """500 服务器内部错误"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"
    code = 50000


class ServiceUnavailableError(BaseAPIException):
    """503 服务不可用"""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Service unavailable"
    code = 50300
