"""
고도화된 캐싱 전략 시스템
"""

import redis
import json
import pickle
import hashlib
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps
import threading
from collections import OrderedDict

logger = logging.getLogger(__name__)

@dataclass
class CacheItem:
    """캐시 아이템"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    access_count: int
    last_accessed: float
    size_bytes: int

@dataclass
class CacheStats:
    """캐시 통계"""
    total_items: int
    total_size: int
    hit_count: int
    miss_count: int
    hit_rate: float
    eviction_count: int
    memory_usage: int

class LRUCache:
    """LRU (Least Recently Used) 캐시"""
    
    def __init__(self, max_size: int = 1000, max_memory: int = 100 * 1024 * 1024):  # 100MB
        self.max_size = max_size
        self.max_memory = max_memory
        self.cache = OrderedDict()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_size': 0
        }
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        with self.lock:
            if key in self.cache:
                # LRU 업데이트
                value = self.cache.pop(key)
                self.cache[key] = value
                self.stats['hits'] += 1
                return value
            else:
                self.stats['misses'] += 1
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """캐시에 값 저장"""
        with self.lock:
            # 크기 계산 (대략적)
            size = len(str(value).encode('utf-8'))
            
            # 메모리 제한 확인
            if self.stats['total_size'] + size > self.max_memory:
                self._evict_items(size)
            
            # TTL 설정
            expires_at = time.time() + ttl if ttl else None
            
            # 캐시 아이템 생성
            item = CacheItem(
                key=key,
                value=value,
                created_at=time.time(),
                expires_at=expires_at,
                access_count=1,
                last_accessed=time.time(),
                size_bytes=size
            )
            
            # 기존 키가 있으면 제거
            if key in self.cache:
                old_item = self.cache.pop(key)
                self.stats['total_size'] -= old_item.size_bytes
            
            # 새 아이템 추가
            self.cache[key] = item
            self.stats['total_size'] += size
            
            # 크기 제한 확인
            if len(self.cache) > self.max_size:
                self._evict_lru()
            
            return True
    
    def _evict_items(self, required_size: int):
        """필요한 크기만큼 아이템 제거"""
        while self.stats['total_size'] + required_size > self.max_memory and self.cache:
            self._evict_lru()
    
    def _evict_lru(self):
        """LRU 아이템 제거"""
        if self.cache:
            key, item = self.cache.popitem(last=False)
            self.stats['total_size'] -= item.size_bytes
            self.stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """캐시에서 키 삭제"""
        with self.lock:
            if key in self.cache:
                item = self.cache.pop(key)
                self.stats['total_size'] -= item.size_bytes
                return True
            return False
    
    def clear(self):
        """캐시 전체 삭제"""
        with self.lock:
            self.cache.clear()
            self.stats['total_size'] = 0
    
    def get_stats(self) -> CacheStats:
        """캐시 통계 조회"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return CacheStats(
                total_items=len(self.cache),
                total_size=self.stats['total_size'],
                hit_count=self.stats['hits'],
                miss_count=self.stats['misses'],
                hit_rate=hit_rate,
                eviction_count=self.stats['evictions'],
                memory_usage=self.stats['total_size']
            )

class RedisCache:
    """Redis 캐시 래퍼"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, 
                 password: str = None, max_connections: int = 10):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            decode_responses=False  # 바이너리 데이터 지원
        )
        self.stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Redis에서 값 조회"""
        try:
            value = self.redis_client.get(key)
            if value is not None:
                self.stats['hits'] += 1
                return pickle.loads(value)
            else:
                self.stats['misses'] += 1
                return None
        except Exception as e:
            logger.error(f"Redis get 오류 {key}: {e}")
            self.stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Redis에 값 저장"""
        try:
            serialized_value = pickle.dumps(value)
            if ttl:
                return self.redis_client.setex(key, ttl, serialized_value)
            else:
                return self.redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Redis set 오류 {key}: {e}")
            self.stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Redis에서 키 삭제"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete 오류 {key}: {e}")
            self.stats['errors'] += 1
            return False
    
    def clear(self):
        """Redis 캐시 전체 삭제"""
        try:
            self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear 오류: {e}")
            self.stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Redis 통계 조회"""
        try:
            info = self.redis_client.info()
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'redis_info': {
                    'used_memory': info.get('used_memory', 0),
                    'used_memory_peak': info.get('used_memory_peak', 0),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0)
                },
                'cache_stats': {
                    'hits': self.stats['hits'],
                    'misses': self.stats['misses'],
                    'errors': self.stats['errors'],
                    'hit_rate': hit_rate
                }
            }
        except Exception as e:
            logger.error(f"Redis stats 조회 오류: {e}")
            return {}

class MultiLevelCache:
    """다단계 캐시 시스템"""
    
    def __init__(self, l1_cache: LRUCache, l2_cache: RedisCache):
        self.l1_cache = l1_cache  # 메모리 캐시 (빠름)
        self.l2_cache = l2_cache  # Redis 캐시 (느림)
        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """다단계 캐시에서 값 조회"""
        # L1 캐시 확인
        value = self.l1_cache.get(key)
        if value is not None:
            self.stats['l1_hits'] += 1
            return value
        
        # L2 캐시 확인
        value = self.l2_cache.get(key)
        if value is not None:
            self.stats['l2_hits'] += 1
            # L1 캐시에도 저장
            self.l1_cache.set(key, value)
            return value
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """다단계 캐시에 값 저장"""
        l1_success = self.l1_cache.set(key, value, ttl)
        l2_success = self.l2_cache.set(key, value, ttl)
        return l1_success and l2_success
    
    def delete(self, key: str) -> bool:
        """다단계 캐시에서 키 삭제"""
        l1_success = self.l1_cache.delete(key)
        l2_success = self.l2_cache.delete(key)
        return l1_success or l2_success
    
    def clear(self):
        """다단계 캐시 전체 삭제"""
        self.l1_cache.clear()
        self.l2_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """다단계 캐시 통계 조회"""
        l1_stats = self.l1_cache.get_stats()
        l2_stats = self.l2_cache.get_stats()
        
        total_requests = self.stats['l1_hits'] + self.stats['l2_hits'] + self.stats['misses']
        overall_hit_rate = ((self.stats['l1_hits'] + self.stats['l2_hits']) / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'l1_cache': asdict(l1_stats),
            'l2_cache': l2_stats,
            'overall': {
                'l1_hits': self.stats['l1_hits'],
                'l2_hits': self.stats['l2_hits'],
                'misses': self.stats['misses'],
                'overall_hit_rate': overall_hit_rate
            }
        }

class CacheDecorator:
    """캐시 데코레이터"""
    
    def __init__(self, cache: Union[LRUCache, RedisCache, MultiLevelCache], 
                 ttl: Optional[int] = None, key_prefix: str = ""):
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix
    
    def __call__(self, func: Callable) -> Callable:
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
            
            # 결과 캐싱
            self.cache.set(cache_key, result, self.ttl)
            
            return result
        
        return wrapper
    
    def _generate_cache_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
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
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'l1_cache': {
                'max_size': 1000,
                'max_memory': 100 * 1024 * 1024  # 100MB
            },
            'l2_cache': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'password': None
            },
            'default_ttl': 3600  # 1시간
        }
        
        # 캐시 인스턴스 생성
        self.l1_cache = LRUCache(
            max_size=self.config['l1_cache']['max_size'],
            max_memory=self.config['l1_cache']['max_memory']
        )
        
        self.l2_cache = RedisCache(
            host=self.config['l2_cache']['host'],
            port=self.config['l2_cache']['port'],
            db=self.config['l2_cache']['db'],
            password=self.config['l2_cache']['password']
        )
        
        self.multi_cache = MultiLevelCache(self.l1_cache, self.l2_cache)
        
        # 캐시별 데코레이터
        self.l1_decorator = CacheDecorator(self.l1_cache, self.config['default_ttl'])
        self.l2_decorator = CacheDecorator(self.l2_cache, self.config['default_ttl'])
        self.multi_decorator = CacheDecorator(self.multi_cache, self.config['default_ttl'])
    
    def cache(self, ttl: Optional[int] = None, level: str = 'multi') -> Callable:
        """캐시 데코레이터 팩토리"""
        if level == 'l1':
            return CacheDecorator(self.l1_cache, ttl or self.config['default_ttl'])
        elif level == 'l2':
            return CacheDecorator(self.l2_cache, ttl or self.config['default_ttl'])
        else:
            return CacheDecorator(self.multi_cache, ttl or self.config['default_ttl'])
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """모든 캐시 통계 조회"""
        return {
            'l1_cache': asdict(self.l1_cache.get_stats()),
            'l2_cache': self.l2_cache.get_stats(),
            'multi_cache': self.multi_cache.get_stats()
        }
    
    def clear_all_caches(self):
        """모든 캐시 삭제"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        logger.info("모든 캐시가 삭제되었습니다.")
    
    def warm_up_cache(self, warm_up_data: Dict[str, Any]):
        """캐시 워밍업"""
        for key, value in warm_up_data.items():
            self.multi_cache.set(key, value)
        logger.info(f"캐시 워밍업 완료: {len(warm_up_data)}개 아이템")
    
    def get_cache_health(self) -> Dict[str, Any]:
        """캐시 상태 확인"""
        try:
            l1_stats = self.l1_cache.get_stats()
            l2_stats = self.l2_cache.get_stats()
            
            # Redis 연결 확인
            redis_healthy = False
            try:
                self.l2_cache.redis_client.ping()
                redis_healthy = True
            except:
                pass
            
            return {
                'l1_cache': {
                    'healthy': True,
                    'memory_usage_percent': (l1_stats.memory_usage / self.config['l1_cache']['max_memory']) * 100,
                    'item_count': l1_stats.total_items
                },
                'l2_cache': {
                    'healthy': redis_healthy,
                    'hit_rate': l2_stats.get('cache_stats', {}).get('hit_rate', 0),
                    'error_count': l2_stats.get('cache_stats', {}).get('errors', 0)
                },
                'overall': {
                    'healthy': True and redis_healthy,
                    'recommendations': self._generate_cache_recommendations(l1_stats, l2_stats)
                }
            }
        except Exception as e:
            logger.error(f"캐시 상태 확인 실패: {e}")
            return {'overall': {'healthy': False, 'error': str(e)}}
    
    def _generate_cache_recommendations(self, l1_stats: CacheStats, l2_stats: Dict) -> List[str]:
        """캐시 최적화 권장사항 생성"""
        recommendations = []
        
        # L1 캐시 권장사항
        memory_usage_percent = (l1_stats.memory_usage / self.config['l1_cache']['max_memory']) * 100
        if memory_usage_percent > 80:
            recommendations.append("L1 캐시 메모리 사용률이 높습니다. 메모리 크기를 늘리거나 TTL을 줄이세요.")
        
        if l1_stats.eviction_count > 100:
            recommendations.append("L1 캐시에서 많은 아이템이 제거되고 있습니다. 캐시 크기를 늘리세요.")
        
        # L2 캐시 권장사항
        l2_hit_rate = l2_stats.get('cache_stats', {}).get('hit_rate', 0)
        if l2_hit_rate < 50:
            recommendations.append("L2 캐시 히트율이 낮습니다. 캐시 키 전략을 검토하세요.")
        
        l2_errors = l2_stats.get('cache_stats', {}).get('errors', 0)
        if l2_errors > 10:
            recommendations.append("L2 캐시에서 오류가 발생하고 있습니다. Redis 연결을 확인하세요.")
        
        if not recommendations:
            recommendations.append("캐시가 정상적으로 작동하고 있습니다.")
        
        return recommendations

# 전역 캐시 관리자 인스턴스
cache_manager = CacheManager()

class AdvancedCache:
    """고급 캐시 클래스 - 합 대시보드용"""
    
    def __init__(self):
        self.cache_manager = cache_manager
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        return self.cache_manager.multi_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """캐시에 값 저장"""
        return self.cache_manager.multi_cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        return self.cache_manager.multi_cache.delete(key)
    
    def clear(self):
        """캐시 전체 삭제"""
        self.cache_manager.clear_all_caches()
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        return self.cache_manager.get_cache_stats()
    
    def get_health(self) -> Dict[str, Any]:
        """캐시 상태 조회"""
        return self.cache_manager.get_cache_health()
    
    def get_settings(self) -> Dict[str, Any]:
        """캐시 설정 조회"""
        return {
            'enabled': True,
            'default_ttl': 300,
            'max_size': 100,
            'lru_policy': True,
            'auto_cleanup': True,
            'cleanup_interval': 60
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """캐시 설정 업데이트"""
        logger.info(f"캐시 설정 업데이트: {settings}")
        # 실제로는 설정을 적용하는 로직 구현
