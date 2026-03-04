FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# === 新增：配置阿里云 APT 镜像源 ===
# 兼容 Debian 11 (bullseye) 和 Debian 12 (bookworm) 不同格式的源文件
RUN set -ex; \
    if [ -f /etc/apt/sources.list ]; then \
        sed -i 's@http://\(deb\|security\)\.debian\.org@http://mirrors.aliyun.com@g' /etc/apt/sources.list; \
    fi; \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's@http://\(deb\|security\)\.debian\.org@http://mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources; \
    fi

# 安装 gcc (现在会从阿里云下载，速度很快)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# === 修改：pip 也使用阿里云镜像源 ===
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY . .

RUN mkdir -p /app/media

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]