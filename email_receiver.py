"""
邮件接收服务 - Flask 应用
功能：接收验证邮件、存储链接、提供 API

重构版本 3.0.0 - 模块化架构
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///emails.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models after app config
from backend.emailhandler.models import Base, Mailbox, Email, Attachment

# Initialize SQLAlchemy with Base
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize CORS
CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))

# Register blueprints
from backend.api import api_bp, webhook_bp
app.register_blueprint(api_bp)
app.register_blueprint(webhook_bp)

# Create tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """主页 - API 端点列表"""
    return jsonify({
        'name': 'EmailHandler - 邮件认证服务',
        'version': '3.0.0',
        'status': 'running',
        'architecture': 'modular',
        'endpoints': {
            'POST /webhook/email': '接收邮件 (Webhook)',
            'GET /verification_link': '获取最新验证链接',
            'GET /emails': '查看所有邮件 (分页)',
            'GET /status': '服务状态',
            'POST /clear': '清空数据',
            'GET /api/mailboxes': '获取所有邮箱',
            'GET /api/emails/<id>': '获取单个邮件详情',
            'PATCH /api/emails/<id>': '更新邮件',
            'DELETE /api/emails/<id>': '删除邮件',
            'GET /api/search?q=<keyword>': '搜索邮件'
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
    """查看所有邮件（分页）"""
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
    print(f"  邮件接收服务 - EmailHandler v3.0.0")
    print(f"{'='*60}")
    print(f"\n📍 服务地址: http://{host}:{port}")
    print(f"\n📋 核心端点:")
    print(f"  - POST /webhook/email      - 接收邮件")
    print(f"  - GET  /verification_link  - 获取验证链接")
    print(f"  - GET  /emails             - 查看所有邮件")
    print(f"  - GET  /status             - 服务状态")
    print(f"  - POST /clear              - 清空数据")
    print(f"\n📋 API 端点:")
    print(f"  - GET    /api/mailboxes    - 邮箱列表")
    print(f"  - GET    /api/emails/<id>  - 邮件详情")
    print(f"  - PATCH  /api/emails/<id>  - 更新邮件")
    print(f"  - DELETE /api/emails/<id>  - 删除邮件")
    print(f"  - GET    /api/search       - 搜索邮件")
    print(f"\n{'='*60}\n")

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
