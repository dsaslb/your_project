"""
통합 모니터링 시스템
시스템 성능, 에러, 사용자 활동 모니터링
"""

import logging
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, request, g, current_app
from collections import defaultdict, deque
from extensions import db, cache

logger = logging.getLogger(__name__)


class SystemMonitor:
    """시스템 모니터링 클래스"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.metrics = {
            'requests': deque(maxlen=1000),
            'errors': deque(maxlen=1000),
            'performance': deque(maxlen=1000),
            'database': deque(maxlen=1000)
        }
        self.start_time = datetime.utcnow()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Flask 앱에 모니터링 설정"""
        self.app = app
        
        # 요청 전후 처리
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
        
        logger.info("시스템 모니터링 초기화 완료")
    
    def before_request(self):
        """요청 전 처리"""
        g.start_time = time.time()
        g.request_id = self._generate_request_id()
        
        # 요청 정보 기록
        request_info = {
            'timestamp': datetime.utcnow(),
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_length': request.content_length or 0
        }
        
        self.metrics['requests'].append(request_info)
    
    def after_request(self, response):
        """요청 후 처리"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # 성능 메트릭 기록
            performance_info = {
                'timestamp': datetime.utcnow(),
                'request_id': g.request_id,
                'duration': duration,
                'status_code': response.status_code,
                'path': request.path,
                'method': request.method
            }
            
            self.metrics['performance'].append(performance_info)
            
            # 느린 요청 로깅
            if duration > 2.0:  # 2초 이상
                logger.warning(f"느린 요청: {request.path} ({duration:.2f}초)")
            
            # 응답 헤더에 성능 정보 추가
            response.headers['X-Request-Time'] = f"{duration:.3f}"
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    def teardown_request(self, exception=None):
        """요청 종료 처리"""
        if exception:
            error_info = {
                'timestamp': datetime.utcnow(),
                'request_id': getattr(g, 'request_id', 'unknown'),
                'error_type': type(exception).__name__,
                'error_message': str(exception),
                'path': request.path,
                'method': request.method
            }
            
            self.metrics['errors'].append(error_info)
            logger.error(f"요청 처리 중 오류: {exception}")
    
    def _generate_request_id(self) -> str:
        """요청 ID 생성"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            
            # 네트워크 I/O
            network = psutil.net_io_counters()
            
            # 프로세스 정보
            process = psutil.Process()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': {
                    'memory_info': process.memory_info()._asdict(),
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads()
                }
            }
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
            return {}
    
    def get_database_metrics(self) -> Dict[str, Any]:
        """데이터베이스 메트릭 수집"""
        try:
            with db.engine.connect() as conn:
                # 연결 풀 상태
                pool = db.engine.pool
                
                # 테이블 크기 정보
                result = conn.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        attname,
                        n_distinct,
                        correlation
                    FROM pg_stats 
                    WHERE schemaname = 'public'
                    LIMIT 10
                """)
                
                return {
                    'timestamp': datetime.utcnow().isoformat(),
                    'pool': {
                        'size': pool.size(),
                        'checked_in': pool.checkedin(),
                        'checked_out': pool.checkedout(),
                        'overflow': pool.overflow(),
                        'invalid': pool.invalid()
                    },
                    'stats': [dict(row) for row in result]
                }
        except Exception as e:
            logger.error(f"데이터베이스 메트릭 수집 실패: {e}")
            return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보"""
        if not self.metrics['performance']:
            return {}
        
        recent_performance = list(self.metrics['performance'])[-100:]  # 최근 100개
        
        durations = [p['duration'] for p in recent_performance]
        status_codes = [p['status_code'] for p in recent_performance]
        
        # 경로별 통계
        path_stats = defaultdict(list)
        for p in recent_performance:
            path_stats[p['path']].append(p['duration'])
        
        return {
            'total_requests': len(recent_performance),
            'avg_response_time': sum(durations) / len(durations),
            'max_response_time': max(durations),
            'min_response_time': min(durations),
            'status_code_distribution': {
                code: status_codes.count(code) for code in set(status_codes)
            },
            'path_performance': {
                path: {
                    'count': len(times),
                    'avg_time': sum(times) / len(times),
                    'max_time': max(times)
                }
                for path, times in path_stats.items()
            }
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """에러 요약 정보"""
        if not self.metrics['errors']:
            return {}
        
        recent_errors = list(self.metrics['errors'])[-100:]  # 최근 100개
        
        error_types = [e['error_type'] for e in recent_errors]
        error_paths = [e['path'] for e in recent_errors]
        
        return {
            'total_errors': len(recent_errors),
            'error_type_distribution': {
                error_type: error_types.count(error_type) 
                for error_type in set(error_types)
            },
            'error_path_distribution': {
                path: error_paths.count(path) 
                for path in set(error_paths)
            },
            'recent_errors': recent_errors[-10:]  # 최근 10개 에러
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime': (datetime.utcnow() - self.start_time).total_seconds(),
            'checks': {}
        }
        
        # 데이터베이스 연결 확인
        try:
            db.session.execute('SELECT 1')
            health_status['checks']['database'] = 'healthy'
        except Exception as e:
            health_status['checks']['database'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
        
        # 캐시 연결 확인
        try:
            cache.set('health_check', 'ok', timeout=10)
            if cache.get('health_check') == 'ok':
                health_status['checks']['cache'] = 'healthy'
            else:
                health_status['checks']['cache'] = 'unhealthy'
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['checks']['cache'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
        
        # 시스템 리소스 확인
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 90 or memory_percent > 90:
                health_status['checks']['resources'] = 'warning'
            else:
                health_status['checks']['resources'] = 'healthy'
        except Exception as e:
            health_status['checks']['resources'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
        
        return health_status
    
    def clear_old_metrics(self, days: int = 7):
        """오래된 메트릭 정리"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        for metric_type in self.metrics:
            self.metrics[metric_type] = deque(
                [m for m in self.metrics[metric_type] 
                 if m['timestamp'] > cutoff_time],
                maxlen=1000
            )
        
        logger.info(f"{days}일 이전 메트릭 정리 완료")


# 전역 모니터링 인스턴스
system_monitor = SystemMonitor()


def monitor_performance(func):
    """성능 모니터링 데코레이터"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # 성능 메트릭 기록
            if hasattr(system_monitor, 'metrics'):
                performance_info = {
                    'timestamp': datetime.utcnow(),
                    'function': func.__name__,
                    'duration': duration,
                    'status': 'success'
                }
                system_monitor.metrics['performance'].append(performance_info)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            
            # 에러 메트릭 기록
            if hasattr(system_monitor, 'metrics'):
                error_info = {
                    'timestamp': datetime.utcnow(),
                    'function': func.__name__,
                    'duration': duration,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'status': 'error'
                }
                system_monitor.metrics['errors'].append(error_info)
            
            raise
    return wrapper


def get_monitoring_dashboard_data() -> Dict[str, Any]:
    """모니터링 대시보드 데이터"""
    return {
        'system': system_monitor.get_system_metrics(),
        'database': system_monitor.get_database_metrics(),
        'performance': system_monitor.get_performance_summary(),
        'errors': system_monitor.get_error_summary(),
        'health': system_monitor.get_health_status()
    } 