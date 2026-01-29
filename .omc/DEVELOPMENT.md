# 开发文档 - EmailHandler 域名邮箱系统

**项目**: EmailHandler v3.0
**开始日期**: 2026-01-29
**状态**: 开发中（60% 完成）

---

## 📋 项目概述

将 EmailHandler v2.0（邮件验证工具）扩展为完整的域名邮箱系统，支持：
- ✅ Cloudflare Email Routing 接收域名邮件
- ✅ 数据库持久化存储
- ✅ React 前端 UI
- 📋 邮件发送功能（P2 优先级）

---

## 🏗️ 架构决策记录

### ADR-001: 数据库选择
**决策**: SQLite (开发) + PostgreSQL (生产)
**理由**:
- SQLite 零配置便于开发
- PostgreSQL 支持全文搜索和高并发
- 使用 SQLAlchemy ORM 便于切换

### ADR-002: 前端框架
**决策**: React + TypeScript + Tailwind CSS
**理由**:
- React 广泛采用，生态成熟
- TypeScript 提供类型安全
- Tailwind 快速开发现代 UI

### ADR-003: 邮件发送方案
**决策**: SendGrid SMTP API (P2 优先级)
**理由**:
- Cloudflare Email Routing 仅支持接收
- SendGrid 提供可靠的 SMTP 服务
- 有免费额度，API 文档完善
- 先完成接收核心功能，发送后续迭代

### ADR-004: 全文搜索
**决策**: SQLite FTS5 虚拟表
**理由**:
- SQLite 内置支持，无需额外依赖
- FTS5 性能优秀
- 触发器自动同步搜索索引

---

## 📦 已完成的功能

### Phase 1: 基础设施 ✅ (100%)

#### 1. 数据库层
- ✅ **models.py** - SQLAlchemy 模型
  - Mailbox 模型（邮箱账户）
  - Email 模型（邮件，含验证链接字段保持兼容）
  - Attachment 模型（附件）
  - 3 个性能索引

- ✅ **Alembic 迁移系统**
  - `alembic.ini` - 主配置
  - `migrations/env.py` - 环境配置
  - `migrations/versions/001_initial_migration.py` - 初始迁移
  - FTS5 全文搜索虚拟表 + 触发器

- ✅ **email_receiver.py 数据库集成**
  - 6 个函数从内存迁移到数据库
  - Flask-SQLAlchemy + CORS 配置
  - 分页支持（get_emails）
  - 事务处理和错误回滚
  - 完全向后兼容

#### 2. Cloudflare Email Worker
- ✅ **worker.js** - 邮件处理核心
  - 自定义 MIME 解析器（无外部依赖）
  - 支持 multipart 邮件和嵌套结构
  - base64 和 quoted-printable 解码
  - 提取附件信息
  - POST 到 Flask webhook
  - 包含 X-Webhook-Secret 认证

- ✅ **wrangler.toml** - Worker 配置
  - 开发/生产环境配置
  - 环境变量占位符

#### 3. 环境配置
- ✅ **.env.example** - 环境变量模板
  - Flask 配置
  - 数据库 URL
  - Webhook 密钥
  - CORS 源地址
  - SendGrid API 密钥

- ✅ **pyproject.toml** - Python 依赖
  - flask-sqlalchemy>=3.0
  - flask-migrate>=4.0
  - flask-cors>=4.0
  - pyjwt>=2.8
  - python-dotenv>=1.0

### Phase 2: 前端开发 ⏳ (60%)

#### 1. React 项目初始化 ✅
- TypeScript React 应用
- 1352 个 npm 包已安装
- Tailwind CSS 配置完成

#### 2. 已完成的组件 ✅

**API Client** (`src/api/client.ts`)
- Axios 实例配置（Base URL: http://localhost:5000/api）
- 完整 TypeScript 类型（Email, Mailbox, PaginatedResponse）
- 6 个 API 方法：
  - getMailboxes()
  - getEmails(folder?, page?)
  - getEmail(id)
  - updateEmail(id, updates)
  - deleteEmail(id)
  - searchEmails(query)
- 统一错误处理机制

**Layout 组件** (`src/components/Layout.tsx`)
- 固定侧边栏（256px）+ 主内容区
- 文件夹列表（Inbox 📥, Sent 📤, Trash 🗑️）
- @heroicons/react 图标
- 响应式设计（移动端可折叠，汉堡菜单）
- 渐变背景（slate → blue → indigo）
- 平滑动画和 hover 效果

**EmailList 组件** (`src/components/EmailList.tsx`)
- 编辑风格设计（Editorial Minimalism）
- 显示发件人、主题、预览、相对时间
- 已读/未读视觉区分（粗体、颜色、脉冲点）
- 选中状态高亮（indigo-600 背景）
- 加载骨架屏（staggered 动画）
- 空状态提示
- 工具函数：
  - `formatRelativeTime()` - 相对时间格式化
  - `truncateText()` - 文本截断

#### 3. 待完成的组件 📋

- EmailView 组件（邮件详情显示）
- ComposeModal 组件（撰写邮件弹窗）

---

## 🔧 技术栈

### 后端
- **框架**: Flask 3.1.2
- **ORM**: SQLAlchemy 3.0
- **数据库**: SQLite (dev) / PostgreSQL (prod)
- **迁移**: Alembic 4.0
- **CORS**: Flask-CORS 4.0
- **认证**: PyJWT 2.8
- **环境变量**: python-dotenv 1.0

### 前端
- **框架**: React 18 + TypeScript 5
- **路由**: react-router-dom 6
- **HTTP**: Axios 1
- **UI**: Tailwind CSS 3
- **组件**: @headlessui/react 1
- **图标**: @heroicons/react 2
- **安全**: dompurify 3

### Cloudflare
- **Worker**: Cloudflare Email Worker
- **工具**: Wrangler 3

---

## 📝 数据库模式

### Mailbox (邮箱账户)
```sql
CREATE TABLE mailboxes (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Email (邮件)
```sql
CREATE TABLE emails (
    id INTEGER PRIMARY KEY,
    mailbox_id INTEGER REFERENCES mailboxes(id),
    message_id TEXT UNIQUE,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    subject TEXT,
    html_body TEXT,
    text_body TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    is_starred BOOLEAN DEFAULT FALSE,
    folder TEXT DEFAULT 'inbox',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_link TEXT,  -- 保持兼容
    raw_headers TEXT
);

-- 索引
CREATE INDEX idx_emails_mailbox ON emails(mailbox_id);
CREATE INDEX idx_emails_folder ON emails(folder);
CREATE INDEX idx_emails_received ON emails(received_at DESC);
```

### Attachment (附件)
```sql
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY,
    email_id INTEGER REFERENCES emails(id),
    filename TEXT,
    content_type TEXT,
    size INTEGER,
    storage_path TEXT
);
```

### FTS5 全文搜索
```sql
CREATE VIRTUAL TABLE emails_fts USING fts5(
    subject,
    text_body,
    content='emails',
    content_rowid='id'
);

-- 触发器自动同步
CREATE TRIGGER emails_ai AFTER INSERT ON emails ...
CREATE TRIGGER emails_ad AFTER DELETE ON emails ...
CREATE TRIGGER emails_au AFTER UPDATE ON emails ...
```

---

## 🔌 API 端点

### 现有端点（已迁移到数据库）
- `GET /` - 服务信息
- `GET /status` - 服务状态
- `POST /webhook/email` - 接收邮件（带 X-Webhook-Secret 认证）
- `GET /verification_link` - 获取最新验证链接
- `GET /emails?page=1&per_page=20` - 获取邮件列表（支持分页）
- `POST /clear` - 清空数据

### 待实现端点（扩展 API）
- `GET /api/mailboxes` - 邮箱列表
- `GET /api/emails?folder=inbox&page=1` - 分页邮件列表（文件夹过滤）
- `GET /api/emails/<id>` - 单个邮件详情
- `PATCH /api/emails/<id>` - 更新邮件（已读、星标、文件夹）
- `DELETE /api/emails/<id>` - 删除邮件
- `GET /api/search?q=keyword` - 全文搜索

---

## 🚀 部署清单

### 1. 数据库迁移
```bash
# 设置环境变量
export DATABASE_URL="sqlite:///emails.db"

# 运行迁移
alembic upgrade head
```

### 2. Flask 应用
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python email_receiver.py
```

### 3. Cloudflare Worker
```bash
cd cloudflare

# 设置密钥
wrangler secret put WEBHOOK_SECRET
wrangler secret put FLASK_API_URL

# 部署
wrangler deploy
```

### 4. React 前端
```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm start

# 生产构建
npm run build
```

---

## 🔐 安全考虑

1. **Webhook 认证**
   - 使用共享密钥（X-Webhook-Secret header）
   - 防止伪造邮件注入

2. **CORS 配置**
   - 明确允许的源地址
   - 开发: localhost:3000, localhost:5173
   - 生产: 实际域名

3. **环境变量**
   - 敏感信息存储在 .env 文件
   - 不提交到版本控制

4. **HTML 消毒**
   - 使用 dompurify 清理邮件 HTML
   - 防止 XSS 攻击

---

## 🐛 已知问题

1. **邮件发送功能** - P2 优先级，待实现
2. **用户认证** - P1 优先级，待实现
3. **附件处理** - P2 优先级，待实现

---

## 📊 进度跟踪

**总任务**: 15 个
**已完成**: 10 个 (67%)
**进行中**: 0 个
**待开始**: 5 个 (33%)

**Phase 1: 基础设施** - ✅ 100%
**Phase 2: 前端开发** - ⏳ 60%
**Phase 3: 后端扩展** - 📋 0%
**Phase 4: 文档** - 📋 0%

---

## 📅 时间线

- **2026-01-29 09:00** - Ralplan 规划完成，Critic 审查通过
- **2026-01-29 09:30** - Ralph 执行模式启动
- **2026-01-29 10:00** - Phase 1 基础设施完成
- **2026-01-29 10:30** - Phase 2 前端 60% 完成（3 个组件）
- **2026-01-29 当前** - 等待剩余 5 个任务完成

---

## 🔄 下一步

1. 完成剩余前端组件（EmailView, ComposeModal）
2. 实现扩展 API 端点
3. 添加 Webhook 认证验证
4. 更新 README.md
5. Architect 最终验证

---

*文档由 Claude Sonnet 4.5 生成*
*最后更新: 2026-01-29*
