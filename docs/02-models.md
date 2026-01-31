# 数据库模型详解

本文档详细说明 EmailHandler 项目的数据库模型设计，包括三个核心模型：`Mailbox`（邮箱）、`Email`（邮件）和 `Attachment`（附件）。

## 目录

- [模型概览](#模型概览)
- [Mailbox 模型](#mailbox-模型)
- [Email 模型](#email-模型)
- [Attachment 模型](#attachment-模型)
- [关系映射详解](#关系映射详解)
- [索引设计](#索引设计)
- [SQLAlchemy 2.0 新语法](#sqlalchemy-20-新语法)
- [使用示例](#使用示例)

---

## 模型概览

### 数据模型关系图

```
┌─────────────┐
│   Mailbox   │
│ (邮箱账户)   │
└──────┬──────┘
       │ 1:N
       │
┌──────▼──────┐
│    Email    │
│  (邮件消息)  │
└──────┬──────┘
       │ 1:N
       │
┌──────▼──────┐
│ Attachment  │
│   (附件)    │
└─────────────┘
```

### 核心特性

- **级联删除**: 删除 Mailbox 自动删除所有关联的 Email，删除 Email 自动删除所有关联的 Attachment
- **索引优化**: 针对查询热点字段建立索引
- **SQLAlchemy 2.0**: 使用最新的类型注解语法 (`Mapped`, `mapped_column`)

---

## Mailbox 模型

邮箱账户模型，用于存储临时邮箱地址信息。

### 字段说明

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| `id` | `int` | 主键 ID | PRIMARY KEY, AUTO_INCREMENT |
| `email` | `str` | 邮箱地址 | UNIQUE, NOT NULL, 最大 255 字符 |
| `display_name` | `Optional[str]` | 显示名称 | NULLABLE, 最大 255 字符 |
| `created_at` | `datetime` | 创建时间 | NOT NULL, 默认当前 UTC 时间 |

### 关系

- `emails`: 一对多关系，关联到 `Email` 模型

### 数据库表定义

```python
class Mailbox(Base):
    """Mailbox account model."""

    __tablename__ = "mailboxes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    emails: Mapped[List["Email"]] = relationship(
        "Email", back_populates="mailbox", cascade="all, delete-orphan"
    )
```

### 使用场景

- **创建临时邮箱**: 当用户请求新的临时邮箱时创建记录
- **邮箱查询**: 通过 `email` 字段快速查找邮箱（UNIQUE 索引）
- **级联删除**: 删除邮箱时自动清理所有相关邮件和附件

---

## Email 模型

邮件消息模型，存储完整的邮件内容和元数据。

### 字段说明

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| `id` | `int` | 主键 ID | PRIMARY KEY, AUTO_INCREMENT |
| `mailbox_id` | `int` | 所属邮箱 ID | FOREIGN KEY → mailboxes.id, NOT NULL |
| `message_id` | `str` | 邮件唯一标识符 | UNIQUE, NOT NULL, 最大 255 字符 |
| `from_address` | `str` | 发件人地址 | NOT NULL, 最大 255 字符 |
| `to_address` | `str` | 收件人地址 | NOT NULL, 最大 255 字符 |
| `subject` | `Optional[str]` | 邮件主题 | NULLABLE, 最大 500 字符 |
| `html_body` | `Optional[str]` | HTML 格式正文 | NULLABLE, TEXT 类型 |
| `text_body` | `Optional[str]` | 纯文本格式正文 | NULLABLE, TEXT 类型 |
| `is_read` | `bool` | 是否已读 | NOT NULL, 默认 False |
| `is_starred` | `bool` | 是否标星 | NOT NULL, 默认 False |
| `folder` | `str` | 文件夹名称 | NOT NULL, 默认 "inbox", 最大 50 字符 |
| `received_at` | `datetime` | 接收时间 | NOT NULL, 默认当前 UTC 时间 |
| `verification_link` | `Optional[str]` | 验证链接（遗留兼容） | NULLABLE, 最大 1000 字符 |
| `raw_headers` | `Optional[str]` | 原始邮件头 | NULLABLE, TEXT 类型 |

### 关系

- `mailbox`: 多对一关系，关联到 `Mailbox` 模型
- `attachments`: 一对多关系，关联到 `Attachment` 模型

### 数据库表定义

```python
class Email(Base):
    """Email message model."""

    __tablename__ = "emails"
    __table_args__ = (
        Index("idx_emails_mailbox", "mailbox_id"),
        Index("idx_emails_folder", "folder"),
        Index("idx_emails_received", "received_at", postgresql_ops={"received_at": "DESC"}),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mailbox_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mailboxes.id"), nullable=False
    )
    message_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    from_address: Mapped[str] = mapped_column(String(255), nullable=False)
    to_address: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    html_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    folder: Mapped[str] = mapped_column(String(50), default="inbox", nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    verification_link: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True
    )  # Legacy compatibility
    raw_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    mailbox: Mapped["Mailbox"] = relationship("Mailbox", back_populates="emails")
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", back_populates="email", cascade="all, delete-orphan"
    )
```

### 特殊字段说明

#### `message_id`
- RFC 5322 标准的邮件唯一标识符（如 `<abc123@example.com>`）
- 确保邮件去重（UNIQUE 约束）

#### `folder`
- 支持邮件分类（inbox, sent, trash 等）
- 默认值为 "inbox"

#### `verification_link`
- 遗留字段，用于兼容旧版本
- 存储邮件中的验证链接（如注册验证、密码重置等）

#### `raw_headers`
- 存储完整的原始邮件头信息
- 用于调试和高级功能（如垃圾邮件分析）

---

## Attachment 模型

邮件附件模型，存储附件的元数据和存储路径。

### 字段说明

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| `id` | `int` | 主键 ID | PRIMARY KEY, AUTO_INCREMENT |
| `email_id` | `int` | 所属邮件 ID | FOREIGN KEY → emails.id, NOT NULL |
| `filename` | `str` | 文件名 | NOT NULL, 最大 255 字符 |
| `content_type` | `str` | MIME 类型 | NOT NULL, 最大 100 字符 |
| `size` | `int` | 文件大小（字节） | NOT NULL |
| `storage_path` | `str` | 存储路径 | NOT NULL, 最大 500 字符 |

### 关系

- `email`: 多对一关系，关联到 `Email` 模型

### 数据库表定义

```python
class Attachment(Base):
    """Email attachment model."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("emails.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Relationships
    email: Mapped["Email"] = relationship("Email", back_populates="attachments")
```

### 字段详解

#### `content_type`
- 标准 MIME 类型（如 `image/png`, `application/pdf`）
- 用于前端正确显示附件图标和处理方式

#### `storage_path`
- 相对或绝对路径
- 实际文件存储位置（可能是本地文件系统或对象存储）

---

## 关系映射详解

### 1. Mailbox → Email (一对多)

**Mailbox 端配置:**
```python
emails: Mapped[List["Email"]] = relationship(
    "Email",
    back_populates="mailbox",
    cascade="all, delete-orphan"
)
```

**Email 端配置:**
```python
mailbox: Mapped["Mailbox"] = relationship(
    "Mailbox",
    back_populates="emails"
)
```

**关键参数:**
- `back_populates`: 双向关系，指定对方的属性名
- `cascade="all, delete-orphan"`: 级联删除配置
  - `all`: 所有操作级联（保存、更新、删除等）
  - `delete-orphan`: 当关系断开时删除孤儿记录

**实际效果:**
```python
# 删除邮箱时，所有关联的邮件也会被删除
session.delete(mailbox)
session.commit()  # 自动删除所有 mailbox.emails
```

### 2. Email → Attachment (一对多)

**Email 端配置:**
```python
attachments: Mapped[List["Attachment"]] = relationship(
    "Attachment",
    back_populates="email",
    cascade="all, delete-orphan"
)
```

**Attachment 端配置:**
```python
email: Mapped["Email"] = relationship(
    "Email",
    back_populates="attachments"
)
```

**实际效果:**
```python
# 删除邮件时，所有附件也会被删除
session.delete(email)
session.commit()  # 自动删除所有 email.attachments
```

### 级联删除链

```
删除 Mailbox
  → 触发 cascade="all, delete-orphan"
  → 删除所有关联的 Email
    → 再次触发 cascade="all, delete-orphan"
    → 删除所有关联的 Attachment
```

---

## 索引设计

索引定义在 `Email` 模型的 `__table_args__` 中：

```python
__table_args__ = (
    Index("idx_emails_mailbox", "mailbox_id"),
    Index("idx_emails_folder", "folder"),
    Index("idx_emails_received", "received_at", postgresql_ops={"received_at": "DESC"}),
)
```

### 索引详解

| 索引名 | 字段 | 用途 | 优化查询 |
|--------|------|------|----------|
| `idx_emails_mailbox` | `mailbox_id` | 加速按邮箱查询 | `WHERE mailbox_id = ?` |
| `idx_emails_folder` | `folder` | 加速按文件夹查询 | `WHERE folder = 'inbox'` |
| `idx_emails_received` | `received_at DESC` | 加速时间倒序排序 | `ORDER BY received_at DESC` |

### 索引选择原则

1. **外键索引** (`mailbox_id`):
   - JOIN 操作和外键约束性能优化
   - 查询某个邮箱的所有邮件时避免全表扫描

2. **分类字段索引** (`folder`):
   - 高频过滤条件（inbox, sent, trash）
   - 基数适中（值的数量有限）

3. **时间戳倒序索引** (`received_at DESC`):
   - 支持 PostgreSQL 专用优化
   - 最新邮件优先显示（最常见的排序需求）

### PostgreSQL 特定优化

```python
postgresql_ops={"received_at": "DESC"}
```

- 创建降序索引（B-Tree 索引）
- 直接支持 `ORDER BY received_at DESC` 查询
- 避免额外的排序操作

---

## SQLAlchemy 2.0 新语法

本项目使用 SQLAlchemy 2.0+ 的现代化类型注解语法。

### `Mapped` 类型注解

**旧语法 (1.4):**
```python
class Mailbox(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
```

**新语法 (2.0):**
```python
class Mailbox(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
```

### 优势

1. **类型安全**: IDE 和 mypy 可以进行类型检查
2. **可读性**: 类型注解清晰表达字段类型
3. **自动推断**: 某些情况下可以省略 `mapped_column` 的类型参数

### `Optional` 类型

表示可为 `None` 的字段：

```python
# 可为 NULL 的字段
display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

# 不可为 NULL 的字段
email: Mapped[str] = mapped_column(String(255), nullable=False)
```

### 关系类型注解

```python
# 一对多（返回列表）
emails: Mapped[List["Email"]] = relationship(...)

# 多对一（返回单个对象）
mailbox: Mapped["Mailbox"] = relationship(...)
```

使用字符串 `"Email"` 是因为前向引用（类尚未定义完成）。

---

## 使用示例

### 1. 创建邮箱和接收邮件

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from emailhandler.models import Base, Mailbox, Email, Attachment
from datetime import datetime

# 创建数据库引擎
engine = create_engine("sqlite:///emailhandler.db")
Base.metadata.create_all(engine)

# 创建会话
session = Session(engine)

# 创建邮箱
mailbox = Mailbox(
    email="temp123@example.com",
    display_name="临时邮箱"
)
session.add(mailbox)
session.commit()

# 接收邮件
email = Email(
    mailbox_id=mailbox.id,
    message_id="<abc123@sender.com>",
    from_address="sender@example.com",
    to_address=mailbox.email,
    subject="欢迎使用临时邮箱",
    text_body="这是一封测试邮件",
    html_body="<h1>这是一封测试邮件</h1>",
    received_at=datetime.utcnow()
)
session.add(email)
session.commit()

# 添加附件
attachment = Attachment(
    email_id=email.id,
    filename="document.pdf",
    content_type="application/pdf",
    size=102400,  # 100KB
    storage_path="/uploads/2024/01/document.pdf"
)
session.add(attachment)
session.commit()
```

### 2. 查询邮箱的所有邮件

```python
# 方式 1: 通过关系属性
mailbox = session.query(Mailbox).filter_by(email="temp123@example.com").first()
for email in mailbox.emails:
    print(f"主题: {email.subject}")
    print(f"附件数: {len(email.attachments)}")

# 方式 2: 直接查询 Email 表
emails = session.query(Email).filter_by(mailbox_id=mailbox.id).all()
```

### 3. 获取最新的 10 封邮件

```python
from sqlalchemy import desc

latest_emails = (
    session.query(Email)
    .filter_by(mailbox_id=mailbox.id, folder="inbox")
    .order_by(desc(Email.received_at))  # 使用索引 idx_emails_received
    .limit(10)
    .all()
)

for email in latest_emails:
    print(f"{email.received_at} - {email.subject}")
```

### 4. 标记邮件为已读

```python
email = session.query(Email).filter_by(message_id="<abc123@sender.com>").first()
email.is_read = True
session.commit()
```

### 5. 移动邮件到垃圾箱

```python
email.folder = "trash"
session.commit()
```

### 6. 级联删除演示

```python
# 删除邮箱（会自动删除所有邮件和附件）
mailbox = session.query(Mailbox).filter_by(email="temp123@example.com").first()
session.delete(mailbox)
session.commit()

# 验证：所有关联的 Email 和 Attachment 都已被删除
emails_count = session.query(Email).filter_by(mailbox_id=mailbox.id).count()
print(f"剩余邮件数: {emails_count}")  # 输出: 0
```

### 7. 查询带附件的邮件

```python
from sqlalchemy.orm import joinedload

# 使用 joinedload 预加载附件，避免 N+1 查询
emails_with_attachments = (
    session.query(Email)
    .options(joinedload(Email.attachments))
    .filter(Email.attachments.any())  # 只查询有附件的邮件
    .all()
)

for email in emails_with_attachments:
    print(f"主题: {email.subject}")
    for att in email.attachments:
        print(f"  - {att.filename} ({att.size} bytes)")
```

### 8. 统计邮箱中未读邮件数

```python
unread_count = (
    session.query(Email)
    .filter_by(mailbox_id=mailbox.id, is_read=False)
    .count()
)
print(f"未读邮件: {unread_count} 封")
```

---

## 数据迁移建议

### Alembic 初始化

```bash
# 初始化 Alembic
alembic init alembic

# 生成初始迁移脚本
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 添加新字段示例

如果需要添加新字段（如 `priority` 优先级字段）：

```python
# 在 Email 模型中添加
priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

# 生成迁移脚本
alembic revision --autogenerate -m "Add priority field to emails"

# 执行迁移
alembic upgrade head
```

---

## 性能优化建议

### 1. 批量操作

```python
# 批量插入邮件
emails = [
    Email(mailbox_id=1, message_id=f"<msg{i}@example.com>", ...)
    for i in range(1000)
]
session.bulk_save_objects(emails)
session.commit()
```

### 2. 分页查询

```python
def get_emails_paginated(mailbox_id, page=1, page_size=20):
    return (
        session.query(Email)
        .filter_by(mailbox_id=mailbox_id)
        .order_by(desc(Email.received_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
```

### 3. 延迟加载 vs 预加载

```python
# 延迟加载（默认）- 可能导致 N+1 查询
emails = session.query(Email).all()
for email in emails:
    print(email.mailbox.email)  # 每次循环都会查询数据库

# 预加载 - 一次性加载所有关联数据
from sqlalchemy.orm import joinedload
emails = session.query(Email).options(joinedload(Email.mailbox)).all()
for email in emails:
    print(email.mailbox.email)  # 不会再次查询数据库
```

---

## 相关文档

- [01-architecture.md](./01-architecture.md) - 项目架构概览
- [03-api.md](./03-api.md) - API 接口文档
- [SQLAlchemy 2.0 官方文档](https://docs.sqlalchemy.org/en/20/)
