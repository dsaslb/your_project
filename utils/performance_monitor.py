import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """시스템 성능 모니터링 클래스"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = defaultdict(lambda: deque(maxlen=max_history))
        self.api_response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.active_requests = 0
        self.total_requests = 0
        self.start_time = datetime.now()
        self.lock = threading.Lock()
        
        # 백그라운드 모니터링 시작
        self.monitoring_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitoring_thread.start()
    
    def _monitor_system(self):
        """시스템 리소스 모니터링"""
        while True:
            try:
                # CPU 사용률
                cpu_percent = psutil.cpu_percent(interval=1)
                self.record_metric('cpu_usage', cpu_percent)
                
                # 메모리 사용률
                memory = psutil.virtual_memory()
                self.record_metric('memory_usage', memory.percent)
                self.record_metric('memory_available', memory.available / (1024**3))  # GB
                
                # 디스크 사용률
                disk = psutil.disk_usage('/')
                self.record_metric('disk_usage', (disk.used / disk.total) * 100)
                
                # 네트워크 I/O
                network = psutil.net_io_counters()
                self.record_metric('network_bytes_sent', network.bytes_sent)
                self.record_metric('network_bytes_recv', network.bytes_recv)
                
                # 활성 연결 수
                connections = len(psutil.net_connections())
                self.record_metric('active_connections', connections)
                
                time.sleep(60)  # 1분마다 측정
                
            except Exception as e:
                logger.error(f"시스템 모니터링 오류: {e}")
                time.sleep(60)
    
    def record_metric(self, metric_name: str, value: float):
        """메트릭 기록"""
        with self.lock:
            timestamp = datetime.now()
            self.metrics_history[metric_name].append({
                'timestamp': timestamp,
                'value': value
            })
    
    def record_api_call(self, endpoint: str, response_time: float, status_code: int = 200):
        """API 호출 기록"""
        with self.lock:
            self.api_response_times[endpoint].append({
                'timestamp': datetime.now(),
                'response_time': response_time,
                'status_code': status_code
            })
            
            # 최대 1000개까지만 유지
            if len(self.api_response_times[endpoint]) > 1000:
                self.api_response_times[endpoint] = self.api_response_times[endpoint][-1000:]
            
            self.total_requests += 1
    
    def record_error(self, error_type: str, error_message: str = ""):
        """에러 기록"""
        with self.lock:
            self.error_counts[error_type] += 1
            logger.error(f"에러 기록: {error_type} - {error_message}")
    
    def start_request(self):
        """요청 시작"""
        with self.lock:
            self.active_requests += 1
    
    def end_request(self):
        """요청 종료"""
        with self.lock:
            self.active_requests = max(0, self.active_requests - 1)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """시스템 통계 조회"""
        with self.lock:
            uptime = datetime.now() - self.start_time
            
            # CPU 및 메모리 현재 상태
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # API 응답 시간 통계
            api_stats = {}
            for endpoint, times in self.api_response_times.items():
                if times:
                    response_times = [t['response_time'] for t in times]
                    api_stats[endpoint] = {
                        'count': len(times),
                        'avg_response_time': sum(response_times) / len(response_times),
                        'min_response_time': min(response_times),
                        'max_response_time': max(response_times),
                        'recent_avg': sum(response_times[-10:]) / min(len(response_times), 10)
                    }
            
            return {
                'uptime': str(uptime),
                'uptime_seconds': uptime.total_seconds(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage': (disk.used / disk.total) * 100,
                'active_requests': self.active_requests,
                'total_requests': self.total_requests,
                'error_counts': dict(self.error_counts),
                'api_stats': api_stats
            }
    
    def get_metric_history(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """메트릭 히스토리 조회"""
        with self.lock:
            if metric_name not in self.metrics_history:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            history = []
            
            for entry in self.metrics_history[metric_name]:
                if entry['timestamp'] >= cutoff_time:
                    history.append({
                        'timestamp': entry['timestamp'].isoformat(),
                        'value': entry['value']
                    })
            
            return history
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """성능 알림 생성"""
        alerts = []
        
        # CPU 사용률 알림
        cpu_history = self.get_metric_history('cpu_usage', hours=1)
        if cpu_history:
            recent_cpu = sum(entry['value'] for entry in cpu_history[-5:]) / len(cpu_history[-5:])
            if recent_cpu > 80:
                alerts.append({
                    'type': 'high_cpu_usage',
                    'severity': 'warning',
                    'message': f'CPU 사용률이 높습니다: {recent_cpu:.1f}%',
                    'value': recent_cpu,
                    'threshold': 80
                })
        
        # 메모리 사용률 알림
        memory_history = self.get_metric_history('memory_usage', hours=1)
        if memory_history:
            recent_memory = sum(entry['value'] for entry in memory_history[-5:]) / len(memory_history[-5:])
            if recent_memory > 85:
                alerts.append({
                    'type': 'high_memory_usage',
                    'severity': 'warning',
                    'message': f'메모리 사용률이 높습니다: {recent_memory:.1f}%',
                    'value': recent_memory,
                    'threshold': 85
                })
        
        # API 응답 시간 알림
        for endpoint, stats in self.get_system_stats()['api_stats'].items():
            if stats['avg_response_time'] > 2.0:  # 2초 이상
                alerts.append({
                    'type': 'slow_api_response',
                    'severity': 'warning',
                    'message': f'API 응답이 느립니다: {endpoint} ({stats["avg_response_time"]:.2f}s)',
                    'endpoint': endpoint,
                    'response_time': stats['avg_response_time'],
                    'threshold': 2.0
                })
        
        # 에러율 알림
        total_requests = self.get_system_stats()['total_requests']
        total_errors = sum(self.error_counts.values())
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            if error_rate > 5:  # 5% 이상
                alerts.append({
                    'type': 'high_error_rate',
                    'severity': 'error',
                    'message': f'에러율이 높습니다: {error_rate:.1f}%',
                    'value': error_rate,
                    'threshold': 5
                })
        
        return alerts
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        stats = self.get_system_stats()
        alerts = self.get_performance_alerts()
        
        # 성능 점수 계산 (0-100)
        performance_score = 100
        
        # CPU 점수
        if stats['cpu_usage'] > 80:
            performance_score -= 20
        elif stats['cpu_usage'] > 60:
            performance_score -= 10
        
        # 메모리 점수
        if stats['memory_usage'] > 85:
            performance_score -= 20
        elif stats['memory_usage'] > 70:
            performance_score -= 10
        
        # API 응답 시간 점수
        slow_apis = sum(1 for api_stats in stats['api_stats'].values() 
                       if api_stats['avg_response_time'] > 2.0)
        performance_score -= slow_apis * 5
        
        # 에러율 점수
        if stats['total_requests'] > 0:
            error_rate = (sum(stats['error_counts'].values()) / stats['total_requests']) * 100
            if error_rate > 5:
                performance_score -= 20
            elif error_rate > 2:
                performance_score -= 10
        
        performance_score = max(0, performance_score)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'performance_score': performance_score,
            'system_stats': stats,
            'alerts': alerts,
            'recommendations': self._generate_recommendations(stats, alerts)
        }
    
    def _generate_recommendations(self, stats: Dict[str, Any], alerts: List[Dict[str, Any]]) -> List[str]:
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        if stats['cpu_usage'] > 80:
            recommendations.append("CPU 사용률이 높습니다. 서버 리소스를 확장하거나 부하를 분산하는 것을 고려하세요.")
        
        if stats['memory_usage'] > 85:
            recommendations.append("메모리 사용률이 높습니다. 메모리 누수를 확인하거나 메모리를 증설하세요.")
        
        slow_apis = [endpoint for endpoint, api_stats in stats['api_stats'].items() 
                    if api_stats['avg_response_time'] > 2.0]
        if slow_apis:
            recommendations.append(f"다음 API들의 응답 시간을 최적화하세요: {', '.join(slow_apis)}")
        
        if stats['total_requests'] > 0:
            error_rate = (sum(stats['error_counts'].values()) / stats['total_requests']) * 100
            if error_rate > 5:
                recommendations.append("에러율이 높습니다. 로그를 확인하여 문제를 해결하세요.")
        
        if not recommendations:
            recommendations.append("시스템 성능이 양호합니다. 현재 상태를 유지하세요.")
        
        return recommendations

# 전역 성능 모니터 인스턴스
performance_monitor = PerformanceMonitor()

def monitor_api_call(endpoint: str):
    """API 호출 모니터링 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            performance_monitor.start_request()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                performance_monitor.record_api_call(endpoint, response_time, 200)
                return result
            except Exception as e:
                response_time = time.time() - start_time
                performance_monitor.record_api_call(endpoint, response_time, 500)
                performance_monitor.record_error(f"{endpoint}_error", str(e))
                raise
            finally:
                performance_monitor.end_request()
        
        return wrapper
    return decorator

def get_performance_metrics() -> Dict[str, Any]:
    """성능 메트릭 조회"""
    return performance_monitor.get_performance_report()

def get_system_health() -> Dict[str, Any]:
    """시스템 건강 상태 조회"""
    stats = performance_monitor.get_system_stats()
    alerts = performance_monitor.get_performance_alerts()
    
    # 건강 상태 결정
    if any(alert['severity'] == 'error' for alert in alerts):
        health_status = 'critical'
    elif any(alert['severity'] == 'warning' for alert in alerts):
        health_status = 'warning'
    else:
        health_status = 'healthy'
    
    return {
        'status': health_status,
        'timestamp': datetime.now().isoformat(),
        'stats': stats,
        'alerts': alerts
    } 