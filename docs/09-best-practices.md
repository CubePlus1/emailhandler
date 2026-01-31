# 代码风格与最佳实践

## 目录

- [命名规范](#命名规范)
- [错误处理模式](#错误处理模式)
- [数据库事务管理](#数据库事务管理)
- [安全实践](#安全实践)
- [日志记录建议](#日志记录建议)
- [API 设计原则](#api-设计原则)
- [测试策略](#测试策略)
- [性能优化建议](#性能优化建议)
- [代码审查清单](#代码审查清单)

---

## 命名规范

### 变量命名

**✅ 推荐：使用描述性的蛇形命名法 (snake_case)**

```python
# 正例
email_address = "user@example.com"
verification_link = "https://example.com/verify/abc123"
is_verified = True
max_retry_count = 3
```

**❌ 反例：缩写、驼峰、含糊不清**

```python
# 反例
e = "user@example.com"           # 过于简短
emailAddress = "user@example.com" # 应使用蛇形命名
flag = True                       # 含义不明确
n = 3                             # 无意义的单字符
```

### 函数命名

**✅ 推荐：动词开头，清晰表达功能**

```python
# 正例
def extract_verification_link(html_content: str) -> Optional[str]:
    """从 HTML 中提取验证链接"""
    pass

def get_mailboxes() -> list[Mailbox]:
    """获取所有邮箱"""
    pass

def update_email_status(email_id: int, is_read: bool) -> bool:
    """更新邮件状态"""
    pass

def validate_email_format(email: str) -> bool:
    """验证邮箱格式"""
    pass
```

**❌ 反例：含糊不清、名词形式**

```python
# 反例
def process(data):              # 处理什么？
    pass

def email():                    # 名词形式，不知道做什么
    pass

def do_stuff(x, y):             # 太笼统
    pass
```

### 类命名

**✅ 推荐：大驼峰命名法 (PascalCase)，名词**

```python
# 正例
class Mailbox(Base):
    """邮箱账户模型"""
    pass

class EmailParser:
    """邮件解析器"""
    pass

class ValidationLinkExtractor:
    """验证链接提取器"""
    pass
```

**❌ 反例：蛇形命名、动词形式**

```python
# 反例
class email_handler:            # 应使用大驼峰
    pass

class ParseEmail:               # 应为名词形式
    pass

class UtilsHelper:              # 太笼统
    pass
```

### 模块命名

**✅ 推荐：简短的蛇形命名法**

```python
# 正例
# backend/api/routes.py
# backend/database/models.py
# backend/utils/email_parser.py
# backend/services/webhook.py
```

**❌ 反例：冗长、驼峰**

```python
# 反例
# backend/apiRoutesForEmailHandling.py
# backend/DatabaseModelsDefinitions.py
# backend/Utilities.py
```

### 常量命名

**✅ 推荐：全大写蛇形命名**

```python
# 正例
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30
WEBHOOK_SECRET_HEADER = "X-Webhook-Signature"
ALLOWED_FOLDER_NAMES = ["inbox", "sent", "trash", "archive"]
```

**❌ 反例：小写或驼峰**

```python
# 反例
max_retry = 3                   # 应全大写
MaxRetry = 3                    # 应全大写蛇形
timeout = 30                    # 无法区分是变量还是常量
```

---

## 错误处理模式

### Try-Except-Rollback 模式

**✅ 推荐：完整的错误处理和回滚**

```python
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

@api_bp.route('/emails/<int:id>', methods=['PATCH'])
def update_email(id):
    """更新邮件"""
    from flask import current_app
    db = current_app.extensions['sqlalchemy']

    try:
        email = db.session.query(Email).filter_by(id=id).first()
        if not email:
            return jsonify({
                'success': False,
                'message': '邮件不存在'
            }), 404

        data = request.get_json() or {}

        # 验证输入
        if 'folder' in data and data['folder'] not in ALLOWED_FOLDER_NAMES:
            return jsonify({
                'success': False,
                'message': f'无效的文件夹名称，允许的值: {ALLOWED_FOLDER_NAMES}'
            }), 400

        # 执行更新
        if 'is_read' in data:
            email.is_read = bool(data['is_read'])
        if 'is_starred' in data:
            email.is_starred = bool(data['is_starred'])
        if 'folder' in data:
            email.folder = data['folder']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '邮件已更新',
            'email': {
                'id': email.id,
                'is_read': email.is_read,
                'is_starred': email.is_starred,
                'folder': email.folder
            }
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        # 记录详细错误到日志
        current_app.logger.error(f"数据库错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': '数据库操作失败'
        }), 500

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"未预期错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500
```

**❌ 反例：不完整的错误处理**

```python
# 反例 1: 笼统的异常捕获，不回滚
@api_bp.route('/emails/<int:id>', methods=['PATCH'])
def update_email(id):
    try:
        email = db.session.query(Email).filter_by(id=id).first()
        email.is_read = True
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        # ❌ 没有回滚！数据库可能处于不一致状态
        return jsonify({'message': str(e)}), 500

# 反例 2: 暴露内部错误信息
@api_bp.route('/emails/<int:id>', methods=['PATCH'])
def update_email(id):
    try:
        email = db.session.query(Email).filter_by(id=id).first()
        email.is_read = True
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        # ❌ 直接暴露内部错误信息给用户
        return jsonify({'message': str(e)}), 500

# 反例 3: 不检查资源是否存在
@api_bp.route('/emails/<int:id>', methods=['PATCH'])
def update_email(id):
    email = db.session.query(Email).filter_by(id=id).first()
    # ❌ 如果 email 为 None，下面会抛出 AttributeError
    email.is_read = True
    db.session.commit()
```

### 自定义异常类

**✅ 推荐：定义特定业务异常**

```python
# backend/exceptions.py

class EmailHandlerError(Exception):
    """邮件处理器基础异常"""
    pass

class EmailNotFoundError(EmailHandlerError):
    """邮件不存在"""
    pass

class WebhookError(EmailHandlerError):
    """Webhook 调用失败"""
    pass

class ValidationError(EmailHandlerError):
    """验证错误"""
    pass

# 使用示例
from backend.exceptions import EmailNotFoundError

def get_email_by_id(email_id: int) -> Email:
    email = db.session.query(Email).filter_by(id=email_id).first()
    if not email:
        raise EmailNotFoundError(f"邮件 ID {email_id} 不存在")
    return email

# API 层统一处理
@api_bp.errorhandler(EmailNotFoundError)
def handle_not_found(error):
    return jsonify({
        'success': False,
        'message': str(error)
    }), 404

@api_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({
        'success': False,
        'message': str(error)
    }), 400
```

---

## 数据库事务管理

### 使用上下文管理器

**✅ 推荐：使用 with 语句自动管理会话**

```python
from contextlib import contextmanager
from backend.database import SessionLocal

@contextmanager
def get_db_session():
    """获取数据库会话的上下文管理器"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# 使用示例
def create_email(email_data: dict) -> Email:
    with get_db_session() as db:
        email = Email(**email_data)
        db.add(email)
        # 自动提交或回滚
    return email
```

### 批量操作优化

**✅ 推荐：使用批量插入和事务**

```python
def save_emails_batch(emails_data: list[dict]) -> int:
    """批量保存邮件"""
    with get_db_session() as db:
        # 使用 bulk_insert_mappings 提升性能
        db.bulk_insert_mappings(Email, emails_data)
        return len(emails_data)

# 或使用 add_all
def save_emails_batch_v2(emails: list[Email]) -> int:
    with get_db_session() as db:
        db.add_all(emails)
        return len(emails)
```

**❌ 反例：逐个插入，多次提交**

```python
# 反例：低效的逐个插入
def save_emails_one_by_one(emails_data: list[dict]):
    for email_data in emails_data:
        # ❌ 每次循环都创建新会话和提交，非常低效
        db = SessionLocal()
        email = Email(**email_data)
        db.add(email)
        db.commit()
        db.close()
```

### 嵌套事务处理

**✅ 推荐：使用 SAVEPOINT**

```python
from sqlalchemy.exc import IntegrityError

def process_email_with_attachments(email_data: dict, attachments_data: list[dict]):
    with get_db_session() as db:
        # 主事务：创建邮件
        email = Email(**email_data)
        db.add(email)
        db.flush()  # 获取 email.id 但不提交

        # 子事务：保存附件
        for attachment_data in attachments_data:
            try:
                # 使用 SAVEPOINT
                with db.begin_nested():
                    attachment = Attachment(
                        email_id=email.id,
                        **attachment_data
                    )
                    db.add(attachment)
            except IntegrityError:
                # 单个附件失败不影响整体
                logger.warning(f"附件保存失败: {attachment_data['filename']}")
                continue

        # 所有操作完成后一次性提交
```

---

## 安全实践

### 防止 SQL 注入

**✅ 推荐：始终使用参数化查询**

```python
# 正例：使用 SQLAlchemy ORM（自动参数化）
def search_emails(query: str) -> list[Email]:
    return db.session.query(Email).filter(
        Email.subject.like(f"%{query}%")
    ).all()

# 正例：使用参数绑定
def search_emails_raw(query: str) -> list[Email]:
    sql = """
        SELECT * FROM emails
        WHERE subject LIKE :query
        ORDER BY received_at DESC
    """
    return db.session.execute(sql, {"query": f"%{query}%"}).fetchall()
```

**❌ 反例：字符串拼接（容易 SQL 注入）**

```python
# 反例：危险的字符串拼接
def search_emails_unsafe(query: str):
    # ❌ 用户输入直接拼接到 SQL，存在注入风险
    # 例如：query = "'; DROP TABLE emails; --"
    sql = f"SELECT * FROM emails WHERE subject LIKE '%{query}%'"
    return db.session.execute(sql).fetchall()
```

### 防止 XSS 攻击

**✅ 推荐：转义 HTML 输出**

```python
from markupsafe import escape
from flask import render_template_string

@api_bp.route('/emails/<int:id>/preview', methods=['GET'])
def preview_email(id):
    """预览邮件（HTML 格式）"""
    email = get_email_by_id(id)

    # 方案 1: 使用 Jinja2 自动转义
    return render_template_string("""
        <h1>{{ subject }}</h1>
        <p>发件人: {{ from_address }}</p>
        <div>{{ body | safe }}</div>  <!-- 仅对可信内容使用 safe -->
    """, subject=email.subject, from_address=email.from_address, body=escape(email.html_body))

# 方案 2: 使用 bleach 清理 HTML
import bleach

def sanitize_html(html_content: str) -> str:
    """清理 HTML 内容，只保留安全标签"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'a', 'ul', 'ol', 'li']
    allowed_attrs = {'a': ['href', 'title']}
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
```

**❌ 反例：直接输出未转义的 HTML**

```python
# 反例：不转义用户输入的 HTML
@api_bp.route('/emails/<int:id>/preview')
def preview_email_unsafe(id):
    email = get_email_by_id(id)
    # ❌ 如果 email.html_body 包含恶意脚本，会被执行
    return f"<html><body>{email.html_body}</body></html>"
```

### 防止 CSRF 攻击

**✅ 推荐：使用 CSRF Token**

```python
from flask_wtf.csrf import CSRFProtect

# 初始化 CSRF 保护
csrf = CSRFProtect(app)

# 配置
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('CSRF_SECRET_KEY')

# 模板中使用
# <form method="POST">
#   {{ csrf_token() }}
#   <input type="text" name="email">
# </form>

# API 端点可以豁免 CSRF（如果使用 Token 认证）
@api_bp.route('/api/emails', methods=['POST'])
@csrf.exempt  # 仅用于 API，需配合其他认证机制
def create_email_api():
    pass
```

### 敏感信息保护

**✅ 推荐：不记录敏感信息**

```python
import logging

logger = logging.getLogger(__name__)

def send_webhook(email_data: dict, webhook_url: str, secret: str):
    """发送 Webhook 通知"""
    # 正例：记录日志时移除敏感信息
    safe_data = {
        'email_id': email_data.get('id'),
        'subject': email_data.get('subject'),
        'webhook_url': webhook_url
        # ❌ 不记录: secret, email 内容, 个人信息
    }
    logger.info(f"发送 Webhook: {safe_data}")

    try:
        response = requests.post(
            webhook_url,
            json=email_data,
            headers={'X-Webhook-Signature': generate_signature(email_data, secret)},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        # 正例：不在日志中暴露完整错误信息
        logger.error(f"Webhook 发送失败: {type(e).__name__}")
        return False
```

**❌ 反例：记录敏感信息**

```python
# 反例：在日志中记录密码和密钥
def authenticate_user(username: str, password: str):
    # ❌ 绝对不要记录密码
    logger.info(f"用户登录: {username}, 密码: {password}")

    # ❌ 不要记录完整的密钥
    logger.debug(f"使用密钥: {SECRET_KEY}")
```

---

## 日志记录建议

### 日志级别使用

**✅ 推荐：正确使用日志级别**

```python
import logging

logger = logging.getLogger(__name__)

def process_email(email_id: int):
    """处理邮件"""
    # DEBUG: 详细的调试信息（仅开发环境）
    logger.debug(f"开始处理邮件 ID: {email_id}")

    try:
        email = get_email_by_id(email_id)

        # INFO: 关键业务操作
        logger.info(f"处理邮件: {email.subject} (ID: {email_id})")

        # 提取验证链接
        link = extract_verification_link(email.html_body)
        if link:
            # INFO: 成功提取
            logger.info(f"提取到验证链接: {link[:50]}...")
        else:
            # WARNING: 预期的情况但需要注意
            logger.warning(f"邮件 {email_id} 未找到验证链接")

        # 发送 Webhook
        if not send_webhook(email_data):
            # ERROR: 失败但可恢复
            logger.error(f"Webhook 发送失败，邮件 ID: {email_id}")

    except EmailNotFoundError:
        # WARNING: 预期的错误
        logger.warning(f"邮件不存在: {email_id}")
    except Exception as e:
        # CRITICAL: 严重错误，需要立即处理
        logger.critical(f"处理邮件时发生严重错误: {email_id}", exc_info=True)
        raise
```

### 结构化日志

**✅ 推荐：使用 JSON 格式记录日志**

```python
import json
import logging

class JSONFormatter(logging.Formatter):
    """JSON 格式日志"""
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # 添加异常信息
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # 添加自定义字段
        if hasattr(record, 'email_id'):
            log_data['email_id'] = record.email_id

        return json.dumps(log_data, ensure_ascii=False)

# 配置日志
handler = logging.FileHandler('logs/emailhandler.json')
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# 使用示例
def process_email(email_id: int):
    logger.info("处理邮件", extra={'email_id': email_id})
```

---

## API 设计原则

### RESTful 规范

**✅ 推荐：遵循 RESTful 最佳实践**

```python
# 正例：清晰的 RESTful 端点
@api_bp.route('/api/v1/mailboxes', methods=['GET'])
def list_mailboxes():
    """列出所有邮箱"""
    pass

@api_bp.route('/api/v1/mailboxes/<int:id>', methods=['GET'])
def get_mailbox(id):
    """获取单个邮箱"""
    pass

@api_bp.route('/api/v1/emails', methods=['GET'])
def list_emails():
    """列出邮件（支持分页和过滤）"""
    # ?limit=20&offset=0&folder=inbox&is_read=false
    pass

@api_bp.route('/api/v1/emails/<int:id>', methods=['GET'])
def get_email(id):
    """获取单个邮件"""
    pass

@api_bp.route('/api/v1/emails/<int:id>', methods=['PATCH'])
def update_email(id):
    """部分更新邮件"""
    pass

@api_bp.route('/api/v1/emails/<int:id>', methods=['DELETE'])
def delete_email(id):
    """删除邮件"""
    pass

@api_bp.route('/api/v1/search', methods=['GET'])
def search():
    """全文搜索"""
    # ?q=keyword&type=email&limit=20
    pass
```

**❌ 反例：不符合 RESTful 规范**

```python
# 反例
@api_bp.route('/api/getEmails')  # ❌ 动词在 URL 中
def get_emails():
    pass

@api_bp.route('/api/email/delete/<int:id>')  # ❌ 应使用 DELETE 方法
def delete_email(id):
    pass

@api_bp.route('/api/update', methods=['POST'])  # ❌ 应使用 PATCH/PUT
def update():
    pass
```

### 统一响应格式

**✅ 推荐：统一的 JSON 响应格式**

```python
from typing import Any, Optional
from flask import jsonify

def api_response(
    success: bool,
    data: Optional[Any] = None,
    message: Optional[str] = None,
    errors: Optional[list] = None,
    meta: Optional[dict] = None
) -> tuple:
    """统一 API 响应格式"""
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }

    if data is not None:
        response['data'] = data

    if message:
        response['message'] = message

    if errors:
        response['errors'] = errors

    if meta:
        response['meta'] = meta

    status_code = 200 if success else 400
    return jsonify(response), status_code

# 使用示例
@api_bp.route('/api/v1/emails', methods=['GET'])
def list_emails():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    emails = get_emails_paginated(page, limit)
    total = get_emails_count()

    return api_response(
        success=True,
        data=[email.to_dict() for email in emails],
        meta={
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    )
```

### 输入验证

**✅ 推荐：使用 Pydantic 验证输入**

```python
from pydantic import BaseModel, EmailStr, Field, validator

class EmailUpdateRequest(BaseModel):
    """邮件更新请求"""
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None
    folder: Optional[str] = None

    @validator('folder')
    def validate_folder(cls, v):
        allowed = ['inbox', 'sent', 'trash', 'archive']
        if v and v not in allowed:
            raise ValueError(f'文件夹必须是 {allowed} 之一')
        return v

@api_bp.route('/api/v1/emails/<int:id>', methods=['PATCH'])
def update_email(id):
    try:
        # 验证输入
        request_data = EmailUpdateRequest(**request.get_json())

        # 执行更新
        email = get_email_by_id(id)
        if request_data.is_read is not None:
            email.is_read = request_data.is_read
        if request_data.is_starred is not None:
            email.is_starred = request_data.is_starred
        if request_data.folder is not None:
            email.folder = request_data.folder

        db.session.commit()

        return api_response(success=True, data=email.to_dict())

    except ValidationError as e:
        return api_response(success=False, errors=e.errors()), 400
```

---

## 测试策略

### 单元测试

**✅ 推荐：测试纯函数和业务逻辑**

```python
import pytest
from backend.api.utils import extract_verification_link

class TestVerificationLinkExtractor:
    """验证链接提取器测试"""

    def test_extract_simple_link(self):
        """测试提取简单链接"""
        html = '<a href="https://example.com/verify/abc123">验证</a>'
        result = extract_verification_link(html)
        assert result == "https://example.com/verify/abc123"

    def test_extract_confirmation_link(self):
        """测试提取确认链接"""
        html = '<a href="https://example.com/confirmation/xyz789">确认</a>'
        result = extract_verification_link(html)
        assert result == "https://example.com/confirmation/xyz789"

    def test_no_link_found(self):
        """测试未找到链接"""
        html = '<p>这是普通文本</p>'
        result = extract_verification_link(html)
        assert result is None

    def test_multiple_links_returns_first(self):
        """测试多个链接时返回第一个"""
        html = '''
        <a href="https://example.com/verify/first">第一个</a>
        <a href="https://example.com/verify/second">第二个</a>
        '''
        result = extract_verification_link(html)
        assert result == "https://example.com/verify/first"
```

### 集成测试

**✅ 推荐：测试 API 端点**

```python
import pytest
from flask import Flask
from backend.main import create_app

@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_email(db_session):
    """创建测试邮件"""
    email = Email(
        mailbox_id=1,
        message_id="test@example.com",
        from_address="sender@example.com",
        to_address="receiver@example.com",
        subject="测试邮件",
        html_body="<p>测试内容</p>"
    )
    db_session.add(email)
    db_session.commit()
    return email

class TestEmailAPI:
    """邮件 API 测试"""

    def test_get_email_success(self, client, sample_email):
        """测试获取邮件成功"""
        response = client.get(f'/api/v1/emails/{sample_email.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['subject'] == "测试邮件"

    def test_get_email_not_found(self, client):
        """测试获取不存在的邮件"""
        response = client.get('/api/v1/emails/999999')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False

    def test_update_email_success(self, client, sample_email):
        """测试更新邮件成功"""
        response = client.patch(
            f'/api/v1/emails/{sample_email.id}',
            json={'is_read': True, 'folder': 'archive'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['is_read'] is True
        assert data['data']['folder'] == 'archive'

    def test_update_email_invalid_folder(self, client, sample_email):
        """测试更新邮件时使用无效文件夹"""
        response = client.patch(
            f'/api/v1/emails/{sample_email.id}',
            json={'folder': 'invalid_folder'}
        )
        assert response.status_code == 400
```

### Mocking 外部依赖

**✅ 推荐：模拟外部服务**

```python
import pytest
from unittest.mock import patch, MagicMock
from backend.services.webhook import send_webhook

class TestWebhookService:
    """Webhook 服务测试"""

    @patch('requests.post')
    def test_send_webhook_success(self, mock_post):
        """测试成功发送 Webhook"""
        # 配置 mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # 执行测试
        result = send_webhook(
            url="https://example.com/webhook",
            data={'email_id': 123},
            secret="test_secret"
        )

        # 验证
        assert result is True
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args.kwargs['url'] == "https://example.com/webhook"
        assert 'X-Webhook-Signature' in call_args.kwargs['headers']

    @patch('requests.post')
    def test_send_webhook_timeout(self, mock_post):
        """测试 Webhook 超时"""
        mock_post.side_effect = requests.Timeout()

        result = send_webhook(
            url="https://example.com/webhook",
            data={'email_id': 123},
            secret="test_secret"
        )

        assert result is False
```

---

## 性能优化建议

### 数据库查询优化

**✅ 推荐：使用索引和预加载关联**

```python
from sqlalchemy.orm import joinedload

# 正例 1: 预加载关联数据（避免 N+1 问题）
def get_emails_with_attachments():
    """获取邮件及其附件"""
    return db.session.query(Email).options(
        joinedload(Email.attachments)
    ).all()

# 正例 2: 只查询需要的字段
def get_email_summaries():
    """获取邮件摘要（不查询大字段）"""
    return db.session.query(
        Email.id,
        Email.subject,
        Email.from_address,
        Email.received_at
    ).all()

# 正例 3: 使用索引字段过滤
def get_recent_unread_emails():
    """获取最近未读邮件"""
    # 确保 is_read 和 received_at 有索引
    return db.session.query(Email).filter(
        Email.is_read == False,
        Email.received_at >= datetime.now() - timedelta(days=7)
    ).order_by(Email.received_at.desc()).limit(100).all()
```

**❌ 反例：N+1 查询问题**

```python
# 反例：N+1 查询
def get_emails_with_attachments_slow():
    emails = db.session.query(Email).all()
    result = []
    for email in emails:
        # ❌ 每个 email 都会触发一次新查询
        attachments = db.session.query(Attachment).filter_by(
            email_id=email.id
        ).all()
        result.append({
            'email': email,
            'attachments': attachments
        })
    return result
```

### 缓存策略

**✅ 推荐：缓存频繁访问的数据**

```python
from functools import lru_cache
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

# 方案 1: 使用 lru_cache（进程内缓存）
@lru_cache(maxsize=128)
def get_allowed_folders() -> list[str]:
    """获取允许的文件夹列表（很少变化）"""
    return ["inbox", "sent", "trash", "archive"]

# 方案 2: 使用 Redis 缓存
@cache.memoize(timeout=300)  # 缓存 5 分钟
def get_email_statistics():
    """获取邮件统计信息"""
    return {
        'total': db.session.query(Email).count(),
        'unread': db.session.query(Email).filter_by(is_read=False).count(),
        'today': db.session.query(Email).filter(
            Email.received_at >= datetime.now().date()
        ).count()
    }

# 缓存失效
def update_email_invalidate_cache(email_id: int, **kwargs):
    """更新邮件并清除缓存"""
    email = get_email_by_id(email_id)
    for key, value in kwargs.items():
        setattr(email, key, value)
    db.session.commit()

    # 清除统计缓存
    cache.delete_memoized(get_email_statistics)
```

### 异步处理

**✅ 推荐：异步处理耗时任务**

```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

# 方案 1: 使用线程池
executor = ThreadPoolExecutor(max_workers=5)

def send_webhook_async(email_data: dict):
    """异步发送 Webhook"""
    future = executor.submit(send_webhook, email_data)
    # 不等待结果，后台执行
    return future

# 方案 2: 使用 asyncio（适合 I/O 密集型）
import aiohttp

async def fetch_multiple_urls(urls: list[str]) -> list[dict]:
    """并发获取多个 URL"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()
```

---

## 代码审查清单

### 提交前自检

- [ ] **代码风格**: 符合 PEP 8 规范（使用 `black` 和 `flake8` 检查）
- [ ] **类型注解**: 关键函数有类型提示
- [ ] **文档字符串**: 公开函数有 docstring
- [ ] **错误处理**: 所有数据库操作有 try-except-rollback
- [ ] **输入验证**: API 端点验证用户输入
- [ ] **SQL 注入**: 无字符串拼接 SQL
- [ ] **XSS 防护**: HTML 输出已转义
- [ ] **敏感信息**: 日志不包含密码、密钥
- [ ] **测试覆盖**: 新功能有单元测试
- [ ] **性能**: 无明显的 N+1 查询
- [ ] **资源清理**: 文件、连接正确关闭

### 审查他人代码时关注

```python
# 1. 安全性
# - 是否有 SQL 注入风险？
# - 用户输入是否验证？
# - 敏感信息是否加密？

# 2. 正确性
# - 逻辑是否正确？
# - 边界条件是否处理？
# - 错误处理是否完整？

# 3. 可维护性
# - 代码是否易读？
# - 命名是否清晰？
# - 是否有重复代码？

# 4. 性能
# - 是否有性能瓶颈？
# - 数据库查询是否优化？
# - 是否需要缓存？

# 5. 测试
# - 是否有测试覆盖？
# - 测试是否充分？
# - 边界情况是否测试？
```

---

**最后更新:** 2025-01-30
