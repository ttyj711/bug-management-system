# BUG管理系统

一个功能完整、前后端分离的BUG管理系统，用于团队内部的缺陷追踪和管理。

## 功能特性

### 📋 核心功能
- **BUG提报**：支持详细的BUG信息录入，包括标题、描述、严重程度、优先级等
- **BUG管理**：支持BUG的编辑、删除、状态流转等操作
- **状态管理**：完整的BUG生命周期管理，从新建到关闭
- **人员分配**：支持将BUG分配给特定开发人员
- **附件管理**：支持上传截图、日志等附件
- **复制BUG**：支持快速复制现有BUG，提高工作效率

### 👥 角色权限
- **超级管理员**：拥有所有权限，可管理用户、模块和BUG
- **普通管理员**：可管理用户和分配BUG
- **测试人员**：可创建和管理自己的BUG
- **开发人员**：可处理分配给自己的BUG

### 🔍 搜索筛选
- 多条件筛选：状态、严重程度、优先级、处理人、创建人
- 搜索功能：按标题或描述搜索
- 快捷筛选：我创建的、分配给我的

### 📊 数据展示
- BUG列表：清晰展示所有BUG信息
- BUG详情：完整展示BUG的所有属性和历史记录
- 字段中文显示：便于理解和操作

## 技术栈

### 后端
- **框架**：Django 3.2.22
- **API**：Django REST Framework
- **认证**：JWT (djangorestframework-simplejwt)
- **跨域**：django-cors-headers
- **数据库**：SQLite（开发环境）、MySQL（生产环境）

### 前端
- **框架**：Vue 3
- **构建工具**：Vite
- **UI组件**：Element Plus
- **状态管理**：Pinia
- **路由**：Vue Router
- **HTTP请求**：Axios
- **工具库**：JS-Cookie

## 安装步骤

### 环境要求
- Python 3.6+ (后端)
- Node.js 16+ (前端)

### 后端安装

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化数据库**
   ```bash
   python manage.py migrate
   ```

4. **创建超级用户**
   ```bash
   python manage.py createsuperuser
   ```

5. **启动开发服务器**
   ```bash
   python manage.py runserver
   ```
   后端服务将运行在 `http://127.0.0.1:8000`

### 前端安装

1. **进入前端目录**
   ```bash
   cd frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **启动开发服务器**
   ```bash
   npm run dev
   ```
   前端服务将运行在 `http://localhost:5173`

## 使用说明

### 登录系统
1. 访问 `http://localhost:5173`
2. 使用创建的超级用户账号登录

### 创建BUG
1. 登录后，点击右上角的"提报BUG"按钮
2. 填写BUG信息：
   - 标题：简洁明了的BUG描述
   - 严重程度：选择致命/严重/一般/轻微
   - 优先级：选择高/中/低
   - 所属模块：通过级联选择器选择
   - 版本号：发现BUG的软件版本
   - 问题描述：详细描述BUG的复现步骤、预期结果和实际结果
   - 附件截图：可选，支持上传多张图片
3. 点击"提交"按钮

### 管理BUG
1. 在BUG列表页，可通过筛选条件查找特定BUG
2. 点击BUG标题查看详情
3. 在详情页可进行以下操作：
   - 编辑：修改BUG信息
   - 修改状态：更新BUG的处理状态
   - 分配：将BUG分配给开发人员
   - 复制BUG：快速创建类似BUG

### 复制BUG功能
1. 在BUG详情页，点击"复制BUG"按钮
2. 系统会自动跳转到创建页面，并填充复制的数据
3. 标题会自动添加"【复制】"前缀
4. 可修改后提交

### BUG状态流转
- **待处理**：BUG初始状态
- **处理中**：开发人员开始处理
- **已解决**：开发人员修复完成
- **已驳回**：非BUG或无法复现
- **已关闭**：测试验证通过

## 项目结构

```
.
├── backend/                 # 后端代码
│   ├── backend/            # Django项目配置
│   ├── bugs/               # BUG模块
│   ├── modules/            # 模块管理
│   ├── users/              # 用户模块
│   ├── manage.py           # Django管理脚本
│   └── requirements.txt    # 依赖列表
├── frontend/               # 前端代码
│   ├── public/             # 静态资源
│   ├── src/                # 源代码
│   │   ├── api/           # API请求
│   │   ├── components/     # 组件
│   │   ├── router/         # 路由
│   │   ├── stores/         # 状态管理
│   │   ├── utils/          # 工具函数
│   │   ├── views/          # 页面
│   │   ├── App.vue         # 根组件
│   │   └── main.js         # 入口文件
│   ├── index.html          # HTML模板
│   ├── package.json        # 依赖配置
│   └── vite.config.js      # Vite配置
├── 启动指南.md              # 详细启动说明
└── README.md               # 项目介绍
```

## API文档

### 认证
- 使用JWT认证，在请求头中添加 `Authorization: Bearer <token>`
- 登录接口返回access_token和refresh_token
- 支持自动刷新token机制

### 主要API端点

#### BUG管理
- `GET /api/bugs/` - 获取BUG列表
- `POST /api/bugs/` - 创建BUG
- `GET /api/bugs/{id}/` - 获取BUG详情
- `PUT /api/bugs/{id}/` - 更新BUG
- `DELETE /api/bugs/{id}/` - 删除BUG
- `POST /api/bugs/{id}/update_status/` - 更新BUG状态
- `POST /api/bugs/{id}/assign/` - 分配BUG
- `POST /api/bugs/{id}/upload_attachment/` - 上传附件
- `DELETE /api/bugs/{id}/attachment/{attachment_id}/` - 删除附件
- `GET /api/bugs/{id}/copy/` - 复制BUG

#### 用户管理
- `POST /api/users/login/` - 用户登录
- `POST /api/users/logout/` - 用户登出
- `GET /api/users/profile/` - 获取个人信息
- `GET /api/users/developers/` - 获取开发人员列表

#### 模块管理
- `GET /api/modules/cascade/` - 获取模块级联数据

## 开发指南

### 后端开发
1. 创建新应用：`python manage.py startapp <app_name>`
2. 添加应用到 `INSTALLED_APPS`
3. 定义模型，运行迁移：`python manage.py makemigrations && python manage.py migrate`
4. 编写视图和序列化器
5. 配置URL路由

### 前端开发
1. 创建新页面：在 `src/views/` 目录下创建新的Vue组件
2. 配置路由：在 `src/router/index.js` 中添加路由
3. 编写API请求：在 `src/api/` 目录下添加请求函数
4. 开发组件：在 `src/components/` 目录下创建组件
5. 管理状态：在 `src/stores/` 目录下创建Pinia store

## 部署说明

### 生产环境部署

#### 后端
1. 使用Gunicorn作为WSGI服务器：`gunicorn backend.wsgi:application`
2. 配置Nginx作为反向代理
3. 使用MySQL作为数据库
4. 配置HTTPS

#### 前端
1. 构建生产版本：`npm run build`
2. 将 `dist/` 目录部署到Nginx或其他静态文件服务器
3. 配置Nginx代理API请求

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 邮箱：2638182207@qq.com
- GitHub：https://github.com/your-username/bug-management-system

## 更新日志

### v1.0.0 (2026-01-20)
- 初始版本发布
- 实现完整的BUG管理功能
- 支持用户角色权限管理
- 实现复制BUG功能
- 完整的前后端分离架构

### v0.1.0 (2026-01-15)
- 项目初始化
- 实现基本的BUG CRUD功能
- 完成用户认证系统

## 贡献指南

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交Pull Request

## 致谢

感谢所有为项目做出贡献的开发者！

---

**使用愉快！** 🚀
