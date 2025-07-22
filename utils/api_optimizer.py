"""
API 성능 최적화 도구
응답 캐싱, 쿼리 최적화, 압축
"""

import logging
import time
import json
import gzip
import hashlib
from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
import redis
from flask import request, Response, g
import sqlalchemy as sa
from sqlalchemy.orm import Query
from collections import defaultdict

logger = logging.getLogger(__name__)

class APIOptimizer:
    """API 성능 최적화 관리자"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache_enabled = True
        self.compression_enabled = True
        self.cache_ttl = 3600  # 1시간
        self.max_cache_size = 10 * 1024 * 1024  # 10MB
        
        # 캐시 통계
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0
        }
    
    def cache_response(self, ttl: int = None, key_prefix: str = "", 
                      condition: Callable = None) -> Callable:
        """응답 캐싱 데코레이터"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.cache_enabled:
                    return func(*args, **kwargs)
                
                # 캐시 키 생성
                cache_key = self._generate_cache_key(func, args, kwargs, key_prefix)
                
                # 조건 체크
                if condition and not condition(*args, **kwargs):
                    return func(*args, **kwargs)
                
                # 캐시에서 조회
                cached_response = self._get_cached_response(cache_key)
                if cached_response is not None:
                    self.cache_stats['hits'] += 1
                    return cached_response
                
                # 함수 실행
                start_time = time.time()
                response = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 응답 캐시
                self._cache_response(cache_key, response, ttl or self.cache_ttl)
                
                # 성능 로깅
                logger.debug(f"API 호출: {func.__name__}, 시간: {execution_time:.3f}s")
                
                return response
            
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func: Callable, args: tuple, kwargs: dict, 
                           key_prefix: str) -> str:
        """캐시 키 생성"""
        try:
            # 함수 정보
            func_info = f"{func.__module__}.{func.__name__}"
            
            # 요청 정보
            request_info = {
                'args': args,
                'kwargs': kwargs,
                'query_params': dict(request.args),
                'headers': dict(request.headers),
                'user_id': getattr(g, 'user_id', None)
            }
            
            # 해시 생성
            key_data = f"{key_prefix}:{func_info}:{json.dumps(request_info, sort_keys=True)}"
            return f"api_cache:{hashlib.md5(key_data.encode()).hexdigest()}"
            
        except Exception as e:
            logger.error(f"캐시 키 생성 실패: {e}")
            return f"api_cache:{func.__name__}:{int(time.time())}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[Response]:
        """캐시된 응답 조회"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data is None:
                self.cache_stats['misses'] += 1
                return None
            
            # 압축 해제
            if self.compression_enabled:
                cached_data = gzip.decompress(cached_data)
            
            # JSON 역직렬화
            response_data = json.loads(cached_data.decode('utf-8'))
            
            # Response 객체 재생성
            response = Response(
                response_data['data'],
                status=response_data['status'],
                headers=response_data['headers']
            )
            
            return response
            
        except Exception as e:
            logger.error(f"캐시된 응답 조회 실패: {e}")
            return None
    
    def _cache_response(self, cache_key: str, response: Response, ttl: int):
        """응답 캐시"""
        try:
            # Response 객체 직렬화
            response_data = {
                'data': response.get_data(as_text=True),
                'status': response.status_code,
                'headers': dict(response.headers)
            }
            
            # JSON 직렬화
            json_data = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
            
            # 압축
            if self.compression_enabled and len(json_data) > 1024:
                json_data = gzip.compress(json_data)
            
            # Redis에 저장
            self.redis_client.setex(cache_key, ttl, json_data)
            self.cache_stats['sets'] += 1
            
        except Exception as e:
            logger.error(f"응답 캐시 실패: {e}")
    
    def invalidate_cache(self, pattern: str) -> int:
        """캐시 무효화"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.cache_stats['invalidations'] += deleted
                logger.info(f"캐시 무효화: {pattern}, {deleted}개 키 삭제")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"캐시 무효화 실패: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """캐시 통계 조회"""
        try:
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.cache_stats,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
            
        except Exception as e:
            logger.error(f"캐시 통계 조회 실패: {e}")
            return {}

class QueryOptimizer:
    """쿼리 최적화"""
    
    def __init__(self):
        self.query_stats = {
            'total_queries': 0,
            'slow_queries': 0,
            'optimized_queries': 0
        }
    
    def optimize_query(self, query: Query, max_results: int = 1000) -> Query:
        """쿼리 최적화"""
        try:
            self.query_stats['total_queries'] += 1
            
            # 결과 수 제한
            if hasattr(query, 'limit') and not query._limit:
                query = query.limit(max_results)
            
            # 불필요한 컬럼 제거
            if hasattr(query, 'with_entities'):
                # 필요한 컬럼만 선택하도록 최적화
                pass
            
            # 인덱스 힌트 추가
            # query = query.with_hint(table, 'USE INDEX (idx_column)')
            
            self.query_stats['optimized_queries'] += 1
            return query
            
        except Exception as e:
            logger.error(f"쿼리 최적화 실패: {e}")
            return query
    
    def paginate_query(self, query: Query, page: int = 1, per_page: int = 20) -> Dict:
        """쿼리 페이지네이션"""
        try:
            # 전체 개수 조회
            total = query.count()
            
            # 페이지네이션 적용
            offset = (page - 1) * per_page
            paginated_query = query.offset(offset).limit(per_page)
            
            # 결과 조회
            results = paginated_query.all()
            
            return {
                'data': results,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page,
                    'has_next': page * per_page < total,
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            logger.error(f"쿼리 페이지네이션 실패: {e}")
            return {'data': [], 'pagination': {}}
    
    def batch_query(self, model_class, ids: List[int], batch_size: int = 100) -> List:
        """배치 쿼리"""
        try:
            results = []
            
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                batch_results = model_class.query.filter(
                    model_class.id.in_(batch_ids)
                ).all()
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            logger.error(f"배치 쿼리 실패: {e}")
            return []
    
    def get_query_stats(self) -> Dict:
        """쿼리 통계 조회"""
        return self.query_stats.copy()

class ResponseOptimizer:
    """응답 최적화"""
    
    def __init__(self):
        self.compression_threshold = 1024  # 1KB 이상 압축
    
    def optimize_response(self, data: Any, compress: bool = True) -> Response:
        """응답 최적화"""
        try:
            # JSON 직렬화
            if isinstance(data, (dict, list)):
                json_data = json.dumps(data, ensure_ascii=False, default=str)
            else:
                json_data = str(data)
            
            # 압축 여부 결정
            should_compress = compress and len(json_data.encode('utf-8')) > self.compression_threshold
            
            if should_compress:
                compressed_data = gzip.compress(json_data.encode('utf-8'))
                response = Response(compressed_data)
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(compressed_data)
            else:
                response = Response(json_data)
                response.headers['Content-Length'] = len(json_data.encode('utf-8'))
            
            # 공통 헤더 설정
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['Cache-Control'] = 'public, max-age=300'
            response.headers['X-Response-Optimized'] = 'true'
            
            if should_compress:
                response.headers['X-Compressed'] = 'true'
            
            return response
            
        except Exception as e:
            logger.error(f"응답 최적화 실패: {e}")
            return Response(str(data), status=500)
    
    def stream_response(self, data_generator: Callable, chunk_size: int = 8192) -> Response:
        """스트리밍 응답"""
        try:
            def generate():
                for chunk in data_generator():
                    if isinstance(chunk, str):
                        yield chunk.encode('utf-8')
                    else:
                        yield chunk
            
            response = Response(generate())
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['Transfer-Encoding'] = 'chunked'
            response.headers['X-Streaming'] = 'true'
            
            return response
            
        except Exception as e:
            logger.error(f"스트리밍 응답 생성 실패: {e}")
            return Response('{"error": "Streaming failed"}', status=500)

class APIMonitor:
    """API 모니터링"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'error_count': 0,
            'last_request': 0
        })
    
    def monitor_endpoint(self, endpoint: str):
        """엔드포인트 모니터링 데코레이터"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # 성공 통계 업데이트
                    self._update_endpoint_stats(endpoint, execution_time, False)
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    # 에러 통계 업데이트
                    self._update_endpoint_stats(endpoint, execution_time, True)
                    
                    raise
            
            return wrapper
        return decorator
    
    def _update_endpoint_stats(self, endpoint: str, execution_time: float, is_error: bool):
        """엔드포인트 통계 업데이트"""
        try:
            stats_key = f"api_stats:{endpoint}"
            
            # Redis에서 현재 통계 조회
            current_stats = self.redis_client.hgetall(stats_key)
            
            # 통계 업데이트
            count = int(current_stats.get('count', 0)) + 1
            total_time = float(current_stats.get('total_time', 0)) + execution_time
            error_count = int(current_stats.get('error_count', 0)) + (1 if is_error else 0)
            last_request = time.time()
            
            # Redis에 저장
            self.redis_client.hset(stats_key, mapping={
                'count': count,
                'total_time': total_time,
                'error_count': error_count,
                'last_request': last_request,
                'avg_time': total_time / count if count > 0 else 0
            })
            
            # 만료 시간 설정 (24시간)
            self.redis_client.expire(stats_key, 86400)
            
        except Exception as e:
            logger.error(f"엔드포인트 통계 업데이트 실패: {e}")
    
    def get_endpoint_stats(self, endpoint: str = None) -> Dict:
        """엔드포인트 통계 조회"""
        try:
            if endpoint:
                # 특정 엔드포인트 통계
                stats_key = f"api_stats:{endpoint}"
                stats = self.redis_client.hgetall(stats_key)
                
                if stats:
                    return {
                        'endpoint': endpoint,
                        'count': int(stats.get('count', 0)),
                        'total_time': float(stats.get('total_time', 0)),
                        'error_count': int(stats.get('error_count', 0)),
                        'avg_time': float(stats.get('avg_time', 0)),
                        'last_request': float(stats.get('last_request', 0))
                    }
                return {}
            else:
                # 모든 엔드포인트 통계
                all_stats = {}
                pattern = "api_stats:*"
                
                for key in self.redis_client.scan_iter(match=pattern):
                    endpoint = key.decode('utf-8').replace('api_stats:', '')
                    stats = self.redis_client.hgetall(key)
                    
                    if stats:
                        all_stats[endpoint] = {
                            'count': int(stats.get('count', 0)),
                            'total_time': float(stats.get('total_time', 0)),
                            'error_count': int(stats.get('error_count', 0)),
                            'avg_time': float(stats.get('avg_time', 0)),
                            'last_request': float(stats.get('last_request', 0))
                        }
                
                return all_stats
                
        except Exception as e:
            logger.error(f"엔드포인트 통계 조회 실패: {e}")
            return {}

# 전역 API 최적화 인스턴스들
api_optimizer = None
query_optimizer = None
response_optimizer = None
api_monitor = None

def init_api_optimizer(redis_client: redis.Redis):
    """API 최적화 도구 초기화"""
    global api_optimizer, query_optimizer, response_optimizer, api_monitor
    
    api_optimizer = APIOptimizer(redis_client)
    query_optimizer = QueryOptimizer()
    response_optimizer = ResponseOptimizer()
    api_monitor = APIMonitor(redis_client)
    
    logger.info("API 최적화 도구 초기화 완료")

def get_api_optimizer() -> Optional[APIOptimizer]:
    """API 최적화 관리자 반환"""
    return api_optimizer

def get_query_optimizer() -> Optional[QueryOptimizer]:
    """쿼리 최적화 관리자 반환"""
    return query_optimizer

def get_response_optimizer() -> Optional[ResponseOptimizer]:
    """응답 최적화 관리자 반환"""
    return response_optimizer

def get_api_monitor() -> Optional[APIMonitor]:
    """API 모니터 반환"""
    return api_monitor 