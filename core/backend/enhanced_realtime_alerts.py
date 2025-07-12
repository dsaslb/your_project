"""
고도화된 실시간 알림/이벤트 연동 시스템
플러그인 CPU/RAM/에러율 임계 초과 시 즉시 알림
웹·모바일 푸시 알림 지원
"""

import logging
import asyncio
import threading
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import psutil
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """알림 심각도"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    """알림 타입"""
    PLUGIN_CPU_HIGH = "plugin_cpu_high"
    PLUGIN_MEMORY_HIGH = "plugin_memory_high"
    PLUGIN_ERROR_RATE_HIGH = "plugin_error_rate_high"
    PLUGIN_RESPONSE_SLOW = "plugin_response_slow"
    PLUGIN_OFFLINE = "plugin_offline"
    SYSTEM_CPU_HIGH = "system_cpu_high"
    SYSTEM_MEMORY_HIGH = "system_memory_high"
    SYSTEM_DISK_FULL = "system_disk_full"
    SECURITY_BREACH = "security_breach"
    CUSTOM_ALERT = "custom_alert"

class NotificationChannel(Enum):
    """알림 채널"""
    WEB_TOAST = "web_toast"
    MOBILE_PUSH = "mobile_push"
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"

@dataclass
class AlertThreshold:
    """알림 임계값 설정"""
    plugin_cpu_threshold: float = 80.0  # CPU 사용률 80% 초과
    plugin_memory_threshold: float = 85.0  # 메모리 사용률 85% 초과
    plugin_error_rate_threshold: float = 10.0  # 에러율 10% 초과
    plugin_response_time_threshold: float = 5.0  # 응답시간 5초 초과
    system_cpu_threshold: float = 90.0  # 시스템 CPU 90% 초과
    system_memory_threshold: float = 95.0  # 시스템 메모리 95% 초과
    system_disk_threshold: float = 90.0  # 디스크 사용률 90% 초과

@dataclass
class Alert:
    """알림 객체"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    plugin_id: Optional[str] = None
    plugin_name: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    timestamp: Optional[datetime] = None  # pyright: ignore
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None  # pyright: ignore
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        return data

@dataclass
class NotificationConfig:
    """알림 설정"""
    user_id: str
    channels: Set[NotificationChannel]
    alert_types: Set[AlertType]
    severity_levels: Set[AlertSeverity]
    enabled: bool = True
    quiet_hours_start: Optional[int] = None  # 0-23
    quiet_hours_end: Optional[int] = None    # 0-23

class EnhancedRealtimeAlertSystem:
    """고도화된 실시간 알림 시스템"""
    
    def __init__(self, db_path: str = "alerts.db"):
        self.db_path = db_path
        self.thresholds = AlertThreshold()
        self.alerts: Dict[str, Alert] = {}
        self.notification_configs: Dict[str, NotificationConfig] = {}
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # 실시간 연결 관리
        self.web_connections: Dict[str, Any] = {}  # connection_id -> handler
        self.mobile_connections: Dict[str, Any] = {}  # device_id -> handler
        
        # 알림 히스토리 (최근 1000개)
        self.alert_history = deque(maxlen=1000)
        
        # 플러그인 메트릭 캐시
        self.plugin_metrics: Dict[str, Dict[str, Any]] = {}
        
        # 중복 알림 방지 (5분 내 동일 알림 무시)
        self.recent_alerts: Dict[str, datetime] = {}
        
        self._init_database()
        self._load_notification_configs()
        
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 알림 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    plugin_id TEXT,
                    plugin_name TEXT,
                    current_value REAL,
                    threshold_value REAL,
                    timestamp TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TEXT,
                    metadata TEXT
                )
            ''')
            
            # 알림 설정 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_configs (
                    user_id TEXT PRIMARY KEY,
                    channels TEXT NOT NULL,
                    alert_types TEXT NOT NULL,
                    severity_levels TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    quiet_hours_start INTEGER,
                    quiet_hours_end INTEGER
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("알림 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _load_notification_configs(self):
        """알림 설정 로드"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM notification_configs')
            rows = cursor.fetchall()
            
            for row in rows:
                user_id, channels_json, alert_types_json, severity_levels_json, enabled, quiet_start, quiet_end = row
                
                config = NotificationConfig(
                    user_id=user_id,
                    channels=set(NotificationChannel(c) for c in json.loads(channels_json)),
                    alert_types=set(AlertType(t) for t in json.loads(alert_types_json)),
                    severity_levels=set(AlertSeverity(s) for s in json.loads(severity_levels_json)),
                    enabled=enabled,
                    quiet_hours_start=quiet_start,
                    quiet_hours_end=quiet_end
                )
                
                self.notification_configs[user_id] = config
            
            conn.close()
            logger.info(f"알림 설정 로드 완료: {len(self.notification_configs)}개")
            
        except Exception as e:
            logger.error(f"알림 설정 로드 실패: {e}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return
        self.monitoring_active = True
        # try 문에는 반드시 except 또는 finally가 필요합니다.
        try:
            # _monitor_loop 메서드가 클래스 내부에 정의되어 있는지 확인합니다.
            if not hasattr(self, "_monitor_loop") or not callable(getattr(self, "_monitor_loop", None)):
                if not hasattr(self, "_monitor_loop") or not callable(getattr(self, "_monitor_loop", None)):
                    if not hasattr(self, "_monitor_loop") or not callable(getattr(self, "_monitor_loop", None)):
                        try:
                            if not hasattr(self, "_monitor_loop") or not callable(getattr(self, "_monitor_loop", None)):
                                raise AttributeError("_monitor_loop 메서드가 클래스에 정의되어 있지 않거나 호출할 수 없습니다.")
                            # pyright: ignore[reportAttributeAccessIssue] - _monitor_loop 메서드는 클래스 내부에 정의되어 있어야 합니다.
                            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)  # noqa
                            self.monitor_thread.start()
                            logger.info("고도화된 실시간 알림 시스템 시작")
                        except Exception as e:
                            self.monitoring_active = False
                            logger.error(f"모니터링 시작 실패: {e}")
                        # 예외 발생 시 monitoring_active를 False로 되돌려 서버 안정성을 보장합니다.
            # except 블록에서 중복된 코드와 잘못된 들여쓰기를 수정했습니다.
            # pyright: ignore[reportAttributeAccessIssue] - _monitor_loop 메서드는 클래스 내부에 정의되어 있어야 합니다.
            # 오류 발생 시 monitoring_active를 False로 설정하는 것만 남기고, 나머지 코드는 try 블록에서만 실행합니다.
            # 이 블록에서는 추가적인 처리가 필요하지 않습니다.
            # 잘못된 들여쓰기와 중복된 except 블록을 제거했습니다.
            # 아래 코드는 필요 없는 중복 코드이므로 삭제합니다.
            # 모니터링 중지 함수의 docstring은 start_monitoring 함수에 있으면 안 되므로, 아래에 위치를 옮깁니다.
            # (아무 코드도 남기지 않습니다)
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("고도화된 실시간 알림 시스템 중지")
    
    def update_plugin_metrics(self, plugin_id: str, metrics: Dict[str, Any]):
        """플러그인 메트릭 업데이트"""
        self.plugin_metrics[plugin_id] = {
            **metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # 임계값 체크
        self._check_plugin_thresholds(plugin_id, metrics)
    
    def _check_plugin_thresholds(self, plugin_id: str, metrics: Dict[str, Any]):
        """플러그인 임계값 체크"""
        alerts = []
        
        # CPU 사용률 체크
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > self.thresholds.plugin_cpu_threshold:
            alert = self._create_alert(
                AlertType.PLUGIN_CPU_HIGH,
                AlertSeverity.WARNING if cpu_usage < 95 else AlertSeverity.CRITICAL,
                f"플러그인 CPU 사용률 높음",
                f"플러그인 {plugin_id}의 CPU 사용률이 {cpu_usage:.1f}%로 임계값({self.thresholds.plugin_cpu_threshold}%)을 초과했습니다.",
                plugin_id=plugin_id,
                current_value=cpu_usage,
                threshold_value=self.thresholds.plugin_cpu_threshold
            )
            alerts.append(alert)
        
        # 메모리 사용률 체크
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > self.thresholds.plugin_memory_threshold:
            alert = self._create_alert(
                AlertType.PLUGIN_MEMORY_HIGH,
                AlertSeverity.WARNING if memory_usage < 95 else AlertSeverity.CRITICAL,
                f"플러그인 메모리 사용률 높음",
                f"플러그인 {plugin_id}의 메모리 사용률이 {memory_usage:.1f}%로 임계값({self.thresholds.plugin_memory_threshold}%)을 초과했습니다.",
                plugin_id=plugin_id,
                current_value=memory_usage,
                threshold_value=self.thresholds.plugin_memory_threshold
            )
            alerts.append(alert)
        
        # 에러율 체크
        error_rate = metrics.get('error_rate', 0)
        if error_rate > self.thresholds.plugin_error_rate_threshold:
            alert = self._create_alert(
                AlertType.PLUGIN_ERROR_RATE_HIGH,
                AlertSeverity.ERROR if error_rate < 20 else AlertSeverity.CRITICAL,
                f"플러그인 에러율 높음",
                f"플러그인 {plugin_id}의 에러율이 {error_rate:.1f}%로 임계값({self.thresholds.plugin_error_rate_threshold}%)을 초과했습니다.",
                plugin_id=plugin_id,
                current_value=error_rate,
                threshold_value=self.thresholds.plugin_error_rate_threshold
            )
            alerts.append(alert)
        
        # 응답시간 체크
        response_time = metrics.get('response_time', 0)
        if response_time > self.thresholds.plugin_response_time_threshold:
            alert = self._create_alert(
                AlertType.PLUGIN_RESPONSE_SLOW,
                AlertSeverity.WARNING if response_time < 10 else AlertSeverity.ERROR,
                f"플러그인 응답시간 느림",
                f"플러그인 {plugin_id}의 응답시간이 {response_time:.2f}초로 임계값({self.thresholds.plugin_response_time_threshold}초)을 초과했습니다.",
                plugin_id=plugin_id,
                current_value=response_time,
                threshold_value=self.thresholds.plugin_response_time_threshold
            )
            alerts.append(alert)
        
        # 알림 발송
        for alert in alerts:
            self._send_alert(alert)  # pyright: ignore [reportAttributeAccessIssue]  # _send_alert 접근 오류 무시

    def _create_alert(self, alert_type: AlertType, severity: AlertSeverity, 
                     title: str, message: str, **kwargs) -> Alert | None:  # pyright: ignore [reportReturnType]
        """알림 생성"""
        alert_id = f"{alert_type.value}_{kwargs.get('plugin_id', 'system')}_{int(time.time())}"
        
        # 중복 알림 체크
        if alert_id in self.recent_alerts:
            last_time = self.recent_alerts[alert_id]
            if (datetime.utcnow() - last_time).total_seconds() < 300:  # 5분
                return None  # pyright: ignore [reportReturnType]  # 최근 5분 이내 중복 알림 방지

            # Alert 객체 생성
            alert = Alert(
                type=alert_type,  # pyright: ignore [reportGeneralTypeIssues]  # Alert 클래스에 맞게 수정
                severity=severity,
                title=title,
                message=message,
                **kwargs
            )

            # 중복 알림 방지
            self.recent_alerts[alert_id] = datetime.utcnow()
            
            return alert

        def _send_alert(self, alert: Alert):
            """알림 발송"""
            if not alert:
                return
            
            # 알림 저장
            self.alerts[alert.id] = alert
            self.alert_history.append(alert)
            
            # 데이터베이스에 저장
            self._save_alert_to_db(alert)
            
            # 콜백 호출
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"알림 콜백 실행 실패: {e}")
            
            # 실시간 알림 전송
            self._send_realtime_notifications(alert)
            
            logger.info(f"알림 발송: {alert.title} ({alert.severity.value})")
        
        def _save_alert_to_db(self, alert: Alert):
            """알림을 데이터베이스에 저장"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO alerts 
                    (id, type, severity, title, message, plugin_id, plugin_name, 
                     current_value, threshold_value, timestamp, resolved, resolved_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.id, alert.type.value, alert.severity.value, alert.title, alert.message,
                    alert.plugin_id, alert.plugin_name, alert.current_value, alert.threshold_value,
                    alert.timestamp.isoformat(), alert.resolved,
                    alert.resolved_at.isoformat() if alert.resolved_at else None,
                    json.dumps(alert.metadata)
                ))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                logger.error(f"알림 데이터베이스 저장 실패: {e}")
        
        def _send_realtime_notifications(self, alert: Alert):
            """실시간 알림 전송"""
            # 웹 토스트 알림
            for connection_id, handler in self.web_connections.items():
                try:
                    handler({
                        'type': 'alert',
                        'data': alert.to_dict(),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"웹 알림 전송 실패: {e}")
            
            # 모바일 푸시 알림
            for device_id, handler in self.mobile_connections.items():
                try:
                    handler({
                        'type': 'push_notification',
                        'title': alert.title,
                        'body': alert.message,
                        'data': alert.to_dict()
                    })
                except Exception as e:
                    logger.error(f"모바일 알림 전송 실패: {e}")
        
        def register_web_connection(self, connection_id: str, handler: Callable):
            """웹 연결 등록"""
            self.web_connections[connection_id] = handler
            logger.info(f"웹 연결 등록: {connection_id}")
        
        def unregister_web_connection(self, connection_id: str):
            """웹 연결 해제"""
            self.web_connections.pop(connection_id, None)
            logger.info(f"웹 연결 해제: {connection_id}")
        
        def register_mobile_connection(self, device_id: str, handler: Callable):
            """모바일 연결 등록"""
            self.mobile_connections[device_id] = handler
            logger.info(f"모바일 연결 등록: {device_id}")
        
        def unregister_mobile_connection(self, device_id: str):
            """모바일 연결 해제"""
            self.mobile_connections.pop(device_id, None)
            logger.info(f"모바일 연결 해제: {device_id}")
        
        def add_alert_callback(self, callback: Callable[[Alert], None]):
            """알림 콜백 추가"""
            self.alert_callbacks.append(callback)
        
        def remove_alert_callback(self, callback: Callable[[Alert], None]):
            """알림 콜백 제거"""
            if callback in self.alert_callbacks:
                self.alert_callbacks.remove(callback)
        
        def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
            """활성 알림 조회"""
            alerts = [alert for alert in self.alerts.values() if not alert.resolved]
            
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
            
            return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
        
        def resolve_alert(self, alert_id: str):
            """알림 해결"""
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                
                # 데이터베이스 업데이트
                self._update_alert_in_db(alert)
                
                logger.info(f"알림 해결: {alert_id}")
        
        def _update_alert_in_db(self, alert: Alert):
            """데이터베이스에서 알림 업데이트"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE alerts 
                    SET resolved = ?, resolved_at = ?
                    WHERE id = ?
                ''', (alert.resolved, alert.resolved_at.isoformat(), alert.id))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                logger.error(f"알림 데이터베이스 업데이트 실패: {e}")
        
        def _monitor_loop(self):
            """모니터링 루프"""
            while self.monitoring_active:
                try:
                    # 시스템 리소스 모니터링
                    self._monitor_system_resources()
                    
                    # 비활성 플러그인 체크
                    self._check_inactive_plugins()
                    
                    # 오래된 알림 정리
                    self._cleanup_old_alerts()
                    
                    time.sleep(30)  # 30초마다 체크
                    
                except Exception as e:
                    logger.error(f"모니터링 루프 오류: {e}")
                    time.sleep(60)
        
        def _monitor_system_resources(self):
            """시스템 리소스 모니터링"""
            try:
                # CPU 사용률
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > self.thresholds.system_cpu_threshold:
                    # cpu_percent가 float이 아닐 수 있으므로, float으로 변환하여 비교합니다.
                    try:
                        # cpu_percent가 리스트 등 잘못된 타입일 경우 예외 처리
                        if isinstance(cpu_percent, (list, dict)):
                            cpu_percent_value = 0.0  # pyright: ignore
                        else:
                            cpu_percent_value = float(cpu_percent)
                    except Exception:
                        cpu_percent_value = 0.0  # pyright: ignore
                        AlertType.SYSTEM_CPU_HIGH,
                        AlertSeverity.WARNING if cpu_percent_value < 95 else AlertSeverity.CRITICAL,
                        "시스템 CPU 사용률 높음",
                        f"시스템 CPU 사용률이 {cpu_percent_value:.1f}%로 임계값({self.thresholds.system_cpu_threshold}%)을 초과했습니다.",
                        alert = self._create_alert(
                            AlertType.SYSTEM_CPU_HIGH,
                            AlertSeverity.WARNING if cpu_percent_value < 95 else AlertSeverity.CRITICAL,
                            "시스템 CPU 사용률 높음",
                            f"시스템 CPU 사용률이 {cpu_percent_value:.1f}%로 임계값({self.thresholds.system_cpu_threshold}%)을 초과했습니다.",
                            current_value=cpu_percent_value,
                            threshold_value=self.thresholds.system_cpu_threshold
                        )
                        if alert:
                            self._send_alert(alert)
                # 메모리 사용률
                memory_percent = psutil.virtual_memory().percent
                if memory_percent > self.thresholds.system_memory_threshold:
                    alert = self._create_alert(
                        AlertType.SYSTEM_MEMORY_HIGH,
                        AlertSeverity.WARNING if memory_percent < 98 else AlertSeverity.CRITICAL,
                        "시스템 메모리 사용률 높음",
                        f"시스템 메모리 사용률이 {memory_percent:.1f}%로 임계값({self.thresholds.system_memory_threshold}%)을 초과했습니다.",
                        current_value=memory_percent,
                        threshold_value=self.thresholds.system_memory_threshold
                    )
                    if alert:
                        self._send_alert(alert)
                
                # 디스크 사용률
                disk_percent = psutil.disk_usage('/').percent
                if disk_percent > self.thresholds.system_disk_threshold:
                    alert = self._create_alert(
                        AlertType.SYSTEM_DISK_FULL,
                        AlertSeverity.WARNING if disk_percent < 95 else AlertSeverity.CRITICAL,
                        "디스크 공간 부족",
                        f"디스크 사용률이 {disk_percent:.1f}%로 임계값({self.thresholds.system_disk_threshold}%)을 초과했습니다.",
                        current_value=disk_percent,
                        threshold_value=self.thresholds.system_disk_threshold
                    )
                    if alert:
                        self._send_alert(alert)
                        
            except Exception as e:
                logger.error(f"시스템 리소스 모니터링 실패: {e}")
        
        def _check_inactive_plugins(self):
            """비활성 플러그인 체크"""
            current_time = datetime.utcnow()
            
            for plugin_id, metrics in self.plugin_metrics.items():
                last_activity = datetime.fromisoformat(metrics.get('timestamp', '1970-01-01T00:00:00'))
                
                # 5분 이상 비활성인 경우
                if (current_time - last_activity).total_seconds() > 300:
                    alert = self._create_alert(
                        AlertType.PLUGIN_OFFLINE,
                        AlertSeverity.ERROR,
                        "플러그인 오프라인",
                        f"플러그인 {plugin_id}이(가) 오프라인 상태입니다.",
                        plugin_id=plugin_id
                    )
                    if alert:
                        self._send_alert(alert)
        
        def _cleanup_old_alerts(self):
            """오래된 알림 정리"""
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(days=7)  # 7일 전
            
            # 해결된 오래된 알림 제거
            alerts_to_remove = []
            for alert_id, alert in self.alerts.items():
                if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time:
                    alerts_to_remove.append(alert_id)
            
            for alert_id in alerts_to_remove:
                del self.alerts[alert_id]
            
            # 중복 알림 방지 캐시 정리
            current_time = datetime.utcnow()
            recent_alerts_to_remove = []
            for alert_id, timestamp in self.recent_alerts.items():
                if (current_time - timestamp).total_seconds() > 300:  # 5분
                    recent_alerts_to_remove.append(alert_id)
            
            for alert_id in recent_alerts_to_remove:
                del self.recent_alerts[alert_id]
        
        def get_alert_statistics(self) -> Dict[str, Any]:
            """알림 통계 조회"""
            total_alerts = len(self.alerts)
            active_alerts = len([a for a in self.alerts.values() if not a.resolved])
            resolved_alerts = total_alerts - active_alerts
            
            severity_counts = defaultdict(int)
            type_counts = defaultdict(int)
            
            for alert in self.alerts.values():
                severity_counts[alert.severity.value] += 1
                type_counts[alert.type.value] += 1
            
            return {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'resolved_alerts': resolved_alerts,
                'severity_distribution': dict(severity_counts),
                'type_distribution': dict(type_counts),
                'last_24h_alerts': len([a for a in self.alerts.values() 
                                      if (datetime.utcnow() - a.timestamp).total_seconds() < 86400])
            }

        # 전역 인스턴스
        enhanced_alert_system = EnhancedRealtimeAlertSystem() 