"""
邮件监控模块 - 监听邮件并处理验证链接
"""

import time
import requests
from .link_handler import VerificationLinkHandler


class EmailMonitor:
    """邮件监控和验证链接处理器"""
    
    def __init__(self, api_url='http://localhost:5000'):
        """
        初始化邮件监控
        
        Args:
            api_url: 邮件接收服务的 API 地址
        """
        self.api_url = api_url
    
    def get_verification_link_from_api(self, max_wait=120):
        """
        从邮件接收服务获取验证链接
        
        Args:
            max_wait: 最多等待的秒数
        
        Returns:
            dict: {'success': bool, 'link': str, 'subject': str}
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # 获取最新验证链接
                response = requests.get(
                    f'{self.api_url}/verification_link',
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('link'):
                        return {
                            'success': True,
                            'link': data.get('link'),
                            'subject': data.get('subject', '')
                        }
            
            except Exception:
                pass
            
            # 等待 2 秒后重试
            time.sleep(2)
        
        return {'success': False, 'message': '等待超时'}
    
    def handle_verification_link(self, verification_link):
        """
        处理验证链接（发送 HTTP 请求）
        
        Args:
            verification_link: 验证链接 URL
        
        Returns:
            dict: {'success': bool, 'verification_id': str, 'message': str}
        """
        try:
            handler = VerificationLinkHandler(timeout=30)
            result = handler.click_link(verification_link)
            handler.close()
            
            return result
        
        except Exception as e:
            return {
                'success': False,
                'verification_id': None,
                'message': str(e)
            }
    
    def wait_and_handle_verification_link(self, max_wait=120):
        """
        等待邮件并处理验证链接
        
        Args:
            max_wait: 最多等待的秒数
        
        Returns:
            dict: {'success': bool, 'verification_id': str, 'message': str}
        """
        try:
            # 第一步：等待邮件
            email_result = self.get_verification_link_from_api(max_wait=max_wait)
            
            if not email_result.get('success'):
                return {
                    'success': False,
                    'verification_id': None,
                    'message': email_result.get('message', '获取验证链接失败')
                }
            
            verification_link = email_result.get('link')
            
            if not verification_link:
                return {
                    'success': False,
                    'verification_id': None,
                    'message': '验证链接为空'
                }
            
            # 第二步：处理验证链接
            result = self.handle_verification_link(verification_link)
            
            return result
        
        except Exception as e:
            return {
                'success': False,
                'verification_id': None,
                'message': str(e)
            }
