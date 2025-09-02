import os
import json
import time
import hashlib
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import uuid
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheType(Enum):
    """캐시 타입"""
    MEMORY = "memory"
    DISK = "disk"
    HYBRID = "hybrid"

class CachePolicy(Enum):
    """캐시 정책"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live

@dataclass
class CacheConfig:
    """캐시 설정 클래스"""
    data_dir: str
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    max_disk_size: int = 1024 * 1024 * 1024   # 1GB
    default_ttl: int = 3600  # 1시간 (초)
    cleanup_interval: int = 300  # 5분
    enable_compression: bool = True
    enable_encryption: bool = False
    encryption_key: str = ""

@dataclass
class CacheItem:
    """캐시 항목"""
    key: str
    value: Any
    cache_type: CacheType
    ttl: int
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    size: int = 0
    tags: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class CacheStats:
    """캐시 통계"""
    total_items: int
    memory_items: int
    disk_items: int
    total_size: int
    memory_size: int
    disk_size: int
    hit_count: int
    miss_count: int
    hit_rate: float
    eviction_count: int

class CacheManager:
    """캐시 관리자 클래스"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.memory_cache: Dict[str, CacheItem] = {}
        self.disk_cache: Dict[str, CacheItem] = {}
        self.access_order: List[str] = []
        self.stats = {
            'hit_count': 0,
            'miss_count': 0,
            'eviction_count': 0
        }
        
        # 데이터 디렉토리 생성
        os.makedirs(config.data_dir, exist_ok=True)
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 백그라운드 정리 작업 시작
        self._start_cleanup_thread()
        
        logger.info("캐시 관리자가 초기화되었습니다")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        db_path = os.path.join(self.config.data_dir, "cache.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_items (
                key TEXT PRIMARY KEY,
                value TEXT,
                cache_type TEXT,
                ttl INTEGER,
                created_at TEXT,
                accessed_at TEXT,
                access_count INTEGER,
                size INTEGER,
                tags TEXT,
                metadata TEXT
            )
        """)
        self.conn.commit()
        
        # 기존 디스크 캐시 로드
        self._load_disk_cache()
    
    def _load_disk_cache(self):
        """디스크 캐시 로드"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM cache_items WHERE cache_type = 'disk'")
        
        for row in cursor.fetchall():
            item = CacheItem(
                key=row['key'],
                value=json.loads(row['value']),
                cache_type=CacheType(row['cache_type']),
                ttl=row['ttl'],
                created_at=datetime.fromisoformat(row['created_at']),
                accessed_at=datetime.fromisoformat(row['accessed_at']),
                access_count=row['access_count'],
                size=row['size'],
                tags=json.loads(row['tags']) if row['tags'] else [],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            self.disk_cache[item.key] = item
    
    def _save_cache_item(self, item: CacheItem):
        """캐시 항목 저장"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO cache_items 
            (key, value, cache_type, ttl, created_at, accessed_at, access_count, size, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.key,
            json.dumps(item.value),
            item.cache_type.value,
            item.ttl,
            item.created_at.isoformat(),
            item.accessed_at.isoformat(),
            item.access_count,
            item.size,
            json.dumps(item.tags),
            json.dumps(item.metadata)
        ))
        self.conn.commit()
    
    def _delete_cache_item(self, key: str):
        """캐시 항목 삭제"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cache_items WHERE key = ?", (key,))
        self.conn.commit()
    
    def set(self, key: str, value: Any, ttl: int = None, 
            cache_type: CacheType = CacheType.MEMORY, tags: List[str] = None,
            metadata: Dict[str, Any] = None) -> bool:
        """캐시에 항목 설정"""
        try:
            if ttl is None:
                ttl = self.config.default_ttl
            
            # 값 크기 계산
            value_size = len(json.dumps(value))
            
            # TTL 확인
            if ttl > 0:
                expiry_time = datetime.now() + timedelta(seconds=ttl)
            else:
                expiry_time = None
            
            item = CacheItem(
                key=key,
                value=value,
                cache_type=cache_type,
                ttl=ttl,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                size=value_size,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            if cache_type == CacheType.MEMORY:
                # 메모리 캐시 크기 확인
                if self._get_memory_size() + value_size > self.config.max_memory_size:
                    self._evict_memory_cache()
                
                self.memory_cache[key] = item
                if key not in self.access_order:
                    self.access_order.append(key)
            
            elif cache_type == CacheType.DISK:
                # 디스크 캐시 크기 확인
                if self._get_disk_size() + value_size > self.config.max_disk_size:
                    self._evict_disk_cache()
                
                self.disk_cache[key] = item
                self._save_cache_item(item)
            
            elif cache_type == CacheType.HYBRID:
                # 하이브리드: 메모리와 디스크 모두에 저장
                self.set(key, value, ttl, CacheType.MEMORY, tags, metadata)
                self.set(key, value, ttl, CacheType.DISK, tags, metadata)
            
            logger.info(f"캐시 항목 설정: {key} ({cache_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"캐시 항목 설정 실패: {key} - {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 항목 조회"""
        try:
            # 메모리 캐시에서 먼저 확인
            if key in self.memory_cache:
                item = self.memory_cache[key]
                if self._is_expired(item):
                    del self.memory_cache[key]
                    self.access_order.remove(key)
                    self.stats['miss_count'] += 1
                    return None
                
                # 접근 정보 업데이트
                item.accessed_at = datetime.now()
                item.access_count += 1
                self._update_access_order(key)
                self.stats['hit_count'] += 1
                return item.value
            
            # 디스크 캐시에서 확인
            if key in self.disk_cache:
                item = self.disk_cache[key]
                if self._is_expired(item):
                    del self.disk_cache[key]
                    self._delete_cache_item(key)
                    self.stats['miss_count'] += 1
                    return None
                
                # 접근 정보 업데이트
                item.accessed_at = datetime.now()
                item.access_count += 1
                self._save_cache_item(item)
                self.stats['hit_count'] += 1
                return item.value
            
            self.stats['miss_count'] += 1
            return None
            
        except Exception as e:
            logger.error(f"캐시 항목 조회 실패: {key} - {str(e)}")
            self.stats['miss_count'] += 1
            return None
    
    def delete(self, key: str) -> bool:
        """캐시 항목 삭제"""
        try:
            deleted = False
            
            if key in self.memory_cache:
                del self.memory_cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                deleted = True
            
            if key in self.disk_cache:
                del self.disk_cache[key]
                self._delete_cache_item(key)
                deleted = True
            
            if deleted:
                logger.info(f"캐시 항목 삭제: {key}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"캐시 항목 삭제 실패: {key} - {str(e)}")
            return False
    
    def clear(self, cache_type: CacheType = None) -> bool:
        """캐시 전체 삭제"""
        try:
            if cache_type is None or cache_type == CacheType.MEMORY:
                self.memory_cache.clear()
                self.access_order.clear()
            
            if cache_type is None or cache_type == CacheType.DISK:
                self.disk_cache.clear()
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM cache_items")
                self.conn.commit()
            
            logger.info(f"캐시 전체 삭제 완료: {cache_type.value if cache_type else 'all'}")
            return True
            
        except Exception as e:
            logger.error(f"캐시 전체 삭제 실패: {str(e)}")
            return False
    
    def get_stats(self) -> CacheStats:
        """캐시 통계 조회"""
        total_hits = self.stats['hit_count']
        total_misses = self.stats['miss_count']
        total_requests = total_hits + total_misses
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return CacheStats(
            total_items=len(self.memory_cache) + len(self.disk_cache),
            memory_items=len(self.memory_cache),
            disk_items=len(self.disk_cache),
            total_size=self._get_memory_size() + self._get_disk_size(),
            memory_size=self._get_memory_size(),
            disk_size=self._get_disk_size(),
            hit_count=total_hits,
            miss_count=total_misses,
            hit_rate=hit_rate,
            eviction_count=self.stats['eviction_count']
        )
    
    def _is_expired(self, item: CacheItem) -> bool:
        """캐시 항목 만료 확인"""
        if item.ttl <= 0:
            return False
        return datetime.now() > item.created_at + timedelta(seconds=item.ttl)
    
    def _get_memory_size(self) -> int:
        """메모리 캐시 크기 계산"""
        return sum(item.size for item in self.memory_cache.values())
    
    def _get_disk_size(self) -> int:
        """디스크 캐시 크기 계산"""
        return sum(item.size for item in self.disk_cache.values())
    
    def _update_access_order(self, key: str):
        """접근 순서 업데이트 (LRU)"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _evict_memory_cache(self):
        """메모리 캐시 제거 (LRU)"""
        if not self.access_order:
            return
        
        # 가장 오래된 항목 제거
        oldest_key = self.access_order[0]
        if oldest_key in self.memory_cache:
            del self.memory_cache[oldest_key]
            self.access_order.pop(0)
            self.stats['eviction_count'] += 1
            logger.info(f"메모리 캐시 제거: {oldest_key}")
    
    def _evict_disk_cache(self):
        """디스크 캐시 제거 (LRU)"""
        if not self.disk_cache:
            return
        
        # 가장 오래된 항목 찾기
        oldest_key = min(self.disk_cache.keys(), 
                        key=lambda k: self.disk_cache[k].accessed_at)
        
        if oldest_key in self.disk_cache:
            del self.disk_cache[oldest_key]
            self._delete_cache_item(oldest_key)
            self.stats['eviction_count'] += 1
            logger.info(f"디스크 캐시 제거: {oldest_key}")
    
    def _start_cleanup_thread(self):
        """백그라운드 정리 작업 시작"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(self.config.cleanup_interval)
                    self._cleanup_expired_items()
                except Exception as e:
                    logger.error(f"캐시 정리 작업 오류: {str(e)}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired_items(self):
        """만료된 항목 정리"""
        try:
            # 메모리 캐시 정리
            expired_keys = []
            for key, item in self.memory_cache.items():
                if self._is_expired(item):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
            
            # 디스크 캐시 정리
            expired_keys = []
            for key, item in self.disk_cache.items():
                if self._is_expired(item):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.disk_cache[key]
                self._delete_cache_item(key)
            
            if expired_keys:
                logger.info(f"만료된 캐시 항목 정리: {len(expired_keys)}개")
                
        except Exception as e:
            logger.error(f"캐시 정리 작업 실패: {str(e)}")
    
    def get_by_tags(self, tags: List[str]) -> Dict[str, Any]:
        """태그로 캐시 항목 조회"""
        result = {}
        
        for cache_dict in [self.memory_cache, self.disk_cache]:
            for key, item in cache_dict.items():
                if any(tag in item.tags for tag in tags):
                    if not self._is_expired(item):
                        result[key] = item.value
        
        return result
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """태그로 캐시 항목 무효화"""
        count = 0
        
        for cache_dict in [self.memory_cache, self.disk_cache]:
            keys_to_delete = []
            for key, item in cache_dict.items():
                if any(tag in item.tags for tag in tags):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                if self.delete(key):
                    count += 1
        
        return count 