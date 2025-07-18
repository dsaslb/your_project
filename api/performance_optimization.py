import weakref
import threading
from flask import current_app, g, request
from sqlalchemy.orm import Session  # pyright: ignore
from sqlalchemy import text
import redis
import psutil
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from concurrent.futures import ThreadPoolExecutor  # pyright: ignore
import time
import logging
import gc
import asyncio
from flask import current_app
from flask import request
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
성능 최적화 모듈
쿼리 최적화, 비동기 처리, 메모리 최적화 기능 제공
"""


logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """성능 최적화 클래스"""

    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }
        self.query_stats = {
            'total_queries': 0,
            'slow_queries': 0,
            'avg_response_time': 0
        }

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask 앱 초기화"""
        self.app = app

        # Redis 연결
        try:
            self.redis_client = redis.Redis(
                host=app.config.get('REDIS_HOST', 'localhost'),
                port=app.config.get('REDIS_PORT', 6379),
                db=app.config.get('REDIS_DB', 0),
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis 연결 실패: {e}")
            self.redis_client = None

        # 성능 모니터링 미들웨어 등록
        app.before_request(self.before_request)
        app.after_request(self.after_request)

        # 주기적 메모리 정리
        self._schedule_memory_cleanup()

    def before_request(self):
        """요청 전 처리"""
        g.start_time = time.time()
        g.query_count = 0
        g.slow_queries = []

    def after_request(self, response):
        """요청 후 처리"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            self.query_stats['total_queries'] += 1
            prev_avg = self.query_stats['avg_response_time']
            total_queries = self.query_stats['total_queries']
            self.query_stats['avg_response_time'] = (
                (prev_avg * (total_queries - 1) + duration) / total_queries
            )

            # 느린 쿼리 기록
            if duration > 1.0:  # 1초 이상
                self.query_stats['slow_queries'] += 1
                g.slow_queries.append({
                    'endpoint': request.endpoint,
                    'duration': duration,
                    'timestamp': time.time()
                })

        return response

    def cache_decorator(self, ttl=300):
        """캐시 데코레이터"""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.redis_client:
                    return func(*args, **kwargs)

                # 캐시 키 생성
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items() if kwargs is not None else [])))}"

                # 캐시에서 조회
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    self.cache_stats['hits'] += 1
                    return cached_result

                self.cache_stats['misses'] += 1

                # 함수 실행
                result = func(*args, **kwargs)

                # 결과 캐시 저장
                try:
                    self.redis_client.setex(cache_key, ttl, str(result))
                    self.cache_stats['sets'] += 1
                except Exception as e:
                    logger.warning(f"캐시 저장 실패: {e}")

                return result
            return wrapper
        return decorator

    def async_task(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """비동기 작업 데코레이터"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            future = self.executor.submit(func, *args, **kwargs)
            return future
        return wrapper

    def optimize_query(self,  query: str) -> str:
        """SQL 쿼리 최적화"""
        # 기본적인 쿼리 최적화
        optimized = query.strip() if query is not None else ''

        # SELECT * 대신 필요한 컬럼만 지정
        if 'SELECT *' in optimized.upper():
            logger.warning("SELECT * 사용 감지 - 특정 컬럼 지정 권장")

        # LIMIT 추가 (없는 경우)
        if 'LIMIT' not in optimized.upper() and 'SELECT' in optimized.upper():
            if 'ORDER BY' in optimized.upper():
                optimized += ' LIMIT 1000'
            else:
                optimized += ' LIMIT 1000'

        return optimized

    def batch_process(self, items: List[Any], batch_size=100, func: Optional[Callable[[List[Any]], List[Any]]] = None) -> List[Any]:
        """배치 처리"""
        results: List[Any] = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            if func:
                batch_results = func(batch)
                results.extend(batch_results if batch_results is not None else [])
            else:
                results.extend(batch)
        return results

    def memory_optimization(self):
        """메모리 최적화"""
        # 가비지 컬렉션 실행
        collected = gc.collect()
        logger.info(f"가비지 컬렉션 완료: {collected} 객체 정리")

        # 메모리 사용량 확인
        memory_info = psutil.virtual_memory()
        if memory_info.percent > 80:
            logger.warning(f"메모리 사용량 높음: {memory_info.percent}%")

            # 추가 메모리 정리
            gc.collect()

            # 캐시 정리 (Redis)
            if self.redis_client:
                try:
                    self.redis_client.flushdb()
                    logger.info("Redis 캐시 정리 완료")
                except Exception as e:
                    logger.error(f"Redis 캐시 정리 실패: {e}")

    def _schedule_memory_cleanup(self):
        """주기적 메모리 정리 스케줄링"""
        def cleanup():
            while True:
                time.sleep(300)  # 5분마다
                self.memory_optimization()

        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()

    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        memory_info = psutil.virtual_memory()

        return {
            'cache_stats': self.cache_stats.copy(),
            'query_stats': self.query_stats.copy(),
            'memory_usage': {
                'percent': memory_info.percent,
                'available': memory_info.available,
                'total': memory_info.total
            },
            'system_info': {
                'cpu_percent': psutil.cpu_percent(),
                'disk_usage': psutil.disk_usage('/').percent
            }
        }

    def reset_stats(self):
        """통계 초기화"""
        self.cache_stats = {'hits': 0, 'misses': 0, 'sets': 0}
        self.query_stats = {'total_queries': 0, 'slow_queries': 0, 'avg_response_time': 0}


# 전역 인스턴스
performance_optimizer = PerformanceOptimizer()


def init_performance_optimization(app):
    """성능 최적화 초기화"""
    performance_optimizer.init_app(app)
    return performance_optimizer

# 유틸리티 함수들


def cache_result(ttl=300):
    """캐시 결과 데코레이터"""
    return performance_optimizer.cache_decorator(ttl)


def run_async(func: Callable[..., Any]):
    """비동기 실행 데코레이터"""
    return performance_optimizer.async_task(func)


def optimize_sql_query(query: str) -> str:
    """SQL 쿼리 최적화"""
    return performance_optimizer.optimize_query(query)


def batch_processing(items: List[Any], batch_size: int = 100, func: Optional[Callable[[List[Any]], List[Any]]] = None) -> List[Any]:
    """배치 처리"""
    return performance_optimizer.batch_process(items,  batch_size,  func)


def get_performance_metrics() -> Dict[str, Any]:
    """성능 메트릭 반환"""
    return performance_optimizer.get_performance_stats()
