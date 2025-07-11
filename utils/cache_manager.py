import time
import json
import hashlib
from typing import Any, Optional, Dict, List
from functools import wraps
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """고성능 캐싱 시스템"""
    
    def __init__(self):
        self._cache = {}
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        self._default_ttl = 300  # 5분 기본 TTL
        
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        if key in self._cache:
            item = self._cache[key]
            if item['expires_at'] > datetime.now():
                self._cache_stats['hits'] += 1
                return item['data']
            else:
                # 만료된 항목 제거
                del self._cache[key]
        
        self._cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """캐시에 데이터 저장"""
        ttl = ttl or self._default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            'data': data,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        self._cache_stats['sets'] += 1
        
        # 캐시 크기 제한 (메모리 보호)
        if len(self._cache) > 1000:
            self._cleanup_expired()
    
    def delete(self, key: str) -> bool:
        """캐시에서 데이터 삭제"""
        if key in self._cache:
            del self._cache[key]
            self._cache_stats['deletes'] += 1
            return True
        return False
    
    def clear(self) -> None:
        """전체 캐시 삭제"""
        self._cache.clear()
        logger.info("캐시가 완전히 삭제되었습니다.")
    
    def _cleanup_expired(self) -> None:
        """만료된 캐시 항목 정리"""
        now = datetime.now()
        expired_keys = [
            key for key, item in self._cache.items()
            if item['expires_at'] <= now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"{len(expired_keys)}개의 만료된 캐시 항목이 정리되었습니다.")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = (self._cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self._cache),
            'hits': self._cache_stats['hits'],
            'misses': self._cache_stats['misses'],
            'sets': self._cache_stats['sets'],
            'deletes': self._cache_stats['deletes'],
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def invalidate_pattern(self, pattern: str) -> int:
        """패턴에 맞는 캐시 항목들 삭제"""
        deleted_count = 0
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        
        for key in keys_to_delete:
            del self._cache[key]
            deleted_count += 1
        
        logger.info(f"패턴 '{pattern}'에 맞는 {deleted_count}개의 캐시 항목이 삭제되었습니다.")
        return deleted_count

# 전역 캐시 인스턴스
cache_manager = CacheManager()

def cached(prefix: str, ttl: Optional[int] = None):
    """캐시 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # 캐시에서 조회
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def cache_invalidate(prefix: str):
    """캐시 무효화 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_manager.invalidate_pattern(prefix)
            return result
        return wrapper
    return decorator

# 특정 기능별 캐시 헬퍼 함수들
class CacheHelpers:
    """캐시 헬퍼 클래스"""
    
    @staticmethod
    def user_data_key(user_id: int) -> str:
        return f"user:{user_id}:data"
    
    @staticmethod
    def attendance_data_key(user_id: int, date: str) -> str:
        return f"attendance:{user_id}:{date}"
    
    @staticmethod
    def dashboard_stats_key(branch_id: Optional[int] = None) -> str:
        return f"dashboard:stats:{branch_id or 'all'}"
    
    @staticmethod
    def notification_count_key(user_id: int) -> str:
        return f"notification:count:{user_id}"
    
    @staticmethod
    def ai_analysis_key(analysis_type: str, params: Dict) -> str:
        param_str = json.dumps(params, sort_keys=True)
        return f"ai:analysis:{analysis_type}:{hashlib.md5(param_str.encode()).hexdigest()}" 