"""FastAPI 应用入口"""

from app.bootstrap.app_factory import create_app

# 创建应用实例
app = create_app()
