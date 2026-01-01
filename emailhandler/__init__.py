"""
EmailHandler - 邮件认证和链接处理框架
用于接收验证邮件、提取链接、自动处理验证
"""

from .link_handler import VerificationLinkHandler, click_verification_link
from .email_monitor import EmailMonitor

__version__ = '2.0.0'
__author__ = 'EmailHandler Team'
__license__ = 'MIT'

__all__ = [
    'VerificationLinkHandler',
    'click_verification_link',
    'EmailMonitor',
]
