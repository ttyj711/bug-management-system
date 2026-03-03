# Git拉取 → Docker镜像构建 → 宿主机部署流程

本指南详细说明如何实现从Git仓库拉取代码、构建Docker镜像到最终在宿主机上部署的完整流程。

## 一、准备工作

### 1. 环境要求

- **宿主机**：安装Docker和Docker Compose
- **Git仓库**：代码托管在GitHub、GitLab或其他Git服务
- **CI/CD工具**：（可选）GitHub Actions、GitLab CI等

### 2. 宿主机环境配置

在宿主机上安装必要的工具：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y git docker.io docker-compose

# CentOS/RHEL
sudo yum install -y git docker docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到docker组（避免使用sudo）
sudo usermod -aG docker $USER
newgrp docker
```

## 二、手动部署流程

### 1. 从Git拉取代码

```bash
# 克隆仓库
cd /path/to/deploy
git clone https://github.com/your-username/bug-management-system.git
cd bug-management-system

# 切换到指定分支（可选）
git checkout main
```

### 2. 构建Docker镜像

```bash
# 构建镜像
docker-compose build

# 或使用缓存构建
docker-compose build --no-cache
```

### 3. 启动服务

```bash
# 启动容器
docker-compose up -d

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 数据库初始化（首次部署）

```bash
# 进入后端容器
docker exec -it bug-management-backend bash

# 运行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 退出容器
exit
```

### 5. 验证部署

- 访问前端应用：`http://宿主机IP`
- 访问后端API：`http://宿主机IP:8000/api`

## 三、自动化部署流程

### 1. GitHub Actions配置

在项目根目录创建 `.github/workflows/deploy.yml` 文件：

```yaml
name: Deploy to Server

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push backend image
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: your-username/bug-management-backend:latest

      - name: Build and push frontend image
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: your-username/bug-management-frontend:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.7
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          password: ${{ secrets.SERVER_PASSWORD }}
          script: |
            cd /path/to/bug-management-system
            git pull origin main
            docker-compose pull
            docker-compose up -d
            docker-compose logs -f --tail=10
```

### 2. 配置GitHub Secrets

在GitHub仓库的 `Settings > Secrets and variables > Actions` 中添加以下 secrets：

- `DOCKER_USERNAME`：Docker Hub用户名
- `DOCKER_PASSWORD`：Docker Hub密码
- `SERVER_HOST`：宿主机IP地址
- `SERVER_USER`：宿主机用户名
- `SERVER_PASSWORD`：宿主机密码

### 3. 宿主机自动部署脚本

在宿主机上创建部署脚本 `deploy.sh`：

```bash
#!/bin/bash

# 部署脚本

# 进入项目目录
cd /path/to/bug-management-system

# 拉取最新代码
echo "拉取最新代码..."
git pull origin main

# 停止并移除旧容器
echo "停止旧容器..."
docker-compose down

# 拉取最新镜像
echo "拉取最新镜像..."
docker-compose pull

# 启动服务
echo "启动服务..."
docker-compose up -d

# 查看状态
echo "查看服务状态..."
docker-compose ps

echo "部署完成！"
```

## 四、持续集成/持续部署（CI/CD）最佳实践

### 1. 分支管理策略

- **main**：主分支，用于生产部署
- **develop**：开发分支，用于集成测试
- **feature/***：特性分支，用于开发新功能
- **hotfix/***：热修复分支，用于紧急修复

### 2. 构建优化

- **多阶段构建**：减少镜像大小
- **缓存利用**：加速构建过程
- **镜像分层**：优化镜像结构

### 3. 部署策略

- **蓝绿部署**：零 downtime 部署
- **滚动更新**：逐步替换容器
- **健康检查**：确保服务正常运行

### 4. 监控与日志

- **容器监控**：使用 Prometheus + Grafana
- **日志管理**：使用 ELK Stack 或 Loki
- **告警机制**：配置邮件或短信告警

## 五、常见问题与解决方案

### 1. 权限问题

**问题**：Docker命令需要sudo
**解决方案**：将用户添加到docker组

### 2. 网络问题

**问题**：容器间通信失败
**解决方案**：检查网络配置，确保使用正确的网络名称

### 3. 镜像拉取失败

**问题**：Docker Hub拉取速度慢
**解决方案**：使用国内镜像源或私有镜像仓库

### 4. 数据库连接问题

**问题**：容器重启后数据丢失
**解决方案**：使用持久化卷或外部数据库

### 5. CI/CD构建失败

**问题**：构建过程中依赖安装失败
**解决方案**：检查网络连接，使用国内镜像源

## 六、完整部署流程图

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Git 提交代码  │────►│ GitHub Actions │────►│  构建Docker镜像  │
└────────────────┘     └────────────────┘     └────────────────┘
                                                │
                                                ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  宿主机部署    │◄────│  推送镜像到仓库  │◄────│  推送Docker镜像  │
└────────────────┘     └────────────────┘     └────────────────┘
        │
        ▼
┌────────────────┐     ┌────────────────┐
│  启动容器服务  │────►│  验证服务状态  │
└────────────────┘     └────────────────┘
```

## 七、生产环境部署建议

1. **使用私有镜像仓库**：提高拉取速度和安全性
2. **配置环境变量**：使用 `.env` 文件或Docker secrets管理敏感信息
3. **启用HTTPS**：使用Let's Encrypt或商业SSL证书
4. **设置防火墙**：限制只允许必要的端口访问
5. **实现备份策略**：定期备份数据库和重要数据
6. **监控系统状态**：使用监控工具实时监控服务状态
7. **自动化测试**：在部署前运行自动化测试

## 八、总结

通过本指南，您可以实现从Git代码拉取到Docker容器部署的完整流程，无论是手动部署还是自动化CI/CD部署。这种部署方式具有以下优势：

- **环境一致性**：确保开发、测试和生产环境一致
- **部署速度快**：使用Docker镜像快速部署
- **可扩展性强**：易于水平扩展和负载均衡
- **回滚简单**：出现问题时可以快速回滚到之前的版本
- **维护成本低**：容器化管理减少了环境配置的复杂性

通过合理的CI/CD配置和部署策略，您可以实现项目的快速迭代和稳定运行。
