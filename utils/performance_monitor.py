"""
성능 모니터링 및 분석 시스템
메트릭 수집, 성능 분석, 병목 지점 탐지
"""

import logging
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import redis
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """성능 메트릭"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_io_read: float
    disk_io_write: float
    network_sent: float
    network_recv: float
    active_connections: int
    request_count: int
    response_time_avg: float
    error_count: int

@dataclass
class RequestMetric:
    """요청 메트릭"""
    timestamp: float
    method: str
    endpoint: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    user_id: Optional[str] = None

class PerformanceMonitor:
    """성능 모니터링"""
    
    def __init__(self, redis_client: redis.Redis, sample_interval: int = 60):
        self.redis_client = redis_client
        self.sample_interval = sample_interval
        self.metrics_history = deque(maxlen=1440)  # 24시간 (1분 간격)
        self.request_history = deque(maxlen=10000)  # 최근 10,000 요청
        self.monitoring_active = False
        self.monitor_thread = None
        
        # 성능 임계값
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 2.0,
            'error_rate': 5.0
        }
        
        # 알림 콜백
        self.alert_callbacks: List[Callable] = []
    
    def start_monitoring(self):
        """모니터링 시작"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("성능 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("성능 모니터링 중지")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                metric = self._collect_system_metrics()
                self.metrics_history.append(metric)
                
                # 임계값 체크
                self._check_thresholds(metric)
                
                # Redis에 메트릭 저장
                self._save_metric_to_redis(metric)
                
                time.sleep(self.sample_interval)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(5)
    
    def _collect_system_metrics(self) -> PerformanceMetric:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 디스크 I/O
            disk_io = psutil.disk_io_counters()
            disk_io_read = disk_io.read_bytes if disk_io else 0
            disk_io_write = disk_io.write_bytes if disk_io else 0
            
            # 네트워크 I/O
            network_io = psutil.net_io_counters()
            network_sent = network_io.bytes_sent
            network_recv = network_io.bytes_recv
            
            # 연결 수 (간단한 추정)
            active_connections = len(psutil.net_connections())
            
            # 요청 통계 (Redis에서 조회)
            request_stats = self._get_request_stats()
            
            return PerformanceMetric(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_io_read=disk_io_read,
                disk_io_write=disk_io_write,
                network_sent=network_sent,
                network_recv=network_recv,
                active_connections=active_connections,
                request_count=request_stats.get('count', 0),
                response_time_avg=request_stats.get('avg_time', 0),
                error_count=request_stats.get('error_count', 0)
            )
            
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
            return PerformanceMetric(
                timestamp=time.time(),
                cpu_usage=0,
                memory_usage=0,
                disk_io_read=0,
                disk_io_write=0,
                network_sent=0,
                network_recv=0,
                active_connections=0,
                request_count=0,
                response_time_avg=0,
                error_count=0
            )
    
    def _get_request_stats(self) -> Dict:
        """요청 통계 조회"""
        try:
            # Redis에서 요청 통계 조회
            current_time = time.time()
            window_start = current_time - 60  # 1분 윈도우
            
            # 최근 요청들 필터링
            recent_requests = [
                req for req in self.request_history
                if req.timestamp >= window_start
            ]
            
            if not recent_requests:
                return {'count': 0, 'avg_time': 0, 'error_count': 0}
            
            count = len(recent_requests)
            avg_time = statistics.mean(req.response_time for req in recent_requests)
            error_count = len([req for req in recent_requests if req.status_code >= 400])
            
            return {
                'count': count,
                'avg_time': avg_time,
                'error_count': error_count
            }
            
        except Exception as e:
            logger.error(f"요청 통계 조회 실패: {e}")
            return {'count': 0, 'avg_time': 0, 'error_count': 0}
    
    def _check_thresholds(self, metric: PerformanceMetric):
        """임계값 체크"""
        try:
            alerts = []
            
            # CPU 사용률 체크
            if metric.cpu_usage > self.thresholds['cpu_usage']:
                alerts.append(f"CPU 사용률 높음: {metric.cpu_usage:.1f}%")
            
            # 메모리 사용률 체크
            if metric.memory_usage > self.thresholds['memory_usage']:
                alerts.append(f"메모리 사용률 높음: {metric.memory_usage:.1f}%")
            
            # 응답 시간 체크
            if metric.response_time_avg > self.thresholds['response_time']:
                alerts.append(f"응답 시간 높음: {metric.response_time_avg:.2f}s")
            
            # 에러율 체크
            if metric.request_count > 0:
                error_rate = (metric.error_count / metric.request_count) * 100
                if error_rate > self.thresholds['error_rate']:
                    alerts.append(f"에러율 높음: {error_rate:.1f}%")
            
            # 알림 전송
            if alerts:
                self._send_alerts(alerts, metric)
                
        except Exception as e:
            logger.error(f"임계값 체크 실패: {e}")
    
    def _send_alerts(self, alerts: List[str], metric: PerformanceMetric):
        """알림 전송"""
        try:
            alert_message = {
                'timestamp': datetime.now().isoformat(),
                'alerts': alerts,
                'metric': asdict(metric)
            }
            
            # 알림 콜백 실행
            for callback in self.alert_callbacks:
                try:
                    callback(alert_message)
                except Exception as e:
                    logger.error(f"알림 콜백 실행 실패: {e}")
            
            # Redis에 알림 저장
            self.redis_client.lpush('performance_alerts', json.dumps(alert_message))
            self.redis_client.ltrim('performance_alerts', 0, 99)  # 최근 100개만 유지
            
            logger.warning(f"성능 알림: {', '.join(alerts)}")
            
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
    
    def record_request(self, request_metric: RequestMetric):
        """요청 메트릭 기록"""
        try:
            self.request_history.append(request_metric)
            
            # Redis에 요청 통계 업데이트
            self._update_request_stats(request_metric)
            
        except Exception as e:
            logger.error(f"요청 메트릭 기록 실패: {e}")
    
    def _update_request_stats(self, request_metric: RequestMetric):
        """요청 통계 업데이트"""
        try:
            # 엔드포인트별 통계
            endpoint_key = f"stats:endpoint:{request_metric.endpoint}"
            
            # 요청 수 증가
            self.redis_client.hincrby(endpoint_key, 'count', 1)
            
            # 응답 시간 업데이트
            self.redis_client.hincrbyfloat(endpoint_key, 'total_time', request_metric.response_time)
            
            # 에러 수 증가
            if request_metric.status_code >= 400:
                self.redis_client.hincrby(endpoint_key, 'error_count', 1)
            
            # 최근 요청 시간 업데이트
            self.redis_client.hset(endpoint_key, 'last_request', request_metric.timestamp)
            
        except Exception as e:
            logger.error(f"요청 통계 업데이트 실패: {e}")
    
    def _save_metric_to_redis(self, metric: PerformanceMetric):
        """메트릭을 Redis에 저장"""
        try:
            metric_data = asdict(metric)
            metric_data['timestamp'] = datetime.fromtimestamp(metric.timestamp).isoformat()
            
            # 최근 메트릭 저장
            self.redis_client.set('current_metrics', json.dumps(metric_data))
            
            # 메트릭 히스토리 저장
            self.redis_client.lpush('metrics_history', json.dumps(metric_data))
            self.redis_client.ltrim('metrics_history', 0, 1439)  # 24시간 (1440개)
            
        except Exception as e:
            logger.error(f"메트릭 Redis 저장 실패: {e}")
    
    def get_performance_report(self, hours: int = 24) -> Dict:
        """성능 리포트 생성"""
        try:
            # 지정된 시간 범위의 메트릭 필터링
            current_time = time.time()
            start_time = current_time - (hours * 3600)
            
            relevant_metrics = [
                metric for metric in self.metrics_history
                if metric.timestamp >= start_time
            ]
            
            if not relevant_metrics:
                return {'error': '데이터가 없습니다'}
            
            # 통계 계산
            cpu_usage = [m.cpu_usage for m in relevant_metrics]
            memory_usage = [m.memory_usage for m in relevant_metrics]
            response_times = [m.response_time_avg for m in relevant_metrics]
            
            report = {
                'period_hours': hours,
                'total_samples': len(relevant_metrics),
                'cpu': {
                    'avg': statistics.mean(cpu_usage),
                    'max': max(cpu_usage),
                    'min': min(cpu_usage),
                    'p95': statistics.quantiles(cpu_usage, n=20)[18] if len(cpu_usage) > 1 else 0
                },
                'memory': {
                    'avg': statistics.mean(memory_usage),
                    'max': max(memory_usage),
                    'min': min(memory_usage),
                    'p95': statistics.quantiles(memory_usage, n=20)[18] if len(memory_usage) > 1 else 0
                },
                'response_time': {
                    'avg': statistics.mean(response_times),
                    'max': max(response_times),
                    'min': min(response_times),
                    'p95': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0
                },
                'alerts': self._get_recent_alerts(hours)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"성능 리포트 생성 실패: {e}")
            return {'error': str(e)}
    
    def _get_recent_alerts(self, hours: int) -> List[Dict]:
        """최근 알림 조회"""
        try:
            alerts = []
            alert_data = self.redis_client.lrange('performance_alerts', 0, -1)
            
            current_time = time.time()
            start_time = current_time - (hours * 3600)
            
            for alert_json in alert_data:
                try:
                    alert = json.loads(alert_json)
                    alert_timestamp = datetime.fromisoformat(alert['timestamp']).timestamp()
                    
                    if alert_timestamp >= start_time:
                        alerts.append(alert)
                except:
                    continue
            
            return alerts
            
        except Exception as e:
            logger.error(f"최근 알림 조회 실패: {e}")
            return []

class PerformanceAnalyzer:
    """성능 분석기"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.monitor = performance_monitor
    
    def analyze_bottlenecks(self) -> Dict:
        """병목 지점 분석"""
        try:
            bottlenecks = []
            
            # 최근 메트릭 분석
            recent_metrics = list(self.monitor.metrics_history)[-60:]  # 최근 1시간
            
            if not recent_metrics:
                return {'bottlenecks': []}
            
            # CPU 병목 분석
            cpu_usage = [m.cpu_usage for m in recent_metrics]
            avg_cpu = statistics.mean(cpu_usage)
            if avg_cpu > 70:
                bottlenecks.append({
                    'type': 'cpu',
                    'severity': 'high' if avg_cpu > 85 else 'medium',
                    'description': f'CPU 사용률이 높습니다: {avg_cpu:.1f}%',
                    'recommendation': 'CPU 사용량이 많은 프로세스를 확인하거나 서버를 스케일 업하세요'
                })
            
            # 메모리 병목 분석
            memory_usage = [m.memory_usage for m in recent_metrics]
            avg_memory = statistics.mean(memory_usage)
            if avg_memory > 80:
                bottlenecks.append({
                    'type': 'memory',
                    'severity': 'high' if avg_memory > 90 else 'medium',
                    'description': f'메모리 사용률이 높습니다: {avg_memory:.1f}%',
                    'recommendation': '메모리 누수를 확인하거나 메모리를 증가시키세요'
                })
            
            # 응답 시간 병목 분석
            response_times = [m.response_time_avg for m in recent_metrics if m.response_time_avg > 0]
            if response_times:
                avg_response_time = statistics.mean(response_times)
                if avg_response_time > 1.5:
                    bottlenecks.append({
                        'type': 'response_time',
                        'severity': 'high' if avg_response_time > 3 else 'medium',
                        'description': f'응답 시간이 느립니다: {avg_response_time:.2f}s',
                        'recommendation': '데이터베이스 쿼리나 캐시를 최적화하세요'
                    })
            
            # 에러율 분석
            total_requests = sum(m.request_count for m in recent_metrics)
            total_errors = sum(m.error_count for m in recent_metrics)
            
            if total_requests > 0:
                error_rate = (total_errors / total_requests) * 100
                if error_rate > 3:
                    bottlenecks.append({
                        'type': 'error_rate',
                        'severity': 'high' if error_rate > 10 else 'medium',
                        'description': f'에러율이 높습니다: {error_rate:.1f}%',
                        'recommendation': '에러 로그를 확인하고 문제를 해결하세요'
                    })
            
            return {'bottlenecks': bottlenecks}
            
        except Exception as e:
            logger.error(f"병목 지점 분석 실패: {e}")
            return {'bottlenecks': []}
    
    def analyze_trends(self, hours: int = 24) -> Dict:
        """성능 트렌드 분석"""
        try:
            # 지정된 시간 범위의 메트릭 분석
            current_time = time.time()
            start_time = current_time - (hours * 3600)
            
            relevant_metrics = [
                metric for metric in self.monitor.metrics_history
                if metric.timestamp >= start_time
            ]
            
            if len(relevant_metrics) < 2:
                return {'trends': []}
            
            trends = []
            
            # 시간대별 분석 (1시간 단위)
            hourly_data = defaultdict(list)
            for metric in relevant_metrics:
                hour = datetime.fromtimestamp(metric.timestamp).hour
                hourly_data[hour].append(metric)
            
            # 피크 시간대 분석
            peak_hours = []
            for hour, metrics in hourly_data.items():
                avg_cpu = statistics.mean([m.cpu_usage for m in metrics])
                if avg_cpu > 70:
                    peak_hours.append({
                        'hour': hour,
                        'avg_cpu': avg_cpu,
                        'request_count': sum(m.request_count for m in metrics)
                    })
            
            if peak_hours:
                trends.append({
                    'type': 'peak_hours',
                    'description': f'피크 시간대: {len(peak_hours)}개 시간대',
                    'data': peak_hours
                })
            
            # 성능 저하 패턴 분석
            performance_degradation = []
            for i in range(1, len(relevant_metrics)):
                prev = relevant_metrics[i-1]
                curr = relevant_metrics[i]
                
                if (curr.cpu_usage > prev.cpu_usage * 1.5 or
                    curr.response_time_avg > prev.response_time_avg * 2):
                    
                    performance_degradation.append({
                        'timestamp': datetime.fromtimestamp(curr.timestamp).isoformat(),
                        'cpu_increase': curr.cpu_usage - prev.cpu_usage,
                        'response_time_increase': curr.response_time_avg - prev.response_time_avg
                    })
            
            if performance_degradation:
                trends.append({
                    'type': 'performance_degradation',
                    'description': f'성능 저하 발생: {len(performance_degradation)}회',
                    'data': performance_degradation
                })
            
            return {'trends': trends}
            
        except Exception as e:
            logger.error(f"트렌드 분석 실패: {e}")
            return {'trends': []}
    
    def generate_optimization_recommendations(self) -> List[Dict]:
        """최적화 권장사항 생성"""
        try:
            recommendations = []
            
            # 병목 지점 분석
            bottlenecks = self.analyze_bottlenecks()
            
            for bottleneck in bottlenecks.get('bottlenecks', []):
                recommendations.append({
                    'priority': 'high' if bottleneck['severity'] == 'high' else 'medium',
                    'category': bottleneck['type'],
                    'description': bottleneck['description'],
                    'recommendation': bottleneck['recommendation'],
                    'impact': '높음' if bottleneck['severity'] == 'high' else '중간'
                })
            
            # 일반적인 최적화 권장사항
            general_recommendations = [
                {
                    'priority': 'medium',
                    'category': 'caching',
                    'description': '캐시 사용률이 낮습니다',
                    'recommendation': 'Redis 캐시를 더 적극적으로 활용하세요',
                    'impact': '중간'
                },
                {
                    'priority': 'low',
                    'category': 'monitoring',
                    'description': '상세한 성능 모니터링이 필요합니다',
                    'recommendation': 'APM 도구를 도입하여 더 정확한 성능 분석을 수행하세요',
                    'impact': '낮음'
                }
            ]
            
            recommendations.extend(general_recommendations)
            
            # 우선순위별 정렬
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"최적화 권장사항 생성 실패: {e}")
            return []

# 전역 성능 모니터 인스턴스
performance_monitor = None
performance_analyzer = None

def init_performance_monitor(redis_client: redis.Redis):
    """성능 모니터 초기화"""
    global performance_monitor, performance_analyzer
    performance_monitor = PerformanceMonitor(redis_client)
    performance_analyzer = PerformanceAnalyzer(performance_monitor)
    logger.info("성능 모니터 초기화 완료")

def get_performance_monitor() -> Optional[PerformanceMonitor]:
    """성능 모니터 반환"""
    return performance_monitor

def get_performance_analyzer() -> Optional[PerformanceAnalyzer]:
    """성능 분석기 반환"""
    return performance_analyzer
