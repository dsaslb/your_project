from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from models import db, User, Order, Schedule, Attendance
from api.gateway import token_required, role_required
from datetime import datetime, timedelta
import psutil
import os
import json
import traceback

monitoring = Blueprint('monitoring', __name__)

# 오류 로그 저장소 (실제 운영에서는 데이터베이스나 로그 파일 사용)
_error_logs = []
_performance_logs = []

def log_error(error_type, message, details=None, user_id=None):
    """오류 로그 기록"""
    error_log = {
        'timestamp': datetime.utcnow().isoformat(),
        'type': error_type,
        'message': message,
        'details': details,
        'user_id': user_id,
        'traceback': traceback.format_exc() if details else None
    }
    _error_logs.append(error_log)
    
    # 로그 개수 제한 (최근 1000개만 유지)
    if len(_error_logs) > 1000:
        _error_logs.pop(0)

def log_performance(operation, execution_time, user_id=None):
    """성능 로그 기록"""
    performance_log = {
        'timestamp': datetime.utcnow().isoformat(),
        'operation': operation,
        'execution_time': execution_time,
        'user_id': user_id
    }
    _performance_logs.append(performance_log)
    
    # 로그 개수 제한 (최근 1000개만 유지)
    if len(_performance_logs) > 1000:
        _performance_logs.pop(0)

# 시스템 상태 모니터링
@monitoring.route('/system/status', methods=['GET'])
@token_required
@role_required(['super_admin'])
def get_system_status(current_user):
    """시스템 상태 조회"""
    try:
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        # 네트워크 상태
        network = psutil.net_io_counters()
        
        # 데이터베이스 연결 상태
        db_status = "healthy"
        try:
            db.session.execute("SELECT 1")
        except Exception as e:
            db_status = "error"
            log_error("database_connection", str(e), user_id=current_user.id)
        
        # 애플리케이션 상태
        app_status = "running"
        
        return jsonify({
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'percent': memory_percent,
                    'used_gb': round(memory_used_gb, 2),
                    'total_gb': round(memory_total_gb, 2)
                },
                'disk': {
                    'percent': disk_percent,
                    'used_gb': round(disk_used_gb, 2),
                    'total_gb': round(disk_total_gb, 2)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                }
            },
            'services': {
                'database': db_status,
                'application': app_status
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        log_error("system_status", str(e), user_id=current_user.id)
        return jsonify({'message': '시스템 상태 조회 중 오류가 발생했습니다'}), 500

# 오류 로그 조회
@monitoring.route('/logs/errors', methods=['GET'])
@token_required
@role_required(['super_admin'])
def get_error_logs(current_user):
    """오류 로그 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        error_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 필터링
        filtered_logs = _error_logs.copy()
        
        if error_type:
            filtered_logs = [log for log in filtered_logs if log['type'] == error_type]
        
        if start_date:
            start_datetime = datetime.fromisoformat(start_date)
            filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log['timestamp']) >= start_datetime]
        
        if end_date:
            end_datetime = datetime.fromisoformat(end_date)
            filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log['timestamp']) <= end_datetime]
        
        # 최신순 정렬
        filtered_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 페이지네이션
        total = len(filtered_logs)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_logs = filtered_logs[start_idx:end_idx]
        
        return jsonify({
            'logs': paginated_logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        log_error("error_logs", str(e), user_id=current_user.id)
        return jsonify({'message': '오류 로그 조회 중 오류가 발생했습니다'}), 500

# 성능 로그 조회
@monitoring.route('/logs/performance', methods=['GET'])
@token_required
@role_required(['super_admin'])
def get_performance_logs(current_user):
    """성능 로그 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        operation = request.args.get('operation')
        min_time = request.args.get('min_time', type=float)
        
        # 필터링
        filtered_logs = _performance_logs.copy()
        
        if operation:
            filtered_logs = [log for log in filtered_logs if log['operation'] == operation]
        
        if min_time:
            filtered_logs = [log for log in filtered_logs if log['execution_time'] >= min_time]
        
        # 최신순 정렬
        filtered_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 페이지네이션
        total = len(filtered_logs)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_logs = filtered_logs[start_idx:end_idx]
        
        # 성능 통계
        if filtered_logs:
            execution_times = [log['execution_time'] for log in filtered_logs]
            performance_stats = {
                'avg_time': sum(execution_times) / len(execution_times),
                'max_time': max(execution_times),
                'min_time': min(execution_times),
                'total_operations': len(filtered_logs)
            }
        else:
            performance_stats = {
                'avg_time': 0,
                'max_time': 0,
                'min_time': 0,
                'total_operations': 0
            }
        
        return jsonify({
            'logs': paginated_logs,
            'stats': performance_stats,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        log_error("performance_logs", str(e), user_id=current_user.id)
        return jsonify({'message': '성능 로그 조회 중 오류가 발생했습니다'}), 500

# 실시간 알림 설정
@monitoring.route('/alerts/settings', methods=['GET', 'PUT'])
@token_required
@role_required(['super_admin'])
def alert_settings(current_user):
    """알림 설정 관리"""
    try:
        if request.method == 'GET':
            # 알림 설정 조회 (실제로는 데이터베이스에서 조회)
            settings = {
                'cpu_threshold': 80,
                'memory_threshold': 85,
                'disk_threshold': 90,
                'error_notification': True,
                'performance_notification': True,
                'email_notifications': True,
                'slack_notifications': False
            }
            
            return jsonify(settings), 200
            
        elif request.method == 'PUT':
            data = request.get_json()
            
            # 알림 설정 업데이트 (실제로는 데이터베이스에 저장)
            updated_settings = {
                'cpu_threshold': data.get('cpu_threshold', 80),
                'memory_threshold': data.get('memory_threshold', 85),
                'disk_threshold': data.get('disk_threshold', 90),
                'error_notification': data.get('error_notification', True),
                'performance_notification': data.get('performance_notification', True),
                'email_notifications': data.get('email_notifications', True),
                'slack_notifications': data.get('slack_notifications', False)
            }
            
            # 설정 변경 로그
            log_error("alert_settings_updated", "Alert settings updated", 
                     details=updated_settings, user_id=current_user.id)
            
            return jsonify({
                'message': '알림 설정이 업데이트되었습니다',
                'settings': updated_settings
            }), 200
            
    except Exception as e:
        log_error("alert_settings", str(e), user_id=current_user.id)
        return jsonify({'message': '알림 설정 처리 중 오류가 발생했습니다'}), 500

# 시스템 메트릭 수집
@monitoring.route('/metrics/collect', methods=['POST'])
@token_required
@role_required(['super_admin'])
def collect_metrics(current_user):
    """시스템 메트릭 수집"""
    try:
        # 데이터베이스 메트릭
        db_metrics = {
            'total_users': User.query.count(),
            'total_orders': Order.query.count(),
            'total_schedules': Schedule.query.count(),
            'total_attendance': Attendance.query.count(),
            'active_users': User.query.filter_by(is_active=True).count()
        }
        
        # 시스템 메트릭
        system_metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # 성능 메트릭 (최근 1시간)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_logs = [log for log in _performance_logs 
                      if datetime.fromisoformat(log['timestamp']) >= one_hour_ago]
        
        if recent_logs:
            execution_times = [log['execution_time'] for log in recent_logs]
            performance_metrics = {
                'avg_response_time': sum(execution_times) / len(execution_times),
                'max_response_time': max(execution_times),
                'total_requests': len(recent_logs)
            }
        else:
            performance_metrics = {
                'avg_response_time': 0,
                'max_response_time': 0,
                'total_requests': 0
            }
        
        # 오류 메트릭 (최근 1시간)
        recent_errors = [log for log in _error_logs 
                        if datetime.fromisoformat(log['timestamp']) >= one_hour_ago]
        
        error_metrics = {
            'total_errors': len(recent_errors),
            'error_types': {}
        }
        
        for error in recent_errors:
            error_type = error['type']
            error_metrics['error_types'][error_type] = error_metrics['error_types'].get(error_type, 0) + 1
        
        return jsonify({
            'database': db_metrics,
            'system': system_metrics,
            'performance': performance_metrics,
            'errors': error_metrics
        }), 200
        
    except Exception as e:
        log_error("metrics_collection", str(e), user_id=current_user.id)
        return jsonify({'message': '메트릭 수집 중 오류가 발생했습니다'}), 500

# 로그 정리
@monitoring.route('/logs/cleanup', methods=['POST'])
@token_required
@role_required(['super_admin'])
def cleanup_logs(current_user):
    """오래된 로그 정리"""
    try:
        days_to_keep = request.json.get('days_to_keep', 30)
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # 오류 로그 정리
        original_error_count = len(_error_logs)
        _error_logs[:] = [log for log in _error_logs 
                         if datetime.fromisoformat(log['timestamp']) >= cutoff_date]
        cleaned_error_count = original_error_count - len(_error_logs)
        
        # 성능 로그 정리
        original_performance_count = len(_performance_logs)
        _performance_logs[:] = [log for log in _performance_logs 
                               if datetime.fromisoformat(log['timestamp']) >= cutoff_date]
        cleaned_performance_count = original_performance_count - len(_performance_logs)
        
        log_error("logs_cleanup", f"Cleaned {cleaned_error_count} error logs and {cleaned_performance_count} performance logs",
                 user_id=current_user.id)
        
        return jsonify({
            'message': '로그 정리가 완료되었습니다',
            'cleaned_error_logs': cleaned_error_count,
            'cleaned_performance_logs': cleaned_performance_count,
            'remaining_error_logs': len(_error_logs),
            'remaining_performance_logs': len(_performance_logs)
        }), 200
        
    except Exception as e:
        log_error("logs_cleanup", str(e), user_id=current_user.id)
        return jsonify({'message': '로그 정리 중 오류가 발생했습니다'}), 500 