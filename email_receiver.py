"""
邮件接收服务 - Flask 应用
功能：接收验证邮件、存储链接、提供 API
"""

import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 存储邮件和链接
emails = []
verification_links = []


def extract_verification_link(html_content):
    """从 HTML 邮件内容中提取验证链接"""
    import re
    
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


@app.route('/')
def index():
    """主页"""
    return jsonify({
        'name': 'EmailHandler - 邮件认证服务',
        'version': '2.0.0',
        'status': 'running',
        'endpoints': {
            'POST /webhook/email': '接收邮件',
            'GET /verification_link': '获取验证链接',
            'GET /emails': '查看所有邮件',
            'GET /status': '服务状态',
            'POST /clear': '清空数据'
        }
    })


@app.route('/status')
def status():
    """服务状态"""
    return jsonify({
        'status': 'running',
        'emails_count': len(emails),
        'links_count': len(verification_links),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/webhook/email', methods=['POST'])
def receive_email():
    """接收邮件（从 Cloudflare Worker 或其他来源）"""
    try:
        data = request.get_json() or {}
        
        # 提取邮件信息
        email_data = {
            'timestamp': datetime.now().isoformat(),
            'from': data.get('from', 'unknown'),
            'to': data.get('to', 'unknown'),
            'subject': data.get('subject', 'No Subject'),
            'html': data.get('html', ''),
            'text': data.get('text', ''),
        }
        
        # 提取验证链接
        html_content = email_data['html'] or email_data['text']
        verification_link = extract_verification_link(html_content)
        
        if verification_link:
            email_data['verification_link'] = verification_link
            verification_links.append({
                'link': verification_link,
                'subject': email_data['subject'],
                'from': email_data['from'],
                'timestamp': email_data['timestamp']
            })
        
        emails.append(email_data)
        
        return jsonify({
            'success': True,
            'message': '邮件已接收',
            'verification_link': verification_link
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@app.route('/verification_link')
def get_verification_link():
    """获取最新的验证链接"""
    if verification_links:
        link_data = verification_links[-1]
        return jsonify({
            'success': True,
            'link': link_data['link'],
            'subject': link_data['subject'],
            'from': link_data.get('from', ''),
            'timestamp': link_data['timestamp']
        }), 200
    
    return jsonify({
        'success': False,
        'message': '暂无验证链接'
    }), 404


@app.route('/emails')
def get_emails():
    """查看所有邮件"""
    return jsonify({
        'count': len(emails),
        'emails': emails
    }), 200


@app.route('/clear', methods=['POST'])
def clear_data():
    """清空所有数据"""
    global emails, verification_links
    
    emails = []
    verification_links = []
    
    return jsonify({
        'success': True,
        'message': '数据已清空'
    }), 200


def run_server(host='127.0.0.1', port=5000, debug=False):
    """运行服务器"""
    print(f"\n{'='*60}")
    print(f"  邮件接收服务 - EmailHandler")
    print(f"{'='*60}")
    print(f"\n📍 服务地址: http://{host}:{port}")
    print(f"\n📋 可用端点:")
    print(f"  - POST /webhook/email  - 接收邮件")
    print(f"  - GET /verification_link - 获取验证链接")
    print(f"  - GET /emails          - 查看所有邮件")
    print(f"  - GET /status          - 服务状态")
    print(f"  - POST /clear          - 清空数据")
    print(f"\n{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
