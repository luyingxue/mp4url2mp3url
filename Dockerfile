FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 创建static目录
RUN mkdir -p /app/static

# 复制项目文件
COPY requirements.txt .
COPY main.py .
COPY static/index.html static/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir moviepy

# 验证moviepy安装
RUN python -c "import moviepy.editor; print('moviepy installed successfully')"

# 设置权限
RUN chmod -R 755 /app/static

# 暴露端口
EXPOSE 8000

# 使用shell形式的CMD以便能看到更多错误信息
CMD python -c "import main; print('Main module imported successfully')" && \
    uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug 