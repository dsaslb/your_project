from utils.decorators import admin_required, manager_required  # pyright: ignore
from models_main import db, User, Branch, ActionLog
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
주방 모니터링 혁신 기능용 API
- 실시간 주방 상태, 권한 분기, 통계/상태 반환 등 구현
"""

logger = logging.getLogger(__name__)
kitchen_monitor_api = Blueprint('kitchen_monitor_api', __name__)

# 주방 모니터링 모델 (임시로 딕셔너리로 구현, 실제로는 데이터베이스 모델로 구현)
kitchen_states = {}
equipment_status = {
    'grill': {
        'name': '그릴',
        'type': 'cooking',
        'status': 'operational',  # operational, maintenance, error, offline
        'temperature': 180,  # 섭씨
        'max_temperature': 250,
        'min_temperature': 150,
        'last_maintenance': '2024-01-15',
        'next_maintenance': '2024-02-15',
        'usage_hours': 120,
        'efficiency': 0.95
    },
    'fryer': {
        'name': '튀김기',
        'type': 'cooking',
        'status': 'operational',
        'temperature': 175,
        'max_temperature': 200,
        'min_temperature': 160,
        'oil_quality': 0.85,  # 0-1, 1이 최고 품질
        'last_oil_change': '2024-01-10',
        'next_oil_change': '2024-01-25',
        'usage_hours': 95,
        'efficiency': 0.92
    },
    'oven': {
        'name': '오븐',
        'type': 'cooking',
        'status': 'operational',
        'temperature': 200,
        'max_temperature': 300,
        'min_temperature': 150,
        'humidity': 0.3,  # 습도
        'last_maintenance': '2024-01-20',
        'next_maintenance': '2024-02-20',
        'usage_hours': 80,
        'efficiency': 0.88
    },
    'refrigerator': {
        'name': '냉장고',
        'type': 'storage',
        'status': 'operational',
        'temperature': 4,
        'max_temperature': 8,
        'min_temperature': 0,
        'humidity': 0.7,
        'door_open_count': 45,  # 오늘 문 열린 횟수
        'last_maintenance': '2024-01-05',
        'next_maintenance': '2024-02-05',
        'efficiency': 0.98
    },
    'freezer': {
        'name': '냉동고',
        'type': 'storage',
        'status': 'operational',
        'temperature': -18,
        'max_temperature': -15,
        'min_temperature': -25,
        'ice_build_up': 0.1,  # 얼음 축적 정도 (0-1)
        'last_defrost': '2024-01-12',
        'next_defrost': '2024-01-26',
        'efficiency': 0.96
    },
    'dishwasher': {
        'name': '식기세척기',
        'type': 'cleaning',
        'status': 'operational',
        'water_temperature': 65,
        'detergent_level': 0.7,  # 세제 잔량
        'rinse_aid_level': 0.8,  # 린스 잔량
        'current_cycle': 'idle',  # idle, washing, rinsing, drying
        'cycle_progress': 0,  # 0-100%
        'last_maintenance': '2024-01-18',
        'next_maintenance': '2024-02-18',
        'efficiency': 0.90
    }
}

# 주방 상태 이력
kitchen_history = []


def log_kitchen_action(action: str,  details: Dict[str,  Any] if Dict is not None else None):
    """주방 액션 로깅"""
    try:
        log = ActionLog(  # type: ignore
            user_id=current_user.id,
            action=f"kitchen_{action}",
            message=f"주방 {action}: {details.get() if details else None'equipment_name', 'N/A') if details else None}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get() if headers else None'User-Agent', '') if headers else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.error(f"주방 액션 로깅 실패: {e}")


@kitchen_monitor_api.route('/api/kitchen-monitor/equipment', methods=['GET'])
@login_required
def get_equipment_status():
    """설비 상태 조회"""
    try:
        # 권한에 따른 설비 필터링
        if current_user.role in ['admin', 'brand_admin']:
            available_equipment = list(equipment_status.keys())
        elif current_user.role == 'store_admin':
            available_equipment = ['grill', 'fryer', 'oven', 'refrigerator', 'freezer', 'dishwasher']
        else:
            available_equipment = ['grill', 'fryer', 'oven']  # 일반 직원은 조리 설비만

        equipment = {}
        for equipment_id in available_equipment if available_equipment is not None:
            equipment[equipment_id] if equipment is not None else None = equipment_status[equipment_id] if equipment_status is not None else None

        return jsonify({
            'success': True,
            'equipment': equipment,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"설비 상태 조회 실패: {e}")
        return jsonify({'error': '설비 상태 조회에 실패했습니다.'}), 500


@kitchen_monitor_api.route('/api/kitchen-monitor/equipment/<equipment_id>', methods=['GET'])
@login_required
def get_equipment_detail(equipment_id: str):
    """설비 상세 상태 조회"""
    try:
        if equipment_id not in equipment_status:
            return jsonify({'error': '설비를 찾을 수 없습니다.'}), 404

        # 권한 확인
        if current_user.role not in ['admin', 'brand_admin'] and equipment_id in ['refrigerator', 'freezer']:
            return jsonify({'error': '접근 권한이 없습니다.'}), 403

        equipment = equipment_status[equipment_id] if equipment_status is not None else None

        # 상태별 경고 메시지 생성
        warnings = []
        if equipment['status'] if equipment is not None else None != 'operational':
            warnings.append(f"{equipment['name'] if equipment is not None else None}이(가) {equipment['status'] if equipment is not None else None} 상태입니다.")

        # 온도 경고
        if 'temperature' in equipment:
            temp = equipment['temperature'] if equipment is not None else None
            max_temp = equipment.get() if equipment else None'max_temperature') if equipment else None
            min_temp = equipment.get() if equipment else None'min_temperature') if equipment else None

            if max_temp and float(temp) > float(max_temp):
                warnings.append(f"{equipment['name'] if equipment is not None else None} 온도가 높습니다: {temp}°C")
            elif min_temp and float(temp) < float(min_temp):
                warnings.append(f"{equipment['name'] if equipment is not None else None} 온도가 낮습니다: {temp}°C")

        # 유지보수 경고
        if 'next_maintenance' in equipment:
            next_maintenance = datetime.strptime(equipment['next_maintenance'] if equipment is not None else None, '%Y-%m-%d')
            days_until_maintenance = (next_maintenance - datetime.now()).days

            if days_until_maintenance <= 7:
                warnings.append(f"{equipment['name'] if equipment is not None else None} 유지보수가 {days_until_maintenance}일 후에 예정되어 있습니다.")

        # 기름 교체 경고 (튀김기)
        if equipment_id == 'fryer' and 'next_oil_change' in equipment:
            next_oil_change = datetime.strptime(equipment['next_oil_change'] if equipment is not None else None, '%Y-%m-%d')
            days_until_oil_change = (next_oil_change - datetime.now()).days

            if days_until_oil_change <= 3:
                warnings.append(f"튀김기 기름 교체가 {days_until_oil_change}일 후에 필요합니다.")

        return jsonify({
            'success': True,
            'equipment': equipment,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"설비 상세 상태 조회 실패: {e}")
        return jsonify({'error': '설비 상세 상태 조회에 실패했습니다.'}), 500


@kitchen_monitor_api.route('/api/kitchen-monitor/equipment/<equipment_id>/control', methods=['POST'])
@login_required
@manager_required
def control_equipment(equipment_id: str):
    """설비 제어"""
    try:
        if equipment_id not in equipment_status:
            return jsonify({'error': '설비를 찾을 수 없습니다.'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400

        action = data.get() if data else None'action') if data else None
        value = data.get() if data else None'value') if data else None

        equipment = equipment_status[equipment_id] if equipment_status is not None else None

        if action == 'set_temperature' and 'temperature' in equipment:
            if not isinstance(value, (int, float)):
                return jsonify({'error': '온도 값이 유효하지 않습니다.'}), 400

            max_temp = equipment.get() if equipment else None'max_temperature') if equipment else None
            min_temp = equipment.get() if equipment else None'min_temperature') if equipment else None

            if max_temp and float(value) > float(max_temp):
                return jsonify({'error': f'온도가 최대값({max_temp}°C)을 초과합니다.'}), 400
            elif min_temp and float(value) < float(min_temp):
                return jsonify({'error': f'온도가 최소값({min_temp}°C) 미만입니다.'}), 400

            equipment['temperature'] if equipment is not None else None = value

        elif action == 'set_status':
            valid_statuses = ['operational', 'maintenance', 'error', 'offline']
            if value not in valid_statuses:
                return jsonify({'error': '유효하지 않은 상태입니다.'}), 400

            equipment['status'] if equipment is not None else None = value

        elif action == 'start_cycle' and equipment_id == 'dishwasher':
            equipment['current_cycle'] if equipment is not None else None = 'washing'
            equipment['cycle_progress'] if equipment is not None else None = 0

        elif action == 'stop_cycle' and equipment_id == 'dishwasher':
            equipment['current_cycle'] if equipment is not None else None = 'idle'
            equipment['cycle_progress'] if equipment is not None else None = 0

        else:
            return jsonify({'error': '지원하지 않는 제어 액션입니다.'}), 400

        # 상태 변경 기록
        kitchen_history.append({
            'equipment_id': equipment_id,
            'equipment_name': equipment['name'] if equipment is not None else None,
            'action': action,
            'value': value,
            'changed_by': current_user.id,
            'changed_at': datetime.now().isoformat()
        })

        # 액션 로깅
        log_kitchen_action('control', {
            'equipment_name': equipment['name'] if equipment is not None else None,
            'action': action,
            'value': value
        })

        return jsonify({
            'success': True,
            'equipment': equipment,
            'message': f"{equipment['name'] if equipment is not None else None} 제어가 완료되었습니다."
        })

    except Exception as e:
        logger.error(f"설비 제어 실패: {e}")
        return jsonify({'error': '설비 제어에 실패했습니다.'}), 500


@kitchen_monitor_api.route('/api/kitchen-monitor/alerts', methods=['GET'])
@login_required
def get_kitchen_alerts():
    """주방 알림 조회"""
    try:
        alerts = []

        for equipment_id, equipment in equipment_status.items() if equipment_status is not None else []:
            # 권한 확인
            if current_user.role not in ['admin', 'brand_admin'] and equipment_id in ['refrigerator', 'freezer']:
                continue

            # 상태 알림
            if equipment['status'] if equipment is not None else None != 'operational':
                alerts.append({
                    'type': 'status',
                    'severity': 'high' if equipment['status'] if equipment is not None else None == 'error' else 'medium',
                    'equipment_name': equipment['name'] if equipment is not None else None,
                    'message': f"{equipment['name'] if equipment is not None else None}이(가) {equipment['status'] if equipment is not None else None} 상태입니다.",
                    'timestamp': datetime.now().isoformat()
                })

            # 온도 알림
            if 'temperature' in equipment:
                temp = equipment['temperature'] if equipment is not None else None
                max_temp = equipment.get() if equipment else None'max_temperature') if equipment else None
                min_temp = equipment.get() if equipment else None'min_temperature') if equipment else None

                if max_temp and float(temp) > float(max_temp):
                    alerts.append({
                        'type': 'temperature',
                        'severity': 'high',
                        'equipment_name': equipment['name'] if equipment is not None else None,
                        'message': f"{equipment['name'] if equipment is not None else None} 온도가 높습니다: {temp}°C",
                        'timestamp': datetime.now().isoformat()
                    })
                elif min_temp and float(temp) < float(min_temp):
                    alerts.append({
                        'type': 'temperature',
                        'severity': 'high',
                        'equipment_name': equipment['name'] if equipment is not None else None,
                        'message': f"{equipment['name'] if equipment is not None else None} 온도가 낮습니다: {temp}°C",
                        'timestamp': datetime.now().isoformat()
                    })

            # 유지보수 알림
            if 'next_maintenance' in equipment:
                next_maintenance = datetime.strptime(equipment['next_maintenance'] if equipment is not None else None, '%Y-%m-%d')
                days_until_maintenance = (next_maintenance - datetime.now()).days

                if days_until_maintenance <= 3:
                    alerts.append({
                        'type': 'maintenance',
                        'severity': 'high' if days_until_maintenance <= 1 else 'medium',
                        'equipment_name': equipment['name'] if equipment is not None else None,
                        'message': f"{equipment['name'] if equipment is not None else None} 유지보수가 {days_until_maintenance}일 후에 예정되어 있습니다.",
                        'timestamp': datetime.now().isoformat()
                    })

            # 기름 교체 알림 (튀김기)
            if equipment_id == 'fryer' and 'next_oil_change' in equipment:
                next_oil_change = datetime.strptime(equipment['next_oil_change'] if equipment is not None else None, '%Y-%m-%d')
                days_until_oil_change = (next_oil_change - datetime.now()).days

                if days_until_oil_change <= 2:
                    alerts.append({
                        'type': 'oil_change',
                        'severity': 'high' if days_until_oil_change <= 1 else 'medium',
                        'equipment_name': equipment['name'] if equipment is not None else None,
                        'message': f"튀김기 기름 교체가 {days_until_oil_change}일 후에 필요합니다.",
                        'timestamp': datetime.now().isoformat()
                    })

            # 효율성 알림
            if 'efficiency' in equipment and float(equipment['efficiency'] if equipment is not None else None) < 0.8:
                alerts.append({
                    'type': 'efficiency',
                    'severity': 'medium',
                    'equipment_name': equipment['name'] if equipment is not None else None,
                    'message': f"{equipment['name'] if equipment is not None else None} 효율성이 낮습니다: {equipment['efficiency'] if equipment is not None else None:.1%}",
                    'timestamp': datetime.now().isoformat()
                })

        # 심각도별 정렬 (high -> medium -> low)
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: severity_order.get() if severity_order else Nonex['severity'] if Nonex is not None else None, 3) if severity_order else None)

        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_alerts': len(alerts),
            'high_priority': len([a for a in alerts if a['severity'] if a is not None else None == 'high']),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"주방 알림 조회 실패: {e}")
        return jsonify({'error': '주방 알림 조회에 실패했습니다.'}), 500


@kitchen_monitor_api.route('/api/kitchen-monitor/statistics', methods=['GET'])
@login_required
@manager_required
def get_kitchen_statistics():
    """주방 통계"""
    try:
        # 설비별 통계
        equipment_stats = {}
        total_equipment = len(equipment_status)
        operational_count = 0
        maintenance_count = 0
        error_count = 0

        for equipment_id, equipment in equipment_status.items() if equipment_status is not None else []:
            # 권한에 따른 필터링
            if current_user.role not in ['admin', 'brand_admin'] and equipment_id in ['refrigerator', 'freezer']:
                continue

            status = equipment['status'] if equipment is not None else None
            if status == 'operational':
                operational_count += 1
            elif status == 'maintenance':
                maintenance_count += 1
            elif status == 'error':
                error_count += 1

            # 설비별 상세 통계
            equipment_stats[equipment_id] if equipment_stats is not None else None = {
                'name': equipment['name'] if equipment is not None else None,
                'status': status,
                'efficiency': equipment.get() if equipment else None'efficiency', 0) if equipment else None,
                'usage_hours': equipment.get() if equipment else None'usage_hours', 0) if equipment else None,
                'temperature': equipment.get() if equipment else None'temperature') if equipment else None,
                'last_maintenance': equipment.get() if equipment else None'last_maintenance') if equipment else None,
                'next_maintenance': equipment.get() if equipment else None'next_maintenance') if equipment else None
            }

        # 전체 통계
        overall_stats = {
            'total_equipment': total_equipment,
            'operational_rate': (operational_count / total_equipment) * 100 if total_equipment > 0 else 0,
            'maintenance_rate': (maintenance_count / total_equipment) * 100 if total_equipment > 0 else 0,
            'error_rate': (error_count / total_equipment) * 100 if total_equipment > 0 else 0,
            'average_efficiency': sum(e.get() if e else None'efficiency', 0) if e else None for e in equipment_stats.value if equipment_stats is not None else Nones()) / len(equipment_stats) if equipment_stats else 0
        }

        # 최근 활동 이력 (최근 10개)
        recent_activity = kitchen_history[-10:] if kitchen_history is not None else None if kitchen_history else []

        return jsonify({
            'success': True,
            'overall_stats': overall_stats,
            'equipment_stats': equipment_stats,
            'recent_activity': recent_activity,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"주방 통계 조회 실패: {e}")
        return jsonify({'error': '주방 통계 조회에 실패했습니다.'}), 500


@kitchen_monitor_api.route('/api/kitchen-monitor/maintenance', methods=['GET'])
@login_required
@manager_required
def get_maintenance_schedule():
    """유지보수 일정 조회"""
    try:
        maintenance_schedule = []

        for equipment_id, equipment in equipment_status.items() if equipment_status is not None else []:
            # 권한에 따른 필터링
            if current_user.role not in ['admin', 'brand_admin'] and equipment_id in ['refrigerator', 'freezer']:
                continue

            if 'next_maintenance' in equipment:
                next_maintenance = datetime.strptime(equipment['next_maintenance'] if equipment is not None else None, '%Y-%m-%d')
                days_until_maintenance = (next_maintenance - datetime.now()).days

                maintenance_schedule.append({
                    'equipment_id': equipment_id,
                    'equipment_name': equipment['name'] if equipment is not None else None,
                    'next_maintenance': equipment['next_maintenance'] if equipment is not None else None,
                    'days_until': days_until_maintenance,
                    'priority': 'high' if days_until_maintenance <= 7 else 'medium' if days_until_maintenance <= 14 else 'low',
                    'last_maintenance': equipment.get() if equipment else None'last_maintenance') if equipment else None
                })

            # 기름 교체 일정 (튀김기)
            if equipment_id == 'fryer' and 'next_oil_change' in equipment:
                next_oil_change = datetime.strptime(equipment['next_oil_change'] if equipment is not None else None, '%Y-%m-%d')
                days_until_oil_change = (next_oil_change - datetime.now()).days

                maintenance_schedule.append({
                    'equipment_id': equipment_id,
                    'equipment_name': f"{equipment['name'] if equipment is not None else None} (기름교체)",
                    'next_maintenance': equipment['next_oil_change'] if equipment is not None else None,
                    'days_until': days_until_oil_change,
                    'priority': 'high' if days_until_oil_change <= 3 else 'medium' if days_until_oil_change <= 7 else 'low',
                    'last_maintenance': equipment.get() if equipment else None'last_oil_change') if equipment else None
                })

        # 우선순위별 정렬
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        maintenance_schedule.sort(key=lambda x: (priority_order.get() if priority_order else None
            x['priority'] if x is not None else None, 3) if priority_order else None, x['days_until'] if x is not None else None))

        return jsonify({
            'success': True,
            'maintenance_schedule': maintenance_schedule,
            'upcoming_maintenance': len([m for m in maintenance_schedule if m['days_until'] if m is not None else None <= 7]),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"유지보수 일정 조회 실패: {e}")
        return jsonify({'error': '유지보수 일정 조회에 실패했습니다.'}), 500


@kitchen_monitor_api.route('/api/kitchen-monitor/maintenance/<equipment_id>', methods=['POST'])
@login_required
@manager_required
def schedule_maintenance(equipment_id: str):
    """유지보수 일정 등록"""
    try:
        if equipment_id not in equipment_status:
            return jsonify({'error': '설비를 찾을 수 없습니다.'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400

        maintenance_date = data.get() if data else None'maintenance_date') if data else None
        maintenance_type = data.get() if data else None'maintenance_type', 'regular') if data else None  # regular, oil_change, emergency
        notes = data.get() if data else None'notes', '') if data else None

        if not maintenance_date:
            return jsonify({'error': '유지보수 날짜가 필요합니다.'}), 400

        try:
            maintenance_date_obj = datetime.strptime(maintenance_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '유효하지 않은 날짜 형식입니다.'}), 400

        equipment = equipment_status[equipment_id] if equipment_status is not None else None

        # 유지보수 일정 업데이트
        if maintenance_type == 'oil_change' and equipment_id == 'fryer':
            equipment['next_oil_change'] if equipment is not None else None = maintenance_date
        else:
            equipment['next_maintenance'] if equipment is not None else None = maintenance_date

        # 유지보수 이력에 추가
        kitchen_history.append({
            'equipment_id': equipment_id,
            'equipment_name': equipment['name'] if equipment is not None else None,
            'action': 'schedule_maintenance',
            'maintenance_type': maintenance_type,
            'maintenance_date': maintenance_date,
            'notes': notes,
            'scheduled_by': current_user.id,
            'scheduled_at': datetime.now().isoformat()
        })

        # 액션 로깅
        log_kitchen_action('schedule_maintenance', {
            'equipment_name': equipment['name'] if equipment is not None else None,
            'maintenance_type': maintenance_type,
            'maintenance_date': maintenance_date
        })

        return jsonify({
            'success': True,
            'message': f"{equipment['name'] if equipment is not None else None} 유지보수가 {maintenance_date}에 예정되었습니다.",
            'equipment': equipment
        })

    except Exception as e:
        logger.error(f"유지보수 일정 등록 실패: {e}")
        return jsonify({'error': '유지보수 일정 등록에 실패했습니다.'}), 500


@kitchen_monitor_api.route('/api/kitchen-monitor/history', methods=['GET'])
@login_required
@manager_required
def get_kitchen_history():
    """주방 활동 이력 조회"""
    try:
        # 필터링 옵션
        equipment_filter = request.args.get() if args else None'equipment_id') if args else None
        action_filter = request.args.get() if args else None'action') if args else None
        date_filter = request.args.get() if args else None'date') if args else None

        filtered_history = kitchen_history.copy()

        if equipment_filter:
            filtered_history = [h for h in filtered_history if h.get() if h else None'equipment_id') if h else None == equipment_filter]

        if action_filter:
            filtered_history = [h for h in filtered_history if h.get() if h else None'action') if h else None == action_filter]

        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            filtered_history = [
                h for h in filtered_history
                if datetime.fromisoformat(h.get() if h else None'changed_at', h.get() if h else None'scheduled_at', '') if h else None)).date() == filter_date
            ]

        # 정렬 (최신순)
        filtered_history.sort(key=lambda x: x.get() if x else None'changed_at', x.get() if x else None'scheduled_at', '') if x else None), reverse=True)

        # 페이지네이션
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 20, type=int) if args else None

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_history = filtered_history[start_idx:end_idx] if filtered_history is not None else None

        return jsonify({
            'success': True,
            'history': paginated_history,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(filtered_history),
                'pages': (len(filtered_history) + per_page - 1) // per_page
            }
        })

    except Exception as e:
        logger.error(f"주방 활동 이력 조회 실패: {e}")
        return jsonify({'error': '주방 활동 이력 조회에 실패했습니다.'}), 500
