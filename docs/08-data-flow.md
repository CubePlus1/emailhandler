# 数据流与生命周期文档

## 概述

本文档详细描述了 EmailHandler 系统中的数据流动、处理流程和邮件生命周期管理。

---

## 1. 邮件接收完整流程

### 1.1 整体流程图

```mermaid
flowchart TB
    A[Cloudflare Email Routing] -->|转发邮件| B[Cloudflare Worker]
    B -->|解析邮件| C{验证 Webhook Secret}
    C -->|验证失败| D[返回 401 Unauthorized]
    C -->|验证成功| E[提取邮件数据]

    E --> F[构建 JSON Payload]
    F -->|POST /webhook/email| G[Flask Webhook 端点]

    G --> H{验证 X-Webhook-Secret}
    H -->|失败| I[返回 401]
    H -->|成功| J[接收 JSON 数据]

    J --> K[提取验证链接]
    K --> L{邮箱是否存在?}

    L -->|否| M[创建新邮箱记录]
    L -->|是| N[获取现有邮箱]

    M --> O[开始数据库事务]
    N --> O

    O --> P[创建邮件记录]
    P --> Q[提交事务]
    Q --> R{提交成功?}

    R -->|失败| S[回滚事务]
    R -->|成功| T[返回 200 OK]

    S --> U[返回 400 错误]
    T --> V[邮件存储完成]
```

### 1.2 数据转换流程

```mermaid
sequenceDiagram
    participant CF as Cloudflare Worker
    participant WH as Webhook 端点
    participant DB as 数据库
    participant Utils as 工具函数

    CF->>WH: POST /webhook/email
    Note over CF,WH: Content-Type: application/json<br/>X-Webhook-Secret: ***

    WH->>WH: 验证密钥

    WH->>Utils: extract_verification_link(html)
    Utils-->>WH: verification_link

    WH->>DB: 查询 Mailbox(email=to_address)
    alt 邮箱不存在
        WH->>DB: INSERT Mailbox
        DB-->>WH: mailbox.id
    else 邮箱已存在
        DB-->>WH: existing mailbox
    end

    WH->>DB: INSERT Email(...)
    WH->>DB: COMMIT

    alt 提交成功
        DB-->>WH: success
        WH-->>CF: 200 OK + verification_link
    else 提交失败
        DB-->>WH: error
        WH->>DB: ROLLBACK
        WH-->>CF: 400 Bad Request
    end
```

---

## 2. API 查询流程

### 2.1 获取验证链接流程

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as Flask API
    participant DB as SQLite 数据库

    Client->>API: GET /verification_link

    API->>DB: SELECT * FROM emails<br/>WHERE verification_link IS NOT NULL<br/>ORDER BY received_at DESC<br/>LIMIT 1

    alt 找到记录
        DB-->>API: Email 对象
        API->>API: 构建响应 JSON
        API-->>Client: 200 OK<br/>{success: true, link: "...", ...}
    else 无记录
        DB-->>API: None
        API-->>Client: 404 Not Found<br/>{success: false, message: "暂无验证链接"}
    end
```

### 2.2 邮件搜索流程

```mermaid
flowchart LR
    A[GET /api/search?q=keyword] --> B{检查搜索关键词}
    B -->|为空| C[返回 400 错误]
    B -->|有效| D[构建 LIKE 查询]

    D --> E[搜索字段]
    E --> F[subject LIKE %keyword%]
    E --> G[text_body LIKE %keyword%]
    E --> H[html_body LIKE %keyword%]
    E --> I[from_address LIKE %keyword%]

    F --> J[OR 组合]
    G --> J
    H --> J
    I --> J

    J --> K[ORDER BY received_at DESC]
    K --> L[LIMIT 100]
    L --> M[返回搜索结果]
```

### 2.3 邮件详情查询时序图

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as /api/emails/:id
    participant DB as 数据库

    Client->>API: GET /api/emails/123

    API->>DB: SELECT * FROM emails WHERE id=123

    alt 邮件存在
        DB-->>API: Email 对象

        API->>DB: SELECT * FROM attachments<br/>WHERE email_id=123
        DB-->>API: Attachment 列表

        API->>API: 组装完整响应
        API-->>Client: 200 OK<br/>{id, subject, attachments: [...]}
    else 邮件不存在
        DB-->>API: None
        API-->>Client: 404 Not Found
    end
```

---

## 3. 验证链接提取流程

### 3.1 链接提取算法

```mermaid
flowchart TB
    A[HTML 邮件内容] --> B[正则表达式匹配]

    B --> C1[模式1: href + verify]
    B --> C2[模式2: href + confirmation]
    B --> C3[模式3: href + validate]
    B --> C4[模式4: href + confirm]
    B --> C5[模式5: URL 包含关键词]

    C1 --> D{匹配成功?}
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D

    D -->|是| E[返回第一个匹配]
    D -->|否| F[返回 None]

    E --> G[存储到 Email.verification_link]
```

### 3.2 验证链接点击流程

```mermaid
sequenceDiagram
    participant User as 用户/自动化
    participant Handler as VerificationLinkHandler
    participant Target as 目标服务器

    User->>Handler: click_link(url)

    Handler->>Handler: extract_verification_id(url)
    Note over Handler: 提取 verificationId

    Handler->>Target: GET url
    Note over Handler,Target: User-Agent: Chrome<br/>Allow Redirects: True

    alt 请求成功
        Target-->>Handler: 200/302 Response
        Handler->>Handler: 从最终 URL 提取 ID
        Handler-->>User: {success: true, verification_id: "..."}
    else 超时
        Target--xHandler: Timeout
        Handler-->>User: {success: false, message: "请求超时"}
    else 连接失败
        Target--xHandler: Connection Error
        Handler-->>User: {success: false, message: "连接失败"}
    end
```

---

## 4. 数据库事务流程

### 4.1 邮件接收事务

```mermaid
stateDiagram-v2
    [*] --> 开始事务

    开始事务 --> 查询邮箱
    查询邮箱 --> 邮箱存在: 已存在
    查询邮箱 --> 创建邮箱: 不存在

    创建邮箱 --> flush
    flush --> 获取邮箱ID
    邮箱存在 --> 获取邮箱ID

    获取邮箱ID --> 创建邮件记录
    创建邮件记录 --> 提交事务

    提交事务 --> 提交成功: 无异常
    提交事务 --> 回滚事务: 异常

    提交成功 --> [*]
    回滚事务 --> [*]
```

### 4.2 邮件删除事务

```mermaid
flowchart TB
    A[DELETE /api/emails/:id] --> B[开始事务]
    B --> C[查询邮件]

    C --> D{邮件存在?}
    D -->|否| E[返回 404]
    D -->|是| F[删除关联附件]

    F --> G[DELETE FROM attachments<br/>WHERE email_id=:id]
    G --> H[删除邮件]
    H --> I[DELETE FROM emails<br/>WHERE id=:id]

    I --> J[提交事务]
    J --> K{提交成功?}

    K -->|是| L[返回 200 OK]
    K -->|否| M[回滚事务]
    M --> N[返回 500 错误]
```

### 4.3 邮件更新事务

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as PATCH /api/emails/:id
    participant DB as 数据库

    Client->>API: PATCH /api/emails/123<br/>{is_read: true, folder: "archive"}

    API->>DB: BEGIN TRANSACTION
    API->>DB: SELECT * FROM emails WHERE id=123

    alt 邮件不存在
        DB-->>API: None
        API-->>Client: 404 Not Found
    else 邮件存在
        DB-->>API: Email 对象

        API->>API: 验证字段<br/>(is_read, is_starred, folder)
        API->>API: 更新允许的字段

        API->>DB: UPDATE emails SET ...<br/>WHERE id=123
        API->>DB: COMMIT

        alt 提交成功
            DB-->>API: Success
            API-->>Client: 200 OK<br/>{success: true, email: {...}}
        else 提交失败
            DB-->>API: Error
            API->>DB: ROLLBACK
            API-->>Client: 500 Internal Error
        end
    end
```

---

## 5. 错误处理流程

### 5.1 Webhook 错误处理

```mermaid
flowchart TB
    A[接收 Webhook 请求] --> B{验证密钥}
    B -->|失败| C[返回 401 Unauthorized]

    B -->|成功| D{解析 JSON}
    D -->|失败| E[返回 400 Bad Request]

    D -->|成功| F[数据库操作]
    F --> G{异常捕获}

    G -->|数据库错误| H[db.session.rollback]
    H --> I[记录错误日志]
    I --> J[返回 400 + 错误信息]

    G -->|无异常| K[返回 200 OK]
```

### 5.2 API 错误分类

```mermaid
graph TB
    A[API 请求] --> B{错误类型}

    B -->|认证错误| C[401 Unauthorized]
    B -->|参数错误| D[400 Bad Request]
    B -->|资源不存在| E[404 Not Found]
    B -->|数据库错误| F[500 Internal Error]
    B -->|搜索参数为空| G[400 + 错误提示]

    C --> H[检查 X-Webhook-Secret]
    D --> I[检查 JSON 格式]
    E --> J[检查资源 ID]
    F --> K[回滚事务]
    G --> L[返回友好提示]
```

### 5.3 链接处理错误流程

```mermaid
flowchart LR
    A[click_link] --> B{异常类型}

    B -->|Timeout| C[返回超时错误]
    B -->|ConnectionError| D[返回连接失败]
    B -->|其他异常| E[返回通用异常]

    C --> F[success: false]
    D --> F
    E --> F

    F --> G[记录错误信息]
    G --> H[返回给调用者]
```

---

## 6. 邮件生命周期

### 6.1 完整生命周期图

```mermaid
stateDiagram-v2
    [*] --> 接收: Cloudflare 转发

    接收 --> 解析: Webhook 处理
    解析 --> 存储: 提取验证链接

    存储 --> inbox: folder="inbox"<br/>is_read=False

    inbox --> 已读: PATCH is_read=true
    inbox --> 星标: PATCH is_starred=true
    inbox --> 归档: PATCH folder="archive"
    inbox --> 垃圾箱: PATCH folder="trash"

    已读 --> 归档
    星标 --> 归档

    归档 --> 垃圾箱
    垃圾箱 --> 永久删除: DELETE /api/emails/:id

    永久删除 --> [*]
```

### 6.2 状态字段说明

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `is_read` | Boolean | `false` | 是否已读 |
| `is_starred` | Boolean | `false` | 是否星标 |
| `folder` | String | `"inbox"` | 所属文件夹 (inbox/archive/trash) |
| `received_at` | DateTime | `utcnow()` | 接收时间 |

### 6.3 数据操作时间线

```mermaid
gantt
    title 邮件数据生命周期时间线
    dateFormat YYYY-MM-DD HH:mm

    section 接收阶段
    Cloudflare 转发      :a1, 2024-01-01 10:00, 1m
    Webhook 处理         :a2, after a1, 2m
    数据库存储           :a3, after a2, 1m

    section 处理阶段
    用户查看邮件         :b1, 2024-01-01 10:30, 5m
    标记已读             :b2, after b1, 1m
    提取验证链接         :b3, after b2, 2m

    section 归档阶段
    移动到归档           :c1, 2024-01-01 12:00, 1m
    长期存储             :c2, after c1, 30d

    section 清理阶段
    移动到垃圾箱         :d1, 2024-02-01 10:00, 1m
    永久删除             :d2, after d1, 1m
```

---

## 7. 关键数据流路径

### 7.1 Webhook 到数据库路径

```
Cloudflare Email Routing
    ↓
Cloudflare Worker (解析邮件)
    ↓
POST /webhook/email
    ↓
webhooks.receive_email()
    ↓
extract_verification_link(html)
    ↓
Mailbox 查询/创建
    ↓
Email 记录创建
    ↓
SQLite 数据库
```

### 7.2 查询到响应路径

```
客户端请求 GET /api/emails/:id
    ↓
routes.get_email_detail(id)
    ↓
db.session.query(Email)
    ↓
db.session.query(Attachment)
    ↓
JSON 序列化
    ↓
HTTP 响应返回
```

### 7.3 搜索流程路径

```
GET /api/search?q=keyword
    ↓
routes.search_emails()
    ↓
构建 LIKE 查询
    ↓
db.session.query(Email).filter(OR(...))
    ↓
ORDER BY received_at DESC
    ↓
LIMIT 100
    ↓
返回结果列表
```

---

## 8. 性能优化点

### 8.1 数据库索引

```sql
-- 邮箱查询索引
CREATE INDEX idx_emails_mailbox ON emails(mailbox_id);

-- 文件夹过滤索引
CREATE INDEX idx_emails_folder ON emails(folder);

-- 时间排序索引 (降序)
CREATE INDEX idx_emails_received ON emails(received_at DESC);
```

### 8.2 查询优化

```mermaid
graph LR
    A[查询优化] --> B[使用索引]
    A --> C[分页限制]
    A --> D[字段选择]

    B --> E[idx_emails_received]
    C --> F[LIMIT 100]
    D --> G[只查询必要字段]
```

### 8.3 事务优化

- 使用 `db.session.flush()` 获取自增 ID 而不立即提交
- 批量操作使用单个事务
- 异常时自动回滚，避免数据不一致

---

## 9. 安全机制

### 9.1 认证流程

```mermaid
sequenceDiagram
    participant Client as 外部服务
    participant Webhook as Webhook 端点
    participant Env as 环境变量

    Client->>Webhook: POST /webhook/email<br/>Header: X-Webhook-Secret

    Webhook->>Env: os.getenv('WEBHOOK_SECRET')
    Env-->>Webhook: expected_secret

    Webhook->>Webhook: 比较密钥

    alt 密钥匹配
        Webhook-->>Client: 继续处理
    else 密钥不匹配
        Webhook-->>Client: 401 Unauthorized
    end
```

### 9.2 CORS 配置

```
允许的来源: os.getenv('CORS_ORIGINS')
默认值: http://localhost:3000
支持多域名: 逗号分隔
```

---

## 10. 监控与日志

### 10.1 关键监控指标

```mermaid
graph TB
    A[监控指标] --> B[邮件接收量]
    A --> C[验证链接提取成功率]
    A --> D[数据库查询性能]
    A --> E[错误率]

    B --> F[/status 端点]
    C --> F
    D --> G[慢查询日志]
    E --> H[异常捕获]
```

### 10.2 状态端点

```json
GET /status

{
  "status": "running",
  "emails_count": 1234,
  "links_count": 456,
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## 总结

本文档涵盖了 EmailHandler 系统的所有关键数据流：

1. **接收流程**: Cloudflare → Webhook → 数据库
2. **查询流程**: API 端点 → 数据库查询 → JSON 响应
3. **验证链接**: 正则提取 → 存储 → HTTP 点击
4. **事务管理**: 开始 → 操作 → 提交/回滚
5. **错误处理**: 异常捕获 → 回滚 → 友好提示
6. **生命周期**: 接收 → 处理 → 归档 → 删除

所有流程都采用可视化 Mermaid 图表展示，便于理解和维护。
