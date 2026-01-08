"""API 路由模块"""

from fastapi import APIRouter

from app.api.example import router as example_router

router = APIRouter()

# 注册示例路由
router.include_router(example_router, prefix="/example", tags=["Example"])
