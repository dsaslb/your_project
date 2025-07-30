"""
데이터베이스 쿼리 최적화 시스템
성능 향상을 위한 쿼리 최적화 및 캐싱
"""

import logging
import time
import functools
from typing import Dict, List, Any, Optional
from collections import defaultdict
import redis
import json

logger = logging.getLogger(__name__)

class QueryOptimizer:
    def __init__(self):
        self.query_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'avg_time': 0,
            'slow_queries': []
        })
        self.cache = {}
        self.slow_query_threshold = 1.0  # 1초 이상 걸리는 쿼리
        
    def optimize_query(self, query_func):
        """쿼리 함수를 최적화하는 데코레이터"""
        @functools.wraps(query_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            query_name = query_func.__name__
            
            try:
                # 캐시 확인
                cache_key = self._generate_cache_key(query_name, args, kwargs)
                if cache_key in self.cache:
                    logger.info(f"캐시 히트: {query_name}")
                    return self.cache[cache_key]
                
                # 쿼리 실행
                result = query_func(*args, **kwargs)
                
                # 실행 시간 측정
                execution_time = time.time() - start_time
                
                # 통계 업데이트
                self._update_stats(query_name, execution_time)
                
                # 캐시 저장
                self.cache[cache_key] = result
                
                # 느린 쿼리 로깅
                if execution_time > self.slow_query_threshold:
                    logger.warning(f"느린 쿼리 감지: {query_name} ({execution_time:.2f}초)")
                
                return result
                
            except Exception as e:
                logger.error(f"쿼리 실행 오류: {query_name} - {str(e)}")
                raise
                
        return wrapper
    
    def _generate_cache_key(self, query_name: str, args: tuple, kwargs: dict) -> str:
        """캐시 키 생성"""
        key_data = {
            'query': query_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        return json.dumps(key_data, sort_keys=True)
    
    def _update_stats(self, query_name: str, execution_time: float):
        """쿼리 통계 업데이트"""
        stats = self.query_stats[query_name]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        
        if execution_time > self.slow_query_threshold:
            stats['slow_queries'].append({
                'time': execution_time,
                'timestamp': time.time()
            })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        report = {
            'total_queries': sum(stats['count'] for stats in self.query_stats.values()),
            'slow_queries': sum(len(stats['slow_queries']) for stats in self.query_stats.values()),
            'queries': {}
        }
        
        for query_name, stats in self.query_stats.items():
            report['queries'][query_name] = {
                'count': stats['count'],
                'avg_time': stats['avg_time'],
                'total_time': stats['total_time'],
                'slow_count': len(stats['slow_queries'])
            }
        
        return report
    
    def clear_cache(self):
        """캐시 초기화"""
        self.cache.clear()
        logger.info("쿼리 캐시 초기화 완료")

# 전역 인스턴스
query_optimizer = QueryOptimizer()
