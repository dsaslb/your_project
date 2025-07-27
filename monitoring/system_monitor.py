"""
시스템 모니터링 및 성능 추적
CPU, 메모리, 디스크, 네트워크 사용량 모니터링
"""

import time
import psutil
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """시스템 메트릭 데이터 클래스"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used: float
    memory_total: float
    disk_usage_percent: float
    disk_used: float
    disk_total: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    load_average: List[float]

class SystemMonitor:
    """시스템 모니터링 클래스"""
    
    def __init__(self, interval: int = 60):
        self.interval = interval  # 모니터링 간격 (초)
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1440  # 24시간 (1분 간격)
        self.is_monitoring = False
        self.monitor_thread = None
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0
        }
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring:
            logger.warning("모니터링이 이미 실행 중입니다.")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"시스템 모니터링 시작 (간격: {self.interval}초)")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("시스템 모니터링 중지")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # 히스토리 크기 제한
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                # 알림 체크
                self._check_alerts(metrics)
                
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                time.sleep(self.interval)
    
    def _collect_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 정보
        memory = psutil.virtual_memory()
        
        # 디스크 사용률 (루트 파티션)
        disk = psutil.disk_usage('/')
        
        # 네트워크 통계
        network = psutil.net_io_counters()
        
        # 활성 연결 수
        connections = len(psutil.net_connections())
        
        # 로드 평균 (Linux/Mac)
        try:
            load_avg = psutil.getloadavg()
        except:
            load_avg = [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used=memory.used / (1024**3),  # GB
            memory_total=memory.total / (1024**3),  # GB
            disk_usage_percent=disk.percent,
            disk_used=disk.used / (1024**3),  # GB
            disk_total=disk.total / (1024**3),  # GB
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            active_connections=connections,
            load_average=list(load_avg)
        )
    
    def _check_alerts(self, metrics: SystemMetrics):
        """알림 체크"""
        alerts = []
        
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"CPU 사용률 높음: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"메모리 사용률 높음: {metrics.memory_percent:.1f}%")
        
        if metrics.disk_usage_percent > self.alert_thresholds['disk_usage_percent']:
            alerts.append(f"디스크 사용률 높음: {metrics.disk_usage_percent:.1f}%")
        
        if alerts:
            logger.warning(f"시스템 알림: {'; '.join(alerts)}")
            # 여기에 알림 전송 로직 추가 (이메일, Slack 등)
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """현재 메트릭 반환"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """지정된 시간 범위의 메트릭 히스토리 반환"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics_history if m.timestamp > cutoff_time]
    
    def get_average_metrics(self, hours: int = 1) -> Dict[str, float]:
        """평균 메트릭 계산"""
        metrics = self.get_metrics_history(hours)
        if not metrics:
            return {}
        
        return {
            'cpu_percent': sum(m.cpu_percent for m in metrics) / len(metrics),
            'memory_percent': sum(m.memory_percent for m in metrics) / len(metrics),
            'disk_usage_percent': sum(m.disk_usage_percent for m in metrics) / len(metrics),
            'active_connections': sum(m.active_connections for m in metrics) / len(metrics)
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        current = self.get_current_metrics()
        if not current:
            return {}
        
        # 최근 1시간 평균
        avg_1h = self.get_average_metrics(1)
        
        # 최근 24시간 평균
        avg_24h = self.get_average_metrics(24)
        
        return {
            'current': {
                'timestamp': current.timestamp.isoformat(),
                'cpu_percent': current.cpu_percent,
                'memory_percent': current.memory_percent,
                'memory_used_gb': round(current.memory_used, 2),
                'memory_total_gb': round(current.memory_total, 2),
                'disk_usage_percent': current.disk_usage_percent,
                'disk_used_gb': round(current.disk_used, 2),
                'disk_total_gb': round(current.disk_total, 2),
                'active_connections': current.active_connections,
                'load_average': current.load_average
            },
            'average_1h': avg_1h,
            'average_24h': avg_24h,
            'status': self._get_system_status(current)
        }
    
    def _get_system_status(self, metrics: SystemMetrics) -> str:
        """시스템 상태 판단"""
        if (metrics.cpu_percent > 90 or 
            metrics.memory_percent > 95 or 
            metrics.disk_usage_percent > 95):
            return 'critical'
        elif (metrics.cpu_percent > 70 or 
              metrics.memory_percent > 80 or 
              metrics.disk_usage_percent > 85):
            return 'warning'
        else:
            return 'healthy'
    
    def export_metrics(self, filename: str):
        """메트릭을 JSON 파일로 내보내기"""
        try:
            data = {
                'export_time': datetime.now().isoformat(),
                'metrics': [
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'cpu_percent': m.cpu_percent,
                        'memory_percent': m.memory_percent,
                        'memory_used_gb': m.memory_used,
                        'memory_total_gb': m.memory_total,
                        'disk_usage_percent': m.disk_usage_percent,
                        'disk_used_gb': m.disk_used,
                        'disk_total_gb': m.disk_total,
                        'network_bytes_sent': m.network_bytes_sent,
                        'network_bytes_recv': m.network_bytes_recv,
                        'active_connections': m.active_connections,
                        'load_average': m.load_average
                    }
                    for m in self.metrics_history
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"메트릭 내보내기 완료: {filename}")
        except Exception as e:
            logger.error(f"메트릭 내보내기 실패: {e}")

# 전역 시스템 모니터 인스턴스
system_monitor = SystemMonitor() 