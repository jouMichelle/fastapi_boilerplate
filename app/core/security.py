"""接口鉴权模块

提供简单的 API Key 验证机制，适用于小型项目的接口保护。
"""

from fastapi import Header, HTTPException, Depends, status

from app.core.config import settings


async def verify_api_key(
    x_api_key: str = Header(..., description="API 密钥"),
) -> str:
    """
    验证 API Key

    使用方式:
        @router.get("/protected", dependencies=[Depends(verify_api_key)])
        async def protected_endpoint():
            return {"message": "OK"}

    或者获取 API Key:
        @router.get("/protected")
        async def protected_endpoint(api_key: str = Depends(verify_api_key)):
            return {"api_key": api_key}
    """
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


async def verify_api_key_optional(
    x_api_key: str | None = Header(None, description="API 密钥（可选）"),
) -> str | None:
    """
    可选的 API Key 验证

    如果提供了 API Key 则验证，否则返回 None
    """
    if x_api_key is None:
        return None

    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


class APIKeyAuth:
    """API Key 认证依赖类

    支持自定义 API Key 来源（Header、Query、Cookie）

    使用方式:
        auth = APIKeyAuth(header_name="Authorization", prefix="Bearer ")

        @router.get("/protected", dependencies=[Depends(auth)])
        async def protected_endpoint():
            return {"message": "OK"}
    """

    def __init__(
        self,
        header_name: str = "X-API-Key",
        query_name: str | None = None,
        prefix: str = "",
        auto_error: bool = True,
    ):
        self.header_name = header_name
        self.query_name = query_name
        self.prefix = prefix
        self.auto_error = auto_error

    async def __call__(
        self,
        api_key_header: str | None = Header(None, alias="X-API-Key"),
    ) -> str | None:
        api_key = api_key_header

        if api_key and self.prefix:
            if api_key.startswith(self.prefix):
                api_key = api_key[len(self.prefix) :]
            elif self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"API Key must start with '{self.prefix}'",
                )

        if not api_key:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API Key is required",
                )
            return None

        if api_key != settings.API_KEY:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API Key",
                )
            return None

        return api_key


# 默认的 API Key 认证实例
api_key_auth = APIKeyAuth()
