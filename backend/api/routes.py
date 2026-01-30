"""
API 路由模块
提供邮箱和邮件管理的 REST API 端点
"""

from flask import Blueprint, request, jsonify
from backend.emailhandler.models import Mailbox, Email, Attachment


# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/mailboxes', methods=['GET'])
def get_mailboxes():
    """获取所有邮箱

    Returns:
        tuple: (邮箱列表 JSON, HTTP状态码)
    """
    from flask import current_app
    db = current_app.extensions['sqlalchemy']

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


@api_bp.route('/emails/<int:id>', methods=['GET'])
def get_email_detail(id):
    """获取单个邮件详情

    Args:
        id (int): 邮件 ID

    Returns:
        tuple: (邮件详情 JSON, HTTP状态码)
    """
    from flask import current_app
    db = current_app.extensions['sqlalchemy']

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


@api_bp.route('/emails/<int:id>', methods=['PATCH'])
def update_email(id):
    """更新邮件

    支持更新字段: is_read, is_starred, folder

    Args:
        id (int): 邮件 ID

    Returns:
        tuple: (更新结果 JSON, HTTP状态码)
    """
    from flask import current_app
    db = current_app.extensions['sqlalchemy']

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


@api_bp.route('/emails/<int:id>', methods=['DELETE'])
def delete_email(id):
    """删除邮件

    同时删除关联的附件

    Args:
        id (int): 邮件 ID

    Returns:
        tuple: (删除结果 JSON, HTTP状态码)
    """
    from flask import current_app
    db = current_app.extensions['sqlalchemy']

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


@api_bp.route('/search', methods=['GET'])
def search_emails():
    """全文搜索邮件

    支持搜索字段: subject, text_body, html_body, from_address

    Query参数:
        q (str): 搜索关键词

    Returns:
        tuple: (搜索结果 JSON, HTTP状态码)
    """
    from flask import current_app
    db = current_app.extensions['sqlalchemy']

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
