"""示例 API 路由

展示如何使用 API Key 鉴权和数据库操作。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import success
from app.core.security import verify_api_key
from app.database import get_db_session

router = APIRouter()


@router.get("/")
async def get_example():
    """公开接口示例"""
    return success(data={"message": "Hello, World!"})


@router.get("/protected", dependencies=[Depends(verify_api_key)])
async def get_protected_example():
    """需要 API Key 验证的接口示例

    请求时需要在 Header 中添加: X-API-Key: your-api-key
    """
    return success(data={"message": "You have access!"})


@router.get("/db-example")
async def get_db_example(db: AsyncSession = Depends(get_db_session)):
    """数据库操作示例

    展示如何在路由中使用数据库会话。
    """
    # 示例：执行一个简单的查询
    # result = await db.execute(select(SomeModel))
    # items = result.scalars().all()

    return success(data={"message": "Database connection works!", "db_bound": db.is_active})
