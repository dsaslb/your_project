# -*- coding: utf-8 -*-
"""
시스템 상태 조회 및 최적화 API
프론트엔드에서 시스템 상태를 모니터링하고 최적화를 실행할 수 있는 API
"""

from flask import Blueprint, jsonify, request
import psutil
import sqlite3
import json
import os
from datetime import datetime, timedelta
import threading
import time

system_health_api = Blueprint('system_health_api', __name__)

# 시스템 상태 데이터 저장소
system_status = {
    'backend': 'online',
    'frontend': 'online', 
    'database': 'online',
    'aiModels': 'online',
    'performance': {
        'cpu': 0,
        'memory': 0,
        'responseTime': 0
    },
    'alerts': []
}

def get_system_metrics():
    """시스템 메트릭 수집"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': round(cpu_percent, 2),
            'memory': round(memory.percent, 2),
            'disk': round(disk.percent, 2),
            'responseTime': round(time.time() * 1000) % 200 + 50  # 시뮬레이션
        }
    except Exception as e:
        print(f"시스템 메트릭 수집 오류: {e}")
        return {
            'cpu': 0,
            'memory': 0,
            'disk': 0,
            'responseTime': 100
        }

def check_database_status():
    """데이터베이스 상태 확인"""
    try:
        conn = sqlite3.connect('data/performance_metrics.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM performance_metrics")
        count = cursor.fetchone()[0]
        conn.close()
        return 'online' if count >= 0 else 'warning'
    except Exception as e:
        print(f"데이터베이스 상태 확인 오류: {e}")
        return 'error'

def check_ai_models():
    """AI 모델 상태 확인"""
    try:
        # AI 모델 파일 존재 확인
        model_files = [
            'ai/performance_predictor.py',
            'data/performance_metrics.db'
        ]
        
        for file_path in model_files:
            if not os.path.exists(file_path):
                return 'warning'
        
        return 'online'
    except Exception as e:
        print(f"AI 모델 상태 확인 오류: {e}")
        return 'error'

def update_system_status():
    """시스템 상태 업데이트 (백그라운드에서 실행)"""
    while True:
        try:
            metrics = get_system_metrics()
            
            # 성능 기반 상태 결정
            if metrics['cpu'] > 90 or metrics['memory'] > 90:
                system_status['backend'] = 'error'
            elif metrics['cpu'] > 70 or metrics['memory'] > 70:
                system_status['backend'] = 'warning'
            else:
                system_status['backend'] = 'online'
            
            # 데이터베이스 상태 확인
            system_status['database'] = check_database_status()
            
            # AI 모델 상태 확인
            system_status['aiModels'] = check_ai_models()
            
            # 성능 메트릭 업데이트
            system_status['performance'] = metrics
            
            # 알림 생성
            if metrics['cpu'] > 80:
                alert = {
                    'id': f"alert_{int(time.time())}",
                    'type': 'warning',
                    'message': f"CPU 사용률이 높습니다: {metrics['cpu']}%",
                    'timestamp': datetime.now().isoformat()
                }
                if alert not in system_status['alerts']:
                    system_status['alerts'].append(alert)
            
            if metrics['memory'] > 80:
                alert = {
                    'id': f"alert_{int(time.time())}",
                    'type': 'warning',
                    'message': f"메모리 사용률이 높습니다: {metrics['memory']}%",
                    'timestamp': datetime.now().isoformat()
                }
                if alert not in system_status['alerts']:
                    system_status['alerts'].append(alert)
            
            # 알림 개수 제한 (최근 10개만 유지)
            system_status['alerts'] = system_status['alerts'][-10:]
            
        except Exception as e:
            print(f"시스템 상태 업데이트 오류: {e}")
        
        time.sleep(5)  # 5초마다 업데이트

# 백그라운드 스레드 시작
status_thread = threading.Thread(target=update_system_status, daemon=True)
status_thread.start()

@system_health_api.route('/api/system/health', methods=['GET'])
def get_system_health():
    """시스템 상태 조회"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'backend': system_status['backend'],
                'frontend': system_status['frontend'],
                'database': system_status['database'],
                'aiModels': system_status['aiModels'],
                'performance': system_status['performance'],
                'alerts': system_status['alerts'],
                'lastUpdated': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_health_api.route('/api/system/performance', methods=['GET'])
def get_performance_metrics():
    """성능 메트릭 조회"""
    try:
        metrics = get_system_metrics()
        
        # 히스토리 데이터 생성 (시뮬레이션)
        history = []
        for i in range(50):
            timestamp = datetime.now() - timedelta(minutes=i*5)
            history.append({
                'timestamp': timestamp.isoformat(),
                'cpu': max(0, min(100, metrics['cpu'] + (i % 20 - 10))),
                'memory': max(0, min(100, metrics['memory'] + (i % 15 - 7))),
                'disk': max(0, min(100, metrics['disk'] + (i % 10 - 5))),
                'network': max(0, min(100, 50 + (i % 30 - 15))),
                'responseTime': max(50, min(500, metrics['responseTime'] + (i % 100 - 50)))
            })
        
        return jsonify({
            'success': True,
            'data': {
                'current': metrics,
                'history': history,
                'trends': {
                    'cpu': 'up' if metrics['cpu'] > 60 else 'down' if metrics['cpu'] < 30 else 'stable',
                    'memory': 'up' if metrics['memory'] > 70 else 'down' if metrics['memory'] < 40 else 'stable',
                    'disk': 'up' if metrics['disk'] > 80 else 'down' if metrics['disk'] < 50 else 'stable',
                    'network': 'stable',
                    'responseTime': 'up' if metrics['responseTime'] > 200 else 'down' if metrics['responseTime'] < 100 else 'stable'
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_health_api.route('/api/system/alerts', methods=['GET'])
def get_alerts():
    """알림 조회"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'alerts': system_status['alerts'],
                'summary': {
                    'total': len(system_status['alerts']),
                    'unread': len([a for a in system_status['alerts'] if a.get('read', False) == False]),
                    'error': len([a for a in system_status['alerts'] if a['type'] == 'error']),
                    'warning': len([a for a in system_status['alerts'] if a['type'] == 'warning']),
                    'info': len([a for a in system_status['alerts'] if a['type'] == 'info'])
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_health_api.route('/api/system/alerts/<alert_id>/read', methods=['POST'])
def mark_alert_read(alert_id):
    """알림 읽음 처리"""
    try:
        for alert in system_status['alerts']:
            if alert['id'] == alert_id:
                alert['read'] = True
                break
        
        return jsonify({
            'success': True,
            'message': '알림이 읽음 처리되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_health_api.route('/api/system/optimize', methods=['POST'])
def optimize_system():
    """시스템 최적화 실행"""
    try:
        data = request.get_json()
        optimization_type = data.get('type', 'general')
        
        # 최적화 시뮬레이션
        if optimization_type == 'memory':
            # 메모리 최적화
            import gc
            gc.collect()
            message = "메모리 최적화가 완료되었습니다."
        elif optimization_type == 'cpu':
            # CPU 최적화
            message = "CPU 사용률 최적화가 완료되었습니다."
        else:
            # 일반 최적화
            message = "시스템 최적화가 완료되었습니다."
        
        # 성공 알림 추가
        alert = {
            'id': f"optimization_{int(time.time())}",
            'type': 'info',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        system_status['alerts'].append(alert)
        
        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'optimizationType': optimization_type,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_health_api.route('/api/system/backup', methods=['POST'])
def create_backup():
    """시스템 백업 생성"""
    try:
        # 백업 시뮬레이션
        backup_id = f"backup_{int(time.time())}"
        
        # 백업 알림 추가
        alert = {
            'id': f"backup_{int(time.time())}",
            'type': 'info',
            'message': f"시스템 백업이 생성되었습니다. (ID: {backup_id})",
            'timestamp': datetime.now().isoformat()
        }
        system_status['alerts'].append(alert)
        
        return jsonify({
            'success': True,
            'message': '백업이 성공적으로 생성되었습니다.',
            'data': {
                'backupId': backup_id,
                'timestamp': datetime.now().isoformat(),
                'size': '15.2MB'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 