# API 文档 - EmailHandler 后端接口

**版本**: 3.0
**Base URL**: `http://localhost:5000`

---

## 🔐 认证

### Webhook 认证
Cloudflare Worker 到 Flask 的请求使用共享密钥认证：

**Header**: `X-Webhook-Secret: <your-secret>`
**配置**: 环境变量 `WEBHOOK_SECRET`

---

## 📬 邮件接收端点

### POST /webhook/email
接收来自 Cloudflare Email Worker 的邮件。

**认证**: 需要 `X-Webhook-Secret` header

**请求体**:
```json
{
  "from": "sender@example.com",
  "to": "recipient@yourdomain.com",
  "subject": "邮件主题",
  "html_body": "<html>...</html>",
  "text_body": "纯文本内容",
  "headers": {
    "date": "Wed, 29 Jan 2026 10:00:00 +0000",
    "message-id": "<unique-id@example.com>",
    "reply-to": "reply@example.com",
    "cc": "cc@example.com",
    "bcc": "bcc@example.com"
  },
  "attachments": [
    {
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "size": 12345
    }
  ]
}
```

**响应**:
```json
{
  "status": "success",
  "message": "邮件已接收"
}
```

**错误响应**:
```json
{
  "error": "Unauthorized",
  "message": "无效的 webhook 密钥"
}
```

---

## 📊 服务状态端点

### GET /
获取服务信息。

**响应**:
```json
{
  "service": "EmailHandler",
  "version": "3.0.0",
  "status": "running"
}
```

### GET /status
获取服务状态和统计信息。

**响应**:
```json
{
  "status": "ok",
  "email_count": 42,
  "database": "connected",
  "uptime": "2h 34m"
}
```

---

## 📧 邮件管理端点（向后兼容）

### GET /verification_link
获取最新验证链接（保持 v2.0 兼容）。

**查询参数**:
- `timeout` (可选) - 超时时间（秒），默认 120

**响应**:
```json
{
  "success": true,
  "link": "https://example.com/verify?token=abc123",
  "timestamp": "2026-01-29T10:00:00Z"
}
```

### GET /emails
获取所有邮件列表（带分页）。

**查询参数**:
- `page` (可选) - 页码，默认 1
- `per_page` (可选) - 每页数量，默认 20

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "from_address": "sender@example.com",
      "to_address": "you@yourdomain.com",
      "subject": "邮件主题",
      "text_body": "邮件内容预览...",
      "is_read": false,
      "received_at": "2026-01-29T10:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

### POST /clear
清空所有邮件和邮箱数据。

**响应**:
```json
{
  "status": "success",
  "message": "数据已清空"
}
```

---

## 🔌 扩展 API 端点（待实现）

### GET /api/mailboxes
获取所有邮箱列表。

**响应**:
```json
[
  {
    "id": 1,
    "email": "user@yourdomain.com",
    "display_name": "用户名",
    "created_at": "2026-01-29T10:00:00Z"
  }
]
```

### GET /api/emails
获取邮件列表（支持文件夹过滤和分页）。

**查询参数**:
- `folder` (可选) - 文件夹名称（inbox, sent, trash）
- `page` (可选) - 页码，默认 1
- `per_page` (可选) - 每页数量，默认 20

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "mailbox_id": 1,
      "message_id": "<unique@example.com>",
      "from_address": "sender@example.com",
      "to_address": "you@yourdomain.com",
      "subject": "邮件主题",
      "html_body": "<html>...</html>",
      "text_body": "纯文本内容",
      "is_read": false,
      "is_starred": false,
      "folder": "inbox",
      "received_at": "2026-01-29T10:00:00Z",
      "verification_link": "https://example.com/verify?token=abc"
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
```

### GET /api/emails/:id
获取单个邮件详情。

**路径参数**:
- `id` - 邮件 ID

**响应**:
```json
{
  "id": 1,
  "mailbox_id": 1,
  "message_id": "<unique@example.com>",
  "from_address": "sender@example.com",
  "to_address": "you@yourdomain.com",
  "subject": "邮件主题",
  "html_body": "<html>完整邮件内容</html>",
  "text_body": "完整纯文本内容",
  "is_read": false,
  "is_starred": false,
  "folder": "inbox",
  "received_at": "2026-01-29T10:00:00Z",
  "raw_headers": "Date: ...\nFrom: ...",
  "attachments": [
    {
      "id": 1,
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "size": 12345,
      "storage_path": "/path/to/file"
    }
  ]
}
```

### PATCH /api/emails/:id
更新邮件状态。

**路径参数**:
- `id` - 邮件 ID

**请求体**:
```json
{
  "is_read": true,
  "is_starred": true,
  "folder": "trash"
}
```

**响应**:
```json
{
  "id": 1,
  "is_read": true,
  "is_starred": true,
  "folder": "trash"
}
```

### DELETE /api/emails/:id
删除邮件。

**路径参数**:
- `id` - 邮件 ID

**响应**:
```json
{
  "status": "success",
  "message": "邮件已删除"
}
```

### GET /api/search
全文搜索邮件。

**查询参数**:
- `q` - 搜索关键词

**响应**:
```json
[
  {
    "id": 1,
    "from_address": "sender@example.com",
    "subject": "包含关键词的邮件",
    "text_body": "邮件内容包含搜索关键词...",
    "received_at": "2026-01-29T10:00:00Z"
  }
]
```

---

## 📮 邮件发送端点（P2 - 待实现）

### POST /api/send
发送邮件（使用 SendGrid SMTP）。

**请求体**:
```json
{
  "from": "you@yourdomain.com",
  "to": "recipient@example.com",
  "subject": "邮件主题",
  "body": "邮件内容",
  "html": "<html>HTML 内容</html>"
}
```

**响应**:
```json
{
  "status": "sent",
  "message_id": "<sent-id@yourdomain.com>",
  "timestamp": "2026-01-29T10:00:00Z"
}
```

---

## 🔒 认证端点（P1 - 待实现）

### POST /api/login
用户登录。

**请求体**:
```json
{
  "email": "user@yourdomain.com",
  "password": "password"
}
```

**响应**:
```json
{
  "access_token": "jwt-token",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### POST /api/register
用户注册。

**请求体**:
```json
{
  "email": "user@yourdomain.com",
  "password": "password",
  "display_name": "用户名"
}
```

**响应**:
```json
{
  "id": 1,
  "email": "user@yourdomain.com",
  "display_name": "用户名"
}
```

---

## ⚠️ 错误响应

所有错误遵循统一格式：

```json
{
  "error": "错误类型",
  "message": "详细错误信息",
  "status_code": 400
}
```

**常见错误码**:
- `400` - 请求参数错误
- `401` - 未授权（Webhook 密钥无效）
- `404` - 资源不存在
- `500` - 服务器内部错误

---

## 🔧 CORS 配置

**允许的源地址**（通过环境变量 `CORS_ORIGINS` 配置）:
- 开发环境: `http://localhost:3000`, `http://localhost:5173`
- 生产环境: 实际域名

**允许的方法**: GET, POST, PATCH, DELETE, OPTIONS
**允许的 Headers**: Content-Type, Authorization, X-Webhook-Secret

---

*API 文档由 Claude Sonnet 4.5 生成*
*最后更新: 2026-01-29*
