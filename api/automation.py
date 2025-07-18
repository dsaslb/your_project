import json
import random
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, jsonify, request
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore

automation_bp = Blueprint('automation', __name__)

# 자동화 규칙 타입
AUTOMATION_TYPES = {
    'inventory_alert': '재고 부족 알림',
    'staff_schedule': '직원 스케줄 자동화',
    'order_optimization': '주문 최적화',
    'cleaning_reminder': '청소 알림',
    'performance_alert': '성과 알림',
    'maintenance_reminder': '정비 알림'
}

# 자동화 규칙 데이터 생성 (실제 데이터베이스 기반)


def generate_automation_rules():
    """실제 자동화 규칙 데이터 생성"""
    from models_main import AutomationRule

    # 실제 데이터베이스에서 자동화 규칙 조회
    rules = AutomationRule.query.filter_by(is_active=True).all()

    return [
        {
            'id': rule.id,
            'name': rule.name,
            'type': rule.trigger_type,
            'description': rule.description,
            'conditions': rule.trigger_config,
            'actions': rule.action_config,
            'is_active': rule.is_active,
            'created_at': rule.created_at.isoformat(),
            'last_triggered': rule.updated_at.isoformat() if rule.updated_at else None
        }
        for rule in rules
    ]

# 알림 데이터 생성 (실제 데이터베이스 기반)


def generate_notifications():
    """실제 알림 데이터 생성"""
    from models_main import Notification

    # 실제 데이터베이스에서 알림 조회
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(10).all()

    return [
        {
            'id': notification.id,
            'type': notification.category,
            'title': notification.title or '알림',
            'message': notification.content,
            'priority': notification.priority,
            'status': 'read' if notification.is_read else 'unread',
            'created_at': notification.created_at.isoformat(),
            'target_role': notification.recipient_role,
            'action_required': notification.priority in ['urgent', 'important']
        }
        for notification in notifications
    ]


@automation_bp.route('/api/automation/rules', methods=['GET'])
@jwt_required()
def get_automation_rules():
    """자동화 규칙 목록 조회"""
    try:
        rules = generate_automation_rules()

        return jsonify({
            'success': True,
            'data': {
                'rules': rules,
                'summary': {
                    'total_rules': len(rules),
                    'active_rules': len([r for r in rules if r['is_active'] if r is not None else None]),
                    'types': list(AUTOMATION_TYPES.keys())
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/rules', methods=['POST'])
@jwt_required()
def create_automation_rule():
    """새 자동화 규칙 생성"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['name', 'type', 'description', 'conditions', 'actions']
        for field in required_fields if required_fields is not None:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        # 새 규칙 생성 (실제로는 데이터베이스에 저장)
        new_rule = {
            'id': random.randint(1000, 9999),
            'name': data['name'] if data is not None else None,
            'type': data['type'] if data is not None else None,
            'description': data['description'] if data is not None else None,
            'conditions': data['conditions'] if data is not None else None,
            'actions': data['actions'] if data is not None else None,
            'is_active': data.get() if data else None'is_active', True) if data else None,
            'created_at': datetime.now().isoformat(),
            'last_triggered': None
        }

        return jsonify({
            'success': True,
            'data': new_rule,
            'message': '자동화 규칙이 성공적으로 생성되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/rules/<int:rule_id>', methods=['PUT'])
@jwt_required()
def update_automation_rule(rule_id):
    """자동화 규칙 수정"""
    try:
        data = request.get_json()
        rules = generate_automation_rules()

        # 규칙 찾기
        rule = next((r for r in rules if r['id'] if r is not None else None == rule_id), None)
        if not rule:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        # 규칙 업데이트
        for key, value in data.items() if data is not None else []:
            if key in rule:
                rule[key] if rule is not None else None = value

        return jsonify({
            'success': True,
            'data': rule,
            'message': '자동화 규칙이 성공적으로 수정되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/rules/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_automation_rule(rule_id):
    """자동화 규칙 삭제"""
    try:
        rules = generate_automation_rules()

        # 규칙 찾기
        rule = next((r for r in rules if r['id'] if r is not None else None == rule_id), None)
        if not rule:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        return jsonify({
            'success': True,
            'message': '자동화 규칙이 성공적으로 삭제되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/rules/<int:rule_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_automation_rule(rule_id):
    """자동화 규칙 활성화/비활성화 토글"""
    try:
        rules = generate_automation_rules()

        # 규칙 찾기
        rule = next((r for r in rules if r['id'] if r is not None else None == rule_id), None)
        if not rule:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        # 토글
        rule['is_active'] if rule is not None else None = not rule['is_active'] if rule is not None else None

        return jsonify({
            'success': True,
            'data': {
                'id': rule_id,
                'is_active': rule['is_active'] if rule is not None else None
            },
            'message': f'규칙이 {"활성화" if rule["is_active"] if rule is not None else None else "비활성화"}되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """알림 목록 조회"""
    try:
        notifications = generate_notifications()

        # 필터링 옵션
        status = request.args.get() if args else None'status') if args else None
        priority = request.args.get() if args else None'priority') if args else None
        type_filter = request.args.get() if args else None'type') if args else None

        if status:
            notifications = [n for n in notifications if n['status'] if n is not None else None == status]
        if priority:
            notifications = [n for n in notifications if n['priority'] if n is not None else None == priority]
        if type_filter:
            notifications = [n for n in notifications if n['type'] if n is not None else None == type_filter]

        # 읽지 않은 알림 수
        unread_count = len([n for n in notifications if n['status'] if n is not None else None == 'unread'])

        return jsonify({
            'success': True,
            'data': {
                'notifications': notifications,
                'summary': {
                    'total': len(notifications),
                    'unread': unread_count,
                    'high_priority': len([n for n in notifications if n['priority'] if n is not None else None == 'high'])
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    try:
        notifications = generate_notifications()

        # 알림 찾기
        notification = next((n for n in notifications if n['id'] if n is not None else None == notification_id), None)
        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404

        # 읽음 처리
        notification['status'] if notification is not None else None = 'read'

        return jsonify({
            'success': True,
            'message': '알림이 읽음 처리되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/notifications/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """모든 알림 읽음 처리"""
    try:
        notifications = generate_notifications()

        # 모든 읽지 않은 알림을 읽음 처리
        for notification in notifications if notifications is not None:
            if notification['status'] if notification is not None else None == 'unread':
                notification['status'] if notification is not None else None = 'read'

        return jsonify({
            'success': True,
            'message': '모든 알림이 읽음 처리되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """알림 삭제"""
    try:
        notifications = generate_notifications()

        # 알림 찾기
        notification = next((n for n in notifications if n['id'] if n is not None else None == notification_id), None)
        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404

        return jsonify({
            'success': True,
            'message': '알림이 삭제되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/execute', methods=['POST'])
@jwt_required()
def execute_automation():
    """자동화 규칙 실행 (테스트용)"""
    try:
        data = request.get_json()
        rule_id = data.get() if data else None'rule_id') if data else None

        if not rule_id:
            return jsonify({'success': False, 'error': 'Rule ID is required'}), 400

        rules = generate_automation_rules()
        rule = next((r for r in rules if r['id'] if r is not None else None == rule_id), None)

        if not rule:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        if not rule['is_active'] if rule is not None else None:
            return jsonify({'success': False, 'error': 'Rule is not active'}), 400

        # 규칙 실행 시뮬레이션
        execution_result = {
            'rule_id': rule_id,
            'rule_name': rule['name'] if rule is not None else None,
            'executed_at': datetime.now().isoformat(),
            'actions_executed': rule['actions'] if rule is not None else None,
            'status': 'success'
        }

        return jsonify({
            'success': True,
            'data': execution_result,
            'message': '자동화 규칙이 성공적으로 실행되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/api/automation/statistics', methods=['GET'])
@jwt_required()
def get_automation_statistics():
    """자동화 통계"""
    try:
        rules = generate_automation_rules()
        notifications = generate_notifications()

        # 통계 계산
        total_rules = len(rules)
        active_rules = len([r for r in rules if r['is_active'] if r is not None else None])

        # 타입별 규칙 수
        type_counts = {}
        for rule in rules if rules is not None:
            rule_type = rule['type'] if rule is not None else None
            type_counts[rule_type] if type_counts is not None else None = type_counts.get() if type_counts else Nonerule_type, 0) if type_counts else None + 1

        # 알림 통계
        total_notifications = len(notifications)
        unread_notifications = len([n for n in notifications if n['status'] if n is not None else None == 'unread'])
        high_priority_notifications = len([n for n in notifications if n['priority'] if n is not None else None == 'high'])

        # 최근 실행된 규칙
        recent_executions = [
            {
                'rule_name': rule['name'] if rule is not None else None,
                'last_triggered': rule['last_triggered'] if rule is not None else None,
                'type': rule['type'] if rule is not None else None
            }
            for rule in rules if rule['last_triggered'] if rule is not None else None
        ]

        return jsonify({
            'success': True,
            'data': {
                'rules': {
                    'total': total_rules,
                    'active': active_rules,
                    'inactive': total_rules - active_rules,
                    'by_type': type_counts
                },
                'notifications': {
                    'total': total_notifications,
                    'unread': unread_notifications,
                    'high_priority': high_priority_notifications
                },
                'recent_executions': recent_executions
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
