# EmailHandler v3.0 - 项目结构

```
emailhandler/
├── backend/                   # 后端代码（统一目录）
│   ├── emailhandler/         # Python 核心包（数据层）
│   │   ├── __init__.py      # v3.0.0
│   │   ├── models.py        # 数据库模型
│   │   ├── email_monitor.py # v2.0 兼容
│   │   └── link_handler.py  # v2.0 兼容
│   └── api/                  # API 模块（应用层）
│       ├── __init__.py      # 蓝图导出
│       ├── routes.py        # REST API 路由
│       ├── webhooks.py      # Webhook 处理
│       └── utils.py         # 工具函数
├── cloudflare/               # Cloudflare Worker
│   ├── worker.js            # Email Worker
│   └── wrangler.toml        # Worker 配置
├── frontend/                 # React 前端
│   ├── public/
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/      # UI 组件
│   │   ├── types/          # TypeScript 类型
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── tailwind.config.js
├── migrations/               # Alembic 数据库迁移
│   ├── env.py
│   ├── versions/
│   └── script.py.mako
├── .omc/                     # OMC 文档
│   ├── plans/
│   ├── API.md
│   └── DEVELOPMENT.md
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略规则
├── alembic.ini               # 迁移配置
├── email_receiver.py         # Flask 主应用
├── pyproject.toml            # Python 依赖
├── uv.lock                   # uv 锁文件
└── README.md                 # 项目文档
```

## 已删除的文件

### v2.0 遗留文件
- `tests/` - 旧版测试文件
- `quickstart.py` - 旧版快速开始
- `show_emails.py` - 旧版工具
- `verify.py` - 旧版工具
- `STRUCTURE.md`, `COMPLETION.md` - 旧文档

### 过时配置
- `setup.py` - 已用 pyproject.toml
- `requirements.txt` - 已用 pyproject.toml
- `start.bat`, `start.sh` - 旧启动脚本
- `emailhandler.egg-info/` - 构建产物

## 项目清理完成

文件结构现在更加清晰，只保留必要的 v3.0 文件。
