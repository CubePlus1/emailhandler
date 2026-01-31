# EmailHandler 项目文档

## 📖 项目简介

EmailHandler 是一个基于 Cloudflare Email Routing 的现代化域名邮箱系统，提供完整的邮箱管理、邮件转发和 Webhook 处理功能。

### 主要功能

- 🔐 完整的 RBAC 权限控制系统
- 📧 邮件转发规则管理
- 🔄 Webhook 事件处理
- 🌐 RESTful API 接口
- 💾 SQLite 数据库存储
- 🔒 安全的身份验证机制

## 📚 文档导航

本文档集合详细介绍了 EmailHandler 项目的各个方面：

| 序号 | 文档名称 | 描述 |
|------|----------|------|
| 1 | [架构总览](./01-architecture.md) | 系统整体架构、技术栈、目录结构 |
| 2 | [数据库模型](./02-models.md) | User、ForwardRule、Webhook、WebhookEvent 等模型详解 |
| 3 | [API 路由](./03-api-routes.md) | 用户管理、邮箱管理、转发规则等 API 端点 |
| 4 | [Webhook 处理](./04-webhooks.md) | Webhook 注册、验证、事件处理流程 |
| 5 | [Flask 应用主程序](./05-app.md) | Flask 应用初始化、配置、蓝图注册 |
| 6 | [工具函数](./06-utils.md) | 密码哈希、JWT 令牌、权限装饰器 |
| 7 | [依赖管理与环境配置](./07-setup.md) | requirements.txt、环境变量、部署配置 |
| 8 | [数据流和生命周期](./08-data-flow.md) | 请求处理流程、邮件转发、Webhook 事件 |
| 9 | [代码风格和最佳实践](./09-best-practices.md) | 代码规范、安全实践、性能优化 |
| 10 | [快速参考和 FAQ](./10-quick-reference.md) | 常用命令、API 速查、常见问题 |
| 11 | [错误处理和日志](./11-error-handling.md) | 错误处理机制、日志系统、调试方法 |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/CubePlus1/emailhandler.git
cd emailhandler
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖（推荐使用 uv）
uv pip install -r requirements.txt
# 或使用标准 pip
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/emailhandler.db
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 启动应用

```bash
python backend/app.py
```

访问 http://localhost:5000 即可使用。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                │
│                   (未来扩展预留)                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask API 层                            │
│  ┌─────────────┬──────────────┬──────────────┬───────────┐ │
│  │ 用户管理API │ 邮箱管理API  │ 转发规则API  │ WebhookAPI│ │
│  └─────────────┴──────────────┴──────────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      业务逻辑层                              │
│  ┌─────────────┬──────────────┬──────────────┬───────────┐ │
│  │ 权限控制    │ 邮件转发     │ Webhook处理  │ 工具函数  │ │
│  └─────────────┴──────────────┴──────────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据访问层                              │
│  ┌─────────────┬──────────────┬──────────────┬───────────┐ │
│  │ User Model  │ ForwardRule  │ Webhook      │ WebhookEvt│ │
│  └─────────────┴──────────────┴──────────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite 数据库                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔌 API 使用示例

### 用户认证

```bash
# 登录
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 创建转发规则

```bash
# 创建转发规则
curl -X POST http://localhost:5000/api/forward-rules \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "info@yourdomain.com",
    "destination": "your-email@gmail.com"
  }'
```

### Webhook 订阅

```bash
# 注册 Webhook
curl -X POST http://localhost:5000/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "event_types": ["email.received", "email.forwarded"]
  }'
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 为新功能添加测试
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](../LICENSE) 文件

## 📞 联系方式

- 项目主页: https://github.com/CubePlus1/emailhandler
- 问题反馈: https://github.com/CubePlus1/emailhandler/issues
- 作者: CubePlus1

## 📝 版本历史

### v3.0 (当前版本)
- ✨ 重构项目结构，将模块移至 backend 目录
- 🔐 完善 RBAC 权限控制系统
- 📧 优化邮件转发规则管理
- 🔄 增强 Webhook 处理机制
- 📚 新增完整项目文档

### v2.x
- 🎨 改进前端界面
- 🐛 修复已知问题

### v1.x
- 🎉 项目初始版本
- 🔨 基础功能实现

---

**感谢使用 EmailHandler！如有问题，请查阅文档或提交 Issue。**
