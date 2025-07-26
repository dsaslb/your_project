import logging
import psutil
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(filename="system_monitor.log", level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemMonitor:
    def __init__(self):
        self.error_history = []
        self.event_history = []
        self.performance_metrics = {}
        self.websocket_stats = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """시스템 모니터링 시작"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("시스템 모니터링이 시작되었습니다.")
    
    def stop_monitoring(self):
        """시스템 모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("시스템 모니터링이 중지되었습니다.")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                self._check_system_health()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(120)  # 오류 시 2분 대기
    
    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # CPU 사용량
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용량
            memory = psutil.virtual_memory()
            
            # 디스크 사용량
            disk = psutil.disk_usage('/')
            
            # 네트워크 통계
            network = psutil.net_io_counters()
            
            self.performance_metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv
            }
            
            # 임계값 체크
            if cpu_percent > 80:
                self.log_error(f"CPU 사용량이 높습니다: {cpu_percent}%")
            
            if memory.percent > 85:
                self.log_error(f"메모리 사용량이 높습니다: {memory.percent}%")
                
            if disk.percent > 90:
                self.log_error(f"디스크 사용량이 높습니다: {disk.percent}%")
                
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 오류: {e}")
    
    def _check_system_health(self):
        """시스템 상태 체크"""
        try:
            # 프로세스 상태 체크
            current_process = psutil.Process()
            
            # 메모리 누수 체크 (1시간 이상 실행 시)
            if hasattr(self, '_last_memory_check'):
                time_diff = datetime.now() - self._last_memory_check
                if time_diff.total_seconds() > 3600:  # 1시간
                    current_memory = current_process.memory_info().rss
                    if hasattr(self, '_baseline_memory'):
                        memory_increase = current_memory - self._baseline_memory
                        if memory_increase > 100 * 1024 * 1024:  # 100MB 이상 증가
                            self.log_error(f"메모리 누수 의심: {memory_increase / (1024*1024):.2f}MB 증가")
                    self._baseline_memory = current_memory
                    self._last_memory_check = datetime.now()
            else:
                self._baseline_memory = current_process.memory_info().rss
                self._last_memory_check = datetime.now()
                
        except Exception as e:
            logger.error(f"시스템 상태 체크 오류: {e}")
    
    def update_websocket_stats(self, stats: Dict[str, Any]):
        """WebSocket 통계 업데이트"""
        self.websocket_stats = {
            **stats,
            'timestamp': datetime.now().isoformat()
        }
        
        # WebSocket 연결 수 체크
        connected_clients = stats.get('connected_clients', 0)
        if connected_clients > 1000:
            self.log_error(f"WebSocket 연결 수가 많습니다: {connected_clients}개")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 반환"""
        return {
            'current_metrics': self.performance_metrics,
            'websocket_stats': self.websocket_stats,
            'error_count': len(self.error_history),
            'event_count': len(self.event_history),
            'monitoring_active': self.monitoring_active
        }
    
    def export_metrics(self, filename: str):
        """메트릭을 파일로 내보내기"""
        try:
            import json
            data = {
                'performance_metrics': self.performance_metrics,
                'websocket_stats': self.websocket_stats,
                'error_history': self.error_history[-100:],  # 최근 100개
                'event_history': self.event_history[-100:],  # 최근 100개
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"메트릭이 {filename}에 내보내졌습니다.")
        except Exception as e:
            logger.error(f"메트릭 내보내기 오류: {e}")

    def log_event(self, event):
        entry = {"type": "event", "event": event, "timestamp": datetime.now()}
        self.event_history.append(entry)
        logging.info(
            f"EVENT: {event} at {entry['timestamp'] if entry is not None else None}"
        )

    def log_error(self, error):
        entry = {"type": "error", "error": error, "timestamp": datetime.now()}
        self.error_history.append(entry)
        logging.error(
            f"ERROR: {error} at {entry['timestamp'] if entry is not None else None}"
        )
        self.send_alert(error)

    def send_alert(self, message):
        # 실제 구현 시 이메일/슬랙 등 알림 연동
        logging.warning(f"ALERT: {message} (관리자에게 알림)")

    def get_error_history(self):
        return self.error_history

    def get_event_history(self):
        return self.event_history


# 전역 시스템 모니터링 인스턴스
system_monitor = SystemMonitor()
