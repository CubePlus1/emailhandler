"""
验证链接处理模块 - 纯 HTTP 请求处理
功能：发送 HTTP 请求到验证链接，提取验证 ID
"""

import requests
import time
import re
from urllib.parse import urlparse, parse_qs


class VerificationLinkHandler:
    """验证链接处理器 - 纯 HTTP 请求"""
    
    def __init__(self, timeout=30):
        """
        初始化链接处理器
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置真实的 User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract_verification_id(self, url):
        """
        从 URL 中提取 verificationId
        
        Args:
            url: 验证链接
        
        Returns:
            str: verificationId 或 None
        """
        try:
            patterns = [
                r'[?&]verificationId[=/]?([a-f0-9]{24})',
                r'verification[Ii]d[=/]([a-f0-9]{24})',
                r'/verify/([a-f0-9]{24})',
                r'id=([a-f0-9]{24})',
                r'token=([a-zA-Z0-9_-]{20,})',
                r'code=([a-zA-Z0-9_-]{20,})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
        except Exception:
            return None
    
    def click_link(self, verification_url):
        """
        点击验证链接（发送 HTTP 请求）
        
        Args:
            verification_url: 验证链接 URL
        
        Returns:
            dict: {'success': bool, 'verification_id': str, 'status_code': int, 'message': str}
        """
        try:
            # 提取 verificationId
            verification_id = self.extract_verification_id(verification_url)
            
            # 发送 GET 请求（点击链接）
            response = self.session.get(
                verification_url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True
            )
            
            # 检查响应
            success = response.status_code in [200, 201, 302, 303, 307, 308]
            
            if success:
                # 从响应中再次尝试提取验证 ID
                final_id = self.extract_verification_id(response.url)
                if final_id and not verification_id:
                    verification_id = final_id
                
                return {
                    'success': True,
                    'verification_id': verification_id,
                    'status_code': response.status_code,
                    'final_url': response.url,
                    'message': f'链接已处理 (HTTP {response.status_code})'
                }
            else:
                return {
                    'success': False,
                    'verification_id': verification_id,
                    'status_code': response.status_code,
                    'final_url': response.url,
                    'message': f'请求失败 (HTTP {response.status_code})'
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'verification_id': None,
                'message': f'请求超时 ({self.timeout}s)'
            }
        
        except requests.exceptions.ConnectionError as e:
            return {
                'success': False,
                'verification_id': None,
                'message': f'连接失败: {str(e)[:50]}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'verification_id': None,
                'message': f'异常: {str(e)[:50]}'
            }
    
    def close(self):
        """关闭会话"""
        try:
            self.session.close()
        except:
            pass


def click_verification_link(verification_url, timeout=30):
    """
    快速点击验证链接
    
    Args:
        verification_url: 验证链接
        timeout: 超时时间
    
    Returns:
        dict: 结果信息
    """
    handler = VerificationLinkHandler(timeout=timeout)
    result = handler.click_link(verification_url)
    handler.close()
    return result
