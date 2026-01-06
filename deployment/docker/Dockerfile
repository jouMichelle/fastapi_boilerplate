# 生产环境 Dockerfile
# 多阶段构建，优化镜像大小

# ========== 构建阶段 ==========
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 包管理器
RUN pip install --no-cache-dir uv

# 复制依赖文件
COPY pyproject.toml ./

# 安装依赖到虚拟环境
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -e .

# ========== 运行阶段 ==========
FROM python:3.11-slim as runtime

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 设置环境变量
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production

# 创建非 root 用户
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# 复制应用代码
COPY --chown=appuser:appgroup . .

# 创建必要目录
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appgroup /app/data /app/logs

# 复制并设置启动脚本权限
COPY --chown=appuser:appgroup deployment/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
