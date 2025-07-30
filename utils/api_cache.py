"""
API 응답 캐싱 시스템
Redis를 활용한 고성능 캐싱
"""

import json
import hashlib
import time
import logging
from typing import Any, Optional, Dict
from functools import wraps
import redis

logger = logging.getLogger(__name__)

class APICache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("Redis 캐시 연결 성공")
        except Exception as e:
            logger.warning(f"Redis 연결 실패, 메모리 캐시 사용: {e}")
            self.redis_client = None
            self.memory_cache = {}
    
    def cache_response(self, ttl: int = 300):
        """API 응답 캐싱 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 캐시 키 생성
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # 캐시에서 응답 확인
                cached_response = self._get_cache(cache_key)
                if cached_response is not None:
                    logger.info(f"캐시 히트: {func.__name__}")
                    return cached_response
                
                # 원본 함수 실행
                response = func(*args, **kwargs)
                
                # 응답 캐싱
                self._set_cache(cache_key, response, ttl)
                
                return response
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """캐시 키 생성"""
        key_data = {
            'func': func_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"api_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        try:
            if self.redis_client:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)
            else:
                if key in self.memory_cache:
                    data, expiry = self.memory_cache[key]
                    if time.time() < expiry:
                        return data
                    else:
                        del self.memory_cache[key]
        except Exception as e:
            logger.error(f"캐시 조회 오류: {e}")
        return None
    
    def _set_cache(self, key: str, data: Any, ttl: int):
        """캐시에 데이터 저장"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(data))
            else:
                self.memory_cache[key] = (data, time.time() + ttl)
        except Exception as e:
            logger.error(f"캐시 저장 오류: {e}")
    
    def invalidate_cache(self, pattern: str = "*"):
        """캐시 무효화"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(f"api_cache:{pattern}")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"캐시 무효화 완료: {len(keys)}개 키")
            else:
                # 메모리 캐시에서 패턴 매칭으로 삭제
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                logger.info(f"메모리 캐시 무효화 완료: {len(keys_to_delete)}개 키")
        except Exception as e:
            logger.error(f"캐시 무효화 오류: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys("api_cache:*")
                return {
                    'type': 'redis',
                    'total_keys': len(keys),
                    'memory_usage': self.redis_client.info()['used_memory_human']
                }
            else:
                return {
                    'type': 'memory',
                    'total_keys': len(self.memory_cache),
                    'memory_usage': 'N/A'
                }
        except Exception as e:
            logger.error(f"캐시 통계 조회 오류: {e}")
            return {'error': str(e)}

# 전역 인스턴스
api_cache = APICache() 