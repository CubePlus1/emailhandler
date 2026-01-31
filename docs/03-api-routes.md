# API 路由文档

本文档详细说明了邮件管理系统提供的所有 REST API 端点。

## 基础信息

- **基础 URL**: `http://localhost:5000/api`
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

---

## API 端点列表

### 1. 获取所有邮箱

获取系统中配置的所有邮箱账户列表。

**端点**: `GET /api/mailboxes`

**请求参数**: 无

**响应格式**:

```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "display_name": "用户名",
    "created_at": "2024-01-01T12:00:00"
  }
]
```

**字段说明**:
- `id`: 邮箱唯一标识符
- `email`: 邮箱地址
- `display_name`: 显示名称
- `created_at`: 创建时间（ISO 8601 格式）

**状态码**:
- `200 OK`: 成功
- `500 Internal Server Error`: 服务器错误

**curl 示例**:

```bash
curl -X GET http://localhost:5000/api/mailboxes
```

**错误响应示例**:

```json
{
  "success": false,
  "message": "数据库连接失败"
}
```

---

### 2. 获取单个邮件详情

根据邮件 ID 获取完整的邮件内容，包括附件信息。

**端点**: `GET /api/emails/:id`

**URL 参数**:
- `id` (必需): 邮件 ID（整数）

**响应格式**:

```json
{
  "id": 123,
  "mailbox_id": 1,
  "message_id": "<message@example.com>",
  "from_address": "sender@example.com",
  "to_address": "receiver@example.com",
  "subject": "邮件主题",
  "html_body": "<html>...</html>",
  "text_body": "纯文本内容",
  "verification_link": "https://example.com/verify/abc123",
  "is_read": false,
  "is_starred": false,
  "folder": "inbox",
  "received_at": "2024-01-01T12:30:00",
  "attachments": [
    {
      "id": 1,
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "size": 102400
    }
  ]
}
```

**字段说明**:
- `id`: 邮件唯一标识符
- `mailbox_id`: 所属邮箱 ID
- `message_id`: RFC 822 消息 ID
- `from_address`: 发件人地址
- `to_address`: 收件人地址
- `subject`: 邮件主题
- `html_body`: HTML 格式正文
- `text_body`: 纯文本格式正文
- `verification_link`: 提取的验证链接（如有）
- `is_read`: 是否已读
- `is_starred`: 是否已标星
- `folder`: 所在文件夹（inbox/sent/trash/archive）
- `received_at`: 接收时间（ISO 8601 格式）
- `attachments`: 附件列表
  - `filename`: 文件名
  - `content_type`: MIME 类型
  - `size`: 文件大小（字节）

**状态码**:
- `200 OK`: 成功
- `404 Not Found`: 邮件不存在
- `500 Internal Server Error`: 服务器错误

**curl 示例**:

```bash
curl -X GET http://localhost:5000/api/emails/123
```

**错误响应示例**:

```json
{
  "success": false,
  "message": "邮件不存在"
}
```

---

### 3. 更新邮件

更新邮件的状态标记和文件夹位置。

**端点**: `PATCH /api/emails/:id`

**URL 参数**:
- `id` (必需): 邮件 ID（整数）

**请求体**:

```json
{
  "is_read": true,
  "is_starred": false,
  "folder": "archive"
}
```

**可更新字段**:
- `is_read` (可选): 已读状态（布尔值）
- `is_starred` (可选): 星标状态（布尔值）
- `folder` (可选): 文件夹名称（字符串：inbox/sent/trash/archive）

**响应格式**:

```json
{
  "success": true,
  "message": "邮件已更新",
  "email": {
    "id": 123,
    "is_read": true,
    "is_starred": false,
    "folder": "archive"
  }
}
```

**状态码**:
- `200 OK`: 成功
- `404 Not Found`: 邮件不存在
- `500 Internal Server Error`: 服务器错误

**curl 示例**:

```bash
# 标记为已读
curl -X PATCH http://localhost:5000/api/emails/123 \
  -H "Content-Type: application/json" \
  -d '{"is_read": true}'

# 添加星标并移动到归档
curl -X PATCH http://localhost:5000/api/emails/123 \
  -H "Content-Type: application/json" \
  -d '{"is_starred": true, "folder": "archive"}'
```

**错误响应示例**:

```json
{
  "success": false,
  "message": "数据库更新失败"
}
```

---

### 4. 删除邮件

永久删除指定邮件及其所有附件。

**端点**: `DELETE /api/emails/:id`

**URL 参数**:
- `id` (必需): 邮件 ID（整数）

**请求参数**: 无

**响应格式**:

```json
{
  "success": true,
  "message": "邮件已删除"
}
```

**状态码**:
- `200 OK`: 成功
- `404 Not Found`: 邮件不存在
- `500 Internal Server Error`: 服务器错误

**curl 示例**:

```bash
curl -X DELETE http://localhost:5000/api/emails/123
```

**注意事项**:
- 删除操作不可逆
- 同时删除所有关联的附件记录
- 如需软删除，建议使用 PATCH 方法将 `folder` 设置为 `trash`

**错误响应示例**:

```json
{
  "success": false,
  "message": "邮件不存在"
}
```

---

### 5. 全文搜索邮件

在邮件内容中搜索关键词，支持主题、正文、发件人等字段。

**端点**: `GET /api/search`

**Query 参数**:
- `q` (必需): 搜索关键词（字符串，最小长度 1）

**搜索范围**:
- 邮件主题 (`subject`)
- 纯文本正文 (`text_body`)
- HTML 正文 (`html_body`)
- 发件人地址 (`from_address`)

**响应格式**:

```json
{
  "success": true,
  "count": 2,
  "query": "验证码",
  "emails": [
    {
      "id": 456,
      "from_address": "noreply@service.com",
      "to_address": "user@example.com",
      "subject": "您的验证码",
      "received_at": "2024-01-02T10:00:00",
      "is_read": false,
      "is_starred": false,
      "folder": "inbox",
      "verification_link": "https://service.com/verify/xyz789"
    }
  ]
}
```

**字段说明**:
- `success`: 请求是否成功
- `count`: 匹配结果数量
- `query`: 搜索关键词
- `emails`: 匹配的邮件列表（按接收时间倒序排列）

**限制**:
- 最多返回 100 条结果
- 使用 LIKE 模糊匹配（性能优化建议使用 FTS5 全文索引）

**状态码**:
- `200 OK`: 成功
- `400 Bad Request`: 搜索关键词为空
- `500 Internal Server Error`: 服务器错误

**curl 示例**:

```bash
# 搜索包含"验证码"的邮件
curl -X GET "http://localhost:5000/api/search?q=验证码"

# URL 编码示例
curl -X GET "http://localhost:5000/api/search?q=%E9%AA%8C%E8%AF%81%E7%A0%81"
```

**错误响应示例**:

```json
{
  "success": false,
  "message": "搜索关键词不能为空"
}
```

---

## 错误处理

所有 API 端点遵循统一的错误响应格式：

```json
{
  "success": false,
  "message": "错误描述信息"
}
```

### HTTP 状态码说明

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 200 | 成功 | 请求成功处理 |
| 400 | 请求错误 | 参数缺失或格式错误 |
| 404 | 未找到 | 资源不存在 |
| 500 | 服务器错误 | 数据库错误或内部异常 |

---

## 分页支持

当前版本的搜索端点限制返回 100 条结果。未来版本将支持分页参数：

**计划中的分页参数**:
- `page`: 页码（默认 1）
- `per_page`: 每页数量（默认 20，最大 100）

**计划中的分页响应**:

```json
{
  "success": true,
  "count": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8,
  "emails": [...]
}
```

---

## 使用示例

### 完整工作流示例

```bash
# 1. 获取所有邮箱
curl -X GET http://localhost:5000/api/mailboxes

# 2. 搜索包含"订单"的邮件
curl -X GET "http://localhost:5000/api/search?q=订单"

# 3. 查看邮件详情
curl -X GET http://localhost:5000/api/emails/123

# 4. 标记为已读
curl -X PATCH http://localhost:5000/api/emails/123 \
  -H "Content-Type: application/json" \
  -d '{"is_read": true}'

# 5. 归档邮件
curl -X PATCH http://localhost:5000/api/emails/123 \
  -H "Content-Type: application/json" \
  -d '{"folder": "archive"}'

# 6. 删除邮件
curl -X DELETE http://localhost:5000/api/emails/123
```

### Python 客户端示例

```python
import requests

BASE_URL = "http://localhost:5000/api"

# 获取所有邮箱
response = requests.get(f"{BASE_URL}/mailboxes")
mailboxes = response.json()

# 搜索邮件
response = requests.get(f"{BASE_URL}/search", params={"q": "验证码"})
search_results = response.json()

# 更新邮件状态
response = requests.patch(
    f"{BASE_URL}/emails/123",
    json={"is_read": True, "is_starred": True}
)
result = response.json()
```

### JavaScript (fetch) 示例

```javascript
const BASE_URL = 'http://localhost:5000/api';

// 获取邮件详情
async function getEmailDetail(emailId) {
  const response = await fetch(`${BASE_URL}/emails/${emailId}`);
  return await response.json();
}

// 更新邮件
async function updateEmail(emailId, updates) {
  const response = await fetch(`${BASE_URL}/emails/${emailId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  });
  return await response.json();
}

// 搜索邮件
async function searchEmails(keyword) {
  const response = await fetch(`${BASE_URL}/search?q=${encodeURIComponent(keyword)}`);
  return await response.json();
}
```

---

## 注意事项

1. **字符编码**: 所有请求和响应均使用 UTF-8 编码
2. **日期格式**: 统一使用 ISO 8601 格式（`YYYY-MM-DDTHH:MM:SS`）
3. **布尔值**: JSON 中使用 `true`/`false`（小写）
4. **空值处理**: 空字段返回 `null`
5. **事务安全**: 更新和删除操作支持自动回滚
6. **并发控制**: 当前未实现乐观锁，高并发场景需注意

---

## 相关文档

- [数据库模型文档](./01-database-models.md)
- [邮件处理流程](./02-email-processing.md)
- [部署指南](./04-deployment.md)
