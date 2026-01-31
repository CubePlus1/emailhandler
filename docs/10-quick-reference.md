# 快速参考和常见问题

## 目录

- [常见问题解答 (FAQ)](#常见问题解答-faq)
- [快速启动命令清单](#快速启动命令清单)
- [常见错误排查](#常见错误排查)
- [性能优化清单](#性能优化清单)
- [快速开发技巧](#快速开发技巧)
- [有用的数据库查询语句](#有用的数据库查询语句)
- [API 测试命令](#api-测试命令)

---

## 常见问题解答 (FAQ)

### 如何启动应用？

**开发环境:**
```bash
# 1. 激活虚拟环境
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# 2. 安装依赖
uv pip install -r requirements.txt

# 3. 配置环境变量（复制并修改 .env.example）
cp .env.example .env

# 4. 启动应用
python -m backend.main
```

**生产环境:**
```bash
# 使用 systemd（推荐）
sudo systemctl start emailhandler

# 或直接运行
python -m backend.main
```

### 如何配置数据库？

**1. 在 `.env` 文件中配置连接信息:**
```env
# SQLite（默认，适合开发环境）
DATABASE_URL=sqlite:///./emails.db

# PostgreSQL（推荐生产环境）
DATABASE_URL=postgresql://user:password@localhost:5432/emailhandler

# MySQL
DATABASE_URL=mysql://user:password@localhost:3306/emailhandler
```

**2. 运行数据库迁移（自动创建表）:**
```bash
# 应用启动时会自动创建表，无需手动操作
python -m backend.main
```

**3. 查看数据库状态:**
```bash
# SQLite
sqlite3 emails.db ".tables"

# PostgreSQL
psql -U user -d emailhandler -c "\dt"
```

### 如何配置 Webhook？

**1. 在 `.env` 文件中启用 Webhook:**
```env
# 启用 Webhook
ENABLE_WEBHOOK=true
WEBHOOK_URL=https://your-webhook-endpoint.com/notify

# 可选：配置 Webhook 签名密钥（用于验证请求）
WEBHOOK_SECRET=your-secret-key-here
```

**2. Webhook 请求格式:**
```json
{
  "email_id": 123,
  "subject": "邮件主题",
  "sender": "sender@example.com",
  "received_at": "2025-01-30T12:00:00Z",
  "validation_status": "verified",
  "validation_link": "https://example.com/verify/abc123"
}
```

**3. 验证 Webhook 签名（推荐）:**
```python
import hmac
import hashlib

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### 如何添加新的验证链接模式？

**1. 编辑 `backend/utils/url_validator.py`:**
```python
VALIDATION_PATTERNS = [
    # 现有模式
    r'https?://[^\s]+/verify/[a-zA-Z0-9]+',

    # 添加新模式
    r'https?://[^\s]+/confirm\?token=[a-zA-Z0-9]+',  # 新增
    r'https?://[^\s]+/activate/[0-9]+/[a-zA-Z0-9]+', # 新增
]
```

**2. 测试新模式:**
```python
from backend.utils.url_validator import extract_validation_links

test_email = """
请点击以下链接确认:
https://example.com/confirm?token=abc123xyz
https://example.com/activate/123/def456ghi
"""

links = extract_validation_links(test_email)
print(links)  # 应输出匹配的链接
```

**3. 重启应用:**
```bash
# 开发环境（支持热重载）
python -m backend.main

# 生产环境
sudo systemctl restart emailhandler
```

---

## 快速启动命令清单

### 项目初始化
```bash
# 克隆项目
git clone https://github.com/your-username/emailhandler.git
cd emailhandler

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# 安装依赖（优先使用 uv）
uv pip install -r requirements.txt
# 或
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库、IMAP 等
```

### 开发环境
```bash
# 启动应用（自动重载）
python -m backend.main

# 运行测试
pytest tests/

# 代码检查
flake8 backend/
black backend/ --check
mypy backend/
```

### 生产环境
```bash
# 安装为系统服务（Linux）
sudo cp systemd/emailhandler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable emailhandler
sudo systemctl start emailhandler

# 查看服务状态
sudo systemctl status emailhandler

# 查看日志
sudo journalctl -u emailhandler -f
```

---

## 常见错误排查

### 1. 无法连接到 IMAP 服务器

**错误信息:**
```
IMAPError: [AUTHENTICATIONFAILED] Invalid credentials
```

**解决方案:**
```bash
# 1. 检查 .env 配置
cat .env | grep IMAP

# 2. 确认 IMAP 服务已启用（Gmail 示例）
# - 访问 https://myaccount.google.com/security
# - 启用"两步验证"
# - 生成"应用专用密码"并使用该密码

# 3. 测试 IMAP 连接
python -c "
import imaplib
import os
from dotenv import load_dotenv
load_dotenv()

mail = imaplib.IMAP4_SSL(os.getenv('IMAP_SERVER'))
mail.login(os.getenv('IMAP_USER'), os.getenv('IMAP_PASSWORD'))
print('连接成功！')
"
```

### 2. 数据库连接失败

**错误信息:**
```
OperationalError: unable to open database file
```

**解决方案:**
```bash
# 1. 检查数据库文件权限
ls -la emails.db

# 2. 检查目录权限
ls -la .

# 3. 修复权限
chmod 644 emails.db
chmod 755 .

# 4. 如果使用 PostgreSQL，检查连接信息
psql -U user -d emailhandler -c "SELECT 1"
```

### 3. Webhook 调用失败

**错误信息:**
```
WebhookError: Failed to send webhook notification
```

**解决方案:**
```bash
# 1. 检查 Webhook URL 是否可访问
curl -X POST https://your-webhook-endpoint.com/notify \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# 2. 检查 .env 配置
cat .env | grep WEBHOOK

# 3. 查看详细错误日志
tail -f logs/emailhandler.log | grep webhook

# 4. 测试 Webhook 发送
python -c "
import requests
import os
from dotenv import load_dotenv
load_dotenv()

response = requests.post(
    os.getenv('WEBHOOK_URL'),
    json={'test': True},
    timeout=10
)
print(f'状态码: {response.status_code}')
print(f'响应: {response.text}')
"
```

### 4. 邮件解析失败

**错误信息:**
```
EmailParseError: Failed to extract email body
```

**解决方案:**
```bash
# 1. 检查邮件编码
python -c "
import email
from email import policy

# 从文件读取原始邮件
with open('problematic_email.eml', 'rb') as f:
    msg = email.message_from_binary_file(f, policy=policy.default)
    print(f'Content-Type: {msg.get_content_type()}')
    print(f'Charset: {msg.get_content_charset()}')
"

# 2. 手动解析邮件内容
python -c "
from backend.utils.email_parser import parse_email_content

with open('problematic_email.eml', 'rb') as f:
    content = parse_email_content(f.read())
    print(content)
"
```

### 5. 内存占用过高

**现象:** 应用运行一段时间后内存占用持续增长

**解决方案:**
```bash
# 1. 检查进程内存使用
ps aux | grep python

# 2. 启用内存监控
python -m memory_profiler backend/main.py

# 3. 配置 .env 限制批处理大小
BATCH_SIZE=10          # 默认 50，降低批处理大小
MAX_EMAILS=100         # 每次处理的最大邮件数

# 4. 启用定期重启（systemd）
sudo systemctl edit emailhandler
# 添加:
# [Service]
# Restart=always
# RuntimeMaxSec=86400  # 每 24 小时重启一次
```

---

## 性能优化清单

### 数据库优化

```sql
-- 1. 创建索引（提升查询速度）
CREATE INDEX idx_emails_received_at ON emails(received_at DESC);
CREATE INDEX idx_emails_validation_status ON emails(validation_status);
CREATE INDEX idx_emails_sender ON emails(sender);

-- 2. 定期清理旧数据（减少数据库大小）
DELETE FROM emails WHERE received_at < datetime('now', '-90 days');
VACUUM;  -- 回收空间

-- 3. 分析查询性能
EXPLAIN QUERY PLAN
SELECT * FROM emails
WHERE validation_status = 'verified'
ORDER BY received_at DESC
LIMIT 100;
```

### 应用优化

**1. 批量处理邮件**
```python
# .env 配置
BATCH_SIZE=50          # 每次处理 50 封邮件
FETCH_INTERVAL=300     # 每 5 分钟检查一次新邮件
```

**2. 启用连接池（PostgreSQL）**
```python
# .env 配置
DATABASE_URL=postgresql://user:password@localhost:5432/emailhandler?pool_size=10&max_overflow=20
```

**3. 异步处理 Webhook**
```python
# .env 配置
WEBHOOK_ASYNC=true     # 异步发送 Webhook，不阻塞主流程
WEBHOOK_TIMEOUT=5      # Webhook 超时时间（秒）
```

### 系统优化

**1. 限制日志文件大小**
```bash
# 编辑 backend/utils/logger.py
logging.handlers.RotatingFileHandler(
    'logs/emailhandler.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5           # 保留 5 个备份
)
```

**2. 使用 Redis 缓存（可选）**
```python
# .env 配置
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300  # 缓存过期时间（秒）
```

---

## 快速开发技巧

### 1. 热重载开发

```bash
# 使用 watchdog 实现文件变更自动重启
pip install watchdog
watchmedo auto-restart --recursive --pattern="*.py" -- python -m backend.main
```

### 2. 快速测试单个功能

```python
# 测试邮件解析
python -c "
from backend.utils.email_parser import parse_email_content
from backend.utils.url_validator import extract_validation_links

sample_email = '''
Subject: 请验证您的邮箱
From: noreply@example.com

点击链接验证: https://example.com/verify/abc123
'''

body = parse_email_content(sample_email.encode())
links = extract_validation_links(body)
print(f'提取到的链接: {links}')
"
```

### 3. 数据库快速重置

```bash
# 删除数据库并重新创建
rm emails.db
python -m backend.main  # 自动创建新数据库
```

### 4. 生成测试数据

```python
python -c "
from backend.database import SessionLocal, Email
from datetime import datetime

db = SessionLocal()

# 插入测试数据
for i in range(10):
    email = Email(
        subject=f'测试邮件 {i}',
        sender=f'test{i}@example.com',
        body=f'这是测试邮件内容 {i}',
        received_at=datetime.now(),
        validation_status='pending',
        validation_link=f'https://example.com/verify/{i}'
    )
    db.add(email)

db.commit()
print('已插入 10 条测试数据')
"
```

### 5. 快速调试 Webhook

```python
# 启动本地 Webhook 测试服务器
python -c "
from flask import Flask, request
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    print('收到 Webhook 请求:')
    print(request.json)
    return 'OK', 200

app.run(port=8000)
"

# 然后在 .env 中配置:
# WEBHOOK_URL=http://localhost:8000/webhook
```

---

## 有用的数据库查询语句

### 统计查询

```sql
-- 统计各验证状态的邮件数量
SELECT validation_status, COUNT(*) as count
FROM emails
GROUP BY validation_status;

-- 统计每日接收邮件数
SELECT DATE(received_at) as date, COUNT(*) as count
FROM emails
GROUP BY DATE(received_at)
ORDER BY date DESC
LIMIT 30;

-- 统计发件人排行榜
SELECT sender, COUNT(*) as count
FROM emails
GROUP BY sender
ORDER BY count DESC
LIMIT 10;

-- 统计验证链接域名分布
SELECT
  SUBSTR(validation_link, 1, INSTR(SUBSTR(validation_link, 9), '/') + 8) as domain,
  COUNT(*) as count
FROM emails
WHERE validation_link IS NOT NULL
GROUP BY domain
ORDER BY count DESC;
```

### 数据清理

```sql
-- 删除 90 天前的已验证邮件
DELETE FROM emails
WHERE validation_status = 'verified'
  AND received_at < datetime('now', '-90 days');

-- 删除重复邮件（保留最新的）
DELETE FROM emails
WHERE id NOT IN (
  SELECT MAX(id)
  FROM emails
  GROUP BY subject, sender, received_at
);

-- 重置验证失败的邮件状态
UPDATE emails
SET validation_status = 'pending',
    validation_link = NULL
WHERE validation_status = 'failed';
```

### 数据导出

```sql
-- 导出为 CSV
.mode csv
.headers on
.output emails_export.csv
SELECT * FROM emails WHERE received_at > datetime('now', '-7 days');
.output stdout

-- 导出验证链接列表
SELECT validation_link
FROM emails
WHERE validation_status = 'verified'
  AND validation_link IS NOT NULL
ORDER BY received_at DESC;
```

---

## API 测试命令

### 使用 curl

```bash
# 1. 获取邮件列表
curl -X GET "http://localhost:8000/api/emails?limit=10&offset=0"

# 2. 获取单个邮件详情
curl -X GET "http://localhost:8000/api/emails/123"

# 3. 更新邮件验证状态
curl -X PATCH "http://localhost:8000/api/emails/123" \
  -H "Content-Type: application/json" \
  -d '{"validation_status": "verified"}'

# 4. 手动触发邮件检查
curl -X POST "http://localhost:8000/api/emails/fetch"

# 5. 获取统计信息
curl -X GET "http://localhost:8000/api/stats"

# 6. 健康检查
curl -X GET "http://localhost:8000/health"
```

### 使用 HTTPie（更友好）

```bash
# 安装 HTTPie
pip install httpie

# 1. 获取邮件列表（自动美化输出）
http GET http://localhost:8000/api/emails limit==10 offset==0

# 2. 更新验证状态
http PATCH http://localhost:8000/api/emails/123 \
  validation_status=verified

# 3. 手动触发邮件检查
http POST http://localhost:8000/api/emails/fetch

# 4. 获取统计信息
http GET http://localhost:8000/api/stats
```

### 使用 Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 获取邮件列表
response = requests.get(f"{BASE_URL}/api/emails", params={
    "limit": 10,
    "offset": 0
})
print(response.json())

# 2. 获取单个邮件
email_id = 123
response = requests.get(f"{BASE_URL}/api/emails/{email_id}")
print(response.json())

# 3. 更新验证状态
response = requests.patch(
    f"{BASE_URL}/api/emails/{email_id}",
    json={"validation_status": "verified"}
)
print(response.json())

# 4. 手动触发邮件检查
response = requests.post(f"{BASE_URL}/api/emails/fetch")
print(response.json())
```

---

## 快速备忘单

### 环境变量配置速查

```env
# 数据库
DATABASE_URL=sqlite:///./emails.db

# IMAP 配置
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USER=your-email@gmail.com
IMAP_PASSWORD=your-app-password
IMAP_FOLDER=INBOX

# Webhook 配置
ENABLE_WEBHOOK=true
WEBHOOK_URL=https://your-webhook-endpoint.com/notify
WEBHOOK_SECRET=your-secret-key
WEBHOOK_TIMEOUT=10

# 应用配置
BATCH_SIZE=50
FETCH_INTERVAL=300
LOG_LEVEL=INFO
```

### 常用文件路径

```
emails.db              # SQLite 数据库文件
logs/emailhandler.log  # 应用日志
.env                   # 环境变量配置
backend/               # 后端代码目录
tests/                 # 测试代码目录
docs/                  # 文档目录
```

### 常用端口

```
8000  # FastAPI 默认端口
993   # IMAP SSL 端口
587   # SMTP TLS 端口
5432  # PostgreSQL 默认端口
3306  # MySQL 默认端口
6379  # Redis 默认端口
```

---

## 获取帮助

- **文档:** 查看 `docs/` 目录下的完整文档
- **日志:** 检查 `logs/emailhandler.log` 获取错误详情
- **GitHub Issues:** https://github.com/your-username/emailhandler/issues
- **社区支持:** [添加您的社区链接]

---

**最后更新:** 2025-01-30
