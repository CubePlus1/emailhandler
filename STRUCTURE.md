# EmailHandler 项目结构

```
emailhandler/                    # 邮件认证框架 (独立项目)
│
├── emailhandler/               # Python 包
│   ├── __init__.py            # 模块导出
│   ├── link_handler.py        # 验证链接处理 (183 行)
│   └── email_monitor.py       # 邮件监控 (115 行)
│
├── tests/                      # 测试
│   └── __init__.py            # 测试脚本
│
├── email_receiver.py           # Flask 邮件服务 (160 行)
├── verify.py                   # CLI 验证工具 (60 行)
├── quickstart.py               # 快速开始示例
│
├── setup.py                    # setuptools 配置
├── pyproject.toml              # 现代 Python 配置
├── requirements.txt            # 依赖列表
├── .gitignore                  # Git 忽略规则
├── README.md                   # 项目文档
└── start.bat / start.sh        # 快速启动脚本
```

## 核心组件

### emailhandler 包 (Python)
- `link_handler.py` - VerificationLinkHandler 类 (HTTP 请求处理)
- `email_monitor.py` - EmailMonitor 类 (邮件监控协调)

### 应用脚本
- `email_receiver.py` - Flask 服务，监听邮件
- `verify.py` - 命令行工具，自动处理验证
- `quickstart.py` - 快速开始示例

### 配置文件
- `setup.py` - setuptools 配置 (pip install . )
- `pyproject.toml` - 现代 Python 项目配置
- `requirements.txt` - 依赖管理 (pip install -r requirements.txt)
- `.gitignore` - Git 忽略规则

## 特点

✅ **完全独立** - 不依赖 SheerID，纯邮件验证
✅ **轻量级** - 仅 2 个依赖 (requests, flask)
✅ **模块化** - 可独立使用各个组件
✅ **文档完善** - README 和示例齐全
✅ **即插即用** - 克隆即可使用

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
python email_receiver.py      # 终端 1
python verify.py              # 终端 2
```

### 或通过脚本
```bash
python start.bat              # Windows
bash start.sh                 # Linux/Mac
```

## 使用示例

```python
from emailhandler import EmailMonitor

monitor = EmailMonitor()
result = monitor.wait_and_handle_verification_link(max_wait=300)

if result['success']:
    print(f"验证 ID: {result['verification_id']}")
```

## 文件大小

- emailhandler/__init__.py: ~350 bytes
- emailhandler/link_handler.py: ~5.8 KB
- emailhandler/email_monitor.py: ~4.7 KB
- email_receiver.py: ~6.2 KB
- verify.py: ~2.1 KB
- 总计: ~19 KB (压缩核心)

## 版本信息

- **版本**: 2.0.0
- **Python**: 3.9+
- **依赖**: requests>=2.31.0, flask>=3.1.4
- **许可证**: MIT

---

让邮件认证变得简单！🚀
