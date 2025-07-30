"""
🔒 고급 보안 모니터링 시스템

실시간 보안 위협 탐지 및 대응을 위한 고급 보안 모니터링 시스템입니다.
"""

import asyncio
import logging
import json
import time
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import sqlite3
import redis
from pathlib import Path
from collections import defaultdict, deque

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """보안 이벤트 데이터 클래스"""
    timestamp: datetime
    event_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    source_ip: str
    user_agent: str
    request_path: str
    request_method: str
    payload: Optional[str] = None
    threat_score: float = 0.0
    description: str = ""
    mitigation: str = ""

@dataclass
class SecurityAlert:
    """보안 알림 데이터"""
    timestamp: datetime
    alert_type: str
    severity: str
    title: str
    description: str
    affected_assets: List[str]
    recommended_actions: List[str]
    threat_score: float
    status: str = "open"  # 'open', 'investigating', 'resolved'

class AdvancedSecurityMonitor:
    """고급 보안 모니터링 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        
        # 보안 데이터 저장소
        self.db_path = Path(config.get('db_path', 'security_data.db'))
        self.init_database()
        
        # 모니터링 상태
        self.is_monitoring = False
        self.security_events: deque = deque(maxlen=10000)
        self.security_alerts: List[SecurityAlert] = []
        
        # 위협 탐지 규칙
        self.threat_rules = self.load_threat_rules()
        
        # IP 화이트리스트/블랙리스트
        self.ip_whitelist = set(config.get('ip_whitelist', []))
        self.ip_blacklist = set(config.get('ip_blacklist', []))
        
        # 위협 점수 임계값
        self.threat_thresholds = {
            'low': 10,
            'medium': 30,
            'high': 60,
            'critical': 90
        }
        
        # 이상 탐지 모델
        self.anomaly_detector = AnomalyDetector()
        
    def init_database(self):
        """SQLite 데이터베이스 초기화"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 보안 이벤트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                user_agent TEXT,
                request_path TEXT,
                request_method TEXT,
                payload TEXT,
                threat_score REAL,
                description TEXT,
                mitigation TEXT
            )
        ''')
        
        # 보안 알림 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                affected_assets TEXT,
                recommended_actions TEXT,
                threat_score REAL,
                status TEXT DEFAULT 'open'
            )
        ''')
        
        # IP 평판 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_reputation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE NOT NULL,
                reputation_score REAL,
                threat_count INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_source_ip ON security_events(source_ip)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON security_alerts(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON security_alerts(status)')
        
        conn.commit()
        conn.close()
        
    def load_threat_rules(self) -> Dict[str, Any]:
        """위협 탐지 규칙 로드"""
        rules = {
            'sql_injection': {
                'patterns': [
                    r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\bfrom\b)",
                    r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\bwhere\b)",
                    r"(--|#|/\*|\*/)",
                    r"(\b(exec|execute|sp_|xp_)\b)",
                ],
                'score': 80,
                'description': "SQL Injection 시도 탐지"
            },
            'xss_attack': {
                'patterns': [
                    r"(<script[^>]*>.*?</script>)",
                    r"(javascript:.*)",
                    r"(on\w+\s*=)",
                    r"(<iframe[^>]*>)",
                ],
                'score': 70,
                'description': "Cross-Site Scripting (XSS) 공격 탐지"
            },
            'path_traversal': {
                'patterns': [
                    r"(\.\./|\.\.\\)",
                    r"(%2e%2e%2f|%2e%2e%5c)",
                ],
                'score': 60,
                'description': "Path Traversal 공격 탐지"
            },
            'command_injection': {
                'patterns': [
                    r"(\b(cmd|command|exec|system|shell)\b)",
                    r"(\||&|;|`|\$\(|\$\{)",
                ],
                'score': 75,
                'description': "Command Injection 공격 탐지"
            },
            'brute_force': {
                'patterns': [
                    r"(login|auth|signin)",
                ],
                'score': 40,
                'description': "Brute Force 공격 탐지"
            }
        }
        return rules
        
    async def start_monitoring(self):
        """보안 모니터링 시작"""
        if self.is_monitoring:
            logger.warning("보안 모니터링이 이미 실행 중입니다.")
            return
            
        self.is_monitoring = True
        logger.info("고급 보안 모니터링을 시작합니다.")
        
        # 주기적 업데이트 작업 시작
        asyncio.create_task(self.periodic_anomaly_detection())
        
    async def stop_monitoring(self):
        """보안 모니터링 중지"""
        self.is_monitoring = False
        logger.info("고급 보안 모니터링을 중지합니다.")
        
    async def analyze_request(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """요청 분석 및 보안 이벤트 생성"""
        try:
            source_ip = request_data.get('source_ip', '')
            user_agent = request_data.get('user_agent', '')
            request_path = request_data.get('request_path', '')
            request_method = request_data.get('request_method', '')
            payload = request_data.get('payload', '')
            
            # 기본 위협 점수 계산
            threat_score = 0.0
            detected_threats = []
            
            # 1. IP 평판 확인
            ip_score = await self.check_ip_reputation(source_ip)
            threat_score += ip_score
            
            # 2. 패턴 기반 위협 탐지
            pattern_threats = self.detect_pattern_threats(payload, request_path, user_agent)
            for threat in pattern_threats:
                threat_score += threat['score']
                detected_threats.append(threat['description'])
                
            # 3. 이상 탐지
            anomaly_score = self.anomaly_detector.detect_anomaly(request_data)
            threat_score += anomaly_score
            
            # 4. 사용자 에이전트 분석
            ua_score = self.analyze_user_agent(user_agent)
            threat_score += ua_score
            
            # 위협 점수에 따른 심각도 결정
            severity = self.determine_severity(threat_score)
            
            # 보안 이벤트 생성
            if threat_score > 0:
                event = SecurityEvent(
                    timestamp=datetime.now(),
                    event_type='threat_detected',
                    severity=severity,
                    source_ip=source_ip,
                    user_agent=user_agent,
                    request_path=request_path,
                    request_method=request_method,
                    payload=payload,
                    threat_score=threat_score,
                    description="; ".join(detected_threats),
                    mitigation=self.generate_mitigation(severity, detected_threats)
                )
                
                # 이벤트 저장
                await self.save_security_event(event)
                
                # 높은 위협 점수인 경우 알림 생성
                if threat_score >= self.threat_thresholds['high']:
                    await self.create_security_alert(event)
                    
                return event
                
        except Exception as e:
            logger.error(f"요청 분석 중 오류: {e}")
            
        return None
        
    async def check_ip_reputation(self, ip_address: str) -> float:
        """IP 평판 확인"""
        try:
            # 캐시된 평판 확인
            cached_reputation = self.redis_client.get(f"ip_reputation:{ip_address}")
            if cached_reputation:
                return float(cached_reputation)
                
            # 데이터베이스에서 평판 확인
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT reputation_score, threat_count FROM ip_reputation 
                WHERE ip_address = ?
            ''', (ip_address,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                reputation_score = row[0] or 0
                threat_count = row[1] or 0
                
                # 위협 횟수에 따른 점수 조정
                if threat_count > 10:
                    reputation_score += 30
                elif threat_count > 5:
                    reputation_score += 15
                    
                # 캐시에 저장
                self.redis_client.setex(f"ip_reputation:{ip_address}", 3600, str(reputation_score))
                return reputation_score
                
        except Exception as e:
            logger.error(f"IP 평판 확인 중 오류: {e}")
            
        return 0.0
        
    def detect_pattern_threats(self, payload: str, request_path: str, user_agent: str) -> List[Dict[str, Any]]:
        """패턴 기반 위협 탐지"""
        threats = []
        
        # 모든 텍스트를 하나로 결합
        text_to_analyze = f"{payload} {request_path} {user_agent}".lower()
        
        for rule_name, rule in self.threat_rules.items():
            for pattern in rule['patterns']:
                if re.search(pattern, text_to_analyze, re.IGNORECASE):
                    threats.append({
                        'rule': rule_name,
                        'score': rule['score'],
                        'description': rule['description']
                    })
                    break  # 한 규칙당 하나의 매치만
                    
        return threats
        
    def analyze_user_agent(self, user_agent: str) -> float:
        """사용자 에이전트 분석"""
        score = 0.0
        
        if not user_agent:
            return 10.0  # User-Agent가 없는 경우 의심
            
        user_agent_lower = user_agent.lower()
        
        # 의심스러운 User-Agent 패턴
        suspicious_patterns = [
            'sqlmap', 'nikto', 'nmap', 'scanner', 'bot', 'crawler',
            'spider', 'curl', 'wget', 'python-requests', 'go-http-client'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in user_agent_lower:
                score += 20
                
        # 비정상적으로 긴 User-Agent
        if len(user_agent) > 500:
            score += 15
            
        return score
        
    def determine_severity(self, threat_score: float) -> str:
        """위협 점수에 따른 심각도 결정"""
        if threat_score >= self.threat_thresholds['critical']:
            return 'critical'
        elif threat_score >= self.threat_thresholds['high']:
            return 'high'
        elif threat_score >= self.threat_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
            
    def generate_mitigation(self, severity: str, threats: List[str]) -> str:
        """위협 완화 방안 생성"""
        mitigations = {
            'critical': [
                "즉시 IP 차단",
                "관리자에게 긴급 알림",
                "시스템 로그 상세 분석"
            ],
            'high': [
                "IP 임시 차단 (24시간)",
                "요청 속도 제한",
                "추가 모니터링 활성화"
            ],
            'medium': [
                "요청 속도 제한",
                "추가 인증 요구",
                "모니터링 강화"
            ],
            'low': [
                "로그 기록",
                "추가 관찰"
            ]
        }
        
        return "; ".join(mitigations.get(severity, ["로그 기록"]))
        
    async def save_security_event(self, event: SecurityEvent):
        """보안 이벤트 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events 
                (timestamp, event_type, severity, source_ip, user_agent, 
                 request_path, request_method, payload, threat_score, 
                 description, mitigation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.timestamp.isoformat(),
                event.event_type,
                event.severity,
                event.source_ip,
                event.user_agent,
                event.request_path,
                event.request_method,
                event.payload,
                event.threat_score,
                event.description,
                event.mitigation
            ))
            
            conn.commit()
            conn.close()
            
            # 메모리 캐시에 추가
            self.security_events.append(event)
            
        except Exception as e:
            logger.error(f"보안 이벤트 저장 중 오류: {e}")
            
    async def create_security_alert(self, event: SecurityEvent):
        """보안 알림 생성"""
        try:
            alert = SecurityAlert(
                timestamp=datetime.now(),
                alert_type='threat_detected',
                severity=event.severity,
                title=f"보안 위협 탐지: {event.severity.upper()}",
                description=f"IP {event.source_ip}에서 {event.description}",
                affected_assets=[event.request_path],
                recommended_actions=event.mitigation.split("; "),
                threat_score=event.threat_score
            )
            
            # 알림 저장
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_alerts 
                (timestamp, alert_type, severity, title, description, 
                 affected_assets, recommended_actions, threat_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.timestamp.isoformat(),
                alert.alert_type,
                alert.severity,
                alert.title,
                alert.description,
                json.dumps(alert.affected_assets),
                json.dumps(alert.recommended_actions),
                alert.threat_score,
                alert.status
            ))
            
            conn.commit()
            conn.close()
            
            # 알림 목록에 추가
            self.security_alerts.append(alert)
            
            # Redis에 실시간 알림 저장
            alert_data = {
                'timestamp': alert.timestamp.isoformat(),
                'type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'description': alert.description,
                'threat_score': alert.threat_score
            }
            
            self.redis_client.lpush('security_alerts:recent', json.dumps(alert_data))
            self.redis_client.ltrim('security_alerts:recent', 0, 99)
            
            logger.warning(f"보안 알림 생성: {alert.title}")
            
        except Exception as e:
            logger.error(f"보안 알림 생성 중 오류: {e}")
            
    async def periodic_anomaly_detection(self):
        """주기적 이상 탐지"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(300)  # 5분마다 실행
                await self.detect_anomalies()
            except Exception as e:
                logger.error(f"주기적 이상 탐지 중 오류: {e}")
                
    async def detect_anomalies(self):
        """이상 탐지 실행"""
        try:
            # 최근 이벤트 분석
            recent_events = list(self.security_events)[-100:]  # 최근 100개 이벤트
            
            if len(recent_events) < 10:
                return
                
            # IP별 요청 빈도 분석
            ip_frequency = defaultdict(int)
            for event in recent_events:
                ip_frequency[event.source_ip] += 1
                
            # 비정상적으로 높은 요청 빈도 탐지
            for ip, count in ip_frequency.items():
                if count > 50:  # 5분 내 50회 이상 요청
                    await self.create_rate_limit_alert(ip, count)
                    
        except Exception as e:
            logger.error(f"이상 탐지 중 오류: {e}")
            
    async def create_rate_limit_alert(self, ip: str, count: int):
        """속도 제한 알림 생성"""
        alert = SecurityAlert(
            timestamp=datetime.now(),
            alert_type='rate_limit_exceeded',
            severity='high',
            title=f"속도 제한 초과: {ip}",
            description=f"IP {ip}에서 5분 내 {count}회 요청 감지",
            affected_assets=['전체 시스템'],
            recommended_actions=[
                "IP 임시 차단 (30분)",
                "요청 속도 제한 강화",
                "추가 모니터링 활성화"
            ],
            threat_score=50.0
        )
        
        await self.create_security_alert_from_alert(alert)
        
    async def create_security_alert_from_alert(self, alert: SecurityAlert):
        """SecurityAlert 객체로부터 알림 생성"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_alerts 
                (timestamp, alert_type, severity, title, description, 
                 affected_assets, recommended_actions, threat_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.timestamp.isoformat(),
                alert.alert_type,
                alert.severity,
                alert.title,
                alert.description,
                json.dumps(alert.affected_assets),
                json.dumps(alert.recommended_actions),
                alert.threat_score,
                alert.status
            ))
            
            conn.commit()
            conn.close()
            
            self.security_alerts.append(alert)
            
        except Exception as e:
            logger.error(f"보안 알림 생성 중 오류: {e}")
            
    async def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """보안 요약 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 시간 범위 계산
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 이벤트 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_events,
                    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_events,
                    COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_events,
                    COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_events,
                    AVG(threat_score) as avg_threat_score,
                    MAX(threat_score) as max_threat_score
                FROM security_events
                WHERE timestamp BETWEEN ? AND ?
            ''', (start_time.isoformat(), end_time.isoformat()))
            
            event_stats = cursor.fetchone()
            
            # 알림 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_alerts,
                    COUNT(CASE WHEN status = 'open' THEN 1 END) as open_alerts,
                    COUNT(CASE WHEN status = 'investigating' THEN 1 END) as investigating_alerts,
                    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_alerts
                FROM security_alerts
                WHERE timestamp BETWEEN ? AND ?
            ''', (start_time.isoformat(), end_time.isoformat()))
            
            alert_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'period_hours': hours,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'events': {
                    'total': event_stats[0] if event_stats else 0,
                    'critical': event_stats[1] if event_stats else 0,
                    'high': event_stats[2] if event_stats else 0,
                    'medium': event_stats[3] if event_stats else 0,
                    'low': event_stats[4] if event_stats else 0,
                    'avg_threat_score': round(event_stats[5], 2) if event_stats and event_stats[5] else 0,
                    'max_threat_score': round(event_stats[6], 2) if event_stats and event_stats[6] else 0
                },
                'alerts': {
                    'total': alert_stats[0] if alert_stats else 0,
                    'open': alert_stats[1] if alert_stats else 0,
                    'investigating': alert_stats[2] if alert_stats else 0,
                    'resolved': alert_stats[3] if alert_stats else 0
                }
            }
            
        except Exception as e:
            logger.error(f"보안 요약 조회 중 오류: {e}")
            return {}

class AnomalyDetector:
    """이상 탐지 클래스"""
    
    def __init__(self):
        self.request_patterns = defaultdict(int)
        self.ip_patterns = defaultdict(int)
        
    def detect_anomaly(self, request_data: Dict[str, Any]) -> float:
        """이상 탐지"""
        score = 0.0
        
        # 요청 패턴 분석
        request_key = f"{request_data.get('request_method', '')}:{request_data.get('request_path', '')}"
        self.request_patterns[request_key] += 1
        
        # IP 패턴 분석
        source_ip = request_data.get('source_ip', '')
        self.ip_patterns[source_ip] += 1
        
        # 비정상적인 요청 빈도 탐지
        if self.request_patterns[request_key] > 100:  # 같은 요청이 100회 이상
            score += 20
            
        if self.ip_patterns[source_ip] > 50:  # 같은 IP에서 50회 이상
            score += 30
            
        return score

# 보안 모니터링 인스턴스
security_monitor = None

async def start_security_monitoring(config: Dict[str, Any]):
    """보안 모니터링 시작"""
    global security_monitor
    
    if security_monitor is None:
        security_monitor = AdvancedSecurityMonitor(config)
        
    await security_monitor.start_monitoring()

async def stop_security_monitoring():
    """보안 모니터링 중지"""
    global security_monitor
    
    if security_monitor:
        await security_monitor.stop_monitoring()

def get_security_monitor() -> Optional[AdvancedSecurityMonitor]:
    """보안 모니터링 인스턴스 반환"""
    return security_monitor 