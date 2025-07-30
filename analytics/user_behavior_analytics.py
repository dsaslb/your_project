#!/usr/bin/env python3
"""
📊 Your Program 사용자 행동 분석 및 피드백 시스템

실시간으로 사용자 행동을 추적하고 분석하여 데이터 기반의
기능 개선 인사이트를 제공하는 지능형 분석 시스템입니다.

주요 기능:
- 실시간 사용자 행동 추적
- 사용자 여정 분석 (User Journey)
- A/B 테스트 프레임워크
- 피드백 수집 및 감정 분석
- 기능 사용률 분석
- 사용자 세그먼테이션
- 개인화 추천 엔진
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import sqlite3
import redis
import pandas as pd
import numpy as np
from pathlib import Path
import aiohttp
from collections import defaultdict, Counter
import hashlib

# ML/분석 라이브러리
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class UserEvent:
    """사용자 이벤트"""
    event_id: str
    user_id: str
    session_id: str
    event_type: str
    page_url: str
    element_id: Optional[str]
    event_data: Dict[str, Any]
    timestamp: datetime
    user_agent: str
    ip_address: str

@dataclass
class UserSession:
    """사용자 세션"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    page_views: int
    events_count: int
    duration_seconds: int
    entry_page: str
    exit_page: Optional[str]
    device_type: str
    browser: str
    referrer: Optional[str]

@dataclass
class UserFeedback:
    """사용자 피드백"""
    feedback_id: str
    user_id: str
    feedback_type: str  # 'rating', 'comment', 'suggestion', 'bug_report'
    content: str
    rating: Optional[int]
    category: str
    sentiment_score: float
    timestamp: datetime
    page_context: str
    resolved: bool

@dataclass
class ABTestVariant:
    """A/B 테스트 변형"""
    test_id: str
    variant_id: str
    name: str
    description: str
    traffic_allocation: float
    active: bool
    start_date: datetime
    end_date: Optional[datetime]
    conversion_metric: str

@dataclass
class UserSegment:
    """사용자 세그먼트"""
    segment_id: str
    name: str
    description: str
    criteria: Dict[str, Any]
    user_count: int
    characteristics: Dict[str, Any]
    created_date: datetime

class UserBehaviorAnalytics:
    """사용자 행동 분석 시스템"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=3)
        self.data_path = "analytics/user_analytics.db"
        
        # 데이터 저장소
        self.user_events: List[UserEvent] = []
        self.user_sessions: Dict[str, UserSession] = {}
        self.user_feedback: List[UserFeedback] = []
        self.ab_tests: Dict[str, ABTestVariant] = {}
        self.user_segments: Dict[str, UserSegment] = {}
        
        # 설정
        self.session_timeout = 1800  # 30분
        self.event_buffer_size = 10000
        self.analytics_enabled = True
        
        self.init_database()
        self.load_ab_tests()
        
    def init_database(self):
        """데이터베이스 초기화"""
        Path(self.data_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        # 사용자 이벤트 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT,
                session_id TEXT,
                event_type TEXT,
                page_url TEXT,
                element_id TEXT,
                event_data TEXT,
                timestamp TEXT,
                user_agent TEXT,
                ip_address TEXT
            )
        """)
        
        # 사용자 세션 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TEXT,
                end_time TEXT,
                page_views INTEGER,
                events_count INTEGER,
                duration_seconds INTEGER,
                entry_page TEXT,
                exit_page TEXT,
                device_type TEXT,
                browser TEXT,
                referrer TEXT
            )
        """)
        
        # 사용자 피드백 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id TEXT PRIMARY KEY,
                user_id TEXT,
                feedback_type TEXT,
                content TEXT,
                rating INTEGER,
                category TEXT,
                sentiment_score REAL,
                timestamp TEXT,
                page_context TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        # A/B 테스트 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ab_tests (
                test_id TEXT PRIMARY KEY,
                variant_id TEXT,
                name TEXT,
                description TEXT,
                traffic_allocation REAL,
                active BOOLEAN,
                start_date TEXT,
                end_date TEXT,
                conversion_metric TEXT
            )
        """)
        
        # 사용자 세그먼트 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_segments (
                segment_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                criteria TEXT,
                user_count INTEGER,
                characteristics TEXT,
                created_date TEXT
            )
        """)
        
        # 사용자 메트릭 집계 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_metrics_daily (
                date TEXT,
                total_users INTEGER,
                new_users INTEGER,
                active_users INTEGER,
                page_views INTEGER,
                sessions INTEGER,
                avg_session_duration REAL,
                bounce_rate REAL,
                PRIMARY KEY (date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def load_ab_tests(self):
        """A/B 테스트 로드"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM ab_tests WHERE active = 1")
            rows = cursor.fetchall()
            
            for row in rows:
                test = ABTestVariant(
                    test_id=row[0],
                    variant_id=row[1],
                    name=row[2],
                    description=row[3],
                    traffic_allocation=row[4],
                    active=bool(row[5]),
                    start_date=datetime.fromisoformat(row[6]),
                    end_date=datetime.fromisoformat(row[7]) if row[7] else None,
                    conversion_metric=row[8]
                )
                self.ab_tests[test.test_id] = test
            
            conn.close()
            logger.info(f"✅ {len(self.ab_tests)}개 A/B 테스트 로드 완료")
            
        except Exception as e:
            logger.error(f"A/B 테스트 로드 오류: {e}")
    
    async def start_analytics(self):
        """분석 시스템 시작"""
        logger.info("📊 사용자 행동 분석 시스템 시작")
        
        tasks = [
            asyncio.create_task(self._process_events()),
            asyncio.create_task(self._analyze_user_behavior()),
            asyncio.create_task(self._generate_insights()),
            asyncio.create_task(self._update_segments()),
            asyncio.create_task(self._cleanup_old_data()),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def track_event(self, event_data: Dict[str, Any]) -> str:
        """이벤트 추적"""
        try:
            event_id = str(uuid.uuid4())
            
            # 이벤트 객체 생성
            event = UserEvent(
                event_id=event_id,
                user_id=event_data.get('user_id'),
                session_id=event_data.get('session_id'),
                event_type=event_data.get('event_type'),
                page_url=event_data.get('page_url'),
                element_id=event_data.get('element_id'),
                event_data=event_data.get('data', {}),
                timestamp=datetime.now(),
                user_agent=event_data.get('user_agent', ''),
                ip_address=event_data.get('ip_address', '')
            )
            
            # 메모리 버퍼에 추가
            self.user_events.append(event)
            
            # 버퍼 크기 제한
            if len(self.user_events) > self.event_buffer_size:
                self.user_events = self.user_events[-self.event_buffer_size:]
            
            # 세션 업데이트
            await self._update_user_session(event)
            
            # A/B 테스트 할당
            if event.event_type in ['page_view', 'session_start']:
                await self._assign_ab_test(event.user_id, event.session_id)
            
            # 실시간 Redis 캐시
            await self._cache_event(event)
            
            return event_id
            
        except Exception as e:
            logger.error(f"이벤트 추적 오류: {e}")
            return ""
    
    async def _update_user_session(self, event: UserEvent):
        """사용자 세션 업데이트"""
        try:
            session_id = event.session_id
            
            if session_id in self.user_sessions:
                # 기존 세션 업데이트
                session = self.user_sessions[session_id]
                session.events_count += 1
                session.end_time = event.timestamp
                session.duration_seconds = int((event.timestamp - session.start_time).total_seconds())
                
                if event.event_type == 'page_view':
                    session.page_views += 1
                    session.exit_page = event.page_url
            
            else:
                # 새 세션 생성
                device_type, browser = self._parse_user_agent(event.user_agent)
                
                session = UserSession(
                    session_id=session_id,
                    user_id=event.user_id,
                    start_time=event.timestamp,
                    end_time=event.timestamp,
                    page_views=1 if event.event_type == 'page_view' else 0,
                    events_count=1,
                    duration_seconds=0,
                    entry_page=event.page_url,
                    exit_page=event.page_url,
                    device_type=device_type,
                    browser=browser,
                    referrer=event.event_data.get('referrer')
                )
                
                self.user_sessions[session_id] = session
            
        except Exception as e:
            logger.error(f"세션 업데이트 오류: {e}")
    
    def _parse_user_agent(self, user_agent: str) -> Tuple[str, str]:
        """User Agent 파싱"""
        try:
            ua_lower = user_agent.lower()
            
            # 디바이스 타입 감지
            if any(mobile in ua_lower for mobile in ['mobile', 'android', 'iphone', 'ipad']):
                device_type = 'mobile'
            elif 'tablet' in ua_lower:
                device_type = 'tablet'
            else:
                device_type = 'desktop'
            
            # 브라우저 감지
            if 'chrome' in ua_lower:
                browser = 'chrome'
            elif 'firefox' in ua_lower:
                browser = 'firefox'
            elif 'safari' in ua_lower:
                browser = 'safari'
            elif 'edge' in ua_lower:
                browser = 'edge'
            else:
                browser = 'other'
            
            return device_type, browser
            
        except Exception:
            return 'unknown', 'unknown'
    
    async def _assign_ab_test(self, user_id: str, session_id: str):
        """A/B 테스트 할당"""
        try:
            for test_id, test in self.ab_tests.items():
                if not test.active:
                    continue
                
                # 사용자 해시 기반 일관된 할당
                user_hash = int(hashlib.md5(f"{user_id}_{test_id}".encode()).hexdigest()[:8], 16)
                assignment_probability = (user_hash % 100) / 100.0
                
                if assignment_probability < test.traffic_allocation:
                    # A/B 테스트 참여
                    assignment_data = {
                        'user_id': user_id,
                        'session_id': session_id,
                        'test_id': test_id,
                        'variant_id': test.variant_id,
                        'assigned_at': datetime.now().isoformat()
                    }
                    
                    # Redis에 할당 정보 저장
                    self.redis_client.setex(
                        f"ab_test:{user_id}:{test_id}",
                        86400,  # 24시간
                        json.dumps(assignment_data)
                    )
                    
                    logger.info(f"A/B 테스트 할당: {user_id} -> {test.name} ({test.variant_id})")
            
        except Exception as e:
            logger.error(f"A/B 테스트 할당 오류: {e}")
    
    async def submit_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """피드백 제출"""
        try:
            feedback_id = str(uuid.uuid4())
            
            # 감정 분석
            sentiment_score = self._analyze_sentiment(feedback_data.get('content', ''))
            
            feedback = UserFeedback(
                feedback_id=feedback_id,
                user_id=feedback_data.get('user_id'),
                feedback_type=feedback_data.get('type', 'comment'),
                content=feedback_data.get('content', ''),
                rating=feedback_data.get('rating'),
                category=feedback_data.get('category', 'general'),
                sentiment_score=sentiment_score,
                timestamp=datetime.now(),
                page_context=feedback_data.get('page_context', ''),
                resolved=False
            )
            
            self.user_feedback.append(feedback)
            
            # 즉시 저장
            await self._save_feedback(feedback)
            
            # 부정적 피드백 즉시 알림
            if sentiment_score < -0.5 or (feedback.rating and feedback.rating <= 2):
                await self._send_feedback_alert(feedback)
            
            logger.info(f"피드백 수집: {feedback.feedback_type} - {sentiment_score:.2f}")
            
            return feedback_id
            
        except Exception as e:
            logger.error(f"피드백 제출 오류: {e}")
            return ""
    
    def _analyze_sentiment(self, text: str) -> float:
        """감정 분석"""
        try:
            if not text.strip():
                return 0.0
            
            blob = TextBlob(text)
            return blob.sentiment.polarity  # -1 (부정) ~ 1 (긍정)
            
        except Exception as e:
            logger.error(f"감정 분석 오류: {e}")
            return 0.0
    
    async def _process_events(self):
        """이벤트 처리 루프"""
        while self.analytics_enabled:
            try:
                if self.user_events:
                    # 배치로 이벤트 저장
                    events_to_save = self.user_events[-100:]  # 최근 100개
                    await self._save_events_batch(events_to_save)
                
                # 세션 정리 (타임아웃된 세션)
                await self._cleanup_sessions()
                
                await asyncio.sleep(60)  # 1분마다 처리
                
            except Exception as e:
                logger.error(f"이벤트 처리 오류: {e}")
                await asyncio.sleep(60)
    
    async def _save_events_batch(self, events: List[UserEvent]):
        """이벤트 배치 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            for event in events:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_events 
                    (event_id, user_id, session_id, event_type, page_url,
                     element_id, event_data, timestamp, user_agent, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.user_id,
                    event.session_id,
                    event.event_type,
                    event.page_url,
                    event.element_id,
                    json.dumps(event.event_data),
                    event.timestamp.isoformat(),
                    event.user_agent,
                    event.ip_address
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"이벤트 배치 저장 오류: {e}")
    
    async def _cleanup_sessions(self):
        """세션 정리"""
        try:
            current_time = datetime.now()
            timeout_sessions = []
            
            for session_id, session in self.user_sessions.items():
                if session.end_time:
                    time_diff = (current_time - session.end_time).total_seconds()
                    if time_diff > self.session_timeout:
                        timeout_sessions.append(session_id)
            
            # 타임아웃된 세션 저장 및 제거
            for session_id in timeout_sessions:
                session = self.user_sessions[session_id]
                await self._save_session(session)
                del self.user_sessions[session_id]
            
            if timeout_sessions:
                logger.info(f"세션 정리: {len(timeout_sessions)}개 세션 종료")
            
        except Exception as e:
            logger.error(f"세션 정리 오류: {e}")
    
    async def _save_session(self, session: UserSession):
        """세션 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_sessions 
                (session_id, user_id, start_time, end_time, page_views,
                 events_count, duration_seconds, entry_page, exit_page,
                 device_type, browser, referrer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.user_id,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else None,
                session.page_views,
                session.events_count,
                session.duration_seconds,
                session.entry_page,
                session.exit_page,
                session.device_type,
                session.browser,
                session.referrer
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"세션 저장 오류: {e}")
    
    async def _analyze_user_behavior(self):
        """사용자 행동 분석"""
        while self.analytics_enabled:
            try:
                # 사용자 여정 분석
                await self._analyze_user_journeys()
                
                # 기능 사용률 분석
                await self._analyze_feature_usage()
                
                # 페이지 성능 분석
                await self._analyze_page_performance()
                
                await asyncio.sleep(1800)  # 30분마다 분석
                
            except Exception as e:
                logger.error(f"사용자 행동 분석 오류: {e}")
                await asyncio.sleep(1800)
    
    async def _analyze_user_journeys(self):
        """사용자 여정 분석"""
        try:
            # 최근 24시간 데이터 분석
            recent_sessions = [
                session for session in self.user_sessions.values()
                if session.start_time > datetime.now() - timedelta(days=1)
            ]
            
            if not recent_sessions:
                return
            
            # 공통 사용자 여정 패턴 찾기
            journey_patterns = defaultdict(int)
            
            for session in recent_sessions:
                # 세션의 페이지 순서 추적 (간단화된 버전)
                session_events = [
                    event for event in self.user_events
                    if event.session_id == session.session_id and event.event_type == 'page_view'
                ]
                
                if len(session_events) >= 2:
                    # 페이지 전환 패턴
                    for i in range(len(session_events) - 1):
                        from_page = self._simplify_url(session_events[i].page_url)
                        to_page = self._simplify_url(session_events[i + 1].page_url)
                        pattern = f"{from_page} -> {to_page}"
                        journey_patterns[pattern] += 1
            
            # 상위 패턴 분석
            top_patterns = sorted(journey_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Redis에 캐시
            pattern_data = {
                'patterns': top_patterns,
                'total_sessions': len(recent_sessions),
                'analyzed_at': datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                "user_journey_patterns",
                3600,  # 1시간
                json.dumps(pattern_data)
            )
            
            logger.info(f"사용자 여정 분석 완료: {len(top_patterns)}개 주요 패턴 식별")
            
        except Exception as e:
            logger.error(f"사용자 여정 분석 오류: {e}")
    
    def _simplify_url(self, url: str) -> str:
        """URL 단순화"""
        try:
            # 쿼리 파라미터 제거하고 주요 경로만 추출
            if '?' in url:
                url = url.split('?')[0]
            
            path_parts = url.split('/')
            if len(path_parts) >= 2:
                return f"/{path_parts[-2]}/{path_parts[-1]}" if len(path_parts) > 2 else f"/{path_parts[-1]}"
            
            return url
            
        except Exception:
            return url
    
    async def _analyze_feature_usage(self):
        """기능 사용률 분석"""
        try:
            # 최근 7일간 기능별 사용 통계
            week_ago = datetime.now() - timedelta(days=7)
            recent_events = [
                event for event in self.user_events
                if event.timestamp > week_ago and event.event_type == 'click'
            ]
            
            # 기능별 클릭 수 집계
            feature_usage = defaultdict(int)
            user_feature_usage = defaultdict(set)
            
            for event in recent_events:
                if event.element_id:
                    feature_usage[event.element_id] += 1
                    user_feature_usage[event.element_id].add(event.user_id)
            
            # 사용률 계산
            total_users = len(set(event.user_id for event in recent_events))
            feature_stats = {}
            
            for feature, clicks in feature_usage.items():
                unique_users = len(user_feature_usage[feature])
                adoption_rate = (unique_users / total_users * 100) if total_users > 0 else 0
                
                feature_stats[feature] = {
                    'total_clicks': clicks,
                    'unique_users': unique_users,
                    'adoption_rate': adoption_rate,
                    'avg_clicks_per_user': clicks / unique_users if unique_users > 0 else 0
                }
            
            # 상위/하위 기능 식별
            sorted_features = sorted(feature_stats.items(), key=lambda x: x[1]['adoption_rate'], reverse=True)
            
            usage_analysis = {
                'top_features': sorted_features[:10],
                'underused_features': [f for f in sorted_features if f[1]['adoption_rate'] < 10][-10:],
                'total_features': len(feature_stats),
                'analyzed_period': '7_days',
                'generated_at': datetime.now().isoformat()
            }
            
            # Redis에 캐시
            self.redis_client.setex(
                "feature_usage_analysis",
                3600,
                json.dumps(usage_analysis, default=str)
            )
            
            logger.info(f"기능 사용률 분석 완료: {len(feature_stats)}개 기능 분석")
            
        except Exception as e:
            logger.error(f"기능 사용률 분석 오류: {e}")
    
    async def _analyze_page_performance(self):
        """페이지 성능 분석"""
        try:
            # 페이지별 성능 메트릭 분석
            page_metrics = defaultdict(list)
            
            for event in self.user_events:
                if event.event_type == 'page_view' and 'load_time' in event.event_data:
                    page = self._simplify_url(event.page_url)
                    load_time = event.event_data.get('load_time', 0)
                    if load_time > 0:
                        page_metrics[page].append(load_time)
            
            # 페이지별 통계 계산
            page_performance = {}
            
            for page, load_times in page_metrics.items():
                if len(load_times) >= 5:  # 최소 5개 데이터 필요
                    page_performance[page] = {
                        'avg_load_time': np.mean(load_times),
                        'median_load_time': np.median(load_times),
                        'p95_load_time': np.percentile(load_times, 95),
                        'sample_count': len(load_times),
                        'slow_loads': len([t for t in load_times if t > 3000])  # 3초 이상
                    }
            
            # 성능 문제 페이지 식별
            slow_pages = {
                page: stats for page, stats in page_performance.items()
                if stats['avg_load_time'] > 2000  # 2초 이상
            }
            
            performance_analysis = {
                'page_performance': page_performance,
                'slow_pages': slow_pages,
                'total_pages_analyzed': len(page_performance),
                'generated_at': datetime.now().isoformat()
            }
            
            # Redis에 캐시
            self.redis_client.setex(
                "page_performance_analysis",
                3600,
                json.dumps(performance_analysis, default=str)
            )
            
            if slow_pages:
                logger.warning(f"성능 문제 페이지 감지: {len(slow_pages)}개 페이지")
            
        except Exception as e:
            logger.error(f"페이지 성능 분석 오류: {e}")
    
    async def _generate_insights(self):
        """인사이트 생성"""
        while self.analytics_enabled:
            try:
                # 사용자 만족도 분석
                await self._analyze_user_satisfaction()
                
                # 이탈률 분석
                await self._analyze_bounce_rate()
                
                # 전환율 분석
                await self._analyze_conversion_rates()
                
                # A/B 테스트 결과 분석
                await self._analyze_ab_test_results()
                
                await asyncio.sleep(3600)  # 1시간마다 인사이트 생성
                
            except Exception as e:
                logger.error(f"인사이트 생성 오류: {e}")
                await asyncio.sleep(3600)
    
    async def _analyze_user_satisfaction(self):
        """사용자 만족도 분석"""
        try:
            # 최근 30일 피드백 분석
            month_ago = datetime.now() - timedelta(days=30)
            recent_feedback = [
                fb for fb in self.user_feedback
                if fb.timestamp > month_ago
            ]
            
            if not recent_feedback:
                return
            
            # 평점 통계
            ratings = [fb.rating for fb in recent_feedback if fb.rating is not None]
            sentiment_scores = [fb.sentiment_score for fb in recent_feedback]
            
            satisfaction_metrics = {
                'total_feedback_count': len(recent_feedback),
                'avg_rating': np.mean(ratings) if ratings else None,
                'rating_distribution': dict(Counter(ratings)) if ratings else {},
                'avg_sentiment': np.mean(sentiment_scores) if sentiment_scores else 0,
                'positive_feedback_ratio': len([s for s in sentiment_scores if s > 0.2]) / len(sentiment_scores) if sentiment_scores else 0,
                'negative_feedback_ratio': len([s for s in sentiment_scores if s < -0.2]) / len(sentiment_scores) if sentiment_scores else 0
            }
            
            # 카테고리별 만족도
            category_satisfaction = defaultdict(list)
            for fb in recent_feedback:
                if fb.rating is not None:
                    category_satisfaction[fb.category].append(fb.rating)
            
            category_stats = {
                category: {
                    'avg_rating': np.mean(ratings),
                    'count': len(ratings)
                }
                for category, ratings in category_satisfaction.items()
            }
            
            satisfaction_analysis = {
                'overall_metrics': satisfaction_metrics,
                'category_breakdown': category_stats,
                'period': '30_days',
                'generated_at': datetime.now().isoformat()
            }
            
            # Redis에 캐시
            self.redis_client.setex(
                "user_satisfaction_analysis",
                3600,
                json.dumps(satisfaction_analysis, default=str)
            )
            
            # 만족도 저하 알림
            if satisfaction_metrics['avg_rating'] and satisfaction_metrics['avg_rating'] < 3.0:
                await self._send_satisfaction_alert(satisfaction_analysis)
            
        except Exception as e:
            logger.error(f"사용자 만족도 분석 오류: {e}")
    
    async def _analyze_bounce_rate(self):
        """이탈률 분석"""
        try:
            # 최근 7일간 세션 분석
            week_ago = datetime.now() - timedelta(days=7)
            recent_sessions = [
                session for session in self.user_sessions.values()
                if session.start_time > week_ago
            ]
            
            if not recent_sessions:
                return
            
            # 이탈률 계산 (1페이지만 보고 떠난 세션 비율)
            single_page_sessions = len([s for s in recent_sessions if s.page_views <= 1])
            bounce_rate = (single_page_sessions / len(recent_sessions)) * 100
            
            # 페이지별 이탈률
            page_bounce_rates = defaultdict(lambda: {'sessions': 0, 'bounces': 0})
            
            for session in recent_sessions:
                entry_page = self._simplify_url(session.entry_page)
                page_bounce_rates[entry_page]['sessions'] += 1
                if session.page_views <= 1:
                    page_bounce_rates[entry_page]['bounces'] += 1
            
            # 페이지별 이탈률 계산
            page_bounce_stats = {}
            for page, stats in page_bounce_rates.items():
                if stats['sessions'] >= 10:  # 최소 10세션
                    bounce_rate_page = (stats['bounces'] / stats['sessions']) * 100
                    page_bounce_stats[page] = {
                        'bounce_rate': bounce_rate_page,
                        'sessions': stats['sessions'],
                        'bounces': stats['bounces']
                    }
            
            # 높은 이탈률 페이지
            high_bounce_pages = {
                page: stats for page, stats in page_bounce_stats.items()
                if stats['bounce_rate'] > 70  # 70% 이상
            }
            
            bounce_analysis = {
                'overall_bounce_rate': bounce_rate,
                'total_sessions': len(recent_sessions),
                'page_bounce_rates': page_bounce_stats,
                'high_bounce_pages': high_bounce_pages,
                'period': '7_days',
                'generated_at': datetime.now().isoformat()
            }
            
            # Redis에 캐시
            self.redis_client.setex(
                "bounce_rate_analysis",
                3600,
                json.dumps(bounce_analysis, default=str)
            )
            
            if bounce_rate > 60:  # 60% 이상 이탈률
                logger.warning(f"높은 이탈률 감지: {bounce_rate:.1f}%")
            
        except Exception as e:
            logger.error(f"이탈률 분석 오류: {e}")
    
    async def _analyze_conversion_rates(self):
        """전환율 분석"""
        try:
            # 목표 이벤트 정의 (회원가입, 구매, 문의 등)
            conversion_events = ['signup', 'purchase', 'contact', 'subscribe']
            
            # 최근 30일 전환율 분석
            month_ago = datetime.now() - timedelta(days=30)
            recent_sessions = [
                session for session in self.user_sessions.values()
                if session.start_time > month_ago
            ]
            
            if not recent_sessions:
                return
            
            conversion_stats = {}
            
            for conversion_event in conversion_events:
                # 해당 이벤트를 발생시킨 세션들
                converted_sessions = set()
                
                for event in self.user_events:
                    if (event.timestamp > month_ago and 
                        event.event_type == conversion_event):
                        converted_sessions.add(event.session_id)
                
                conversion_rate = (len(converted_sessions) / len(recent_sessions)) * 100
                
                conversion_stats[conversion_event] = {
                    'conversion_rate': conversion_rate,
                    'converted_sessions': len(converted_sessions),
                    'total_sessions': len(recent_sessions)
                }
            
            # 전환 퍼널 분석 (간단화된 버전)
            funnel_steps = ['page_view', 'click', 'form_submit', 'purchase']
            funnel_analysis = {}
            
            for i, step in enumerate(funnel_steps):
                step_sessions = set()
                for event in self.user_events:
                    if (event.timestamp > month_ago and 
                        event.event_type == step):
                        step_sessions.add(event.session_id)
                
                funnel_analysis[step] = {
                    'sessions': len(step_sessions),
                    'conversion_rate': (len(step_sessions) / len(recent_sessions)) * 100 if i == 0 else None
                }
                
                # 이전 단계 대비 전환율
                if i > 0:
                    prev_step_sessions = funnel_analysis[funnel_steps[i-1]]['sessions']
                    if prev_step_sessions > 0:
                        step_conversion = (len(step_sessions) / prev_step_sessions) * 100
                        funnel_analysis[step]['step_conversion_rate'] = step_conversion
            
            conversion_analysis = {
                'conversion_rates': conversion_stats,
                'funnel_analysis': funnel_analysis,
                'period': '30_days',
                'generated_at': datetime.now().isoformat()
            }
            
            # Redis에 캐시
            self.redis_client.setex(
                "conversion_analysis",
                3600,
                json.dumps(conversion_analysis, default=str)
            )
            
        except Exception as e:
            logger.error(f"전환율 분석 오류: {e}")
    
    async def _analyze_ab_test_results(self):
        """A/B 테스트 결과 분석"""
        try:
            for test_id, test in self.ab_tests.items():
                if not test.active:
                    continue
                
                # 테스트 참여자 데이터 수집
                test_participants = []
                
                # Redis에서 테스트 할당 정보 조회
                pattern = f"ab_test:*:{test_id}"
                keys = self.redis_client.keys(pattern)
                
                for key in keys:
                    assignment_data = self.redis_client.get(key)
                    if assignment_data:
                        participant = json.loads(assignment_data)
                        test_participants.append(participant)
                
                if len(test_participants) < 10:  # 최소 참여자 수
                    continue
                
                # 전환 이벤트 수집
                conversion_events = []
                for participant in test_participants:
                    user_id = participant['user_id']
                    session_id = participant['session_id']
                    
                    # 해당 사용자의 전환 이벤트 찾기
                    for event in self.user_events:
                        if (event.user_id == user_id and 
                            event.session_id == session_id and
                            event.event_type == test.conversion_metric):
                            conversion_events.append({
                                'user_id': user_id,
                                'variant_id': participant['variant_id'],
                                'converted': True
                            })
                            break
                    else:
                        conversion_events.append({
                            'user_id': user_id,
                            'variant_id': participant['variant_id'],
                            'converted': False
                        })
                
                # 변형별 결과 분석
                variant_results = defaultdict(lambda: {'participants': 0, 'conversions': 0})
                
                for event in conversion_events:
                    variant_id = event['variant_id']
                    variant_results[variant_id]['participants'] += 1
                    if event['converted']:
                        variant_results[variant_id]['conversions'] += 1
                
                # 전환율 계산
                for variant_id, results in variant_results.items():
                    if results['participants'] > 0:
                        results['conversion_rate'] = (results['conversions'] / results['participants']) * 100
                    else:
                        results['conversion_rate'] = 0
                
                test_results = {
                    'test_id': test_id,
                    'test_name': test.name,
                    'variant_results': dict(variant_results),
                    'total_participants': len(test_participants),
                    'analyzed_at': datetime.now().isoformat()
                }
                
                # Redis에 결과 저장
                self.redis_client.setex(
                    f"ab_test_results:{test_id}",
                    3600,
                    json.dumps(test_results, default=str)
                )
                
                logger.info(f"A/B 테스트 결과 분석: {test.name} - {len(test_participants)}명 참여")
            
        except Exception as e:
            logger.error(f"A/B 테스트 결과 분석 오류: {e}")
    
    async def _update_segments(self):
        """사용자 세그먼트 업데이트"""
        while self.analytics_enabled:
            try:
                # 행동 기반 세그먼테이션
                await self._segment_users_by_behavior()
                
                # 가치 기반 세그먼테이션
                await self._segment_users_by_value()
                
                await asyncio.sleep(86400)  # 24시간마다 세그먼트 업데이트
                
            except Exception as e:
                logger.error(f"세그먼트 업데이트 오류: {e}")
                await asyncio.sleep(86400)
    
    async def _segment_users_by_behavior(self):
        """행동 기반 사용자 세그먼테이션"""
        try:
            # 최근 30일 사용자 행동 데이터 수집
            month_ago = datetime.now() - timedelta(days=30)
            
            user_behavior = defaultdict(lambda: {
                'sessions': 0,
                'page_views': 0,
                'total_time': 0,
                'events': 0,
                'last_activity': None
            })
            
            # 세션 데이터 집계
            for session in self.user_sessions.values():
                if session.start_time > month_ago:
                    user_id = session.user_id
                    user_behavior[user_id]['sessions'] += 1
                    user_behavior[user_id]['page_views'] += session.page_views
                    user_behavior[user_id]['total_time'] += session.duration_seconds
                    user_behavior[user_id]['events'] += session.events_count
                    
                    if (user_behavior[user_id]['last_activity'] is None or
                        session.end_time > user_behavior[user_id]['last_activity']):
                        user_behavior[user_id]['last_activity'] = session.end_time
            
            # 세그먼트 기준 정의
            segments = {
                'power_users': [],      # 높은 활동량
                'regular_users': [],    # 중간 활동량
                'casual_users': [],     # 낮은 활동량
                'inactive_users': []    # 비활성 사용자
            }
            
            for user_id, behavior in user_behavior.items():
                avg_session_time = behavior['total_time'] / behavior['sessions'] if behavior['sessions'] > 0 else 0
                
                # 세그먼트 분류 로직
                if behavior['sessions'] >= 10 and avg_session_time >= 300:  # 10회 이상, 평균 5분 이상
                    segments['power_users'].append(user_id)
                elif behavior['sessions'] >= 3 and avg_session_time >= 120:  # 3회 이상, 평균 2분 이상
                    segments['regular_users'].append(user_id)
                elif behavior['sessions'] >= 1:
                    segments['casual_users'].append(user_id)
                else:
                    segments['inactive_users'].append(user_id)
            
            # 세그먼트 저장
            for segment_name, user_list in segments.items():
                if user_list:
                    segment = UserSegment(
                        segment_id=f"behavior_{segment_name}",
                        name=f"행동 기반 - {segment_name}",
                        description=f"{segment_name} 사용자 그룹",
                        criteria={'type': 'behavior', 'segment': segment_name},
                        user_count=len(user_list),
                        characteristics={'users': user_list[:100]},  # 최대 100명까지 저장
                        created_date=datetime.now()
                    )
                    
                    self.user_segments[segment.segment_id] = segment
                    await self._save_segment(segment)
            
            logger.info(f"행동 기반 세그먼테이션 완료: {sum(len(users) for users in segments.values())}명 분류")
            
        except Exception as e:
            logger.error(f"행동 기반 세그먼테이션 오류: {e}")
    
    async def _segment_users_by_value(self):
        """가치 기반 사용자 세그먼테이션"""
        try:
            # 피드백 점수 기반 가치 세그먼테이션
            user_satisfaction = defaultdict(list)
            
            for feedback in self.user_feedback:
                if feedback.rating is not None:
                    user_satisfaction[feedback.user_id].append(feedback.rating)
            
            # 만족도 기반 세그먼트
            satisfaction_segments = {
                'promoters': [],      # 평점 4-5
                'passives': [],       # 평점 3
                'detractors': []      # 평점 1-2
            }
            
            for user_id, ratings in user_satisfaction.items():
                avg_rating = np.mean(ratings)
                
                if avg_rating >= 4:
                    satisfaction_segments['promoters'].append(user_id)
                elif avg_rating >= 3:
                    satisfaction_segments['passives'].append(user_id)
                else:
                    satisfaction_segments['detractors'].append(user_id)
            
            # 세그먼트 저장
            for segment_name, user_list in satisfaction_segments.items():
                if user_list:
                    segment = UserSegment(
                        segment_id=f"satisfaction_{segment_name}",
                        name=f"만족도 기반 - {segment_name}",
                        description=f"{segment_name} 사용자 그룹",
                        criteria={'type': 'satisfaction', 'segment': segment_name},
                        user_count=len(user_list),
                        characteristics={'users': user_list[:100]},
                        created_date=datetime.now()
                    )
                    
                    self.user_segments[segment.segment_id] = segment
                    await self._save_segment(segment)
            
        except Exception as e:
            logger.error(f"가치 기반 세그먼테이션 오류: {e}")
    
    async def _cleanup_old_data(self):
        """오래된 데이터 정리"""
        while self.analytics_enabled:
            try:
                # 30일 이상 된 이벤트 삭제
                cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
                
                conn = sqlite3.connect(self.data_path)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM user_events WHERE timestamp < ?", (cutoff_date,))
                cursor.execute("DELETE FROM user_sessions WHERE start_time < ?", (cutoff_date,))
                
                deleted_events = cursor.rowcount
                conn.commit()
                conn.close()
                
                # 메모리 데이터도 정리
                cutoff_time = datetime.now() - timedelta(days=7)
                self.user_events = [
                    event for event in self.user_events 
                    if event.timestamp > cutoff_time
                ]
                
                if deleted_events > 0:
                    logger.info(f"오래된 데이터 정리: {deleted_events}개 이벤트 삭제")
                
                await asyncio.sleep(86400)  # 24시간마다 정리
                
            except Exception as e:
                logger.error(f"데이터 정리 오류: {e}")
                await asyncio.sleep(86400)
    
    # 저장 및 캐시 메서드들
    async def _cache_event(self, event: UserEvent):
        """이벤트 Redis 캐시"""
        try:
            event_data = {
                'event_id': event.event_id,
                'user_id': event.user_id,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat()
            }
            
            # 최근 이벤트 리스트 유지
            self.redis_client.lpush("recent_events", json.dumps(event_data))
            self.redis_client.ltrim("recent_events", 0, 999)  # 최근 1000개만 유지
            
            # 실시간 통계 업데이트
            current_hour = datetime.now().strftime("%Y%m%d%H")
            self.redis_client.incr(f"events_hour:{current_hour}")
            self.redis_client.expire(f"events_hour:{current_hour}", 86400)  # 24시간 유지
            
        except Exception as e:
            logger.error(f"이벤트 캐시 오류: {e}")
    
    async def _save_feedback(self, feedback: UserFeedback):
        """피드백 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_feedback 
                (feedback_id, user_id, feedback_type, content, rating,
                 category, sentiment_score, timestamp, page_context, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.feedback_id,
                feedback.user_id,
                feedback.feedback_type,
                feedback.content,
                feedback.rating,
                feedback.category,
                feedback.sentiment_score,
                feedback.timestamp.isoformat(),
                feedback.page_context,
                feedback.resolved
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"피드백 저장 오류: {e}")
    
    async def _save_segment(self, segment: UserSegment):
        """세그먼트 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_segments 
                (segment_id, name, description, criteria, user_count,
                 characteristics, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                segment.segment_id,
                segment.name,
                segment.description,
                json.dumps(segment.criteria),
                segment.user_count,
                json.dumps(segment.characteristics),
                segment.created_date.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"세그먼트 저장 오류: {e}")
    
    # 알림 메서드들
    async def _send_feedback_alert(self, feedback: UserFeedback):
        """피드백 알림"""
        try:
            alert_data = {
                'type': 'negative_feedback',
                'feedback_id': feedback.feedback_id,
                'user_id': feedback.user_id,
                'sentiment_score': feedback.sentiment_score,
                'rating': feedback.rating,
                'content': feedback.content[:200],
                'timestamp': feedback.timestamp.isoformat()
            }
            
            self.redis_client.publish("feedback_alerts", json.dumps(alert_data))
            
        except Exception as e:
            logger.error(f"피드백 알림 오류: {e}")
    
    async def _send_satisfaction_alert(self, analysis: Dict[str, Any]):
        """만족도 알림"""
        try:
            alert_data = {
                'type': 'low_satisfaction',
                'avg_rating': analysis['overall_metrics']['avg_rating'],
                'negative_ratio': analysis['overall_metrics']['negative_feedback_ratio'],
                'period': analysis['period'],
                'timestamp': datetime.now().isoformat()
            }
            
            self.redis_client.publish("satisfaction_alerts", json.dumps(alert_data))
            
        except Exception as e:
            logger.error(f"만족도 알림 오류: {e}")
    
    # 분석 리포트 생성
    async def generate_analytics_report(self) -> Dict[str, Any]:
        """분석 리포트 생성"""
        try:
            # 캐시된 분석 결과 수집
            cached_analyses = {}
            
            analysis_keys = [
                "user_journey_patterns",
                "feature_usage_analysis", 
                "page_performance_analysis",
                "user_satisfaction_analysis",
                "bounce_rate_analysis",
                "conversion_analysis"
            ]
            
            for key in analysis_keys:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    cached_analyses[key] = json.loads(cached_data)
            
            # 실시간 통계
            current_hour = datetime.now().strftime("%Y%m%d%H")
            current_events = self.redis_client.get(f"events_hour:{current_hour}") or 0
            
            # 종합 리포트
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'current_hour_events': int(current_events),
                'active_sessions': len(self.user_sessions),
                'total_segments': len(self.user_segments),
                'active_ab_tests': len([t for t in self.ab_tests.values() if t.active]),
                'cached_analyses': cached_analyses,
                'recent_feedback_count': len([f for f in self.user_feedback if f.timestamp > datetime.now() - timedelta(hours=24)]),
                'system_status': 'active' if self.analytics_enabled else 'inactive'
            }
            
            return report
            
        except Exception as e:
            logger.error(f"분석 리포트 생성 오류: {e}")
            return {}

# 메인 실행
async def main():
    """메인 실행 함수"""
    analytics = UserBehaviorAnalytics()
    
    try:
        logger.info("📊 사용자 행동 분석 시스템 시작")
        await analytics.start_analytics()
    except KeyboardInterrupt:
        logger.info("⏹️ 시스템 종료")
        analytics.analytics_enabled = False
    except Exception as e:
        logger.error(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 