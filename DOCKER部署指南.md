# Docker部署指南

本指南详细说明如何使用Docker容器化部署BUG管理系统。

## 准备工作

### 1. 安装Docker

- **Windows**：下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- **macOS**：下载并安装 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
- **Linux**：根据发行版安装Docker Engine和Docker Compose

### 2. 验证Docker环境

打开终端，执行以下命令验证Docker是否正确安装：

```bash
docker --version
docker-compose --version
```

## 构建和启动

### 1. 进入项目根目录

```bash
cd /path/to/bug-management-system
```

### 2. 构建和启动容器

使用Docker Compose构建和启动整个项目：

```bash
docker-compose up -d --build
```

### 3. 查看容器状态

```bash
docker-compose ps
```

### 4. 访问应用

- **前端应用**：访问 `http://localhost`
- **后端API**：访问 `http://localhost:8000/api`

### 5. 停止容器

```bash
docker-compose down
```

## 配置说明

### 1. 环境变量配置

在 `docker-compose.yml` 文件中，可以修改以下环境变量：

- `DEBUG`：是否开启调试模式（生产环境建议设为False）
- `SECRET_KEY`：Django密钥（生产环境建议修改为随机字符串）
- `ALLOWED_HOSTS`：允许访问的主机（生产环境建议设置为具体域名）
- `CORS_ALLOW_ALL_ORIGINS`：是否允许所有跨域请求

### 2. 端口配置

默认端口映射：
- 后端：`8000:8000`
- 前端：`80:80`

如需修改端口，可在 `docker-compose.yml` 文件中调整 `ports` 配置。

### 3. 数据持久化

- 后端代码：通过卷挂载实现实时同步
- 媒体文件：通过卷挂载实现持久化存储

## 常见问题与解决方案

### 1. 构建失败

**问题**：构建过程中出现依赖安装失败
**解决方案**：
- 检查网络连接
- 尝试使用国内镜像源
- 确保Dockerfile中的依赖版本正确

### 2. 容器启动失败

**问题**：容器启动后立即退出
**解决方案**：
- 查看容器日志：`docker-compose logs <service_name>`
- 检查端口是否被占用
- 确保环境变量配置正确

### 3. 前端无法访问后端API

**问题**：前端应用无法连接后端API
**解决方案**：
- 检查后端容器是否正常运行
- 查看Nginx配置中的API代理设置
- 检查CORS配置是否正确

### 4. 数据库初始化

**问题**：首次部署时数据库未初始化
**解决方案**：
- 进入后端容器：`docker exec -it bug-management-backend bash`
- 运行数据库迁移：`python manage.py migrate`
- 创建超级用户：`python manage.py createsuperuser`

## 生产环境部署建议

1. **使用正式的数据库**：生产环境建议使用PostgreSQL或MySQL，而不是SQLite
2. **配置HTTPS**：使用SSL证书启用HTTPS
3. **设置环境变量**：使用环境变量文件或Docker secrets管理敏感信息
4. **配置日志**：设置适当的日志级别和日志存储
5. **监控和备份**：实现容器监控和数据备份策略

## 开发环境使用

### 1. 实时代码更新

由于使用了卷挂载，修改代码后会自动同步到容器中：
- 后端：Django开发服务器会自动重启
- 前端：需要重新构建镜像或在本地开发模式下运行

### 2. 本地开发模式

如需在本地开发模式下运行前端：

```bash
# 进入前端目录
cd frontend
# 启动开发服务器
npm run dev
```

## 高级配置

### 1. 使用Docker镜像仓库

构建并推送镜像到Docker Hub：

```bash
# 构建镜像
docker build -t yourusername/bug-management-backend ./backend
docker build -t yourusername/bug-management-frontend ./frontend

# 推送镜像
docker push yourusername/bug-management-backend
docker push yourusername/bug-management-frontend
```

### 2. 多环境部署

创建不同环境的Docker Compose配置文件：
- `docker-compose.yml`：开发环境
- `docker-compose.prod.yml`：生产环境

运行特定环境：

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 总结

使用Docker容器化部署可以：
- 简化部署流程
- 确保环境一致性
- 提高系统可靠性
- 便于横向扩展

通过本指南，您可以快速将BUG管理系统部署到任何支持Docker的环境中。
