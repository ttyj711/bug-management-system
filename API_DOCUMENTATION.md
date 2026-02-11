# BUG管理系统 API文档

## 目录
- [认证接口](#认证接口)
- [用户管理接口](#用户管理接口)
- [项目-产品-模块管理接口](#项目-产品-模块管理接口)
- [BUG管理接口](#bug管理接口)
- [通用说明](#通用说明)

---

## 认证接口

### 用户登录
- **接口**: `POST /api/users/login/`
- **说明**: 验证用户凭证，返回JWT令牌
- **权限**: 允许匿名访问

**请求参数**:
```json
{
  "username": "string",
  "password": "string"
}
```

**成功响应**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "phone": "13800138000",
    "role": "super_admin",
    "role_display": "超级管理员",
    "status": "active",
    "status_display": "启用",
    "avatar": "/media/avatars/default.png",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**错误响应**:
```json
{
  "detail": "用户名或密码错误"
}
```

---

### 用户登出
- **接口**: `POST /api/users/logout/`
- **说明**: 将refresh令牌加入黑名单，使其失效
- **权限**: 需要登录

**请求参数**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**成功响应**:
```json
{
  "detail": "登出成功"
}
```

---

### 刷新令牌
- **接口**: `POST /api/users/token/refresh/`
- **说明**: 使用refresh令牌获取新的access令牌
- **权限**: 允许匿名访问

**请求参数**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**成功响应**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 用户管理接口

### 获取用户列表
- **接口**: `GET /api/users/`
- **说明**: 获取所有用户列表
- **权限**: 仅超级管理员

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| role | string | 按角色筛选 (super_admin/admin/developer/tester) |
| status | string | 按状态筛选 (active/disabled) |
| search | string | 按用户名搜索 |

**成功响应**:
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "phone": "13800138000",
      "role": "super_admin",
      "role_display": "超级管理员",
      "status": "active",
      "status_display": "启用",
      "avatar": "/media/avatars/default.png",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 创建用户
- **接口**: `POST /api/users/`
- **说明**: 创建新用户
- **权限**: 仅超级管理员

**请求参数**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "phone": "13900139000",
  "password": "Password123!",
  "confirm_password": "Password123!",
  "role": "developer",
  "status": "active"
}
```

**成功响应**:
```json
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "phone": "13900139000",
  "role": "developer",
  "status": "active"
}
```

---

### 获取用户详情
- **接口**: `GET /api/users/{id}/`
- **说明**: 获取指定用户详情
- **权限**: 仅超级管理员

---

### 更新用户
- **接口**: `PUT /api/users/{id}/` 或 `PATCH /api/users/{id}/`
- **说明**: 更新用户信息
- **权限**: 仅超级管理员

**请求参数**:
```json
{
  "email": "updated@example.com",
  "phone": "13700137000",
  "role": "admin",
  "status": "active"
}
```

---

### 删除用户
- **接口**: `DELETE /api/users/{id}/`
- **说明**: 删除用户
- **权限**: 仅超级管理员

---

### 重置用户密码
- **接口**: `POST /api/users/{id}/reset_password/`
- **说明**: 管理员重置用户密码
- **权限**: 仅超级管理员

**请求参数**:
```json
{
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}
```

**成功响应**:
```json
{
  "detail": "密码重置成功"
}
```

---

### 切换用户状态
- **接口**: `POST /api/users/{id}/toggle_status/`
- **说明**: 切换用户启用/禁用状态
- **权限**: 仅超级管理员

**成功响应**:
```json
{
  "detail": "状态更新成功",
  "status": "disabled"
}
```

---

### 获取个人信息
- **接口**: `GET /api/users/profile/`
- **说明**: 获取当前登录用户信息
- **权限**: 需要登录

**成功响应**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "phone": "13800138000",
  "role": "super_admin",
  "role_display": "超级管理员",
  "avatar": "/media/avatars/default.png"
}
```

---

### 更新个人信息
- **接口**: `PUT /api/users/profile/`
- **说明**: 更新当前登录用户信息
- **权限**: 需要登录

**请求参数**:
```json
{
  "email": "newemail@example.com",
  "phone": "13600136000"
}
```

---

### 修改密码
- **接口**: `POST /api/users/change-password/`
- **说明**: 用户修改自己的密码
- **权限**: 需要登录

**请求参数**:
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}
```

**成功响应**:
```json
{
  "detail": "密码修改成功"
}
```

---

### 获取开发人员列表
- **接口**: `GET /api/users/developers/`
- **说明**: 返回所有启用状态的开发人员列表
- **权限**: 需要登录

**成功响应**:
```json
[
  {
    "id": 2,
    "username": "developer1",
    "email": "dev1@example.com",
    "phone": "13900139000",
    "role": "developer",
    "role_display": "开发人员",
    "status": "active",
    "status_display": "启用",
    "avatar": "/media/avatars/default.png",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

## 项目-产品-模块管理接口

### 获取项目列表
- **接口**: `GET /api/modules/projects/`
- **说明**: 获取所有项目列表
- **权限**: 需要登录

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| is_active | string | 按启用状态筛选 (true/false) |

**成功响应**:
```json
[
  {
    "id": 1,
    "name": "电商平台",
    "description": "电商平台项目",
    "is_active": true,
    "products": [
      {
        "id": 1,
        "name": "用户中心",
        "is_active": true
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### 创建项目
- **接口**: `POST /api/modules/projects/`
- **说明**: 创建新项目
- **权限**: 仅超级管理员

**请求参数**:
```json
{
  "name": "新项目",
  "description": "项目描述",
  "is_active": true
}
```

---

### 获取项目详情
- **接口**: `GET /api/modules/projects/{id}/`
- **说明**: 获取指定项目详情
- **权限**: 需要登录

---

### 更新项目
- **接口**: `PUT /api/modules/projects/{id}/` 或 `PATCH /api/modules/projects/{id}/`
- **说明**: 更新项目信息
- **权限**: 仅超级管理员

---

### 删除项目
- **接口**: `DELETE /api/modules/projects/{id}/`
- **说明**: 删除项目
- **权限**: 仅超级管理员

---

### 获取产品列表
- **接口**: `GET /api/modules/products/`
- **说明**: 获取所有产品列表
- **权限**: 需要登录

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| project | integer | 按所属项目ID筛选 |
| is_active | string | 按启用状态筛选 (true/false) |

**成功响应**:
```json
[
  {
    "id": 1,
    "project": 1,
    "project_name": "电商平台",
    "name": "用户中心",
    "description": "用户中心产品",
    "is_active": true,
    "modules": [
      {
        "id": 1,
        "product": 1,
        "product_name": "用户中心",
        "name": "用户注册",
        "description": "用户注册模块",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### 创建产品
- **接口**: `POST /api/modules/products/`
- **说明**: 创建新产品
- **权限**: 仅超级管理员

**请求参数**:
```json
{
  "project": 1,
  "name": "新产品",
  "description": "产品描述",
  "is_active": true
}
```

---

### 获取产品详情
- **接口**: `GET /api/modules/products/{id}/`
- **说明**: 获取指定产品详情
- **权限**: 需要登录

---

### 更新产品
- **接口**: `PUT /api/modules/products/{id}/` 或 `PATCH /api/modules/products/{id}/`
- **说明**: 更新产品信息
- **权限**: 仅超级管理员

---

### 删除产品
- **接口**: `DELETE /api/modules/products/{id}/`
- **说明**: 删除产品
- **权限**: 仅超级管理员

---

### 获取模块列表
- **接口**: `GET /api/modules/modules/`
- **说明**: 获取所有模块列表
- **权限**: 需要登录

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| product | integer | 按所属产品ID筛选 |
| is_active | string | 按启用状态筛选 (true/false) |

**成功响应**:
```json
[
  {
    "id": 1,
    "product": 1,
    "product_name": "用户中心",
    "name": "用户注册",
    "description": "用户注册模块",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### 创建模块
- **接口**: `POST /api/modules/modules/`
- **说明**: 创建新模块
- **权限**: 仅超级管理员

**请求参数**:
```json
{
  "product": 1,
  "name": "新模块",
  "description": "模块描述",
  "is_active": true
}
```

---

### 获取模块详情
- **接口**: `GET /api/modules/modules/{id}/`
- **说明**: 获取指定模块详情
- **权限**: 需要登录

---

### 更新模块
- **接口**: `PUT /api/modules/modules/{id}/` 或 `PATCH /api/modules/modules/{id}/`
- **说明**: 更新模块信息
- **权限**: 仅超级管理员

---

### 删除模块
- **接口**: `DELETE /api/modules/modules/{id}/`
- **说明**: 删除模块
- **权限**: 仅超级管理员

---

### 获取模块级联数据
- **接口**: `GET /api/modules/cascade/`
- **说明**: 返回项目-产品-模块的完整层级结构数据，用于前端级联选择器
- **权限**: 需要登录

**成功响应**:
```json
[
  {
    "value": 1,
    "label": "电商平台",
    "children": [
      {
        "value": 1,
        "label": "用户中心",
        "children": [
          {
            "value": 1,
            "label": "用户注册"
          },
          {
            "value": 2,
            "label": "用户登录"
          }
        ]
      }
    ]
  }
]
```

---

## BUG管理接口

### 获取BUG列表
- **接口**: `GET /api/bugs/`
- **说明**: 获取BUG列表
- **权限**: 需要登录

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 按状态筛选 (pending/processing/resolved/rejected/closed) |
| severity | string | 按严重程度筛选 (critical/major/minor/trivial) |
| priority | string | 按优先级筛选 (high/medium/low) |
| assignee | integer | 按处理人ID筛选 |
| creator | integer | 按创建人ID筛选 |
| search | string | 按标题或描述搜索 |
| my_bugs | string | 快捷筛选 (created=我创建的, assigned=分配给我的) |

**成功响应**:
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "登录页面无法加载",
      "severity": "critical",
      "severity_display": "严重",
      "priority": "high",
      "priority_display": "高",
      "status": "pending",
      "status_display": "待处理",
      "module": 1,
      "module_path": "电商平台 / 用户中心 / 用户注册",
      "version": "1.0.0",
      "creator": 1,
      "creator_name": "admin",
      "assignee": null,
      "assignee_name": "",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 创建BUG
- **接口**: `POST /api/bugs/`
- **说明**: 创建新BUG
- **权限**: 超级管理员、普通管理员、测试人员

**请求参数** (multipart/form-data):
| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | BUG标题 (必填) |
| description | string | BUG描述 (必填) |
| severity | string | 严重程度 (critical/major/minor/trivial) |
| priority | string | 优先级 (high/medium/low) |
| module | integer | 模块ID |
| version | string | 版本号 |
| assignee | integer | 处理人ID |
| attachments | file[] | 附件列表 (可选) |

**示例**:
```
POST /api/bugs/
Content-Type: multipart/form-data

title: "登录页面无法加载"
description: "用户点击登录按钮后，页面无响应"
severity: "critical"
priority: "high"
module: 1
version: "1.0.0"
attachments: [screenshot1.png, screenshot2.png]
```

**成功响应**:
```json
{
  "id": 1,
  "title": "登录页面无法加载",
  "description": "用户点击登录按钮后，页面无响应",
  "severity": "critical",
  "severity_display": "严重",
  "priority": "high",
  "priority_display": "高",
  "status": "pending",
  "status_display": "待处理",
  "module": 1,
  "module_path": "电商平台 / 用户中心 / 用户注册",
  "version": "1.0.0",
  "creator": 1,
  "creator_name": "admin",
  "assignee": null,
  "assignee_name": "",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### 获取BUG详情
- **接口**: `GET /api/bugs/{id}/`
- **说明**: 获取指定BUG详情
- **权限**: 需要登录

**成功响应**:
```json
{
  "id": 1,
  "title": "登录页面无法加载",
  "description": "用户点击登录按钮后，页面无响应",
  "severity": "critical",
  "severity_display": "严重",
  "priority": "high",
  "priority_display": "高",
  "status": "pending",
  "status_display": "待处理",
  "module": 1,
  "module_path": "电商平台 / 用户中心 / 用户注册",
  "module_cascade": [1, 1, 1],
  "version": "1.0.0",
  "creator": 1,
  "creator_name": "admin",
  "assignee": null,
  "assignee_name": "",
  "solution": "",
  "reject_reason": "",
  "attachments": [
    {
      "id": 1,
      "file": "/media/bugs/1/screenshot1.png",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### 更新BUG
- **接口**: `PUT /api/bugs/{id}/` 或 `PATCH /api/bugs/{id}/`
- **说明**: 更新BUG信息
- **权限**: 超级管理员可编辑所有BUG；测试人员只能编辑自己创建的且状态为"待处理"的BUG

**请求参数** (multipart/form-data):
| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | BUG标题 |
| description | string | BUG描述 |
| severity | string | 严重程度 |
| priority | string | 优先级 |
| module | integer | 模块ID |
| version | string | 版本号 |
| assignee | integer | 处理人ID |
| attachments | file[] | 新附件列表 (可选，追加到现有附件) |

---

### 删除BUG
- **接口**: `DELETE /api/bugs/{id}/`
- **说明**: 删除BUG
- **权限**: 仅超级管理员

---

### 更新BUG状态
- **接口**: `POST /api/bugs/{id}/update_status/`
- **说明**: 更新BUG状态
- **权限**: 开发人员只能处理分配给自己的BUG；超级管理员可以修改任何BUG的状态

**请求参数**:
```json
{
  "status": "resolved",
  "solution": "已修复登录逻辑中的死循环问题",
  "reject_reason": ""
}
```

**状态值说明**:
| 值 | 说明 |
|------|------|
| pending | 待处理 |
| processing | 处理中 |
| resolved | 已解决 |
| rejected | 已驳回 |
| closed | 已关闭 |

**注意**:
- 状态改为 `resolved` 时必须填写 `solution`
- 状态改为 `rejected` 时必须填写 `reject_reason`

**成功响应**:
```json
{
  "detail": "状态更新成功",
  "status": "resolved"
}
```

---

### 分配BUG
- **接口**: `POST /api/bugs/{id}/assign/`
- **说明**: 分配BUG给开发人员
- **权限**: 超级管理员、普通管理员

**请求参数**:
```json
{
  "assignee": 2
}
```

**成功响应**:
```json
{
  "detail": "分配成功"
}
```

---

### 上传附件
- **接口**: `POST /api/bugs/{id}/upload_attachment/`
- **说明**: 上传BUG附件（截图）
- **请求**: multipart/form-data，包含file字段
- **权限**: 需要登录

**请求**:
```
POST /api/bugs/1/upload_attachment/
Content-Type: multipart/form-data

file: screenshot.png
```

**成功响应**:
```json
{
  "id": 2,
  "file": "/media/bugs/1/screenshot.png",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### 删除附件
- **接口**: `DELETE /api/bugs/{id}/attachment/{attachment_id}/`
- **说明**: 删除BUG附件
- **权限**: 需要登录

**成功响应**:
```json
{
  "detail": "删除成功"
}
```

---

### 复制BUG
- **接口**: `GET /api/bugs/{id}/copy/`
- **说明**: 复制BUG功能，返回复制后的数据用于新BUG提报
- **权限**: 需要登录

**成功响应**:
```json
{
  "module": 1,
  "module_cascade": [1, 1, 1],
  "severity": "critical",
  "priority": "high",
  "title": "【复制】登录页面无法加载",
  "description": "用户点击登录按钮后，页面无响应",
  "version": "1.0.0",
  "status": "pending",
  "creator": 1,
  "assignee": null,
  "attachments": [
    {
      "id": 1,
      "file": "/media/bugs/1/screenshot1.png",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 通用说明

### 认证方式
所有需要认证的接口都需要在请求头中携带JWT令牌:
```
Authorization: Bearer <access_token>
```

### 角色说明
| 角色 | 说明 | 权限 |
|------|------|------|
| super_admin | 超级管理员 | 完整系统权限 |
| admin | 普通管理员 | 用户管理、BUG管理 |
| developer | 开发人员 | 处理分配给自己的BUG |
| tester | 测试人员 | 提报BUG、编辑自己创建的BUG |

### 状态说明
**用户状态**:
| 状态 | 说明 |
|------|------|
| active | 启用 |
| disabled | 禁用 |

**BUG状态**:
| 状态 | 说明 |
|------|------|
| pending | 待处理 |
| processing | 处理中 |
| resolved | 已解决 |
| rejected | 已驳回 |
| closed | 已关闭 |

**BUG严重程度**:
| 程度 | 说明 |
|------|------|
| critical | 严重 |
| major | 较大 |
| minor | 较小 |
| trivial | 轻微 |

**BUG优先级**:
| 优先级 | 说明 |
|------|------|
| high | 高 |
| medium | 中 |
| low | 低 |

### 错误响应格式
所有错误响应统一格式:
```json
{
  "detail": "错误描述信息"
}
```

### HTTP状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
