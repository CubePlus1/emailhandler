# Webhook 处理文档

## 概述

本系统提供 Webhook 端点用于接收来自 Cloudflare Email Routing 或其他邮件服务的推送邮件。Webhook 处理模块负责解析邮件内容、提取验证链接并存储到数据库。

## Webhook 端点详解

### 端点信息

- **URL**: `POST /webhook/email`
- **认证方式**: 自定义请求头 `X-Webhook-Secret`
- **Content-Type**: `application/json`
- **响应格式**: JSON

### 请求示例

```bash
curl -X POST https://your-domain.com/webhook/email \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-webhook-secret" \
  -d '{
    "from": "sender@example.com",
    "to": "recipient@yourdomain.com",
    "subject": "Verify your email address",
    "html": "<html><body><a href=\"https://example.com/verify?token=abc123\">Verify</a></body></html>",
    "text": "Click here to verify: https://example.com/verify?token=abc123",
    "message_id": "unique-message-id@example.com"
  }'
```

## 认证机制

### 环境变量配置

在 `.env` 文件中设置 Webhook 密钥：

```env
WEBHOOK_SECRET=your-secure-random-string-here
```

**建议生成方式**：

```bash
# Linux/macOS
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 认证流程

1. 客户端在请求头中包含 `X-Webhook-Secret`
2. 服务器验证密钥是否与环境变量 `WEBHOOK_SECRET` 匹配
3. 验证失败返回 `401 Unauthorized`

```python
# 认证验证代码
webhook_secret = os.getenv('WEBHOOK_SECRET')
if webhook_secret:
    request_secret = request.headers.get('X-Webhook-Secret')
    if request_secret != webhook_secret:
        return jsonify({
            'error': 'Unauthorized',
            'message': '无效的 webhook 密钥'
        }), 401
```

## 请求数据格式

### 必需字段

| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `from` | string | 发件人邮箱地址 | "unknown" |
| `to` | string | 收件人邮箱地址 | "unknown" |
| `subject` | string | 邮件主题 | "No Subject" |
| `html` | string | HTML 格式邮件内容 | "" |
| `text` | string | 纯文本格式邮件内容 | "" |
| `message_id` | string | 邮件唯一标识符 | 自动生成 |

### 完整请求体示例

```json
{
  "from": "noreply@service.com",
  "to": "user@yourdomain.com",
  "subject": "Confirm your registration",
  "html": "<html><body><p>Welcome!</p><a href=\"https://service.com/verify?token=xyz789\">Verify Email</a></body></html>",
  "text": "Welcome! Verify your email: https://service.com/verify?token=xyz789",
  "message_id": "20240115123456@service.com"
}
```

## 邮件解析流程

### 处理步骤

1. **验证 Webhook 密钥**
   - 检查 `X-Webhook-Secret` 请求头
   - 与环境变量对比验证

2. **提取邮件信息**
   - 解析 JSON 请求体
   - 提取发件人、收件人、主题、内容等字段

3. **提取验证链接**
   - 优先从 HTML 内容提取
   - 如无 HTML 则从纯文本提取
   - 使用 5 个正则表达式模式匹配

4. **数据库操作**
   - 查找或创建邮箱记录
   - 创建邮件记录
   - 存储验证链接

5. **返回响应**
   - 成功: `200 OK` + 验证链接
   - 失败: `400 Bad Request` + 错误信息

## 验证链接提取逻辑

### 正则表达式模式

系统使用 5 个正则表达式模式按优先级匹配验证链接：

```python
patterns = [
    # 模式 1: 包含 "verify" 的链接
    r'href=["\']?(https?://[^\s"\'<>]+verify[^\s"\'<>]*)',

    # 模式 2: 包含 "confirmation" 的链接
    r'href=["\']?(https?://[^\s"\'<>]+confirmation[^\s"\'<>]*)',

    # 模式 3: 包含 "validate" 的链接
    r'href=["\']?(https?://[^\s"\'<>]+validate[^\s"\'<>]*)',

    # 模式 4: 包含 "confirm" 的链接
    r'href=["\']?(https?://[^\s"\'<>]+confirm[^\s"\'<>]*)',

    # 模式 5: 通用验证链接模式（无 href 属性）
    r'(https?://[^\s<>]+(?:verify|verification|confirm|confirmation)[^\s<>]*)',
]
```

### 支持的验证链接示例

- `https://example.com/verify?token=abc123`
- `https://example.com/email/confirmation/xyz789`
- `https://example.com/account/validate?code=def456`
- `https://example.com/confirm-email?key=ghi789`
- `https://example.com/verification/jkl012`

### 提取优先级

1. 优先匹配 HTML `href` 属性中的链接
2. 按照模式顺序依次尝试
3. 返回第一个匹配成功的链接
4. 未找到任何匹配则返回 `None`

## Cloudflare Email Routing 集成

### 步骤 1: 配置 Cloudflare Email Routing

1. 登录 Cloudflare Dashboard
2. 选择你的域名
3. 进入 **Email** → **Email Routing**
4. 添加目标邮箱地址（用于接收转发邮件）
5. 配置路由规则

### 步骤 2: 创建 Cloudflare Worker

创建一个 Worker 将邮件转发到 Webhook 端点：

```javascript
// Cloudflare Worker 代码
addEventListener('email', event => {
  event.waitUntil(handleEmail(event));
});

async function handleEmail(event) {
  const message = event.message;

  // 读取邮件内容
  const rawEmail = await new Response(message.raw).text();

  // 提取邮件头信息
  const from = message.from;
  const to = message.to;
  const subject = message.headers.get('subject');

  // 解析邮件正文（简化版，实际需要 MIME 解析）
  const htmlMatch = rawEmail.match(/Content-Type: text\/html[\s\S]*?\n\n([\s\S]*?)(?=\n--)/);
  const textMatch = rawEmail.match(/Content-Type: text\/plain[\s\S]*?\n\n([\s\S]*?)(?=\n--)/);

  const html = htmlMatch ? htmlMatch[1].trim() : '';
  const text = textMatch ? textMatch[1].trim() : '';

  // 构造 Webhook 请求
  const webhookData = {
    from: from,
    to: to,
    subject: subject,
    html: html,
    text: text,
    message_id: message.headers.get('message-id')
  };

  // 发送到你的 Webhook 端点
  const response = await fetch('https://your-domain.com/webhook/email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Webhook-Secret': 'your-webhook-secret' // 从环境变量读取
    },
    body: JSON.stringify(webhookData)
  });

  // 检查响应
  if (!response.ok) {
    console.error('Webhook failed:', await response.text());
  }
}
```

### 步骤 3: 配置 Worker 环境变量

在 Cloudflare Worker 设置中添加环境变量：

```toml
# wrangler.toml
[vars]
WEBHOOK_URL = "https://your-domain.com/webhook/email"
WEBHOOK_SECRET = "your-webhook-secret"
```

### 步骤 4: 部署 Worker

```bash
# 安装 Wrangler CLI
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 部署 Worker
wrangler deploy
```

### 步骤 5: 绑定 Email Routing

在 Cloudflare Email Routing 设置中：

1. 创建新的路由规则
2. 选择 "Send to Worker"
3. 选择刚才部署的 Worker

## 安全最佳实践

### 1. 强密钥策略

- 使用至少 32 字节的随机字符串作为 `WEBHOOK_SECRET`
- 定期轮换密钥
- 不要在代码中硬编码密钥

### 2. HTTPS 强制

- 生产环境必须使用 HTTPS
- 配置 HSTS 头部
- 使用有效的 SSL/TLS 证书

```python
# Flask 配置示例
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SESSION_COOKIE_SECURE'] = True
```

### 3. IP 白名单（可选）

如果 Webhook 来源固定，可以限制 IP 访问：

```python
ALLOWED_IPS = ['104.16.0.0/12', '172.64.0.0/13']  # Cloudflare IP 范围

@webhook_bp.before_request
def check_ip():
    client_ip = request.headers.get('CF-Connecting-IP') or request.remote_addr
    if not any(ip_in_range(client_ip, cidr) for cidr in ALLOWED_IPS):
        return jsonify({'error': 'Forbidden'}), 403
```

### 4. 请求速率限制

```python
from flask_limiter import Limiter

limiter = Limiter(
    app=app,
    key_func=lambda: request.headers.get('X-Webhook-Secret', 'anonymous')
)

@webhook_bp.route('/webhook/email', methods=['POST'])
@limiter.limit("60 per minute")
def receive_email():
    # ...
```

### 5. 日志记录

记录所有 Webhook 请求用于审计：

```python
import logging

logger = logging.getLogger(__name__)

@webhook_bp.route('/webhook/email', methods=['POST'])
def receive_email():
    logger.info(f"Webhook received from IP: {request.remote_addr}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    # ...
```

## 错误处理

### 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "success": false,
  "error": "错误类型",
  "message": "详细错误信息"
}
```

### 常见错误码

| HTTP 状态码 | 错误类型 | 说明 |
|------------|---------|------|
| `401` | Unauthorized | 无效的 Webhook 密钥 |
| `400` | Bad Request | 请求数据格式错误或处理失败 |
| `500` | Internal Server Error | 服务器内部错误 |

### 错误示例

#### 401 未授权

```json
{
  "error": "Unauthorized",
  "message": "无效的 webhook 密钥"
}
```

#### 400 请求错误

```json
{
  "success": false,
  "message": "missing required field: to"
}
```

### 异常处理流程

```python
try:
    # 处理邮件逻辑
    db.session.add(email)
    db.session.commit()
    return jsonify({'success': True, 'message': '邮件已接收'}), 200

except Exception as e:
    # 回滚数据库事务
    db.session.rollback()

    # 记录错误日志
    logger.error(f"Failed to process webhook: {str(e)}", exc_info=True)

    # 返回错误响应
    return jsonify({
        'success': False,
        'message': str(e)
    }), 400
```

## 测试 Webhook

### 本地测试

使用 `curl` 命令测试：

```bash
curl -X POST http://localhost:5000/webhook/email \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: test-secret" \
  -d '{
    "from": "test@example.com",
    "to": "user@test.com",
    "subject": "Test Email",
    "html": "<a href=\"https://example.com/verify?token=test123\">Verify</a>",
    "text": "Verify: https://example.com/verify?token=test123",
    "message_id": "test-message-id"
  }'
```

### 预期成功响应

```json
{
  "success": true,
  "message": "邮件已接收",
  "verification_link": "https://example.com/verify?token=test123"
}
```

### 使用 Postman 测试

1. 创建新的 POST 请求
2. URL: `http://localhost:5000/webhook/email`
3. Headers:
   - `Content-Type`: `application/json`
   - `X-Webhook-Secret`: `your-webhook-secret`
4. Body (raw JSON):
   ```json
   {
     "from": "sender@example.com",
     "to": "recipient@test.com",
     "subject": "Verification Email",
     "html": "<a href=\"https://example.com/confirm?code=abc\">Confirm</a>",
     "text": "Confirm: https://example.com/confirm?code=abc"
   }
   ```

## 监控与调试

### 日志配置

```python
# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)
```

### 关键监控指标

- Webhook 请求成功率
- 验证链接提取成功率
- 平均响应时间
- 数据库写入失败次数

### 调试技巧

1. **检查请求头**：确认 `X-Webhook-Secret` 是否正确
2. **验证 JSON 格式**：确保请求体是有效的 JSON
3. **检查数据库连接**：确认数据库可访问
4. **测试正则表达式**：验证链接提取逻辑是否正确
5. **查看日志文件**：分析详细错误信息

## 附录

### 环境变量清单

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `WEBHOOK_SECRET` | Webhook 认证密钥 | `a1b2c3d4e5f6...` |
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///emails.db` |
| `FLASK_ENV` | Flask 运行环境 | `production` |

### 相关资源

- [Cloudflare Email Routing 文档](https://developers.cloudflare.com/email-routing/)
- [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [正则表达式在线测试工具](https://regex101.com/)
