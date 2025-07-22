"""
위협 탐지 및 대응 시스템
실시간 위협 탐지와 자동 대응을 위한 고급 보안 시스템
"""
import re
import json
import logging
import hashlib
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from enum import Enum
import ipaddress
import sqlite3
import os
from dataclasses import dataclass
import requests
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """위협 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """위협 타입"""
    # 웹 공격
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    CSRF_ATTACK = "csrf_attack"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    FILE_UPLOAD = "file_upload"
    
    # 인증 공격
    BRUTE_FORCE = "brute_force"
    PASSWORD_SPRAYING = "password_spraying"
    SESSION_HIJACKING = "session_hijacking"
    CREDENTIAL_STUFFING = "credential_stuffing"
    
    # 네트워크 공격
    DDoS_ATTACK = "ddos_attack"
    PORT_SCANNING = "port_scanning"
    MAN_IN_THE_MIDDLE = "man_in_the_middle"
    DNS_POISONING = "dns_poisoning"
    
    # 데이터 공격
    DATA_EXFILTRATION = "data_exfiltration"
    DATA_TAMPERING = "data_tampering"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    
    # 악성코드
    MALWARE_DETECTED = "malware_detected"
    RANSOMWARE_DETECTED = "ransomware_detected"
    BACKDOOR_DETECTED = "backdoor_detected"

class ResponseAction(Enum):
    """대응 액션"""
    BLOCK_IP = "block_ip"
    RATE_LIMIT = "rate_limit"
    CAPTCHA_CHALLENGE = "captcha_challenge"
    ACCOUNT_LOCKOUT = "account_lockout"
    SESSION_TERMINATION = "session_termination"
    ALERT_ADMIN = "alert_admin"
    LOG_VIOLATION = "log_violation"
    QUARANTINE_FILE = "quarantine_file"

@dataclass
class ThreatEvent:
    """위협 이벤트"""
    threat_id: str
    timestamp: datetime
    threat_type: ThreatType
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    session_id: Optional[str]
    request_data: Dict[str, Any]
    detection_method: str
    confidence_score: float
    response_actions: List[ResponseAction]
    details: Dict[str, Any]

class ThreatDetector:
    """위협 탐지 시스템 클래스"""
    
    def __init__(self, db_path: str = "security/threats.db"):
        """초기화"""
        self.db_path = db_path
        self.initialize_database()
        
        # 위협 패턴 정의
        self.threat_patterns = self._load_threat_patterns()
        
        # IP 블랙리스트/화이트리스트
        self.ip_blacklist = set()
        self.ip_whitelist = set()
        
        # 위협 카운터
        self.threat_counters = {}
        
        # 대응 규칙
        self.response_rules = self._load_response_rules()
        
        # 알림 콜백
        self.alert_callbacks = []
        
        # 실시간 모니터링
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_threats, daemon=True)
        self.monitor_thread.start()
        
        logger.info("위협 탐지 시스템 초기화 완료")
    
    def initialize_database(self):
        """데이터베이스 초기화"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 위협 이벤트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_events (
                    threat_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    request_data TEXT,
                    detection_method TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    response_actions TEXT,
                    details TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # IP 블랙리스트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_blacklist (
                    ip_address TEXT PRIMARY KEY,
                    reason TEXT,
                    blocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT
                )
            ''')
            
            # 위협 통계 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_statistics (
                    date TEXT PRIMARY KEY,
                    total_threats INTEGER DEFAULT 0,
                    threats_by_type TEXT,
                    threats_by_level TEXT,
                    blocked_ips INTEGER DEFAULT 0
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_timestamp ON threat_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_type ON threat_events(threat_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_level ON threat_events(threat_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_ip ON threat_events(source_ip)')
            
            conn.commit()
            conn.close()
            
            logger.info("위협 탐지 데이터베이스 초기화 완료")
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {str(e)}")
            raise
    
    def _load_threat_patterns(self) -> Dict[ThreatType, List[Dict[str, Any]]]:
        """위협 패턴 로드"""
        return {
            ThreatType.SQL_INJECTION: [
                {
                    'pattern': r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
                    'flags': re.IGNORECASE,
                    'weight': 0.8
                },
                {
                    'pattern': r"(--|#|/\*|\*/|xp_|sp_)",
                    'weight': 0.6
                },
                {
                    'pattern': r"(\b(and|or)\b\s+\d+\s*=\s*\d+)",
                    'flags': re.IGNORECASE,
                    'weight': 0.7
                }
            ],
            ThreatType.XSS_ATTACK: [
                {
                    'pattern': r"(<script[^>]*>.*?</script>)",
                    'flags': re.IGNORECASE | re.DOTALL,
                    'weight': 0.9
                },
                {
                    'pattern': r"(javascript:|vbscript:|onload=|onerror=|onclick=)",
                    'flags': re.IGNORECASE,
                    'weight': 0.7
                },
                {
                    'pattern': r"(<iframe|<object|<embed)",
                    'flags': re.IGNORECASE,
                    'weight': 0.6
                }
            ],
            ThreatType.CSRF_ATTACK: [
                {
                    'pattern': r"(<img[^>]*src\s*=\s*['\"][^'\"]*['\"][^>]*>)",
                    'weight': 0.5
                },
                {
                    'pattern': r"(<form[^>]*action\s*=\s*['\"][^'\"]*['\"][^>]*>)",
                    'weight': 0.4
                }
            ],
            ThreatType.PATH_TRAVERSAL: [
                {
                    'pattern': r"(\.\./|\.\.\\)",
                    'weight': 0.8
                },
                {
                    'pattern': r"(/etc/passwd|/etc/shadow|/windows/system32)",
                    'flags': re.IGNORECASE,
                    'weight': 0.9
                }
            ],
            ThreatType.COMMAND_INJECTION: [
                {
                    'pattern': r"(\b(cmd|command|exec|system|shell)\b)",
                    'flags': re.IGNORECASE,
                    'weight': 0.7
                },
                {
                    'pattern': r"(\||&|;|`|\$\(|\$\{)",
                    'weight': 0.6
                }
            ],
            ThreatType.BRUTE_FORCE: [
                {
                    'pattern': r"(failed.*login|invalid.*password)",
                    'flags': re.IGNORECASE,
                    'weight': 0.5
                }
            ]
        }
    
    def _load_response_rules(self) -> Dict[ThreatType, List[ResponseAction]]:
        """대응 규칙 로드"""
        return {
            ThreatType.SQL_INJECTION: [
                ResponseAction.BLOCK_IP,
                ResponseAction.ALERT_ADMIN,
                ResponseAction.LOG_VIOLATION
            ],
            ThreatType.XSS_ATTACK: [
                ResponseAction.BLOCK_IP,
                ResponseAction.ALERT_ADMIN,
                ResponseAction.LOG_VIOLATION
            ],
            ThreatType.BRUTE_FORCE: [
                ResponseAction.RATE_LIMIT,
                ResponseAction.ACCOUNT_LOCKOUT,
                ResponseAction.CAPTCHA_CHALLENGE,
                ResponseAction.ALERT_ADMIN
            ],
            ThreatType.DDoS_ATTACK: [
                ResponseAction.BLOCK_IP,
                ResponseAction.RATE_LIMIT,
                ResponseAction.ALERT_ADMIN
            ]
        }
    
    def detect_threat(self, request_data: Dict[str, Any], 
                     source_ip: str, user_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> Optional[ThreatEvent]:
        """위협 탐지"""
        try:
            # IP 화이트리스트 확인
            if source_ip in self.ip_whitelist:
                return None
            
            # IP 블랙리스트 확인
            if source_ip in self.ip_blacklist:
                return self._create_threat_event(
                    ThreatType.BRUTE_FORCE,
                    ThreatLevel.HIGH,
                    source_ip, user_id, session_id, request_data,
                    "blacklisted_ip", 1.0
                )
            
            detected_threats = []
            
            # SQL 인젝션 탐지
            sql_threat = self._detect_sql_injection(request_data)
            if sql_threat:
                detected_threats.append(sql_threat)
            
            # XSS 공격 탐지
            xss_threat = self._detect_xss_attack(request_data)
            if xss_threat:
                detected_threats.append(xss_threat)
            
            # CSRF 공격 탐지
            csrf_threat = self._detect_csrf_attack(request_data)
            if csrf_threat:
                detected_threats.append(csrf_threat)
            
            # 경로 순회 공격 탐지
            path_threat = self._detect_path_traversal(request_data)
            if path_threat:
                detected_threats.append(path_threat)
            
            # 명령어 인젝션 탐지
            cmd_threat = self._detect_command_injection(request_data)
            if cmd_threat:
                detected_threats.append(cmd_threat)
            
            # 브루트 포스 공격 탐지
            brute_threat = self._detect_brute_force(source_ip, user_id)
            if brute_threat:
                detected_threats.append(brute_threat)
            
            # DDoS 공격 탐지
            ddos_threat = self._detect_ddos_attack(source_ip)
            if ddos_threat:
                detected_threats.append(ddos_threat)
            
            # 가장 높은 위험도의 위협 반환
            if detected_threats:
                return max(detected_threats, key=lambda x: x.confidence_score)
            
            return None
            
        except Exception as e:
            logger.error(f"위협 탐지 오류: {str(e)}")
            return None
    
    def _detect_sql_injection(self, request_data: Dict[str, Any]) -> Optional[ThreatEvent]:
        """SQL 인젝션 탐지"""
        patterns = self.threat_patterns[ThreatType.SQL_INJECTION]
        
        for field, value in request_data.items():
            if isinstance(value, str):
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    flags = pattern_info.get('flags', 0)
                    weight = pattern_info['weight']
                    
                    if re.search(pattern, value, flags):
                        return self._create_threat_event(
                            ThreatType.SQL_INJECTION,
                            ThreatLevel.CRITICAL,
                            request_data.get('source_ip', ''),
                            request_data.get('user_id'),
                            request_data.get('session_id'),
                            request_data,
                            f"sql_pattern_match_{pattern[:20]}",
                            weight,
                            details={'field': field, 'value': value[:100]}
                        )
        
        return None
    
    def _detect_xss_attack(self, request_data: Dict[str, Any]) -> Optional[ThreatEvent]:
        """XSS 공격 탐지"""
        patterns = self.threat_patterns[ThreatType.XSS_ATTACK]
        
        for field, value in request_data.items():
            if isinstance(value, str):
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    flags = pattern_info.get('flags', 0)
                    weight = pattern_info['weight']
                    
                    if re.search(pattern, value, flags):
                        return self._create_threat_event(
                            ThreatType.XSS_ATTACK,
                            ThreatLevel.HIGH,
                            request_data.get('source_ip', ''),
                            request_data.get('user_id'),
                            request_data.get('session_id'),
                            request_data,
                            f"xss_pattern_match_{pattern[:20]}",
                            weight,
                            details={'field': field, 'value': value[:100]}
                        )
        
        return None
    
    def _detect_csrf_attack(self, request_data: Dict[str, Any]) -> Optional[ThreatEvent]:
        """CSRF 공격 탐지"""
        patterns = self.threat_patterns[ThreatType.CSRF_ATTACK]
        
        for field, value in request_data.items():
            if isinstance(value, str):
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    weight = pattern_info['weight']
                    
                    if re.search(pattern, value):
                        return self._create_threat_event(
                            ThreatType.CSRF_ATTACK,
                            ThreatLevel.MEDIUM,
                            request_data.get('source_ip', ''),
                            request_data.get('user_id'),
                            request_data.get('session_id'),
                            request_data,
                            f"csrf_pattern_match_{pattern[:20]}",
                            weight,
                            details={'field': field, 'value': value[:100]}
                        )
        
        return None
    
    def _detect_path_traversal(self, request_data: Dict[str, Any]) -> Optional[ThreatEvent]:
        """경로 순회 공격 탐지"""
        patterns = self.threat_patterns[ThreatType.PATH_TRAVERSAL]
        
        for field, value in request_data.items():
            if isinstance(value, str):
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    flags = pattern_info.get('flags', 0)
                    weight = pattern_info['weight']
                    
                    if re.search(pattern, value, flags):
                        return self._create_threat_event(
                            ThreatType.PATH_TRAVERSAL,
                            ThreatLevel.HIGH,
                            request_data.get('source_ip', ''),
                            request_data.get('user_id'),
                            request_data.get('session_id'),
                            request_data,
                            f"path_traversal_match_{pattern[:20]}",
                            weight,
                            details={'field': field, 'value': value[:100]}
                        )
        
        return None
    
    def _detect_command_injection(self, request_data: Dict[str, Any]) -> Optional[ThreatEvent]:
        """명령어 인젝션 탐지"""
        patterns = self.threat_patterns[ThreatType.COMMAND_INJECTION]
        
        for field, value in request_data.items():
            if isinstance(value, str):
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    flags = pattern_info.get('flags', 0)
                    weight = pattern_info['weight']
                    
                    if re.search(pattern, value, flags):
                        return self._create_threat_event(
                            ThreatType.COMMAND_INJECTION,
                            ThreatLevel.CRITICAL,
                            request_data.get('source_ip', ''),
                            request_data.get('user_id'),
                            request_data.get('session_id'),
                            request_data,
                            f"cmd_injection_match_{pattern[:20]}",
                            weight,
                            details={'field': field, 'value': value[:100]}
                        )
        
        return None
    
    def _detect_brute_force(self, source_ip: str, user_id: Optional[str]) -> Optional[ThreatEvent]:
        """브루트 포스 공격 탐지"""
        key = f"{source_ip}_{user_id or 'anonymous'}"
        
        if key not in self.threat_counters:
            self.threat_counters[key] = {
                'count': 0,
                'first_attempt': datetime.now(),
                'last_attempt': datetime.now()
            }
        
        counter = self.threat_counters[key]
        counter['count'] += 1
        counter['last_attempt'] = datetime.now()
        
        # 5분 내 10회 이상 실패 시 브루트 포스로 판단
        time_diff = (counter['last_attempt'] - counter['first_attempt']).total_seconds()
        if counter['count'] >= 10 and time_diff <= 300:
            return self._create_threat_event(
                ThreatType.BRUTE_FORCE,
                ThreatLevel.HIGH,
                source_ip, user_id, None, {},
                "brute_force_detected",
                0.9,
                details={
                    'attempts': counter['count'],
                    'time_window': time_diff,
                    'user_id': user_id
                }
            )
        
        return None
    
    def _detect_ddos_attack(self, source_ip: str) -> Optional[ThreatEvent]:
        """DDoS 공격 탐지"""
        key = f"ddos_{source_ip}"
        
        if key not in self.threat_counters:
            self.threat_counters[key] = {
                'count': 0,
                'first_request': datetime.now(),
                'last_request': datetime.now()
            }
        
        counter = self.threat_counters[key]
        counter['count'] += 1
        counter['last_request'] = datetime.now()
        
        # 1분 내 100회 이상 요청 시 DDoS로 판단
        time_diff = (counter['last_request'] - counter['first_request']).total_seconds()
        if counter['count'] >= 100 and time_diff <= 60:
            return self._create_threat_event(
                ThreatType.DDoS_ATTACK,
                ThreatLevel.CRITICAL,
                source_ip, None, None, {},
                "ddos_detected",
                0.95,
                details={
                    'requests': counter['count'],
                    'time_window': time_diff
                }
            )
        
        return None
    
    def _create_threat_event(self, threat_type: ThreatType, threat_level: ThreatLevel,
                           source_ip: str, user_id: Optional[str], session_id: Optional[str],
                           request_data: Dict[str, Any], detection_method: str,
                           confidence_score: float, details: Optional[Dict[str, Any]] = None) -> ThreatEvent:
        """위협 이벤트 생성"""
        threat_id = f"{threat_type.value}_{int(time.time())}_{hash(source_ip) % 10000}"
        
        # 대응 액션 결정
        response_actions = self.response_rules.get(threat_type, [ResponseAction.LOG_VIOLATION])
        
        event = ThreatEvent(
            threat_id=threat_id,
            timestamp=datetime.now(),
            threat_type=threat_type,
            threat_level=threat_level,
            source_ip=source_ip,
            user_id=user_id,
            session_id=session_id,
            request_data=request_data,
            detection_method=detection_method,
            confidence_score=confidence_score,
            response_actions=response_actions,
            details=details or {}
        )
        
        # 이벤트 저장
        self._save_threat_event(event)
        
        # 대응 액션 실행
        self._execute_response_actions(event)
        
        return event
    
    def _save_threat_event(self, event: ThreatEvent):
        """위협 이벤트 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO threat_events (
                    threat_id, timestamp, threat_type, threat_level, source_ip,
                    user_id, session_id, request_data, detection_method,
                    confidence_score, response_actions, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.threat_id,
                event.timestamp.isoformat(),
                event.threat_type.value,
                event.threat_level.value,
                event.source_ip,
                event.user_id,
                event.session_id,
                json.dumps(event.request_data),
                event.detection_method,
                event.confidence_score,
                json.dumps([action.value for action in event.response_actions]),
                json.dumps(event.details)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"위협 이벤트 저장 오류: {str(e)}")
    
    def _execute_response_actions(self, event: ThreatEvent):
        """대응 액션 실행"""
        try:
            for action in event.response_actions:
                if action == ResponseAction.BLOCK_IP:
                    self._block_ip(event.source_ip, f"Threat: {event.threat_type.value}")
                
                elif action == ResponseAction.RATE_LIMIT:
                    self._apply_rate_limit(event.source_ip)
                
                elif action == ResponseAction.ACCOUNT_LOCKOUT:
                    if event.user_id:
                        self._lockout_account(event.user_id)
                
                elif action == ResponseAction.SESSION_TERMINATION:
                    if event.session_id:
                        self._terminate_session(event.session_id)
                
                elif action == ResponseAction.ALERT_ADMIN:
                    self._send_admin_alert(event)
                
                elif action == ResponseAction.LOG_VIOLATION:
                    self._log_violation(event)
            
            # 알림 콜백 실행
            for callback in self.alert_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"알림 콜백 실행 오류: {str(e)}")
                    
        except Exception as e:
            logger.error(f"대응 액션 실행 오류: {str(e)}")
    
    def _block_ip(self, ip_address: str, reason: str):
        """IP 차단"""
        try:
            self.ip_blacklist.add(ip_address)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ip_blacklist (ip_address, reason, blocked_at)
                VALUES (?, ?, ?)
            ''', (ip_address, reason, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.warning(f"IP 차단: {ip_address} - {reason}")
        except Exception as e:
            logger.error(f"IP 차단 오류: {str(e)}")
    
    def _apply_rate_limit(self, ip_address: str):
        """속도 제한 적용"""
        # 실제로는 Redis나 다른 캐시 시스템 사용
        logger.info(f"속도 제한 적용: {ip_address}")
    
    def _lockout_account(self, user_id: str):
        """계정 잠금"""
        logger.warning(f"계정 잠금: {user_id}")
    
    def _terminate_session(self, session_id: str):
        """세션 종료"""
        logger.warning(f"세션 종료: {session_id}")
    
    def _send_admin_alert(self, event: ThreatEvent):
        """관리자 알림 발송"""
        alert_message = f"""
        🚨 보안 위협 탐지
        
        위협 타입: {event.threat_type.value}
        위협 레벨: {event.threat_level.value}
        소스 IP: {event.source_ip}
        사용자 ID: {event.user_id or 'N/A'}
        탐지 방법: {event.detection_method}
        신뢰도: {event.confidence_score:.2f}
        시간: {event.timestamp.isoformat()}
        
        세부 정보: {json.dumps(event.details, indent=2)}
        """
        
        logger.warning(alert_message)
    
    def _log_violation(self, event: ThreatEvent):
        """위반 로그 기록"""
        violation_log = {
            'timestamp': event.timestamp.isoformat(),
            'threat_type': event.threat_type.value,
            'threat_level': event.threat_level.value,
            'source_ip': event.source_ip,
            'user_id': event.user_id,
            'detection_method': event.detection_method,
            'confidence_score': event.confidence_score,
            'details': event.details
        }
        
        logger.warning(f"보안 위반: {json.dumps(violation_log)}")
    
    def add_alert_callback(self, callback: Callable[[ThreatEvent], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def get_threat_events(self, filters: Optional[Dict[str, Any]] = None,
                         limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """위협 이벤트 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM threat_events WHERE 1=1"
            params = []
            
            if filters:
                if 'threat_type' in filters:
                    query += " AND threat_type = ?"
                    params.append(filters['threat_type'])
                
                if 'threat_level' in filters:
                    query += " AND threat_level = ?"
                    params.append(filters['threat_level'])
                
                if 'source_ip' in filters:
                    query += " AND source_ip = ?"
                    params.append(filters['source_ip'])
                
                if 'start_date' in filters:
                    query += " AND timestamp >= ?"
                    params.append(filters['start_date'])
                
                if 'end_date' in filters:
                    query += " AND timestamp <= ?"
                    params.append(filters['end_date'])
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = {
                    'threat_id': row[0],
                    'timestamp': row[1],
                    'threat_type': row[2],
                    'threat_level': row[3],
                    'source_ip': row[4],
                    'user_id': row[5],
                    'session_id': row[6],
                    'request_data': json.loads(row[7]) if row[7] else {},
                    'detection_method': row[8],
                    'confidence_score': row[9],
                    'response_actions': json.loads(row[10]) if row[10] else [],
                    'details': json.loads(row[11]) if row[11] else {}
                }
                events.append(event)
            
            conn.close()
            return events
        except Exception as e:
            logger.error(f"위협 이벤트 조회 오류: {str(e)}")
            return []
    
    def get_threat_statistics(self, days: int = 30) -> Dict[str, Any]:
        """위협 통계 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 전체 위협 수
            cursor.execute(
                "SELECT COUNT(*) FROM threat_events WHERE timestamp >= ?",
                [start_date]
            )
            total_threats = cursor.fetchone()[0]
            
            # 위협 타입별 통계
            cursor.execute('''
                SELECT threat_type, COUNT(*) 
                FROM threat_events 
                WHERE timestamp >= ? 
                GROUP BY threat_type
            ''', [start_date])
            threats_by_type = dict(cursor.fetchall())
            
            # 위협 레벨별 통계
            cursor.execute('''
                SELECT threat_level, COUNT(*) 
                FROM threat_events 
                WHERE timestamp >= ? 
                GROUP BY threat_level
            ''', [start_date])
            threats_by_level = dict(cursor.fetchall())
            
            # 차단된 IP 수
            cursor.execute('SELECT COUNT(*) FROM ip_blacklist')
            blocked_ips = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_threats': total_threats,
                'threats_by_type': threats_by_type,
                'threats_by_level': threats_by_level,
                'blocked_ips': blocked_ips,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"위협 통계 조회 오류: {str(e)}")
            return {}
    
    def _monitor_threats(self):
        """위협 모니터링 (백그라운드)"""
        while self.monitoring_active:
            try:
                # 주기적으로 위협 통계 업데이트
                self._update_threat_statistics()
                
                # 오래된 카운터 정리
                self._cleanup_old_counters()
                
                time.sleep(60)  # 1분마다 실행
            except Exception as e:
                logger.error(f"위협 모니터링 오류: {str(e)}")
                time.sleep(60)
    
    def _update_threat_statistics(self):
        """위협 통계 업데이트"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            stats = self.get_threat_statistics(days=1)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_statistics 
                (date, total_threats, threats_by_type, threats_by_level, blocked_ips)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                today,
                stats.get('total_threats', 0),
                json.dumps(stats.get('threats_by_type', {})),
                json.dumps(stats.get('threats_by_level', {})),
                stats.get('blocked_ips', 0)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"위협 통계 업데이트 오류: {str(e)}")
    
    def _cleanup_old_counters(self):
        """오래된 카운터 정리"""
        try:
            current_time = datetime.now()
            keys_to_remove = []
            
            for key, counter in self.threat_counters.items():
                # 1시간 이상 된 카운터 삭제
                if (current_time - counter['last_attempt']).total_seconds() > 3600:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.threat_counters[key]
                
        except Exception as e:
            logger.error(f"카운터 정리 오류: {str(e)}")

# 전역 인스턴스
threat_detector = ThreatDetector()

if __name__ == '__main__':
    # 테스트 코드
    print("위협 탐지 시스템 테스트")
    
    # SQL 인젝션 테스트
    request_data = {
        'username': "admin' OR '1'='1",
        'password': 'test123',
        'source_ip': '192.168.1.100'
    }
    
    threat = threat_detector.detect_threat(request_data, '192.168.1.100', 'test_user')
    if threat:
        print(f"SQL 인젝션 탐지: {threat.threat_type.value}")
    
    # XSS 공격 테스트
    request_data = {
        'comment': '<script>alert("XSS")</script>',
        'source_ip': '192.168.1.101'
    }
    
    threat = threat_detector.detect_threat(request_data, '192.168.1.101')
    if threat:
        print(f"XSS 공격 탐지: {threat.threat_type.value}")
    
    # 위협 이벤트 조회
    events = threat_detector.get_threat_events(limit=10)
    print(f"위협 이벤트 조회: {len(events)}개")
    
    # 위협 통계
    stats = threat_detector.get_threat_statistics(days=1)
    print(f"위협 통계: {stats}")
    
    print("위협 탐지 시스템 테스트 완료") 