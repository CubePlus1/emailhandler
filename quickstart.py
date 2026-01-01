"""
快速开始指南
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from emailhandler import EmailMonitor, VerificationLinkHandler

print("\n" + "="*60)
print("  EmailHandler 快速开始")
print("="*60 + "\n")

# 示例 1: 直接处理链接
print("📝 示例 1: 直接处理链接\n")

handler = VerificationLinkHandler(timeout=10)
result = handler.click_link("https://httpbin.org/get?verificationId=abc123def456ab123def456")

print(f"结果: {result['success']}")
print(f"验证 ID: {result['verification_id']}")
print(f"消息: {result['message']}\n")

# 示例 2: 等待邮件并处理
print("📝 示例 2: 等待邮件并处理\n")

monitor = EmailMonitor(api_url='http://localhost:5000')
print("提示: 需要 email_receiver.py 正在运行")
print("      并且已接收验证邮件\n")

# 示例 3: 使用代码
print("📝 示例 3: 在代码中使用\n")

code_example = '''
from emailhandler import EmailMonitor

monitor = EmailMonitor()
result = monitor.wait_and_handle_verification_link(max_wait=300)

if result['success']:
    print(f"验证成功! ID: {result['verification_id']}")
else:
    print(f"失败: {result['message']}")
'''

print(code_example)

print("="*60)
print("✓ 快速开始演示完成")
print("="*60 + "\n")
