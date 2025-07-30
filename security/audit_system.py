"""
보안 감사 시스템
엔터프라이즈급 보안 모니터링 및 감사 시스템
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import ipaddress
from collections import defaultdict
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """보안 수준"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EventType(Enum):
    """이벤트 타입"""
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_FAILED = "mfa_failed"
    FILE_ACCESS = "file_access"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    PERMISSION_CHANGE = "permission_change"
    API_ACCESS = "api_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_ERROR = "system_error"
    SECURITY_ALERT = "security_alert"

@dataclass
class AuditEvent:
    """감사 이벤트"""
    event_id: str
    event_type: EventType
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    security_level: SecurityLevel
    description: str
    details: Dict[str, Any]
    success: bool
    metadata: Dict[str, Any]

@dataclass
class SecurityAlert:
    """보안 알림"""
    alert_id: str
    alert_type: str
    severity: SecurityLevel
    title: str
    description: str
    timestamp: datetime
    user_id: Optional[str]
    ip_address: str
    resolved: bool
    resolution_notes: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class ThreatIndicator:
    """위협 지표"""
    indicator_id: str
    indicator_type: str  # ip, user, behavior, pattern
    value: str
    confidence: float  # 0.0 - 1.0
    first_seen: datetime
    last_seen: datetime
    threat_level: SecurityLevel
    description: str
    metadata: Dict[str, Any]

class AuditSystem:
    """감사 시스템"""
    
    def __init__(self, db_path: str = "security/audit.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.alert_handlers: List[callable] = []
        self.threat_indicators: Dict[str, ThreatIndicator] = {}
        self.rate_limits: Dict[str, List[datetime]] = defaultdict(list)
        
        self.init_database()
        self.load_threat_indicators()
    
    def init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            # 감사 이벤트 테이블
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    security_level TEXT NOT NULL,
                    description TEXT NOT NULL,
                    details TEXT,
                    success BOOLEAN NOT NULL,
                    metadata TEXT
                )
            """)
            
            # 보안 알림 테이블
            conn.execute("""
                CREATE TABLE IF NOT EXISTS security_alerts (
                    alert_id TEXT PRIMARY KEY,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    user_id TEXT,
                    ip_address TEXT,
                    resolved BOOLEAN NOT NULL DEFAULT FALSE,
                    resolution_notes TEXT,
                    metadata TEXT
                )
            """)
            
            # 위협 지표 테이블
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_indicators (
                    indicator_id TEXT PRIMARY KEY,
                    indicator_type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    first_seen TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    threat_level TEXT NOT NULL,
                    description TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # 인덱스 생성
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON audit_events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_user_id ON audit_events(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_ip_address ON audit_events(ip_address)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_event_type ON audit_events(event_type)")
            
            conn.commit()
    
    def log_event(self, event: AuditEvent) -> bool:
        """이벤트 로깅"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO audit_events 
                    (event_id, event_type, user_id, session_id, ip_address, user_agent, 
                     timestamp, security_level, description, details, success, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.event_type.value,
                    event.user_id,
                    event.session_id,
                    event.ip_address,
                    event.user_agent,
                    event.timestamp.isoformat(),
                    event.security_level.value,
                    event.description,
                    json.dumps(event.details),
                    event.success,
                    json.dumps(event.metadata)
                ))
                conn.commit()
            
            # 실시간 분석
            self.analyze_event(event)
            
            logger.info(f"감사 이벤트 로깅 완료: {event.event_id}")
            return True
            
        except Exception as e:
            logger.error(f"감사 이벤트 로깅 오류: {e}")
            return False
    
    def analyze_event(self, event: AuditEvent):
        """이벤트 실시간 분석"""
        # 위협 지표 확인
        self.check_threat_indicators(event)
        
        # 이상 행동 패턴 감지
        self.detect_anomalies(event)
        
        # 레이트 리미팅 확인
        self.check_rate_limits(event)
        
        # 보안 알림 생성
        self.generate_alerts(event)
    
    def check_threat_indicators(self, event: AuditEvent):
        """위협 지표 확인"""
        # IP 주소 기반 위협 확인
        if event.ip_address in self.threat_indicators:
            indicator = self.threat_indicators[event.ip_address]
            if indicator.indicator_type == 'ip':
                self.create_security_alert(
                    alert_type="threat_indicator_detected",
                    severity=indicator.threat_level,
                    title=f"위협 지표 감지: {event.ip_address}",
                    description=f"알려진 위협 IP에서 활동 감지: {indicator.description}",
                    user_id=event.user_id,
                    ip_address=event.ip_address,
                    metadata={'indicator_id': indicator.indicator_id}
                )
        
        # 사용자 기반 위협 확인
        if event.user_id and event.user_id in self.threat_indicators:
            indicator = self.threat_indicators[event.user_id]
            if indicator.indicator_type == 'user':
                self.create_security_alert(
                    alert_type="suspicious_user_activity",
                    severity=indicator.threat_level,
                    title=f"의심스러운 사용자 활동: {event.user_id}",
                    description=f"의심스러운 사용자 활동 감지: {indicator.description}",
                    user_id=event.user_id,
                    ip_address=event.ip_address,
                    metadata={'indicator_id': indicator.indicator_id}
                )
    
    def detect_anomalies(self, event: AuditEvent):
        """이상 행동 패턴 감지"""
        # 로그인 실패 패턴 감지
        if event.event_type == EventType.LOGIN_FAILED:
            recent_failures = self.get_recent_events(
                event_type=EventType.LOGIN_FAILED,
                ip_address=event.ip_address,
                minutes=15
            )
            
            if len(recent_failures) >= 5:
                self.create_security_alert(
                    alert_type="brute_force_attempt",
                    severity=SecurityLevel.HIGH,
                    title="무차별 대입 공격 시도 감지",
                    description=f"IP {event.ip_address}에서 15분 내 5회 이상 로그인 실패",
                    user_id=event.user_id,
                    ip_address=event.ip_address,
                    metadata={'failure_count': len(recent_failures)}
                )
        
        # 비정상적인 시간대 활동 감지
        hour = event.timestamp.hour
        if hour < 6 or hour > 23:  # 새벽 시간대
            if event.event_type in [EventType.LOGIN, EventType.DATA_EXPORT, EventType.PERMISSION_CHANGE]:
                self.create_security_alert(
                    alert_type="unusual_time_activity",
                    severity=SecurityLevel.MEDIUM,
                    title="비정상적인 시간대 활동",
                    description=f"비정상적인 시간대({hour}시)에 {event.event_type.value} 활동 감지",
                    user_id=event.user_id,
                    ip_address=event.ip_address,
                    metadata={'hour': hour}
                )
        
        # 지리적 이상 감지
        if event.ip_address:
            # 실제 구현에서는 IP 지리 정보 서비스 사용
            # 여기서는 간단한 예시
            if self.is_suspicious_location(event.ip_address):
                self.create_security_alert(
                    alert_type="geographic_anomaly",
                    severity=SecurityLevel.MEDIUM,
                    title="지리적 이상 감지",
                    description=f"의심스러운 지역에서의 접근: {event.ip_address}",
                    user_id=event.user_id,
                    ip_address=event.ip_address
                )
    
    def check_rate_limits(self, event: AuditEvent):
        """레이트 리미팅 확인"""
        key = f"{event.ip_address}:{event.event_type.value}"
        current_time = datetime.now()
        
        # 1분 내 이벤트 수 확인
        self.rate_limits[key] = [
            t for t in self.rate_limits[key]
            if current_time - t < timedelta(minutes=1)
        ]
        self.rate_limits[key].append(current_time)
        
        # 레이트 리밋 초과 확인
        if len(self.rate_limits[key]) > 10:  # 1분 내 10회 초과
            self.create_security_alert(
                alert_type="rate_limit_exceeded",
                severity=SecurityLevel.HIGH,
                title="레이트 리밋 초과",
                description=f"IP {event.ip_address}에서 {event.event_type.value} 레이트 리밋 초과",
                user_id=event.user_id,
                ip_address=event.ip_address,
                metadata={'event_count': len(self.rate_limits[key])}
            )
    
    def create_security_alert(self, alert_type: str, severity: SecurityLevel, 
                            title: str, description: str, user_id: Optional[str] = None,
                            ip_address: Optional[str] = None, metadata: Dict[str, Any] = None):
        """보안 알림 생성"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
        
        alert = SecurityAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address or "",
            resolved=False,
            resolution_notes=None,
            metadata=metadata or {}
        )
        
        # 데이터베이스에 저장
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO security_alerts 
                (alert_id, alert_type, severity, title, description, timestamp, 
                 user_id, ip_address, resolved, resolution_notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id,
                alert.alert_type,
                alert.severity.value,
                alert.title,
                alert.description,
                alert.timestamp.isoformat(),
                alert.user_id,
                alert.ip_address,
                alert.resolved,
                alert.resolution_notes,
                json.dumps(alert.metadata)
            ))
            conn.commit()
        
        # 알림 핸들러 호출
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"알림 핸들러 오류: {e}")
        
        logger.warning(f"보안 알림 생성: {alert_id} - {title}")
    
    def get_recent_events(self, event_type: Optional[EventType] = None, 
                         user_id: Optional[str] = None, ip_address: Optional[str] = None,
                         minutes: int = 60) -> List[AuditEvent]:
        """최근 이벤트 조회"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT event_id, event_type, user_id, session_id, ip_address, user_agent,
                       timestamp, security_level, description, details, success, metadata
                FROM audit_events
                WHERE timestamp >= ?
            """
            params = [(datetime.now() - timedelta(minutes=minutes)).isoformat()]
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if ip_address:
                query += " AND ip_address = ?"
                params.append(ip_address)
            
            query += " ORDER BY timestamp DESC"
            
            cursor = conn.execute(query, params)
            events = []
            
            for row in cursor.fetchall():
                event_id, event_type, user_id, session_id, ip_address, user_agent, \
                timestamp, security_level, description, details, success, metadata = row
                
                events.append(AuditEvent(
                    event_id=event_id,
                    event_type=EventType(event_type),
                    user_id=user_id,
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=datetime.fromisoformat(timestamp),
                    security_level=SecurityLevel(security_level),
                    description=description,
                    details=json.loads(details) if details else {},
                    success=bool(success),
                    metadata=json.loads(metadata) if metadata else {}
                ))
            
            return events
    
    def get_security_alerts(self, resolved: Optional[bool] = None, 
                          severity: Optional[SecurityLevel] = None,
                          hours: int = 24) -> List[SecurityAlert]:
        """보안 알림 조회"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT alert_id, alert_type, severity, title, description, timestamp,
                       user_id, ip_address, resolved, resolution_notes, metadata
                FROM security_alerts
                WHERE timestamp >= ?
            """
            params = [(datetime.now() - timedelta(hours=hours)).isoformat()]
            
            if resolved is not None:
                query += " AND resolved = ?"
                params.append(resolved)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity.value)
            
            query += " ORDER BY timestamp DESC"
            
            cursor = conn.execute(query, params)
            alerts = []
            
            for row in cursor.fetchall():
                alert_id, alert_type, severity, title, description, timestamp, \
                user_id, ip_address, resolved, resolution_notes, metadata = row
                
                alerts.append(SecurityAlert(
                    alert_id=alert_id,
                    alert_type=alert_type,
                    severity=SecurityLevel(severity),
                    title=title,
                    description=description,
                    timestamp=datetime.fromisoformat(timestamp),
                    user_id=user_id,
                    ip_address=ip_address,
                    resolved=bool(resolved),
                    resolution_notes=resolution_notes,
                    metadata=json.loads(metadata) if metadata else {}
                ))
            
            return alerts
    
    def resolve_alert(self, alert_id: str, resolution_notes: str) -> bool:
        """알림 해결"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE security_alerts 
                    SET resolved = TRUE, resolution_notes = ?
                    WHERE alert_id = ?
                """, (resolution_notes, alert_id))
                conn.commit()
            
            logger.info(f"보안 알림 해결: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"알림 해결 오류: {e}")
            return False
    
    def add_threat_indicator(self, indicator: ThreatIndicator):
        """위협 지표 추가"""
        self.threat_indicators[indicator.value] = indicator
        
        # 데이터베이스에 저장
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO threat_indicators 
                (indicator_id, indicator_type, value, confidence, first_seen, 
                 last_seen, threat_level, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                indicator.indicator_id,
                indicator.indicator_type,
                indicator.value,
                indicator.confidence,
                indicator.first_seen.isoformat(),
                indicator.last_seen.isoformat(),
                indicator.threat_level.value,
                indicator.description,
                json.dumps(indicator.metadata)
            ))
            conn.commit()
        
        logger.info(f"위협 지표 추가: {indicator.value}")
    
    def load_threat_indicators(self):
        """위협 지표 로드"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT indicator_id, indicator_type, value, confidence, first_seen,
                       last_seen, threat_level, description, metadata
                FROM threat_indicators
            """)
            
            for row in cursor.fetchall():
                indicator_id, indicator_type, value, confidence, first_seen, \
                last_seen, threat_level, description, metadata = row
                
                indicator = ThreatIndicator(
                    indicator_id=indicator_id,
                    indicator_type=indicator_type,
                    value=value,
                    confidence=confidence,
                    first_seen=datetime.fromisoformat(first_seen),
                    last_seen=datetime.fromisoformat(last_seen),
                    threat_level=SecurityLevel(threat_level),
                    description=description,
                    metadata=json.loads(metadata) if metadata else {}
                )
                
                self.threat_indicators[value] = indicator
    
    def add_alert_handler(self, handler: callable):
        """알림 핸들러 추가"""
        self.alert_handlers.append(handler)
    
    def is_suspicious_location(self, ip_address: str) -> bool:
        """의심스러운 위치 확인"""
        # 실제 구현에서는 IP 지리 정보 서비스 사용
        # 여기서는 간단한 예시
        suspicious_ranges = [
            "192.168.1.0/24",  # 내부 네트워크
            "10.0.0.0/8",      # 내부 네트워크
            "172.16.0.0/12",   # 내부 네트워크
        ]
        
        try:
            ip = ipaddress.ip_address(ip_address)
            for range_str in suspicious_ranges:
                if ip in ipaddress.ip_network(range_str):
                    return True
        except ValueError:
            pass
        
        return False
    
    def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """보안 리포트 생성"""
        events = self.get_recent_events(minutes=hours * 60)
        alerts = self.get_security_alerts(hours=hours)
        
        # 이벤트 통계
        event_stats = defaultdict(int)
        for event in events:
            event_stats[event.event_type.value] += 1
        
        # 보안 수준별 통계
        security_stats = defaultdict(int)
        for event in events:
            security_stats[event.security_level.value] += 1
        
        # 알림 심각도별 통계
        alert_stats = defaultdict(int)
        for alert in alerts:
            alert_stats[alert.severity.value] += 1
        
        return {
            'period': f"{hours}시간",
            'total_events': len(events),
            'total_alerts': len(alerts),
            'event_stats': dict(event_stats),
            'security_stats': dict(security_stats),
            'alert_stats': dict(alert_stats),
            'unresolved_alerts': len([a for a in alerts if not a.resolved]),
            'threat_indicators': len(self.threat_indicators),
            'generated_at': datetime.now().isoformat()
        }

# 사용 예시
if __name__ == "__main__":
    # 감사 시스템 초기화
    audit_system = AuditSystem()
    
    # 알림 핸들러 등록
    def alert_handler(alert: SecurityAlert):
        print(f"보안 알림: {alert.title} - {alert.severity.value}")
    
    audit_system.add_alert_handler(alert_handler)
    
    # 위협 지표 추가
    threat_indicator = ThreatIndicator(
        indicator_id="threat_001",
        indicator_type="ip",
        value="192.168.1.100",
        confidence=0.9,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        threat_level=SecurityLevel.HIGH,
        description="알려진 악성 IP",
        metadata={'source': 'threat_intel'}
    )
    audit_system.add_threat_indicator(threat_indicator)
    
    # 감사 이벤트 로깅
    event = AuditEvent(
        event_id="event_001",
        event_type=EventType.LOGIN,
        user_id="user123",
        session_id="session_001",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0...",
        timestamp=datetime.now(),
        security_level=SecurityLevel.MEDIUM,
        description="사용자 로그인",
        details={'method': 'password'},
        success=True,
        metadata={'location': 'Seoul'}
    )
    
    audit_system.log_event(event)
    
    # 보안 리포트 생성
    report = audit_system.generate_security_report()
    print("보안 리포트:", json.dumps(report, indent=2, default=str)) 