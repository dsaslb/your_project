"""
위협 인텔리전스 시스템
위협 정보 수집, 분석, 공유, 자동 대응을 포함한 완전한 위협 인텔리전스 플랫폼
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
import requests
import feedparser
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import yaml
import csv
import io

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatType(Enum):
    """위협 타입"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DDoS = "ddos"
    RANSOMWARE = "ransomware"
    APT = "apt"
    BOTNET = "botnet"
    EXPLOIT = "exploit"
    VULNERABILITY = "vulnerability"

class ConfidenceLevel(Enum):
    """신뢰도 수준"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class SourceType(Enum):
    """소스 타입"""
    OPEN_SOURCE = "open_source"
    COMMERCIAL = "commercial"
    COMMUNITY = "community"
    INTERNAL = "internal"
    GOVERNMENT = "government"

@dataclass
class ThreatIndicator:
    """위협 지표"""
    indicator_id: str
    indicator_type: str
    value: str
    threat_type: ThreatType
    confidence: ConfidenceLevel
    source: str
    source_type: SourceType
    first_seen: datetime
    last_seen: datetime
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class ThreatReport:
    """위협 리포트"""
    report_id: str
    title: str
    description: str
    threat_type: ThreatType
    severity: str
    confidence: ConfidenceLevel
    source: str
    source_type: SourceType
    published_date: datetime
    indicators: List[ThreatIndicator]
    tags: List[str]
    content: str
    metadata: Dict[str, Any]

@dataclass
class ThreatCampaign:
    """위협 캠페인"""
    campaign_id: str
    name: str
    description: str
    threat_type: ThreatType
    start_date: datetime
    end_date: datetime
    targets: List[str]
    indicators: List[ThreatIndicator]
    tactics: List[str]
    techniques: List[str]
    attribution: str
    metadata: Dict[str, Any]

@dataclass
class ThreatFeed:
    """위협 피드"""
    feed_id: str
    name: str
    url: str
    feed_type: str
    source_type: SourceType
    update_interval: int
    last_update: datetime
    enabled: bool
    credentials: Dict[str, str]
    metadata: Dict[str, Any]

class ThreatIntelligenceSystem:
    """위협 인텔리전스 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.reports: Dict[str, ThreatReport] = {}
        self.campaigns: Dict[str, ThreatCampaign] = {}
        self.feeds: Dict[str, ThreatFeed] = {}
        
        # Redis 클라이언트
        self.redis_client = None
        self._init_redis()
        
        # HTTP 클라이언트 세션
        self.http_session = None
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './threat_intelligence.db'))
        self._init_database()
        
        # 기본 피드 로드
        self._load_default_feeds()
        
        # 피드 업데이트 스레드
        self.feed_update_thread = None
        self.is_updating = False
        
        # 분석 스레드
        self.analysis_thread = None
        self.is_analyzing = False
        
        # ML 모델
        self.clustering_model = None
        self.vectorizer = None
        self._init_ml_models()
        
        logger.info("위협 인텔리전스 시스템 초기화 완료")
    
    def _init_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 3),
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
            
            # 위협 지표 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_indicators (
                    indicator_id TEXT PRIMARY KEY,
                    indicator_type TEXT,
                    value TEXT,
                    threat_type TEXT,
                    confidence TEXT,
                    source TEXT,
                    source_type TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    tags TEXT,
                    metadata TEXT
                )
            ''')
            
            # 위협 리포트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_reports (
                    report_id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    threat_type TEXT,
                    severity TEXT,
                    confidence TEXT,
                    source TEXT,
                    source_type TEXT,
                    published_date TEXT,
                    tags TEXT,
                    content TEXT,
                    metadata TEXT
                )
            ''')
            
            # 위협 캠페인 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_campaigns (
                    campaign_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    threat_type TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    targets TEXT,
                    tactics TEXT,
                    techniques TEXT,
                    attribution TEXT,
                    metadata TEXT
                )
            ''')
            
            # 위협 피드 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_feeds (
                    feed_id TEXT PRIMARY KEY,
                    name TEXT,
                    url TEXT,
                    feed_type TEXT,
                    source_type TEXT,
                    update_interval INTEGER,
                    last_update TEXT,
                    enabled INTEGER,
                    credentials TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("위협 인텔리전스 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_default_feeds(self):
        """기본 피드 로드"""
        try:
            default_feeds = [
                {
                    'name': 'AbuseIPDB',
                    'url': 'https://api.abuseipdb.com/api/v2/blacklist',
                    'feed_type': 'ip_blacklist',
                    'source_type': SourceType.COMMUNITY,
                    'update_interval': 3600,
                    'enabled': True,
                    'credentials': {'api_key': 'your-api-key'}
                },
                {
                    'name': 'PhishTank',
                    'url': 'https://data.phishtank.com/data/online-valid.json',
                    'feed_type': 'phishing_urls',
                    'source_type': SourceType.COMMUNITY,
                    'update_interval': 1800,
                    'enabled': True,
                    'credentials': {}
                },
                {
                    'name': 'OpenPhish',
                    'url': 'https://openphish.com/feed.txt',
                    'feed_type': 'phishing_urls',
                    'source_type': SourceType.OPEN_SOURCE,
                    'update_interval': 1800,
                    'enabled': True,
                    'credentials': {}
                },
                {
                    'name': 'MalwareBazaar',
                    'url': 'https://bazaar.abuse.ch/export/txt/recent/',
                    'feed_type': 'malware_hashes',
                    'source_type': SourceType.COMMUNITY,
                    'update_interval': 3600,
                    'enabled': True,
                    'credentials': {}
                }
            ]
            
            for feed_info in default_feeds:
                self.create_feed(feed_info)
            
            logger.info(f"{len(default_feeds)}개 기본 피드 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 피드 로드 오류: {e}")
    
    def _init_ml_models(self):
        """ML 모델 초기화"""
        try:
            # 클러스터링 모델
            self.clustering_model = DBSCAN(eps=0.3, min_samples=2)
            
            # 텍스트 벡터화
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            logger.info("ML 모델 초기화 완료")
            
        except Exception as e:
            logger.error(f"ML 모델 초기화 오류: {e}")
    
    def create_feed(self, feed_info: Dict[str, Any]) -> str:
        """위협 피드 생성"""
        try:
            feed_id = str(uuid.uuid4())
            
            feed = ThreatFeed(
                feed_id=feed_id,
                name=feed_info['name'],
                url=feed_info['url'],
                feed_type=feed_info['feed_type'],
                source_type=SourceType(feed_info['source_type']),
                update_interval=feed_info.get('update_interval', 3600),
                last_update=datetime.now(),
                enabled=feed_info.get('enabled', True),
                credentials=feed_info.get('credentials', {}),
                metadata=feed_info.get('metadata', {})
            )
            
            self.feeds[feed_id] = feed
            
            # 데이터베이스에 저장
            self._save_feed_to_db(feed)
            
            logger.info(f"위협 피드 생성 완료: {feed_id}")
            return feed_id
            
        except Exception as e:
            logger.error(f"위협 피드 생성 오류: {e}")
            raise
    
    def start_feed_updates(self):
        """피드 업데이트 시작"""
        try:
            if self.is_updating:
                logger.warning("피드 업데이트가 이미 실행 중입니다")
                return
            
            self.is_updating = True
            self.feed_update_thread = threading.Thread(
                target=self._feed_update_loop,
                daemon=True
            )
            self.feed_update_thread.start()
            
            logger.info("피드 업데이트 시작")
            
        except Exception as e:
            logger.error(f"피드 업데이트 시작 오류: {e}")
    
    def _feed_update_loop(self):
        """피드 업데이트 루프"""
        try:
            while self.is_updating:
                for feed in self.feeds.values():
                    if not feed.enabled:
                        continue
                    
                    # 업데이트 간격 확인
                    time_since_update = datetime.now() - feed.last_update
                    if time_since_update.total_seconds() >= feed.update_interval:
                        self._update_feed(feed)
                
                # 1분 대기
                time.sleep(60)
                
        except Exception as e:
            logger.error(f"피드 업데이트 루프 오류: {e}")
        finally:
            self.is_updating = False
    
    async def _update_feed(self, feed: ThreatFeed):
        """피드 업데이트"""
        try:
            if not self.http_session:
                timeout = ClientTimeout(total=30)
                self.http_session = ClientSession(timeout=timeout)
            
            headers = {}
            if feed.credentials.get('api_key'):
                headers['Key'] = feed.credentials['api_key']
            
            async with self.http_session.get(feed.url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # 피드 타입에 따른 파싱
                    if feed.feed_type == 'ip_blacklist':
                        await self._parse_ip_blacklist(feed, content)
                    elif feed.feed_type == 'phishing_urls':
                        await self._parse_phishing_urls(feed, content)
                    elif feed.feed_type == 'malware_hashes':
                        await self._parse_malware_hashes(feed, content)
                    
                    # 마지막 업데이트 시간 갱신
                    feed.last_update = datetime.now()
                    self._save_feed_to_db(feed)
                    
                    logger.info(f"피드 업데이트 완료: {feed.name}")
                else:
                    logger.error(f"피드 업데이트 실패: {feed.name} - {response.status}")
                    
        except Exception as e:
            logger.error(f"피드 업데이트 오류: {feed.name} - {e}")
    
    async def _parse_ip_blacklist(self, feed: ThreatFeed, content: str):
        """IP 블랙리스트 파싱"""
        try:
            # CSV 형식 파싱
            lines = content.strip().split('\n')
            for line in lines:
                if line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) >= 1:
                        ip_address = parts[0].strip()
                        
                        # 위협 지표 생성
                        indicator = ThreatIndicator(
                            indicator_id=str(uuid.uuid4()),
                            indicator_type='ip',
                            value=ip_address,
                            threat_type=ThreatType.MALWARE,
                            confidence=ConfidenceLevel.MEDIUM,
                            source=feed.name,
                            source_type=feed.source_type,
                            first_seen=datetime.now(),
                            last_seen=datetime.now(),
                            tags=['blacklist', 'malware'],
                            metadata={'feed_id': feed.feed_id}
                        )
                        
                        self.indicators[indicator.indicator_id] = indicator
                        self._save_indicator_to_db(indicator)
                        
        except Exception as e:
            logger.error(f"IP 블랙리스트 파싱 오류: {e}")
    
    async def _parse_phishing_urls(self, feed: ThreatFeed, content: str):
        """피싱 URL 파싱"""
        try:
            if feed.name == 'PhishTank':
                # JSON 형식 파싱
                data = json.loads(content)
                for item in data:
                    url = item.get('url', '')
                    if url:
                        indicator = ThreatIndicator(
                            indicator_id=str(uuid.uuid4()),
                            indicator_type='url',
                            value=url,
                            threat_type=ThreatType.PHISHING,
                            confidence=ConfidenceLevel.HIGH,
                            source=feed.name,
                            source_type=feed.source_type,
                            first_seen=datetime.fromisoformat(item.get('submission_time', datetime.now().isoformat())),
                            last_seen=datetime.now(),
                            tags=['phishing', 'url'],
                            metadata={'feed_id': feed.feed_id, 'phish_id': item.get('phish_id')}
                        )
                        
                        self.indicators[indicator.indicator_id] = indicator
                        self._save_indicator_to_db(indicator)
            else:
                # 텍스트 형식 파싱
                lines = content.strip().split('\n')
                for line in lines:
                    if line and not line.startswith('#'):
                        url = line.strip()
                        
                        indicator = ThreatIndicator(
                            indicator_id=str(uuid.uuid4()),
                            indicator_type='url',
                            value=url,
                            threat_type=ThreatType.PHISHING,
                            confidence=ConfidenceLevel.MEDIUM,
                            source=feed.name,
                            source_type=feed.source_type,
                            first_seen=datetime.now(),
                            last_seen=datetime.now(),
                            tags=['phishing', 'url'],
                            metadata={'feed_id': feed.feed_id}
                        )
                        
                        self.indicators[indicator.indicator_id] = indicator
                        self._save_indicator_to_db(indicator)
                        
        except Exception as e:
            logger.error(f"피싱 URL 파싱 오류: {e}")
    
    async def _parse_malware_hashes(self, feed: ThreatFeed, content: str):
        """악성코드 해시 파싱"""
        try:
            lines = content.strip().split('\n')
            for line in lines:
                if line and not line.startswith('#'):
                    hash_value = line.strip()
                    
                    # 해시 타입 판별
                    if len(hash_value) == 32:
                        hash_type = 'md5'
                    elif len(hash_value) == 40:
                        hash_type = 'sha1'
                    elif len(hash_value) == 64:
                        hash_type = 'sha256'
                    else:
                        continue
                    
                    indicator = ThreatIndicator(
                        indicator_id=str(uuid.uuid4()),
                        indicator_type=f'hash_{hash_type}',
                        value=hash_value,
                        threat_type=ThreatType.MALWARE,
                        confidence=ConfidenceLevel.HIGH,
                        source=feed.name,
                        source_type=feed.source_type,
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        tags=['malware', 'hash'],
                        metadata={'feed_id': feed.feed_id, 'hash_type': hash_type}
                    )
                    
                    self.indicators[indicator.indicator_id] = indicator
                    self._save_indicator_to_db(indicator)
                    
        except Exception as e:
            logger.error(f"악성코드 해시 파싱 오류: {e}")
    
    def create_report(self, report_info: Dict[str, Any]) -> str:
        """위협 리포트 생성"""
        try:
            report_id = str(uuid.uuid4())
            
            report = ThreatReport(
                report_id=report_id,
                title=report_info['title'],
                description=report_info['description'],
                threat_type=ThreatType(report_info['threat_type']),
                severity=report_info.get('severity', 'medium'),
                confidence=ConfidenceLevel(report_info.get('confidence', 'medium')),
                source=report_info['source'],
                source_type=SourceType(report_info['source_type']),
                published_date=datetime.now(),
                indicators=report_info.get('indicators', []),
                tags=report_info.get('tags', []),
                content=report_info.get('content', ''),
                metadata=report_info.get('metadata', {})
            )
            
            self.reports[report_id] = report
            
            # 데이터베이스에 저장
            self._save_report_to_db(report)
            
            logger.info(f"위협 리포트 생성 완료: {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"위협 리포트 생성 오류: {e}")
            raise
    
    def create_campaign(self, campaign_info: Dict[str, Any]) -> str:
        """위협 캠페인 생성"""
        try:
            campaign_id = str(uuid.uuid4())
            
            campaign = ThreatCampaign(
                campaign_id=campaign_id,
                name=campaign_info['name'],
                description=campaign_info['description'],
                threat_type=ThreatType(campaign_info['threat_type']),
                start_date=datetime.now(),
                end_date=campaign_info.get('end_date'),
                targets=campaign_info.get('targets', []),
                indicators=campaign_info.get('indicators', []),
                tactics=campaign_info.get('tactics', []),
                techniques=campaign_info.get('techniques', []),
                attribution=campaign_info.get('attribution', ''),
                metadata=campaign_info.get('metadata', {})
            )
            
            self.campaigns[campaign_id] = campaign
            
            # 데이터베이스에 저장
            self._save_campaign_to_db(campaign)
            
            logger.info(f"위협 캠페인 생성 완료: {campaign_id}")
            return campaign_id
            
        except Exception as e:
            logger.error(f"위협 캠페인 생성 오류: {e}")
            raise
    
    def search_indicators(self, query: str, indicator_type: str = None) -> List[ThreatIndicator]:
        """지표 검색"""
        try:
            results = []
            
            for indicator in self.indicators.values():
                # 타입 필터링
                if indicator_type and indicator.indicator_type != indicator_type:
                    continue
                
                # 검색어 매칭
                if (query.lower() in indicator.value.lower() or
                    query.lower() in ' '.join(indicator.tags).lower() or
                    query.lower() in indicator.source.lower()):
                    results.append(indicator)
            
            return results
            
        except Exception as e:
            logger.error(f"지표 검색 오류: {e}")
            return []
    
    def get_indicators_by_type(self, indicator_type: str) -> List[ThreatIndicator]:
        """타입별 지표 조회"""
        try:
            return [indicator for indicator in self.indicators.values() 
                   if indicator.indicator_type == indicator_type]
        except Exception as e:
            logger.error(f"타입별 지표 조회 오류: {e}")
            return []
    
    def get_indicators_by_threat_type(self, threat_type: ThreatType) -> List[ThreatIndicator]:
        """위협 타입별 지표 조회"""
        try:
            return [indicator for indicator in self.indicators.values() 
                   if indicator.threat_type == threat_type]
        except Exception as e:
            logger.error(f"위협 타입별 지표 조회 오류: {e}")
            return []
    
    def analyze_campaigns(self) -> List[Dict[str, Any]]:
        """캠페인 분석"""
        try:
            analysis_results = []
            
            for campaign in self.campaigns.values():
                # 캠페인 통계
                stats = {
                    'campaign_id': campaign.campaign_id,
                    'name': campaign.name,
                    'threat_type': campaign.threat_type.value,
                    'indicator_count': len(campaign.indicators),
                    'target_count': len(campaign.targets),
                    'tactic_count': len(campaign.tactics),
                    'technique_count': len(campaign.techniques),
                    'duration_days': (campaign.end_date - campaign.start_date).days if campaign.end_date else None
                }
                
                analysis_results.append(stats)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"캠페인 분석 오류: {e}")
            return []
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """위협 통계"""
        try:
            stats = {
                'total_indicators': len(self.indicators),
                'total_reports': len(self.reports),
                'total_campaigns': len(self.campaigns),
                'total_feeds': len(self.feeds),
                'indicators_by_type': defaultdict(int),
                'indicators_by_threat_type': defaultdict(int),
                'indicators_by_source': defaultdict(int),
                'recent_indicators': 0,
                'recent_reports': 0
            }
            
            # 최근 24시간 지표
            one_day_ago = datetime.now() - timedelta(days=1)
            
            for indicator in self.indicators.values():
                stats['indicators_by_type'][indicator.indicator_type] += 1
                stats['indicators_by_threat_type'][indicator.threat_type.value] += 1
                stats['indicators_by_source'][indicator.source] += 1
                
                if indicator.last_seen > one_day_ago:
                    stats['recent_indicators'] += 1
            
            # 최근 24시간 리포트
            for report in self.reports.values():
                if report.published_date > one_day_ago:
                    stats['recent_reports'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"위협 통계 조회 오류: {e}")
            return {}
    
    def _save_indicator_to_db(self, indicator: ThreatIndicator):
        """지표를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_indicators 
                (indicator_id, indicator_type, value, threat_type, confidence,
                 source, source_type, first_seen, last_seen, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                indicator.indicator_id,
                indicator.indicator_type,
                indicator.value,
                indicator.threat_type.value,
                indicator.confidence.value,
                indicator.source,
                indicator.source_type.value,
                indicator.first_seen.isoformat(),
                indicator.last_seen.isoformat(),
                json.dumps(indicator.tags),
                json.dumps(indicator.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"지표 데이터베이스 저장 오류: {e}")
    
    def _save_report_to_db(self, report: ThreatReport):
        """리포트를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_reports 
                (report_id, title, description, threat_type, severity, confidence,
                 source, source_type, published_date, tags, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.report_id,
                report.title,
                report.description,
                report.threat_type.value,
                report.severity,
                report.confidence.value,
                report.source,
                report.source_type.value,
                report.published_date.isoformat(),
                json.dumps(report.tags),
                report.content,
                json.dumps(report.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"리포트 데이터베이스 저장 오류: {e}")
    
    def _save_campaign_to_db(self, campaign: ThreatCampaign):
        """캠페인을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_campaigns 
                (campaign_id, name, description, threat_type, start_date, end_date,
                 targets, tactics, techniques, attribution, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                campaign.campaign_id,
                campaign.name,
                campaign.description,
                campaign.threat_type.value,
                campaign.start_date.isoformat(),
                campaign.end_date.isoformat() if campaign.end_date else None,
                json.dumps(campaign.targets),
                json.dumps(campaign.tactics),
                json.dumps(campaign.techniques),
                campaign.attribution,
                json.dumps(campaign.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"캠페인 데이터베이스 저장 오류: {e}")
    
    def _save_feed_to_db(self, feed: ThreatFeed):
        """피드를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_feeds 
                (feed_id, name, url, feed_type, source_type, update_interval,
                 last_update, enabled, credentials, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feed.feed_id,
                feed.name,
                feed.url,
                feed.feed_type,
                feed.source_type.value,
                feed.update_interval,
                feed.last_update.isoformat(),
                1 if feed.enabled else 0,
                json.dumps(feed.credentials),
                json.dumps(feed.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"피드 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            self.is_updating = False
            self.is_analyzing = False
            
            if self.http_session:
                asyncio.create_task(self.http_session.close())
            
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("위협 인텔리전스 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './threat_intelligence.db',
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 3
        }
    }
    
    # 위협 인텔리전스 시스템 생성
    ti_system = ThreatIntelligenceSystem(config)
    
    # 사용자 정의 피드 생성
    custom_feed = {
        'name': 'Custom Threat Feed',
        'url': 'https://example.com/threats.json',
        'feed_type': 'custom',
        'source_type': 'internal',
        'update_interval': 7200,
        'enabled': True,
        'credentials': {}
    }
    
    feed_id = ti_system.create_feed(custom_feed)
    print(f"피드 생성 완료: {feed_id}")
    
    # 사용자 정의 리포트 생성
    custom_report = {
        'title': 'Custom Threat Report',
        'description': '사용자 정의 위협 리포트',
        'threat_type': 'malware',
        'severity': 'high',
        'confidence': 'high',
        'source': 'internal',
        'source_type': 'internal',
        'tags': ['custom', 'malware'],
        'content': '위협 상세 내용...'
    }
    
    report_id = ti_system.create_report(custom_report)
    print(f"리포트 생성 완료: {report_id}")
    
    # 지표 검색
    results = ti_system.search_indicators('malware')
    print(f"검색 결과: {len(results)}개")
    
    # 위협 통계
    stats = ti_system.get_threat_statistics()
    print(f"총 지표 수: {stats['total_indicators']}")
    print(f"총 리포트 수: {stats['total_reports']}")
    
    # 피드 업데이트 시작
    ti_system.start_feed_updates() 