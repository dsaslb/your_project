"""
플러그인 성능 모니터링 및 실시간 알림 시스템
"""

import logging
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """알림 레벨"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PluginMetrics:
    """플러그인 메트릭"""
    plugin_id: str
    plugin_name: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_count: int
    request_count: int
    last_activity: datetime
    status: str
    uptime: float

@dataclass
class AlertThreshold:
    """알림 임계값"""
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    response_time_threshold: float = 5.0
    error_rate_threshold: float = 10.0
    consecutive_errors_threshold: int = 5

@dataclass
class Alert:
    """알림 정보"""
    id: str
    plugin_id: str
    plugin_name: str
    level: AlertLevel
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class PluginMonitor:
    """플러그인 모니터링 클래스"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginMetrics] = {}
        self.alerts: List[Alert] = []
        self.thresholds = AlertThreshold()
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.alert_callbacks: List[Callable] = []
        self.metrics_history: Dict[str, List[PluginMetrics]] = {}
        
    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("플러그인 모니터링 시작")
        
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("플러그인 모니터링 중지")
        
    def register_plugin(self, plugin_id: str, plugin_name: str):
        """플러그인 등록"""
        self.plugins[plugin_id] = PluginMetrics(
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            cpu_usage=0.0,
            memory_usage=0.0,
            response_time=0.0,
            error_count=0,
            request_count=0,
            last_activity=datetime.utcnow(),
            status="active",
            uptime=0.0
        )
        self.metrics_history[plugin_id] = []
        logger.info(f"플러그인 등록: {plugin_name} ({plugin_id})")
        
    def update_metrics(self, plugin_id: str, metrics: Dict[str, Any]):
        """플러그인 메트릭 업데이트"""
        if plugin_id not in self.plugins:
            return
            
        plugin = self.plugins[plugin_id]
        
        # 메트릭 업데이트
        plugin.cpu_usage = metrics.get('cpu_usage', plugin.cpu_usage)
        plugin.memory_usage = metrics.get('memory_usage', plugin.memory_usage)
        plugin.response_time = metrics.get('response_time', plugin.response_time)
        plugin.error_count = metrics.get('error_count', plugin.error_count)
        plugin.request_count = metrics.get('request_count', plugin.request_count)
        plugin.last_activity = datetime.utcnow()
        plugin.uptime = metrics.get('uptime', plugin.uptime)
        
        # 메트릭 히스토리 저장 (최근 100개)
        plugin_copy = PluginMetrics(
            plugin_id=plugin.plugin_id,
            plugin_name=plugin.plugin_name,
            cpu_usage=plugin.cpu_usage,
            memory_usage=plugin.memory_usage,
            response_time=plugin.response_time,
            error_count=plugin.error_count,
            request_count=plugin.request_count,
            last_activity=plugin.last_activity,
            status=plugin.status,
            uptime=plugin.uptime
        )
        self.metrics_history[plugin_id].append(plugin_copy)
        if len(self.metrics_history[plugin_id]) > 100:
            self.metrics_history[plugin_id].pop(0)
            
        # 임계값 체크 및 알림 생성
        self._check_thresholds(plugin_id)
        
    def _check_thresholds(self, plugin_id: str):
        """임계값 체크 및 알림 생성"""
        plugin = self.plugins[plugin_id]
        alerts_created = []
        
        # CPU 사용률 체크
        if plugin.cpu_usage > self.thresholds.cpu_threshold:
            alert = Alert(
                id=f"cpu_{plugin_id}_{int(time.time())}",
                plugin_id=plugin_id,
                plugin_name=plugin.plugin_name,
                level=AlertLevel.WARNING if plugin.cpu_usage < 95 else AlertLevel.CRITICAL,
                message=f"CPU 사용률이 임계값을 초과했습니다: {plugin.cpu_usage:.1f}%",
                details={
                    "metric": "cpu_usage",
                    "value": plugin.cpu_usage,
                    "threshold": self.thresholds.cpu_threshold
                },
                timestamp=datetime.utcnow()
            )
            alerts_created.append(alert)
            
        # 메모리 사용률 체크
        if plugin.memory_usage > self.thresholds.memory_threshold:
            alert = Alert(
                id=f"memory_{plugin_id}_{int(time.time())}",
                plugin_id=plugin_id,
                plugin_name=plugin.plugin_name,
                level=AlertLevel.WARNING if plugin.memory_usage < 95 else AlertLevel.CRITICAL,
                message=f"메모리 사용률이 임계값을 초과했습니다: {plugin.memory_usage:.1f}%",
                details={
                    "metric": "memory_usage",
                    "value": plugin.memory_usage,
                    "threshold": self.thresholds.memory_threshold
                },
                timestamp=datetime.utcnow()
            )
            alerts_created.append(alert)
            
        # 응답 시간 체크
        if plugin.response_time > self.thresholds.response_time_threshold:
            alert = Alert(
                id=f"response_{plugin_id}_{int(time.time())}",
                plugin_id=plugin_id,
                plugin_name=plugin.plugin_name,
                level=AlertLevel.WARNING,
                message=f"응답 시간이 임계값을 초과했습니다: {plugin.response_time:.2f}초",
                details={
                    "metric": "response_time",
                    "value": plugin.response_time,
                    "threshold": self.thresholds.response_time_threshold
                },
                timestamp=datetime.utcnow()
            )
            alerts_created.append(alert)
            
        # 에러율 체크
        if plugin.request_count > 0:
            error_rate = (plugin.error_count / plugin.request_count) * 100
            if error_rate > self.thresholds.error_rate_threshold:
                alert = Alert(
                    id=f"error_rate_{plugin_id}_{int(time.time())}",
                    plugin_id=plugin_id,
                    plugin_name=plugin.plugin_name,
                    level=AlertLevel.ERROR,
                    message=f"에러율이 임계값을 초과했습니다: {error_rate:.1f}%",
                    details={
                        "metric": "error_rate",
                        "value": error_rate,
                        "threshold": self.thresholds.error_rate_threshold,
                        "error_count": plugin.error_count,
                        "request_count": plugin.request_count
                    },
                    timestamp=datetime.utcnow()
                )
                alerts_created.append(alert)
                
        # 연속 에러 체크
        if plugin.error_count >= self.thresholds.consecutive_errors_threshold:
            alert = Alert(
                id=f"consecutive_errors_{plugin_id}_{int(time.time())}",
                plugin_id=plugin_id,
                plugin_name=plugin.plugin_name,
                level=AlertLevel.CRITICAL,
                message=f"연속 에러가 발생했습니다: {plugin.error_count}회",
                details={
                    "metric": "consecutive_errors",
                    "value": plugin.error_count,
                    "threshold": self.thresholds.consecutive_errors_threshold
                },
                timestamp=datetime.utcnow()
            )
            alerts_created.append(alert)
            
        # 알림 생성 및 콜백 호출
        for alert in alerts_created:
            self.alerts.append(alert)
            self._trigger_alert_callbacks(alert)
            logger.warning(f"플러그인 알림 생성: {alert.message}")
            
    def _trigger_alert_callbacks(self, alert: Alert):
        """알림 콜백 함수들 호출"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"알림 콜백 실행 오류: {e}")
                
    def add_alert_callback(self, callback: Callable):
        """알림 콜백 함수 등록"""
        self.alert_callbacks.append(callback)
        
    def get_plugin_metrics(self, plugin_id: str) -> Optional[PluginMetrics]:
        """플러그인 메트릭 조회"""
        return self.plugins.get(plugin_id)
        
    def get_all_metrics(self) -> Dict[str, PluginMetrics]:
        """모든 플러그인 메트릭 조회"""
        return self.plugins.copy()
        
    def get_active_alerts(self) -> List[Alert]:
        """활성 알림 조회"""
        return [alert for alert in self.alerts if not alert.resolved]
        
    def resolve_alert(self, alert_id: str):
        """알림 해결 처리"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                break
                
    def get_metrics_history(self, plugin_id: str, hours: int = 24) -> List[PluginMetrics]:
        """플러그인 메트릭 히스토리 조회"""
        if plugin_id not in self.metrics_history:
            return []
            
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        filtered_metrics = []
        for metrics in self.metrics_history[plugin_id]:
            if metrics.last_activity >= cutoff_time:
                filtered_metrics.append(metrics)
        return filtered_metrics
        
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 시스템 리소스 모니터링
                self._monitor_system_resources()
                
                # 비활성 플러그인 체크
                self._check_inactive_plugins()
                
                # 30초 대기
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
                
    def _monitor_system_resources(self):
        """시스템 리소스 모니터링"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # 전체 시스템 리소스가 임계값을 초과하면 알림
            if isinstance(cpu_percent, (int, float)) and cpu_percent > 90:
                alert = Alert(
                    id=f"system_cpu_{int(time.time())}",
                    plugin_id="system",
                    plugin_name="시스템",
                    level=AlertLevel.CRITICAL,
                    message=f"시스템 CPU 사용률이 높습니다: {cpu_percent:.1f}%",
                    details={"metric": "system_cpu", "value": cpu_percent},
                    timestamp=datetime.utcnow()
                )
                self.alerts.append(alert)
                self._trigger_alert_callbacks(alert)
                
            if memory.percent > 90:
                alert = Alert(
                    id=f"system_memory_{int(time.time())}",
                    plugin_id="system",
                    plugin_name="시스템",
                    level=AlertLevel.CRITICAL,
                    message=f"시스템 메모리 사용률이 높습니다: {memory.percent:.1f}%",
                    details={"metric": "system_memory", "value": memory.percent},
                    timestamp=datetime.utcnow()
                )
                self.alerts.append(alert)
                self._trigger_alert_callbacks(alert)
                
        except Exception as e:
            logger.error(f"시스템 리소스 모니터링 오류: {e}")
            
    def _check_inactive_plugins(self):
        """비활성 플러그인 체크"""
        current_time = datetime.utcnow()
        for plugin_id, plugin in self.plugins.items():
            # 5분 이상 비활성인 플러그인 체크
            if (current_time - plugin.last_activity).total_seconds() > 300:
                if plugin.status != "inactive":
                    plugin.status = "inactive"
                    alert = Alert(
                        id=f"inactive_{plugin_id}_{int(time.time())}",
                        plugin_id=plugin_id,
                        plugin_name=plugin.plugin_name,
                        level=AlertLevel.WARNING,
                        message=f"플러그인이 비활성 상태입니다: {plugin.plugin_name}",
                        details={"metric": "status", "value": "inactive"},
                        timestamp=current_time
                    )
                    self.alerts.append(alert)
                    self._trigger_alert_callbacks(alert)

# 전역 플러그인 모니터 인스턴스
plugin_monitor = PluginMonitor() 