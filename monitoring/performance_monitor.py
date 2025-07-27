"""
성능 모니터링 및 프로파일링 시스템
"""

import time
import psutil
import threading
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import functools
import gc
import os
import sys

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """성능 메트릭"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_available: int
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    request_count: int
    response_time_avg: float
    error_count: int

@dataclass
class FunctionProfile:
    """함수 프로파일 정보"""
    function_name: str
    module_name: str
    call_count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    last_called: str

@dataclass
class DatabaseQueryProfile:
    """데이터베이스 쿼리 프로파일"""
    query: str
    execution_count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    last_executed: str
    slow_query: bool

class PerformanceMonitor:
    """성능 모니터링 시스템"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'monitoring_interval': 30,  # 30초마다 모니터링
            'history_size': 1000,       # 최대 1000개 메트릭 저장
            'alert_thresholds': {
                'cpu_percent': 80,
                'memory_percent': 85,
                'disk_usage_percent': 90,
                'response_time_avg': 2.0,  # 2초
                'error_rate': 5.0  # 5%
            }
        }
        
        self.metrics_history = deque(maxlen=self.config['history_size'])
        self.function_profiles = defaultdict(lambda: {
            'call_count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'last_called': None
        })
        self.database_profiles = defaultdict(lambda: {
            'execution_count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'last_executed': None
        })
        self.request_stats = {
            'total_requests': 0,
            'total_response_time': 0.0,
            'error_count': 0,
            'active_connections': 0
        }
        
        self.monitoring_active = False
        self.monitor_thread = None
        self.alert_callbacks = []
        
        # 네트워크 통계 초기화
        self.last_network_stats = psutil.net_io_counters()
        self.last_network_check = time.time()
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            logger.warning("모니터링이 이미 실행 중입니다.")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("성능 모니터링이 시작되었습니다.")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("성능 모니터링이 중지되었습니다.")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                metric = self._collect_metrics()
                self.metrics_history.append(metric)
                
                # 알림 체크
                self._check_alerts(metric)
                
                time.sleep(self.config['monitoring_interval'])
            except Exception as e:
                logger.error(f"모니터링 중 오류 발생: {e}")
                time.sleep(5)
    
    def _collect_metrics(self) -> PerformanceMetric:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            
            # 네트워크 통계
            current_network = psutil.net_io_counters()
            current_time = time.time()
            
            # 네트워크 속도 계산
            time_diff = current_time - self.last_network_check
            bytes_sent = (current_network.bytes_sent - self.last_network_stats.bytes_sent) / time_diff
            bytes_recv = (current_network.bytes_recv - self.last_network_stats.bytes_recv) / time_diff
            
            self.last_network_stats = current_network
            self.last_network_check = current_time
            
            # 응답 시간 평균 계산
            response_time_avg = 0.0
            if self.request_stats['total_requests'] > 0:
                response_time_avg = self.request_stats['total_response_time'] / self.request_stats['total_requests']
            
            metric = PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_available=memory.available,
                disk_usage_percent=disk.percent,
                network_bytes_sent=int(bytes_sent),
                network_bytes_recv=int(bytes_recv),
                active_connections=self.request_stats['active_connections'],
                request_count=self.request_stats['total_requests'],
                response_time_avg=response_time_avg,
                error_count=self.request_stats['error_count']
            )
            
            return metric
            
        except Exception as e:
            logger.error(f"메트릭 수집 실패: {e}")
            # 기본 메트릭 반환
            return PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used=0,
                memory_available=0,
                disk_usage_percent=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                active_connections=0,
                request_count=0,
                response_time_avg=0.0,
                error_count=0
            )
    
    def _check_alerts(self, metric: PerformanceMetric):
        """알림 조건 확인"""
        thresholds = self.config['alert_thresholds']
        alerts = []
        
        if metric.cpu_percent > thresholds['cpu_percent']:
            alerts.append(f"CPU 사용률이 높습니다: {metric.cpu_percent:.1f}%")
        
        if metric.memory_percent > thresholds['memory_percent']:
            alerts.append(f"메모리 사용률이 높습니다: {metric.memory_percent:.1f}%")
        
        if metric.disk_usage_percent > thresholds['disk_usage_percent']:
            alerts.append(f"디스크 사용률이 높습니다: {metric.disk_usage_percent:.1f}%")
        
        if metric.response_time_avg > thresholds['response_time_avg']:
            alerts.append(f"응답 시간이 느립니다: {metric.response_time_avg:.2f}초")
        
        if metric.request_count > 0:
            error_rate = (metric.error_count / metric.request_count) * 100
            if error_rate > thresholds['error_rate']:
                alerts.append(f"오류율이 높습니다: {error_rate:.1f}%")
        
        # 알림 콜백 실행
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert, metric)
                except Exception as e:
                    logger.error(f"알림 콜백 실행 실패: {e}")
    
    def add_alert_callback(self, callback: Callable[[str, PerformanceMetric], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def record_request(self, response_time: float, is_error: bool = False):
        """요청 기록"""
        self.request_stats['total_requests'] += 1
        self.request_stats['total_response_time'] += response_time
        if is_error:
            self.request_stats['error_count'] += 1
    
    def set_active_connections(self, count: int):
        """활성 연결 수 설정"""
        self.request_stats['active_connections'] = count
    
    def profile_function(self, func):
        """함수 프로파일링 데코레이터"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                self._record_function_profile(func, execution_time)
        
        return wrapper
    
    def _record_function_profile(self, func, execution_time: float):
        """함수 프로파일 기록"""
        function_key = f"{func.__module__}.{func.__name__}"
        profile = self.function_profiles[function_key]
        
        profile['call_count'] += 1
        profile['total_time'] += execution_time
        profile['min_time'] = min(profile['min_time'], execution_time)
        profile['max_time'] = max(profile['max_time'], execution_time)
        profile['last_called'] = datetime.now().isoformat()
    
    def record_database_query(self, query: str, execution_time: float):
        """데이터베이스 쿼리 프로파일 기록"""
        profile = self.database_profiles[query]
        
        profile['execution_count'] += 1
        profile['total_time'] += execution_time
        profile['min_time'] = min(profile['min_time'], execution_time)
        profile['max_time'] = max(profile['max_time'], execution_time)
        profile['last_executed'] = datetime.now().isoformat()
        profile['slow_query'] = execution_time > 1.0  # 1초 이상은 느린 쿼리
    
    def get_current_metrics(self) -> Optional[PerformanceMetric]:
        """현재 메트릭 조회"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_history(self, hours: int = 24) -> List[PerformanceMetric]:
        """메트릭 히스토리 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metric for metric in self.metrics_history
            if datetime.fromisoformat(metric.timestamp) > cutoff_time
        ]
    
    def get_function_profiles(self) -> List[FunctionProfile]:
        """함수 프로파일 조회"""
        profiles = []
        for function_key, profile in self.function_profiles.items():
            if profile['call_count'] > 0:
                module_name, function_name = function_key.rsplit('.', 1)
                profiles.append(FunctionProfile(
                    function_name=function_name,
                    module_name=module_name,
                    call_count=profile['call_count'],
                    total_time=profile['total_time'],
                    avg_time=profile['total_time'] / profile['call_count'],
                    min_time=profile['min_time'],
                    max_time=profile['max_time'],
                    last_called=profile['last_called']
                ))
        
        # 총 실행 시간 기준 정렬
        profiles.sort(key=lambda x: x.total_time, reverse=True)
        return profiles
    
    def get_database_profiles(self) -> List[DatabaseQueryProfile]:
        """데이터베이스 쿼리 프로파일 조회"""
        profiles = []
        for query, profile in self.database_profiles.items():
            if profile['execution_count'] > 0:
                profiles.append(DatabaseQueryProfile(
                    query=query,
                    execution_count=profile['execution_count'],
                    total_time=profile['total_time'],
                    avg_time=profile['total_time'] / profile['execution_count'],
                    min_time=profile['min_time'],
                    max_time=profile['max_time'],
                    last_executed=profile['last_executed'],
                    slow_query=profile['slow_query']
                ))
        
        # 총 실행 시간 기준 정렬
        profiles.sort(key=lambda x: x.total_time, reverse=True)
        return profiles
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 조회"""
        current_metric = self.get_current_metrics()
        if not current_metric:
            return {}
        
        # 최근 1시간 메트릭
        recent_metrics = self.get_metrics_history(hours=1)
        
        if not recent_metrics:
            return {}
        
        # 평균값 계산
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics)
        
        # 오류율 계산
        total_requests = sum(m.request_count for m in recent_metrics)
        total_errors = sum(m.error_count for m in recent_metrics)
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'current': {
                'cpu_percent': current_metric.cpu_percent,
                'memory_percent': current_metric.memory_percent,
                'disk_usage_percent': current_metric.disk_usage_percent,
                'active_connections': current_metric.active_connections,
                'response_time_avg': current_metric.response_time_avg
            },
            'averages_1h': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory,
                'response_time_avg': avg_response_time,
                'error_rate': error_rate
            },
            'system_health': {
                'status': 'healthy' if avg_cpu < 70 and avg_memory < 80 else 'warning',
                'recommendations': self._generate_recommendations(avg_cpu, avg_memory, error_rate)
            }
        }
    
    def _generate_recommendations(self, avg_cpu: float, avg_memory: float, error_rate: float) -> List[str]:
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        if avg_cpu > 80:
            recommendations.append("CPU 사용률이 높습니다. 서버 리소스를 확장하거나 코드 최적화를 고려하세요.")
        elif avg_cpu > 60:
            recommendations.append("CPU 사용률이 중간 수준입니다. 모니터링을 지속하세요.")
        
        if avg_memory > 85:
            recommendations.append("메모리 사용률이 높습니다. 메모리 누수를 확인하거나 메모리를 확장하세요.")
        elif avg_memory > 70:
            recommendations.append("메모리 사용률이 중간 수준입니다. 메모리 사용량을 모니터링하세요.")
        
        if error_rate > 10:
            recommendations.append("오류율이 높습니다. 로그를 확인하고 오류 원인을 분석하세요.")
        elif error_rate > 5:
            recommendations.append("오류율이 증가하고 있습니다. 오류 모니터링을 강화하세요.")
        
        if not recommendations:
            recommendations.append("시스템이 정상적으로 작동하고 있습니다.")
        
        return recommendations
    
    def export_metrics(self, filename: str = None) -> str:
        """메트릭 내보내기"""
        if filename is None:
            filename = f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'metrics': [asdict(metric) for metric in self.metrics_history],
            'function_profiles': [asdict(profile) for profile in self.get_function_profiles()],
            'database_profiles': [asdict(profile) for profile in self.get_database_profiles()],
            'performance_summary': self.get_performance_summary()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"성능 메트릭이 내보내졌습니다: {filename}")
            return filename
        except Exception as e:
            logger.error(f"메트릭 내보내기 실패: {e}")
            return None
    
    def clear_history(self):
        """히스토리 초기화"""
        self.metrics_history.clear()
        self.function_profiles.clear()
        self.database_profiles.clear()
        logger.info("성능 모니터링 히스토리가 초기화되었습니다.")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """메모리 사용량 상세 정보"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'physical': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'percent': swap.percent
                }
            }
        except Exception as e:
            logger.error(f"메모리 사용량 조회 실패: {e}")
            return {}
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """디스크 사용량 상세 정보"""
        try:
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            return {
                'usage': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'io': {
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                }
            }
        except Exception as e:
            logger.error(f"디스크 사용량 조회 실패: {e}")
            return {}

# 전역 성능 모니터 인스턴스
performance_monitor = PerformanceMonitor() 