"""
고급 보안 모니터링 시스템

실시간 보안 위협 탐지 및 대응:
- 침입 시도 감지
- 이상 행동 탐지  
- 보안 이벤트 로깅
- 실시간 알림
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re
import hashlib
from collections import defaultdict, deque
import redis
import aiohttp
from prometheus_client import Counter, Gauge, Histogram
import logging
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 데이터베이스 설정
Base = declarative_base()
engine = create_engine('sqlite:///security_monitoring.db')
Session = sessionmaker(bind=engine)

# Prometheus 메트릭스
security_events_counter = Counter('security_events_total', 'Total security events', ['event_type', 'severity'])
active_threats_gauge = Gauge('active_threats', 'Number of active threats')
threat_detection_time = Histogram('threat_detection_seconds', 'Time to detect threats')
false_positive_rate = Gauge('security_false_positive_rate', 'False positive rate')

# Redis 연결
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@dataclass
class SecurityEvent:
    """보안 이벤트 데이터 클래스"""
    event_id: str
    event_type: str
    severity: str  # critical, high, medium, low
    source_ip: str
    target: str
    description: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class ThreatPattern:
    """위협 패턴 데이터 클래스"""
    pattern_id: str
    pattern_type: str
    pattern: str
    severity: str
    action: str  # block, alert, monitor
    enabled: bool = True

class SecurityEventDB(Base):
    """보안 이벤트 데이터베이스 모델"""
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(String(50), unique=True)
    event_type = Column(String(50))
    severity = Column(String(20))
    source_ip = Column(String(50))
    target = Column(String(100))
    description = Column(Text)
    timestamp = Column(DateTime)
    metadata = Column(Text)
    
class ThreatIntelligenceDB(Base):
    """위협 인텔리전스 데이터베이스 모델"""
    __tablename__ = 'threat_intelligence'
    
    id = Column(Integer, primary_key=True)
    threat_id = Column(String(50), unique=True)
    threat_type = Column(String(50))
    indicators = Column(Text)
    severity = Column(String(20))
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    confidence = Column(Float)

class AdvancedSecurityMonitor:
    """고급 보안 모니터링 시스템"""
    
    def __init__(self):
        self.session = Session()
        self.threat_patterns = self._load_threat_patterns()
        self.ip_reputation_cache = {}
        self.behavior_baselines = defaultdict(lambda: deque(maxlen=1000))
        self.active_sessions = {}
        self.blocked_ips = set()
        
        # 이상 탐지 설정
        self.anomaly_threshold = 3.0  # 표준편차
        self.rate_limit_threshold = 100  # 분당 요청 수
        
        # 패턴 매칭 설정
        self.sql_injection_patterns = [
            r"(?i)union.*select",
            r"(?i)select.*from.*where",
            r"(?i)drop\s+table",
            r"(?i)insert\s+into",
            r"(?i)update.*set",
            r"(?i)delete\s+from"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>"
        ]
        
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\\/",
            r"%2e%2e",
            r"\.\.%2f",
            r"\.\.%5c"
        ]
        
        # 데이터베이스 테이블 생성
        Base.metadata.create_all(engine)
        
    def _load_threat_patterns(self) -> List[ThreatPattern]:
        """위협 패턴 로드"""
        patterns = [
            ThreatPattern(
                pattern_id="SQL_INJ_001",
                pattern_type="sql_injection",
                pattern=r"(?i)union.*select",
                severity="high",
                action="block"
            ),
            ThreatPattern(
                pattern_id="XSS_001",
                pattern_type="xss",
                pattern=r"<script[^>]*>",
                severity="high",
                action="block"
            ),
            ThreatPattern(
                pattern_id="PATH_TRAV_001",
                pattern_type="path_traversal",
                pattern=r"\.\./",
                severity="medium",
                action="alert"
            ),
            ThreatPattern(
                pattern_id="BRUTE_FORCE_001",
                pattern_type="brute_force",
                pattern="multiple_failed_logins",
                severity="high",
                action="block"
            )
        ]
        return patterns
        
    async def monitor_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP 요청 모니터링"""
        try:
            # 요청 데이터 추출
            source_ip = request_data.get('source_ip', '')
            path = request_data.get('path', '')
            method = request_data.get('method', '')
            headers = request_data.get('headers', {})
            body = request_data.get('body', '')
            
            # IP 차단 확인
            if source_ip in self.blocked_ips:
                return {
                    'action': 'block',
                    'reason': 'IP blocked',
                    'severity': 'high'
                }
            
            # 속도 제한 확인
            rate_limit_check = await self._check_rate_limit(source_ip)
            if not rate_limit_check['allowed']:
                await self._create_security_event(
                    event_type='rate_limit_exceeded',
                    severity='medium',
                    source_ip=source_ip,
                    target=path,
                    description=f"Rate limit exceeded: {rate_limit_check['rate']} requests/min"
                )
                return {
                    'action': 'rate_limit',
                    'reason': 'Rate limit exceeded',
                    'severity': 'medium'
                }
            
            # 패턴 기반 탐지
            threats = await self._detect_patterns(path, headers, body)
            if threats:
                highest_severity = max(threats, key=lambda x: self._severity_score(x['severity']))
                await self._create_security_event(
                    event_type=highest_severity['type'],
                    severity=highest_severity['severity'],
                    source_ip=source_ip,
                    target=path,
                    description=highest_severity['description']
                )
                
                if highest_severity['severity'] in ['critical', 'high']:
                    self.blocked_ips.add(source_ip)
                    return {
                        'action': 'block',
                        'reason': highest_severity['description'],
                        'severity': highest_severity['severity']
                    }
            
            # 이상 행동 탐지
            anomaly = await self._detect_anomaly(source_ip, request_data)
            if anomaly['is_anomaly']:
                await self._create_security_event(
                    event_type='anomaly_detected',
                    severity='medium',
                    source_ip=source_ip,
                    target=path,
                    description=anomaly['description']
                )
            
            return {
                'action': 'allow',
                'monitored': True,
                'threats': threats,
                'anomaly': anomaly
            }
            
        except Exception as e:
            logger.error(f"Error monitoring request: {str(e)}")
            return {'action': 'allow', 'error': str(e)}
    
    async def _check_rate_limit(self, source_ip: str) -> Dict[str, Any]:
        """속도 제한 확인"""
        key = f"rate_limit:{source_ip}"
        current_time = datetime.now()
        
        # Redis에서 요청 횟수 확인
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # 1분 만료
        results = pipe.execute()
        
        request_count = results[0]
        
        if request_count > self.rate_limit_threshold:
            return {
                'allowed': False,
                'rate': request_count,
                'limit': self.rate_limit_threshold
            }
        
        return {
            'allowed': True,
            'rate': request_count,
            'limit': self.rate_limit_threshold
        }
    
    async def _detect_patterns(self, path: str, headers: Dict, body: str) -> List[Dict[str, Any]]:
        """패턴 기반 위협 탐지"""
        threats = []
        
        # URL과 body 결합하여 검사
        content = f"{path} {json.dumps(headers)} {body}"
        
        # SQL Injection 검사
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, content):
                threats.append({
                    'type': 'sql_injection',
                    'severity': 'high',
                    'pattern': pattern,
                    'description': 'SQL Injection attempt detected'
                })
                break
        
        # XSS 검사
        for pattern in self.xss_patterns:
            if re.search(pattern, content):
                threats.append({
                    'type': 'xss',
                    'severity': 'high',
                    'pattern': pattern,
                    'description': 'XSS attempt detected'
                })
                break
        
        # Path Traversal 검사
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, path):
                threats.append({
                    'type': 'path_traversal',
                    'severity': 'medium',
                    'pattern': pattern,
                    'description': 'Path traversal attempt detected'
                })
                break
        
        return threats
    
    async def _detect_anomaly(self, source_ip: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """이상 행동 탐지"""
        # 요청 특성 추출
        features = {
            'path_length': len(request_data.get('path', '')),
            'header_count': len(request_data.get('headers', {})),
            'body_length': len(request_data.get('body', '')),
            'method': request_data.get('method', 'GET')
        }
        
        # 베이스라인과 비교
        baseline_key = f"baseline:{source_ip}"
        baseline = self.behavior_baselines[baseline_key]
        
        # 베이스라인에 현재 특성 추가
        baseline.append(features)
        
        # 충분한 데이터가 있을 때만 이상 탐지
        if len(baseline) < 10:
            return {'is_anomaly': False, 'description': 'Insufficient data'}
        
        # 간단한 통계적 이상 탐지
        path_lengths = [f['path_length'] for f in baseline]
        avg_path_length = sum(path_lengths) / len(path_lengths)
        std_path_length = (sum((x - avg_path_length) ** 2 for x in path_lengths) / len(path_lengths)) ** 0.5
        
        if std_path_length > 0:
            z_score = abs(features['path_length'] - avg_path_length) / std_path_length
            if z_score > self.anomaly_threshold:
                return {
                    'is_anomaly': True,
                    'description': f'Unusual path length detected (z-score: {z_score:.2f})',
                    'z_score': z_score
                }
        
        return {'is_anomaly': False, 'description': 'Normal behavior'}
    
    async def _create_security_event(self, event_type: str, severity: str, 
                                   source_ip: str, target: str, description: str) -> SecurityEvent:
        """보안 이벤트 생성"""
        event = SecurityEvent(
            event_id=hashlib.md5(f"{datetime.now().isoformat()}{source_ip}{target}".encode()).hexdigest()[:12],
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            target=target,
            description=description,
            timestamp=datetime.now()
        )
        
        # 데이터베이스에 저장
        db_event = SecurityEventDB(
            event_id=event.event_id,
            event_type=event.event_type,
            severity=event.severity,
            source_ip=event.source_ip,
            target=event.target,
            description=event.description,
            timestamp=event.timestamp,
            metadata=json.dumps(event.metadata)
        )
        
        try:
            self.session.add(db_event)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving security event: {str(e)}")
        
        # Prometheus 메트릭 업데이트
        security_events_counter.labels(event_type=event_type, severity=severity).inc()
        
        # Redis에 실시간 알림
        redis_client.publish('security_alerts', json.dumps({
            'event_id': event.event_id,
            'event_type': event.event_type,
            'severity': event.severity,
            'source_ip': event.source_ip,
            'description': event.description,
            'timestamp': event.timestamp.isoformat()
        }))
        
        return event
    
    def _severity_score(self, severity: str) -> int:
        """심각도 점수 반환"""
        scores = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return scores.get(severity, 0)
    
    async def monitor_authentication(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """인증 모니터링"""
        username = auth_data.get('username', '')
        source_ip = auth_data.get('source_ip', '')
        success = auth_data.get('success', False)
        
        # 실패한 로그인 시도 추적
        if not success:
            key = f"failed_login:{source_ip}:{username}"
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 300)  # 5분
            results = pipe.execute()
            
            failed_attempts = results[0]
            
            # 무차별 대입 공격 탐지
            if failed_attempts >= 5:
                await self._create_security_event(
                    event_type='brute_force',
                    severity='high',
                    source_ip=source_ip,
                    target=username,
                    description=f"Brute force attack detected: {failed_attempts} failed attempts"
                )
                
                # IP 차단
                self.blocked_ips.add(source_ip)
                
                return {
                    'action': 'block',
                    'reason': 'Brute force attack detected',
                    'failed_attempts': failed_attempts
                }
        else:
            # 성공 시 카운터 리셋
            key = f"failed_login:{source_ip}:{username}"
            redis_client.delete(key)
        
        return {'action': 'allow', 'monitored': True}
    
    async def get_threat_intelligence(self) -> List[Dict[str, Any]]:
        """위협 인텔리전스 조회"""
        try:
            threats = self.session.query(ThreatIntelligenceDB).all()
            return [{
                'threat_id': t.threat_id,
                'threat_type': t.threat_type,
                'indicators': json.loads(t.indicators),
                'severity': t.severity,
                'first_seen': t.first_seen.isoformat(),
                'last_seen': t.last_seen.isoformat(),
                'confidence': t.confidence
            } for t in threats]
        except Exception as e:
            logger.error(f"Error getting threat intelligence: {str(e)}")
            return []
    
    async def get_security_dashboard_data(self) -> Dict[str, Any]:
        """보안 대시보드 데이터 조회"""
        try:
            # 최근 24시간 이벤트
            since = datetime.now() - timedelta(hours=24)
            recent_events = self.session.query(SecurityEventDB).filter(
                SecurityEventDB.timestamp >= since
            ).all()
            
            # 이벤트 타입별 통계
            event_stats = defaultdict(int)
            severity_stats = defaultdict(int)
            
            for event in recent_events:
                event_stats[event.event_type] += 1
                severity_stats[event.severity] += 1
            
            # 차단된 IP 목록
            blocked_ips_list = list(self.blocked_ips)
            
            # 활성 위협 수
            active_threats_count = len([e for e in recent_events if e.severity in ['critical', 'high']])
            active_threats_gauge.set(active_threats_count)
            
            return {
                'total_events_24h': len(recent_events),
                'event_types': dict(event_stats),
                'severity_distribution': dict(severity_stats),
                'blocked_ips': blocked_ips_list[:10],  # 상위 10개
                'active_threats': active_threats_count,
                'recent_events': [{
                    'event_id': e.event_id,
                    'event_type': e.event_type,
                    'severity': e.severity,
                    'source_ip': e.source_ip,
                    'description': e.description,
                    'timestamp': e.timestamp.isoformat()
                } for e in recent_events[:20]]  # 최근 20개
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {}
    
    async def update_threat_intelligence(self, threat_data: Dict[str, Any]):
        """위협 인텔리전스 업데이트"""
        try:
            threat = ThreatIntelligenceDB(
                threat_id=threat_data['threat_id'],
                threat_type=threat_data['threat_type'],
                indicators=json.dumps(threat_data['indicators']),
                severity=threat_data['severity'],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                confidence=threat_data.get('confidence', 0.8)
            )
            
            self.session.merge(threat)
            self.session.commit()
            
            logger.info(f"Updated threat intelligence: {threat_data['threat_id']}")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating threat intelligence: {str(e)}")

# 싱글톤 인스턴스
_security_monitor = None

def get_security_monitor() -> AdvancedSecurityMonitor:
    """보안 모니터 인스턴스 반환"""
    global _security_monitor
    if _security_monitor is None:
        _security_monitor = AdvancedSecurityMonitor()
    return _security_monitor