"""
IoT API 엔드포인트
IoT 기기 데이터 수집, 관리, 분석을 위한 API
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Any, Optional

from utils.iot_simulator import get_iot_manager, DeviceType, DeviceStatus
from utils.auth_decorators import role_required

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
iot_bp = Blueprint('iot', __name__)

@iot_bp.route('/api/iot/devices', methods=['GET'])
@login_required
def get_devices():
    """모든 IoT 기기 상태 조회"""
    try:
        iot_manager = get_iot_manager()
        devices = iot_manager.get_all_devices_status()
        
        return jsonify({
            'success': True,
            'data': devices,
            'count': len(devices),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"IoT 기기 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': '기기 조회 중 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

@iot_bp.route('/api/iot/devices/<device_id>', methods=['GET'])
@login_required
def get_device_status(device_id):
    """특정 IoT 기기 상태 조회"""
    try:
        iot_manager = get_iot_manager()
        device_status = iot_manager.get_device_status(device_id)
        
        if not device_status:
            return jsonify({
                'success': False,
                'error': '기기를 찾을 수 없습니다.',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        return jsonify({
            'success': True,
            'data': device_status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"IoT 기기 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': '기기 상태 조회 중 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

@iot_bp.route('/api/iot/devices/<device_id>/data', methods=['GET'])
@login_required
def get_device_data(device_id):
    """특정 IoT 기기 데이터 조회"""
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 1000)  # 최대 1000개로 제한
        
        iot_manager = get_iot_manager()
        device_data = iot_manager.get_device_data(device_id, limit)
        
        return jsonify({
            'success': True,
            'data': device_data,
            'count': len(device_data),
            'device_id': device_id,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"IoT 기기 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': '기기 데이터 조회 중 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

@iot_bp.route('/api/iot/data/latest', methods=['GET'])
@login_required
def get_latest_data():
    """모든 기기의 최신 데이터 조회"""
    try:
        iot_manager = get_iot_manager()
        latest_data = iot_manager.get_latest_data()
        
        return jsonify({
            'success': True,
            'data': latest_data,
            'count': len(latest_data),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"최신 IoT 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': '최신 데이터 조회 중 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

@iot_bp.route('/api/iot/data/analytics', methods=['GET'])
@role_required(['admin', 'manager'])
def get_iot_analytics():
    """IoT 데이터 분석"""
    try:
        iot_manager = get_iot_manager()
        latest_data = iot_manager.get_latest_data()
        
        # 데이터 타입별 분석
        analytics = {
            'temperature': {
                'devices': [],
                'average': 0,
                'min': 0,
                'max': 0
            },
            'humidity': {
                'devices': [],
                'average': 0,
                'min': 0,
                'max': 0
            },
            'weight': {
                'devices': [],
                'total': 0,
                'low_stock': []
            },
            'motion': {
                'active_areas': [],
                'total_active': 0
            },
            'lighting': {
                'devices': [],
                'total_power': 0
            }
        }
        
        temp_values = []
        humidity_values = []
        weight_total = 0
        motion_active = 0
        lighting_power = 0
        
        for data in latest_data:
            device_type = data.get('device_type', '')
            
            if 'temperature' in device_type:
                temp_values.append(data.get('value', 0))
                analytics['temperature']['devices'].append({
                    'device_id': data.get('device_id'),
                    'value': data.get('value'),
                    'location': data.get('location')
                })
            
            elif 'humidity' in device_type:
                humidity_values.append(data.get('value', 0))
                analytics['humidity']['devices'].append({
                    'device_id': data.get('device_id'),
                    'value': data.get('value'),
                    'location': data.get('location')
                })
            
            elif 'weight' in device_type:
                weight_value = data.get('value', 0)
                weight_total += weight_value
                analytics['weight']['devices'].append({
                    'device_id': data.get('device_id'),
                    'value': weight_value,
                    'location': data.get('location'),
                    'remaining_percentage': data.get('metadata', {}).get('remaining_percentage', 0)
                })
                
                # 재고 부족 체크 (20% 미만)
                if data.get('metadata', {}).get('remaining_percentage', 100) < 20:
                    analytics['weight']['low_stock'].append({
                        'device_id': data.get('device_id'),
                        'location': data.get('location'),
                        'remaining_percentage': data.get('metadata', {}).get('remaining_percentage', 0)
                    })
            
            elif 'motion' in device_type:
                if data.get('value', 0) > 0:
                    motion_active += 1
                    analytics['motion']['active_areas'].append({
                        'device_id': data.get('device_id'),
                        'location': data.get('location')
                    })
            
            elif 'light' in device_type:
                power_consumption = data.get('metadata', {}).get('power_consumption', 0)
                lighting_power += power_consumption
                analytics['lighting']['devices'].append({
                    'device_id': data.get('device_id'),
                    'brightness': data.get('value'),
                    'power_consumption': power_consumption,
                    'location': data.get('location')
                })
        
        # 통계 계산
        if temp_values:
            analytics['temperature']['average'] = round(sum(temp_values) / len(temp_values), 1)
            analytics['temperature']['min'] = min(temp_values)
            analytics['temperature']['max'] = max(temp_values)
        
        if humidity_values:
            analytics['humidity']['average'] = round(sum(humidity_values) / len(humidity_values), 1)
            analytics['humidity']['min'] = min(humidity_values)
            analytics['humidity']['max'] = max(humidity_values)
        
        analytics['weight']['total'] = round(weight_total, 2)
        analytics['motion']['total_active'] = motion_active
        analytics['lighting']['total_power'] = round(lighting_power, 2)
        
        return jsonify({
            'success': True,
            'data': analytics,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"IoT 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': 'IoT 데이터 분석 중 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

@iot_bp.route('/api/iot/alerts', methods=['GET'])
@role_required(['admin', 'manager'])
def get_iot_alerts():
    """IoT 알림 조회"""
    try:
        iot_manager = get_iot_manager()
        latest_data = iot_manager.get_latest_data()
        
        alerts = []
        
        for data in latest_data:
            device_type = data.get('device_type', '')
            value = data.get('value', 0)
            location = data.get('location', '')
            device_id = data.get('device_id', '')
            
            # 온도 알림 (냉장고)
            if 'refrigerator' in device_type:
                if value > 8:  # 냉장고 온도가 너무 높음
                    alerts.append({
                        'type': 'temperature_high',
                        'severity': 'high',
                        'message': f'냉장고 온도가 높습니다: {value}°C',
                        'device_id': device_id,
                        'location': location,
                        'value': value,
                        'timestamp': data.get('timestamp')
                    })
                elif value < -2:  # 냉장고 온도가 너무 낮음
                    alerts.append({
                        'type': 'temperature_low',
                        'severity': 'medium',
                        'message': f'냉장고 온도가 낮습니다: {value}°C',
                        'device_id': device_id,
                        'location': location,
                        'value': value,
                        'timestamp': data.get('timestamp')
                    })
            
            # 습도 알림
            elif 'humidity' in device_type:
                if value > 70:  # 습도가 너무 높음
                    alerts.append({
                        'type': 'humidity_high',
                        'severity': 'medium',
                        'message': f'습도가 높습니다: {value}%',
                        'device_id': device_id,
                        'location': location,
                        'value': value,
                        'timestamp': data.get('timestamp')
                    })
                elif value < 30:  # 습도가 너무 낮음
                    alerts.append({
                        'type': 'humidity_low',
                        'severity': 'low',
                        'message': f'습도가 낮습니다: {value}%',
                        'device_id': device_id,
                        'location': location,
                        'value': value,
                        'timestamp': data.get('timestamp')
                    })
            
            # 재고 부족 알림
            elif 'weight' in device_type:
                remaining_percentage = data.get('metadata', {}).get('remaining_percentage', 100)
                if remaining_percentage < 10:  # 10% 미만
                    alerts.append({
                        'type': 'inventory_low',
                        'severity': 'high',
                        'message': f'재고가 부족합니다: {remaining_percentage}%',
                        'device_id': device_id,
                        'location': location,
                        'value': remaining_percentage,
                        'timestamp': data.get('timestamp')
                    })
                elif remaining_percentage < 20:  # 20% 미만
                    alerts.append({
                        'type': 'inventory_warning',
                        'severity': 'medium',
                        'message': f'재고가 부족할 수 있습니다: {remaining_percentage}%',
                        'device_id': device_id,
                        'location': location,
                        'value': remaining_percentage,
                        'timestamp': data.get('timestamp')
                    })
            
            # 기기 오류 알림
            if data.get('status') == 'error':
                alerts.append({
                    'type': 'device_error',
                    'severity': 'high',
                    'message': f'기기 오류: {device_id}',
                    'device_id': device_id,
                    'location': location,
                    'value': None,
                    'timestamp': data.get('timestamp')
                })
        
        # 심각도별 정렬 (high > medium > low)
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 0), reverse=True)
        
        return jsonify({
            'success': True,
            'data': alerts,
            'count': len(alerts),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"IoT 알림 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': 'IoT 알림 조회 중 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

@iot_bp.route('/api/iot/devices/<device_id>/control', methods=['POST'])
@role_required(['admin'])
def control_device(device_id):
    """IoT 기기 제어"""
    try:
        data = request.get_json()
        action = data.get('action')
        parameters = data.get('parameters', {})
        
        iot_manager = get_iot_manager()
        device = iot_manager.devices.get(device_id)
        
        if not device:
            return jsonify({
                'success': False,
                'error': '기기를 찾을 수 없습니다.',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # 기기 타입별 제어 로직
        if hasattr(device, 'control'):
            result = device.control(action, parameters)
            return jsonify({
                'success': True,
                'data': result,
                'message': f'기기 {device_id} 제어 완료',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '이 기기는 제어할 수 없습니다.',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        logger.error(f"IoT 기기 제어 오류: {e}")
        return jsonify({
            'success': False,
            'error': '기기 제어 중 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

@iot_bp.route('/api/iot/dashboard', methods=['GET'])
@login_required
def get_iot_dashboard():
    """IoT 대시보드 데이터"""
    try:
        iot_manager = get_iot_manager()
        latest_data = iot_manager.get_latest_data()
        
        # 대시보드 요약 데이터
        dashboard = {
            'total_devices': len(iot_manager.devices),
            'online_devices': 0,
            'error_devices': 0,
            'temperature_summary': {
                'average': 0,
                'min': 0,
                'max': 0
            },
            'humidity_summary': {
                'average': 0,
                'min': 0,
                'max': 0
            },
            'inventory_summary': {
                'total_weight': 0,
                'low_stock_count': 0
            },
            'active_areas': [],
            'recent_alerts': []
        }
        
        temp_values = []
        humidity_values = []
        total_weight = 0
        low_stock_count = 0
        
        for data in latest_data:
            # 온라인/오프라인 기기 카운트
            if data.get('status') == 'online':
                dashboard['online_devices'] += 1
            elif data.get('status') == 'error':
                dashboard['error_devices'] += 1
            
            device_type = data.get('device_type', '')
            value = data.get('value', 0)
            
            # 온도 데이터
            if 'temperature' in device_type:
                temp_values.append(value)
            
            # 습도 데이터
            elif 'humidity' in device_type:
                humidity_values.append(value)
            
            # 재고 데이터
            elif 'weight' in device_type:
                total_weight += value
                remaining_percentage = data.get('metadata', {}).get('remaining_percentage', 100)
                if remaining_percentage < 20:
                    low_stock_count += 1
            
            # 활성 영역
            elif 'motion' in device_type and value > 0:
                dashboard['active_areas'].append(data.get('location'))
        
        # 통계 계산
        if temp_values:
            dashboard['temperature_summary']['average'] = round(sum(temp_values) / len(temp_values), 1)
            dashboard['temperature_summary']['min'] = min(temp_values)
            dashboard['temperature_summary']['max'] = max(temp_values)
        
        if humidity_values:
            dashboard['humidity_summary']['average'] = round(sum(humidity_values) / len(humidity_values), 1)
            dashboard['humidity_summary']['min'] = min(humidity_values)
            dashboard['humidity_summary']['max'] = max(humidity_values)
        
        dashboard['inventory_summary']['total_weight'] = round(total_weight, 2)
        dashboard['inventory_summary']['low_stock_count'] = low_stock_count
        
        # 중복 제거
        dashboard['active_areas'] = list(set(dashboard['active_areas']))
        
        return jsonify({
            'success': True,
            'data': dashboard,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"IoT 대시보드 오류: {e}")
        return jsonify({
            'success': False,
            'error': 'IoT 대시보드 데이터 조회 중 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

# Blueprint 등록 함수
def init_iot_api(app):
    """IoT API 초기화"""
    app.register_blueprint(iot_bp)
    logger.info("IoT API 등록 완료") 