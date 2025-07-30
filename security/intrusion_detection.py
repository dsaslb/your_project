"""
침입 탐지 및 방지 시스템 (IDS/IPS)
실시간 네트워크 모니터링, 패턴 분석, 위협 탐지 및 자동 대응을 포함한 완전한 보안 시스템
"""

import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import asyncio
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout
import sqlite3
from pathlib import Path
import pickle
import hashlib
import hmac
import base64
import secrets
import struct
import socket
import ssl
import redis
from redis.exceptions import RedisError
import re
import ipaddress
import scapy.all as scapy
from scapy.layers import http
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import yaml
import requests
from collections import defaultdict, deque

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """위협 수준"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """알림 타입"""
    INTRUSION_DETECTED = "intrusion_detected"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MALWARE_DETECTED = "malware_detected"
    DDoS_ATTACK = "ddos_attack"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    PORT_SCAN = "port_scan"
    ANOMALY_DETECTED = "anomaly_detected"

class ActionType(Enum):
    """대응 액션 타입"""
    BLOCK_IP = "block_ip"
    RATE_LIMIT = "rate_limit"
    ALERT = "alert"
    LOG = "log"
    QUARANTINE = "quarantine"
    TERMINATE_SESSION = "terminate_session"
    UPDATE_FIREWALL = "update_firewall"

@dataclass
class NetworkPacket:
    """네트워크 패킷"""
    packet_id: str
    timestamp: datetime
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    payload: bytes
    packet_size: int
    flags: Dict[str, bool]
    metadata: Dict[str, Any]

@dataclass
class SecurityAlert:
    """보안 알림"""
    alert_id: str
    alert_type: AlertType
    threat_level: ThreatLevel
    source_ip: str
    destination_ip: str
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime
    status: str
    assigned_to: str = None
    resolution_notes: str = None

@dataclass
class ThreatSignature:
    """위협 시그니처"""
    signature_id: str
    name: str
    description: str
    pattern: str
    regex_pattern: str
    threat_level: ThreatLevel
    category: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class SecurityRule:
    """보안 규칙"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[ActionType]
    priority: int
    enabled: bool
    created_at: datetime
    updated_at: datetime

class IntrusionDetectionSystem:
    """침입 탐지 및 방지 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.packets: deque = deque(maxlen=10000)
        self.alerts: Dict[str, SecurityAlert] = {}
        self.signatures: Dict[str, ThreatSignature] = {}
        self.rules: Dict[str, SecurityRule] = {}
        self.blocked_ips: set = set()
        self.suspicious_ips: Dict[str, Dict[str, Any]] = {}
        
        # Redis 클라이언트
        self.redis_client = None
        self._init_redis()
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './ids.db'))
        self._init_database()
        
        # 기본 시그니처 로드
        self._load_default_signatures()
        
        # 기본 규칙 로드
        self._load_default_rules()
        
        # 패킷 캡처 스레드
        self.capture_thread = None
        self.is_capturing = False
        
        # 분석 스레드
        self.analysis_thread = None
        self.is_analyzing = False
        
        # ML 모델
        self.anomaly_detector = None
        self.scaler = None
        self._init_ml_models()
        
        logger.info("침입 탐지 및 방지 시스템 초기화 완료")
    
    def _init_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 2),
                decode_responses=True
            )
            
            # Redis 연결 테스트
            self.redis_client.ping()
            logger.info("Redis 클라이언트 초기화 완료")
            
        except RedisError as e:
            logger.warning(f"Redis 클라이언트 초기화 실패: {e}")
            self.redis_client = None
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 보안 알림 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    alert_id TEXT PRIMARY KEY,
                    alert_type TEXT,
                    threat_level TEXT,
                    source_ip TEXT,
                    destination_ip TEXT,
                    description TEXT,
                    evidence TEXT,
                    timestamp TEXT,
                    status TEXT,
                    assigned_to TEXT,
                    resolution_notes TEXT
                )
            ''')
            
            # 위협 시그니처 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_signatures (
                    signature_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    pattern TEXT,
                    regex_pattern TEXT,
                    threat_level TEXT,
                    category TEXT,
                    enabled INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 보안 규칙 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    conditions TEXT,
                    actions TEXT,
                    priority INTEGER,
                    enabled INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 네트워크 패킷 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS network_packets (
                    packet_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    source_ip TEXT,
                    destination_ip TEXT,
                    source_port INTEGER,
                    destination_port INTEGER,
                    protocol TEXT,
                    packet_size INTEGER,
                    flags TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("IDS 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_default_signatures(self):
        """기본 시그니처 로드"""
        try:
            default_signatures = [
                {
                    'name': 'SQL Injection',
                    'description': 'SQL 인젝션 공격 탐지',
                    'pattern': 'UNION SELECT|DROP TABLE|INSERT INTO|DELETE FROM',
                    'regex_pattern': r'(?i)(UNION\s+SELECT|DROP\s+TABLE|INSERT\s+INTO|DELETE\s+FROM)',
                    'threat_level': ThreatLevel.HIGH,
                    'category': 'injection'
                },
                {
                    'name': 'XSS Attack',
                    'description': 'XSS 공격 탐지',
                    'pattern': '<script>|javascript:|onload=|onerror=',
                    'regex_pattern': r'(?i)(<script>|javascript:|onload=|onerror=)',
                    'threat_level': ThreatLevel.MEDIUM,
                    'category': 'xss'
                },
                {
                    'name': 'Brute Force',
                    'description': '무차별 대입 공격 탐지',
                    'pattern': 'multiple_failed_logins',
                    'regex_pattern': r'multiple_failed_logins',
                    'threat_level': ThreatLevel.HIGH,
                    'category': 'brute_force'
                },
                {
                    'name': 'Port Scan',
                    'description': '포트 스캔 탐지',
                    'pattern': 'multiple_port_attempts',
                    'regex_pattern': r'multiple_port_attempts',
                    'threat_level': ThreatLevel.MEDIUM,
                    'category': 'reconnaissance'
                },
                {
                    'name': 'DDoS Attack',
                    'description': 'DDoS 공격 탐지',
                    'pattern': 'high_traffic_volume',
                    'regex_pattern': r'high_traffic_volume',
                    'threat_level': ThreatLevel.CRITICAL,
                    'category': 'ddos'
                }
            ]
            
            for sig_info in default_signatures:
                self.create_signature(sig_info)
            
            logger.info(f"{len(default_signatures)}개 기본 시그니처 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 시그니처 로드 오류: {e}")
    
    def _load_default_rules(self):
        """기본 규칙 로드"""
        try:
            default_rules = [
                {
                    'name': 'Block SQL Injection',
                    'description': 'SQL 인젝션 공격 차단',
                    'conditions': {
                        'signature_match': 'SQL Injection',
                        'threat_level': 'high'
                    },
                    'actions': [ActionType.BLOCK_IP, ActionType.ALERT],
                    'priority': 100
                },
                {
                    'name': 'Rate Limit Brute Force',
                    'description': '무차별 대입 공격 속도 제한',
                    'conditions': {
                        'signature_match': 'Brute Force',
                        'attempts_threshold': 5
                    },
                    'actions': [ActionType.RATE_LIMIT, ActionType.ALERT],
                    'priority': 80
                },
                {
                    'name': 'Block DDoS',
                    'description': 'DDoS 공격 차단',
                    'conditions': {
                        'signature_match': 'DDoS Attack',
                        'traffic_threshold': 1000
                    },
                    'actions': [ActionType.BLOCK_IP, ActionType.UPDATE_FIREWALL],
                    'priority': 90
                }
            ]
            
            for rule_info in default_rules:
                self.create_rule(rule_info)
            
            logger.info(f"{len(default_rules)}개 기본 규칙 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 규칙 로드 오류: {e}")
    
    def _init_ml_models(self):
        """ML 모델 초기화"""
        try:
            # 이상 탐지 모델
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # 스케일러
            self.scaler = StandardScaler()
            
            logger.info("ML 모델 초기화 완료")
            
        except Exception as e:
            logger.error(f"ML 모델 초기화 오류: {e}")
    
    def create_signature(self, signature_info: Dict[str, Any]) -> str:
        """시그니처 생성"""
        try:
            signature_id = str(uuid.uuid4())
            
            signature = ThreatSignature(
                signature_id=signature_id,
                name=signature_info['name'],
                description=signature_info['description'],
                pattern=signature_info['pattern'],
                regex_pattern=signature_info['regex_pattern'],
                threat_level=ThreatLevel(signature_info['threat_level']),
                category=signature_info['category'],
                enabled=signature_info.get('enabled', True),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.signatures[signature_id] = signature
            
            # 데이터베이스에 저장
            self._save_signature_to_db(signature)
            
            logger.info(f"시그니처 생성 완료: {signature_id}")
            return signature_id
            
        except Exception as e:
            logger.error(f"시그니처 생성 오류: {e}")
            raise
    
    def create_rule(self, rule_info: Dict[str, Any]) -> str:
        """보안 규칙 생성"""
        try:
            rule_id = str(uuid.uuid4())
            
            rule = SecurityRule(
                rule_id=rule_id,
                name=rule_info['name'],
                description=rule_info['description'],
                conditions=rule_info['conditions'],
                actions=[ActionType(action) for action in rule_info['actions']],
                priority=rule_info.get('priority', 50),
                enabled=rule_info.get('enabled', True),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.rules[rule_id] = rule
            
            # 데이터베이스에 저장
            self._save_rule_to_db(rule)
            
            logger.info(f"보안 규칙 생성 완료: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"보안 규칙 생성 오류: {e}")
            raise
    
    def start_packet_capture(self, interface: str = None):
        """패킷 캡처 시작"""
        try:
            if self.is_capturing:
                logger.warning("패킷 캡처가 이미 실행 중입니다")
                return
            
            self.is_capturing = True
            self.capture_thread = threading.Thread(
                target=self._packet_capture_loop,
                args=(interface,),
                daemon=True
            )
            self.capture_thread.start()
            
            logger.info("패킷 캡처 시작")
            
        except Exception as e:
            logger.error(f"패킷 캡처 시작 오류: {e}")
    
    def _packet_capture_loop(self, interface: str = None):
        """패킷 캡처 루프"""
        try:
            def packet_handler(packet):
                try:
                    # 패킷 정보 추출
                    packet_info = self._extract_packet_info(packet)
                    if packet_info:
                        self.packets.append(packet_info)
                        
                        # 실시간 분석
                        self._analyze_packet(packet_info)
                        
                except Exception as e:
                    logger.error(f"패킷 처리 오류: {e}")
            
            # 패킷 캡처 시작
            if interface:
                scapy.sniff(iface=interface, prn=packet_handler, store=0)
            else:
                scapy.sniff(prn=packet_handler, store=0)
                
        except Exception as e:
            logger.error(f"패킷 캡처 루프 오류: {e}")
        finally:
            self.is_capturing = False
    
    def _extract_packet_info(self, packet) -> Optional[NetworkPacket]:
        """패킷 정보 추출"""
        try:
            if packet.haslayer(scapy.IP):
                packet_id = str(uuid.uuid4())
                
                # IP 레이어 정보
                ip_layer = packet[scapy.IP]
                source_ip = ip_layer.src
                destination_ip = ip_layer.dst
                
                # TCP/UDP 레이어 정보
                source_port = 0
                destination_port = 0
                protocol = "unknown"
                
                if packet.haslayer(scapy.TCP):
                    tcp_layer = packet[scapy.TCP]
                    source_port = tcp_layer.sport
                    destination_port = tcp_layer.dport
                    protocol = "tcp"
                    flags = {
                        'syn': bool(tcp_layer.flags & 0x02),
                        'ack': bool(tcp_layer.flags & 0x10),
                        'fin': bool(tcp_layer.flags & 0x01),
                        'rst': bool(tcp_layer.flags & 0x04),
                        'psh': bool(tcp_layer.flags & 0x08),
                        'urg': bool(tcp_layer.flags & 0x20)
                    }
                elif packet.haslayer(scapy.UDP):
                    udp_layer = packet[scapy.UDP]
                    source_port = udp_layer.sport
                    destination_port = udp_layer.dport
                    protocol = "udp"
                    flags = {}
                
                # 페이로드 추출
                payload = bytes(packet[scapy.Raw].load) if packet.haslayer(scapy.Raw) else b''
                
                # 메타데이터
                metadata = {
                    'ttl': ip_layer.ttl,
                    'tos': ip_layer.tos,
                    'len': ip_layer.len,
                    'id': ip_layer.id
                }
                
                return NetworkPacket(
                    packet_id=packet_id,
                    timestamp=datetime.now(),
                    source_ip=source_ip,
                    destination_ip=destination_ip,
                    source_port=source_port,
                    destination_port=destination_port,
                    protocol=protocol,
                    payload=payload,
                    packet_size=len(packet),
                    flags=flags,
                    metadata=metadata
                )
            
            return None
            
        except Exception as e:
            logger.error(f"패킷 정보 추출 오류: {e}")
            return None
    
    def _analyze_packet(self, packet: NetworkPacket):
        """패킷 분석"""
        try:
            # 시그니처 기반 탐지
            self._signature_based_detection(packet)
            
            # 이상 탐지
            self._anomaly_detection(packet)
            
            # 규칙 기반 분석
            self._rule_based_analysis(packet)
            
        except Exception as e:
            logger.error(f"패킷 분석 오류: {e}")
    
    def _signature_based_detection(self, packet: NetworkPacket):
        """시그니처 기반 탐지"""
        try:
            payload_str = packet.payload.decode('utf-8', errors='ignore')
            
            for signature in self.signatures.values():
                if not signature.enabled:
                    continue
                
                # 정규식 패턴 매칭
                if re.search(signature.regex_pattern, payload_str, re.IGNORECASE):
                    self._create_alert(
                        alert_type=AlertType.INTRUSION_DETECTED,
                        threat_level=signature.threat_level,
                        source_ip=packet.source_ip,
                        destination_ip=packet.destination_ip,
                        description=f"{signature.name} 탐지됨",
                        evidence={
                            'signature_id': signature.signature_id,
                            'signature_name': signature.name,
                            'pattern_matched': signature.pattern,
                            'payload_sample': payload_str[:200]
                        }
                    )
                    
        except Exception as e:
            logger.error(f"시그니처 기반 탐지 오류: {e}")
    
    def _anomaly_detection(self, packet: NetworkPacket):
        """이상 탐지"""
        try:
            # 특성 벡터 생성
            features = [
                packet.packet_size,
                packet.source_port,
                packet.destination_port,
                len(packet.payload),
                packet.metadata.get('ttl', 64)
            ]
            
            # 스케일링
            features_scaled = self.scaler.transform([features])
            
            # 이상 탐지
            prediction = self.anomaly_detector.predict(features_scaled)
            
            if prediction[0] == -1:  # 이상 탐지
                self._create_alert(
                    alert_type=AlertType.ANOMALY_DETECTED,
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=packet.source_ip,
                    destination_ip=packet.destination_ip,
                    description="이상 패킷 탐지됨",
                    evidence={
                        'packet_size': packet.packet_size,
                        'source_port': packet.source_port,
                        'destination_port': packet.destination_port,
                        'payload_size': len(packet.payload),
                        'features': features
                    }
                )
                
        except Exception as e:
            logger.error(f"이상 탐지 오류: {e}")
    
    def _rule_based_analysis(self, packet: NetworkPacket):
        """규칙 기반 분석"""
        try:
            for rule in sorted(self.rules.values(), key=lambda x: x.priority, reverse=True):
                if not rule.enabled:
                    continue
                
                if self._evaluate_rule_conditions(rule, packet):
                    self._execute_rule_actions(rule, packet)
                    
        except Exception as e:
            logger.error(f"규칙 기반 분석 오류: {e}")
    
    def _evaluate_rule_conditions(self, rule: SecurityRule, packet: NetworkPacket) -> bool:
        """규칙 조건 평가"""
        try:
            conditions = rule.conditions
            
            # 시그니처 매칭 조건
            if 'signature_match' in conditions:
                signature_name = conditions['signature_match']
                for signature in self.signatures.values():
                    if signature.name == signature_name:
                        payload_str = packet.payload.decode('utf-8', errors='ignore')
                        if re.search(signature.regex_pattern, payload_str, re.IGNORECASE):
                            return True
                return False
            
            # 위협 수준 조건
            if 'threat_level' in conditions:
                # 실제로는 알림의 위협 수준을 확인해야 함
                pass
            
            # 시도 횟수 임계값
            if 'attempts_threshold' in conditions:
                threshold = conditions['attempts_threshold']
                attempts = self._get_attempts_count(packet.source_ip)
                return attempts >= threshold
            
            # 트래픽 임계값
            if 'traffic_threshold' in conditions:
                threshold = conditions['traffic_threshold']
                traffic = self._get_traffic_volume(packet.source_ip)
                return traffic >= threshold
            
            return False
            
        except Exception as e:
            logger.error(f"규칙 조건 평가 오류: {e}")
            return False
    
    def _execute_rule_actions(self, rule: SecurityRule, packet: NetworkPacket):
        """규칙 액션 실행"""
        try:
            for action in rule.actions:
                if action == ActionType.BLOCK_IP:
                    self._block_ip(packet.source_ip)
                elif action == ActionType.RATE_LIMIT:
                    self._rate_limit_ip(packet.source_ip)
                elif action == ActionType.ALERT:
                    self._create_alert(
                        alert_type=AlertType.INTRUSION_DETECTED,
                        threat_level=ThreatLevel.HIGH,
                        source_ip=packet.source_ip,
                        destination_ip=packet.destination_ip,
                        description=f"규칙 '{rule.name}' 트리거됨",
                        evidence={'rule_id': rule.rule_id, 'rule_name': rule.name}
                    )
                elif action == ActionType.LOG:
                    self._log_security_event(rule, packet)
                elif action == ActionType.UPDATE_FIREWALL:
                    self._update_firewall_rules(packet.source_ip)
                    
        except Exception as e:
            logger.error(f"규칙 액션 실행 오류: {e}")
    
    def _create_alert(self, alert_type: AlertType, threat_level: ThreatLevel,
                     source_ip: str, destination_ip: str, description: str, evidence: Dict[str, Any]):
        """보안 알림 생성"""
        try:
            alert_id = str(uuid.uuid4())
            
            alert = SecurityAlert(
                alert_id=alert_id,
                alert_type=alert_type,
                threat_level=threat_level,
                source_ip=source_ip,
                destination_ip=destination_ip,
                description=description,
                evidence=evidence,
                timestamp=datetime.now(),
                status='open'
            )
            
            self.alerts[alert_id] = alert
            
            # 데이터베이스에 저장
            self._save_alert_to_db(alert)
            
            # Redis에 알림 저장
            if self.redis_client:
                alert_key = f"alert:{alert_id}"
                self.redis_client.setex(
                    alert_key,
                    3600,  # 1시간 TTL
                    json.dumps(asdict(alert))
                )
            
            logger.warning(f"보안 알림 생성: {alert_id} - {description}")
            
        except Exception as e:
            logger.error(f"보안 알림 생성 오류: {e}")
    
    def _block_ip(self, ip_address: str):
        """IP 주소 차단"""
        try:
            self.blocked_ips.add(ip_address)
            
            # Redis에 차단된 IP 저장
            if self.redis_client:
                self.redis_client.sadd('blocked_ips', ip_address)
                self.redis_client.expire('blocked_ips', 3600)  # 1시간 TTL
            
            logger.info(f"IP 주소 차단: {ip_address}")
            
        except Exception as e:
            logger.error(f"IP 주소 차단 오류: {e}")
    
    def _rate_limit_ip(self, ip_address: str):
        """IP 주소 속도 제한"""
        try:
            if ip_address not in self.suspicious_ips:
                self.suspicious_ips[ip_address] = {
                    'first_seen': datetime.now(),
                    'attempts': 0,
                    'rate_limited': False
                }
            
            self.suspicious_ips[ip_address]['attempts'] += 1
            
            # 임계값 초과 시 속도 제한
            if self.suspicious_ips[ip_address]['attempts'] >= 10:
                self.suspicious_ips[ip_address]['rate_limited'] = True
                
                # Redis에 속도 제한된 IP 저장
                if self.redis_client:
                    self.redis_client.sadd('rate_limited_ips', ip_address)
                    self.redis_client.expire('rate_limited_ips', 1800)  # 30분 TTL
                
                logger.info(f"IP 주소 속도 제한: {ip_address}")
                
        except Exception as e:
            logger.error(f"IP 주소 속도 제한 오류: {e}")
    
    def _get_attempts_count(self, ip_address: str) -> int:
        """시도 횟수 조회"""
        try:
            if ip_address in self.suspicious_ips:
                return self.suspicious_ips[ip_address]['attempts']
            return 0
        except Exception as e:
            logger.error(f"시도 횟수 조회 오류: {e}")
            return 0
    
    def _get_traffic_volume(self, ip_address: str) -> int:
        """트래픽 볼륨 조회"""
        try:
            # 최근 1분간의 패킷 수 계산
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            count = sum(1 for packet in self.packets 
                       if packet.source_ip == ip_address and packet.timestamp > one_minute_ago)
            return count
        except Exception as e:
            logger.error(f"트래픽 볼륨 조회 오류: {e}")
            return 0
    
    def _log_security_event(self, rule: SecurityRule, packet: NetworkPacket):
        """보안 이벤트 로깅"""
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'source_ip': packet.source_ip,
                'destination_ip': packet.destination_ip,
                'action': 'logged'
            }
            
            logger.info(f"보안 이벤트 로깅: {event}")
            
        except Exception as e:
            logger.error(f"보안 이벤트 로깅 오류: {e}")
    
    def _update_firewall_rules(self, ip_address: str):
        """방화벽 규칙 업데이트"""
        try:
            # 실제로는 방화벽 API를 호출하여 규칙을 업데이트
            logger.info(f"방화벽 규칙 업데이트: {ip_address}")
            
        except Exception as e:
            logger.error(f"방화벽 규칙 업데이트 오류: {e}")
    
    def get_alerts(self, hours: int = 24) -> List[SecurityAlert]:
        """알림 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_alerts = [
                alert for alert in self.alerts.values()
                if alert.timestamp > cutoff_time
            ]
            return sorted(recent_alerts, key=lambda x: x.timestamp, reverse=True)
        except Exception as e:
            logger.error(f"알림 조회 오류: {e}")
            return []
    
    def get_blocked_ips(self) -> List[str]:
        """차단된 IP 목록 조회"""
        try:
            return list(self.blocked_ips)
        except Exception as e:
            logger.error(f"차단된 IP 목록 조회 오류: {e}")
            return []
    
    def get_suspicious_ips(self) -> Dict[str, Dict[str, Any]]:
        """의심스러운 IP 목록 조회"""
        try:
            return self.suspicious_ips.copy()
        except Exception as e:
            logger.error(f"의심스러운 IP 목록 조회 오류: {e}")
            return {}
    
    def _save_alert_to_db(self, alert: SecurityAlert):
        """알림을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_alerts 
                (alert_id, alert_type, threat_level, source_ip, destination_ip,
                 description, evidence, timestamp, status, assigned_to, resolution_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.alert_type.value,
                alert.threat_level.value,
                alert.source_ip,
                alert.destination_ip,
                alert.description,
                json.dumps(alert.evidence),
                alert.timestamp.isoformat(),
                alert.status,
                alert.assigned_to,
                alert.resolution_notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"알림 데이터베이스 저장 오류: {e}")
    
    def _save_signature_to_db(self, signature: ThreatSignature):
        """시그니처를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_signatures 
                (signature_id, name, description, pattern, regex_pattern,
                 threat_level, category, enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signature.signature_id,
                signature.name,
                signature.description,
                signature.pattern,
                signature.regex_pattern,
                signature.threat_level.value,
                signature.category,
                1 if signature.enabled else 0,
                signature.created_at.isoformat(),
                signature.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"시그니처 데이터베이스 저장 오류: {e}")
    
    def _save_rule_to_db(self, rule: SecurityRule):
        """규칙을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_rules 
                (rule_id, name, description, conditions, actions,
                 priority, enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id,
                rule.name,
                rule.description,
                json.dumps(rule.conditions),
                json.dumps([action.value for action in rule.actions]),
                rule.priority,
                1 if rule.enabled else 0,
                rule.created_at.isoformat(),
                rule.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"규칙 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            self.is_capturing = False
            self.is_analyzing = False
            
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("침입 탐지 및 방지 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './ids.db',
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 2
        }
    }
    
    # IDS 시스템 생성
    ids_system = IntrusionDetectionSystem(config)
    
    # 사용자 정의 시그니처 생성
    custom_signature = {
        'name': 'Custom Malware',
        'description': '사용자 정의 악성코드 탐지',
        'pattern': 'malware_signature',
        'regex_pattern': r'malware_signature',
        'threat_level': 'high',
        'category': 'malware'
    }
    
    signature_id = ids_system.create_signature(custom_signature)
    print(f"시그니처 생성 완료: {signature_id}")
    
    # 사용자 정의 규칙 생성
    custom_rule = {
        'name': 'Custom Block Rule',
        'description': '사용자 정의 차단 규칙',
        'conditions': {
            'signature_match': 'Custom Malware',
            'threat_level': 'high'
        },
        'actions': ['block_ip', 'alert'],
        'priority': 90
    }
    
    rule_id = ids_system.create_rule(custom_rule)
    print(f"규칙 생성 완료: {rule_id}")
    
    # 패킷 캡처 시작
    ids_system.start_packet_capture()
    
    # 알림 조회
    alerts = ids_system.get_alerts(hours=1)
    print(f"최근 1시간 알림: {len(alerts)}개")
    
    # 차단된 IP 조회
    blocked_ips = ids_system.get_blocked_ips()
    print(f"차단된 IP: {len(blocked_ips)}개") 