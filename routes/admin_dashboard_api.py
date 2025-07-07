from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Branch, User, Order, Notification, SystemLog
from extensions import db

admin_dashboard_api = Blueprint('admin_dashboard_api', __name__, url_prefix='/api/admin')

# 1. 매장별 통계
@admin_dashboard_api.route('/branch_stats', methods=['GET'])
@login_required
def branch_stats():
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    branch_id = request.args.get('branch_id')
    if branch_id:
        branches = Branch.query.filter_by(id=branch_id).all()
    else:
        branches = Branch.query.all()
    stats = []
    for branch in branches:
        user_count = User.query.filter_by(branch_id=branch.id).count()
        order_count = Order.query.filter_by(branch_id=branch.id).count()
        unread_notifications = Notification.query.filter_by(branch_id=branch.id, is_read=False).count()
        stats.append({
            'branch_id': branch.id,
            'branch_name': branch.name,
            'user_count': user_count,
            'order_count': order_count,
            'unread_notifications': unread_notifications,
        })
    return jsonify({'success': True, 'stats': stats})

# 2. 계정 목록 및 승인/차단
@admin_dashboard_api.route('/users', methods=['GET'])
@login_required
def admin_users():
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'status': user.status,
            'branch_id': user.branch_id,
        })
    return jsonify({'success': True, 'users': user_list})

@admin_dashboard_api.route('/user/<int:user_id>/status', methods=['POST'])
@login_required
def update_user_status(user_id):
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': '사용자를 찾을 수 없습니다.'}), 404
    data = request.json
    new_status = data.get('status')
    if new_status not in ['approved', 'blocked', 'pending']:
        return jsonify({'success': False, 'error': '잘못된 상태 값'}), 400
    user.status = new_status
    db.session.commit()
    return jsonify({'success': True, 'user_id': user.id, 'new_status': user.status})

# 3. 시스템 로그
@admin_dashboard_api.route('/system_logs', methods=['GET'])
@login_required
def system_logs():
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(100).all()
    log_list = []
    for log in logs:
        log_list.append({
            'id': log.id,
            'action': log.action,
            'user_id': log.user_id,
            'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'details': log.details if hasattr(log, 'details') else '',
        })
    return jsonify({'success': True, 'logs': log_list}) 