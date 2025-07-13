"""
주방 모니터링 혁신 기능용 API
- 실시간 주방 상태, 권한 분기, 통계/상태 반환 등 구현
"""
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from models import db, User, Branch, ActionLog
from utils.decorators import admin_required, manager_required

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

def log_kitchen_action(action: str, details: Dict[str, Any]):
    """주방 액션 로깅"""
    try:
        log = ActionLog(  # type: ignore
            user_id=current_user.id,
            action=f"kitchen_{action}",
            message=f"주방 {action}: {details.get('equipment_name', 'N/A')}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
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
        for equipment_id in available_equipment:
            equipment[equipment_id] = equipment_status[equipment_id]
        
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
        
        equipment = equipment_status[equipment_id]
        
        # 상태별 경고 메시지 생성
        warnings = []
        if equipment['status'] != 'operational':
            warnings.append(f"{equipment['name']}이(가) {equipment['status']} 상태입니다.")
        
        # 온도 경고
        if 'temperature' in equipment:
            temp = equipment['temperature']
            max_temp = equipment.get('max_temperature')
            min_temp = equipment.get('min_temperature')
            
            if max_temp and float(temp) > float(max_temp):
                warnings.append(f"{equipment['name']} 온도가 높습니다: {temp}°C")
            elif min_temp and float(temp) < float(min_temp):
                warnings.append(f"{equipment['name']} 온도가 낮습니다: {temp}°C")
        
        # 유지보수 경고
        if 'next_maintenance' in equipment:
            next_maintenance = datetime.strptime(equipment['next_maintenance'], '%Y-%m-%d')
            days_until_maintenance = (next_maintenance - datetime.now()).days
            
            if days_until_maintenance <= 7:
                warnings.append(f"{equipment['name']} 유지보수가 {days_until_maintenance}일 후에 예정되어 있습니다.")
        
        # 기름 교체 경고 (튀김기)
        if equipment_id == 'fryer' and 'next_oil_change' in equipment:
            next_oil_change = datetime.strptime(equipment['next_oil_change'], '%Y-%m-%d')
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
        
        action = data.get('action')
        value = data.get('value')
        
        equipment = equipment_status[equipment_id]
        
        if action == 'set_temperature' and 'temperature' in equipment:
            if not isinstance(value, (int, float)):
                return jsonify({'error': '온도 값이 유효하지 않습니다.'}), 400
            
            max_temp = equipment.get('max_temperature')
            min_temp = equipment.get('min_temperature')
            
            if max_temp and float(value) > float(max_temp):
                return jsonify({'error': f'온도가 최대값({max_temp}°C)을 초과합니다.'}), 400
            elif min_temp and float(value) < float(min_temp):
                return jsonify({'error': f'온도가 최소값({min_temp}°C) 미만입니다.'}), 400
            
            equipment['temperature'] = value
            
        elif action == 'set_status':
            valid_statuses = ['operational', 'maintenance', 'error', 'offline']
            if value not in valid_statuses:
                return jsonify({'error': '유효하지 않은 상태입니다.'}), 400
            
            equipment['status'] = value
            
        elif action == 'start_cycle' and equipment_id == 'dishwasher':
            equipment['current_cycle'] = 'washing'
            equipment['cycle_progress'] = 0
            
        elif action == 'stop_cycle' and equipment_id == 'dishwasher':
            equipment['current_cycle'] = 'idle'
            equipment['cycle_progress'] = 0
            
        else:
            return jsonify({'error': '지원하지 않는 제어 액션입니다.'}), 400
        
        # 상태 변경 기록
        kitchen_history.append({
            'equipment_id': equipment_id,
            'equipment_name': equipment['name'],
            'action': action,
            'value': value,
            'changed_by': current_user.id,
            'changed_at': datetime.now().isoformat()
        })
        
        # 액션 로깅
        log_kitchen_action('control', {
            'equipment_name': equipment['name'],
            'action': action,
            'value': value
        })
        
        return jsonify({
            'success': True,
            'equipment': equipment,
            'message': f"{equipment['name']} 제어가 완료되었습니다."
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
        
        for equipment_id, equipment in equipment_status.items():
            # 권한 확인
            if current_user.role not in ['admin', 'brand_admin'] and equipment_id in ['refrigerator', 'freezer']:
                continue
            
            # 상태 알림
            if equipment['status'] != 'operational':
                alerts.append({
                    'type': 'status',
                    'severity': 'high' if equipment['status'] == 'error' else 'medium',
                    'equipment_name': equipment['name'],
                    'message': f"{equipment['name']}이(가) {equipment['status']} 상태입니다.",
                    'timestamp': datetime.now().isoformat()
                })
            
            # 온도 알림
            if 'temperature' in equipment:
                temp = equipment['temperature']
                max_temp = equipment.get('max_temperature')
                min_temp = equipment.get('min_temperature')
                
                if max_temp and float(temp) > float(max_temp):
                    alerts.append({
                        'type': 'temperature',
                        'severity': 'high',
                        'equipment_name': equipment['name'],
                        'message': f"{equipment['name']} 온도가 높습니다: {temp}°C",
                        'timestamp': datetime.now().isoformat()
                    })
                elif min_temp and float(temp) < float(min_temp):
                    alerts.append({
                        'type': 'temperature',
                        'severity': 'high',
                        'equipment_name': equipment['name'],
                        'message': f"{equipment['name']} 온도가 낮습니다: {temp}°C",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # 유지보수 알림
            if 'next_maintenance' in equipment:
                next_maintenance = datetime.strptime(equipment['next_maintenance'], '%Y-%m-%d')
                days_until_maintenance = (next_maintenance - datetime.now()).days
                
                if days_until_maintenance <= 3:
                    alerts.append({
                        'type': 'maintenance',
                        'severity': 'high' if days_until_maintenance <= 1 else 'medium',
                        'equipment_name': equipment['name'],
                        'message': f"{equipment['name']} 유지보수가 {days_until_maintenance}일 후에 예정되어 있습니다.",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # 기름 교체 알림 (튀김기)
            if equipment_id == 'fryer' and 'next_oil_change' in equipment:
                next_oil_change = datetime.strptime(equipment['next_oil_change'], '%Y-%m-%d')
                days_until_oil_change = (next_oil_change - datetime.now()).days
                
                if days_until_oil_change <= 2:
                    alerts.append({
                        'type': 'oil_change',
                        'severity': 'high' if days_until_oil_change <= 1 else 'medium',
                        'equipment_name': equipment['name'],
                        'message': f"튀김기 기름 교체가 {days_until_oil_change}일 후에 필요합니다.",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # 효율성 알림
            if 'efficiency' in equipment and float(equipment['efficiency']) < 0.8:
                alerts.append({
                    'type': 'efficiency',
                    'severity': 'medium',
                    'equipment_name': equipment['name'],
                    'message': f"{equipment['name']} 효율성이 낮습니다: {equipment['efficiency']:.1%}",
                    'timestamp': datetime.now().isoformat()
                })
        
        # 심각도별 정렬 (high -> medium -> low)
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_alerts': len(alerts),
            'high_priority': len([a for a in alerts if a['severity'] == 'high']),
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
        
        for equipment_id, equipment in equipment_status.items():
            # 권한에 따른 필터링
            if current_user.role not in ['admin', 'brand_admin'] and equipment_id in ['refrigerator', 'freezer']:
                continue
            
            status = equipment['status']
            if status == 'operational':
                operational_count += 1
            elif status == 'maintenance':
                maintenance_count += 1
            elif status == 'error':
                error_count += 1
            
            # 설비별 상세 통계
            equipment_stats[equipment_id] = {
                'name': equipment['name'],
                'status': status,
                'efficiency': equipment.get('efficiency', 0),
                'usage_hours': equipment.get('usage_hours', 0),
                'temperature': equipment.get('temperature'),
                'last_maintenance': equipment.get('last_maintenance'),
                'next_maintenance': equipment.get('next_maintenance')
            }
        
        # 전체 통계
        overall_stats = {
            'total_equipment': total_equipment,
            'operational_rate': (operational_count / total_equipment) * 100 if total_equipment > 0 else 0,
            'maintenance_rate': (maintenance_count / total_equipment) * 100 if total_equipment > 0 else 0,
            'error_rate': (error_count / total_equipment) * 100 if total_equipment > 0 else 0,
            'average_efficiency': sum(e.get('efficiency', 0) for e in equipment_stats.values()) / len(equipment_stats) if equipment_stats else 0
        }
        
        # 최근 활동 이력 (최근 10개)
        recent_activity = kitchen_history[-10:] if kitchen_history else []
        
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
        
        for equipment_id, equipment in equipment_status.items():
            # 권한에 따른 필터링
            if current_user.role not in ['admin', 'brand_admin'] and equipment_id in ['refrigerator', 'freezer']:
                continue
            
            if 'next_maintenance' in equipment:
                next_maintenance = datetime.strptime(equipment['next_maintenance'], '%Y-%m-%d')
                days_until_maintenance = (next_maintenance - datetime.now()).days
                
                maintenance_schedule.append({
                    'equipment_id': equipment_id,
                    'equipment_name': equipment['name'],
                    'next_maintenance': equipment['next_maintenance'],
                    'days_until': days_until_maintenance,
                    'priority': 'high' if days_until_maintenance <= 7 else 'medium' if days_until_maintenance <= 14 else 'low',
                    'last_maintenance': equipment.get('last_maintenance')
                })
            
            # 기름 교체 일정 (튀김기)
            if equipment_id == 'fryer' and 'next_oil_change' in equipment:
                next_oil_change = datetime.strptime(equipment['next_oil_change'], '%Y-%m-%d')
                days_until_oil_change = (next_oil_change - datetime.now()).days
                
                maintenance_schedule.append({
                    'equipment_id': equipment_id,
                    'equipment_name': f"{equipment['name']} (기름교체)",
                    'next_maintenance': equipment['next_oil_change'],
                    'days_until': days_until_oil_change,
                    'priority': 'high' if days_until_oil_change <= 3 else 'medium' if days_until_oil_change <= 7 else 'low',
                    'last_maintenance': equipment.get('last_oil_change')
                })
        
        # 우선순위별 정렬
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        maintenance_schedule.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['days_until']))
        
        return jsonify({
            'success': True,
            'maintenance_schedule': maintenance_schedule,
            'upcoming_maintenance': len([m for m in maintenance_schedule if m['days_until'] <= 7]),
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
        
        maintenance_date = data.get('maintenance_date')
        maintenance_type = data.get('maintenance_type', 'regular')  # regular, oil_change, emergency
        notes = data.get('notes', '')
        
        if not maintenance_date:
            return jsonify({'error': '유지보수 날짜가 필요합니다.'}), 400
        
        try:
            maintenance_date_obj = datetime.strptime(maintenance_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '유효하지 않은 날짜 형식입니다.'}), 400
        
        equipment = equipment_status[equipment_id]
        
        # 유지보수 일정 업데이트
        if maintenance_type == 'oil_change' and equipment_id == 'fryer':
            equipment['next_oil_change'] = maintenance_date
        else:
            equipment['next_maintenance'] = maintenance_date
        
        # 유지보수 이력에 추가
        kitchen_history.append({
            'equipment_id': equipment_id,
            'equipment_name': equipment['name'],
            'action': 'schedule_maintenance',
            'maintenance_type': maintenance_type,
            'maintenance_date': maintenance_date,
            'notes': notes,
            'scheduled_by': current_user.id,
            'scheduled_at': datetime.now().isoformat()
        })
        
        # 액션 로깅
        log_kitchen_action('schedule_maintenance', {
            'equipment_name': equipment['name'],
            'maintenance_type': maintenance_type,
            'maintenance_date': maintenance_date
        })
        
        return jsonify({
            'success': True,
            'message': f"{equipment['name']} 유지보수가 {maintenance_date}에 예정되었습니다.",
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
        equipment_filter = request.args.get('equipment_id')
        action_filter = request.args.get('action')
        date_filter = request.args.get('date')
        
        filtered_history = kitchen_history.copy()
        
        if equipment_filter:
            filtered_history = [h for h in filtered_history if h.get('equipment_id') == equipment_filter]
        
        if action_filter:
            filtered_history = [h for h in filtered_history if h.get('action') == action_filter]
        
        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            filtered_history = [
                h for h in filtered_history 
                if datetime.fromisoformat(h.get('changed_at', h.get('scheduled_at', ''))).date() == filter_date
            ]
        
        # 정렬 (최신순)
        filtered_history.sort(key=lambda x: x.get('changed_at', x.get('scheduled_at', '')), reverse=True)
        
        # 페이지네이션
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_history = filtered_history[start_idx:end_idx]
        
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