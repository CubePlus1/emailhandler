# Cloudflare Email UI - Implementation Plan

## Context

### Original Request
扩展现有的 EmailHandler 邮件认证框架为完整的域名邮箱系统，集成 Cloudflare Email Routing，并提供现代化 UI 界面。

### Current Codebase Analysis

**Existing Architecture:**
```
emailhandler/
├── emailhandler/                 # Python 包 (核心模块)
│   ├── __init__.py              # 模块导出 (v2.0.0)
│   ├── email_monitor.py         # 邮件监控，轮询 API 获取验证链接
│   └── link_handler.py          # HTTP 请求处理验证链接
├── email_receiver.py            # Flask 服务 (端口 5000)
│   ├── POST /webhook/email      # 接收邮件 webhook
│   ├── GET /verification_link   # 获取最新验证链接
│   ├── GET /emails              # 查看所有邮件
│   └── POST /clear              # 清空数据
├── verify.py                    # CLI 验证工具
├── show_emails.py               # 邮件列表查看工具
└── pyproject.toml               # Python 3.9+, flask>=3.1.2, requests>=2.31.0
```

**Current Limitations:**
1. 数据存储在内存中 (`emails = []`, `verification_links = []`)
2. 无持久化存储
3. 无用户认证
4. 仅支持 webhook 接收，无主动邮件收发
5. 无 UI 界面

### Research Findings

**Cloudflare Email Routing:**
- 支持将域名邮件路由到 Worker 或外部地址
- Email Workers 可以处理入站邮件 (解析、存储、转发)
- 需要域名已添加到 Cloudflare

**UI Framework Options:**
| Option | Pros | Cons |
|--------|------|------|
| Roundcube | 成熟、功能完整 | PHP 依赖、难集成 |
| Rainloop | 轻量、现代 | PHP 依赖 |
| React SPA | 完全可控、现代 | 需从头构建 |
| Vue SPA | 响应式、易上手 | 需从头构建 |

**推荐方案:** 自建 React SPA + Python Flask API

---

## Work Objectives

### Core Objective
将 EmailHandler 从验证链接处理工具扩展为完整的域名邮箱系统，支持：
1. 通过 Cloudflare Email Routing 接收域名邮件
2. 通过 Cloudflare API 发送邮件
3. 现代化 Web UI (收件箱、发件、搜索)

### Deliverables

| # | Deliverable | Priority |
|---|-------------|----------|
| 1 | Cloudflare Worker 邮件接收器 | P0 |
| 2 | 持久化存储层 (SQLite/PostgreSQL) | P0 |
| 3 | 扩展 Flask API (完整邮箱操作) | P0 |
| 4 | React 前端 UI | P0 |
| 5 | 邮件发送功能 | P2 |
| 6 | 用户认证系统 | P1 |
| 7 | 附件处理 | P2 |

### Definition of Done
- [ ] 可通过域名邮箱地址接收邮件
- [ ] 邮件持久化存储在数据库中
- [ ] Web UI 可查看收件箱、阅读邮件
- [ ] 可通过 UI 发送邮件
- [ ] 邮件搜索功能可用
- [ ] 所有现有 API 端点保持兼容

---

## Guardrails

### Must Have
- 保持现有 `/webhook/email`, `/verification_link`, `/emails`, `/clear` API 兼容
- 使用 TypeScript 开发前端
- 数据库迁移脚本
- 环境变量配置敏感信息
- Webhook 认证机制 (X-Webhook-Secret header)
- CORS 配置明确允许的源地址

### Must NOT Have
- 不存储明文密码
- 不暴露 Cloudflare API Token 到前端
- 不删除现有功能

---

## Architecture Design

### System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
│                    React SPA (Port 3000)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Flask API (Port 5000)                        │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐      │
│  │  /api/mail  │ /api/send   │ /api/search │  /webhook   │      │
│  └─────────────┴─────────────┴─────────────┴─────────────┘      │
│                              │                                   │
│                    ┌─────────┴─────────┐                        │
│                    │   Storage Layer   │                        │
│                    │ SQLite/PostgreSQL │                        │
│                    └───────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ POST /webhook/email
┌─────────────────────────────────────────────────────────────────┐
│                  Cloudflare Email Worker                         │
│         (Receives email → Parses → Forwards to API)             │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Email Routing
┌─────────────────────────────────────────────────────────────────┐
│                    Cloudflare DNS                                │
│              MX Records → Email Routing                          │
└─────────────────────────────────────────────────────────────────┘
```

### Email Flow
1. 邮件发送到 `*@yourdomain.com`
2. Cloudflare Email Routing 接收邮件
3. Email Worker 解析邮件 (from, to, subject, body, attachments)
4. Worker POST 到 Flask `/webhook/email`
5. Flask 存储到数据库
6. React UI 通过 API 获取并展示

### Database Schema
```sql
-- 邮箱账户
CREATE TABLE mailboxes (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 邮件
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
    folder TEXT DEFAULT 'inbox',  -- inbox, sent, trash, spam
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_link TEXT,  -- 保持兼容
    raw_headers TEXT
);

-- 附件
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY,
    email_id INTEGER REFERENCES emails(id),
    filename TEXT,
    content_type TEXT,
    size INTEGER,
    storage_path TEXT
);

-- 索引
CREATE INDEX idx_emails_mailbox ON emails(mailbox_id);
CREATE INDEX idx_emails_folder ON emails(folder);
CREATE INDEX idx_emails_received ON emails(received_at DESC);

-- 全文搜索 (SQLite FTS5 虚拟表)
CREATE VIRTUAL TABLE emails_fts USING fts5(
    subject,
    text_body,
    content='emails',
    content_rowid='id'
);

-- FTS5 触发器保持同步
CREATE TRIGGER emails_ai AFTER INSERT ON emails BEGIN
    INSERT INTO emails_fts(rowid, subject, text_body) VALUES (new.id, new.subject, new.text_body);
END;
CREATE TRIGGER emails_ad AFTER DELETE ON emails BEGIN
    INSERT INTO emails_fts(emails_fts, rowid, subject, text_body) VALUES('delete', old.id, old.subject, old.text_body);
END;
CREATE TRIGGER emails_au AFTER UPDATE ON emails BEGIN
    INSERT INTO emails_fts(emails_fts, rowid, subject, text_body) VALUES('delete', old.id, old.subject, old.text_body);
    INSERT INTO emails_fts(rowid, subject, text_body) VALUES (new.id, new.subject, new.text_body);
END;
```

---

## Task Flow

```
Phase 1: Foundation (P0)
├── Task 1.1: Database Layer
│   ├── Create models.py with SQLAlchemy models
│   ├── Create migrations
│   └── Update email_receiver.py to use DB
│
├── Task 1.2: Extended API
│   ├── GET /api/mailboxes
│   ├── GET /api/emails?folder=inbox&page=1
│   ├── GET /api/emails/<id>
│   ├── PATCH /api/emails/<id> (read, star, move)
│   ├── DELETE /api/emails/<id>
│   └── GET /api/search?q=keyword
│
└── Task 1.3: Cloudflare Worker
    ├── Create worker script
    ├── Configure email routing
    └── Test email reception

Phase 2: Frontend (P0)
├── Task 2.1: React Project Setup
│   ├── Create React app with TypeScript
│   ├── Configure Tailwind CSS
│   └── Setup routing (react-router)
│
├── Task 2.2: Core Components
│   ├── MailboxLayout (sidebar + main)
│   ├── EmailList (inbox view)
│   ├── EmailView (single email)
│   ├── ComposeModal (write email)
│   └── SearchBar
│
└── Task 2.3: API Integration
    ├── Create API client (axios/fetch)
    ├── Connect components to API
    └── Real-time updates (polling/WebSocket)

Phase 3: Send Email (P2)
├── Task 3.1: SMTP/API Integration
│   ├── Integrate SendGrid SMTP as primary provider
│   ├── Implement send endpoint
│   └── Connect to compose UI
│
└── Task 3.2: Authentication
    ├── Add JWT auth to API
    ├── Login/register UI
    └── Protect routes

Phase 4: Polish (P2)
├── Task 4.1: Attachments
├── Task 4.2: Mobile responsive
└── Task 4.3: Dark mode
```

---

## Detailed TODOs

### Phase 1: Foundation

#### TODO 1.1.1: Create Database Models
**File:** `emailhandler/models.py` (NEW)
**Acceptance Criteria:**
- [ ] SQLAlchemy models for Mailbox, Email, Attachment
- [ ] Relationship mappings defined
- [ ] Indexes for performance

#### TODO 1.1.2: Database Migration Setup
**File:** `migrations/` (NEW directory)
**Acceptance Criteria:**
- [ ] Alembic configured
- [ ] Initial migration creates all tables
- [ ] `alembic upgrade head` works

#### TODO 1.1.3: Update Email Receiver for DB
**File:** `email_receiver.py` (MODIFY)
**Functions to Modify:**
| Function | Lines | Changes |
|----------|-------|---------|
| Global variables | 15-17 | Replace `emails = []`, `verification_links = []` with DB session |
| `status()` | 58-66 | Query count from DB instead of `len(emails)` |
| `receive_email()` | 69-110 | Insert into DB instead of appending to list |
| `get_verification_link()` | 113-129 | Query latest link from DB |
| `get_emails()` | 132-138 | Query from DB with pagination support |
| `clear_data()` | 141-152 | Delete from DB tables instead of resetting lists |

**Changes:**
- Replace in-memory `emails = []` with DB session
- Update `receive_email()` to insert into DB
- Update `get_verification_link()` to query from DB
- Update `get_emails()` to query from DB with pagination
- Update `clear_data()` to delete from DB
- Update `status()` to count from DB
- Keep backward compatibility for all existing endpoints

#### TODO 1.2.1: Extended API Endpoints
**File:** `email_receiver.py` (MODIFY) or `api/routes.py` (NEW)
**New Endpoints:**
```python
GET  /api/mailboxes              # List all mailboxes
GET  /api/emails                 # List emails (pagination, folder filter)
GET  /api/emails/<id>            # Get single email
PATCH /api/emails/<id>           # Update email (read, star, folder)
DELETE /api/emails/<id>          # Delete email
GET  /api/search                 # Full-text search
```
**Acceptance Criteria:**
- [ ] All endpoints return JSON
- [ ] Pagination works (page, per_page)
- [ ] Folder filtering works
- [ ] Search returns relevant results

#### TODO 1.3.1: Cloudflare Email Worker
**File:** `cloudflare/worker.js` (NEW)
**Acceptance Criteria:**
- [ ] Handles `email` event
- [ ] Parses email headers, body, attachments
- [ ] POSTs to Flask webhook
- [ ] Error handling and logging

#### TODO 1.3.2: Cloudflare Wrangler Config
**File:** `cloudflare/wrangler.toml` (NEW)
**Acceptance Criteria:**
- [ ] Worker name configured
- [ ] Environment variables for API URL
- [ ] Email routing trigger

#### TODO 1.3.3: Webhook Authentication
**File:** `email_receiver.py` (MODIFY) + `cloudflare/worker.js` (MODIFY)
**Security Requirement:** Prevent forged email submissions via shared secret authentication.
**Implementation:**
```
Flask side:
- Read WEBHOOK_SECRET from environment variable
- Validate X-Webhook-Secret header on POST /webhook/email
- Return 401 if secret missing or invalid

Cloudflare Worker side:
- Configure WEBHOOK_SECRET as Worker environment variable
- Include X-Webhook-Secret header in POST request to Flask
```
**Acceptance Criteria:**
- [ ] Flask rejects requests without valid X-Webhook-Secret header
- [ ] Cloudflare Worker sends correct secret in requests
- [ ] Secret is configured via environment variables (never hardcoded)
- [ ] Clear error message returned for authentication failures

### Phase 2: Frontend

#### TODO 2.1.1: React Project Setup
**Directory:** `frontend/` (NEW)
**Commands:**
```bash
npx create-react-app frontend --template typescript
cd frontend
npm install tailwindcss postcss autoprefixer
npm install react-router-dom axios
npm install @headlessui/react @heroicons/react
npx tailwindcss init -p
```
**Acceptance Criteria:**
- [ ] `npm start` runs dev server
- [ ] Tailwind CSS working
- [ ] TypeScript strict mode

#### TODO 2.2.1: Layout Component
**File:** `frontend/src/components/Layout.tsx` (NEW)
**Acceptance Criteria:**
- [ ] Sidebar with folders (Inbox, Sent, Trash)
- [ ] Main content area
- [ ] Responsive design

#### TODO 2.2.2: Email List Component
**File:** `frontend/src/components/EmailList.tsx` (NEW)
**Acceptance Criteria:**
- [ ] Displays email list with sender, subject, preview, time
- [ ] Click to select email
- [ ] Read/unread visual distinction
- [ ] Infinite scroll or pagination

#### TODO 2.2.3: Email View Component
**File:** `frontend/src/components/EmailView.tsx` (NEW)
**Acceptance Criteria:**
- [ ] Shows full email content
- [ ] HTML rendering (sanitized)
- [ ] Actions: reply, delete, star

#### TODO 2.2.4: Compose Modal
**File:** `frontend/src/components/ComposeModal.tsx` (NEW)
**Acceptance Criteria:**
- [ ] To, Subject, Body fields
- [ ] Rich text editor (optional)
- [ ] Send button triggers API

#### TODO 2.3.1: API Client
**File:** `frontend/src/api/client.ts` (NEW)
**Acceptance Criteria:**
- [ ] Axios instance with base URL
- [ ] Type definitions for Email, Mailbox
- [ ] Error handling wrapper

### Phase 3: Send Email (P2 - Deferred)

#### TODO 3.1.1: Send Email Endpoint
**File:** `email_receiver.py` (MODIFY) or `api/routes.py`
**Endpoint:** `POST /api/send`
**Provider:** SendGrid SMTP (confirmed decision)
**Body:**
```json
{
  "from": "user@domain.com",
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Email content"
}
```
**Acceptance Criteria:**
- [ ] Validates input
- [ ] Sends via SendGrid SMTP API
- [ ] Saves to Sent folder
- [ ] Returns delivery status

**Note:** This is P2 priority. Complete P0 (receive email) functionality first.

#### TODO 3.2.1: JWT Authentication
**File:** `emailhandler/auth.py` (NEW)
**Acceptance Criteria:**
- [ ] `/api/login` returns JWT
- [ ] Protected routes require valid token
- [ ] Token refresh mechanism

---

## Commit Strategy

| Commit # | Description | Files |
|----------|-------------|-------|
| 1 | Add database models and migrations | `models.py`, `migrations/` |
| 2 | Update email_receiver to use DB | `email_receiver.py` |
| 3 | Add extended API endpoints | `email_receiver.py` or `api/routes.py` |
| 4 | Add Cloudflare Email Worker | `cloudflare/worker.js`, `wrangler.toml` |
| 5 | Initialize React frontend | `frontend/` |
| 6 | Add core UI components | `frontend/src/components/` |
| 7 | Connect frontend to API | `frontend/src/api/` |
| 8 | Add email sending | `email_receiver.py`, `ComposeModal.tsx` |
| 9 | Add authentication | `auth.py`, `Login.tsx` |

---

## Success Criteria

### Functional Requirements
- [ ] 域名邮件可以被接收并存储
- [ ] UI 可以显示收件箱邮件列表
- [ ] 可以阅读单封邮件内容
- [ ] 可以搜索邮件
- [ ] 可以发送邮件
- [ ] 现有 `/webhook/email` API 保持兼容

### Performance Requirements
- [ ] 邮件列表加载 < 500ms (100 封邮件)
- [ ] 搜索响应 < 1s
- [ ] UI 首次加载 < 3s

### Quality Requirements
- [ ] TypeScript 无类型错误
- [ ] Python linting 通过
- [ ] 核心功能有测试覆盖

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Cloudflare Worker 调试困难 | Medium | High | 使用 Miniflare 本地开发 |
| 邮件发送配额限制 | High | Medium | 研究 Cloudflare 发送限制，备选 SMTP |
| 大附件存储 | Medium | Medium | 使用 Cloudflare R2 或 S3 |
| 垃圾邮件过滤 | Low | High | 后续迭代添加 |

---

## Technical Decisions

### Database Choice
**Decision:** SQLite (开发) + PostgreSQL (生产)
**Rationale:** SQLite 零配置便于开发，PostgreSQL 支持全文搜索和高并发

### Frontend Framework
**Decision:** React + TypeScript + Tailwind CSS
**Rationale:** 广泛采用、类型安全、快速开发

### Email Sending
**Decision:** SendGrid SMTP API (P2 priority)
**Rationale:** Cloudflare Email Routing 仅支持接收，不支持发送。SendGrid 提供可靠的 SMTP 服务，有免费额度，API 文档完善。
**Priority:** P2 - 先完成邮件接收核心功能，发送功能后续迭代。

---

## Dependencies to Install

### Python (Backend)
```
flask>=3.1.2
flask-sqlalchemy>=3.0
flask-migrate>=4.0
flask-cors>=4.0
pyjwt>=2.8
python-dotenv>=1.0
```

### Node.js (Frontend)
```
react@18
react-dom@18
react-router-dom@6
typescript@5
tailwindcss@3
axios@1
@headlessui/react@1
@heroicons/react@2
dompurify@3
```

### Cloudflare
```
wrangler@3
```

---

## File Structure After Implementation

```
emailhandler/
├── emailhandler/
│   ├── __init__.py
│   ├── models.py           # NEW: SQLAlchemy models
│   ├── auth.py             # NEW: JWT authentication
│   ├── email_monitor.py
│   └── link_handler.py
├── api/
│   ├── __init__.py         # NEW
│   └── routes.py           # NEW: Extended API routes
├── migrations/             # NEW: Alembic migrations
├── cloudflare/
│   ├── worker.js           # NEW: Email Worker
│   └── wrangler.toml       # NEW: Worker config
├── frontend/               # NEW: React app
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── EmailList.tsx
│   │   │   ├── EmailView.tsx
│   │   │   ├── ComposeModal.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── pages/
│   │   │   ├── Inbox.tsx
│   │   │   └── Login.tsx
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
├── email_receiver.py       # MODIFIED: Use DB
├── verify.py
├── pyproject.toml          # MODIFIED: New dependencies
├── .env.example            # NEW: Environment template
└── README.md               # MODIFIED: Updated docs
```

### Environment Variables (.env.example)
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///emails.db
# For production: DATABASE_URL=postgresql://user:pass@host:5432/emailhandler

# Webhook Authentication
WEBHOOK_SECRET=your-webhook-secret-here

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
# For production: CORS_ORIGINS=https://mail.yourdomain.com

# SendGrid SMTP (P2 - Email Sending)
SENDGRID_API_KEY=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### CORS Configuration
| Environment | Allowed Origins |
|-------------|-----------------|
| Development | `http://localhost:3000`, `http://localhost:5173` |
| Production | `https://mail.yourdomain.com` (your actual domain) |

---

## Estimated Effort

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Foundation | 6 | 8-12 hours |
| Phase 2: Frontend | 5 | 10-15 hours |
| Phase 3: Send Email | 2 | 4-6 hours |
| Phase 4: Polish | 3 | 4-6 hours |
| **Total** | **16** | **26-39 hours** |

---

*Plan generated by Prometheus Planner*
*Last updated: 2026-01-29*
