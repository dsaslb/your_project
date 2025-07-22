"""
백엔드 성능 최적화 유틸리티
캐싱, 데이터베이스 최적화, 쿼리 최적화 기능 제공
"""

import time
import logging
import functools
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from flask import current_app, g
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import redis
import json

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """성능 최적화 관리자"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.query_cache = {}
        self.slow_query_threshold = 1.0  # 1초 이상 쿼리 로깅
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 성능 최적화 초기화"""
        self.app = app
        
        # Redis 연결 설정
        try:
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url)
            logger.info("Redis 캐시 연결 성공")
        except Exception as e:
            logger.warning(f"Redis 연결 실패: {e}")
        
        # 데이터베이스 연결 풀 최적화
        self._optimize_db_pool(app)
        
        # 쿼리 모니터링 설정
        self._setup_query_monitoring(app)
        
        logger.info("성능 최적화 시스템 초기화 완료")
    
    def _optimize_db_pool(self, app):
        """데이터베이스 연결 풀 최적화"""
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_url:
            engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=20,  # 연결 풀 크기
                max_overflow=30,  # 최대 오버플로우
                pool_pre_ping=True,  # 연결 상태 확인
                pool_recycle=3600,  # 1시간마다 연결 재생성
                echo=False  # SQL 로깅 비활성화 (프로덕션)
            )
            app.config['SQLALCHEMY_ENGINE'] = engine
    
    def _setup_query_monitoring(self, app):
        """쿼리 모니터링 설정"""
        @app.before_request
        def before_request():
            g.start_time = time.time()
            g.query_count = 0
            g.slow_queries = []
        
        @app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                request_time = time.time() - g.start_time
                query_count = getattr(g, 'query_count', 0)
                
                # 느린 요청 로깅
                if request_time > 2.0:  # 2초 이상 요청
                    logger.warning(f"느린 요청: {request_time:.2f}초, 쿼리 수: {query_count}")
                
                # 느린 쿼리 로깅
                slow_queries = getattr(g, 'slow_queries', [])
                for query in slow_queries:
                    logger.warning(f"느린 쿼리: {query['time']:.2f}초 - {query['sql']}")
                
                # 응답 헤더에 성능 정보 추가
                response.headers['X-Request-Time'] = f"{request_time:.3f}"
                response.headers['X-Query-Count'] = str(query_count)
            
            return response
    
    def cache_result(self, key: str, ttl: int = 300):
        """함수 결과 캐싱 데코레이터"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.redis_client:
                    return func(*args, **kwargs)
                
                # 캐시 키 생성
                cache_key = f"cache:{key}:{hash(str(args) + str(kwargs))}"
                
                # 캐시에서 결과 조회
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    try:
                        return json.loads(cached_result)
                    except:
                        pass
                
                # 함수 실행 및 결과 캐싱
                result = func(*args, **kwargs)
                try:
                    self.redis_client.setex(
                        cache_key, 
                        ttl, 
                        json.dumps(result, default=str)
                    )
                except:
                    pass
                
                return result
            return wrapper
        return decorator
    
    def query_optimizer(self, func: Callable) -> Callable:
        """쿼리 최적화 데코레이터"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 쿼리 실행
            result = func(*args, **kwargs)
            
            # 실행 시간 측정
            execution_time = time.time() - start_time
            
            # 쿼리 카운트 증가
            if hasattr(g, 'query_count'):
                g.query_count += 1
            
            # 느린 쿼리 로깅
            if execution_time > self.slow_query_threshold:
                if hasattr(g, 'slow_queries'):
                    g.slow_queries.append({
                        'sql': str(func.__name__),
                        'time': execution_time,
                        'args': args,
                        'kwargs': kwargs
                    })
            
            return result
        return wrapper
    
    def batch_processor(self, items: List[Any], batch_size: int = 100):
        """배치 처리 제너레이터"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    def memory_optimizer(self, func: Callable) -> Callable:
        """메모리 최적화 데코레이터"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import gc
            
            # 가비지 컬렉션 실행
            gc.collect()
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 메모리 사용량 로깅
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            logger.debug(f"메모리 사용량: {memory_info.rss / 1024 / 1024:.2f} MB")
            
            return result
        return wrapper
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 수집"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cache_hit_rate': 0.0,
            'average_query_time': 0.0,
            'memory_usage': 0.0,
            'active_connections': 0
        }
        
        # 캐시 히트율 계산
        if self.redis_client:
            try:
                info = self.redis_client.info('stats')
                hits = info.get('keyspace_hits', 0)
                misses = info.get('keyspace_misses', 0)
                total = hits + misses
                if total > 0:
                    metrics['cache_hit_rate'] = hits / total
            except:
                pass
        
        # 메모리 사용량
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            metrics['memory_usage'] = memory_info.rss / 1024 / 1024  # MB
        except:
            pass
        
        # 데이터베이스 연결 수
        try:
            if hasattr(current_app, 'config') and 'SQLALCHEMY_ENGINE' in current_app.config:
                engine = current_app.config['SQLALCHEMY_ENGINE']
                metrics['active_connections'] = engine.pool.size()
        except:
            pass
        
        return metrics
    
    def clear_cache(self, pattern: str = "*"):
        """캐시 정리"""
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"cache:{pattern}")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"캐시 정리 완료: {len(keys)}개 키")
            except Exception as e:
                logger.error(f"캐시 정리 실패: {e}")
    
    def optimize_database(self):
        """데이터베이스 최적화"""
        try:
            from app import db
            
            # 인덱스 최적화
            with db.engine.connect() as conn:
                # 테이블별 통계 업데이트
                conn.execute(text("ANALYZE"))
                
                # 느린 쿼리 로그 확인
                conn.execute(text("SHOW VARIABLES LIKE 'slow_query_log'"))
                
            logger.info("데이터베이스 최적화 완료")
        except Exception as e:
            logger.error(f"데이터베이스 최적화 실패: {e}")

# 전역 성능 최적화 인스턴스
performance_optimizer = PerformanceOptimizer() 