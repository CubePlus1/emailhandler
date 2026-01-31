# Flask 应用主程序 (email_receiver.py)

## 概述

`email_receiver.py` 是整个 EmailHandler 系统的主程序入口，负责初始化 Flask 应用、配置数据库、注册蓝图、启用 CORS，并提供核心 API 端点。

**架构特点：**
- 模块化设计：使用蓝图（Blueprint）模式分离业务逻辑
- 声明式数据库模型：基于 SQLAlchemy 的 DeclarativeBase
- 环境变量配置：通过 `.env` 文件管理敏感信息
- 跨域支持：灵活的 CORS 配置支持前后端分离
- 生产就绪：支持 Gunicorn/uWSGI 部署

---

## 1. Flask 应用启动流程

### 1.1 完整启动流程

```
加载环境变量 (.env)
    ↓
创建 Flask 实例
    ↓
配置应用参数 (JSON, Database, CORS)
    ↓
初始化 SQLAlchemy
    ↓
注册蓝图 (api_bp, webhook_bp)
    ↓
创建数据库表 (db.create_all)
    ↓
启动服务器 (Werkzeug / Gunicorn)
```

### 1.2 应用创建代码

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)

# 核心配置
app.config['JSON_AS_ASCII'] = False                # 支持中文 JSON
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///emails.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

**配置说明：**

| 配置项 | 作用 | 默认值 |
|--------|------|--------|
| `JSON_AS_ASCII` | 禁用 ASCII 编码，允许中文响应 | `False` |
| `SQLALCHEMY_DATABASE_URI` | 数据库连接字符串 | `sqlite:///emails.db` |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | 禁用对象修改追踪（提升性能） | `False` |

---

## 2. 蓝图注册机制

### 2.1 蓝图架构

项目采用 **蓝图模式** 实现模块化路由管理：

```
backend/
├── api/
│   ├── __init__.py       # 导出 api_bp, webhook_bp
│   ├── routes.py         # API 路由 (api_bp)
│   └── webhooks.py       # Webhook 路由 (webhook_bp)
```

### 2.2 蓝图导入与注册

```python
# 从 backend.api 导入蓝图
from backend.api import api_bp, webhook_bp

# 注册蓝图到应用
app.register_blueprint(api_bp)      # 前缀: /api
app.register_blueprint(webhook_bp)  # 无前缀
```

**蓝图路由映射：**

| 蓝图 | URL 前缀 | 定义位置 | 主要功能 |
|------|----------|----------|----------|
| `api_bp` | `/api` | `backend/api/routes.py` | 邮箱/邮件 CRUD API |
| `webhook_bp` | 无 | `backend/api/webhooks.py` | 接收外部 Webhook |

### 2.3 蓝图定义示例

**routes.py (api_bp):**
```python
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/mailboxes', methods=['GET'])
def get_mailboxes():
    # 实际路由: GET /api/mailboxes
    pass
```

**webhooks.py (webhook_bp):**
```python
from flask import Blueprint

webhook_bp = Blueprint('webhooks', __name__)

@webhook_bp.route('/webhook/email', methods=['POST'])
def receive_email():
    # 实际路由: POST /webhook/email
    pass
```

---

## 3. 数据库初始化（SQLAlchemy 配置）

### 3.1 声明式模型系统

项目使用 SQLAlchemy 2.x 的 `DeclarativeBase` 模式：

```python
from backend.emailhandler.models import Base, Mailbox, Email, Attachment

# 使用声明式基类初始化 SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)
```

**关键特性：**
- `Base` 是所有模型的基类（定义在 `models.py`）
- 支持类型提示和现代 Python 语法
- 自动管理表结构映射

### 3.2 表创建流程

```python
# 在应用上下文中创建所有表
with app.app_context():
    db.create_all()
```

**执行时机：**
- 开发模式：每次启动时自动创建表（如果不存在）
- 生产模式：使用 Alembic 进行数据库迁移

### 3.3 数据库访问模式

在蓝图路由中通过 `current_app` 访问数据库：

```python
from flask import current_app

@api_bp.route('/mailboxes', methods=['GET'])
def get_mailboxes():
    db = current_app.extensions['sqlalchemy']
    mailboxes = db.session.query(Mailbox).all()
    # ...
```

**为什么使用 `current_app`？**
- 避免循环导入问题
- 支持应用工厂模式
- 允许多应用实例共存

---

## 4. CORS 配置详解

### 4.1 基本配置

```python
from flask_cors import CORS

CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))
```

### 4.2 环境变量配置

**.env 文件：**
```bash
# 开发环境（多源）
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 生产环境（单源）
CORS_ORIGINS=https://mail.yourdomain.com
```

### 4.3 高级 CORS 配置

如需更精细控制，可以使用字典配置：

```python
cors_config = {
    "origins": os.getenv('CORS_ORIGINS', '*').split(','),
    "methods": ["GET", "POST", "PATCH", "DELETE"],
    "allow_headers": ["Content-Type", "Authorization", "X-Webhook-Secret"],
    "supports_credentials": True,
    "max_age": 3600
}

CORS(app, **cors_config)
```

**参数说明：**

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `origins` | 允许的源列表 | `["https://example.com"]` |
| `methods` | 允许的 HTTP 方法 | `["GET", "POST"]` |
| `allow_headers` | 允许的请求头 | `["Content-Type"]` |
| `supports_credentials` | 是否支持 Cookie | `True` |
| `max_age` | 预检请求缓存时间（秒） | `3600` |

---

## 5. 环境变量加载

### 5.1 加载机制

```python
from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载环境变量
```

### 5.2 环境变量清单

**.env 文件结构：**
```bash
# Flask 配置
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here

# 数据库
DATABASE_URL=sqlite:///emails.db

# Webhook 认证
WEBHOOK_SECRET=your-webhook-secret-here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# SendGrid (可选)
SENDGRID_API_KEY=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### 5.3 安全实践

```python
# ❌ 错误：硬编码敏感信息
app.config['SECRET_KEY'] = 'my-secret-key'

# ✅ 正确：使用环境变量 + 默认值
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-fallback-key')
```

**Git 安全：**
```bash
# .gitignore
.env           # 永远不提交到版本控制
.env.local
*.db           # 不提交数据库文件
```

---

## 6. 生产部署配置（Gunicorn）

### 6.1 为什么使用 Gunicorn？

| 特性 | Werkzeug (开发) | Gunicorn (生产) |
|------|-----------------|-----------------|
| 并发模型 | 单线程 | 多进程/多线程 |
| 性能 | 低 | 高 |
| 稳定性 | 一般 | 优秀 |
| 热重载 | 支持 | 不支持 |
| 适用场景 | 本地开发 | 生产环境 |

### 6.2 Gunicorn 启动命令

```bash
# 基础启动（4 个 worker）
gunicorn -w 4 -b 0.0.0.0:5000 email_receiver:app

# 完整配置
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile access.log \
  --error-logfile error.log \
  --log-level info \
  email_receiver:app
```

**参数说明：**

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `-w` / `--workers` | Worker 进程数 | `(CPU核心数 × 2) + 1` |
| `-b` / `--bind` | 绑定地址和端口 | `0.0.0.0:5000` |
| `--timeout` | 请求超时时间（秒） | `120` |
| `--log-level` | 日志级别 | `info` |

### 6.3 配置文件方式（gunicorn.conf.py）

```python
# gunicorn.conf.py
import os

bind = "0.0.0.0:5000"
workers = int(os.getenv("WORKERS", 4))
worker_class = "sync"
timeout = 120
keepalive = 5

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 性能优化
max_requests = 1000          # 每个 worker 处理 N 个请求后重启
max_requests_jitter = 50     # 随机偏移避免同时重启
preload_app = True           # 预加载应用代码
```

启动命令：
```bash
gunicorn -c gunicorn.conf.py email_receiver:app
```

### 6.4 使用 Systemd 守护进程

**/etc/systemd/system/emailhandler.service:**
```ini
[Unit]
Description=EmailHandler Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/emailhandler
Environment="PATH=/var/www/emailhandler/venv/bin"
ExecStart=/var/www/emailhandler/venv/bin/gunicorn \
  -c gunicorn.conf.py email_receiver:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

管理命令：
```bash
sudo systemctl start emailhandler
sudo systemctl enable emailhandler
sudo systemctl status emailhandler
```

---

## 7. 开发模式 vs 生产模式

### 7.1 模式对比

| 特性 | 开发模式 | 生产模式 |
|------|----------|----------|
| 调试器 | 启用 | 禁用 |
| 代码热重载 | 启用 | 禁用 |
| 详细错误页面 | 显示 | 隐藏 |
| 日志级别 | DEBUG | INFO/WARNING |
| 数据库 | SQLite | PostgreSQL |
| CORS | `localhost:*` | 特定域名 |
| 服务器 | Werkzeug | Gunicorn/uWSGI |

### 7.2 开发模式启动

```python
# email_receiver.py
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True  # 开启调试模式
    )
```

**调试模式特性：**
- 代码修改自动重载
- 异常时显示 Werkzeug 调试器
- 不适合公网暴露（安全风险）

### 7.3 生产模式配置

```python
# 禁用调试模式
app.config['DEBUG'] = False
app.config['TESTING'] = False

# 设置日志级别
import logging
logging.basicConfig(level=logging.INFO)

# 使用生产数据库
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
```

---

## 8. 启动命令示例

### 8.1 开发模式

```bash
# 方法 1：直接运行主程序
python email_receiver.py

# 方法 2：使用 Flask CLI
export FLASK_APP=email_receiver.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

# 方法 3：使用自定义函数
python -c "from email_receiver import run_server; run_server(debug=True)"
```

### 8.2 生产模式

```bash
# Gunicorn（推荐）
gunicorn -w 4 -b 0.0.0.0:5000 email_receiver:app

# uWSGI
uwsgi --http :5000 --wsgi-file email_receiver.py --callable app --processes 4

# Waitress（Windows 友好）
waitress-serve --host=0.0.0.0 --port=5000 email_receiver:app
```

### 8.3 Docker 容器部署

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "email_receiver:app"]
```

**启动命令：**
```bash
docker build -t emailhandler .
docker run -d -p 5000:5000 --env-file .env emailhandler
```

---

## 9. 核心端点示例

### 9.1 主页端点

```python
@app.route('/')
def index():
    """返回 API 端点列表"""
    return jsonify({
        'name': 'EmailHandler - 邮件认证服务',
        'version': '3.0.0',
        'status': 'running',
        'architecture': 'modular',
        'endpoints': {
            'POST /webhook/email': '接收邮件 (Webhook)',
            'GET /verification_link': '获取最新验证链接',
            'GET /emails': '查看所有邮件 (分页)',
            'GET /status': '服务状态'
        }
    })
```

### 9.2 状态端点

```python
@app.route('/status')
def status():
    """返回服务运行状态"""
    emails_count = db.session.query(Email).count()
    links_count = db.session.query(Email).filter(
        Email.verification_link.isnot(None)
    ).count()

    return jsonify({
        'status': 'running',
        'emails_count': emails_count,
        'links_count': links_count,
        'timestamp': datetime.now().isoformat()
    })
```

**测试命令：**
```bash
# 检查服务状态
curl http://localhost:5000/status

# 获取 API 列表
curl http://localhost:5000/
```

---

## 10. 完整应用创建示例

```python
"""
邮件接收服务 - Flask 应用
功能：接收验证邮件、存储链接、提供 API
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# ============ 1. 加载环境变量 ============
load_dotenv()

# ============ 2. 创建 Flask 应用 ============
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///emails.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ============ 3. 导入模型 ============
from backend.emailhandler.models import Base, Mailbox, Email, Attachment

# ============ 4. 初始化 SQLAlchemy ============
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# ============ 5. 配置 CORS ============
CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))

# ============ 6. 注册蓝图 ============
from backend.api import api_bp, webhook_bp
app.register_blueprint(api_bp)
app.register_blueprint(webhook_bp)

# ============ 7. 创建数据库表 ============
with app.app_context():
    db.create_all()

# ============ 8. 定义路由 ============
@app.route('/')
def index():
    return jsonify({'status': 'running', 'version': '3.0.0'})

# ============ 9. 启动服务器 ============
def run_server(host='127.0.0.1', port=5000, debug=False):
    """运行服务器"""
    print(f"\n{'='*60}")
    print(f"  邮件接收服务 - EmailHandler v3.0.0")
    print(f"{'='*60}")
    print(f"\n📍 服务地址: http://{host}:{port}")
    print(f"\n{'='*60}\n")

    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server()
```

---

## 11. 最佳实践

### 11.1 应用工厂模式（高级）

适用于多环境部署或测试场景：

```python
def create_app(config_name='development'):
    """应用工厂函数"""
    app = Flask(__name__)

    # 根据环境加载配置
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    # 初始化扩展
    db.init_app(app)
    CORS(app)

    # 注册蓝图
    app.register_blueprint(api_bp)
    app.register_blueprint(webhook_bp)

    return app

# 使用方式
app = create_app(os.getenv('FLASK_ENV', 'development'))
```

### 11.2 健康检查端点

```python
@app.route('/health')
def health():
    """Kubernetes/Docker 健康检查"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503
```

### 11.3 错误处理

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': '端点不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal Server Error'}), 500
```

---

## 相关文档

- [数据库模型设计 (01-models.md)](./01-models.md)
- [API 路由文档 (02-routes.md)](./02-routes.md)
- [Webhook 处理 (03-webhooks.md)](./03-webhooks.md)
- [工具函数文档 (04-utils.md)](./04-utils.md)
