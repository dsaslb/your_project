"""
보안 모니터링 및 침입 탐지 시스템
"""

import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import re
import ipaddress
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """위협 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AttackType(Enum):
    """공격 타입"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DOS = "dos"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_EXFILTRATION = "data_exfiltration"

@dataclass
class SecurityEvent:
    """보안 이벤트"""
    timestamp: str
    event_type: str
    source_ip: str
    user_id: Optional[str]
    session_id: Optional[str]
    threat_level: str
    attack_type: Optional[str]
    description: str
    details: Dict[str, Any]
    risk_score: float
    is_blocked: bool
    hash: str

@dataclass
class ThreatPattern:
    """위협 패턴"""
    pattern_id: str
    name: str
    description: str
    pattern_type: str
    pattern_data: str
    threat_level: str
    attack_type: str
    risk_score: float
    is_active: bool
    created_at: str

@dataclass
class IPReputation:
    """IP 평판"""
    ip_address: str
    reputation_score: float
    threat_level: str
    first_seen: str
    last_seen: str
    event_count: int
    blocked_count: int
    is_blacklisted: bool
    is_whitelisted: bool
    metadata: Dict[str, Any]

class IntrusionDetectionSystem:
    """침입 탐지 시스템"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'database_file': 'security/ids.db',
            'alert_threshold': 0.7,
            'block_threshold': 0.9,
            'time_window_minutes': 15,
            'max_events_per_ip': 100,
            'reputation_decay_days': 30,
            'auto_block_duration_hours': 24,
            'whitelist_ips': [],
            'blacklist_ips': []
        }
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 위협 패턴 초기화
        self.threat_patterns = {}
        self._init_threat_patterns()
        
        # IP 평판 관리
        self.ip_reputations = {}
        self._load_ip_reputations()
        
        # 이벤트 버퍼
        self.event_buffer = deque(maxlen=10000)
        self.buffer_lock = threading.Lock()
        
        # 실시간 모니터링
        self.monitoring_active = False
        self.monitor_thread = None
        
        # 알림 콜백
        self.alert_callbacks = []
        self.block_callbacks = []
        
        # 통계
        self.stats = {
            'total_events': 0,
            'blocked_events': 0,
            'alerted_events': 0,
            'unique_ips': set(),
            'threat_levels': defaultdict(int)
        }
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            # 보안 이벤트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    threat_level TEXT NOT NULL,
                    attack_type TEXT,
                    description TEXT NOT NULL,
                    details TEXT,
                    risk_score REAL NOT NULL,
                    is_blocked BOOLEAN DEFAULT 0,
                    hash TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 위협 패턴 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    attack_type TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # IP 평판 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_reputations (
                    ip_address TEXT PRIMARY KEY,
                    reputation_score REAL NOT NULL,
                    threat_level TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    event_count INTEGER DEFAULT 0,
                    blocked_count INTEGER DEFAULT 0,
                    is_blacklisted BOOLEAN DEFAULT 0,
                    is_whitelisted BOOLEAN DEFAULT 0,
                    metadata TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_ip ON security_events(source_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_threat_level ON security_events(threat_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_attack_type ON security_events(attack_type)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"IDS 데이터베이스 초기화 실패: {e}")
    
    def _init_threat_patterns(self):
        """위협 패턴 초기화"""
        default_patterns = [
            {
                'pattern_id': 'sql_injection_1',
                'name': 'SQL Injection - Basic',
                'description': '기본적인 SQL 인젝션 패턴',
                'pattern_type': 'regex',
                'pattern_data': r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(from|into|where|table|database)\b)",
                'threat_level': 'high',
                'attack_type': 'sql_injection',
                'risk_score': 0.8
            },
            {
                'pattern_id': 'xss_1',
                'name': 'XSS - Script Tags',
                'description': '스크립트 태그를 이용한 XSS',
                'pattern_type': 'regex',
                'pattern_data': r"<script[^>]*>.*?</script>",
                'threat_level': 'high',
                'attack_type': 'xss',
                'risk_score': 0.8
            },
            {
                'pattern_id': 'brute_force_1',
                'name': 'Brute Force - Login',
                'description': '로그인 무차별 대입 공격',
                'pattern_type': 'frequency',
                'pattern_data': 'login_failure:10:300',  # 5분 내 10회 실패
                'threat_level': 'medium',
                'attack_type': 'brute_force',
                'risk_score': 0.6
            },
            {
                'pattern_id': 'dos_1',
                'name': 'DoS - High Request Rate',
                'description': '높은 요청 빈도',
                'pattern_type': 'frequency',
                'pattern_data': 'request:100:60',  # 1분 내 100회 요청
                'threat_level': 'medium',
                'attack_type': 'dos',
                'risk_score': 0.7
            },
            {
                'pattern_id': 'suspicious_1',
                'name': 'Suspicious - Admin Access',
                'description': '관리자 페이지 접근 시도',
                'pattern_type': 'regex',
                'pattern_data': r"/admin|/manage|/config",
                'threat_level': 'medium',
                'attack_type': 'unauthorized_access',
                'risk_score': 0.5
            }
        ]
        
        for pattern_data in default_patterns:
            self.add_threat_pattern(**pattern_data)
    
    def _load_ip_reputations(self):
        """IP 평판 로드"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM ip_reputations')
            rows = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            
            for row in rows:
                reputation_data = dict(zip(columns, row))
                if reputation_data.get('metadata'):
                    reputation_data['metadata'] = json.loads(reputation_data['metadata'])
                
                self.ip_reputations[reputation_data['ip_address']] = IPReputation(**reputation_data)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"IP 평판 로드 실패: {e}")
    
    def add_threat_pattern(self, pattern_id: str, name: str, description: str, pattern_type: str,
                          pattern_data: str, threat_level: str, attack_type: str, risk_score: float) -> bool:
        """위협 패턴 추가"""
        try:
            pattern = ThreatPattern(
                pattern_id=pattern_id,
                name=name,
                description=description,
                pattern_type=pattern_type,
                pattern_data=pattern_data,
                threat_level=threat_level,
                attack_type=attack_type,
                risk_score=risk_score,
                is_active=True,
                created_at=datetime.now().isoformat()
            )
            
            self.threat_patterns[pattern_id] = pattern
            
            # 데이터베이스에 저장
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_patterns 
                (pattern_id, name, description, pattern_type, pattern_data, 
                 threat_level, attack_type, risk_score, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id, pattern.name, pattern.description, pattern.pattern_type,
                pattern.pattern_data, pattern.threat_level, pattern.attack_type,
                pattern.risk_score, pattern.is_active, pattern.created_at
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"위협 패턴 추가 완료: {pattern_id}")
            return True
            
        except Exception as e:
            logger.error(f"위협 패턴 추가 실패: {e}")
            return False
    
    def analyze_request(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """요청 분석"""
        try:
            source_ip = request_data.get('source_ip', '')
            user_id = request_data.get('user_id')
            session_id = request_data.get('session_id')
            url = request_data.get('url', '')
            method = request_data.get('method', '')
            headers = request_data.get('headers', {})
            body = request_data.get('body', '')
            user_agent = request_data.get('user_agent', '')
            
            # IP 화이트리스트 확인
            if source_ip in self.config['whitelist_ips']:
                return None
            
            # IP 블랙리스트 확인
            if source_ip in self.config['blacklist_ips']:
                return self._create_security_event(
                    event_type='blocked_ip',
                    source_ip=source_ip,
                    user_id=user_id,
                    session_id=session_id,
                    threat_level='high',
                    attack_type='unauthorized_access',
                    description=f'블랙리스트 IP 접근 시도: {source_ip}',
                    details={'url': url, 'method': method},
                    risk_score=1.0
                )
            
            # 위협 패턴 분석
            detected_threats = []
            max_risk_score = 0.0
            
            for pattern in self.threat_patterns.values():
                if not pattern.is_active:
                    continue
                
                if pattern.pattern_type == 'regex':
                    if self._check_regex_pattern(pattern, url, body, headers, user_agent):
                        detected_threats.append(pattern)
                        max_risk_score = max(max_risk_score, pattern.risk_score)
                
                elif pattern.pattern_type == 'frequency':
                    if self._check_frequency_pattern(pattern, source_ip, user_id):
                        detected_threats.append(pattern)
                        max_risk_score = max(max_risk_score, pattern.risk_score)
            
            # IP 평판 기반 위험도 조정
            ip_reputation = self._get_ip_reputation(source_ip)
            if ip_reputation:
                reputation_adjustment = (1.0 - ip_reputation.reputation_score) * 0.3
                max_risk_score = min(max_risk_score + reputation_adjustment, 1.0)
            
            # 보안 이벤트 생성
            if detected_threats:
                threat = detected_threats[0]  # 가장 높은 위험도의 첫 번째 위협
                
                event = self._create_security_event(
                    event_type='threat_detected',
                    source_ip=source_ip,
                    user_id=user_id,
                    session_id=session_id,
                    threat_level=threat.threat_level,
                    attack_type=threat.attack_type,
                    description=f'위협 패턴 감지: {threat.name}',
                    details={
                        'url': url,
                        'method': method,
                        'pattern_id': threat.pattern_id,
                        'detected_patterns': [t.pattern_id for t in detected_threats]
                    },
                    risk_score=max_risk_score
                )
                
                # IP 평판 업데이트
                self._update_ip_reputation(source_ip, max_risk_score)
                
                return event
            
            return None
            
        except Exception as e:
            logger.error(f"요청 분석 실패: {e}")
            return None
    
    def _check_regex_pattern(self, pattern: ThreatPattern, url: str, body: str, 
                           headers: Dict[str, str], user_agent: str) -> bool:
        """정규식 패턴 확인"""
        try:
            # 대소문자 무시 플래그로 정규식 컴파일
            regex = re.compile(pattern.pattern_data, re.IGNORECASE)
            
            # URL, 본문, 헤더, User-Agent에서 패턴 검색
            search_targets = [url, body, user_agent] + list(headers.values())
            
            for target in search_targets:
                if regex.search(target):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"정규식 패턴 확인 실패: {e}")
            return False
    
    def _check_frequency_pattern(self, pattern: ThreatPattern, source_ip: str, user_id: str) -> bool:
        """빈도 패턴 확인"""
        try:
            # 패턴 데이터 파싱 (예: "login_failure:10:300")
            parts = pattern.pattern_data.split(':')
            if len(parts) != 3:
                return False
            
            event_type = parts[0]
            threshold = int(parts[1])
            time_window = int(parts[2])  # 초 단위
            
            # 최근 이벤트 카운트
            recent_events = 0
            cutoff_time = datetime.now() - timedelta(seconds=time_window)
            
            with self.buffer_lock:
                for event in self.event_buffer:
                    if (event.timestamp > cutoff_time.isoformat() and
                        event.event_type == event_type and
                        event.source_ip == source_ip):
                        recent_events += 1
            
            return recent_events >= threshold
            
        except Exception as e:
            logger.error(f"빈도 패턴 확인 실패: {e}")
            return False
    
    def _create_security_event(self, event_type: str, source_ip: str, user_id: Optional[str],
                              session_id: Optional[str], threat_level: str, attack_type: Optional[str],
                              description: str, details: Dict[str, Any], risk_score: float) -> SecurityEvent:
        """보안 이벤트 생성"""
        try:
            # 이벤트 해시 생성
            event_data = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'source_ip': source_ip,
                'user_id': user_id,
                'session_id': session_id,
                'threat_level': threat_level,
                'attack_type': attack_type,
                'description': description,
                'details': details,
                'risk_score': risk_score
            }
            
            event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
            
            # 이벤트 생성
            event = SecurityEvent(
                timestamp=event_data['timestamp'],
                event_type=event_type,
                source_ip=source_ip,
                user_id=user_id,
                session_id=session_id,
                threat_level=threat_level,
                attack_type=attack_type,
                description=description,
                details=details,
                risk_score=risk_score,
                is_blocked=risk_score >= self.config['block_threshold'],
                hash=event_hash
            )
            
            # 버퍼에 추가
            with self.buffer_lock:
                self.event_buffer.append(event)
            
            # 통계 업데이트
            self.stats['total_events'] += 1
            self.stats['threat_levels'][threat_level] += 1
            self.stats['unique_ips'].add(source_ip)
            
            if event.is_blocked:
                self.stats['blocked_events'] += 1
                self._trigger_block(event)
            
            if risk_score >= self.config['alert_threshold']:
                self.stats['alerted_events'] += 1
                self._trigger_alert(event)
            
            # 데이터베이스에 저장
            self._save_event(event)
            
            return event
            
        except Exception as e:
            logger.error(f"보안 이벤트 생성 실패: {e}")
            raise
    
    def _save_event(self, event: SecurityEvent):
        """이벤트 저장"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO security_events 
                (timestamp, event_type, source_ip, user_id, session_id, threat_level,
                 attack_type, description, details, risk_score, is_blocked, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.timestamp, event.event_type, event.source_ip, event.user_id,
                event.session_id, event.threat_level, event.attack_type, event.description,
                json.dumps(event.details), event.risk_score, event.is_blocked, event.hash
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"이벤트 저장 실패: {e}")
    
    def _get_ip_reputation(self, ip_address: str) -> Optional[IPReputation]:
        """IP 평판 조회"""
        return self.ip_reputations.get(ip_address)
    
    def _update_ip_reputation(self, ip_address: str, risk_score: float):
        """IP 평판 업데이트"""
        try:
            current_time = datetime.now().isoformat()
            
            if ip_address in self.ip_reputations:
                reputation = self.ip_reputations[ip_address]
                reputation.last_seen = current_time
                reputation.event_count += 1
                
                # 평판 점수 업데이트 (가중 평균)
                reputation.reputation_score = (reputation.reputation_score * 0.7 + risk_score * 0.3)
                
                if risk_score >= self.config['block_threshold']:
                    reputation.blocked_count += 1
                    reputation.is_blacklisted = True
                
            else:
                # 새 IP 평판 생성
                reputation = IPReputation(
                    ip_address=ip_address,
                    reputation_score=risk_score,
                    threat_level=self._get_threat_level(risk_score),
                    first_seen=current_time,
                    last_seen=current_time,
                    event_count=1,
                    blocked_count=1 if risk_score >= self.config['block_threshold'] else 0,
                    is_blacklisted=risk_score >= self.config['block_threshold'],
                    is_whitelisted=False,
                    metadata={}
                )
                self.ip_reputations[ip_address] = reputation
            
            # 데이터베이스에 저장
            self._save_ip_reputation(reputation)
            
        except Exception as e:
            logger.error(f"IP 평판 업데이트 실패: {e}")
    
    def _save_ip_reputation(self, reputation: IPReputation):
        """IP 평판 저장"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ip_reputations 
                (ip_address, reputation_score, threat_level, first_seen, last_seen,
                 event_count, blocked_count, is_blacklisted, is_whitelisted, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reputation.ip_address, reputation.reputation_score, reputation.threat_level,
                reputation.first_seen, reputation.last_seen, reputation.event_count,
                reputation.blocked_count, reputation.is_blacklisted, reputation.is_whitelisted,
                json.dumps(reputation.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"IP 평판 저장 실패: {e}")
    
    def _get_threat_level(self, risk_score: float) -> str:
        """위험 점수에 따른 위협 레벨 반환"""
        if risk_score >= 0.9:
            return 'critical'
        elif risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _trigger_alert(self, event: SecurityEvent):
        """보안 알림 트리거"""
        alert_data = {
            'timestamp': event.timestamp,
            'event_type': event.event_type,
            'source_ip': event.source_ip,
            'threat_level': event.threat_level,
            'attack_type': event.attack_type,
            'description': event.description,
            'risk_score': event.risk_score,
            'details': event.details
        }
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"알림 콜백 실행 실패: {e}")
    
    def _trigger_block(self, event: SecurityEvent):
        """IP 차단 트리거"""
        block_data = {
            'ip_address': event.source_ip,
            'reason': event.description,
            'threat_level': event.threat_level,
            'risk_score': event.risk_score,
            'duration_hours': self.config['auto_block_duration_hours']
        }
        
        for callback in self.block_callbacks:
            try:
                callback(block_data)
            except Exception as e:
                logger.error(f"차단 콜백 실행 실패: {e}")
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def add_block_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """차단 콜백 추가"""
        self.block_callbacks.append(callback)
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("보안 모니터링이 시작되었습니다.")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("보안 모니터링이 중지되었습니다.")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # IP 평판 정리 (오래된 데이터)
                self._cleanup_old_reputations()
                
                # 통계 업데이트
                self._update_statistics()
                
                time.sleep(60)  # 1분마다 실행
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(10)
    
    def _cleanup_old_reputations(self):
        """오래된 IP 평판 정리"""
        try:
            cutoff_time = datetime.now() - timedelta(days=self.config['reputation_decay_days'])
            
            ips_to_remove = []
            for ip, reputation in self.ip_reputations.items():
                if datetime.fromisoformat(reputation.last_seen) < cutoff_time:
                    ips_to_remove.append(ip)
            
            for ip in ips_to_remove:
                del self.ip_reputations[ip]
            
            if ips_to_remove:
                logger.info(f"오래된 IP 평판 {len(ips_to_remove)}개 정리됨")
                
        except Exception as e:
            logger.error(f"IP 평판 정리 실패: {e}")
    
    def _update_statistics(self):
        """통계 업데이트"""
        try:
            # 고유 IP 수 업데이트
            self.stats['unique_ips'] = set(self.ip_reputations.keys())
            
        except Exception as e:
            logger.error(f"통계 업데이트 실패: {e}")
    
    def get_security_statistics(self, days: int = 7) -> Dict[str, Any]:
        """보안 통계 조회"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            stats = {}
            
            # 총 이벤트 수
            cursor.execute("SELECT COUNT(*) FROM security_events WHERE timestamp >= ?", (start_date,))
            stats['total_events'] = cursor.fetchone()[0]
            
            # 위협 레벨별 통계
            cursor.execute("""
                SELECT threat_level, COUNT(*) FROM security_events 
                WHERE timestamp >= ? GROUP BY threat_level
            """, (start_date,))
            stats['by_threat_level'] = dict(cursor.fetchall())
            
            # 공격 타입별 통계
            cursor.execute("""
                SELECT attack_type, COUNT(*) FROM security_events 
                WHERE timestamp >= ? AND attack_type IS NOT NULL GROUP BY attack_type
            """, (start_date,))
            stats['by_attack_type'] = dict(cursor.fetchall())
            
            # 차단된 이벤트 수
            cursor.execute("SELECT COUNT(*) FROM security_events WHERE timestamp >= ? AND is_blocked = 1", (start_date,))
            stats['blocked_events'] = cursor.fetchone()[0]
            
            # IP별 통계
            cursor.execute("""
                SELECT source_ip, COUNT(*) FROM security_events 
                WHERE timestamp >= ? GROUP BY source_ip 
                ORDER BY COUNT(*) DESC LIMIT 10
            """, (start_date,))
            stats['top_ips'] = dict(cursor.fetchall())
            
            conn.close()
            
            # 실시간 통계 추가
            stats['current_stats'] = self.stats.copy()
            stats['current_stats']['unique_ips'] = len(self.stats['unique_ips'])
            
            return stats
            
        except Exception as e:
            logger.error(f"보안 통계 조회 실패: {e}")
            return {}
    
    def block_ip(self, ip_address: str, reason: str, duration_hours: int = 24) -> bool:
        """IP 수동 차단"""
        try:
            self.config['blacklist_ips'].append(ip_address)
            
            # IP 평판 업데이트
            if ip_address in self.ip_reputations:
                self.ip_reputations[ip_address].is_blacklisted = True
                self.ip_reputations[ip_address].reputation_score = 1.0
                self._save_ip_reputation(self.ip_reputations[ip_address])
            
            logger.info(f"IP 차단 완료: {ip_address} (사유: {reason})")
            return True
            
        except Exception as e:
            logger.error(f"IP 차단 실패: {e}")
            return False
    
    def whitelist_ip(self, ip_address: str, reason: str) -> bool:
        """IP 화이트리스트 추가"""
        try:
            if ip_address not in self.config['whitelist_ips']:
                self.config['whitelist_ips'].append(ip_address)
            
            # IP 평판 업데이트
            if ip_address in self.ip_reputations:
                self.ip_reputations[ip_address].is_whitelisted = True
                self.ip_reputations[ip_address].reputation_score = 0.0
                self._save_ip_reputation(self.ip_reputations[ip_address])
            
            logger.info(f"IP 화이트리스트 추가 완료: {ip_address} (사유: {reason})")
            return True
            
        except Exception as e:
            logger.error(f"IP 화이트리스트 추가 실패: {e}")
            return False

# 전역 침입 탐지 시스템 인스턴스
ids_system = IntrusionDetectionSystem() 