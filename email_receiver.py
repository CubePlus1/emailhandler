"""
邮件接收服务 - Flask 应用
功能：接收验证邮件、存储链接、提供 API
"""

import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///emails.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models after app config
from emailhandler.models import Base, Mailbox, Email, Attachment

# Initialize SQLAlchemy with Base
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize CORS
CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))

# Create tables
with app.app_context():
    db.create_all()


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
    emails_count = db.session.query(Email).count()
    links_count = db.session.query(Email).filter(Email.verification_link.isnot(None)).count()

    return jsonify({
        'status': 'running',
        'emails_count': emails_count,
        'links_count': links_count,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/webhook/email', methods=['POST'])
def receive_email():
    """接收邮件（从 Cloudflare Worker 或其他来源）"""
    try:
        data = request.get_json() or {}

        # 提取邮件信息
        from_address = data.get('from', 'unknown')
        to_address = data.get('to', 'unknown')
        subject = data.get('subject', 'No Subject')
        html_body = data.get('html', '')
        text_body = data.get('text', '')

        # 提取验证链接
        html_content = html_body or text_body
        verification_link = extract_verification_link(html_content)

        # 确保邮箱存在
        mailbox = db.session.query(Mailbox).filter_by(email=to_address).first()
        if not mailbox:
            mailbox = Mailbox(email=to_address)
            db.session.add(mailbox)
            db.session.flush()  # Get mailbox.id

        # 创建邮件记录
        email = Email(
            mailbox_id=mailbox.id,
            message_id=data.get('message_id', f"{datetime.now().timestamp()}@emailhandler"),
            from_address=from_address,
            to_address=to_address,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            verification_link=verification_link,
            received_at=datetime.utcnow()
        )

        db.session.add(email)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '邮件已接收',
            'verification_link': verification_link
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@app.route('/verification_link')
def get_verification_link():
    """获取最新的验证链接"""
    email = db.session.query(Email).filter(
        Email.verification_link.isnot(None)
    ).order_by(Email.received_at.desc()).first()

    if email:
        return jsonify({
            'success': True,
            'link': email.verification_link,
            'subject': email.subject,
            'from': email.from_address,
            'timestamp': email.received_at.isoformat()
        }), 200

    return jsonify({
        'success': False,
        'message': '暂无验证链接'
    }), 404


@app.route('/emails')
def get_emails():
    """查看所有邮件"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    pagination = db.session.query(Email).order_by(
        Email.received_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    emails_list = [{
        'timestamp': email.received_at.isoformat(),
        'from': email.from_address,
        'to': email.to_address,
        'subject': email.subject,
        'html': email.html_body,
        'text': email.text_body,
        'verification_link': email.verification_link
    } for email in pagination.items]

    return jsonify({
        'count': pagination.total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages,
        'emails': emails_list
    }), 200


@app.route('/clear', methods=['POST'])
def clear_data():
    """清空所有数据"""
    try:
        db.session.query(Email).delete()
        db.session.query(Mailbox).delete()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '数据已清空'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


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
