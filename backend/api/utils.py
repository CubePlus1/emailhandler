"""
工具函数模块
提供邮件处理相关的辅助功能
"""

import re


def extract_verification_link(html_content):
    """从 HTML 邮件内容中提取验证链接

    Args:
        html_content (str): HTML 格式的邮件内容

    Returns:
        str | None: 提取到的验证链接，如果未找到则返回 None
    """
    # 常见的验证链接模式
    patterns = [
        r'href=["\']?(https?://[^\s"\'<>]+verify[^\s"\'<>]*)',
        r'href=["\']?(https?://[^\s"\'<>]+confirmation[^\s"\'<>]*)',
        r'href=["\']?(https?://[^\s"\'<>]+validate[^\s"\'<>]*)',
        r'href=["\']?(https?://[^\s"\'<>]+confirm[^\s"\'<>]*)',
        r'(https?://[^\s<>]+(?:verify|verification|confirm|confirmation)[^\s<>]*)',
    ]

    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match:
            return match.group(1)

    return None
