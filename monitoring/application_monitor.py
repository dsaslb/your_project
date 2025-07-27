"""
애플리케이션 모니터링 및 성능 추적
요청/응답 시간, 에러율, 처리량 모니터링
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """요청 메트릭 데이터 클래스"""
    timestamp: datetime
    method: str
    path: str
    status_code: int
    response_time: float
    request_size: int = 0
    response_size: int = 0
    user_agent: str = ""
    ip_address: str = ""

@dataclass
class EndpointMetrics:
    """엔드포인트별 메트릭"""
    path: str
    method: str
    total_requests: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    error_count: int = 0
    recent_requests: deque = field(default_factory=lambda: deque(maxlen=100))

class ApplicationMonitor:
    """애플리케이션 모니터링 클래스"""
    
    def __init__(self):
        self.request_history: List[RequestMetrics] = []
        self.endpoint_metrics: Dict[str, EndpointMetrics] = {}
        self.error_log: List[Dict[str, Any]] = []
        self.max_history_size = 10000  # 최대 요청 히스토리 크기
        self.is_monitoring = False
        
        # 실시간 통계
        self.current_minute_requests = 0
        self.current_minute_errors = 0
        self.current_minute_start = datetime.now()
        
        # 알림 설정
        self.alert_thresholds = {
            'error_rate': 0.05,  # 5% 에러율
            'avg_response_time': 2.0,  # 2초 평균 응답시간
            'requests_per_minute': 1000  # 분당 1000 요청
        }
    
    def start_monitoring(self):
        """모니터링 시작"""
        self.is_monitoring = True
        logger.info("애플리케이션 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        logger.info("애플리케이션 모니터링 중지")
    
    def record_request(self, request_metrics: RequestMetrics):
        """요청 기록"""
        if not self.is_monitoring:
            return
        
        # 요청 히스토리에 추가
        self.request_history.append(request_metrics)
        
        # 히스토리 크기 제한
        if len(self.request_history) > self.max_history_size:
            self.request_history.pop(0)
        
        # 엔드포인트별 메트릭 업데이트
        endpoint_key = f"{request_metrics.method}:{request_metrics.path}"
        if endpoint_key not in self.endpoint_metrics:
            self.endpoint_metrics[endpoint_key] = EndpointMetrics(
                path=request_metrics.path,
                method=request_metrics.method
            )
        
        endpoint = self.endpoint_metrics[endpoint_key]
        endpoint.total_requests += 1
        endpoint.total_response_time += request_metrics.response_time
        endpoint.min_response_time = min(endpoint.min_response_time, request_metrics.response_time)
        endpoint.max_response_time = max(endpoint.max_response_time, request_metrics.response_time)
        
        if request_metrics.status_code >= 400:
            endpoint.error_count += 1
        
        endpoint.recent_requests.append(request_metrics)
        
        # 실시간 통계 업데이트
        self._update_realtime_stats(request_metrics)
        
        # 알림 체크
        self._check_alerts(request_metrics)
    
    def record_error(self, error_info: Dict[str, Any]):
        """에러 기록"""
        error_info['timestamp'] = datetime.now().isoformat()
        self.error_log.append(error_info)
        
        # 에러 로그 크기 제한
        if len(self.error_log) > 1000:
            self.error_log.pop(0)
        
        logger.error(f"애플리케이션 에러: {error_info}")
    
    def _update_realtime_stats(self, request_metrics: RequestMetrics):
        """실시간 통계 업데이트"""
        current_time = datetime.now()
        
        # 분 단위 통계 리셋
        if (current_time - self.current_minute_start).seconds >= 60:
            self.current_minute_requests = 0
            self.current_minute_errors = 0
            self.current_minute_start = current_time
        
        self.current_minute_requests += 1
        if request_metrics.status_code >= 400:
            self.current_minute_errors += 1
    
    def _check_alerts(self, request_metrics: RequestMetrics):
        """알림 체크"""
        alerts = []
        
        # 에러율 체크
        if self.current_minute_requests > 0:
            error_rate = self.current_minute_errors / self.current_minute_requests
            if error_rate > self.alert_thresholds['error_rate']:
                alerts.append(f"높은 에러율: {error_rate:.2%}")
        
        # 응답시간 체크
        if request_metrics.response_time > self.alert_thresholds['avg_response_time']:
            alerts.append(f"느린 응답시간: {request_metrics.response_time:.2f}초")
        
        # 요청량 체크
        if self.current_minute_requests > self.alert_thresholds['requests_per_minute']:
            alerts.append(f"높은 요청량: {self.current_minute_requests}/분")
        
        if alerts:
            logger.warning(f"애플리케이션 알림: {'; '.join(alerts)}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """현재 통계 반환"""
        current_time = datetime.now()
        
        # 최근 1분 통계
        recent_requests = [
            r for r in self.request_history 
            if (current_time - r.timestamp).seconds <= 60
        ]
        
        if not recent_requests:
            return {
                'requests_per_minute': 0,
                'error_rate': 0.0,
                'avg_response_time': 0.0,
                'active_endpoints': 0
            }
        
        error_count = len([r for r in recent_requests if r.status_code >= 400])
        avg_response_time = sum(r.response_time for r in recent_requests) / len(recent_requests)
        
        return {
            'requests_per_minute': len(recent_requests),
            'error_rate': error_count / len(recent_requests),
            'avg_response_time': avg_response_time,
            'active_endpoints': len(self.endpoint_metrics)
        }
    
    def get_endpoint_stats(self, hours: int = 1) -> List[Dict[str, Any]]:
        """엔드포인트별 통계"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        stats = []
        for endpoint_key, endpoint in self.endpoint_metrics.items():
            # 지정된 시간 범위의 요청만 필터링
            recent_requests = [
                r for r in endpoint.recent_requests 
                if r.timestamp > cutoff_time
            ]
            
            if not recent_requests:
                continue
            
            avg_response_time = sum(r.response_time for r in recent_requests) / len(recent_requests)
            error_count = len([r for r in recent_requests if r.status_code >= 400])
            
            stats.append({
                'endpoint': endpoint_key,
                'method': endpoint.method,
                'path': endpoint.path,
                'total_requests': len(recent_requests),
                'avg_response_time': avg_response_time,
                'min_response_time': min(r.response_time for r in recent_requests),
                'max_response_time': max(r.response_time for r in recent_requests),
                'error_count': error_count,
                'error_rate': error_count / len(recent_requests) if recent_requests else 0
            })
        
        # 응답시간 기준으로 정렬
        stats.sort(key=lambda x: x['avg_response_time'], reverse=True)
        return stats
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """에러 요약"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 시간 범위 내 에러만 필터링
        recent_errors = [
            error for error in self.error_log
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
        
        if not recent_errors:
            return {
                'total_errors': 0,
                'error_types': {},
                'most_common_errors': []
            }
        
        # 에러 타입별 집계
        error_types = defaultdict(int)
        for error in recent_errors:
            error_type = error.get('type', 'unknown')
            error_types[error_type] += 1
        
        # 가장 빈번한 에러
        most_common_errors = sorted(
            error_types.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            'total_errors': len(recent_errors),
            'error_types': dict(error_types),
            'most_common_errors': most_common_errors
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        current_stats = self.get_current_stats()
        endpoint_stats = self.get_endpoint_stats(1)  # 최근 1시간
        error_summary = self.get_error_summary(24)   # 최근 24시간
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_stats': current_stats,
            'top_slow_endpoints': endpoint_stats[:5],
            'top_error_endpoints': sorted(
                endpoint_stats, 
                key=lambda x: x['error_rate'], 
                reverse=True
            )[:5],
            'error_summary': error_summary,
            'status': self._get_application_status(current_stats)
        }
    
    def _get_application_status(self, stats: Dict[str, Any]) -> str:
        """애플리케이션 상태 판단"""
        if (stats['error_rate'] > 0.1 or  # 10% 이상 에러율
            stats['avg_response_time'] > 5.0):  # 5초 이상 평균 응답시간
            return 'critical'
        elif (stats['error_rate'] > 0.05 or  # 5% 이상 에러율
              stats['avg_response_time'] > 2.0):  # 2초 이상 평균 응답시간
            return 'warning'
        else:
            return 'healthy'
    
    def export_metrics(self, filename: str):
        """메트릭을 JSON 파일로 내보내기"""
        try:
            data = {
                'export_time': datetime.now().isoformat(),
                'request_history': [
                    {
                        'timestamp': r.timestamp.isoformat(),
                        'method': r.method,
                        'path': r.path,
                        'status_code': r.status_code,
                        'response_time': r.response_time,
                        'request_size': r.request_size,
                        'response_size': r.response_size
                    }
                    for r in self.request_history[-1000:]  # 최근 1000개 요청만
                ],
                'endpoint_metrics': {
                    key: {
                        'path': endpoint.path,
                        'method': endpoint.method,
                        'total_requests': endpoint.total_requests,
                        'total_response_time': endpoint.total_response_time,
                        'min_response_time': endpoint.min_response_time,
                        'max_response_time': endpoint.max_response_time,
                        'error_count': endpoint.error_count
                    }
                    for key, endpoint in self.endpoint_metrics.items()
                },
                'error_log': self.error_log[-100:]  # 최근 100개 에러만
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"애플리케이션 메트릭 내보내기 완료: {filename}")
        except Exception as e:
            logger.error(f"애플리케이션 메트릭 내보내기 실패: {e}")

# 전역 애플리케이션 모니터 인스턴스
application_monitor = ApplicationMonitor() 