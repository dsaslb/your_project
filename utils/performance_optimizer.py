"""
성능 최적화 유틸리티
데이터베이스 쿼리, 캐싱, 연결 풀링 최적화
"""

import logging
import time
from functools import wraps
from typing import Dict, Any, List, Optional
from flask import current_app, g
from sqlalchemy import text
from sqlalchemy.orm import joinedload, selectinload
from extensions import db, cache

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """성능 최적화 관리자"""
    
    def __init__(self):
        self.query_stats = {}
        self.slow_query_threshold = 1.0  # 1초 이상 쿼리
        self.cache_hit_ratio = 0.0
        self.connection_pool_stats = {}
    
    def optimize_query(self, query, eager_loads=None):
        """쿼리 최적화"""
        if eager_loads:
            for load in eager_loads:
                if hasattr(load, 'relationship'):
                    query = query.options(joinedload(load.relationship))
                else:
                    query = query.options(selectinload(load))
        
        return query
    
    def cache_query_result(self, key: str, result: Any, ttl: int = 300):
        """쿼리 결과 캐싱"""
        try:
            cache.set(key, result, timeout=ttl)
            return True
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
            return False
    
    def get_cached_result(self, key: str):
        """캐시된 결과 조회"""
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"캐시 조회 실패: {e}")
            return None
    
    def monitor_query_performance(self, query_name: str):
        """쿼리 성능 모니터링 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # 성능 통계 기록
                    if query_name not in self.query_stats:
                        self.query_stats[query_name] = {
                            'count': 0,
                            'total_time': 0,
                            'avg_time': 0,
                            'max_time': 0,
                            'min_time': float('inf')
                        }
                    
                    stats = self.query_stats[query_name]
                    stats['count'] += 1
                    stats['total_time'] += execution_time
                    stats['avg_time'] = stats['total_time'] / stats['count']
                    stats['max_time'] = max(stats['max_time'], execution_time)
                    stats['min_time'] = min(stats['min_time'], execution_time)
                    
                    # 느린 쿼리 로깅
                    if execution_time > self.slow_query_threshold:
                        logger.warning(f"느린 쿼리 감지: {query_name} ({execution_time:.2f}초)")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"쿼리 실행 실패: {query_name} ({execution_time:.2f}초) - {e}")
                    raise
            return wrapper
        return decorator
    
    def optimize_database_connections(self):
        """데이터베이스 연결 최적화"""
        try:
            # 연결 풀 설정 최적화
            engine = db.engine
            engine.pool_size = 20
            engine.max_overflow = 30
            engine.pool_timeout = 30
            engine.pool_recycle = 3600
            
            logger.info("데이터베이스 연결 풀 최적화 완료")
            return True
        except Exception as e:
            logger.error(f"데이터베이스 연결 최적화 실패: {e}")
            return False
    
    def create_database_indexes(self):
        """데이터베이스 인덱스 생성"""
        try:
            # 자주 사용되는 쿼리를 위한 인덱스
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                "CREATE INDEX IF NOT EXISTS idx_brands_name ON brands(name)",
                "CREATE INDEX IF NOT EXISTS idx_branches_brand_id ON branches(brand_id)",
                "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)"
            ]
            
            for index_sql in indexes:
                db.session.execute(text(index_sql))
            
            db.session.commit()
            logger.info("데이터베이스 인덱스 생성 완료")
            return True
        except Exception as e:
            logger.error(f"인덱스 생성 실패: {e}")
            db.session.rollback()
            return False
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        return {
            'query_stats': self.query_stats,
            'cache_hit_ratio': self.cache_hit_ratio,
            'connection_pool_stats': self.connection_pool_stats,
            'slow_queries': [
                name for name, stats in self.query_stats.items()
                if stats['avg_time'] > self.slow_query_threshold
            ],
            'optimization_recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """최적화 권장사항 생성"""
        recommendations = []
        
        # 느린 쿼리 권장사항
        slow_queries = [
            name for name, stats in self.query_stats.items()
            if stats['avg_time'] > self.slow_query_threshold
        ]
        
        if slow_queries:
            recommendations.append(f"느린 쿼리 최적화 필요: {', '.join(slow_queries)}")
        
        # 캐시 히트율 권장사항
        if self.cache_hit_ratio < 0.7:
            recommendations.append("캐시 히트율 개선 필요 (현재: {:.1%})".format(self.cache_hit_ratio))
        
        # 연결 풀 권장사항
        if self.connection_pool_stats.get('overflow', 0) > 10:
            recommendations.append("데이터베이스 연결 풀 크기 증가 고려")
        
        return recommendations


# 전역 성능 최적화 인스턴스
performance_optimizer = PerformanceOptimizer()


def optimize_database_queries():
    """데이터베이스 쿼리 최적화 실행"""
    optimizer = PerformanceOptimizer()
    
    # 연결 풀 최적화
    optimizer.optimize_database_connections()
    
    # 인덱스 생성
    optimizer.create_database_indexes()
    
    logger.info("데이터베이스 최적화 완료")


def get_query_performance_stats():
    """쿼리 성능 통계 조회"""
    return performance_optimizer.get_performance_report() 