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

## 项目架构说明

### 系统架构

#### 1. 架构模式
- **前后端分离架构**：前端和后端完全独立，通过API进行通信
- **MVC架构**（后端）：Model-View-Controller设计模式
- **组件化架构**（前端）：基于Vue 3的组件化开发

#### 2. 系统分层

| 层       | 技术栈                | 职责                          |
|---------|--------------------|-----------------------------|
| 前端界面层   | Vue 3 + Element Plus | 用户交互和数据展示                  |
| 前端逻辑层   | Pinia + Vue Router  | 状态管理和路由控制                  |
| 通信层     | Axios              | 前后端数据通信                    |
| API层     | Django REST Framework | 提供RESTful API              |
| 业务逻辑层   | Django             | 处理核心业务逻辑                   |
| 数据访问层   | Django ORM         | 数据库操作                      |
| 数据库层    | SQLite/MySQL       | 数据存储                       |

### 数据库设计

#### 1. 数据库选型
- **开发环境**：SQLite（轻量级，无需额外配置）
- **生产环境**：MySQL（高性能，适合生产部署）

#### 2. 核心表关系

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  projects  │────►│  products  │────►│  modules   │
└────────────┘     └────────────┘     └────────────┘
                                           │
                                           ▼
┌────────────┐     ┌────────────┐     ┌────────────┐
│   users    │◄────┤    bugs    │◄────┤ bug_attach │
└────────────┘     └────────────┘     └────────────┘
```

#### 3. 主要表结构

##### 3.1 项目表（projects）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY | 项目ID |
| name | VARCHAR(100) | NOT NULL | 项目名称 |
| description | TEXT | | 项目描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

##### 3.2 产品表（products）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY | 产品ID |
| name | VARCHAR(100) | NOT NULL | 产品名称 |
| project_id | INT | FOREIGN KEY | 关联项目ID |
| description | TEXT | | 产品描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

##### 3.3 模块表（modules）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY | 模块ID |
| name | VARCHAR(100) | NOT NULL | 模块名称 |
| product_id | INT | FOREIGN KEY | 关联产品ID |
| description | TEXT | | 模块描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

##### 3.4 用户表（users）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY | 用户ID |
| username | VARCHAR(150) | NOT NULL, UNIQUE | 用户名 |
| email | VARCHAR(254) | UNIQUE | 邮箱 |
| password | VARCHAR(128) | NOT NULL | 密码（加密存储） |
| role | VARCHAR(20) | NOT NULL | 角色（super_admin/admin/tester/developer） |
| status | VARCHAR(20) | NOT NULL | 状态（active/disabled） |
| phone | VARCHAR(20) | | 手机号 |
| avatar | VARCHAR(100) | | 头像URL |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

##### 3.5 BUG表（bugs）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY | BUG ID |
| title | VARCHAR(200) | NOT NULL | BUG标题 |
| description | TEXT | NOT NULL | BUG描述 |
| severity | VARCHAR(20) | NOT NULL | 严重程度 |
| priority | VARCHAR(20) | NOT NULL | 优先级 |
| status | VARCHAR(20) | NOT NULL | 状态 |
| module_id | INT | FOREIGN KEY | 所属模块ID |
| version | VARCHAR(50) | | 版本号 |
| creator_id | INT | FOREIGN KEY | 创建人ID |
| assignee_id | INT | FOREIGN KEY | 处理人ID |
| solution | TEXT | | 解决说明 |
| reject_reason | TEXT | | 驳回原因 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

##### 3.6 BUG附件表（bug_attachments）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY | 附件ID |
| bug_id | INT | FOREIGN KEY | 关联BUG ID |
| file | VARCHAR(200) | NOT NULL | 附件路径 |
| created_at | DATETIME | NOT NULL | 上传时间 |

### 4. 表关系说明

1. **项目-产品-模块**：三层级联关系，一个项目包含多个产品，一个产品包含多个模块
2. **模块-BUG**：一对多关系，一个模块包含多个BUG
3. **用户-BUG**：
   - 创建关系：一个用户可以创建多个BUG
   - 分配关系：一个用户可以处理多个BUG
4. **BUG-附件**：一对多关系，一个BUG可以有多个附件

### 5. 核心业务流程

1. **BUG提报流程**：
   - 测试人员登录系统
   - 选择所属项目、产品、模块
   - 填写BUG详情和附件
   - 提交BUG（状态：待处理）

2. **BUG处理流程**：
   - 管理员分配BUG给开发人员
   - 开发人员修改状态为"处理中"
   - 开发人员修复后修改状态为"已解决"或"已驳回"
   - 测试人员验证后修改状态为"已关闭"

3. **状态流转**：
   ```
   新建 → 待处理 → 处理中 → 已解决/已驳回 → 已关闭
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
- 邮箱：your-email@example.com
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
