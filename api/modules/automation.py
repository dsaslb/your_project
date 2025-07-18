from api.modules.notification_system import create_notification, send_system_notification  # pyright: ignore
from api.gateway import token_required, role_required  # pyright: ignore
from models_main import db, User, Order, Schedule, Attendance, InventoryItem
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
form = None  # pyright: ignore

automation = Blueprint('automation', __name__)

# 자동화 규칙 저장소 (실제로는 데이터베이스 사용)
_automation_rules = []

# 자동화 작업 저장소
_automation_jobs = []


def create_automation_rule(
    name,
    description,
    trigger_type,
    trigger_conditions,
    actions,
    enabled=True,
    priority='medium'
):
    """자동화 규칙 생성"""
    rule = {
        'id': len(_automation_rules) + 1,
        'name': name,
        'description': description,
        'trigger_type': trigger_type,
        'trigger_conditions': trigger_conditions,
        'actions': actions,
        'enabled': enabled,
        'priority': priority,
        'created_at': datetime.utcnow().isoformat(),
        'last_executed': None,
        'execution_count': 0
    }

    _automation_rules.append(rule)
    return rule


def execute_automation_rule(rule, context=None):
    """자동화 규칙 실행"""
    try:
        # 트리거 조건 확인
        if not check_trigger_conditions(rule['trigger_conditions'] if rule is not None else None,  context):
            return False, "트리거 조건이 충족되지 않았습니다"

        # 액션 실행
        results = []
        for action in rule['actions'] if rule and 'actions' in rule else []:
            result = execute_action(action,  context)
            results.append(result)

        # 규칙 실행 기록 업데이트
        if rule is not None:
            rule['last_executed'] = datetime.utcnow().isoformat()
            rule['execution_count'] += 1

        # 작업 로그 생성
        job_log = {
            'id': len(_automation_jobs) + 1,
            'rule_id': rule['id'] if rule is not None else None,
            'rule_name': rule['name'] if rule is not None else None,
            'status': 'success',
            'results': results,
            'executed_at': datetime.utcnow().isoformat(),
            'context': context
        }
        _automation_jobs.append(job_log)

        return True, results

    except Exception as e:
        current_app.logger.error(f"자동화 규칙 실행 오류: {str(e)}")

        # 실패 로그 생성
        job_log = {
            'id': len(_automation_jobs) + 1,
            'rule_id': rule['id'] if rule is not None else None,
            'rule_name': rule['name'] if rule is not None else None,
            'status': 'failed',
            'error': str(e),
            'executed_at': datetime.utcnow().isoformat(),
            'context': context
        }
        _automation_jobs.append(job_log)

        return False, str(e)


def check_trigger_conditions(conditions,  context):
    """트리거 조건 확인"""
    if not conditions:
        return True

    for condition in conditions if conditions is not None else []:
        condition_type = condition.get('type') if condition else None
        condition_value = condition.get('value') if condition else None

        if condition_type == 'time_based':
            # 시간 기반 조건
            current_time = datetime.utcnow()
            if condition_value == 'business_hours':
                # 영업 시간 확인 (9:00-22:00)
                if not (9 <= current_time.hour < 22):
                    return False
            elif condition_value == 'night_hours':
                # 야간 시간 확인 (22:00-9:00)
                if not (current_time.hour >= 22 or current_time.hour < 9):
                    return False

        elif condition_type == 'data_based':
            # 데이터 기반 조건
            field = condition.get('field') if condition else None
            operator = condition.get('operator') if condition else None
            value = condition.get('value') if condition else None

            if not context or field not in context:
                return False

            context_value = context[field] if context is not None else None

            if operator == 'equals' and context_value != value:
                return False
            elif operator == 'greater_than' and context_value <= value:
                return False
            elif operator == 'less_than' and context_value >= value:
                return False
            elif operator == 'contains' and value not in str(context_value):
                return False

    return True


def execute_action(action,  context):
    """액션 실행"""
    action_type = action.get('type') if action else None
    action_params = action.get('params', {}) if action else None

    try:
        if action_type == 'send_notification':
            # 알림 전송
            user_id = action_params.get('user_id') if action_params else None
            title = action_params.get('title', '자동화 알림') if action_params else None
            message = action_params.get('message', '자동화 규칙이 실행되었습니다') if action_params else None
            priority = action_params.get('priority', 'medium') if action_params else None

            notification = create_notification(
                'system_alert',
                title,
                message,
                user_id,
                priority,
                {'automation': True, 'context': context}
            )

            return {
                'type': 'notification',
                'status': 'success',
                'notification_id': notification['id'] if notification is not None else None
            }

        elif action_type == 'update_inventory':
            # 재고 업데이트
            item_id = action_params.get('item_id') if action_params else None
            quantity_change = action_params.get('quantity_change', 0) if action_params else None

            # 실제로는 데이터베이스 업데이트
            return {
                'type': 'inventory_update',
                'status': 'success',
                'item_id': item_id,
                'quantity_change': quantity_change
            }

        elif action_type == 'create_order':
            # 주문 생성
            customer_name = action_params.get('customer_name', '자동 주문') if action_params else None
            items = action_params.get('items', []) if action_params else None

            # 실제로는 데이터베이스에 주문 생성
            return {
                'type': 'order_creation',
                'status': 'success',
                'customer_name': customer_name,
                'items': items
            }

        elif action_type == 'update_schedule':
            # 스케줄 업데이트
            user_id = action_params.get('user_id') if action_params else None
            schedule_data = action_params.get('schedule_data', {}) if action_params else None

            # 실제로는 데이터베이스 업데이트
            return {
                'type': 'schedule_update',
                'status': 'success',
                'user_id': user_id,
                'schedule_data': schedule_data
            }

        elif action_type == 'send_email':
            # 이메일 전송
            recipient = action_params.get('recipient') if action_params else None
            subject = action_params.get('subject', '자동화 알림') if action_params else None
            body = action_params.get('body', '자동화 규칙이 실행되었습니다') if action_params else None

            # 실제로는 이메일 전송 로직
            return {
                'type': 'email',
                'status': 'success',
                'recipient': recipient,
                'subject': subject
            }

        else:
            return {
                'type': action_type,
                'status': 'unknown_action',
                'error': f'알 수 없는 액션 타입: {action_type}'
            }

    except Exception as e:
        return {
            'type': action_type,
            'status': 'error',
            'error': str(e)
        }

# 자동화 규칙 조회


@automation.route('/rules', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_automation_rules(current_user):
    """자동화 규칙 조회"""
    try:
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'

        rules = _automation_rules.copy()

        if enabled_only:
            rules = [rule for rule in rules if rule['enabled']]

        return jsonify({
            'rules': rules,
            'total': len(rules)
        }), 200

    except Exception as e:
        current_app.logger.error(f"자동화 규칙 조회 오류: {str(e)}")
        return jsonify({'message': '자동화 규칙 조회 중 오류가 발생했습니다'}), 500

# 자동화 규칙 생성


@automation.route('/rules', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def create_automation_rule_api(current_user):
    """자동화 규칙 생성"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['name', 'trigger_type', 'actions']
        for field in required_fields if required_fields is not None:
            if not data.get(field):
                return jsonify({'message': f'{field} 필드는 필수입니다'}), 400

        rule = create_automation_rule(
            name=data['name'],
            description=data.get('description', ''),
            trigger_type=data['trigger_type'],
            trigger_conditions=data.get('trigger_conditions', []),
            actions=data['actions'],
            enabled=data.get('enabled', True),
            priority=data.get('priority', 'medium')
        )

        return jsonify({
            'message': '자동화 규칙이 생성되었습니다',
            'rule': rule
        }), 201

    except Exception as e:
        current_app.logger.error(f"자동화 규칙 생성 오류: {str(e)}")
        return jsonify({'message': '자동화 규칙 생성 중 오류가 발생했습니다'}), 500

# 자동화 규칙 업데이트


@automation.route('/rules/<int:rule_id>', methods=['PUT'])
@token_required
@role_required(['admin', 'super_admin'])
def update_automation_rule(current_user,  rule_id):
    """자동화 규칙 업데이트"""
    try:
        data = request.get_json()
        rule = next((r for r in _automation_rules if r['id'] == rule_id), None)

        if not rule:
            return jsonify({'message': '자동화 규칙을 찾을 수 없습니다'}), 404

        # 규칙 업데이트
        for key, value in data.items():
            if key in ['name', 'description', 'trigger_type', 'trigger_conditions', 'actions', 'enabled', 'priority']:
                rule[key] = value

        return jsonify({
            'message': '자동화 규칙이 업데이트되었습니다',
            'rule': rule
        }), 200

    except Exception as e:
        current_app.logger.error(f"자동화 규칙 업데이트 오류: {str(e)}")
        return jsonify({'message': '자동화 규칙 업데이트 중 오류가 발생했습니다'}), 500

# 자동화 규칙 삭제


@automation.route('/rules/<int:rule_id>', methods=['DELETE'])
@token_required
@role_required(['admin', 'super_admin'])
def delete_automation_rule(current_user,  rule_id):
    """자동화 규칙 삭제"""
    try:
        rule = next((r for r in _automation_rules if r['id'] == rule_id), None)

        if not rule:
            return jsonify({'message': '자동화 규칙을 찾을 수 없습니다'}), 404

        _automation_rules.remove(rule)

        return jsonify({'message': '자동화 규칙이 삭제되었습니다'}), 200

    except Exception as e:
        current_app.logger.error(f"자동화 규칙 삭제 오류: {str(e)}")
        return jsonify({'message': '자동화 규칙 삭제 중 오류가 발생했습니다'}), 500

# 자동화 규칙 실행


@automation.route('/rules/<int:rule_id>/execute', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def execute_automation_rule_api(current_user,  rule_id):
    """자동화 규칙 수동 실행"""
    try:
        data = request.get_json() or {}
        context = data.get('context', {})

        rule = next((r for r in _automation_rules if r['id'] == rule_id), None)

        if not rule:
            return jsonify({'message': '자동화 규칙을 찾을 수 없습니다'}), 404

        if not rule['enabled']:
            return jsonify({'message': '비활성화된 규칙입니다'}), 400

        success, result = execute_automation_rule(rule,  context)

        if success:
            return jsonify({
                'message': '자동화 규칙이 성공적으로 실행되었습니다',
                'result': result
            }), 200
        else:
            return jsonify({
                'message': '자동화 규칙 실행에 실패했습니다',
                'error': result
            }), 400

    except Exception as e:
        current_app.logger.error(f"자동화 규칙 실행 오류: {str(e)}")
        return jsonify({'message': '자동화 규칙 실행 중 오류가 발생했습니다'}), 500

# 자동화 작업 로그 조회


@automation.route('/jobs', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_automation_jobs(current_user):
    """자동화 작업 로그 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        rule_id = request.args.get('rule_id', type=int)

        jobs = _automation_jobs.copy()

        # 필터링
        if status:
            jobs = [job for job in jobs if job['status'] == status]

        if rule_id:
            jobs = [job for job in jobs if job['rule_id'] == rule_id]

        # 최신순 정렬
        jobs.sort(key=lambda x: x['executed_at'], reverse=True)

        # 페이지네이션
        total = len(jobs)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_jobs = jobs[start_idx:end_idx]

        return jsonify({
            'jobs': paginated_jobs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"자동화 작업 로그 조회 오류: {str(e)}")
        return jsonify({'message': '자동화 작업 로그 조회 중 오류가 발생했습니다'}), 500

# 자동화 통계


@automation.route('/stats', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_automation_stats(current_user):
    """자동화 통계 조회"""
    try:
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # 오늘 실행된 작업
        today_jobs = [
            job for job in _automation_jobs
            if today_start <= datetime.fromisoformat(job['executed_at']) <= today_end
        ]

        # 상태별 통계
        status_stats = {}
        for job in today_jobs:
            status = job['status']
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1

        # 규칙별 통계
        rule_stats = {}
        for job in today_jobs:
            rule_name = job['rule_name']
            if rule_name not in rule_stats:
                rule_stats[rule_name] = 0
            rule_stats[rule_name] += 1

        return jsonify({
            'today_total': len(today_jobs),
            'today_success': status_stats.get('success', 0),
            'today_failed': status_stats.get('failed', 0),
            'status_stats': status_stats,
            'rule_stats': rule_stats,
            'total_rules': len(_automation_rules),
            'enabled_rules': len([r for r in _automation_rules if r['enabled']]),
            'total_jobs': len(_automation_jobs)
        }), 200

    except Exception as e:
        current_app.logger.error(f"자동화 통계 조회 오류: {str(e)}")
        return jsonify({'message': '자동화 통계 조회 중 오류가 발생했습니다'}), 500

# === 운영 자동화 정책/규칙 관리 API (초보자용 설명) ===


@automation.route('/policy', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def list_policies(current_user):
    """
    모든 자동화 정책/규칙 목록 조회
    """
    return jsonify({'policies': _automation_rules})


@automation.route('/policy', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def create_policy(current_user):
    """
    새로운 자동화 정책/규칙 생성
    """
    data = request.get_json()
    rule = create_automation_rule(
        name=data['name'],
        description=data.get('description', ''),
        trigger_type=data['trigger_type'],
        trigger_conditions=data.get('trigger_conditions', []),
        actions=data['actions'],
        enabled=data.get('enabled', True),
        priority=data.get('priority', 'medium')
    )
    return jsonify({'policy': rule}), 201


@automation.route('/policy/<int:rule_id>', methods=['PUT'])
@token_required
@role_required(['admin', 'super_admin'])
def update_policy(current_user,  rule_id):
    """
    자동화 정책/규칙 수정
    """
    data = request.get_json()
    rule = next((r for r in _automation_rules if r['id'] == rule_id), None)
    if not rule:
        return jsonify({'message': '정책/규칙을 찾을 수 없습니다.'}), 404
    for key, value in data.items():
        if key in ['name', 'description', 'trigger_type', 'trigger_conditions', 'actions', 'enabled', 'priority']:
            rule[key] = value
    return jsonify({'policy': rule})


@automation.route('/policy/<int:rule_id>', methods=['DELETE'])
@token_required
@role_required(['admin', 'super_admin'])
def delete_policy(current_user,  rule_id):
    """
    자동화 정책/규칙 삭제
    """
    global _automation_rules
    _automation_rules = [r for r in _automation_rules if r['id'] != rule_id]
    return jsonify({'message': '정책/규칙이 삭제되었습니다.'})

# === 예시 정책 추가 (초기화 시) ===


def initialize_example_policies():
    if not _automation_rules or not any(r['name'] == '지각 자동 경고' for r in _automation_rules):
        create_automation_rule(
            name='지각 자동 경고',
            description='직원 지각 시 자동 경고 알림',
            trigger_type='attendance_late',
            trigger_conditions=[{'type': 'data_based', 'field': 'clock_in', 'operator': 'greater_than', 'value': '09:15'}],
            actions=[{'type': 'send_notification', 'params': {'title': '지각 경고', 'message': '지각이 감지되었습니다.', 'priority': 'warning'}}],
            enabled=True,
            priority='medium'
        )
    if not any(r['name'] == '재고 부족 자동 발주' for r in _automation_rules):
        create_automation_rule(
            name='재고 부족 자동 발주',
            description='재고 부족 시 자동 발주 요청',
            trigger_type='inventory_low',
            trigger_conditions=[{'type': 'data_based', 'field': 'quantity', 'operator': 'less_than', 'value': 10}],
            actions=[{'type': 'create_order', 'params': {'customer_name': '자동 발주', 'items': []}}],
            enabled=True,
            priority='high'
        )


initialize_example_policies()

# 기본 자동화 규칙 초기화


def initialize_default_rules():
    """기본 자동화 규칙 초기화"""
    if not _automation_rules:
        # 재고 부족 알림 규칙
        create_automation_rule(
            name="재고 부족 알림",
            description="재고가 부족할 때 관리자에게 알림",
            trigger_type="inventory_low",
            trigger_conditions=[
                {
                    "type": "data_based",
                    "field": "quantity",
                    "operator": "less_than",
                    "value": 10
                }
            ],
            actions=[
                {
                    "type": "send_notification",
                    "params": {
                        "title": "재고 부족 알림",
                        "message": "재고가 부족합니다. 발주를 확인해주세요.",
                        "priority": "high"
                    }
                }
            ],
            enabled=True,
            priority="high"
        )

        # 영업 시간 시작 알림
        create_automation_rule(
            name="영업 시작 알림",
            description="영업 시간 시작 시 직원들에게 알림",
            trigger_type="time_based",
            trigger_conditions=[
                {
                    "type": "time_based",
                    "value": "business_hours"
                }
            ],
            actions=[
                {
                    "type": "send_notification",
                    "params": {
                        "title": "영업 시작",
                        "message": "영업이 시작되었습니다. 준비를 완료해주세요.",
                        "priority": "medium"
                    }
                }
            ],
            enabled=True,
            priority="medium"
        )

        # 시스템 성능 알림
        create_automation_rule(
            name="시스템 성능 알림",
            description="시스템 성능이 저하될 때 알림",
            trigger_type="performance_alert",
            trigger_conditions=[
                {
                    "type": "data_based",
                    "field": "cpu_usage",
                    "operator": "greater_than",
                    "value": 80
                }
            ],
            actions=[
                {
                    "type": "send_notification",
                    "params": {
                        "title": "시스템 성능 경고",
                        "message": "시스템 성능이 저하되고 있습니다.",
                        "priority": "high"
                    }
                }
            ],
            enabled=True,
            priority="high"
        )


# 앱 시작 시 기본 규칙 초기화
initialize_default_rules()
