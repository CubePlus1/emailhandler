"""
Webhook 处理模块
处理来自外部服务的 Webhook 请求
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from backend.emailhandler.models import Mailbox, Email
from .utils import extract_verification_link


# 创建蓝图
webhook_bp = Blueprint('webhooks', __name__)


@webhook_bp.route('/webhook/email', methods=['POST'])
def receive_email():
    """接收邮件（从 Cloudflare Worker 或其他来源）

    接收并处理来自外部邮件服务的 Webhook 请求，
    提取验证链接并存储到数据库

    Returns:
        tuple: (JSON响应, HTTP状态码)
    """
    from flask import current_app
    db = current_app.extensions['sqlalchemy']

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
