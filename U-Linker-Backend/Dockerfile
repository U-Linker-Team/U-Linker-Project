# 使用 Python 3.11 官方镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录（容器内的项目目录）
WORKDIR /app

# 设置环境变量
# PYTHONDONTWRITEBYTECODE=1: 防止 Python 生成 .pyc 文件
# PYTHONUNBUFFERED=1: 让 Python 输出直接显示，不缓冲
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

# 替换 Debian 源为国内镜像（加速 apt-get 下载）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm main" > /etc/apt/sources.list || true

# 安装系统依赖（MySQL 客户端库等）
# --no-install-recommends: 不安装推荐包，减小镜像体积
# && rm -rf /var/lib/apt/lists/*: 清理 apt 缓存，减小镜像体积
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 设置时区为 Asia/Shanghai（中国时区）
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制依赖文件（先复制依赖文件可以利用 Docker 缓存层）
COPY requirements.txt .

# 配置 pip 使用国内镜像源（加速 Python 包下载）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.timeout 300 && \
    pip config set global.retries 5

# 安装 Python 依赖
# --no-cache-dir: 不缓存 pip 下载的包，减小镜像体积
# --default-timeout=300: 设置超时时间为 300 秒
RUN pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# 复制项目文件到容器
COPY . .

# 创建必要的目录（确保目录存在）
RUN mkdir -p uploads instance

# 暴露端口（Flask 运行在 8000 端口）
EXPOSE 8000

# 启动命令（使用 gunicorn 作为生产服务器）
# --bind: 绑定地址和端口
# --workers: 工作进程数（建议为 CPU 核心数 * 2 + 1）
# --timeout: 请求超时时间（秒）
# --access-logfile -: 输出访问日志到标准输出
# --error-logfile -: 输出错误日志到标准错误
# app:create_app(): 应用工厂函数（gunicorn 会自动调用）
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:create_app()"]


