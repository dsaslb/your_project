import threading
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import psutil
import time
import platform
import sys
from flask import request
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """시스템 성능 모니터링 클래스"""

    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'network_io': [],
            'slow_queries': [],
            'api_response_times': [],
            'error_counts': []
        }
        self.max_history = 1000  # 최대 기록 수
        self.monitoring_active = False
        self.monitor_thread = None

    def start_monitoring(self, interval=60):
        """성능 모니터링 시작"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("성능 모니터링이 시작되었습니다.")

    def stop_monitoring(self):
        """성능 모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("성능 모니터링이 중지되었습니다.")

    def _monitor_loop(self,  interval: int):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"모니터링 오류: {str(e)}")
                time.sleep(interval)

    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        timestamp = datetime.now()

        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        self._add_metric('cpu_usage', {
            'timestamp': timestamp,
            'value': cpu_percent
        })

        # 메모리 사용률
        memory = psutil.virtual_memory()
        self._add_metric('memory_usage', {
            'timestamp': timestamp,
            'value': memory.percent,
            'total': memory.total,
            'available': memory.available
        })

        # 디스크 사용률
        disk = psutil.disk_usage('/')
        self._add_metric('disk_usage', {
            'timestamp': timestamp,
            'value': (disk.used / disk.total) * 100,
            'total': disk.total,
            'used': disk.used,
            'free': disk.free
        })

        # 네트워크 I/O
        network = psutil.net_io_counters()
        self._add_metric('network_io', {
            'timestamp': timestamp,
            'bytes_sent': getattr(network, 'bytes_sent', 0),
            'bytes_recv': getattr(network, 'bytes_recv', 0),
            'packets_sent': getattr(network, 'packets_sent', 0),
            'packets_recv': getattr(network, 'packets_recv', 0)
        })

    def _add_metric(self,  metric_type: str,  data: Dict[str,  Any]):
        """
        메트릭 추가
        """
        if metric_type in self.metrics:
            self.metrics[metric_type].append(data)
            # 최대 기록 수 제한
            if len(self.metrics[metric_type]) > self.max_history:
                self.metrics[metric_type].pop(0)

    def record_slow_query(self,  query: str,  execution_time: float, timestamp=None):
        """느린 쿼리 기록"""
        if timestamp is None:
            timestamp = datetime.now()

        self._add_metric('slow_queries', {
            'timestamp': timestamp,
            'query': query,
            'execution_time': execution_time
        })

        if execution_time > 5.0:  # 5초 이상 걸리는 쿼리 경고
            logger.warning(f"매우 느린 쿼리 감지: {execution_time:.2f}초 - {query[:100] if query is not None else None}...")

    def record_api_response_time(self,  endpoint: str,  method: str,  response_time: float, status_code=None):
        """API 응답 시간 기록"""
        self._add_metric('api_response_times', {
            'timestamp': datetime.now(),
            'endpoint': endpoint,
            'method': method,
            'response_time': response_time,
            'status_code': status_code if status_code is not None else 0
        })

    def record_error(self,  error_type: str,  error_message: str,  context: Optional[Dict[str, Any]] = None):
        """오류 기록"""
        self._add_metric('error_counts', {
            'timestamp': datetime.now(),
            'error_type': error_type,
            'error_message': error_message,
            'context': context if context is not None else {}
        })

    def get_performance_summary(self, hours=24) -> Dict[str, Any]:
        """
        성능 요약 정보
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        summary = {
            'monitoring_active': self.monitoring_active,
            'current_time': datetime.now(),
            'summary_period_hours': hours
        }
        # CPU 사용률 평균
        recent_cpu = [m for m in self.metrics['cpu_usage'] if m['timestamp'] > cutoff_time]
        if recent_cpu:
            summary['avg_cpu_usage'] = float(sum(m['value'] for m in recent_cpu)) / len(recent_cpu)  # pyright: ignore
            summary['max_cpu_usage'] = float(max(m['value'] for m in recent_cpu))  # pyright: ignore
        # 메모리 사용률 평균
        recent_memory = [m for m in self.metrics['memory_usage'] if m['timestamp'] > cutoff_time]
        if recent_memory:
            summary['avg_memory_usage'] = float(sum(m['value'] for m in recent_memory)) / len(recent_memory)  # pyright: ignore
            summary['max_memory_usage'] = float(max(m['value'] for m in recent_memory))  # pyright: ignore
        # 느린 쿼리 통계
        recent_slow_queries = [m for m in self.metrics['slow_queries'] if m['timestamp'] > cutoff_time]
        summary['slow_query_count'] = len(recent_slow_queries)
        if recent_slow_queries:
            summary['avg_slow_query_time'] = sum(m['execution_time'] for m in recent_slow_queries) / len(recent_slow_queries)
            summary['max_slow_query_time'] = max(m['execution_time'] for m in recent_slow_queries)
        # API 응답 시간 통계
        recent_api_times = [m for m in self.metrics['api_response_times'] if m['timestamp'] > cutoff_time]
        summary['api_request_count'] = len(recent_api_times)
        if recent_api_times:
            summary['avg_api_response_time'] = sum(m['response_time'] for m in recent_api_times) / len(recent_api_times)
            summary['max_api_response_time'] = max(m['response_time'] for m in recent_api_times)
        # 오류 통계
        recent_errors = [m for m in self.metrics['error_counts'] if m['timestamp'] > cutoff_time]
        summary['error_count'] = len(recent_errors)
        return summary

    def get_alerts(self) -> List[Dict[str, Any]]:
        """성능 알림 생성"""
        alerts = []
        summary = self.get_performance_summary(1)  # 최근 1시간 기준

        # CPU 사용률 알림
        if 'avg_cpu_usage' in summary and summary['avg_cpu_usage'] > 80:
            alerts.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f"CPU 사용률이 높습니다: {summary['avg_cpu_usage']:.1f}%",
                'timestamp': datetime.now()
            })

        # 메모리 사용률 알림
        if 'avg_memory_usage' in summary and summary['avg_memory_usage'] > 85:
            alerts.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f"메모리 사용률이 높습니다: {summary['avg_memory_usage']:.1f}%",
                'timestamp': datetime.now()
            })

        # 느린 쿼리 알림
        if summary.get('slow_query_count', 0) > 10:
            alerts.append({
                'type': 'many_slow_queries',
                'severity': 'warning',
                'message': f"느린 쿼리가 많이 발생했습니다: {summary['slow_query_count']}개",
                'timestamp': datetime.now()
            })

        # 오류 알림
        if summary.get('error_count', 0) > 5:
            alerts.append({
                'type': 'many_errors',
                'severity': 'error',
                'message': f"오류가 많이 발생했습니다: {summary['error_count']}개",
                'timestamp': datetime.now()
            })

        return alerts


# 전역 성능 모니터 인스턴스
performance_monitor = PerformanceMonitor()


def monitor_performance(func):
    """성능 모니터링 데코레이터"""
    @wraps(func)
    def wrapper(*args,  **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # API 응답 시간 기록
            if hasattr(func, '__name__'):
                performance_monitor.record_api_response_time(
                    endpoint=func.__name__,
                    method='GET',
                    response_time=execution_time
                )

            return result
        except Exception as e:
            execution_time = time.time() - start_time
            performance_monitor.record_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={'function': func.__name__, 'execution_time': execution_time}
            )
            raise

    return wrapper


def monitor_query_performance(func):
    """쿼리 성능 모니터링 데코레이터"""
    @wraps(func)
    def wrapper(*args,  **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # 느린 쿼리 기록
            if execution_time > 1.0:  # 1초 이상
                performance_monitor.record_slow_query(
                    query=str(func.__name__),
                    execution_time=execution_time
                )

            return result
        except Exception as e:
            execution_time = time.time() - start_time
            performance_monitor.record_error(
                error_type='query_error',
                error_message=str(e),
                context={'function': func.__name__, 'execution_time': execution_time}
            )
            raise

    return wrapper


class ResourceMonitor:
    """리소스 모니터링 클래스"""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """시스템 정보 조회"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total,
            'platform': platform.system(),
            'python_version': sys.version
        }

    @staticmethod
    def get_process_info() -> Dict[str, Any]:
        """현재 프로세스 정보 조회"""
        process = psutil.Process()
        return {
            'pid': process.pid,
            'name': process.name(),
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_info': process.memory_info()._asdict(),
            'num_threads': process.num_threads(),
            'create_time': datetime.fromtimestamp(process.create_time())
        }

    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """네트워크 정보 조회"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }
