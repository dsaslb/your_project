import os
import psutil
import time
import threading
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """모니터링 설정 클래스"""
    data_dir: str
    collection_interval: int = 60  # 초
    retention_days: int = 30
    alert_enabled: bool = True
    email_enabled: bool = False
    webhook_enabled: bool = False
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    disk_threshold: float = 90.0
    response_time_threshold: float = 5000.0  # ms

@dataclass
class SystemMetrics:
    """시스템 메트릭 정보"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    disk_read: int
    disk_write: int
    load_average: Tuple[float, float, float]
    uptime: float

@dataclass
class ApplicationMetrics:
    """애플리케이션 메트릭 정보"""
    timestamp: datetime
    endpoint: str
    response_time: float
    status_code: int
    request_count: int
    error_count: int
    active_sessions: int
    database_connections: int

@dataclass
class AlertRule:
    """알림 규칙 정보"""
    rule_id: str
    name: str
    metric_type: str  # system, application, custom
    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    threshold: float
    duration: int  # 초
    severity: str  # low, medium, high, critical
    enabled: bool = True
    created_at: datetime = None

@dataclass
class Alert:
    """알림 정보"""
    alert_id: str
    rule_id: str
    metric_type: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str
    message: str
    timestamp: datetime
    status: str = "active"  # active, acknowledged, resolved
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

class MonitoringManager:
    """모니터링 관리자 클래스"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.is_running = False
        self.monitoring_thread = None
        self.system_metrics: List[SystemMetrics] = []
        self.application_metrics: List[ApplicationMetrics] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.metric_history: Dict[str, List[float]] = {}
        
        # 모니터링 디렉토리 생성
        os.makedirs(config.data_dir, exist_ok=True)
        
        # 데이터베이스 초기화
        self.init_database()
        
        # 기본 알림 규칙 생성
        self.create_default_alert_rules()
        
        # 모니터링 시작
        self.start_monitoring()
    
    def init_database(self):
        """모니터링 데이터베이스 초기화"""
        db_path = os.path.join(self.config.data_dir, 'monitoring.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 시스템 메트릭 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL NOT NULL,
                memory_percent REAL NOT NULL,
                disk_percent REAL NOT NULL,
                network_sent INTEGER NOT NULL,
                network_recv INTEGER NOT NULL,
                disk_read INTEGER NOT NULL,
                disk_write INTEGER NOT NULL,
                load_average_1 REAL NOT NULL,
                load_average_5 REAL NOT NULL,
                load_average_15 REAL NOT NULL,
                uptime REAL NOT NULL
            )
        ''')
        
        # 애플리케이션 메트릭 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                response_time REAL NOT NULL,
                status_code INTEGER NOT NULL,
                request_count INTEGER NOT NULL,
                error_count INTEGER NOT NULL,
                active_sessions INTEGER NOT NULL,
                database_connections INTEGER NOT NULL
            )
        ''')
        
        # 알림 규칙 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                operator TEXT NOT NULL,
                threshold REAL NOT NULL,
                duration INTEGER NOT NULL,
                severity TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 알림 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                rule_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                current_value REAL NOT NULL,
                threshold REAL NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                acknowledged_by TEXT,
                resolved_at TEXT,
                FOREIGN KEY (rule_id) REFERENCES alert_rules (rule_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_default_alert_rules(self):
        """기본 알림 규칙 생성"""
        default_rules = [
            {
                'name': 'CPU 사용률 높음',
                'metric_type': 'system',
                'metric_name': 'cpu_percent',
                'operator': '>',
                'threshold': self.config.cpu_threshold,
                'duration': 300,  # 5분
                'severity': 'high'
            },
            {
                'name': '메모리 사용률 높음',
                'metric_type': 'system',
                'metric_name': 'memory_percent',
                'operator': '>',
                'threshold': self.config.memory_threshold,
                'duration': 300,
                'severity': 'high'
            },
            {
                'name': '디스크 사용률 높음',
                'metric_type': 'system',
                'metric_name': 'disk_percent',
                'operator': '>',
                'threshold': self.config.disk_threshold,
                'duration': 300,
                'severity': 'critical'
            },
            {
                'name': 'API 응답 시간 느림',
                'metric_type': 'application',
                'metric_name': 'response_time',
                'operator': '>',
                'threshold': self.config.response_time_threshold,
                'duration': 60,
                'severity': 'medium'
            }
        ]
        
        for rule_data in default_rules:
            self.create_alert_rule(**rule_data)
    
    def create_alert_rule(self, name: str, metric_type: str, metric_name: str,
                         operator: str, threshold: float, duration: int, severity: str) -> str:
        """알림 규칙 생성"""
        rule_id = self._generate_id()
        
        rule = AlertRule(
            rule_id=rule_id,
            name=name,
            metric_type=metric_type,
            metric_name=metric_name,
            operator=operator,
            threshold=threshold,
            duration=duration,
            severity=severity,
            created_at=datetime.utcnow()
        )
        
        self.alert_rules[rule_id] = rule
        self._save_alert_rule(rule)
        
        logger.info(f"알림 규칙 생성: {name} (ID: {rule_id})")
        return rule_id
    
    def _generate_id(self) -> str:
        """고유 ID 생성"""
        import uuid
        return str(uuid.uuid4())
    
    def _save_alert_rule(self, rule: AlertRule):
        """알림 규칙을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'monitoring.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO alert_rules 
            (rule_id, name, metric_type, metric_name, operator, threshold, duration, severity, enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.rule_id,
            rule.name,
            rule.metric_type,
            rule.metric_name,
            rule.operator,
            rule.threshold,
            rule.duration,
            rule.severity,
            1 if rule.enabled else 0,
            rule.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 네트워크 통계
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent
            network_recv = network.bytes_recv
            
            # 디스크 I/O
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes if disk_io else 0
            disk_write = disk_io.write_bytes if disk_io else 0
            
            # 로드 평균
            load_avg = psutil.getloadavg()
            
            # 업타임
            uptime = time.time() - psutil.boot_time()
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_sent=network_sent,
                network_recv=network_recv,
                disk_read=disk_read,
                disk_write=disk_write,
                load_average=load_avg,
                uptime=uptime
            )
            
            self.system_metrics.append(metrics)
            self._save_system_metrics(metrics)
            
            # 메트릭 히스토리 업데이트
            self._update_metric_history('cpu_percent', cpu_percent)
            self._update_metric_history('memory_percent', memory_percent)
            self._update_metric_history('disk_percent', disk_percent)
            
            return metrics
            
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 오류: {e}")
            return None
    
    def collect_application_metrics(self, endpoint: str = "/api/health") -> ApplicationMetrics:
        """애플리케이션 메트릭 수집"""
        try:
            start_time = time.time()
            
            # API 응답 시간 측정
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms로 변환
            
            # 임시 데이터 (실제로는 애플리케이션에서 수집)
            metrics = ApplicationMetrics(
                timestamp=datetime.utcnow(),
                endpoint=endpoint,
                response_time=response_time,
                status_code=response.status_code,
                request_count=1,
                error_count=1 if response.status_code >= 400 else 0,
                active_sessions=10,  # 임시 값
                database_connections=5  # 임시 값
            )
            
            self.application_metrics.append(metrics)
            self._save_application_metrics(metrics)
            
            # 메트릭 히스토리 업데이트
            self._update_metric_history('response_time', response_time)
            
            return metrics
            
        except Exception as e:
            logger.error(f"애플리케이션 메트릭 수집 오류: {e}")
            return None
    
    def _save_system_metrics(self, metrics: SystemMetrics):
        """시스템 메트릭을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'monitoring.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_metrics 
            (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv, 
             disk_read, disk_write, load_average_1, load_average_5, load_average_15, uptime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.timestamp.isoformat(),
            metrics.cpu_percent,
            metrics.memory_percent,
            metrics.disk_percent,
            metrics.network_sent,
            metrics.network_recv,
            metrics.disk_read,
            metrics.disk_write,
            metrics.load_average[0],
            metrics.load_average[1],
            metrics.load_average[2],
            metrics.uptime
        ))
        
        conn.commit()
        conn.close()
    
    def _save_application_metrics(self, metrics: ApplicationMetrics):
        """애플리케이션 메트릭을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'monitoring.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO application_metrics 
            (timestamp, endpoint, response_time, status_code, request_count, error_count, 
             active_sessions, database_connections)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.timestamp.isoformat(),
            metrics.endpoint,
            metrics.response_time,
            metrics.status_code,
            metrics.request_count,
            metrics.error_count,
            metrics.active_sessions,
            metrics.database_connections
        ))
        
        conn.commit()
        conn.close()
    
    def _update_metric_history(self, metric_name: str, value: float):
        """메트릭 히스토리 업데이트"""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = []
        
        self.metric_history[metric_name].append(value)
        
        # 최근 100개만 유지
        if len(self.metric_history[metric_name]) > 100:
            self.metric_history[metric_name] = self.metric_history[metric_name][-100:]
    
    def check_alert_rules(self):
        """알림 규칙 확인"""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            # 메트릭 값 가져오기
            current_value = self._get_current_metric_value(rule.metric_type, rule.metric_name)
            if current_value is None:
                continue
            
            # 규칙 조건 확인
            if self._evaluate_rule(rule, current_value):
                # 알림 생성
                self._create_alert(rule, current_value)
            else:
                # 기존 알림 해결
                self._resolve_alert(rule.rule_id)
    
    def _get_current_metric_value(self, metric_type: str, metric_name: str) -> Optional[float]:
        """현재 메트릭 값 가져오기"""
        if metric_type == 'system':
            if not self.system_metrics:
                return None
            
            latest = self.system_metrics[-1]
            return getattr(latest, metric_name, None)
        
        elif metric_type == 'application':
            if not self.application_metrics:
                return None
            
            latest = self.application_metrics[-1]
            return getattr(latest, metric_name, None)
        
        return None
    
    def _evaluate_rule(self, rule: AlertRule, current_value: float) -> bool:
        """알림 규칙 평가"""
        if rule.operator == '>':
            return current_value > rule.threshold
        elif rule.operator == '<':
            return current_value < rule.threshold
        elif rule.operator == '>=':
            return current_value >= rule.threshold
        elif rule.operator == '<=':
            return current_value <= rule.threshold
        elif rule.operator == '==':
            return current_value == rule.threshold
        elif rule.operator == '!=':
            return current_value != rule.threshold
        
        return False
    
    def _create_alert(self, rule: AlertRule, current_value: float):
        """알림 생성"""
        alert_id = self._generate_id()
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            metric_type=rule.metric_type,
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold=rule.threshold,
            severity=rule.severity,
            message=f"{rule.name}: {current_value:.2f} {rule.operator} {rule.threshold}",
            timestamp=datetime.utcnow()
        )
        
        self.active_alerts[alert_id] = alert
        self._save_alert(alert)
        
        # 알림 전송
        self._send_alert_notification(alert)
        
        logger.warning(f"알림 생성: {alert.message}")
    
    def _resolve_alert(self, rule_id: str):
        """알림 해결"""
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.rule_id == rule_id and alert.status == "active":
                alert.status = "resolved"
                alert.resolved_at = datetime.utcnow()
                self._update_alert(alert)
                
                logger.info(f"알림 해결: {alert.message}")
    
    def _save_alert(self, alert: Alert):
        """알림을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'monitoring.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts 
            (alert_id, rule_id, metric_type, metric_name, current_value, threshold, 
             severity, message, timestamp, status, acknowledged_by, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.alert_id,
            alert.rule_id,
            alert.metric_type,
            alert.metric_name,
            alert.current_value,
            alert.threshold,
            alert.severity,
            alert.message,
            alert.timestamp.isoformat(),
            alert.status,
            alert.acknowledged_by,
            alert.resolved_at.isoformat() if alert.resolved_at else None
        ))
        
        conn.commit()
        conn.close()
    
    def _update_alert(self, alert: Alert):
        """알림 업데이트"""
        db_path = os.path.join(self.config.data_dir, 'monitoring.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE alerts 
            SET status = ?, resolved_at = ?
            WHERE alert_id = ?
        ''', (
            alert.status,
            alert.resolved_at.isoformat() if alert.resolved_at else None,
            alert.alert_id
        ))
        
        conn.commit()
        conn.close()
    
    def _send_alert_notification(self, alert: Alert):
        """알림 전송"""
        if not self.config.alert_enabled:
            return
        
        # 이메일 알림
        if self.config.email_enabled:
            self._send_email_alert(alert)
        
        # 웹훅 알림
        if self.config.webhook_enabled:
            self._send_webhook_alert(alert)
    
    def _send_email_alert(self, alert: Alert):
        """이메일 알림 전송"""
        # 실제 구현에서는 SMTP 설정 필요
        logger.info(f"이메일 알림 전송: {alert.message}")
    
    def _send_webhook_alert(self, alert: Alert):
        """웹훅 알림 전송"""
        # 실제 구현에서는 웹훅 URL 설정 필요
        logger.info(f"웹훅 알림 전송: {alert.message}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """시스템 통계 조회"""
        if not self.system_metrics:
            return {}
        
        latest = self.system_metrics[-1]
        
        # 최근 1시간 평균
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_metrics = [m for m in self.system_metrics if m.timestamp > one_hour_ago]
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        avg_disk = sum(m.disk_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        return {
            'current_cpu': latest.cpu_percent,
            'current_memory': latest.memory_percent,
            'current_disk': latest.disk_percent,
            'avg_cpu_1h': avg_cpu,
            'avg_memory_1h': avg_memory,
            'avg_disk_1h': avg_disk,
            'uptime_hours': latest.uptime / 3600,
            'load_average': latest.load_average,
            'active_alerts': len([a for a in self.active_alerts.values() if a.status == "active"])
        }
    
    def get_application_stats(self) -> Dict[str, Any]:
        """애플리케이션 통계 조회"""
        if not self.application_metrics:
            return {}
        
        latest = self.application_metrics[-1]
        
        # 최근 1시간 통계
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_metrics = [m for m in self.application_metrics if m.timestamp > one_hour_ago]
        
        total_requests = sum(m.request_count for m in recent_metrics)
        total_errors = sum(m.error_count for m in recent_metrics)
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        return {
            'current_response_time': latest.response_time,
            'current_status_code': latest.status_code,
            'avg_response_time_1h': avg_response_time,
            'total_requests_1h': total_requests,
            'total_errors_1h': total_errors,
            'error_rate_1h': (total_errors / total_requests * 100) if total_requests > 0 else 0,
            'active_sessions': latest.active_sessions,
            'database_connections': latest.database_connections
        }
    
    def get_metric_history(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """메트릭 히스토리 조회"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        if metric_name in ['cpu_percent', 'memory_percent', 'disk_percent']:
            metrics = [m for m in self.system_metrics if m.timestamp > cutoff_time]
            return [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'value': getattr(m, metric_name)
                }
                for m in metrics
            ]
        
        elif metric_name == 'response_time':
            metrics = [m for m in self.application_metrics if m.timestamp > cutoff_time]
            return [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'value': m.response_time
                }
                for m in metrics
            ]
        
        return []
    
    def get_alerts(self, status: Optional[str] = None, limit: int = 100) -> List[Alert]:
        """알림 조회"""
        alerts = list(self.active_alerts.values())
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        # 최신 순으로 정렬
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        return alerts[:limit]
    
    def acknowledge_alert(self, alert_id: str, user: str):
        """알림 승인"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = "acknowledged"
            alert.acknowledged_by = user
            self._update_alert(alert)
            
            logger.info(f"알림 승인: {alert_id} by {user}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("모니터링이 시작되었습니다")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("모니터링이 중지되었습니다")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_running:
            try:
                # 시스템 메트릭 수집
                self.collect_system_metrics()
                
                # 애플리케이션 메트릭 수집
                self.collect_application_metrics()
                
                # 알림 규칙 확인
                self.check_alert_rules()
                
                # 오래된 데이터 정리
                self._cleanup_old_data()
                
                time.sleep(self.config.collection_interval)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(10)  # 오류 시 10초 대기
    
    def _cleanup_old_data(self):
        """오래된 데이터 정리"""
        cutoff_time = datetime.utcnow() - timedelta(days=self.config.retention_days)
        
        # 메모리에서 오래된 데이터 제거
        self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff_time]
        self.application_metrics = [m for m in self.application_metrics if m.timestamp > cutoff_time]
        
        # 데이터베이스에서 오래된 데이터 제거
        self._cleanup_database(cutoff_time)
    
    def _cleanup_database(self, cutoff_time: datetime):
        """데이터베이스에서 오래된 데이터 정리"""
        db_path = os.path.join(self.config.data_dir, 'monitoring.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cutoff_str = cutoff_time.isoformat()
        
        cursor.execute('DELETE FROM system_metrics WHERE timestamp < ?', (cutoff_str,))
        cursor.execute('DELETE FROM application_metrics WHERE timestamp < ?', (cutoff_str,))
        
        conn.commit()
        conn.close() 