"""
성능 모니터링 시스템
- API 응답 시간 추적
- 데이터베이스 쿼리 성능 모니터링
- 캐시 히트율 추적
- 시스템 리소스 모니터링
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
from collections import defaultdict, deque
import json
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.metrics = {
            'api_calls': defaultdict(list),  # API 호출 통계
            'db_queries': defaultdict(list),  # DB 쿼리 통계
            'cache_stats': defaultdict(int),  # 캐시 통계
            'system_metrics': deque(maxlen=1000),  # 시스템 메트릭
            'slow_queries': deque(maxlen=100),  # 느린 쿼리 기록
            'errors': deque(maxlen=100)  # 에러 기록
        }
        self.lock = threading.Lock()
        self.monitoring_active = True
        
        # 백그라운드 모니터링 시작
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """백그라운드 모니터링 시작"""
        def monitor_system():
        while self.monitoring_active:
            try:
                    self._collect_system_metrics()
                    time.sleep(60)  # 1분마다 수집
                except Exception as e:
                    logger.error(f"시스템 메트릭 수집 오류: {e}")
        
        thread = threading.Thread(target=monitor_system, daemon=True)
        thread.start()
    
    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict(),
                'process_count': len(psutil.pids())
            }
            
            with self.lock:
                self.metrics['system_metrics'].append(metrics)
            
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
    
    def record_api_call(self, endpoint: str, method: str, duration: float, status_code: int):
        """API 호출 기록"""
        with self.lock:
            self.metrics['api_calls'][endpoint].append({
                'method': method,
                'duration': duration,
                'status_code': status_code,
                'timestamp': datetime.now().isoformat()
            })
            
            # 최근 100개만 유지
            if len(self.metrics['api_calls'][endpoint]) > 100:
                self.metrics['api_calls'][endpoint] = self.metrics['api_calls'][endpoint][-100:]
    
    def record_db_query(self, query: str, duration: float, table: str = None):
        """데이터베이스 쿼리 기록"""
        with self.lock:
            self.metrics['db_queries'][table or 'unknown'].append({
                'query': query[:200] + '...' if len(query) > 200 else query,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
            # 느린 쿼리 기록 (1초 이상)
            if duration > 1.0:
                self.metrics['slow_queries'].append({
                    'query': query[:500] + '...' if len(query) > 500 else query,
                    'duration': duration,
                    'table': table,
                    'timestamp': datetime.now().isoformat()
                })
    
    def record_cache_hit(self, cache_type: str):
        """캐시 히트 기록"""
        with self.lock:
            self.metrics['cache_stats'][f'{cache_type}_hits'] += 1
    
    def record_cache_miss(self, cache_type: str):
        """캐시 미스 기록"""
        with self.lock:
            self.metrics['cache_stats'][f'{cache_type}_misses'] += 1
    
    def record_error(self, error_type: str, error_message: str, endpoint: str = None):
        """에러 기록"""
        with self.lock:
            self.metrics['errors'].append({
                'type': error_type,
                'message': error_message,
                'endpoint': endpoint,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_api_stats(self, endpoint: str = None, hours: int = 24) -> Dict:
        """API 통계 조회"""
        with self.lock:
            if endpoint:
                calls = self.metrics['api_calls'].get(endpoint, [])
            else:
                # 모든 엔드포인트 통합
                calls = []
                for endpoint_calls in self.metrics['api_calls'].values():
                    calls.extend(endpoint_calls)
            
            # 시간 필터링
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_calls = [
                call for call in calls 
                if datetime.fromisoformat(call['timestamp']) > cutoff_time
            ]
            
            if not recent_calls:
                return {
                    'total_calls': 0,
                    'avg_duration': 0,
                    'success_rate': 0,
                    'error_count': 0
                }
            
            durations = [call['duration'] for call in recent_calls]
            status_codes = [call['status_code'] for call in recent_calls]
            
            return {
                'total_calls': len(recent_calls),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'success_rate': len([s for s in status_codes if s < 400]) / len(status_codes) * 100,
                'error_count': len([s for s in status_codes if s >= 400])
            }
    
    def get_db_stats(self, table: str = None, hours: int = 24) -> Dict:
        """데이터베이스 통계 조회"""
        with self.lock:
            if table:
                queries = self.metrics['db_queries'].get(table, [])
            else:
                # 모든 테이블 통합
                queries = []
                for table_queries in self.metrics['db_queries'].values():
                    queries.extend(table_queries)
            
            # 시간 필터링
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_queries = [
                query for query in queries 
                if datetime.fromisoformat(query['timestamp']) > cutoff_time
            ]
            
            if not recent_queries:
                return {
                    'total_queries': 0,
                    'avg_duration': 0,
                    'slow_queries': 0
                }
            
            durations = [query['duration'] for query in recent_queries]
            
            return {
                'total_queries': len(recent_queries),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'slow_queries': len([d for d in durations if d > 1.0])
            }
    
    def get_cache_stats(self) -> Dict:
        """캐시 통계 조회"""
        with self.lock:
            stats = {}
            for key, value in self.metrics['cache_stats'].items():
                if key.endswith('_hits'):
                    cache_type = key.replace('_hits', '')
                    hits = value
                    misses = self.metrics['cache_stats'].get(f'{cache_type}_misses', 0)
                    total = hits + misses
                    hit_rate = (hits / total * 100) if total > 0 else 0
                    
                    stats[cache_type] = {
                        'hits': hits,
                        'misses': misses,
                        'total': total,
                        'hit_rate': hit_rate
                    }
            
            return stats
    
    def get_system_metrics(self, hours: int = 1) -> List[Dict]:
        """시스템 메트릭 조회"""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                metric for metric in self.metrics['system_metrics']
                if datetime.fromisoformat(metric['timestamp']) > cutoff_time
            ]
            return recent_metrics
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict]:
        """느린 쿼리 조회"""
        with self.lock:
            return list(self.metrics['slow_queries'])[-limit:]
    
    def get_errors(self, limit: int = 10) -> List[Dict]:
        """에러 조회"""
        with self.lock:
            return list(self.metrics['errors'])[-limit:]
    
    def get_performance_summary(self) -> Dict:
        """성능 요약 조회"""
        return {
            'api_stats': self.get_api_stats(),
            'db_stats': self.get_db_stats(),
            'cache_stats': self.get_cache_stats(),
            'system_metrics': self.get_system_metrics(),
            'slow_queries_count': len(self.metrics['slow_queries']),
            'errors_count': len(self.metrics['errors'])
        }
    
    def clear_old_data(self, days: int = 7):
        """오래된 데이터 정리"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        with self.lock:
            # API 호출 데이터 정리
            for endpoint in list(self.metrics['api_calls'].keys()):
                self.metrics['api_calls'][endpoint] = [
                    call for call in self.metrics['api_calls'][endpoint]
                    if datetime.fromisoformat(call['timestamp']) > cutoff_time
                ]
            
            # DB 쿼리 데이터 정리
            for table in list(self.metrics['db_queries'].keys()):
                self.metrics['db_queries'][table] = [
                    query for query in self.metrics['db_queries'][table]
                    if datetime.fromisoformat(query['timestamp']) > cutoff_time
                ]
            
            # 시스템 메트릭 정리
            self.metrics['system_metrics'] = deque([
                metric for metric in self.metrics['system_metrics']
                if datetime.fromisoformat(metric['timestamp']) > cutoff_time
            ], maxlen=1000)


# 전역 성능 모니터 인스턴스
performance_monitor = PerformanceMonitor()


# 데코레이터들
def monitor_api_performance(endpoint: str = None):
    """API 성능 모니터링 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # 성능 기록
                ep = endpoint or f"{func.__module__}.{func.__name__}"
                performance_monitor.record_api_call(
                    endpoint=ep,
                    method=request.method if hasattr(request, 'method') else 'GET',
                    duration=duration,
                    status_code=200
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # 에러 기록
                ep = endpoint or f"{func.__module__}.{func.__name__}"
                performance_monitor.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    endpoint=ep
                )
                performance_monitor.record_api_call(
                    endpoint=ep,
                    method=request.method if hasattr(request, 'method') else 'GET',
                    duration=duration,
                    status_code=500
                )
                raise
        return wrapper
    return decorator


def monitor_db_performance(table: str = None):
    """데이터베이스 성능 모니터링 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # DB 쿼리 성능 기록
                performance_monitor.record_db_query(
                    query=f"{func.__name__}",
                    duration=duration,
                    table=table
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # 에러 기록
                performance_monitor.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


# SQLAlchemy 이벤트 리스너 설정
def setup_db_monitoring(db):
    """데이터베이스 모니터링 설정"""
    from sqlalchemy import event
    
    @event.listens_for(db.engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
    
    @event.listens_for(db.engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        
        # 테이블명 추출 (간단한 방식)
        table = 'unknown'
        statement_lower = statement.lower()
        if 'from ' in statement_lower:
            parts = statement_lower.split('from ')
            if len(parts) > 1:
                table_part = parts[1].split()[0]
                table = table_part.strip('`"[]')
        
        performance_monitor.record_db_query(
            query=statement[:200] + '...' if len(statement) > 200 else statement,
            duration=total,
            table=table
        )
