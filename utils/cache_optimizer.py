"""
캐시 최적화 시스템
Redis 캐시, 메모리 최적화, 캐시 무효화
"""

import logging
import time
import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import redis
from redis.exceptions import RedisError
import pickle
import gzip

logger = logging.getLogger(__name__)

class CacheOptimizer:
    """캐시 최적화 관리자"""
    
    def __init__(self, redis_url: str, compression_enabled: bool = True):
        self.redis_url = redis_url
        self.compression_enabled = compression_enabled
        self.redis_client = redis.from_url(redis_url)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """캐시에서 값 조회"""
        try:
            start_time = time.time()
            value = self.redis_client.get(key)
            
            if value is not None:
                # 압축 해제
                if self.compression_enabled:
                    value = self._decompress(value)
                
                # 역직렬화
                value = self._deserialize(value)
                
                self.cache_stats['hits'] += 1
                logger.debug(f"Cache HIT: {key} ({(time.time() - start_time) * 1000:.2f}ms)")
                return value
            else:
                self.cache_stats['misses'] += 1
                logger.debug(f"Cache MISS: {key}")
                return default
                
        except RedisError as e:
            logger.error(f"캐시 조회 실패: {e}")
            return default
    
    def set(self, key: str, value: Any, timeout: int = 3600, compress: bool = None) -> bool:
        """캐시에 값 저장"""
        try:
            start_time = time.time()
            
            # 직렬화
            serialized_value = self._serialize(value)
            
            # 압축
            if compress is None:
                compress = self.compression_enabled
            
            if compress and len(serialized_value) > 1024:  # 1KB 이상만 압축
                serialized_value = self._compress(serialized_value)
            
            # Redis에 저장
            result = self.redis_client.setex(key, timeout, serialized_value)
            
            if result:
                self.cache_stats['sets'] += 1
                logger.debug(f"Cache SET: {key} ({(time.time() - start_time) * 1000:.2f}ms)")
            
            return result
            
        except RedisError as e:
            logger.error(f"캐시 저장 실패: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        try:
            result = self.redis_client.delete(key)
            if result:
                self.cache_stats['deletes'] += 1
                logger.debug(f"Cache DELETE: {key}")
            return bool(result)
            
        except RedisError as e:
            logger.error(f"캐시 삭제 실패: {e}")
            return False
    
    def mget(self, keys: List[str]) -> Dict[str, Any]:
        """여러 키의 값을 한 번에 조회"""
        try:
            start_time = time.time()
            values = self.redis_client.mget(keys)
            
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    # 압축 해제
                    if self.compression_enabled:
                        value = self._decompress(value)
                    
                    # 역직렬화
                    value = self._deserialize(value)
                    result[key] = value
                    self.cache_stats['hits'] += 1
                else:
                    self.cache_stats['misses'] += 1
            
            logger.debug(f"Cache MGET: {len(keys)} keys ({(time.time() - start_time) * 1000:.2f}ms)")
            return result
            
        except RedisError as e:
            logger.error(f"캐시 다중 조회 실패: {e}")
            return {}
    
    def mset(self, data: Dict[str, Any], timeout: int = 3600) -> bool:
        """여러 키의 값을 한 번에 저장"""
        try:
            start_time = time.time()
            
            # 직렬화 및 압축
            serialized_data = {}
            for key, value in data.items():
                serialized_value = self._serialize(value)
                
                if self.compression_enabled and len(serialized_value) > 1024:
                    serialized_value = self._compress(serialized_value)
                
                serialized_data[key] = serialized_value
            
            # Redis에 저장
            result = self.redis_client.mset(serialized_data)
            
            # 만료 시간 설정
            if result:
                for key in data.keys():
                    self.redis_client.expire(key, timeout)
                
                self.cache_stats['sets'] += len(data)
                logger.debug(f"Cache MSET: {len(data)} keys ({(time.time() - start_time) * 1000:.2f}ms)")
            
            return result
            
        except RedisError as e:
            logger.error(f"캐시 다중 저장 실패: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """패턴에 맞는 키들을 삭제"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.cache_stats['deletes'] += deleted
                logger.info(f"Cache INVALIDATE: {pattern} ({deleted} keys deleted)")
                return deleted
            return 0
            
        except RedisError as e:
            logger.error(f"캐시 패턴 삭제 실패: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        try:
            # Redis 정보
            info = self.redis_client.info()
            
            # 메모리 사용량
            memory_usage = {
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'used_memory_peak': info.get('used_memory_peak', 0),
                'used_memory_peak_human': info.get('used_memory_peak_human', '0B'),
                'maxmemory': info.get('maxmemory', 0),
                'maxmemory_human': info.get('maxmemory_human', '0B')
            }
            
            # 히트율 계산
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self.cache_stats['hits'],
                'misses': self.cache_stats['misses'],
                'sets': self.cache_stats['sets'],
                'deletes': self.cache_stats['deletes'],
                'hit_rate': round(hit_rate, 2),
                'memory_usage': memory_usage,
                'total_keys': info.get('db0', {}).get('keys', 0)
            }
            
        except RedisError as e:
            logger.error(f"캐시 통계 조회 실패: {e}")
            return {}
    
    def optimize_memory(self) -> Dict[str, Any]:
        """메모리 최적화"""
        try:
            # 메모리 사용량 분석
            info = self.redis_client.info()
            used_memory = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            
            optimization_results = {
                'before_memory': used_memory,
                'before_memory_human': info.get('used_memory_human', '0B'),
                'actions_taken': []
            }
            
            # 만료된 키 정리
            if used_memory > max_memory * 0.8:  # 80% 이상 사용 시
                # LRU 정책으로 오래된 키 삭제
                self.redis_client.memory('purge')
                optimization_results['actions_taken'].append('memory_purge')
            
            # 만료된 키 정리
            expired_keys = self.redis_client.eval("""
                local keys = redis.call('keys', '*')
                local expired = 0
                for i, key in ipairs(keys) do
                    if redis.call('ttl', key) == -1 then
                        redis.call('expire', key, 3600)  -- 기본 만료 시간 설정
                        expired = expired + 1
                    end
                end
                return expired
            """, 0)
            
            if expired_keys > 0:
                optimization_results['actions_taken'].append(f'set_expiry_for_{expired_keys}_keys')
            
            # 최적화 후 메모리 사용량
            info_after = self.redis_client.info()
            optimization_results['after_memory'] = info_after.get('used_memory', 0)
            optimization_results['after_memory_human'] = info_after.get('used_memory_human', '0B')
            optimization_results['memory_saved'] = used_memory - info_after.get('used_memory', 0)
            
            logger.info(f"메모리 최적화 완료: {optimization_results['memory_saved']} bytes saved")
            return optimization_results
            
        except RedisError as e:
            logger.error(f"메모리 최적화 실패: {e}")
            return {}
    
    def _serialize(self, value: Any) -> bytes:
        """값 직렬화"""
        try:
            # JSON 직렬화 시도
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                return json.dumps(value, ensure_ascii=False).encode('utf-8')
            else:
                # Pickle 직렬화
                return pickle.dumps(value)
        except Exception as e:
            logger.error(f"직렬화 실패: {e}")
            return str(value).encode('utf-8')
    
    def _deserialize(self, value: bytes) -> Any:
        """값 역직렬화"""
        try:
            # JSON 역직렬화 시도
            decoded = value.decode('utf-8')
            return json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError):
            try:
                # Pickle 역직렬화
                return pickle.loads(value)
            except Exception as e:
                logger.error(f"역직렬화 실패: {e}")
                return value.decode('utf-8', errors='ignore')
    
    def _compress(self, data: bytes) -> bytes:
        """데이터 압축"""
        try:
            return gzip.compress(data)
        except Exception as e:
            logger.error(f"압축 실패: {e}")
            return data
    
    def _decompress(self, data: bytes) -> bytes:
        """데이터 압축 해제"""
        try:
            return gzip.decompress(data)
        except Exception as e:
            logger.error(f"압축 해제 실패: {e}")
            return data

class CacheDecorator:
    """캐시 데코레이터"""
    
    def __init__(self, cache_optimizer: CacheOptimizer, timeout: int = 3600, key_prefix: str = ""):
        self.cache = cache_optimizer
        self.timeout = timeout
        self.key_prefix = key_prefix
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = self._generate_cache_key(func, args, kwargs)
            
            # 캐시에서 조회
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐시
            self.cache.set(cache_key, result, self.timeout)
            
            return result
        
        return wrapper
    
    def _generate_cache_key(self, func, args, kwargs) -> str:
        """캐시 키 생성"""
        # 함수 정보
        func_info = f"{func.__module__}.{func.__name__}"
        
        # 인자 정보
        args_str = str(args) + str(sorted(kwargs.items()))
        
        # 해시 생성
        key_data = f"{self.key_prefix}:{func_info}:{args_str}"
        return hashlib.md5(key_data.encode()).hexdigest()

class CacheManager:
    """캐시 관리자"""
    
    def __init__(self, redis_url: str):
        self.cache_optimizer = CacheOptimizer(redis_url)
        self.decorators = {}
    
    def cached(self, timeout: int = 3600, key_prefix: str = ""):
        """캐시 데코레이터 생성"""
        return CacheDecorator(self.cache_optimizer, timeout, key_prefix)
    
    def invalidate_user_cache(self, user_id: int):
        """사용자 관련 캐시 무효화"""
        patterns = [
            f"user:{user_id}:*",
            f"brand:*:user:{user_id}:*",
            f"branch:*:user:{user_id}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.cache_optimizer.invalidate_pattern(pattern)
        
        logger.info(f"사용자 캐시 무효화: user_id={user_id}, deleted={total_deleted}")
        return total_deleted
    
    def invalidate_brand_cache(self, brand_id: int):
        """브랜드 관련 캐시 무효화"""
        patterns = [
            f"brand:{brand_id}:*",
            f"branch:*:brand:{brand_id}:*",
            f"employee:*:brand:{brand_id}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.cache_optimizer.invalidate_pattern(pattern)
        
        logger.info(f"브랜드 캐시 무효화: brand_id={brand_id}, deleted={total_deleted}")
        return total_deleted
    
    def invalidate_module_cache(self, module_name: str):
        """모듈 관련 캐시 무효화"""
        pattern = f"module:{module_name}:*"
        deleted = self.cache_optimizer.invalidate_pattern(pattern)
        
        logger.info(f"모듈 캐시 무효화: module={module_name}, deleted={deleted}")
        return deleted
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        return self.cache_optimizer.get_cache_stats()
    
    def optimize_memory(self) -> Dict[str, Any]:
        """메모리 최적화"""
        return self.cache_optimizer.optimize_memory()

# 전역 캐시 관리자 인스턴스
cache_manager = None

def init_cache_manager(redis_url: str):
    """캐시 관리자 초기화"""
    global cache_manager
    cache_manager = CacheManager(redis_url)
    logger.info("캐시 관리자 초기화 완료")

def get_cache_manager() -> Optional[CacheManager]:
    """캐시 관리자 반환"""
    return cache_manager 