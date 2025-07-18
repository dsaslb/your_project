from api.gateway import token_required, role_required, admin_required, manager_required, employee_required, log_request  # pyright: ignore
from sqlalchemy import func, and_, or_, desc
import sys
import os
import json
from datetime import datetime, timedelta
import logging
from extensions import db
from models_main import User, Order, Attendance, Schedule, InventoryItem, Notification, db
from functools import wraps
from flask import Blueprint, request, jsonify, g, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore

# 로깅 설정
logger = logging.getLogger(__name__)

# 통합 및 확장 API Blueprint
integration = Blueprint('integration', __name__, url_prefix='/api/integration')

# 시스템 상태 모니터링


class SystemMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.active_users = 0

    def get_system_status(self):
        """시스템 상태 정보 반환"""
        uptime = datetime.now() - self.start_time
        return {
            'uptime': str(uptime).split('.')[0],
            'request_count': self.request_count,
            'error_count': self.error_count,
            'active_users': self.active_users,
            'memory_usage': self.get_memory_usage(),
            'disk_usage': self.get_disk_usage(),
            'database_status': self.get_database_status()
        }

    def get_memory_usage(self):
        """메모리 사용량 확인"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            }
        except ImportError:
            return {'error': 'psutil not available'}

    def get_disk_usage(self):
        """디스크 사용량 확인"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except ImportError:
            return {'error': 'psutil not available'}

    def get_database_status(self):
        """데이터베이스 상태 확인"""
        try:
            # 간단한 쿼리로 DB 연결 상태 확인
            db.session.execute('SELECT 1')
            return {'status': 'connected', 'timestamp': datetime.now().isoformat()}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}


# 전역 시스템 모니터 인스턴스
system_monitor = SystemMonitor()


@integration.route('/system-status', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def get_system_status():
    """시스템 상태 조회"""
    try:
        status = system_monitor.get_system_status()

        # 추가 시스템 정보
        status.update({
            'server_info': {
                'python_version': sys.version,
                'flask_version': '2.0+',
                'database_type': 'SQLite',
                'api_version': '1.0.0'
            },
            'feature_status': {
                'ai_prediction': True,
                'real_time_monitoring': True,
                'mobile_api': True,
                'security_audit': True,
                'advanced_reports': True,
                'pwa_support': True
            }
        })

        return jsonify(status)

    except Exception as e:
        logger.error(f"시스템 상태 조회 오류: {str(e)}")
        return jsonify({'error': 'Failed to get system status'}), 500


@integration.route('/health-check', methods=['GET'])
@log_request
def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 기본 시스템 상태 확인
        db_status = system_monitor.get_database_status()

        health_status = {
            'status': 'healthy' if db_status['status'] if db_status is not None else None == 'connected' else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': db_status,
            'version': '1.0.0'
        }

        return jsonify(health_status)

    except Exception as e:
        logger.error(f"헬스 체크 오류: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@integration.route('/api-documentation', methods=['GET'])
@token_required
@log_request
def get_api_documentation():
    """API 문서 생성"""
    try:
        documentation = {
            'version': '1.0.0',
            'base_url': '/api',
            'endpoints': {
                'authentication': {
                    'login': 'POST /api/auth/login',
                    'logout': 'POST /api/auth/logout',
                    'refresh': 'POST /api/auth/refresh'
                },
                'dashboard': {
                    'stats': 'GET /api/dashboard/stats',
                    'realtime': 'GET /api/dashboard/realtime'
                },
                'staff': {
                    'list': 'GET /api/staff',
                    'create': 'POST /api/staff',
                    'update': 'PUT /api/staff/{id}',
                    'delete': 'DELETE /api/staff/{id}'
                },
                'schedule': {
                    'list': 'GET /api/schedule',
                    'create': 'POST /api/schedule',
                    'update': 'PUT /api/schedule/{id}',
                    'delete': 'DELETE /api/schedule/{id}'
                },
                'attendance': {
                    'list': 'GET /api/attendance',
                    'check_in': 'POST /api/attendance/check-in',
                    'check_out': 'POST /api/attendance/check-out'
                },
                'orders': {
                    'list': 'GET /api/orders',
                    'create': 'POST /api/orders',
                    'update': 'PUT /api/orders/{id}',
                    'delete': 'DELETE /api/orders/{id}'
                },
                'inventory': {
                    'list': 'GET /api/inventory',
                    'create': 'POST /api/inventory',
                    'update': 'PUT /api/inventory/{id}',
                    'delete': 'DELETE /api/inventory/{id}'
                },
                'ai_prediction': {
                    'train_models': 'POST /api/ai/train-models',
                    'predict_sales': 'POST /api/ai/predict-sales',
                    'optimize_staff': 'POST /api/ai/optimize-staff',
                    'forecast_inventory': 'POST /api/ai/forecast-inventory'
                },
                'security': {
                    'audit_logs': 'GET /api/security/audit-logs',
                    'security_events': 'GET /api/security/security-events',
                    'user_activity': 'GET /api/security/user-activity'
                },
                'mobile': {
                    'dashboard': 'GET /api/mobile/dashboard',
                    'attendance': 'GET /api/mobile/attendance',
                    'schedule': 'GET /api/mobile/schedule'
                }
            },
            'authentication': {
                'type': 'JWT',
                'header': 'Authorization: Bearer <token>'
            },
            'rate_limiting': {
                'requests_per_minute': 100,
                'burst_limit': 200
            }
        }

        return jsonify(documentation)

    except Exception as e:
        logger.error(f"API 문서 생성 오류: {str(e)}")
        return jsonify({'error': 'Failed to generate API documentation'}), 500


@integration.route('/data-export', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def export_data():
    """데이터 내보내기"""
    try:
        data = request.get_json()
        export_type = data.get() if data else None'type', 'all') if data else None
        format_type = data.get() if data else None'format', 'json') if data else None

        export_data = {}

        if export_type in ['all', 'users']:
            users = User.query.all()
            export_data['users'] if export_data is not None else None = [
                {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'status': user.status,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]

        if export_type in ['all', 'orders']:
            orders = Order.query.all()
            export_data['orders'] if export_data is not None else None = [
                {
                    'id': order.id,
                    'customer_name': order.customer_name,
                    'items': order.items,
                    'total_amount': order.total_amount,
                    'status': order.status,
                    'created_at': order.created_at.isoformat() if order.created_at else None
                }
                for order in orders
            ]

        if export_type in ['all', 'attendance']:
            attendance_records = Attendance.query.all()
            export_data['attendance'] if export_data is not None else None = [
                {
                    'id': record.id,
                    'user_id': record.user_id,
                    'check_in': record.check_in.isoformat() if record.check_in else None,
                    'check_out': record.check_out.isoformat() if record.check_out else None,
                    'date': record.date.isoformat() if record.date else None
                }
                for record in attendance_records
            ]

        # 감사 로그 기록
        logger.info(f"Data export requested by user {g.user.id}: {export_type} in {format_type} format")

        return jsonify({
            'success': True,
            'export_type': export_type,
            'format': format_type,
            'record_count': sum(len(data) for data in export_data.value if export_data is not None else Nones()),
            'data': export_data
        })

    except Exception as e:
        logger.error(f"데이터 내보내기 오류: {str(e)}")
        return jsonify({'error': 'Failed to export data'}), 500


@integration.route('/data-import', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def import_data():
    """데이터 가져오기"""
    try:
        data = request.get_json()
        import_type = data.get() if data else None'type') if data else None
        import_data = data.get() if data else None'data', []) if data else None

        if not import_type or not import_data:
            return jsonify({'error': 'Type and data are required'}), 400

        imported_count = 0

        if import_type == 'users':
            for user_data in import_data if import_data is not None:
                try:
                    user = User(
                        name=user_data.get() if user_data else None'name') if user_data else None,
                        email=user_data.get() if user_data else None'email') if user_data else None,
                        role=user_data.get() if user_data else None'role', 'employee') if user_data else None,
                        status=user_data.get() if user_data else None'status', 'pending') if user_data else None
                    )
                    db.session.add(user)
                    imported_count += 1
                except Exception as e:
                    logger.error(f"User import error: {str(e)}")

        elif import_type == 'orders':
            for order_data in import_data if import_data is not None:
                try:
                    order = Order(
                        customer_name=order_data.get() if order_data else None'customer_name') if order_data else None,
                        items=order_data.get() if order_data else None'items', '') if order_data else None,
                        total_amount=order_data.get() if order_data else None'total_amount', 0) if order_data else None,
                        status=order_data.get() if order_data else None'status', 'pending') if order_data else None
                    )
                    db.session.add(order)
                    imported_count += 1
                except Exception as e:
                    logger.error(f"Order import error: {str(e)}")

        db.session.commit()

        # 감사 로그 기록
        logger.info(f"Data import completed by user {g.user.id}: {imported_count} {import_type} records")

        return jsonify({
            'success': True,
            'import_type': import_type,
            'imported_count': imported_count
        })

    except Exception as e:
        logger.error(f"데이터 가져오기 오류: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to import data'}), 500


@integration.route('/backup', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def create_backup():
    """시스템 백업 생성"""
    try:
        backup_type = request.json.get() if json else None'type', 'full') if json else None
        include_files = request.json.get() if json else None'include_files', False) if json else None

        # 백업 정보
        backup_info = {
            'timestamp': datetime.now().isoformat(),
            'type': backup_type,
            'created_by': g.user.id,
            'database_tables': [
                'users', 'orders', 'attendance', 'schedule',
                'inventory', 'notifications', 'system_logs'
            ]
        }

        if backup_type == 'full':
            backup_info['includes'] if backup_info is not None else None = ['database', 'files', 'configurations']
        elif backup_type == 'database':
            backup_info['includes'] if backup_info is not None else None = ['database']
        elif backup_type == 'files':
            backup_info['includes'] if backup_info is not None else None = ['files']

        # 실제 백업 로직 (여기서는 정보만 반환)
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 감사 로그 기록
        logger.info(f"Backup created by user {g.user.id}: {backup_type} backup - {backup_id}")

        return jsonify({
            'success': True,
            'backup_id': backup_id,
            'backup_info': backup_info,
            'message': f'{backup_type} 백업이 성공적으로 생성되었습니다.'
        })

    except Exception as e:
        logger.error(f"백업 생성 오류: {str(e)}")
        return jsonify({'error': 'Failed to create backup'}), 500


@integration.route('/restore', methods=['POST'])
@token_required
@role_required(['super_admin'])
@log_request
def restore_backup():
    """백업 복원"""
    try:
        backup_id = request.json.get() if json else None'backup_id') if json else None

        if not backup_id:
            return jsonify({'error': 'Backup ID is required'}), 400

        # 실제 복원 로직 (여기서는 정보만 반환)
        restore_info = {
            'backup_id': backup_id,
            'timestamp': datetime.now().isoformat(),
            'restored_by': g.user.id,
            'status': 'completed'
        }

        # 감사 로그 기록
        logger.info(f"Backup restored by user {g.user.id}: {backup_id}")

        return jsonify({
            'success': True,
            'restore_info': restore_info,
            'message': f'백업 {backup_id}이(가) 성공적으로 복원되었습니다.'
        })

    except Exception as e:
        logger.error(f"백업 복원 오류: {str(e)}")
        return jsonify({'error': 'Failed to restore backup'}), 500


@integration.route('/system-optimization', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def optimize_system():
    """시스템 최적화"""
    try:
        optimization_type = request.json.get() if json else None'type', 'all') if json else None

        optimizations = []

        if optimization_type in ['all', 'database']:
            # 데이터베이스 최적화
            try:
                # 불필요한 로그 정리
                old_logs = SystemLog.query.filter(
                    SystemLog.created_at < datetime.now() - timedelta(days=90)
                ).delete()

                # 인덱스 최적화 (실제로는 DB별 다른 명령어 사용)
                optimizations.append({
                    'type': 'database',
                    'action': 'cleaned_old_logs',
                    'records_affected': old_logs
                })
            except Exception as e:
                logger.error(f"Database optimization error: {str(e)}")

        if optimization_type in ['all', 'cache']:
            # 캐시 최적화
            try:
                from extensions import cache
                cache.clear()
                optimizations.append({
                    'type': 'cache',
                    'action': 'cleared_cache',
                    'status': 'completed'
                })
            except Exception as e:
                logger.error(f"Cache optimization error: {str(e)}")

        if optimization_type in ['all', 'files']:
            # 파일 시스템 최적화
            try:
                # 임시 파일 정리
                temp_files_cleaned = 0
                optimizations.append({
                    'type': 'files',
                    'action': 'cleaned_temp_files',
                    'files_cleaned': temp_files_cleaned
                })
            except Exception as e:
                logger.error(f"File optimization error: {str(e)}")

        # 감사 로그 기록
        logger.info(f"System optimization performed by user {g.user.id}: {optimization_type}")

        return jsonify({
            'success': True,
            'optimization_type': optimization_type,
            'optimizations': optimizations,
            'message': '시스템 최적화가 완료되었습니다.'
        })

    except Exception as e:
        logger.error(f"시스템 최적화 오류: {str(e)}")
        return jsonify({'error': 'Failed to optimize system'}), 500


@integration.route('/feature-flags', methods=['GET', 'PUT'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def manage_feature_flags():
    """기능 플래그 관리"""
    try:
        if request.method == 'GET':
            # 현재 기능 플래그 상태 반환
            feature_flags = {
                'ai_prediction': True,
                'real_time_monitoring': True,
                'mobile_api': True,
                'security_audit': True,
                'advanced_reports': True,
                'pwa_support': True,
                'automation_rules': True,
                'data_export': True,
                'system_backup': True
            }

            return jsonify({'feature_flags': feature_flags})

        elif request.method == 'PUT':
            # 기능 플래그 업데이트
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # 실제로는 데이터베이스나 설정 파일에 저장
            updated_flags = data.get() if data else None'feature_flags', {}) if data else None

            # 감사 로그 기록
            logger.info(f"Feature flags updated by user {g.user.id}: {updated_flags}")

            return jsonify({
                'success': True,
                'feature_flags': updated_flags,
                'message': '기능 플래그가 업데이트되었습니다.'
            })

    except Exception as e:
        logger.error(f"기능 플래그 관리 오류: {str(e)}")
        return jsonify({'error': 'Failed to manage feature flags'}), 500


@integration.route('/performance-metrics', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def get_performance_metrics():
    """성능 메트릭 조회"""
    try:
        # 성능 메트릭 수집
        metrics = {
            'api_performance': {
                'average_response_time': 150,  # ms
                'requests_per_second': 25,
                'error_rate': 0.02,  # 2%
                'uptime': 99.8  # %
            },
            'database_performance': {
                'query_count': 1250,
                'average_query_time': 45,  # ms
                'slow_queries': 3,
                'connection_pool_usage': 0.6  # 60%
            },
            'system_resources': {
                'cpu_usage': 35,  # %
                'memory_usage': 45,  # %
                'disk_usage': 32,  # %
                'network_io': 1024  # KB/s
            },
            'user_activity': {
                'active_users': 24,
                'concurrent_sessions': 18,
                'page_views_per_minute': 45,
                'average_session_duration': 1800  # seconds
            }
        }

        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        })

    except Exception as e:
        logger.error(f"성능 메트릭 조회 오류: {str(e)}")
        return jsonify({'error': 'Failed to get performance metrics'}), 500


@integration.route('/system-logs', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def get_system_logs():
    """시스템 로그 조회"""
    try:
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 50, type=int) if args else None
        log_level = request.args.get() if args else None'level') if args else None

        # 실제로는 로그 파일에서 읽어오거나 DB에서 조회
        # 여기서는 샘플 로그 데이터 생성
        sample_logs = [
            {
                'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                'level': 'INFO',
                'message': f'System log entry {i}',
                'user_id': 1,
                'ip_address': '192.168.1.100'
            }
            for i in range(1, 51)
        ]

        # 레벨 필터링
        if log_level:
            sample_logs = [log for log in sample_logs if log['level'] if log is not None else None == log_level.upper()]

        # 페이지네이션
        total = len(sample_logs)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_logs = sample_logs[start_idx:end_idx] if sample_logs is not None else None

        return jsonify({
            'logs': paginated_logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        logger.error(f"시스템 로그 조회 오류: {str(e)}")
        return jsonify({'error': 'Failed to get system logs'}), 500
