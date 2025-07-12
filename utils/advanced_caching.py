#!/usr/bin/env python3
"""
고급 캐싱 시스템
Redis, 메모리 캐시, 파일 캐시를 통합한 다층 캐싱 시스템
"""

import os
import json
import pickle
import hashlib
import logging
from datetime import datetime
from typing import Any, Optional, Dict, List, Callable
from functools import wraps
import threading

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from cachetools import TTLCache  # type: ignore
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False
    # 캐싱 라이브러리 설치 필요: pip install cachetools

logger = logging.getLogger(__name__)

class CacheLevel:
    """캐시 레벨 정의"""
    L1_MEMORY = "l1_memory"      # 메모리 캐시 (가장 빠름)
    L2_REDIS = "l2_redis"        # Redis 캐시 (중간)
    L3_FILE = "l3_file"          # 파일 캐시 (가장 느림)

class CacheStrategy:
    """캐시 전략"""
    WRITE_THROUGH = "write_through"      # 모든 레벨에 즉시 쓰기
    WRITE_BACK = "write_back"           # 지연 쓰기
    WRITE_AROUND = "write_around"       # 캐시 우회
    READ_THROUGH = "read_through"       # 캐시 미스 시 자동 로드

class AdvancedCache:
    """고급 캐싱 시스템"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.l1_cache = None
        self.l2_cache = None
        self.l3_cache = None
        self.stats = {
            'hits': {'l1': 0, 'l2': 0, 'l3': 0},
            'misses': {'l1': 0, 'l2': 0, 'l3': 0},
            'writes': {'l1': 0, 'l2': 0, 'l3': 0},
            'evictions': {'l1': 0, 'l2': 0, 'l3': 0}
        }
        self.lock = threading.RLock()
        
        self._initialize_caches()
    
    def _initialize_caches(self):
        """캐시 초기화"""
        # L1 캐시 (메모리)
        if CACHETOOLS_AVAILABLE:
            maxsize = self.config.get('l1_maxsize', 1000)
            ttl = self.config.get('l1_ttl', 300)  # 5분
            self.l1_cache = TTLCache(maxsize=maxsize, ttl=ttl)
            logger.info(f"L1 캐시 초기화: maxsize={maxsize}, ttl={ttl}s")
        
        # L2 캐시 (Redis)
        if REDIS_AVAILABLE and self.config.get('redis_enabled', True):
            try:
                redis_config = self.config.get('redis', {})
                self.l2_cache = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    password=redis_config.get('password'),
                    decode_responses=False
                )
                # 연결 테스트
                self.l2_cache.ping()
                logger.info("L2 캐시 (Redis) 초기화 완료")
            except Exception as e:
                logger.warning(f"Redis 연결 실패: {e}")
                self.l2_cache = None
        
        # L3 캐시 (파일)
        cache_dir = self.config.get('file_cache_dir', 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        self.l3_cache = FileCache(cache_dir)
        logger.info(f"L3 캐시 (파일) 초기화: {cache_dir}")
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """캐시 키 생성"""
        if namespace:
            key = f"{namespace}:{key}"
        
        # 키 길이 제한 및 해시화
        if len(key) > 250:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{key[:200]}:{key_hash}"
        
        return key
    
    def get(self, key: str, namespace: str = "default", 
            levels: Optional[List[str]] = None) -> Optional[Any]:
        """캐시에서 값 조회"""
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_FILE]
        
        cache_key = self._generate_key(key, namespace)
        
        with self.lock:
            # L1 캐시 조회
            if CacheLevel.L1_MEMORY in levels and self.l1_cache:
                try:
                    value = self.l1_cache.get(cache_key)
                    if value is not None:
                        self.stats['hits']['l1'] += 1
                        logger.debug(f"L1 캐시 히트: {cache_key}")
                        return value
                    else:
                        self.stats['misses']['l1'] += 1
                except Exception as e:
                    logger.warning(f"L1 캐시 조회 오류: {e}")
            
            # L2 캐시 조회
            if CacheLevel.L2_REDIS in levels and self.l2_cache:
                try:
                    value = self.l2_cache.get(cache_key)
                    if value is not None:
                        # L1 캐시에 저장
                        if self.l1_cache:
                            self.l1_cache[cache_key] = pickle.loads(value)  # type: ignore
                        
                        self.stats['hits']['l2'] += 1
                        logger.debug(f"L2 캐시 히트: {cache_key}")
                        return pickle.loads(value)  # type: ignore
                    else:
                        self.stats['misses']['l2'] += 1
                except Exception as e:
                    logger.warning(f"L2 캐시 조회 오류: {e}")
            
            # L3 캐시 조회
            if CacheLevel.L3_FILE in levels and self.l3_cache:
                try:
                    value = self.l3_cache.get(cache_key)
                    if value is not None:
                        # 상위 캐시에 저장
                        if self.l1_cache:
                            self.l1_cache[cache_key] = value
                        if self.l2_cache:
                            l2_ttl = self.config.get('l2_ttl', 3600)
                            if l2_ttl is not None:
                                self.l2_cache.setex(
                                    cache_key, 
                                    l2_ttl,
                                    pickle.dumps(value)
                                )
                        
                        self.stats['hits']['l3'] += 1
                        logger.debug(f"L3 캐시 히트: {cache_key}")
                        return value
                    else:
                        self.stats['misses']['l3'] += 1
                except Exception as e:
                    logger.warning(f"L3 캐시 조회 오류: {e}")
        
        logger.debug(f"캐시 미스: {cache_key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            namespace: str = "default", levels: Optional[List[str]] = None,
            strategy: str = CacheStrategy.WRITE_THROUGH) -> bool:
        """캐시에 값 저장"""
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_FILE]
        
        cache_key = self._generate_key(key, namespace)
        success = True
        
        with self.lock:
            # L1 캐시 저장
            if CacheLevel.L1_MEMORY in levels and self.l1_cache:
                try:
                    self.l1_cache[cache_key] = value
                    self.stats['writes']['l1'] += 1
                    logger.debug(f"L1 캐시 저장: {cache_key}")
                except Exception as e:
                    logger.warning(f"L1 캐시 저장 오류: {e}")
                    success = False
            
            # L2 캐시 저장
            if CacheLevel.L2_REDIS in levels and self.l2_cache:
                try:
                    redis_ttl = ttl if ttl is not None else self.config.get('l2_ttl', 3600)
                    self.l2_cache.setex(
                        cache_key,
                        redis_ttl,
                        pickle.dumps(value)
                    )
                    self.stats['writes']['l2'] += 1
                    logger.debug(f"L2 캐시 저장: {cache_key}")
                except Exception as e:
                    logger.warning(f"L2 캐시 저장 오류: {e}")
                    success = False
            
            # L3 캐시 저장
            if CacheLevel.L3_FILE in levels and self.l3_cache:
                try:
                    file_ttl = ttl or self.config.get('l3_ttl', 86400)
                    self.l3_cache.set(cache_key, value, file_ttl)
                    self.stats['writes']['l3'] += 1
                    logger.debug(f"L3 캐시 저장: {cache_key}")
                except Exception as e:
                    logger.warning(f"L3 캐시 저장 오류: {e}")
                    success = False
        
        return success
    
    def delete(self, key: str, namespace: str = "default", 
               levels: Optional[List[str]] = None) -> bool:
        """캐시에서 값 삭제"""
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_FILE]
        
        cache_key = self._generate_key(key, namespace)
        success = True
        
        with self.lock:
            # L1 캐시 삭제
            if CacheLevel.L1_MEMORY in levels and self.l1_cache:
                try:
                    if cache_key in self.l1_cache:
                        del self.l1_cache[cache_key]
                        logger.debug(f"L1 캐시 삭제: {cache_key}")
                except Exception as e:
                    logger.warning(f"L1 캐시 삭제 오류: {e}")
                    success = False
            
            # L2 캐시 삭제
            if CacheLevel.L2_REDIS in levels and self.l2_cache:
                try:
                    self.l2_cache.delete(cache_key)
                    logger.debug(f"L2 캐시 삭제: {cache_key}")
                except Exception as e:
                    logger.warning(f"L2 캐시 삭제 오류: {e}")
                    success = False
            
            # L3 캐시 삭제
            if CacheLevel.L3_FILE in levels and self.l3_cache:
                try:
                    self.l3_cache.delete(cache_key)
                    logger.debug(f"L3 캐시 삭제: {cache_key}")
                except Exception as e:
                    logger.warning(f"L3 캐시 삭제 오류: {e}")
                    success = False
        
        return success
    
    def clear(self, namespace: Optional[str] = None, levels: Optional[List[str]] = None) -> bool:
        """캐시 전체 삭제"""
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_FILE]
        
        success = True
        
        with self.lock:
            # L1 캐시 전체 삭제
            if CacheLevel.L1_MEMORY in levels and self.l1_cache:
                try:
                    if namespace:
                        # 네임스페이스별 삭제
                        keys_to_delete = [
                            key for key in self.l1_cache.keys()
                            if key.startswith(f"{namespace}:")
                        ]
                        for key in keys_to_delete:
                            del self.l1_cache[key]
                    else:
                        self.l1_cache.clear()
                    logger.info(f"L1 캐시 전체 삭제: {namespace or 'all'}")
                except Exception as e:
                    logger.warning(f"L1 캐시 전체 삭제 오류: {e}")
                    success = False
            
            # L2 캐시 전체 삭제
            if CacheLevel.L2_REDIS in levels and self.l2_cache:
                try:
                    if namespace:
                        pattern = f"{namespace}:*"
                        keys = self.l2_cache.keys(pattern)  # type: ignore
                        if keys and len(keys) > 0:  # type: ignore
                            self.l2_cache.delete(*keys)  # type: ignore
                    else:
                        self.l2_cache.flushdb()
                    logger.info(f"L2 캐시 전체 삭제: {namespace or 'all'}")
                except Exception as e:
                    logger.warning(f"L2 캐시 전체 삭제 오류: {e}")
                    success = False
            
            # L3 캐시 전체 삭제
            if CacheLevel.L3_FILE in levels and self.l3_cache:
                try:
                    self.l3_cache.clear(namespace)
                    logger.info(f"L3 캐시 전체 삭제: {namespace or 'all'}")
                except Exception as e:
                    logger.warning(f"L3 캐시 전체 삭제 오류: {e}")
                    success = False
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        with self.lock:
            stats = self.stats.copy()
            
            # 히트율 계산
            total_hits = sum(stats['hits'].values())
            total_misses = sum(stats['misses'].values())
            total_requests = total_hits + total_misses
            
            if total_requests > 0:
                hit_rate = (total_hits / total_requests) * 100
            else:
                hit_rate = 0
            
            # 레벨별 히트율
            level_hit_rates = {}
            for level in ['l1', 'l2', 'l3']:
                level_hits = stats['hits'][level]
                level_misses = stats['misses'][level]
                level_total = level_hits + level_misses
                
                if level_total > 0:
                    level_hit_rates[level] = (level_hits / level_total) * 100
                else:
                    level_hit_rates[level] = 0
            
            return {
                'hits': stats['hits'],
                'misses': stats['misses'],
                'writes': stats['writes'],
                'evictions': stats['evictions'],
                'total_requests': total_requests,
                'overall_hit_rate': hit_rate,
                'level_hit_rates': level_hit_rates,
                'cache_status': {
                    'l1_enabled': self.l1_cache is not None,
                    'l2_enabled': self.l2_cache is not None,
                    'l3_enabled': self.l3_cache is not None
                }
            }
    
    def reset_stats(self):
        """통계 초기화"""
        with self.lock:
            self.stats = {
                'hits': {'l1': 0, 'l2': 0, 'l3': 0},
                'misses': {'l1': 0, 'l2': 0, 'l3': 0},
                'writes': {'l1': 0, 'l2': 0, 'l3': 0},
                'evictions': {'l1': 0, 'l2': 0, 'l3': 0}
            }

class FileCache:
    """파일 기반 캐시"""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self.metadata_file = os.path.join(cache_dir, 'metadata.json')
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """메타데이터 로드"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"메타데이터 로드 실패: {e}")
        return {}
    
    def _save_metadata(self):
        """메타데이터 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"메타데이터 저장 실패: {e}")
    
    def _get_file_path(self, key: str) -> str:
        """캐시 파일 경로 생성"""
        # 키를 안전한 파일명으로 변환
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        try:
            if key not in self.metadata:
                return None
            
            metadata = self.metadata[key]
            file_path = self._get_file_path(key)
            
            # 만료 확인
            if datetime.now().timestamp() > metadata['expires_at']:
                self.delete(key)
                return None
            
            # 파일에서 값 로드
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            
            return None
            
        except Exception as e:
            logger.warning(f"파일 캐시 조회 실패: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """캐시에 값 저장"""
        try:
            file_path = self._get_file_path(key)
            expires_at = datetime.now().timestamp() + ttl
            
            # 값 저장
            with open(file_path, 'wb') as f:
                pickle.dump(value, f)
            
            # 메타데이터 업데이트
            self.metadata[key] = {
                'file_path': file_path,
                'expires_at': expires_at,
                'created_at': datetime.now().timestamp(),
                'size': os.path.getsize(file_path)
            }
            
            self._save_metadata()
            
        except Exception as e:
            logger.warning(f"파일 캐시 저장 실패: {e}")
    
    def delete(self, key: str):
        """캐시에서 값 삭제"""
        try:
            if key in self.metadata:
                file_path = self.metadata[key]['file_path']
                
                # 파일 삭제
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # 메타데이터에서 제거
                del self.metadata[key]
                self._save_metadata()
                
        except Exception as e:
            logger.warning(f"파일 캐시 삭제 실패: {e}")
    
    def clear(self, namespace: Optional[str] = None):
        """캐시 전체 삭제"""
        try:
            if namespace:
                # 네임스페이스별 삭제
                keys_to_delete = [
                    key for key in list(self.metadata.keys())
                    if key.startswith(f"{namespace}:")
                ]
                for key in keys_to_delete:
                    self.delete(key)
            else:
                # 전체 삭제
                for key in list(self.metadata.keys()):
                    self.delete(key)
                
        except Exception as e:
            logger.warning(f"파일 캐시 전체 삭제 실패: {e}")
    
    def cleanup_expired(self):
        """만료된 캐시 정리"""
        try:
            current_time = datetime.now().timestamp()
            expired_keys = [
                key for key, metadata in self.metadata.items()
                if current_time > metadata['expires_at']
            ]
            
            for key in expired_keys:
                self.delete(key)
            
            logger.info(f"만료된 캐시 {len(expired_keys)}개 정리 완료")
            
        except Exception as e:
            logger.warning(f"만료된 캐시 정리 실패: {e}")

def cached(ttl: int = 300, namespace: str = "default", 
           levels: Optional[List[str]] = None, key_func: Optional[Callable] = None):
    """캐시 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 기본 키 생성
                key_parts = [func.__name__]
                if args:
                    key_parts.extend([str(arg) for arg in args])
                if kwargs:
                    for k, v in sorted(kwargs.items()):
                        key_parts.extend([k, str(v)])
                cache_key = ":".join(key_parts)
            
            # 캐시에서 조회
            cache_instance = getattr(func, '_cache_instance', None)
            if cache_instance is None:
                cache_instance = AdvancedCache()
                func._cache_instance = cache_instance
            
            cached_value = cache_instance.get(cache_key, namespace, levels)
            if cached_value is not None:
                return cached_value
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 캐시에 저장
            cache_instance.set(cache_key, result, ttl, namespace, levels)
            
            return result
        return wrapper
    return decorator

# 전역 캐시 인스턴스
advanced_cache = AdvancedCache()

def get_cache() -> AdvancedCache:
    """전역 캐시 인스턴스 반환"""
    return advanced_cache 