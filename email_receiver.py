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
    # Webhook 认证验证
    webhook_secret = os.getenv('WEBHOOK_SECRET')
    if webhook_secret:
        request_secret = request.headers.get('X-Webhook-Secret')
        if request_secret != webhook_secret:
            return jsonify({
                'error': 'Unauthorized',
                'message': '无效的 webhook 密钥'
            }), 401

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


@app.route('/api/mailboxes', methods=['GET'])
def get_mailboxes():
    """获取所有邮箱"""
    try:
        mailboxes = db.session.query(Mailbox).all()
        return jsonify([{
            'id': m.id,
            'email': m.email,
            'display_name': m.display_name,
            'created_at': m.created_at.isoformat()
        } for m in mailboxes]), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/emails/<int:id>', methods=['GET'])
def get_email_detail(id):
    """获取单个邮件详情"""
    try:
        email = db.session.query(Email).filter_by(id=id).first()
        if not email:
            return jsonify({
                'success': False,
                'message': '邮件不存在'
            }), 404

        attachments = db.session.query(Attachment).filter_by(email_id=id).all()

        return jsonify({
            'id': email.id,
            'mailbox_id': email.mailbox_id,
            'message_id': email.message_id,
            'from_address': email.from_address,
            'to_address': email.to_address,
            'subject': email.subject,
            'html_body': email.html_body,
            'text_body': email.text_body,
            'verification_link': email.verification_link,
            'is_read': email.is_read,
            'is_starred': email.is_starred,
            'folder': email.folder,
            'received_at': email.received_at.isoformat(),
            'attachments': [{
                'id': att.id,
                'filename': att.filename,
                'content_type': att.content_type,
                'size': att.size
            } for att in attachments]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/emails/<int:id>', methods=['PATCH'])
def update_email(id):
    """更新邮件"""
    try:
        email = db.session.query(Email).filter_by(id=id).first()
        if not email:
            return jsonify({
                'success': False,
                'message': '邮件不存在'
            }), 404

        data = request.get_json() or {}

        # 只允许更新特定字段
        if 'is_read' in data:
            email.is_read = bool(data['is_read'])
        if 'is_starred' in data:
            email.is_starred = bool(data['is_starred'])
        if 'folder' in data:
            email.folder = data['folder']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '邮件已更新',
            'email': {
                'id': email.id,
                'is_read': email.is_read,
                'is_starred': email.is_starred,
                'folder': email.folder
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/emails/<int:id>', methods=['DELETE'])
def delete_email(id):
    """删除邮件"""
    try:
        email = db.session.query(Email).filter_by(id=id).first()
        if not email:
            return jsonify({
                'success': False,
                'message': '邮件不存在'
            }), 404

        # 删除关联的附件
        db.session.query(Attachment).filter_by(email_id=id).delete()

        # 删除邮件
        db.session.delete(email)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '邮件已删除'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/search', methods=['GET'])
def search_emails():
    """全文搜索邮件"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'message': '搜索关键词不能为空'
            }), 400

        # 使用 LIKE 进行搜索（如需 FTS5，需额外配置虚拟表）
        search_query = f"%{query}%"
        emails = db.session.query(Email).filter(
            db.or_(
                Email.subject.like(search_query),
                Email.text_body.like(search_query),
                Email.html_body.like(search_query),
                Email.from_address.like(search_query)
            )
        ).order_by(Email.received_at.desc()).limit(100).all()

        return jsonify({
            'success': True,
            'count': len(emails),
            'query': query,
            'emails': [{
                'id': email.id,
                'from_address': email.from_address,
                'to_address': email.to_address,
                'subject': email.subject,
                'received_at': email.received_at.isoformat(),
                'is_read': email.is_read,
                'is_starred': email.is_starred,
                'folder': email.folder,
                'verification_link': email.verification_link
            } for email in emails]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


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
