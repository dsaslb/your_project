#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis 캐시 Fallback 시스템
Redis가 없는 환경에서도 정상 작동하도록 하는 캐시 관리자
"""

import os
import logging
from typing import Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class CacheFallbackManager:
    """캐시 Fallback 관리자"""
    
    def __init__(self):
        self.memory_cache = {}
        self.redis_available = False
        self.redis_client = None
        
    def initialize_redis(self):
        """Redis 연결 시도"""
        # 가상 서버 모드에서는 Redis 비활성화
        if os.getenv('DISABLE_REDIS', '').lower() == 'true':
            logger.info("🔧 가상 서버 모드: Redis 비활성화, 메모리 캐시 사용")
            self.redis_available = False
            return
            
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            if not redis_url or redis_url.strip() == '':
                logger.info("🔧 Redis URL 없음: 메모리 캐시 사용")
                self.redis_available = False
                return
                
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ Redis 연결 실패, 메모리 캐시로 fallback: {e}")
            self.redis_available = False
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if self.redis_available and self.redis_client:
            try:
                value = self.redis_client.get(key)
                return value.decode('utf-8') if value else None
            except Exception as e:
                logger.warning(f"Redis get 실패, 메모리 캐시 사용: {e}")
        
        return self.memory_cache.get(key)
    
    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """캐시에 값 저장"""
        if self.redis_available and self.redis_client:
            try:
                return self.redis_client.setex(key, timeout, str(value))
            except Exception as e:
                logger.warning(f"Redis set 실패, 메모리 캐시 사용: {e}")
        
        self.memory_cache[key] = value
        return True
    
    def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        if self.redis_available and self.redis_client:
            try:
                return bool(self.redis_client.delete(key))
            except Exception as e:
                logger.warning(f"Redis delete 실패, 메모리 캐시 사용: {e}")
        
        return self.memory_cache.pop(key, None) is not None
    
    def clear(self) -> bool:
        """캐시 전체 삭제"""
        if self.redis_available and self.redis_client:
            try:
                return self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis clear 실패, 메모리 캐시 사용: {e}")
        
        self.memory_cache.clear()
        return True

# 전역 캐시 매니저 인스턴스
cache_manager = CacheFallbackManager()

def with_cache(timeout: int = 300):
    """캐시 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 캐시에서 조회
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행 및 결과 캐시
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def get_cache_config():
    """캐시 설정 정보 반환"""
    return {
        "redis_available": cache_manager.redis_available,
        "redis_url": os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        "cache_type": "redis" if cache_manager.redis_available else "memory",
        "fallback_enabled": True,
        "memory_cache_size": len(cache_manager.memory_cache)
    }

def init_cache_system():
    """캐시 시스템 초기화"""
    logger.info("🚀 캐시 시스템 초기화 중...")
    cache_manager.initialize_redis()
    
    if cache_manager.redis_available:
        logger.info("✅ Redis 캐시 시스템 준비 완료")
    else:
        logger.info("✅ 메모리 캐시 시스템 준비 완료 (Redis Fallback)")