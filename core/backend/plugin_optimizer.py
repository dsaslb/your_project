#!/usr/bin/env python3
"""
플러그인 시스템 성능 최적화 및 캐싱 시스템
플러그인 로딩, 실행, 모니터링 성능을 최적화하고 캐싱을 제공
"""

import logging
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
from collections import defaultdict, deque
import psutil
import gc

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginPerformanceOptimizer:
    """플러그인 성능 최적화 시스템"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_ttl = 300  # 5분 캐시 TTL
        
        # 성능 메트릭 저장
        self.performance_metrics = {
            'load_times': defaultdict(lambda: deque(maxlen=100)),
            'execution_times': defaultdict(lambda: deque(maxlen=1000)),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100),
            'error_counts': defaultdict(int),
            'success_counts': defaultdict(int)
        }
        
        # 최적화 설정
        self.optimization_settings = {
            'enable_caching': True,
            'enable_lazy_loading': True,
            'enable_memory_optimization': True,
            'enable_parallel_loading': True,
            'cache_ttl': 300,
            'max_memory_usage': 80.0,  # 80%
            'max_cpu_usage': 90.0,     # 90%
            'cleanup_interval': 3600   # 1시간
        }
        
        # 백그라운드 최적화 스레드
        self.optimization_thread = None
        self.running = False
        
    def start_optimization(self):
        """성능 최적화 시작"""
        if self.running:
            return
            
        self.running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        logger.info("플러그인 성능 최적화 시스템 시작")
        
    def stop_optimization(self):
        """성능 최적화 중지"""
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        logger.info("플러그인 성능 최적화 시스템 중지")
        
    def _optimization_loop(self):
        """백그라운드 최적화 루프"""
        while self.running:
            try:
                # 메모리 사용량 체크 및 최적화
                if self.optimization_settings['enable_memory_optimization']:
                    self._optimize_memory_usage()
                
                # 캐시 정리
                self._cleanup_expired_cache()
                
                # 성능 메트릭 수집
                self._collect_performance_metrics()
                
                # GC 실행
                if self._should_run_gc():
                    gc.collect()
                
                time.sleep(60)  # 1분마다 실행
                
            except Exception as e:
                logger.error(f"성능 최적화 루프 오류: {e}")
                time.sleep(60)
                
    def _optimize_memory_usage(self):
        """메모리 사용량 최적화"""
        try:
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > self.optimization_settings['max_memory_usage']:
                logger.warning(f"메모리 사용량이 높습니다: {memory_percent}%")
                
                # 오래된 캐시 정리
                self._cleanup_old_cache()
                
                # GC 강제 실행
                gc.collect()
                
        except Exception as e:
            logger.error(f"메모리 최적화 실패: {e}")
            
    def _should_run_gc(self) -> bool:
        """GC 실행 여부 결정"""
        try:
            memory_percent = psutil.virtual_memory().percent
            return memory_percent > 70  # 70% 이상일 때 GC 실행
        except:
            return False
            
    def _cleanup_expired_cache(self):
        """만료된 캐시 정리"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, timestamp in self.cache_timestamps.items():
            if (current_time - timestamp).total_seconds() > self.cache_ttl:
                expired_keys.append(key)
                
        for key in expired_keys:
            del self.cache[key]
            del self.cache_timestamps[key]
            
        if expired_keys:
            logger.info(f"만료된 캐시 {len(expired_keys)}개 정리")
            
    def _cleanup_old_cache(self):
        """오래된 캐시 정리"""
        # 가장 오래된 캐시 20% 제거
        if len(self.cache) > 50:
            sorted_keys = sorted(self.cache_timestamps.items(), key=lambda x: x[1])
            remove_count = len(sorted_keys) // 5
            
            for key, _ in sorted_keys[:remove_count]:
                del self.cache[key]
                del self.cache_timestamps[key]
                
            logger.info(f"오래된 캐시 {remove_count}개 정리")
            
    def _collect_performance_metrics(self):
        """성능 메트릭 수집"""
        try:
            # 시스템 메트릭
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent()
            
            self.performance_metrics['memory_usage'].append({
                'timestamp': datetime.now(),
                'usage': memory_percent
            })
            
            self.performance_metrics['cpu_usage'].append({
                'timestamp': datetime.now(),
                'usage': cpu_percent
            })
            
        except Exception as e:
            logger.error(f"성능 메트릭 수집 실패: {e}")
            
    def cache_result(self, key: str, result: Any, ttl: Optional[int] = None):
        """결과 캐싱"""
        if not self.optimization_settings['enable_caching']:
            return
            
        self.cache[key] = result
        self.cache_timestamps[key] = datetime.now()
        
    def get_cached_result(self, key: str) -> Optional[Any]:
        """캐시된 결과 조회"""
        if not self.optimization_settings['enable_caching']:
            return None
            
        if key in self.cache:
            timestamp = self.cache_timestamps.get(key)
            if timestamp and (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return self.cache[key]
            else:
                # 만료된 캐시 제거
                del self.cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
                    
        return None
        
    def record_execution_time(self, plugin_name: str, operation: str, execution_time: float):
        """실행 시간 기록"""
        key = f"{plugin_name}_{operation}"
        self.performance_metrics['execution_times'][key].append({
            'timestamp': datetime.now(),
            'execution_time': execution_time
        })
        
    def record_load_time(self, plugin_name: str, load_time: float):
        """로딩 시간 기록"""
        self.performance_metrics['load_times'][plugin_name].append({
            'timestamp': datetime.now(),
            'load_time': load_time
        })
        
    def record_error(self, plugin_name: str, error_type: str):
        """오류 기록"""
        self.performance_metrics['error_counts'][f"{plugin_name}_{error_type}"] += 1
        
    def record_success(self, plugin_name: str, operation: str):
        """성공 기록"""
        self.performance_metrics['success_counts'][f"{plugin_name}_{operation}"] += 1
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 조회"""
        summary = {
            'cache_stats': {
                'total_cached_items': len(self.cache),
                'cache_hit_rate': self._calculate_cache_hit_rate(),
                'memory_usage': self._get_current_memory_usage(),
                'cpu_usage': self._get_current_cpu_usage()
            },
            'plugin_performance': {},
            'system_health': self._get_system_health()
        }
        
        # 플러그인별 성능 통계
        for plugin_name in set([key.split('_')[0] for key in self.performance_metrics['load_times'].keys()]):
            summary['plugin_performance'][plugin_name] = {
                'avg_load_time': self._calculate_avg_load_time(plugin_name),
                'avg_execution_time': self._calculate_avg_execution_time(plugin_name),
                'error_rate': self._calculate_error_rate(plugin_name),
                'success_rate': self._calculate_success_rate(plugin_name)
            }
            
        return summary
        
    def _calculate_cache_hit_rate(self) -> float:
        """캐시 히트율 계산"""
        total_requests = sum(self.performance_metrics['success_counts'].values())
        cache_hits = len(self.cache)
        
        if total_requests == 0:
            return 0.0
            
        return (cache_hits / total_requests) * 100
        
    def _get_current_memory_usage(self) -> float:
        try:
            value = psutil.virtual_memory().percent
            return float(value) if isinstance(value, (int, float)) else 0.0
        except:
            return 0.0
            
    def _get_current_cpu_usage(self) -> float:
        try:
            value = psutil.cpu_percent()
            return float(value) if isinstance(value, (int, float)) else 0.0
        except:
            return 0.0
            
    def _calculate_avg_load_time(self, plugin_name: str) -> float:
        """평균 로딩 시간 계산"""
        load_times = self.performance_metrics['load_times'].get(plugin_name, [])
        if not load_times:
            return 0.0
            
        return sum(item['load_time'] for item in load_times) / len(load_times)
        
    def _calculate_avg_execution_time(self, plugin_name: str) -> float:
        """평균 실행 시간 계산"""
        execution_times = []
        for key, times in self.performance_metrics['execution_times'].items():
            if key.startswith(plugin_name):
                execution_times.extend(times)
                
        if not execution_times:
            return 0.0
            
        return sum(item['execution_time'] for item in execution_times) / len(execution_times)
        
    def _calculate_error_rate(self, plugin_name: str) -> float:
        """오류율 계산"""
        total_errors = sum(count for key, count in self.performance_metrics['error_counts'].items() 
                          if key.startswith(plugin_name))
        total_operations = sum(count for key, count in self.performance_metrics['success_counts'].items() 
                              if key.startswith(plugin_name))
        
        if total_operations == 0:
            return 0.0
            
        return (total_errors / (total_errors + total_operations)) * 100
        
    def _calculate_success_rate(self, plugin_name: str) -> float:
        """성공율 계산"""
        total_success = sum(count for key, count in self.performance_metrics['success_counts'].items() 
                           if key.startswith(plugin_name))
        total_errors = sum(count for key, count in self.performance_metrics['error_counts'].items() 
                          if key.startswith(plugin_name))
        
        total_operations = total_success + total_errors
        if total_operations == 0:
            return 0.0
            
        return (total_success / total_operations) * 100
        
    def _get_system_health(self) -> Dict[str, Any]:
        try:
            memory_percent = self._get_current_memory_usage()
            cpu_percent = self._get_current_cpu_usage()
            health_status = "healthy"
            if isinstance(memory_percent, (int, float)) and memory_percent > 80 or \
               isinstance(cpu_percent, (int, float)) and cpu_percent > 90:
                health_status = "warning"
            if isinstance(memory_percent, (int, float)) and memory_percent > 95 or \
               isinstance(cpu_percent, (int, float)) and cpu_percent > 95:
                health_status = "critical"
            return {
                'status': health_status,
                'memory_usage': memory_percent,
                'cpu_usage': cpu_percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# 전역 인스턴스
plugin_optimizer = PluginPerformanceOptimizer()

def performance_monitor(plugin_name: str, operation: str):
    """성능 모니터링 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                plugin_optimizer.record_execution_time(plugin_name, operation, execution_time)
                plugin_optimizer.record_success(plugin_name, operation)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                plugin_optimizer.record_execution_time(plugin_name, operation, execution_time)
                plugin_optimizer.record_error(plugin_name, type(e).__name__)
                raise
        return wrapper
    return decorator

def cache_result(ttl: int = 300):
    """캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 캐시된 결과 확인
            cached_result = plugin_optimizer.get_cached_result(cache_key)
            if cached_result is not None:
                return cached_result
                
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            plugin_optimizer.cache_result(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator 