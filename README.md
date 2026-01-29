# EmailHandler - 域名邮箱系统

**版本**: 3.0.0

完整的域名邮箱系统，支持通过 Cloudflare Email Routing 收发邮件，具有现代化 React 前端界面和数据库持久化存储。

---

## 🎯 核心功能

### ✅ 邮件接收
- **Cloudflare Email Worker** - 处理域名邮件
- **自定义 MIME 解析器** - 支持 multipart 邮件和附件
- **Webhook 认证** - 共享密钥保护端点
- **数据库持久化** - SQLite (开发) / PostgreSQL (生产)

### ✅ 现代化 UI
- **React + TypeScript** - 类型安全的前端
- **Tailwind CSS** - 现代化设计
- **响应式布局** - 移动端友好
- **编辑风格设计** - 高对比度、渐变点缀

### ✅ 完整的 API
- **RESTful 端点** - 邮箱管理、邮件 CRUD
- **全文搜索** - SQLite FTS5 虚拟表
- **分页支持** - 高效的数据加载

### ✅ 向后兼容
- **保留 v2.0 API** - 验证链接功能依然可用
- **EmailMonitor** - Python 包继续支持

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    React SPA (Port 3000)                     │
│             Layout + EmailList + EmailView + Compose        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask API (Port 5000)                      │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │ /api/emails  │ /api/search  │ /webhook/... │ /status  │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
│                              │                               │
│                    ┌─────────┴─────────┐                    │
│                    │ SQLAlchemy + DB   │                    │
│                    │ SQLite/PostgreSQL │                    │
│                    └───────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ POST /webhook/email
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare Email Worker                         │
│         MIME Parser → JSON → POST to Flask                  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ Email Routing
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare DNS                            │
│              MX Records → yourdomain.com                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd emailhandler
```

### 2. 后端设置

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 或使用 uv（推荐）
uv pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 DATABASE_URL 和 WEBHOOK_SECRET

# 运行数据库迁移
alembic upgrade head

# 启动 Flask 服务
python email_receiver.py
```

服务运行在 `http://localhost:5000`

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

前端运行在 `http://localhost:3000`

### 4. Cloudflare Worker 部署

```bash
cd cloudflare

# 安装 Wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 设置密钥
wrangler secret put WEBHOOK_SECRET
wrangler secret put FLASK_API_URL

# 部署 Worker
wrangler deploy
```

### 5. 配置 Cloudflare Email Routing

1. 在 Cloudflare 仪表板中进入你的域名
2. 转到 **Email** → **Email Routing**
3. 添加 MX 记录（自动或手动）
4. 创建路由规则：
   - **接收邮件**: `*@yourdomain.com`
   - **发送到**: Worker (`emailhandler-worker`)

---

## 🔌 API 端点

### 服务状态

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/status` | GET | 服务状态和统计 |

### 邮件接收（v2.0 兼容）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/webhook/email` | POST | 接收邮件（需要 X-Webhook-Secret） |
| `/verification_link` | GET | 获取最新验证链接 |
| `/emails` | GET | 查看所有邮件（支持分页） |
| `/clear` | POST | 清空数据 |

### 扩展 API（v3.0 新增）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/mailboxes` | GET | 获取所有邮箱 |
| `/api/emails` | GET | 分页邮件列表（支持文件夹过滤） |
| `/api/emails/:id` | GET | 获取单个邮件详情 |
| `/api/emails/:id` | PATCH | 更新邮件（已读、星标、文件夹） |
| `/api/emails/:id` | DELETE | 删除邮件 |
| `/api/search?q=keyword` | GET | 全文搜索 |

---

## 📚 使用示例

### Python API（v2.0 兼容）

```python
from emailhandler import EmailMonitor

# 等待验证邮件
monitor = EmailMonitor()
result = monitor.wait_and_handle_verification_link(max_wait=300)

if result['success']:
    print(f"验证 ID: {result['verification_id']}")
```

### REST API（v3.0）

```bash
# 获取收件箱邮件
curl http://localhost:5000/api/emails?folder=inbox&page=1

# 搜索邮件
curl http://localhost:5000/api/search?q=重要

# 标记为已读
curl -X PATCH http://localhost:5000/api/emails/1 \
  -H "Content-Type: application/json" \
  -d '{"is_read": true}'
```

### React 前端

```typescript
import api from './api/client';

// 获取邮件列表
const emails = await api.getEmails('inbox', 1);

// 搜索邮件
const results = await api.searchEmails('关键词');

// 更新邮件
await api.updateEmail(1, { is_read: true, is_starred: true });
```

---

## 🗂️ 项目结构

```
emailhandler/
├── emailhandler/              # Python 包
│   ├── __init__.py           # 模块导出
│   ├── models.py             # SQLAlchemy 模型
│   ├── email_monitor.py      # 邮件监控（v2.0）
│   └── link_handler.py       # 链接处理（v2.0）
├── migrations/                # Alembic 数据库迁移
│   ├── env.py
│   └── versions/
│       └── 001_initial_migration.py
├── cloudflare/                # Cloudflare Worker
│   ├── worker.js             # Email Worker
│   └── wrangler.toml         # Worker 配置
├── frontend/                  # React 前端
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts     # API 客户端
│   │   ├── components/
│   │   │   ├── Layout.tsx         # 布局组件
│   │   │   ├── EmailList.tsx      # 邮件列表
│   │   │   ├── EmailView.tsx      # 邮件详情
│   │   │   └── ComposeModal.tsx   # 撰写邮件
│   │   ├── types/
│   │   │   └── email.ts      # TypeScript 类型
│   │   └── utils/
│   │       └── dateUtils.ts  # 工具函数
│   ├── package.json
│   └── tailwind.config.js
├── email_receiver.py          # Flask API 服务
├── verify.py                  # CLI 验证工具
├── pyproject.toml            # Python 依赖
├── alembic.ini               # 迁移配置
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略文件
└── README.md                 # 本文档
```

---

## 🔧 配置

### 环境变量

创建 `.env` 文件（参考 `.env.example`）：

```bash
# Flask 配置
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here

# 数据库
DATABASE_URL=sqlite:///emails.db
# 生产环境: DATABASE_URL=postgresql://user:pass@host:5432/emailhandler

# Webhook 认证
WEBHOOK_SECRET=your-webhook-secret-here

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
# 生产环境: CORS_ORIGINS=https://mail.yourdomain.com
```

### 数据库

**开发环境（SQLite）**:
```bash
DATABASE_URL=sqlite:///emails.db
alembic upgrade head
```

**生产环境（PostgreSQL）**:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/emailhandler
alembic upgrade head
```

---

## 🎨 前端组件

### Layout
- 固定侧边栏（Inbox, Sent, Trash）
- 响应式设计（移动端可折叠）
- 渐变背景（indigo → blue）

### EmailList
- 编辑风格设计（Editorial Minimalism）
- 已读/未读视觉区分
- 脉冲动画未读指示器
- 骨架屏加载状态

### EmailView
- 编辑-野蛮主义融合设计
- HTML 安全渲染（DOMPurify）
- 操作按钮（回复、标星、删除）
- 深色分层渐变背景

### ComposeModal
- Headless UI Dialog
- 实时表单验证
- 回复自动填充
- 渐变按钮 + 光泽效果

---

## 🔐 安全特性

### Webhook 认证
- 共享密钥验证（`X-Webhook-Secret` header）
- 防止未授权的邮件注入
- 环境变量配置

### HTML 消毒
- DOMPurify 清理邮件 HTML
- 防止 XSS 攻击
- 安全标签白名单

### CORS 保护
- 明确允许的源地址
- 开发/生产环境分离配置

### 数据库安全
- SQLAlchemy ORM 防止 SQL 注入
- 事务管理和错误回滚
- 敏感信息环境变量存储

---

## 🚀 部署

### 后端部署

```bash
# 1. 设置环境变量
export DATABASE_URL="postgresql://..."
export WEBHOOK_SECRET="..."

# 2. 运行迁移
alembic upgrade head

# 3. 启动服务（使用 Gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 email_receiver:app
```

### 前端部署

```bash
cd frontend

# 构建生产版本
npm run build

# 部署 build/ 目录到静态托管服务
# 如：Vercel, Netlify, Cloudflare Pages
```

### Cloudflare Worker 部署

```bash
cd cloudflare
wrangler deploy
```

---

## 📊 数据库模式

### Mailbox（邮箱账户）
- `id` - 主键
- `email` - 邮箱地址（唯一）
- `display_name` - 显示名称
- `created_at` - 创建时间

### Email（邮件）
- `id` - 主键
- `mailbox_id` - 外键
- `message_id` - 邮件 ID（唯一）
- `from_address`, `to_address` - 发件人/收件人
- `subject`, `html_body`, `text_body` - 内容
- `is_read`, `is_starred` - 状态
- `folder` - 文件夹（inbox, sent, trash）
- `received_at` - 接收时间
- `verification_link` - 验证链接（v2.0 兼容）

### Attachment（附件）
- `id` - 主键
- `email_id` - 外键
- `filename`, `content_type`, `size` - 文件信息
- `storage_path` - 存储路径

### FTS5 全文搜索
- 虚拟表 `emails_fts`
- 搜索字段：subject, text_body
- 自动同步触发器

---

## 🆘 常见问题

**Q: 如何配置域名邮箱？**
A: 在 Cloudflare 中设置 Email Routing，添加 MX 记录，创建路由规则指向 Worker。

**Q: 如何切换到 PostgreSQL？**
A: 修改 `.env` 中的 `DATABASE_URL`，运行 `alembic upgrade head`。

**Q: v2.0 的验证链接功能还能用吗？**
A: 是的！所有 v2.0 API 端点完全兼容，`verification_link` 字段保留在数据库中。

**Q: 如何添加用户认证？**
A: 实现 JWT 认证端点（`/api/login`, `/api/register`），使用 PyJWT 库。

**Q: 如何发送邮件？**
A: 集成 SendGrid SMTP API（计划功能，待实现）。

---

## 🔄 从 v2.0 升级

### 数据迁移

```bash
# 1. 备份现有数据（如果使用文件存储）
python -c "import json; from email_receiver import emails; \
           json.dump(emails, open('backup.json', 'w'))"

# 2. 运行数据库迁移
alembic upgrade head

# 3. 可选：导入备份数据到数据库
# （编写迁移脚本）
```

### API 变更

- **向后兼容** - 所有 v2.0 端点继续工作
- **新增端点** - `/api/*` 路径提供扩展功能
- **分页支持** - `GET /emails` 现在支持 `?page=1&per_page=20`

---

## 📝 技术栈

### 后端
- **Python 3.9+**
- **Flask 3.1.2** - Web 框架
- **SQLAlchemy 3.0** - ORM
- **Alembic 4.0** - 数据库迁移
- **Flask-CORS 4.0** - 跨域支持
- **PyJWT 2.8** - JWT 认证（待实现）

### 前端
- **React 18** - UI 框架
- **TypeScript 5** - 类型安全
- **Tailwind CSS 3** - 样式框架
- **React Router 6** - 路由
- **Axios 1** - HTTP 客户端
- **@headlessui/react** - 无样式组件
- **@heroicons/react** - 图标库
- **DOMPurify 3** - HTML 消毒

### Cloudflare
- **Cloudflare Workers** - 边缘计算
- **Email Routing** - 邮件路由
- **Wrangler 3** - 部署工具

---

## 📄 许可证

MIT License

---

## 👥 贡献者

EmailHandler Team

---

## 📞 支持

- **文档**: `.omc/DEVELOPMENT.md` - 开发文档
- **API**: `.omc/API.md` - API 参考
- **计划**: `.omc/plans/cloudflare-email-ui.md` - 实施计划

---

**构建你的域名邮箱系统！** 🚀📧

---

*版本 3.0.0 由 Claude Sonnet 4.5 开发*
*最后更新: 2026-01-29*
