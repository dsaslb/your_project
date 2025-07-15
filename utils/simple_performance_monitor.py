
# -*- coding: utf-8 -*-
"""
성능 모니터링 유틸리티
Redis 없이도 작동하는 성능 모니터링
"""

import time
import logging
import threading
from functools import wraps
from typing import Dict, Any, Optional
from collections import defaultdict, deque
import psutil
import os

logger = logging.getLogger(__name__)

class SimplePerformanceMonitor:
    """간단한 성능 모니터링 클래스"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.response_times = defaultdict(lambda: deque(maxlen=max_history))
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.slow_queries = deque(maxlen=100)
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 60):
        """모니터링 시작"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("성능 모니터링 시작됨")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("성능 모니터링 중지됨")
    
    def _monitor_loop(self, interval: int):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                self._log_system_stats()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                time.sleep(interval)
    
    def _log_system_stats(self):
        """시스템 통계 로깅"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            logger.info(f"시스템 상태 - CPU: {cpu_percent}%, "
                       f"메모리: {memory.percent}%, "
                       f"활성 요청: {sum(self.request_counts.values())}")
        except Exception as e:
            logger.error(f"시스템 통계 수집 오류: {e}")
    
    def record_request(self, endpoint: str, method: str, response_time: float, 
                      status_code: int, error: Optional[str] = None):
        """요청 기록"""
        key = f"{method} {endpoint}"
        
        self.request_counts[key] += 1
        self.response_times[key].append(response_time)
        
        if status_code >= 400:
            self.error_counts[key] += 1
        
        if response_time > 2.0:  # 2초 이상
            self.slow_queries.append({
                'endpoint': endpoint,
                'method': method,
                'response_time': response_time,
                'timestamp': time.time()
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 조회"""
        stats = {
            'total_requests': sum(self.request_counts.values()),
            'total_errors': sum(self.error_counts.values()),
            'slow_queries_count': len(self.slow_queries),
            'endpoints': {}
        }
        
        for key in self.request_counts:
            response_times = list(self.response_times[key])
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                stats['endpoints'][key] = {
                    'requests': self.request_counts[key],
                    'errors': self.error_counts[key],
                    'avg_response_time': round(avg_time, 3),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times)
                }
        
        return stats
    
    def get_health_status(self) -> Dict[str, Any]:
        """헬스 상태 조회"""
        stats = self.get_stats()
        
        # 성능 등급 평가
        avg_response_time = 0
        if stats['endpoints']:
            total_time = sum(ep['avg_response_time'] for ep in stats['endpoints'].values())
            avg_response_time = total_time / len(stats['endpoints'])
        
        if avg_response_time < 1.0:
            status = "healthy"
        elif avg_response_time < 2.0:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'status': status,
            'avg_response_time': round(avg_response_time, 3),
            'total_requests': stats['total_requests'],
            'error_rate': (stats['total_errors'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0,
            'slow_queries': len(self.slow_queries)
        }

# 전역 인스턴스
performance_monitor = SimplePerformanceMonitor()

def monitor_performance(f):
    """성능 모니터링 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        error = None
        status_code = 200
        
        try:
            result = f(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            status_code = 500
            raise
        finally:
            response_time = time.time() - start_time
            endpoint = f.__name__
            method = "GET"  # 기본값
            
            performance_monitor.record_request(
                endpoint, method, response_time, status_code, error
            )
    
    return decorated_function
