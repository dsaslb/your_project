import redis
import json
import pickle
from datetime import datetime, timedelta
from functools import wraps
import logging
from typing import Any, Optional, Union, Dict, List

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis 기반 캐싱 시스템"""
    
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 연결 테스트
            self.redis_client.ping()
            self.connected = True
            logger.info("Redis 캐시 서버에 연결되었습니다.")
        except Exception as e:
            logger.warning(f"Redis 연결 실패, 메모리 캐시로 대체: {e}")
            self.connected = False
            self.memory_cache = {}
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """캐시에 데이터 저장"""
        try:
            if self.connected:
                # JSON 직렬화 가능한 데이터
                if isinstance(value, (dict, list, str, int, float, bool)):
                    serialized_value = json.dumps(value, ensure_ascii=False, default=str)
                    return self.redis_client.setex(key, expire, serialized_value)
                else:
                    # 복잡한 객체는 pickle 사용
                    serialized_value = pickle.dumps(value)
                    return self.redis_client.setex(key, expire, serialized_value)
            else:
                # 메모리 캐시 사용
                self.memory_cache[key] = {
                    'value': value,
                    'expire_at': datetime.now() + timedelta(seconds=expire)
                }
                return True
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """캐시에서 데이터 조회"""
        try:
            if self.connected:
                value = self.redis_client.get(key)
                if value is None:
                    return default
                
                # JSON 역직렬화 시도
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    # pickle 역직렬화 시도
                    try:
                        return pickle.loads(value.encode('latin1'))
                    except:
                        return value
            else:
                # 메모리 캐시에서 조회
                cache_data = self.memory_cache.get(key)
                if cache_data and datetime.now() < cache_data['expire_at']:
                    return cache_data['value']
                else:
                    # 만료된 데이터 삭제
                    self.memory_cache.pop(key, None)
                    return default
        except Exception as e:
            logger.error(f"캐시 조회 실패: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """캐시에서 데이터 삭제"""
        try:
            if self.connected:
                return bool(self.redis_client.delete(key))
            else:
                return bool(self.memory_cache.pop(key, None))
        except Exception as e:
            logger.error(f"캐시 삭제 실패: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        try:
            if self.connected:
                return bool(self.redis_client.exists(key))
            else:
                cache_data = self.memory_cache.get(key)
                return cache_data is not None and datetime.now() < cache_data['expire_at']
        except Exception as e:
            logger.error(f"캐시 키 확인 실패: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """키 만료 시간 설정"""
        try:
            if self.connected:
                return bool(self.redis_client.expire(key, seconds))
            else:
                cache_data = self.memory_cache.get(key)
                if cache_data:
                    cache_data['expire_at'] = datetime.now() + timedelta(seconds=seconds)
                    return True
                return False
        except Exception as e:
            logger.error(f"캐시 만료 시간 설정 실패: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """패턴에 맞는 키들 삭제"""
        try:
            if self.connected:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # 메모리 캐시에서 패턴 매칭
                deleted_count = 0
                keys_to_delete = []
                for key in self.memory_cache.keys():
                    if pattern.replace('*', '') in key:
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    if self.delete(key):
                        deleted_count += 1
                return deleted_count
        except Exception as e:
            logger.error(f"패턴 캐시 삭제 실패: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        try:
            if self.connected:
                info = self.redis_client.info()
                return {
                    'connected': True,
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0)
                }
            else:
                return {
                    'connected': False,
                    'memory_cache_size': len(self.memory_cache),
                    'cache_type': 'memory'
                }
        except Exception as e:
            logger.error(f"캐시 통계 조회 실패: {e}")
            return {'connected': False, 'error': str(e)}

# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager()

def cache_result(expire: int = 3600, key_prefix: str = ""):
    """함수 결과 캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 캐시에서 조회
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"캐시 히트: {cache_key}")
                return cached_result
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            cache_manager.set(cache_key, result, expire)
            logger.debug(f"캐시 저장: {cache_key}")
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """캐시 무효화 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_manager.clear_pattern(pattern)
            logger.debug(f"캐시 무효화: {pattern}")
            return result
        return wrapper
    return decorator

# 캐시 키 상수
class CacheKeys:
    """캐시 키 상수 정의"""
    
    # 사용자 관련
    USER_PROFILE = "user:profile:*"
    USER_PERMISSIONS = "user:permissions:*"
    
    # 스케줄 관련
    SCHEDULE_WEEKLY = "schedule:weekly:*"
    SCHEDULE_MONTHLY = "schedule:monthly:*"
    
    # 출퇴근 관련
    ATTENDANCE_DAILY = "attendance:daily:*"
    ATTENDANCE_MONTHLY = "attendance:monthly:*"
    
    # 주문 관련
    ORDERS_TODAY = "orders:today:*"
    ORDERS_WEEKLY = "orders:weekly:*"
    
    # 재고 관련
    INVENTORY_STATUS = "inventory:status:*"
    INVENTORY_LOW_STOCK = "inventory:low_stock:*"
    
    # 분석 관련
    ANALYTICS_SALES = "analytics:sales:*"
    ANALYTICS_STAFF = "analytics:staff:*"
    ANALYTICS_INVENTORY = "analytics:inventory:*"
    
    # 알림 관련
    NOTIFICATIONS_UNREAD = "notifications:unread:*"
    NOTIFICATIONS_COUNT = "notifications:count:*"

# 캐시 유틸리티 함수들
def cache_user_data(user_id: int, data: Dict[str, Any], expire: int = 1800):
    """사용자 데이터 캐싱"""
    key = f"user:data:{user_id}"
    return cache_manager.set(key, data, expire)

def get_cached_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """캐시된 사용자 데이터 조회"""
    key = f"user:data:{user_id}"
    return cache_manager.get(key)

def cache_analytics_data(data_type: str, branch_id: int, data: Any, expire: int = 3600):
    """분석 데이터 캐싱"""
    key = f"analytics:{data_type}:{branch_id}"
    return cache_manager.set(key, data, expire)

def get_cached_analytics_data(data_type: str, branch_id: int) -> Any:
    """캐시된 분석 데이터 조회"""
    key = f"analytics:{data_type}:{branch_id}"
    return cache_manager.get(key)

def clear_user_cache(user_id: int):
    """사용자 관련 캐시 삭제"""
    patterns = [
        f"user:data:{user_id}",
        f"user:profile:{user_id}",
        f"user:permissions:{user_id}"
    ]
    for pattern in patterns:
        cache_manager.clear_pattern(pattern)

def clear_branch_cache(branch_id: int):
    """지점 관련 캐시 삭제"""
    patterns = [
        f"schedule:*:{branch_id}",
        f"attendance:*:{branch_id}",
        f"orders:*:{branch_id}",
        f"inventory:*:{branch_id}",
        f"analytics:*:{branch_id}"
    ]
    for pattern in patterns:
        cache_manager.clear_pattern(pattern)

def get_cache_stats() -> Dict[str, Any]:
    """캐시 통계 조회"""
    return cache_manager.get_stats() 