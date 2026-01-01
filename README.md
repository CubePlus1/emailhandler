# EmailHandler - 邮件认证框架

**版本**: 2.0.0

轻量级邮件认证框架，用于接收验证邮件、提取链接、自动处理验证。无需浏览器，纯 HTTP 请求。

## 🎯 核心功能

- ✓ 邮件接收服务 (Flask)
- ✓ 验证链接提取
- ✓ 自动链接处理 (HTTP)
- ✓ 验证 ID 提取
- ✓ 完整的 API

## 📦 快速开始

### 1. 安装

```bash
pip install -r requirements.txt
```

### 2. 启动邮件服务

```bash
python email_receiver.py
```

服务运行在 `http://localhost:5000`

### 3. 运行验证工具

在另一个终端：

```bash
python verify.py
```

### 4. 或在代码中使用

```python
from emailhandler import EmailMonitor

monitor = EmailMonitor()
result = monitor.wait_and_handle_verification_link(max_wait=300)

if result['success']:
    print(f"验证 ID: {result['verification_id']}")
```

## 📚 API 参考

### EmailMonitor

```python
from emailhandler import EmailMonitor

monitor = EmailMonitor(api_url='http://localhost:5000')

# 等待邮件
email = monitor.get_verification_link_from_api(max_wait=120)

# 处理链接
result = monitor.handle_verification_link(email['link'])

# 或一步完成
result = monitor.wait_and_handle_verification_link(max_wait=300)
```

### VerificationLinkHandler

```python
from emailhandler import VerificationLinkHandler

handler = VerificationLinkHandler(timeout=30)
result = handler.click_link('https://example.com/verify?id=xxx')
handler.close()

# 或使用快速函数
result = click_verification_link('https://example.com/verify?id=xxx')
```

## 🚀 API 端点

### Flask 邮件服务

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/status` | GET | 服务状态 |
| `/webhook/email` | POST | 接收邮件 |
| `/verification_link` | GET | 获取验证链接 |
| `/emails` | GET | 查看所有邮件 |
| `/clear` | POST | 清空数据 |

## 💡 使用示例

### 示例 1：基础使用

```python
from emailhandler import EmailMonitor

monitor = EmailMonitor()
result = monitor.wait_and_handle_verification_link(max_wait=300)

if result['success']:
    verification_id = result['verification_id']
    print(f"验证成功! ID: {verification_id}")
else:
    print(f"失败: {result['message']}")
```

### 示例 2：手动处理

```python
from emailhandler import EmailMonitor, VerificationLinkHandler

monitor = EmailMonitor()

# 等待邮件
email = monitor.get_verification_link_from_api(max_wait=120)

if email['success']:
    # 手动处理链接
    handler = VerificationLinkHandler()
    result = handler.click_link(email['link'])
    handler.close()
    
    print(f"验证 ID: {result['verification_id']}")
```

### 示例 3：集成到应用

```python
from emailhandler import EmailMonitor

def verify_user(email_address):
    """验证用户邮箱"""
    monitor = EmailMonitor()
    result = monitor.wait_and_handle_verification_link(max_wait=600)
    
    if result['success']:
        return {
            'verified': True,
            'email': email_address,
            'verification_id': result['verification_id']
        }
    else:
        return {
            'verified': False,
            'email': email_address,
            'error': result['message']
        }
```

## 🔧 配置

### API 地址

```python
monitor = EmailMonitor(api_url='http://localhost:5000')
```

### 超时时间

```python
# 等待 10 分钟
result = monitor.wait_and_handle_verification_link(max_wait=600)
```

### HTTP 超时

```python
handler = VerificationLinkHandler(timeout=30)  # 30 秒
```

## 🆘 常见问题

**Q: 邮件服务必须启动吗?**
A: 是的，`email_receiver.py` 提供了 `/verification_link` API

**Q: 支持哪些验证链接格式?**
A: 所有包含验证 ID 的链接格式，自动提取多种格式

**Q: 如何获取邮件内容?**
A: GET `/emails` 端点查看所有接收的邮件

**Q: 如何清空数据?**
A: POST `/clear` 端点清空所有存储的数据

## 📊 项目结构

```
emailhandler/
├── emailhandler/           # 核心模块
│   ├── __init__.py        # 模块导出
│   ├── email_monitor.py   # 邮件监控
│   └── link_handler.py    # 链接处理
├── email_receiver.py       # Flask 邮件服务
├── verify.py              # CLI 工具
├── requirements.txt       # 依赖
├── .gitignore            # Git 忽略
└── README.md             # 本文档
```

## 🌟 特性

- **轻量级** - 仅 2 个依赖 (requests, flask)
- **快速** - 无浏览器，纯 HTTP 请求
- **灵活** - 支持多种验证链接格式
- **可靠** - 完整的错误处理
- **易用** - 简洁的 API 设计
- **文档完善** - 详细的文档和示例

## 📝 返回值格式

### 成功响应

```python
{
    'success': True,
    'verification_id': 'xxx',
    'status_code': 200,
    'final_url': 'https://...',
    'message': '链接已处理 (HTTP 200)'
}
```

### 失败响应

```python
{
    'success': False,
    'verification_id': None,
    'message': '错误描述'
}
```

## 🔐 安全建议

1. 只在受信任的网络中使用
2. 保护 `/webhook/email` 端点
3. 定期清空邮件数据
4. 使用环境变量存储敏感信息
5. 在生产环境中添加认证

## 📞 支持

- 查看完整文档
- 查看代码示例
- 检查日志输出

## 📄 许可证

MIT License

## 👥 作者

EmailHandler Team

---

**让邮件认证变得简单！** 🚀
