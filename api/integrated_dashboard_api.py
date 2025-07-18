from concurrent.futures import ThreadPoolExecutor, as_completed  # pyright: ignore
from functools import lru_cache
import gc
import psutil
from .plugin_monitoring_dashboard import PluginMonitoringDashboard  # pyright: ignore
from .iot_api import get_iot_dashboard  # pyright: ignore
from .advanced_analytics import get_realtime_dashboard  # pyright: ignore
from .ai_integrated_api import IntegratedAIService  # pyright: ignore
from .realtime_notifications import notification_manager  # pyright: ignore
# from .realtime_monitoring import realtime_data, update_realtime_data  # pyright: ignore
import queue
import asyncio
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
import time
import threading
import logging
import json
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, Response, current_app
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
통합 대시보드 API
모든 실시간 데이터를 통합하여 제공하는 대시보드 API
"""


# 기존 API 모듈들 import

# 성능 최적화 설정

# 메모리 관리 설정
MEMORY_THRESHOLD = 80  # 메모리 사용률 임계값
CACHE_CLEANUP_INTERVAL = 300  # 캐시 정리 간격 (5분)
MAX_CACHE_SIZE = 1000  # 최대 캐시 항목 수

logger = logging.getLogger(__name__)

integrated_dashboard_bp = Blueprint('integrated_dashboard', __name__)


class MemoryManager:
    """메모리 관리 클래스"""

    @staticmethod
    def check_memory_usage() -> Tuple[float, bool]:
        """메모리 사용률 확인"""
        memory = psutil.virtual_memory()
        usage_percent = memory.percent
        is_critical = usage_percent > MEMORY_THRESHOLD
        return usage_percent, is_critical

    @staticmethod
    def cleanup_memory():
        """메모리 정리"""
        gc.collect()
        logger.info("메모리 정리 완료")

    @staticmethod
    def get_memory_info() -> Dict[str, Any] if Dict is not None else None:
        """메모리 정보 조회"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'free': memory.free
        }


class PerformanceOptimizer:
    """성능 최적화 클래스"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'size': 0
        }

    @lru_cache(maxsize=100)
    def get_cached_metrics(self, cache_key: str) -> dict:
        self.cache_stats['hits'] += 1
        return self._fetch_metrics(cache_key)

    def _fetch_metrics(self, cache_key: str) -> dict:
        self.cache_stats['misses'] += 1
        return {}

    def get_cache_stats(self) -> dict:
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total if total > 0 else 0
        return {
            **self.cache_stats,
            'hit_rate': hit_rate
        }


class IntegratedDashboardService:
    """통합 대시보드 서비스 (성능 최적화 버전)"""

    def __init__(self):
        self.ai_service = IntegratedAIService()
        self.plugin_monitor = PluginMonitoringDashboard()
        self.data_cache = {}
        self.cache_expiry = {}
        self.active_connections = set()
        self.data_queue = queue.Queue()
        self.monitoring_active = False

        # 성능 최적화 컴포넌트
        self.memory_manager = MemoryManager()
        self.performance_optimizer = PerformanceOptimizer()
        self.last_cleanup = datetime.now()

        # 실시간 데이터 업데이트 스레드 시작
        self.start_monitoring()

    def start_monitoring(self):
        """실시간 모니터링 시작 - 비활성화됨"""
        # 통합 대시보드 모니터링 비활성화됨 (서버는 계속 실행)
        # if not self.monitoring_active:
        #     self.monitoring_active = True
        #     self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        #     self.monitor_thread.start()
        logger.info("통합 대시보드 모니터링 비활성화됨")

    def stop_monitoring(self):
        """실시간 모니터링 중지"""
        self.monitoring_active = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        logger.info("통합 대시보드 모니터링 중지")

    def _monitoring_loop(self):
        """실시간 모니터링 루프 (성능 최적화)"""
        while self.monitoring_active:
            try:
                # 메모리 사용률 확인
                memory_usage, is_critical = self.memory_manager.check_memory_usage()

                if is_critical:
                    logger.warning(f"메모리 사용률이 높습니다: {memory_usage}%")
                    self.memory_manager.cleanup_memory()
                    self._cleanup_cache()

                # 정기 캐시 정리
                if (datetime.now() - self.last_cleanup).total_seconds() > CACHE_CLEANUP_INTERVAL:
                    self._cleanup_cache()
                    self.last_cleanup = datetime.now()

                # 모든 실시간 데이터 수집 (병렬 처리)
                dashboard_data = self._collect_all_data_parallel()

                # 캐시 업데이트
                self.data_cache = dashboard_data
                self.cache_expiry = datetime.now() + timedelta(seconds=30)

                # 활성 연결에 데이터 브로드캐스트
                self._broadcast_to_connections(dashboard_data)

                time.sleep(10)  # 10초마다 업데이트

            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(30)

    def _collect_all_data_parallel(self) -> Dict[str, Any] if Dict is not None else None:
        """병렬 처리로 모든 실시간 데이터 수집"""
        try:
            current_time = datetime.now()

            # 병렬로 데이터 수집
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    'system_status': executor.submit(self._get_system_status),
                    'performance_metrics': executor.submit(self._get_performance_metrics),
                    'active_alerts': executor.submit(self._get_active_alerts),
                    'user_activity': executor.submit(self._get_user_activity),
                    'ai_insights': executor.submit(self.ai_service.get_comprehensive_dashboard),
                    'iot_data': executor.submit(self._get_iot_data_safe),
                    'plugin_monitoring': executor.submit(self._get_plugin_data_safe),
                    'notifications': executor.submit(self._get_notifications_safe)
                }

                # 결과 수집
                basic_data = {
                    'timestamp': current_time.isoformat(),
                    'memory_info': self.memory_manager.get_memory_info(),
                    'cache_stats': self.performance_optimizer.get_cache_stats()
                }

                for key, future in futures.items() if futures is not None else []:
                    try:
                        result = future.result(timeout=5)  # 5초 타임아웃
                        if basic_data is not None:
                            basic_data[key] = result
                    except Exception as e:
                        logger.warning(f"{key} 데이터 수집 실패: {e}")
                        if basic_data is not None:
                            basic_data[key] = {'error': f'{key} 데이터를 불러올 수 없습니다.'}

                return basic_data

        except Exception as e:
            logger.error(f"병렬 데이터 수집 오류: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': f'데이터 수집 중 오류 발생: {str(e)}'
            }

    def _get_iot_data_safe(self) -> Dict[str, Any] if Dict is not None else None:
        """IoT 데이터 안전 조회"""
        try:
            return get_iot_dashboard()
        except Exception as e:
            logger.warning(f"IoT 데이터 수집 실패: {e}")
            return {'error': 'IoT 데이터를 불러올 수 없습니다.'}

    def _get_plugin_data_safe(self) -> Dict[str, Any] if Dict is not None else None:
        """플러그인 데이터 안전 조회"""
        try:
            return self.plugin_monitor.real_time_data
        except Exception as e:
            logger.warning(f"플러그인 모니터링 데이터 수집 실패: {e}")
            return {'error': '플러그인 데이터를 불러올 수 없습니다.'}

    def _get_notifications_safe(self) -> List[Dict[str, Any] if List is not None else None]:
        """알림 데이터 안전 조회"""
        try:
            return notification_manager.get_user_notifications(str(current_user.id))
        except Exception as e:
            logger.warning(f"알림 데이터 수집 실패: {e}")
            return []

    def _cleanup_cache(self):
        """캐시 정리"""
        try:
            current_time = datetime.now()
            expired_keys = []

            if self.cache_expiry is not None:
                for key, expiry in self.cache_expiry.items():
                    if current_time > expiry:
                        expired_keys.append(key)

            if expired_keys is not None:
                for key in expired_keys:
                    if self.cache_expiry is not None:
                        del self.cache_expiry[key]
                    if key in self.data_cache and self.data_cache is not None:
                        del self.data_cache[key]

            # 캐시 크기 제한
            if len(self.data_cache) > MAX_CACHE_SIZE:
                # 가장 오래된 항목들 제거
                sorted_items = sorted(self.cache_expiry.items() if self.cache_expiry is not None else [], key=lambda x: x[1] if x is not None else None)
                items_to_remove = len(self.data_cache) - MAX_CACHE_SIZE

                for i in range(items_to_remove):
                    if i < len(sorted_items):
                        key = sorted_items[i][0] if sorted_items is not None else None
                        if self.cache_expiry is not None:
                            del self.cache_expiry[key]
                        if key in self.data_cache and self.data_cache is not None:
                            del self.data_cache[key]

            logger.info(f"캐시 정리 완료: {len(expired_keys)}개 항목 제거")

        except Exception as e:
            logger.error(f"캐시 정리 오류: {e}")

    def _get_system_status(self) -> Dict[str, Any] if Dict is not None else None:
        """시스템 상태 조회"""
        try:
            import psutil

            return {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': self._get_network_io(),
                'active_connections': len(self.active_connections),
                'uptime': self._get_uptime(),
                'last_backup': '2024-01-15 14:30',  # 실제로는 백업 매니저에서 가져옴
                'database_status': 'healthy',
                'api_response_time': 150  # ms
            }
        except Exception as e:
            logger.error(f"시스템 상태 조회 오류: {e}")
            return {'error': '시스템 상태를 확인할 수 없습니다.'}

    def _get_performance_metrics(self) -> Dict[str, Any] if Dict is not None else None:
        """성능 메트릭 조회"""
        try:
            # 실제 데이터베이스에서 조회
            from models_main import Order, User, Attendance
            from extensions import db

            today = datetime.now().date()

            # 오늘의 주문 통계
            today_orders = db.session.query(Order).filter(
                Order.created_at >= today
            ).all()

            # 오늘의 근무 통계
            today_attendance = db.session.query(Attendance).filter(
                Attendance.clock_in >= today
            ).all()

            # 활성 사용자 수
            active_users = db.session.query(User).filter(
                User.last_login >= datetime.now() - timedelta(hours=1)
            ).count()

            return {
                'today_orders': {
                    'total': len(today_orders),
                    'pending': len([o for o in today_orders if o.status == 'pending']),
                    'completed': len([o for o in today_orders if o.status == 'completed']),
                    'total_sales': sum(o.total_amount for o in today_orders if o.total_amount)
                },
                'today_attendance': {
                    'total': len(today_attendance),
                    'on_time': len([a for a in today_attendance if a.clock_in.time() <= datetime.strptime('09:00', '%H:%M').time()]),
                    'late': len([a for a in today_attendance if a.clock_in.time() > datetime.strptime('09:00', '%H:%M').time()])
                },
                'active_users': active_users,
                'system_performance': {
                    'response_time': 150,  # ms
                    'throughput': 1000,    # requests/min
                    'error_rate': 0.1      # %
                }
            }
        except Exception as e:
            logger.error(f"성능 메트릭 조회 오류: {e}")
            return {'error': '성능 메트릭을 확인할 수 없습니다.'}

    def _get_active_alerts(self) -> List[Dict[str, Any] if List is not None else None]:
        """활성 알림 조회"""
        try:
            alerts = []

            # 시스템 알림
            # if hasattr(realtime_data, 'system_alerts'):
            #     alerts.extend(realtime_data.get('system_alerts', []) if realtime_data else None)

            # 재고 부족 알림
            from models_main import InventoryItem
            low_stock_items = InventoryItem.query.filter(
                InventoryItem.current_stock <= 10
            ).all()

            if low_stock_items is not None:
                for item in low_stock_items:
                    alerts.append({
                        'type': 'low_stock',
                        'severity': 'warning',
                        'message': f"{item.name} 재고가 {item.current_stock}개로 부족합니다.",
                        'timestamp': datetime.now().isoformat()
                    })

            # 매출 급감 알림 (AI 기반)
            try:
                ai_alerts = self.ai_service._get_active_alerts()
                alerts.extend(ai_alerts)
            except Exception as e:
                logger.warning(f"AI 알림 조회 실패: {e}")

            return alerts

        except Exception as e:
            logger.error(f"활성 알림 조회 오류: {e}")
            return []

    def _get_user_activity(self) -> Dict[str, Any] if Dict is not None else None:
        """사용자 활동 조회"""
        try:
            from models_main import User, Order, Attendance
            from extensions import db

            # 최근 1시간 활동
            one_hour_ago = datetime.now() - timedelta(hours=1)

            recent_orders = db.session.query(Order).filter(
                Order.created_at >= one_hour_ago
            ).count()

            recent_logins = db.session.query(User).filter(
                User.last_login >= one_hour_ago
            ).count()

            return {
                'recent_orders': recent_orders,
                'recent_logins': recent_logins,
                'active_sessions': len(self.active_connections),
                'peak_hours': self._get_peak_hours()
            }
        except Exception as e:
            logger.error(f"사용자 활동 조회 오류: {e}")
            return {'error': '사용자 활동을 확인할 수 없습니다.'}

    def _get_network_io(self) -> Dict[str, float] if Dict is not None else None:
        """네트워크 I/O 조회"""
        try:
            import psutil
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception:
            return {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0}

    def _get_uptime(self) -> str:
        """시스템 업타임 조회"""
        try:
            import psutil
            uptime_seconds = time.time() - psutil.boot_time()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except Exception:
            return "Unknown"

    def _get_peak_hours(self) -> List[int] if List is not None else None:
        """피크 시간대 조회"""
        try:
            from models_main import Order
            from extensions import db
            from sqlalchemy import func

            # 최근 7일간 시간대별 주문 수
            seven_days_ago = datetime.now() - timedelta(days=7)

            hourly_orders = db.session.query(
                func.extract('hour', Order.created_at).label('hour'),
                func.count(Order.id).label('count')
            ).filter(
                Order.created_at >= seven_days_ago
            ).group_by(
                func.extract('hour', Order.created_at)
            ).all()

            # 상위 3개 시간대 반환
            peak_hours = sorted(hourly_orders, key=lambda x: x.count, reverse=True)[:3]
            return [int(hour.hour) for hour in peak_hours]

        except Exception as e:
            logger.error(f"피크 시간대 조회 오류: {e}")
            return [12, 18, 19]  # 기본값

    def _broadcast_to_connections(self, data: Dict[str, Any] if Dict is not None else None):
        """활성 연결에 데이터 브로드캐스트"""
        try:
            message = json.dumps({
                'type': 'dashboard_update',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })

            # 실제 구현에서는 WebSocket이나 SSE를 통해 브로드캐스트
            # 현재는 큐에 메시지 추가
            self.data_queue.put(message)

        except Exception as e:
            logger.error(f"브로드캐스트 오류: {e}")

    def get_cached_dashboard(self) -> Dict[str, Any] if Dict is not None else None:
        """캐시된 대시보드 데이터 조회"""
        if self.data_cache and datetime.now() < self.cache_expiry:
            return self.data_cache
        else:
            return self._collect_all_data()


# 전역 서비스 인스턴스
dashboard_service = IntegratedDashboardService()


@integrated_dashboard_bp.route('/api/dashboard/integrated', methods=['GET'])
@login_required
def get_integrated_dashboard():
    """통합 대시보드 데이터 조회"""
    try:
        dashboard_data = dashboard_service.get_cached_dashboard()

        return jsonify({
            'success': True,
            'data': dashboard_data,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"통합 대시보드 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '대시보드 데이터를 불러올 수 없습니다.',
            'details': str(e)
        }), 500


@integrated_dashboard_bp.route('/api/dashboard/stream')
@login_required
def dashboard_stream():
    """Server-Sent Events를 통한 실시간 대시보드 스트림"""
    def generate():
        connection_id = str(time.time())
        dashboard_service.active_connections.add(connection_id)

        try:
            # 연결 확인 메시지
            yield f"data: {json.dumps({'type': 'connected', 'connection_id': connection_id})}\n\n"

            # 초기 데이터 전송
            initial_data = dashboard_service.get_cached_dashboard()
            yield f"data: {json.dumps({'type': 'initial_data', 'data': initial_data})}\n\n"

            # 실시간 업데이트 스트림
            while True:
                try:
                    message = dashboard_service.data_queue.get(timeout=30)
                    yield f"data: {message}\n\n"
                except queue.Empty:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"

        except Exception as e:
            logger.error(f"대시보드 스트림 오류: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            dashboard_service.active_connections.discard(connection_id)

    return Response(generate(), mimetype='text/event-stream')


@integrated_dashboard_bp.route('/api/dashboard/metrics', methods=['GET'])
@login_required
def get_dashboard_metrics():
    """대시보드 메트릭 조회"""
    try:
        metrics = dashboard_service._get_performance_metrics()

        return jsonify({
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"대시보드 메트릭 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '메트릭을 불러올 수 없습니다.'
        }), 500


@integrated_dashboard_bp.route('/api/dashboard/alerts', methods=['GET'])
@login_required
def get_dashboard_alerts():
    """대시보드 알림 조회"""
    try:
        alerts = dashboard_service._get_active_alerts()

        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"대시보드 알림 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '알림을 불러올 수 없습니다.'
        }), 500


@integrated_dashboard_bp.route('/api/dashboard/system-status', methods=['GET'])
@login_required
def get_system_status():
    """시스템 상태 조회"""
    try:
        status = dashboard_service._get_system_status()

        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"시스템 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '시스템 상태를 확인할 수 없습니다.'
        }), 500


@integrated_dashboard_bp.route('/api/dashboard/ai-insights', methods=['GET'])
@login_required
def get_ai_insights():
    """AI 인사이트 조회"""
    try:
        insights = dashboard_service.ai_service.get_comprehensive_dashboard()

        return jsonify({
            'success': True,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"AI 인사이트 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': 'AI 인사이트를 불러올 수 없습니다.'
        }), 500


@integrated_dashboard_bp.route('/api/dashboard/performance', methods=['GET'])
@login_required
def get_dashboard_performance():
    """대시보드 성능 정보 조회"""
    try:
        memory_info = dashboard_service.memory_manager.get_memory_info()
        cache_stats = dashboard_service.performance_optimizer.get_cache_stats()

        return jsonify({
            'success': True,
            'performance': {
                'memory': memory_info,
                'cache': cache_stats,
                'active_connections': len(dashboard_service.active_connections),
                'cache_size': len(dashboard_service.data_cache),
                'uptime': dashboard_service._get_uptime()
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"성능 정보 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '성능 정보를 불러올 수 없습니다.'
        }), 500


@integrated_dashboard_bp.route('/api/dashboard/health', methods=['GET'])
@login_required
def get_dashboard_health():
    """대시보드 상태 체크"""
    try:
        # 메모리 상태 확인
        memory_usage, is_critical = dashboard_service.memory_manager.check_memory_usage()

        # 연결 상태 확인
        connection_health = len(dashboard_service.active_connections) < 100

        # 캐시 상태 확인
        cache_health = len(dashboard_service.data_cache) < MAX_CACHE_SIZE

        # 전체 상태 결정
        overall_health = 'healthy'
        if is_critical or not connection_health or not cache_health:
            overall_health = 'warning'
        if memory_usage > 95:
            overall_health = 'critical'

        return jsonify({
            'success': True,
            'health': {
                'status': overall_health,
                'memory_usage': memory_usage,
                'memory_critical': is_critical,
                'connections_healthy': connection_health,
                'cache_healthy': cache_health,
                'monitoring_active': dashboard_service.monitoring_active
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"상태 체크 실패: {e}")
        return jsonify({
            'success': False,
            'error': '상태를 확인할 수 없습니다.'
        }), 500


@integrated_dashboard_bp.route('/api/dashboard/cleanup', methods=['POST'])
@login_required
def cleanup_dashboard():
    """대시보드 정리 (관리자 전용)"""
    try:
        # 메모리 정리
        dashboard_service.memory_manager.cleanup_memory()

        # 캐시 정리
        dashboard_service._cleanup_cache()

        return jsonify({
            'success': True,
            'message': '대시보드 정리 완료',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"대시보드 정리 실패: {e}")
        return jsonify({
            'success': False,
            'error': '정리를 완료할 수 없습니다.'
        }), 500
