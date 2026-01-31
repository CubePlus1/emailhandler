# 依赖管理与环境配置

本文档详细说明了 EmailHandler 项目的环境配置、依赖管理和部署准备步骤。

---

## 1. Python 虚拟环境设置

### 🚨 重要：虚拟环境是必需的

**EmailHandler 项目强制要求使用虚拟环境。** 这可以：
- 隔离项目依赖，避免全局污染
- 确保不同项目间的依赖版本不冲突
- 便于在不同环境中复现相同的依赖配置
- 简化部署和依赖管理

### 1.1 创建虚拟环境

**Windows:**
```bash
# 在项目根目录下
python -m venv venv
```

**Linux/macOS:**
```bash
python3 -m venv venv
```

### 1.2 激活虚拟环境

**Windows (CMD):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

**激活成功的标志：** 命令提示符前会显示 `(venv)`

### 1.3 退出虚拟环境

```bash
deactivate
```

---

## 2. 依赖安装

### 2.1 标准安装方式

**确保虚拟环境已激活后**，执行：

```bash
pip install -r requirements.txt
```

### 2.2 使用 uv 加速安装（推荐）

如果已安装 [uv](https://github.com/astral-sh/uv)（更快的 pip 替代品）：

```bash
uv pip install -r requirements.txt
```

**安装 uv：**
```bash
# Windows/Linux/macOS
pip install uv
```

### 2.3 验证安装

```bash
# 查看已安装的包
pip list

# 检查关键依赖
python -c "import flask; print(f'Flask {flask.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy {sqlalchemy.__version__}')"
```

---

## 3. 依赖说明

### 3.1 requirements.txt 详解

| 依赖包 | 版本范围 | 用途 |
|--------|---------|------|
| **flask** | >=3.1.2, <4 | Web 应用框架，提供路由、请求处理等核心功能 |
| **flask-sqlalchemy** | >=3.0, <4 | Flask 的 SQLAlchemy 扩展，简化数据库操作 |
| **flask-cors** | >=4.0, <5 | 跨域资源共享（CORS）支持，允许前端跨域请求 |
| **sqlalchemy** | >=2.0, <3 | Python SQL 工具包和对象关系映射（ORM）库 |
| **alembic** | >=1.13, <2 | 数据库迁移工具，管理数据库结构变更 |
| **pyjwt** | >=2.8, <3 | JSON Web Token 实现，用于未来的身份验证功能 |
| **requests** | >=2.31.0 | HTTP 客户端库，用于发送邮件等外部 API 调用 |
| **python-dotenv** | >=1.0, <2 | 从 `.env` 文件加载环境变量 |
| **gunicorn** | >=21.0, <22 | 生产级 WSGI HTTP 服务器（仅 Linux/macOS） |
| **psycopg2-binary** | >=2.9, <3 | PostgreSQL 数据库适配器（可选） |

### 3.2 依赖分类

**核心依赖（必需）：**
- Flask 框架栈（flask, flask-sqlalchemy, flask-cors）
- SQLAlchemy ORM（sqlalchemy, alembic）
- 工具库（requests, python-dotenv）

**可选依赖：**
- `gunicorn`：仅用于生产环境（Windows 下不支持，使用 waitress 替代）
- `psycopg2-binary`：仅在使用 PostgreSQL 时需要

---

## 4. 环境变量配置

### 4.1 创建 .env 文件

在 `backend/` 目录下创建 `.env` 文件：

```bash
# backend/.env

# Flask 配置
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# 数据库配置（SQLite - 开发环境）
DATABASE_URL=sqlite:///emailhandler.db

# 或使用 PostgreSQL（生产环境推荐）
# DATABASE_URL=postgresql://username:password@localhost:5432/emailhandler

# 邮件服务配置
EMAIL_SENDER_API_KEY=your_api_key_here
EMAIL_SERVICE_URL=https://api.your-email-service.com/send

# CORS 配置（允许的前端域名）
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 日志级别
LOG_LEVEL=DEBUG
```

### 4.2 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|-----|--------|------|
| `FLASK_APP` | 是 | app.py | Flask 应用入口文件 |
| `FLASK_ENV` | 否 | production | 运行环境：development/production |
| `SECRET_KEY` | 是 | - | Flask 会话加密密钥（生产环境必须修改） |
| `DATABASE_URL` | 是 | sqlite:/// | 数据库连接 URL |
| `EMAIL_SENDER_API_KEY` | 否 | - | 邮件服务 API 密钥 |
| `EMAIL_SERVICE_URL` | 否 | - | 邮件服务 API 端点 |
| `CORS_ORIGINS` | 否 | * | 允许的 CORS 来源（逗号分隔） |
| `LOG_LEVEL` | 否 | INFO | 日志级别：DEBUG/INFO/WARNING/ERROR |

### 4.3 安全注意事项

⚠️ **重要：**
- `.env` 文件包含敏感信息，**不要提交到 Git**（已在 `.gitignore` 中排除）
- 生产环境必须使用强随机 `SECRET_KEY`
- 数据库密码应使用环境变量或密钥管理服务

**生成安全的 SECRET_KEY：**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 5. 数据库配置

### 5.1 SQLite（开发环境）

**优点：**
- 无需额外安装，开箱即用
- 配置简单，适合本地开发

**配置：**
```bash
# backend/.env
DATABASE_URL=sqlite:///emailhandler.db
```

**数据库文件位置：** `backend/emailhandler.db`

### 5.2 PostgreSQL（生产环境推荐）

**优点：**
- 高并发支持
- 完整的 ACID 支持
- 适合生产环境

**安装 PostgreSQL：**

**Windows:**
```bash
# 下载安装包：https://www.postgresql.org/download/windows/
# 或使用 Chocolatey
choco install postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**创建数据库：**
```bash
# 进入 PostgreSQL 命令行
psql -U postgres

# 创建数据库和用户
CREATE DATABASE emailhandler;
CREATE USER emailhandler_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE emailhandler TO emailhandler_user;
\q
```

**配置：**
```bash
# backend/.env
DATABASE_URL=postgresql://emailhandler_user:your_password@localhost:5432/emailhandler
```

### 5.3 数据库迁移（Alembic）

**初始化迁移环境（仅首次）：**
```bash
cd backend
flask db init
```

**创建迁移脚本：**
```bash
# 自动检测模型变更并生成迁移脚本
flask db migrate -m "Initial migration"
```

**应用迁移：**
```bash
# 将变更应用到数据库
flask db upgrade
```

**常用迁移命令：**
```bash
# 查看当前版本
flask db current

# 查看迁移历史
flask db history

# 回滚上一次迁移
flask db downgrade

# 回滚到指定版本
flask db downgrade <revision_id>
```

**迁移文件位置：** `backend/migrations/versions/`

---

## 6. 开发环境 vs 生产环境

### 6.1 开发环境配置

```bash
# backend/.env
FLASK_ENV=development
DATABASE_URL=sqlite:///emailhandler.db
LOG_LEVEL=DEBUG
```

**启动方式：**
```bash
cd backend
python app.py
# 或
flask run
```

**特点：**
- 自动重载（代码修改后自动重启）
- 详细的错误堆栈信息
- SQLite 数据库

### 6.2 生产环境配置

```bash
# backend/.env
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost:5432/emailhandler
SECRET_KEY=<strong-random-key>
LOG_LEVEL=INFO
```

**启动方式（Linux/macOS）：**
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**启动方式（Windows）：**
```bash
# 使用 waitress 替代 gunicorn
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

**特点：**
- 多进程/线程处理
- PostgreSQL 数据库
- 生产级 WSGI 服务器
- 日志记录到文件

### 6.3 配置对比表

| 配置项 | 开发环境 | 生产环境 |
|--------|---------|---------|
| **FLASK_ENV** | development | production |
| **数据库** | SQLite | PostgreSQL |
| **服务器** | Flask dev server | Gunicorn/Waitress |
| **日志级别** | DEBUG | INFO/WARNING |
| **调试模式** | 开启 | 关闭 |
| **自动重载** | 开启 | 关闭 |

---

## 7. 完整设置流程

### 7.1 首次设置（新开发者）

```bash
# 1. 克隆项目
git clone <repository-url>
cd emailhandler

# 2. 创建并激活虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cd backend
cp .env.example .env  # 如果有示例文件
# 或手动创建 .env 文件，参考上文

# 5. 初始化数据库
flask db upgrade

# 6. 运行应用
python app.py
```

### 7.2 日常开发流程

```bash
# 1. 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 2. 拉取最新代码
git pull

# 3. 更新依赖（如有变更）
pip install -r requirements.txt

# 4. 应用数据库迁移（如有变更）
cd backend
flask db upgrade

# 5. 启动应用
python app.py
```

---

## 8. 故障排查

### 8.1 虚拟环境问题

**问题：** `activate` 命令找不到

**解决方案：**
```bash
# 确保虚拟环境已创建
python -m venv venv

# Windows PowerShell 执行策略问题
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**问题：** 虚拟环境激活后仍使用全局 Python

**解决方案：**
```bash
# 检查 Python 路径
where python  # Windows
which python  # Linux/macOS

# 应该指向 venv 目录下的 Python
```

### 8.2 依赖安装问题

**问题：** `pip install` 失败，提示权限错误

**解决方案：**
```bash
# 确保虚拟环境已激活（不要使用 sudo）
# 如果是虚拟环境，不应该需要 sudo
```

**问题：** `psycopg2-binary` 安装失败

**解决方案：**
```bash
# Windows: 需要安装 Visual C++ Build Tools
# 下载：https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Linux (Ubuntu/Debian):
sudo apt-get install libpq-dev python3-dev

# macOS:
brew install postgresql
```

**问题：** 依赖版本冲突

**解决方案：**
```bash
# 清理并重新安装
pip cache purge
pip uninstall -y -r <(pip freeze)
pip install -r requirements.txt
```

### 8.3 数据库问题

**问题：** `flask db upgrade` 报错 "No such command 'db'"

**解决方案：**
```bash
# 确保已安装 Flask-Migrate
pip install flask-migrate

# 或者重新安装所有依赖
pip install -r requirements.txt
```

**问题：** PostgreSQL 连接失败

**解决方案：**
```bash
# 检查 PostgreSQL 服务是否运行
# Windows:
sc query postgresql-x64-14  # 版本号可能不同

# Linux:
sudo systemctl status postgresql

# macOS:
brew services list

# 检查连接字符串格式
# 正确格式：postgresql://username:password@host:port/database
```

**问题：** SQLite 数据库锁定

**解决方案：**
```bash
# 关闭所有连接到数据库的进程
# 删除数据库文件重新初始化（开发环境）
rm backend/emailhandler.db
flask db upgrade
```

### 8.4 环境变量问题

**问题：** `.env` 文件不生效

**解决方案：**
```bash
# 确认文件位置（应在 backend/ 目录）
ls backend/.env

# 确认已安装 python-dotenv
pip show python-dotenv

# 检查代码中是否加载
# app.py 中应有：
# from dotenv import load_dotenv
# load_dotenv()
```

**问题：** 敏感信息泄露到 Git

**解决方案：**
```bash
# 从 Git 中移除（保留本地文件）
git rm --cached backend/.env
git commit -m "Remove .env from version control"

# 确保 .gitignore 包含
echo ".env" >> .gitignore
```

### 8.5 运行时问题

**问题：** `ModuleNotFoundError: No module named 'xxx'`

**解决方案：**
```bash
# 确认虚拟环境已激活
# 确认依赖已安装
pip list | grep xxx

# 重新安装缺失的包
pip install xxx
```

**问题：** 端口 5000 已被占用

**解决方案：**
```bash
# Windows: 查找并结束占用进程
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -i :5000
kill -9 <PID>

# 或使用其他端口
flask run --port=5001
```

---

## 9. 生产环境部署检查清单

部署到生产环境前，确认以下事项：

- [ ] 使用 PostgreSQL 而非 SQLite
- [ ] 设置强随机的 `SECRET_KEY`
- [ ] `FLASK_ENV=production`
- [ ] 禁用 Flask 调试模式
- [ ] 使用 Gunicorn/Waitress 而非 Flask 内置服务器
- [ ] 配置反向代理（Nginx/Apache）
- [ ] 启用 HTTPS
- [ ] 设置适当的 CORS 策略（不要使用 `*`）
- [ ] 配置日志文件轮转
- [ ] 定期备份数据库
- [ ] 监控应用性能和错误

---

## 10. 进一步阅读

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Alembic 迁移教程](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Gunicorn 部署指南](https://docs.gunicorn.org/en/stable/deploy.html)

---

**文档版本：** 1.0
**最后更新：** 2026-01-30
**维护者：** EmailHandler Team
