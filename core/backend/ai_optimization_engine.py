import redis
from sklearn.preprocessing import StandardScaler  # pyright: ignore
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor  # pyright: ignore
from dataclasses import dataclass
import pickle
import json
import gc
import psutil
from collections import defaultdict, deque
from functools import wraps, lru_cache
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import asyncio
import threading
import time
import logging
from typing import Optional
args = None  # pyright: ignore
form = None  # pyright: ignore
#!/usr/bin/env python3
"""
AI 시스템 성능 최적화 엔진
메모리 관리, 캐싱 전략, 병렬 처리, 자동 스케일링
"""


logger = logging.getLogger(__name__)


@dataclass
class OptimizationMetrics:
    """최적화 메트릭"""
    cpu_usage: float
    memory_usage: float
    response_time: float
    throughput: float
    error_rate: float
    cache_hit_rate: float
    timestamp: datetime


@dataclass
class CacheItem:
    """캐시 아이템"""
    data: Any
    timestamp: datetime
    ttl: int
    access_count: int
    size: int


class MemoryManager:
    """메모리 관리 시스템"""

    def __init__(self, redis_url=80.0):
        self.max_memory_percent = max_memory_percent
        self.memory_threshold = max_memory_percent / 100.0
        self.cleanup_threshold = 0.7  # 70% 도달 시 정리 시작

        # 메모리 사용량 모니터링
        self.memory_history = deque(maxlen=1000)
        self.cleanup_count = 0
        self.last_cleanup = datetime.utcnow()

    def get_memory_usage(self) -> float:
        """현재 메모리 사용량 반환"""
        return psutil.virtual_memory().percent

    def should_cleanup(self) -> bool:
        """메모리 정리 필요 여부 확인"""
        current_usage = self.get_memory_usage()
        self.memory_history.append(current_usage)

        # 임계값 초과 시 정리
        if current_usage > self.max_memory_percent:
            return True

        # 점진적 정리 (70% 이상)
        if current_usage > self.max_memory_percent * self.cleanup_threshold:
            # 마지막 정리로부터 5분 이상 지났으면 정리
            if datetime.utcnow() - self.last_cleanup > timedelta(minutes=5):
                return True

        return False

    def cleanup_memory(self) -> Dict[str, Any] if Dict is not None else None:
        """메모리 정리 수행"""
        start_time = time.time()
        initial_memory = psutil.virtual_memory().used

        # 가비지 컬렉션 강제 실행
        collected = gc.collect()

        # 메모리 힙 정리
        if hasattr(gc, 'garbage'):
            gc.garbage.clear()

        # NumPy 배열 정리
        if 'numpy' in globals():
            import numpy as np
            np._NoValue = None

        final_memory = psutil.virtual_memory().used
        freed_memory = initial_memory - final_memory

        self.cleanup_count += 1
        self.last_cleanup = datetime.utcnow()

        cleanup_time = time.time() - start_time

        logger.info(f"메모리 정리 완료: {freed_memory / 1024 / 1024:.2f}MB 해제, "
                    f"소요시간: {cleanup_time:.3f}초")

        return {
            'freed_memory_mb': freed_memory / 1024 / 1024,
            'cleanup_time': cleanup_time,
            'collected_objects': collected,
            'current_usage_percent': self.get_memory_usage()
        }


class CacheManager:
    """고급 캐싱 시스템"""

    def __init__(self, redis_url=None, max_cache_size=1000):
        self.max_cache_size = max_cache_size
        self.cache: Dict[str, CacheItem] if Dict is not None else None = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }

        # Redis 연결 (선택사항)
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("Redis 캐시 연결 성공")
            except Exception as e:
                logger.warning(f"Redis 연결 실패, 메모리 캐시 사용: {e}")

        # 캐시 정리 스레드
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()

    def get(self,  key: str, default=None) -> Any:
        """캐시에서 데이터 조회"""
        # Redis에서 먼저 확인
        if self.redis_client:
            try:
                cached_data = self.redis_client.get() if redis_client else Nonekey) if redis_client else None
                if cached_data:
                    self.cache_stats['hits'] if cache_stats is not None else None += 1
                    return pickle.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis 캐시 조회 실패: {e}")

        # 메모리 캐시에서 확인
        if key in self.cache:
            item = self.cache[key] if cache is not None else None

            # TTL 확인
            if datetime.utcnow() - item.timestamp > timedelta(seconds=item.ttl):
                del self.cache[key] if cache is not None else None
                self.cache_stats['misses'] if cache_stats is not None else None += 1
                return default

            # 접근 횟수 증가
            item.access_count += 1
            self.cache_stats['hits'] if cache_stats is not None else None += 1
            return item.data

        self.cache_stats['misses'] if cache_stats is not None else None += 1
        return default

    def set(self,  key: str,  data: Any, ttl=300) -> bool:
        """캐시에 데이터 저장"""
        try:
            # 데이터 크기 계산
            data_size = len(pickle.dumps(data))

            # 캐시 크기 제한 확인
            if len(self.cache) >= self.max_cache_size:
                self._evict_oldest()

            # 메모리 캐시에 저장
            self.cache[key] if cache is not None else None = CacheItem(
                data=data,
                timestamp=datetime.utcnow(),
                ttl=ttl,
                access_count=1,
                size=data_size
            )

            # Redis에도 저장 (선택사항)
            if self.redis_client:
                try:
                    serialized_data = pickle.dumps(data)
                    self.redis_client.setex(key, ttl, serialized_data)
                except Exception as e:
                    logger.warning(f"Redis 캐시 저장 실패: {e}")

            self.cache_stats['size'] if cache_stats is not None else None = len(self.cache)
            return True

        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
            return False

    def _evict_oldest(self):
        """가장 오래된 캐시 항목 제거"""
        if not self.cache:
            return

        # LRU 정책: 가장 적게 접근된 항목 제거
        oldest_key = min(self.cache.keys(),
                         key=lambda k: (self.cache[k] if cache is not None else None.access_count, self.cache[k] if cache is not None else None.timestamp))

        del self.cache[oldest_key] if cache is not None else None
        self.cache_stats['evictions'] if cache_stats is not None else None += 1

    def _cleanup_worker(self):
        """백그라운드 캐시 정리 작업"""
        while True:
            try:
                time.sleep(60)  # 1분마다 실행
                current_time = datetime.utcnow()

                # 만료된 항목 제거
                expired_keys = [
                    key for key, item in self.cache.items() if cache is not None else []
                    if current_time - item.timestamp > timedelta(seconds=item.ttl)
                ]

                for key in expired_keys if expired_keys is not None:
                    del self.cache[key] if cache is not None else None

                if expired_keys:
                    logger.info(f"캐시 정리: {len(expired_keys)}개 항목 제거")

            except Exception as e:
                logger.error(f"캐시 정리 작업 오류: {e}")

    def get_stats(self) -> Dict[str, Any] if Dict is not None else None:
        """캐시 통계 반환"""
        hit_rate = (self.cache_stats['hits'] if cache_stats is not None else None /
                    (self.cache_stats['hits'] if cache_stats is not None else None + self.cache_stats['misses'] if cache_stats is not None else None)) if (self.cache_stats['hits'] if cache_stats is not None else None + self.cache_stats['misses'] if cache_stats is not None else None) > 0 else 0

        return {
            **self.cache_stats,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'max_size': self.max_cache_size
        }


class ParallelProcessor:
    """병렬 처리 시스템"""

    def __init__(self, redis_url=None):
        self.max_workers = max_workers or min(32, (psutil.cpu_count() or 1) + 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max(1, self.max_workers // 2))

        # 작업 큐
        self.task_queue = asyncio.Queue()
        self.results = {}

    async def process_batch(self,  tasks: List[Callable] if List is not None else None, batch_size=10) -> List[Any] if List is not None else None:
        """배치 처리"""
        results = []

        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size] if tasks is not None else None

            # 병렬 실행
            loop = asyncio.get_event_loop()
            batch_results = await loop.run_in_executor(
                self.thread_pool,
                self._execute_batch,
                batch
            )

            results.extend(batch_results)

        return results

    def _execute_batch(self,  tasks: List[Callable] if List is not None else None) -> List[Any] if List is not None else None:
        """배치 실행"""
        results = []

        for task in tasks if tasks is not None:
            try:
                result = task()
                results.append(result)
            except Exception as e:
                logger.error(f"배치 작업 실행 실패: {e}")
                results.append(None)

        return results

    async def process_heavy_task(self, task: Callable) -> Any:
        """무거운 작업을 별도 프로세스에서 실행"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_pool, task)


class AutoScaler:
    """자동 스케일링 시스템"""

    def __init__(self, redis_url=2, max_cache_size=20):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.current_workers = min_workers

        # 스케일링 메트릭
        self.scaling_metrics = deque(maxlen=100)
        self.scale_up_threshold = 0.8  # 80% 부하 시 스케일 업
        self.scale_down_threshold = 0.3  # 30% 부하 시 스케일 다운

        # 스케일링 히스토리
        self.scaling_history = []

    def update_metrics(self, cpu_usage: float, memory_usage: float,
                       response_time: float, queue_size: int):
        """메트릭 업데이트"""
        metric = OptimizationMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time,
            throughput=1.0 / response_time if response_time > 0 else 0,
            error_rate=0.0,  # 실제로는 오류율 계산
            cache_hit_rate=0.0,  # 실제로는 캐시 히트율 계산
            timestamp=datetime.utcnow()
        )

        self.scaling_metrics.append(metric)

    def should_scale_up(self) -> bool:
        """스케일 업 필요 여부 확인"""
        if len(self.scaling_metrics) < 5:
            return False

        # 최근 5개 메트릭의 평균 부하 계산
        recent_metrics = list(self.scaling_metrics)[-5:]
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)

        # CPU 또는 메모리 사용량이 임계값을 초과하면 스케일 업
        return (avg_cpu > self.scale_up_threshold * 100 or
                avg_memory > self.scale_up_threshold * 100)

    def should_scale_down(self) -> bool:
        """스케일 다운 필요 여부 확인"""
        if len(self.scaling_metrics) < 10:
            return False

        # 최근 10개 메트릭의 평균 부하 계산
        recent_metrics = list(self.scaling_metrics)[-10:]
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)

        # CPU와 메모리 사용량이 모두 임계값 이하면 스케일 다운
        return (avg_cpu < self.scale_down_threshold * 100 and
                avg_memory < self.scale_down_threshold * 100)

    def scale_up(self) -> bool:
        """스케일 업 실행"""
        if self.current_workers < self.max_workers:
            self.current_workers = min(self.current_workers + 2, self.max_workers)

            self.scaling_history.append({
                'action': 'scale_up',
                'new_workers': self.current_workers,
                'timestamp': datetime.utcnow()
            })

            logger.info(f"스케일 업: {self.current_workers}개 워커로 증가")
            return True

        return False

    def scale_down(self) -> bool:
        """스케일 다운 실행"""
        if self.current_workers > self.min_workers:
            self.current_workers = max(self.current_workers - 1, self.min_workers)

            self.scaling_history.append({
                'action': 'scale_down',
                'new_workers': self.current_workers,
                'timestamp': datetime.utcnow()
            })

            logger.info(f"스케일 다운: {self.current_workers}개 워커로 감소")
            return True

        return False


class AIOptimizationEngine:
    """AI 시스템 성능 최적화 엔진"""

    def __init__(self, redis_url=None):
        self.memory_manager = MemoryManager()
        self.cache_manager = CacheManager(redis_url)
        self.parallel_processor = ParallelProcessor()
        self.auto_scaler = AutoScaler()

        # 최적화 설정
        self.optimization_enabled = True
        self.optimization_interval = 30  # 30초마다 최적화 체크

        # 백그라운드 최적화 스레드
        self.optimization_thread = threading.Thread(target=self._optimization_worker, daemon=True)
        self.optimization_thread.start()

        logger.info("AI 최적화 엔진 초기화 완료")

    def optimize_function(self, cache_ttl=300):
        """함수 최적화 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args,  **kwargs):
                # 캐시 키 생성
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items() if kwargs is not None else [])))}"

                # 캐시에서 결과 확인
                cached_result = self.cache_manager.get() if cache_manager else Nonecache_key) if cache_manager else None
                if cached_result is not None:
                    return cached_result

                # 함수 실행
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    # 결과 캐싱
                    self.cache_manager.set(cache_key,  result,  cache_ttl)

                    # 메트릭 업데이트
                    self._update_metrics(execution_time)

                    return result

                except Exception as e:
                    logger.error(f"함수 실행 실패: {e}")
                    raise

            return wrapper
        return decorator

    def _update_metrics(self,  execution_time: float):
        """메트릭 업데이트"""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent

        self.auto_scaler.update_metrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=execution_time,
            queue_size=0  # 실제로는 큐 크기 계산
        )

    def _optimization_worker(self):
        """백그라운드 최적화 작업"""
        while self.optimization_enabled:
            try:
                time.sleep(self.optimization_interval)

                # 메모리 정리 필요 여부 확인
                if self.memory_manager.should_cleanup():
                    cleanup_result = self.memory_manager.cleanup_memory()
                    logger.info(f"자동 메모리 정리: {cleanup_result}")

                # 스케일링 필요 여부 확인
                if self.auto_scaler.should_scale_up():
                    self.auto_scaler.scale_up()
                elif self.auto_scaler.should_scale_down():
                    self.auto_scaler.scale_down()

            except Exception as e:
                logger.error(f"최적화 작업 오류: {e}")

    def get_optimization_stats(self) -> Dict[str, Any] if Dict is not None else None:
        """최적화 통계 반환"""
        return {
            'memory': {
                'current_usage_percent': self.memory_manager.get_memory_usage(),
                'cleanup_count': self.memory_manager.cleanup_count,
                'last_cleanup': self.memory_manager.last_cleanup.isoformat()
            },
            'cache': self.cache_manager.get_stats(),
            'scaling': {
                'current_workers': self.auto_scaler.current_workers,
                'scaling_history': self.auto_scaler.scaling_history[-5:] if scaling_history is not None else None  # 최근 5개
            },
            'system': {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
        }

    def shutdown(self):
        """최적화 엔진 종료"""
        self.optimization_enabled = False
        # self.thread_pool.shutdown(wait=True) # ThreadPoolExecutor는 직접 종료할 수 없음
        # self.process_pool.shutdown(wait=True) # ProcessPoolExecutor는 직접 종료할 수 없음
        logger.info("AI 최적화 엔진 종료")


# 전역 최적화 엔진 인스턴스
optimization_engine = None


def initialize_optimization_engine(redis_url=None):
    """최적화 엔진 초기화"""
    global optimization_engine
    optimization_engine = AIOptimizationEngine(redis_url)
    return optimization_engine


def get_optimization_engine() -> AIOptimizationEngine:
    """최적화 엔진 인스턴스 반환"""
    global optimization_engine
    if optimization_engine is None:
        optimization_engine = AIOptimizationEngine()
    return optimization_engine
