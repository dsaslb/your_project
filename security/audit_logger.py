"""
보안 감사 로그 시스템
모든 보안 관련 이벤트를 기록하고 분석하는 고급 보안 시스템
"""
import json
import logging
import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import threading
import queue
import time
from dataclasses import dataclass, asdict
import ipaddress
import re

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """보안 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EventType(Enum):
    """이벤트 타입"""
    # 인증 관련
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_VERIFICATION = "mfa_verification"
    MFA_FAILURE = "mfa_failure"
    
    # 권한 관련
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ROLE_CHANGED = "role_changed"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    
    # 데이터 관련
    DATA_ACCESSED = "data_accessed"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    
    # 시스템 관련
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGED = "configuration_changed"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    # 보안 관련
    SECURITY_ALERT = "security_alert"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"
    
    # 네트워크 관련
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_CLOSED = "connection_closed"
    CONNECTION_REJECTED = "connection_rejected"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

@dataclass
class AuditEvent:
    """감사 이벤트 데이터 클래스"""
    event_id: str
    timestamp: datetime
    event_type: EventType
    security_level: SecurityLevel
    user_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    details: Dict[str, Any]
    success: bool
    risk_score: float

class AuditLogger:
    """보안 감사 로그 시스템 클래스"""
    
    def __init__(self, db_path: str = "security/audit_logs.db"):
        """초기화"""
        self.db_path = db_path
        self.initialize_database()
        
        # 로그 큐 (비동기 처리용)
        self.log_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self.processing_thread.start()
        
        # 위험 점수 계산기
        self.risk_calculator = RiskCalculator()
        
        # 이상 탐지기
        self.anomaly_detector = AnomalyDetector()
        
        # 알림 시스템
        self.alert_system = AlertSystem()
        
        logger.info("보안 감사 로그 시스템 초기화 완료")
    
    def initialize_database(self):
        """데이터베이스 초기화"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 감사 로그 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    security_level TEXT NOT NULL,
                    user_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    resource TEXT,
                    action TEXT,
                    details TEXT,
                    success BOOLEAN,
                    risk_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON audit_logs(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON audit_logs(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_level ON audit_logs(security_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_address ON audit_logs(ip_address)')
            
            conn.commit()
            conn.close()
            
            logger.info("감사 로그 데이터베이스 초기화 완료")
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {str(e)}")
            raise
    
    def log_event(self, event_type: EventType, security_level: SecurityLevel, 
                  user_id: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None, session_id: Optional[str] = None,
                  resource: Optional[str] = None, action: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None, success: bool = True):
        """이벤트 로깅"""
        try:
            # 이벤트 ID 생성
            event_id = self._generate_event_id()
            
            # 위험 점수 계산
            risk_score = self.risk_calculator.calculate_risk(
                event_type, security_level, user_id, ip_address, details
            )
            
            # 감사 이벤트 생성
            event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                event_type=event_type,
                security_level=security_level,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                resource=resource,
                action=action,
                details=details or {},
                success=success,
                risk_score=risk_score
            )
            
            # 로그 큐에 추가 (비동기 처리)
            self.log_queue.put(event)
            
            # 높은 위험도 이벤트는 즉시 처리
            if risk_score >= 0.7:
                self._process_event_immediately(event)
            
            return event_id
        except Exception as e:
            logger.error(f"이벤트 로깅 오류: {str(e)}")
            raise
    
    def _process_log_queue(self):
        """로그 큐 처리 (비동기)"""
        while True:
            try:
                event = self.log_queue.get(timeout=1)
                self._save_event_to_database(event)
                self._analyze_event(event)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"로그 큐 처리 오류: {str(e)}")
    
    def _process_event_immediately(self, event: AuditEvent):
        """이벤트 즉시 처리 (높은 위험도)"""
        try:
            # 이상 탐지
            if self.anomaly_detector.detect_anomaly(event):
                self.alert_system.send_alert(
                    "anomaly_detected",
                    f"이상 활동 탐지: {event.event_type.value}",
                    event
                )
            
            # 위험도 기반 알림
            if event.risk_score >= 0.8:
                self.alert_system.send_alert(
                    "high_risk_event",
                    f"높은 위험도 이벤트: {event.event_type.value}",
                    event
                )
        except Exception as e:
            logger.error(f"이벤트 즉시 처리 오류: {str(e)}")
    
    def _save_event_to_database(self, event: AuditEvent):
        """이벤트를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_logs (
                    event_id, timestamp, event_type, security_level, user_id,
                    ip_address, user_agent, session_id, resource, action,
                    details, success, risk_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.timestamp.isoformat(),
                event.event_type.value,
                event.security_level.value,
                event.user_id,
                event.ip_address,
                event.user_agent,
                event.session_id,
                event.resource,
                event.action,
                json.dumps(event.details),
                event.success,
                event.risk_score
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"이벤트 저장 오류: {str(e)}")
    
    def _analyze_event(self, event: AuditEvent):
        """이벤트 분석"""
        try:
            # 이상 탐지
            if self.anomaly_detector.detect_anomaly(event):
                logger.warning(f"이상 활동 탐지: {event.event_id}")
            
            # 패턴 분석
            patterns = self._analyze_patterns(event)
            if patterns:
                logger.info(f"패턴 발견: {patterns}")
            
        except Exception as e:
            logger.error(f"이벤트 분석 오류: {str(e)}")
    
    def _analyze_patterns(self, event: AuditEvent) -> List[str]:
        """패턴 분석"""
        patterns = []
        
        try:
            # 시간 패턴 분석
            if self._is_off_hours(event.timestamp):
                patterns.append("비정상 시간 활동")
            
            # IP 패턴 분석
            if event.ip_address and self._is_suspicious_ip(event.ip_address):
                patterns.append("의심스러운 IP")
            
            # 사용자 패턴 분석
            if event.user_id and self._is_suspicious_user(event.user_id):
                patterns.append("의심스러운 사용자 활동")
            
            # 리소스 패턴 분석
            if event.resource and self._is_sensitive_resource(event.resource):
                patterns.append("민감한 리소스 접근")
            
        except Exception as e:
            logger.error(f"패턴 분석 오류: {str(e)}")
        
        return patterns
    
    def _is_off_hours(self, timestamp: datetime) -> bool:
        """비정상 시간 확인"""
        hour = timestamp.hour
        return hour < 6 or hour > 22
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """의심스러운 IP 확인"""
        try:
            # 사설 IP 범위 확인
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                return False
            
            # 알려진 악성 IP 목록 확인 (실제로는 DB나 API 사용)
            malicious_ips = [
                "192.168.1.100",  # 예시
                "10.0.0.50"       # 예시
            ]
            
            return ip_address in malicious_ips
        except Exception:
            return True
    
    def _is_suspicious_user(self, user_id: str) -> bool:
        """의심스러운 사용자 확인"""
        # 실제로는 사용자 활동 패턴 분석
        return False
    
    def _is_sensitive_resource(self, resource: str) -> bool:
        """민감한 리소스 확인"""
        sensitive_patterns = [
            r'/admin/',
            r'/api/admin/',
            r'/security/',
            r'/config/',
            r'password',
            r'secret',
            r'token'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, resource, re.IGNORECASE):
                return True
        
        return False
    
    def _generate_event_id(self) -> str:
        """이벤트 ID 생성"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        random_part = os.urandom(8).hex()
        return f"{timestamp}_{random_part}"
    
    def get_events(self, filters: Optional[Dict[str, Any]] = None, 
                   limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """이벤트 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if filters:
                if 'user_id' in filters:
                    query += " AND user_id = ?"
                    params.append(filters['user_id'])
                
                if 'event_type' in filters:
                    query += " AND event_type = ?"
                    params.append(filters['event_type'])
                
                if 'security_level' in filters:
                    query += " AND security_level = ?"
                    params.append(filters['security_level'])
                
                if 'start_date' in filters:
                    query += " AND timestamp >= ?"
                    params.append(filters['start_date'])
                
                if 'end_date' in filters:
                    query += " AND timestamp <= ?"
                    params.append(filters['end_date'])
                
                if 'min_risk_score' in filters:
                    query += " AND risk_score >= ?"
                    params.append(filters['min_risk_score'])
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = {
                    'event_id': row[0],
                    'timestamp': row[1],
                    'event_type': row[2],
                    'security_level': row[3],
                    'user_id': row[4],
                    'ip_address': row[5],
                    'user_agent': row[6],
                    'session_id': row[7],
                    'resource': row[8],
                    'action': row[9],
                    'details': json.loads(row[10]) if row[10] else {},
                    'success': bool(row[11]),
                    'risk_score': row[12]
                }
                events.append(event)
            
            conn.close()
            return events
        except Exception as e:
            logger.error(f"이벤트 조회 오류: {str(e)}")
            return []
    
    def get_security_summary(self, days: int = 30) -> Dict[str, Any]:
        """보안 요약 통계"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 전체 이벤트 수
            cursor.execute(
                "SELECT COUNT(*) FROM audit_logs WHERE timestamp >= ?",
                [start_date]
            )
            total_events = cursor.fetchone()[0]
            
            # 보안 레벨별 통계
            cursor.execute('''
                SELECT security_level, COUNT(*) 
                FROM audit_logs 
                WHERE timestamp >= ? 
                GROUP BY security_level
            ''', [start_date])
            security_level_stats = dict(cursor.fetchall())
            
            # 이벤트 타입별 통계
            cursor.execute('''
                SELECT event_type, COUNT(*) 
                FROM audit_logs 
                WHERE timestamp >= ? 
                GROUP BY event_type
            ''', [start_date])
            event_type_stats = dict(cursor.fetchall())
            
            # 높은 위험도 이벤트
            cursor.execute('''
                SELECT COUNT(*) 
                FROM audit_logs 
                WHERE timestamp >= ? AND risk_score >= 0.7
            ''', [start_date])
            high_risk_events = cursor.fetchone()[0]
            
            # 실패한 이벤트
            cursor.execute('''
                SELECT COUNT(*) 
                FROM audit_logs 
                WHERE timestamp >= ? AND success = 0
            ''', [start_date])
            failed_events = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_events': total_events,
                'security_level_stats': security_level_stats,
                'event_type_stats': event_type_stats,
                'high_risk_events': high_risk_events,
                'failed_events': failed_events,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"보안 요약 통계 오류: {str(e)}")
            return {}
    
    def cleanup_old_logs(self, days: int = 90):
        """오래된 로그 정리"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM audit_logs WHERE timestamp < ?",
                [cutoff_date]
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"오래된 로그 {deleted_count}개 정리 완료")
            return deleted_count
        except Exception as e:
            logger.error(f"로그 정리 오류: {str(e)}")
            return 0

class RiskCalculator:
    """위험 점수 계산기"""
    
    def calculate_risk(self, event_type: EventType, security_level: SecurityLevel,
                      user_id: Optional[str], ip_address: Optional[str],
                      details: Optional[Dict[str, Any]]) -> float:
        """위험 점수 계산"""
        risk_score = 0.0
        
        # 기본 위험 점수
        if security_level == SecurityLevel.CRITICAL:
            risk_score += 0.8
        elif security_level == SecurityLevel.HIGH:
            risk_score += 0.6
        elif security_level == SecurityLevel.MEDIUM:
            risk_score += 0.4
        else:
            risk_score += 0.2
        
        # 이벤트 타입별 위험 점수
        high_risk_events = [
            EventType.LOGIN_FAILURE,
            EventType.MFA_FAILURE,
            EventType.PERMISSION_DENIED,
            EventType.ACCESS_DENIED,
            EventType.SECURITY_ALERT,
            EventType.SUSPICIOUS_ACTIVITY,
            EventType.BRUTE_FORCE_ATTEMPT,
            EventType.SQL_INJECTION_ATTEMPT,
            EventType.XSS_ATTEMPT,
            EventType.CSRF_ATTEMPT
        ]
        
        if event_type in high_risk_events:
            risk_score += 0.3
        
        # 사용자 관련 위험 점수
        if not user_id:
            risk_score += 0.2  # 익명 사용자
        
        # IP 관련 위험 점수
        if ip_address:
            # 사설 IP는 낮은 위험도
            try:
                ip = ipaddress.ip_address(ip_address)
                if not ip.is_private:
                    risk_score += 0.1
            except:
                risk_score += 0.1
        
        # 세부 정보 기반 위험 점수
        if details:
            if 'failed_attempts' in details:
                risk_score += min(details['failed_attempts'] * 0.1, 0.5)
            
            if 'suspicious_pattern' in details:
                risk_score += 0.3
        
        return min(risk_score, 1.0)  # 최대 1.0

class AnomalyDetector:
    """이상 탐지기"""
    
    def __init__(self):
        self.user_activity_patterns = {}
        self.ip_activity_patterns = {}
    
    def detect_anomaly(self, event: AuditEvent) -> bool:
        """이상 탐지"""
        try:
            # 사용자 활동 패턴 분석
            if event.user_id and self._detect_user_anomaly(event):
                return True
            
            # IP 활동 패턴 분석
            if event.ip_address and self._detect_ip_anomaly(event):
                return True
            
            # 시간 패턴 분석
            if self._detect_time_anomaly(event):
                return True
            
            return False
        except Exception as e:
            logger.error(f"이상 탐지 오류: {str(e)}")
            return False
    
    def _detect_user_anomaly(self, event: AuditEvent) -> bool:
        """사용자 이상 탐지"""
        if event.user_id not in self.user_activity_patterns:
            self.user_activity_patterns[event.user_id] = {
                'last_activity': event.timestamp,
                'activity_count': 1,
                'failed_attempts': 0
            }
            return False
        
        pattern = self.user_activity_patterns[event.user_id]
        
        # 실패한 시도 카운트
        if not event.success:
            pattern['failed_attempts'] += 1
            if pattern['failed_attempts'] >= 5:
                return True
        else:
            pattern['failed_attempts'] = 0
        
        # 활동 빈도 분석
        time_diff = (event.timestamp - pattern['last_activity']).total_seconds()
        if time_diff < 1:  # 1초 내 연속 활동
            pattern['activity_count'] += 1
            if pattern['activity_count'] > 10:
                return True
        else:
            pattern['activity_count'] = 1
        
        pattern['last_activity'] = event.timestamp
        return False
    
    def _detect_ip_anomaly(self, event: AuditEvent) -> bool:
        """IP 이상 탐지"""
        if event.ip_address not in self.ip_activity_patterns:
            self.ip_activity_patterns[event.ip_address] = {
                'last_activity': event.timestamp,
                'activity_count': 1
            }
            return False
        
        pattern = self.ip_activity_patterns[event.ip_address]
        
        # 활동 빈도 분석
        time_diff = (event.timestamp - pattern['last_activity']).total_seconds()
        if time_diff < 1:  # 1초 내 연속 활동
            pattern['activity_count'] += 1
            if pattern['activity_count'] > 20:
                return True
        else:
            pattern['activity_count'] = 1
        
        pattern['last_activity'] = event.timestamp
        return False
    
    def _detect_time_anomaly(self, event: AuditEvent) -> bool:
        """시간 이상 탐지"""
        hour = event.timestamp.hour
        return hour < 2 or hour > 5  # 새벽 2-5시는 의심스러운 시간

class AlertSystem:
    """알림 시스템"""
    
    def __init__(self):
        self.alert_handlers = {
            'anomaly_detected': self._handle_anomaly_alert,
            'high_risk_event': self._handle_high_risk_alert,
            'security_breach': self._handle_security_breach_alert
        }
    
    def send_alert(self, alert_type: str, message: str, event: AuditEvent):
        """알림 발송"""
        try:
            if alert_type in self.alert_handlers:
                self.alert_handlers[alert_type](message, event)
            
            # 로그에 기록
            logger.warning(f"보안 알림 [{alert_type}]: {message}")
            
        except Exception as e:
            logger.error(f"알림 발송 오류: {str(e)}")
    
    def _handle_anomaly_alert(self, message: str, event: AuditEvent):
        """이상 탐지 알림 처리"""
        # 실제로는 이메일, SMS, Slack 등으로 알림 발송
        pass
    
    def _handle_high_risk_alert(self, message: str, event: AuditEvent):
        """높은 위험도 알림 처리"""
        # 실제로는 즉시 알림 발송
        pass
    
    def _handle_security_breach_alert(self, message: str, event: AuditEvent):
        """보안 침해 알림 처리"""
        # 실제로는 긴급 알림 발송
        pass

# 전역 인스턴스
audit_logger = AuditLogger()

if __name__ == '__main__':
    # 테스트 코드
    print("보안 감사 로그 시스템 테스트")
    
    # 이벤트 로깅 테스트
    event_id = audit_logger.log_event(
        EventType.LOGIN_SUCCESS,
        SecurityLevel.MEDIUM,
        user_id="test_user",
        ip_address="192.168.1.100",
        success=True
    )
    print(f"이벤트 로깅: {event_id}")
    
    # 실패 이벤트 로깅
    event_id = audit_logger.log_event(
        EventType.LOGIN_FAILURE,
        SecurityLevel.HIGH,
        user_id="test_user",
        ip_address="192.168.1.100",
        success=False,
        details={'failed_attempts': 3}
    )
    print(f"실패 이벤트 로깅: {event_id}")
    
    # 이벤트 조회
    events = audit_logger.get_events(limit=10)
    print(f"이벤트 조회: {len(events)}개")
    
    # 보안 요약
    summary = audit_logger.get_security_summary(days=1)
    print(f"보안 요약: {summary}")
    
    print("보안 감사 로그 시스템 테스트 완료") 