"""
보안 정보 및 이벤트 관리 (SIEM) 시스템
로그 수집, 이벤트 상관관계 분석, 실시간 모니터링, 대시보드를 포함한 완전한 SIEM 플랫폼
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
import csv
import io
from collections import defaultdict, deque
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import yaml
import xml.etree.ElementTree as ET
import syslog
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventSeverity(Enum):
    """이벤트 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EventCategory(Enum):
    """이벤트 카테고리"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK = "network"
    SYSTEM = "system"
    APPLICATION = "application"
    SECURITY = "security"
    AUDIT = "audit"

class LogSource(Enum):
    """로그 소스"""
    FIREWALL = "firewall"
    IDS_IPS = "ids_ips"
    ANTIVIRUS = "antivirus"
    WEBSERVER = "webserver"
    DATABASE = "database"
    OPERATING_SYSTEM = "operating_system"
    APPLICATION = "application"
    NETWORK_DEVICE = "network_device"

@dataclass
class SecurityEvent:
    """보안 이벤트"""
    event_id: str
    timestamp: datetime
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    event_type: str
    severity: EventSeverity
    category: EventCategory
    source: LogSource
    message: str
    raw_data: Dict[str, Any]
    normalized_data: Dict[str, Any]
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class CorrelationRule:
    """상관관계 규칙"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    time_window: int
    threshold: int
    actions: List[str]
    enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime

@dataclass
class Alert:
    """알림"""
    alert_id: str
    rule_id: str
    severity: EventSeverity
    title: str
    description: str
    events: List[SecurityEvent]
    timestamp: datetime
    status: str
    assigned_to: str = None
    resolution_notes: str = None

@dataclass
class Dashboard:
    """대시보드"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    layout: Dict[str, Any]
    refresh_interval: int
    created_at: datetime
    updated_at: datetime

class SIEMSystem:
    """보안 정보 및 이벤트 관리 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.events: deque = deque(maxlen=100000)
        self.correlation_rules: Dict[str, CorrelationRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        
        # Redis 클라이언트
        self.redis_client = None
        self._init_redis()
        
        # 이벤트 큐
        self.event_queue = queue.Queue()
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './siem.db'))
        self._init_database()
        
        # 기본 상관관계 규칙 로드
        self._load_default_correlation_rules()
        
        # 기본 대시보드 로드
        self._load_default_dashboards()
        
        # 이벤트 처리 스레드
        self.event_processor_thread = None
        self.is_processing = False
        
        # 상관관계 분석 스레드
        self.correlation_thread = None
        self.is_correlating = False
        
        # 로그 수집기
        self.log_collectors: Dict[str, Callable] = {}
        self._init_log_collectors()
        
        # ML 모델
        self.anomaly_detector = None
        self.vectorizer = None
        self._init_ml_models()
        
        logger.info("SIEM 시스템 초기화 완료")
    
    def _init_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 4),
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
            
            # 보안 이벤트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    source_ip TEXT,
                    destination_ip TEXT,
                    source_port INTEGER,
                    destination_port INTEGER,
                    protocol TEXT,
                    event_type TEXT,
                    severity TEXT,
                    category TEXT,
                    source TEXT,
                    message TEXT,
                    raw_data TEXT,
                    normalized_data TEXT,
                    tags TEXT,
                    metadata TEXT
                )
            ''')
            
            # 상관관계 규칙 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS correlation_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    conditions TEXT,
                    time_window INTEGER,
                    threshold INTEGER,
                    actions TEXT,
                    enabled INTEGER,
                    priority INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 알림 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    rule_id TEXT,
                    severity TEXT,
                    title TEXT,
                    description TEXT,
                    events TEXT,
                    timestamp TEXT,
                    status TEXT,
                    assigned_to TEXT,
                    resolution_notes TEXT
                )
            ''')
            
            # 대시보드 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboards (
                    dashboard_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    widgets TEXT,
                    layout TEXT,
                    refresh_interval INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("SIEM 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_default_correlation_rules(self):
        """기본 상관관계 규칙 로드"""
        try:
            default_rules = [
                {
                    'name': 'Multiple Failed Logins',
                    'description': '다중 실패 로그인 탐지',
                    'conditions': {
                        'event_type': 'authentication_failure',
                        'source_ip': 'same',
                        'time_window': 300
                    },
                    'time_window': 300,
                    'threshold': 5,
                    'actions': ['create_alert', 'block_ip'],
                    'priority': 80
                },
                {
                    'name': 'Port Scan Detection',
                    'description': '포트 스캔 탐지',
                    'conditions': {
                        'event_type': 'connection_attempt',
                        'source_ip': 'same',
                        'destination_ports': 'multiple'
                    },
                    'time_window': 60,
                    'threshold': 10,
                    'actions': ['create_alert', 'rate_limit'],
                    'priority': 70
                },
                {
                    'name': 'DDoS Attack',
                    'description': 'DDoS 공격 탐지',
                    'conditions': {
                        'event_type': 'high_traffic',
                        'source_ips': 'multiple',
                        'destination_ip': 'same'
                    },
                    'time_window': 60,
                    'threshold': 100,
                    'actions': ['create_alert', 'update_firewall'],
                    'priority': 90
                },
                {
                    'name': 'Data Exfiltration',
                    'description': '데이터 유출 탐지',
                    'conditions': {
                        'event_type': 'data_transfer',
                        'data_size': 'large',
                        'destination_ip': 'external'
                    },
                    'time_window': 300,
                    'threshold': 1,
                    'actions': ['create_alert', 'quarantine'],
                    'priority': 95
                }
            ]
            
            for rule_info in default_rules:
                self.create_correlation_rule(rule_info)
            
            logger.info(f"{len(default_rules)}개 기본 상관관계 규칙 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 상관관계 규칙 로드 오류: {e}")
    
    def _load_default_dashboards(self):
        """기본 대시보드 로드"""
        try:
            default_dashboards = [
                {
                    'name': 'Security Overview',
                    'description': '보안 개요 대시보드',
                    'widgets': [
                        {
                            'type': 'chart',
                            'title': '이벤트 분포',
                            'chart_type': 'pie',
                            'data_source': 'events_by_category'
                        },
                        {
                            'type': 'chart',
                            'title': '심각도별 이벤트',
                            'chart_type': 'bar',
                            'data_source': 'events_by_severity'
                        },
                        {
                            'type': 'metric',
                            'title': '총 이벤트 수',
                            'data_source': 'total_events'
                        },
                        {
                            'type': 'metric',
                            'title': '활성 알림',
                            'data_source': 'active_alerts'
                        }
                    ],
                    'layout': {
                        'columns': 2,
                        'rows': 2
                    },
                    'refresh_interval': 30
                },
                {
                    'name': 'Threat Intelligence',
                    'description': '위협 인텔리전스 대시보드',
                    'widgets': [
                        {
                            'type': 'chart',
                            'title': '위협 타입별 분포',
                            'chart_type': 'doughnut',
                            'data_source': 'threats_by_type'
                        },
                        {
                            'type': 'list',
                            'title': '최근 위협',
                            'data_source': 'recent_threats'
                        },
                        {
                            'type': 'map',
                            'title': '지리적 위협 분포',
                            'data_source': 'threats_by_location'
                        }
                    ],
                    'layout': {
                        'columns': 2,
                        'rows': 2
                    },
                    'refresh_interval': 60
                }
            ]
            
            for dashboard_info in default_dashboards:
                self.create_dashboard(dashboard_info)
            
            logger.info(f"{len(default_dashboards)}개 기본 대시보드 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 대시보드 로드 오류: {e}")
    
    def _init_log_collectors(self):
        """로그 수집기 초기화"""
        try:
            # 파일 로그 수집기
            self.log_collectors['file'] = self._collect_file_logs
            
            # Syslog 수집기
            self.log_collectors['syslog'] = self._collect_syslog
            
            # 데이터베이스 로그 수집기
            self.log_collectors['database'] = self._collect_database_logs
            
            # API 로그 수집기
            self.log_collectors['api'] = self._collect_api_logs
            
            logger.info("로그 수집기 초기화 완료")
            
        except Exception as e:
            logger.error(f"로그 수집기 초기화 오류: {e}")
    
    def _init_ml_models(self):
        """ML 모델 초기화"""
        try:
            # 이상 탐지 모델
            self.anomaly_detector = DBSCAN(eps=0.3, min_samples=2)
            
            # 텍스트 벡터화
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            logger.info("ML 모델 초기화 완료")
            
        except Exception as e:
            logger.error(f"ML 모델 초기화 오류: {e}")
    
    def create_correlation_rule(self, rule_info: Dict[str, Any]) -> str:
        """상관관계 규칙 생성"""
        try:
            rule_id = str(uuid.uuid4())
            
            rule = CorrelationRule(
                rule_id=rule_id,
                name=rule_info['name'],
                description=rule_info['description'],
                conditions=rule_info['conditions'],
                time_window=rule_info.get('time_window', 300),
                threshold=rule_info.get('threshold', 1),
                actions=rule_info.get('actions', []),
                enabled=rule_info.get('enabled', True),
                priority=rule_info.get('priority', 50),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.correlation_rules[rule_id] = rule
            
            # 데이터베이스에 저장
            self._save_correlation_rule_to_db(rule)
            
            logger.info(f"상관관계 규칙 생성 완료: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"상관관계 규칙 생성 오류: {e}")
            raise
    
    def create_dashboard(self, dashboard_info: Dict[str, Any]) -> str:
        """대시보드 생성"""
        try:
            dashboard_id = str(uuid.uuid4())
            
            dashboard = Dashboard(
                dashboard_id=dashboard_id,
                name=dashboard_info['name'],
                description=dashboard_info['description'],
                widgets=dashboard_info['widgets'],
                layout=dashboard_info['layout'],
                refresh_interval=dashboard_info.get('refresh_interval', 30),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.dashboards[dashboard_id] = dashboard
            
            # 데이터베이스에 저장
            self._save_dashboard_to_db(dashboard)
            
            logger.info(f"대시보드 생성 완료: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"대시보드 생성 오류: {e}")
            raise
    
    def start_event_processing(self):
        """이벤트 처리 시작"""
        try:
            if self.is_processing:
                logger.warning("이벤트 처리가 이미 실행 중입니다")
                return
            
            self.is_processing = True
            self.event_processor_thread = threading.Thread(
                target=self._event_processing_loop,
                daemon=True
            )
            self.event_processor_thread.start()
            
            logger.info("이벤트 처리 시작")
            
        except Exception as e:
            logger.error(f"이벤트 처리 시작 오류: {e}")
    
    def _event_processing_loop(self):
        """이벤트 처리 루프"""
        try:
            while self.is_processing:
                try:
                    # 이벤트 큐에서 이벤트 가져오기
                    event = self.event_queue.get(timeout=1)
                    
                    # 이벤트 처리
                    self._process_event(event)
                    
                    # 이벤트 큐 작업 완료 표시
                    self.event_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"이벤트 처리 오류: {e}")
                    
        except Exception as e:
            logger.error(f"이벤트 처리 루프 오류: {e}")
        finally:
            self.is_processing = False
    
    def _process_event(self, event: SecurityEvent):
        """이벤트 처리"""
        try:
            # 이벤트 정규화
            normalized_event = self._normalize_event(event)
            
            # 이벤트 저장
            self.events.append(normalized_event)
            
            # 데이터베이스에 저장
            self._save_event_to_db(normalized_event)
            
            # Redis에 이벤트 저장
            if self.redis_client:
                event_key = f"event:{normalized_event.event_id}"
                self.redis_client.setex(
                    event_key,
                    3600,  # 1시간 TTL
                    json.dumps(asdict(normalized_event))
                )
            
            # 상관관계 분석 트리거
            self._trigger_correlation_analysis(normalized_event)
            
            # 이상 탐지
            self._anomaly_detection(normalized_event)
            
        except Exception as e:
            logger.error(f"이벤트 처리 오류: {e}")
    
    def _normalize_event(self, event: SecurityEvent) -> SecurityEvent:
        """이벤트 정규화"""
        try:
            # IP 주소 정규화
            source_ip = self._normalize_ip(event.source_ip)
            destination_ip = self._normalize_ip(event.destination_ip)
            
            # 포트 정규화
            source_port = self._normalize_port(event.source_port)
            destination_port = self._normalize_port(event.destination_port)
            
            # 프로토콜 정규화
            protocol = self._normalize_protocol(event.protocol)
            
            # 메시지 정규화
            normalized_message = self._normalize_message(event.message)
            
            # 태그 생성
            tags = self._generate_tags(event)
            
            # 정규화된 데이터 생성
            normalized_data = {
                'source_ip': source_ip,
                'destination_ip': destination_ip,
                'source_port': source_port,
                'destination_port': destination_port,
                'protocol': protocol,
                'normalized_message': normalized_message,
                'tags': tags
            }
            
            return SecurityEvent(
                event_id=event.event_id,
                timestamp=event.timestamp,
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_port=source_port,
                destination_port=destination_port,
                protocol=protocol,
                event_type=event.event_type,
                severity=event.severity,
                category=event.category,
                source=event.source,
                message=normalized_message,
                raw_data=event.raw_data,
                normalized_data=normalized_data,
                tags=tags,
                metadata=event.metadata
            )
            
        except Exception as e:
            logger.error(f"이벤트 정규화 오류: {e}")
            return event
    
    def _normalize_ip(self, ip_address: str) -> str:
        """IP 주소 정규화"""
        try:
            if not ip_address:
                return "0.0.0.0"
            
            # IPv4 주소 정규화
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip_address):
                return ip_address
            
            # IPv6 주소 정규화
            if ':' in ip_address:
                return ip_address
            
            return "0.0.0.0"
            
        except Exception as e:
            logger.error(f"IP 주소 정규화 오류: {e}")
            return "0.0.0.0"
    
    def _normalize_port(self, port: int) -> int:
        """포트 정규화"""
        try:
            if port is None or port < 0 or port > 65535:
                return 0
            return port
        except Exception as e:
            logger.error(f"포트 정규화 오류: {e}")
            return 0
    
    def _normalize_protocol(self, protocol: str) -> str:
        """프로토콜 정규화"""
        try:
            if not protocol:
                return "unknown"
            
            protocol_lower = protocol.lower()
            
            if protocol_lower in ['tcp', 'udp', 'icmp', 'http', 'https', 'ftp', 'ssh']:
                return protocol_lower
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"프로토콜 정규화 오류: {e}")
            return "unknown"
    
    def _normalize_message(self, message: str) -> str:
        """메시지 정규화"""
        try:
            if not message:
                return ""
            
            # 특수 문자 제거
            normalized = re.sub(r'[^\w\s\-\.]', ' ', message)
            
            # 연속 공백 제거
            normalized = re.sub(r'\s+', ' ', normalized)
            
            return normalized.strip()
            
        except Exception as e:
            logger.error(f"메시지 정규화 오류: {e}")
            return message
    
    def _generate_tags(self, event: SecurityEvent) -> List[str]:
        """태그 생성"""
        try:
            tags = []
            
            # 이벤트 타입 태그
            tags.append(f"type:{event.event_type}")
            
            # 심각도 태그
            tags.append(f"severity:{event.severity.value}")
            
            # 카테고리 태그
            tags.append(f"category:{event.category.value}")
            
            # 소스 태그
            tags.append(f"source:{event.source.value}")
            
            # 프로토콜 태그
            if event.protocol:
                tags.append(f"protocol:{event.protocol}")
            
            # 포트 태그
            if event.destination_port:
                if event.destination_port in [80, 443, 8080]:
                    tags.append("web_traffic")
                elif event.destination_port in [22, 23]:
                    tags.append("remote_access")
                elif event.destination_port in [21, 20]:
                    tags.append("file_transfer")
            
            return tags
            
        except Exception as e:
            logger.error(f"태그 생성 오류: {e}")
            return []
    
    def _trigger_correlation_analysis(self, event: SecurityEvent):
        """상관관계 분석 트리거"""
        try:
            # 상관관계 분석 스레드가 실행 중이지 않으면 시작
            if not self.is_correlating:
                self.is_correlating = True
                self.correlation_thread = threading.Thread(
                    target=self._correlation_analysis_loop,
                    daemon=True
                )
                self.correlation_thread.start()
                
        except Exception as e:
            logger.error(f"상관관계 분석 트리거 오류: {e}")
    
    def _correlation_analysis_loop(self):
        """상관관계 분석 루프"""
        try:
            while self.is_correlating:
                # 모든 상관관계 규칙에 대해 분석
                for rule in self.correlation_rules.values():
                    if not rule.enabled:
                        continue
                    
                    self._evaluate_correlation_rule(rule)
                
                # 10초 대기
                time.sleep(10)
                
        except Exception as e:
            logger.error(f"상관관계 분석 루프 오류: {e}")
        finally:
            self.is_correlating = False
    
    def _evaluate_correlation_rule(self, rule: CorrelationRule):
        """상관관계 규칙 평가"""
        try:
            # 시간 윈도우 내의 이벤트 필터링
            cutoff_time = datetime.now() - timedelta(seconds=rule.time_window)
            recent_events = [
                event for event in self.events
                if event.timestamp > cutoff_time
            ]
            
            # 규칙 조건 평가
            matching_events = self._match_rule_conditions(rule, recent_events)
            
            # 임계값 확인
            if len(matching_events) >= rule.threshold:
                # 알림 생성
                self._create_correlation_alert(rule, matching_events)
                
                # 액션 실행
                self._execute_rule_actions(rule, matching_events)
                
        except Exception as e:
            logger.error(f"상관관계 규칙 평가 오류: {e}")
    
    def _match_rule_conditions(self, rule: CorrelationRule, events: List[SecurityEvent]) -> List[SecurityEvent]:
        """규칙 조건 매칭"""
        try:
            matching_events = []
            conditions = rule.conditions
            
            for event in events:
                match = True
                
                # 이벤트 타입 조건
                if 'event_type' in conditions:
                    if event.event_type != conditions['event_type']:
                        match = False
                
                # 소스 IP 조건
                if 'source_ip' in conditions:
                    if conditions['source_ip'] == 'same':
                        # 같은 소스 IP의 이벤트들만 그룹화
                        pass
                    elif event.source_ip != conditions['source_ip']:
                        match = False
                
                # 목적지 IP 조건
                if 'destination_ip' in conditions:
                    if event.destination_ip != conditions['destination_ip']:
                        match = False
                
                if match:
                    matching_events.append(event)
            
            return matching_events
            
        except Exception as e:
            logger.error(f"규칙 조건 매칭 오류: {e}")
            return []
    
    def _create_correlation_alert(self, rule: CorrelationRule, events: List[SecurityEvent]):
        """상관관계 알림 생성"""
        try:
            alert_id = str(uuid.uuid4())
            
            # 알림 제목 및 설명 생성
            title = f"상관관계 규칙 트리거: {rule.name}"
            description = f"규칙 '{rule.name}'이 {len(events)}개의 이벤트로 트리거되었습니다."
            
            # 심각도 결정
            severity = max(event.severity for event in events)
            
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                severity=severity,
                title=title,
                description=description,
                events=events,
                timestamp=datetime.now(),
                status='open'
            )
            
            self.alerts[alert_id] = alert
            
            # 데이터베이스에 저장
            self._save_alert_to_db(alert)
            
            logger.warning(f"상관관계 알림 생성: {alert_id}")
            
        except Exception as e:
            logger.error(f"상관관계 알림 생성 오류: {e}")
    
    def _execute_rule_actions(self, rule: CorrelationRule, events: List[SecurityEvent]):
        """규칙 액션 실행"""
        try:
            for action in rule.actions:
                if action == 'create_alert':
                    # 이미 알림이 생성되었으므로 추가 작업 없음
                    pass
                elif action == 'block_ip':
                    # IP 차단
                    for event in events:
                        self._block_ip(event.source_ip)
                elif action == 'rate_limit':
                    # 속도 제한
                    for event in events:
                        self._rate_limit_ip(event.source_ip)
                elif action == 'update_firewall':
                    # 방화벽 규칙 업데이트
                    self._update_firewall_rules(events)
                elif action == 'quarantine':
                    # 격리
                    for event in events:
                        self._quarantine_system(event.source_ip)
                        
        except Exception as e:
            logger.error(f"규칙 액션 실행 오류: {e}")
    
    def _block_ip(self, ip_address: str):
        """IP 주소 차단"""
        try:
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
            # Redis에 속도 제한된 IP 저장
            if self.redis_client:
                self.redis_client.sadd('rate_limited_ips', ip_address)
                self.redis_client.expire('rate_limited_ips', 1800)  # 30분 TTL
            
            logger.info(f"IP 주소 속도 제한: {ip_address}")
            
        except Exception as e:
            logger.error(f"IP 주소 속도 제한 오류: {e}")
    
    def _update_firewall_rules(self, events: List[SecurityEvent]):
        """방화벽 규칙 업데이트"""
        try:
            # 실제로는 방화벽 API를 호출하여 규칙을 업데이트
            logger.info(f"방화벽 규칙 업데이트: {len(events)}개 이벤트")
            
        except Exception as e:
            logger.error(f"방화벽 규칙 업데이트 오류: {e}")
    
    def _quarantine_system(self, ip_address: str):
        """시스템 격리"""
        try:
            # 실제로는 격리 시스템을 호출
            logger.info(f"시스템 격리: {ip_address}")
            
        except Exception as e:
            logger.error(f"시스템 격리 오류: {e}")
    
    def _anomaly_detection(self, event: SecurityEvent):
        """이상 탐지"""
        try:
            # 이벤트 특성 벡터 생성
            features = [
                event.source_port,
                event.destination_port,
                len(event.message),
                len(event.tags),
                event.severity.value == 'critical'
            ]
            
            # 이상 탐지 (간단한 임계값 기반)
            if (event.source_port > 1024 and event.destination_port < 1024 and
                len(event.message) > 1000):
                # 이상 이벤트로 분류
                self._create_anomaly_alert(event)
                
        except Exception as e:
            logger.error(f"이상 탐지 오류: {e}")
    
    def _create_anomaly_alert(self, event: SecurityEvent):
        """이상 알림 생성"""
        try:
            alert_id = str(uuid.uuid4())
            
            alert = Alert(
                alert_id=alert_id,
                rule_id='anomaly_detection',
                severity=EventSeverity.MEDIUM,
                title='이상 이벤트 탐지',
                description=f'이상한 패턴의 이벤트가 탐지되었습니다: {event.event_type}',
                events=[event],
                timestamp=datetime.now(),
                status='open'
            )
            
            self.alerts[alert_id] = alert
            
            # 데이터베이스에 저장
            self._save_alert_to_db(alert)
            
            logger.warning(f"이상 알림 생성: {alert_id}")
            
        except Exception as e:
            logger.error(f"이상 알림 생성 오류: {e}")
    
    def add_event(self, event_data: Dict[str, Any]):
        """이벤트 추가"""
        try:
            event_id = str(uuid.uuid4())
            
            event = SecurityEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                source_ip=event_data.get('source_ip', ''),
                destination_ip=event_data.get('destination_ip', ''),
                source_port=event_data.get('source_port', 0),
                destination_port=event_data.get('destination_port', 0),
                protocol=event_data.get('protocol', ''),
                event_type=event_data.get('event_type', 'unknown'),
                severity=EventSeverity(event_data.get('severity', 'low')),
                category=EventCategory(event_data.get('category', 'system')),
                source=LogSource(event_data.get('source', 'application')),
                message=event_data.get('message', ''),
                raw_data=event_data,
                normalized_data={},
                tags=event_data.get('tags', []),
                metadata=event_data.get('metadata', {})
            )
            
            # 이벤트 큐에 추가
            self.event_queue.put(event)
            
        except Exception as e:
            logger.error(f"이벤트 추가 오류: {e}")
    
    def get_events(self, hours: int = 24) -> List[SecurityEvent]:
        """이벤트 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_events = [
                event for event in self.events
                if event.timestamp > cutoff_time
            ]
            return sorted(recent_events, key=lambda x: x.timestamp, reverse=True)
        except Exception as e:
            logger.error(f"이벤트 조회 오류: {e}")
            return []
    
    def get_alerts(self, status: str = None) -> List[Alert]:
        """알림 조회"""
        try:
            if status:
                return [alert for alert in self.alerts.values() if alert.status == status]
            return list(self.alerts.values())
        except Exception as e:
            logger.error(f"알림 조회 오류: {e}")
            return []
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """대시보드 데이터 조회"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                return {}
            
            data = {}
            
            for widget in dashboard.widgets:
                widget_type = widget['type']
                data_source = widget['data_source']
                
                if data_source == 'events_by_category':
                    data[data_source] = self._get_events_by_category()
                elif data_source == 'events_by_severity':
                    data[data_source] = self._get_events_by_severity()
                elif data_source == 'total_events':
                    data[data_source] = len(self.events)
                elif data_source == 'active_alerts':
                    data[data_source] = len([a for a in self.alerts.values() if a.status == 'open'])
            
            return data
            
        except Exception as e:
            logger.error(f"대시보드 데이터 조회 오류: {e}")
            return {}
    
    def _get_events_by_category(self) -> Dict[str, int]:
        """카테고리별 이벤트 수"""
        try:
            category_counts = defaultdict(int)
            for event in self.events:
                category_counts[event.category.value] += 1
            return dict(category_counts)
        except Exception as e:
            logger.error(f"카테고리별 이벤트 수 조회 오류: {e}")
            return {}
    
    def _get_events_by_severity(self) -> Dict[str, int]:
        """심각도별 이벤트 수"""
        try:
            severity_counts = defaultdict(int)
            for event in self.events:
                severity_counts[event.severity.value] += 1
            return dict(severity_counts)
        except Exception as e:
            logger.error(f"심각도별 이벤트 수 조회 오류: {e}")
            return {}
    
    def _save_event_to_db(self, event: SecurityEvent):
        """이벤트를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_events 
                (event_id, timestamp, source_ip, destination_ip, source_port,
                 destination_port, protocol, event_type, severity, category,
                 source, message, raw_data, normalized_data, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.timestamp.isoformat(),
                event.source_ip,
                event.destination_ip,
                event.source_port,
                event.destination_port,
                event.protocol,
                event.event_type,
                event.severity.value,
                event.category.value,
                event.source.value,
                event.message,
                json.dumps(event.raw_data),
                json.dumps(event.normalized_data),
                json.dumps(event.tags),
                json.dumps(event.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"이벤트 데이터베이스 저장 오류: {e}")
    
    def _save_alert_to_db(self, alert: Alert):
        """알림을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO alerts 
                (alert_id, rule_id, severity, title, description, events,
                 timestamp, status, assigned_to, resolution_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.rule_id,
                alert.severity.value,
                alert.title,
                alert.description,
                json.dumps([asdict(event) for event in alert.events]),
                alert.timestamp.isoformat(),
                alert.status,
                alert.assigned_to,
                alert.resolution_notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"알림 데이터베이스 저장 오류: {e}")
    
    def _save_correlation_rule_to_db(self, rule: CorrelationRule):
        """상관관계 규칙을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO correlation_rules 
                (rule_id, name, description, conditions, time_window,
                 threshold, actions, enabled, priority, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id,
                rule.name,
                rule.description,
                json.dumps(rule.conditions),
                rule.time_window,
                rule.threshold,
                json.dumps(rule.actions),
                1 if rule.enabled else 0,
                rule.priority,
                rule.created_at.isoformat(),
                rule.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"상관관계 규칙 데이터베이스 저장 오류: {e}")
    
    def _save_dashboard_to_db(self, dashboard: Dashboard):
        """대시보드를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO dashboards 
                (dashboard_id, name, description, widgets, layout,
                 refresh_interval, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dashboard.dashboard_id,
                dashboard.name,
                dashboard.description,
                json.dumps(dashboard.widgets),
                json.dumps(dashboard.layout),
                dashboard.refresh_interval,
                dashboard.created_at.isoformat(),
                dashboard.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"대시보드 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            self.is_processing = False
            self.is_correlating = False
            
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("SIEM 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './siem.db',
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 4
        }
    }
    
    # SIEM 시스템 생성
    siem_system = SIEMSystem(config)
    
    # 사용자 정의 상관관계 규칙 생성
    custom_rule = {
        'name': 'Custom Correlation Rule',
        'description': '사용자 정의 상관관계 규칙',
        'conditions': {
            'event_type': 'custom_event',
            'source_ip': 'same'
        },
        'time_window': 300,
        'threshold': 3,
        'actions': ['create_alert'],
        'priority': 60
    }
    
    rule_id = siem_system.create_correlation_rule(custom_rule)
    print(f"상관관계 규칙 생성 완료: {rule_id}")
    
    # 사용자 정의 대시보드 생성
    custom_dashboard = {
        'name': 'Custom Dashboard',
        'description': '사용자 정의 대시보드',
        'widgets': [
            {
                'type': 'chart',
                'title': '사용자 정의 차트',
                'chart_type': 'line',
                'data_source': 'custom_data'
            }
        ],
        'layout': {'columns': 1, 'rows': 1},
        'refresh_interval': 60
    }
    
    dashboard_id = siem_system.create_dashboard(custom_dashboard)
    print(f"대시보드 생성 완료: {dashboard_id}")
    
    # 이벤트 추가
    event_data = {
        'source_ip': '192.168.1.100',
        'destination_ip': '192.168.1.1',
        'source_port': 12345,
        'destination_port': 80,
        'protocol': 'tcp',
        'event_type': 'connection_attempt',
        'severity': 'medium',
        'category': 'network',
        'source': 'firewall',
        'message': 'Connection attempt from 192.168.1.100 to 192.168.1.1:80'
    }
    
    siem_system.add_event(event_data)
    print("이벤트 추가 완료")
    
    # 이벤트 처리 시작
    siem_system.start_event_processing()
    
    # 이벤트 조회
    events = siem_system.get_events(hours=1)
    print(f"최근 1시간 이벤트: {len(events)}개")
    
    # 알림 조회
    alerts = siem_system.get_alerts()
    print(f"총 알림 수: {len(alerts)}개") 