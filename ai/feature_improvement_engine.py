#!/usr/bin/env python3
"""
🚀 Your Program 자동화된 기능 개선 추천 엔진

사용자 행동 데이터, 피드백, 성능 메트릭을 종합 분석하여
데이터 기반의 기능 개선 사항을 자동으로 식별하고 우선순위를 매겨
개발팀에 실행 가능한 추천사항을 제공하는 AI 시스템입니다.

주요 기능:
- 다차원 데이터 분석 (행동, 피드백, 성능, 비즈니스)
- 기능 개선 우선순위 매트릭스
- 자동화된 A/B 테스트 제안
- ROI 기반 개선 효과 예측
- 실행 가능한 개발 태스크 생성
- 지속적 학습 및 개선
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import sqlite3
import redis
from pathlib import Path
import uuid
from collections import defaultdict, Counter

# ML/AI 라이브러리
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
from sklearn.cluster import KMeans
import networkx as nx
from textblob import TextBlob
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ImprovementOpportunity:
    """개선 기회"""
    opportunity_id: str
    title: str
    description: str
    category: str  # 'performance', 'usability', 'feature', 'bug_fix'
    priority_score: float
    impact_estimate: str  # 'low', 'medium', 'high', 'critical'
    effort_estimate: str  # 'small', 'medium', 'large', 'epic'
    confidence: float
    data_sources: List[str]
    evidence: Dict[str, Any]
    recommendations: List[str]
    success_metrics: List[str]
    created_date: datetime
    status: str  # 'identified', 'approved', 'in_progress', 'completed', 'rejected'

@dataclass
class FeatureUsagePattern:
    """기능 사용 패턴"""
    feature_id: str
    usage_frequency: float
    user_adoption_rate: float
    user_satisfaction: float
    performance_impact: float
    business_value: float
    support_requests: int
    error_rate: float
    abandonment_rate: float

@dataclass
class UserPainPoint:
    """사용자 고충점"""
    pain_point_id: str
    description: str
    affected_users: int
    severity: str
    frequency: int
    related_features: List[str]
    sentiment_score: float
    resolution_difficulty: str
    business_impact: float

@dataclass
class ImprovementTask:
    """개선 작업"""
    task_id: str
    opportunity_id: str
    title: str
    description: str
    task_type: str  # 'development', 'design', 'research', 'analysis'
    estimated_hours: int
    required_skills: List[str]
    dependencies: List[str]
    acceptance_criteria: List[str]
    priority: int
    assigned_to: Optional[str]
    status: str

class FeatureImprovementEngine:
    """기능 개선 추천 엔진"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=4)
        self.data_path = "ai/improvement_engine.db"
        
        # 데이터 저장소
        self.improvement_opportunities: Dict[str, ImprovementOpportunity] = {}
        self.feature_patterns: Dict[str, FeatureUsagePattern] = {}
        self.pain_points: Dict[str, UserPainPoint] = {}
        self.improvement_tasks: Dict[str, ImprovementTask] = {}
        
        # ML 모델
        self.priority_model = None
        self.impact_model = None
        self.effort_model = None
        
        # 설정
        self.analysis_enabled = True
        self.min_data_points = 10
        self.confidence_threshold = 0.7
        
        self.init_database()
        self.load_models()
        
    def init_database(self):
        """데이터베이스 초기화"""
        Path(self.data_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        # 개선 기회 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS improvement_opportunities (
                opportunity_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                category TEXT,
                priority_score REAL,
                impact_estimate TEXT,
                effort_estimate TEXT,
                confidence REAL,
                data_sources TEXT,
                evidence TEXT,
                recommendations TEXT,
                success_metrics TEXT,
                created_date TEXT,
                status TEXT
            )
        """)
        
        # 기능 사용 패턴 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_usage_patterns (
                feature_id TEXT PRIMARY KEY,
                usage_frequency REAL,
                user_adoption_rate REAL,
                user_satisfaction REAL,
                performance_impact REAL,
                business_value REAL,
                support_requests INTEGER,
                error_rate REAL,
                abandonment_rate REAL,
                last_updated TEXT
            )
        """)
        
        # 사용자 고충점 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_pain_points (
                pain_point_id TEXT PRIMARY KEY,
                description TEXT,
                affected_users INTEGER,
                severity TEXT,
                frequency INTEGER,
                related_features TEXT,
                sentiment_score REAL,
                resolution_difficulty TEXT,
                business_impact REAL,
                identified_date TEXT
            )
        """)
        
        # 개선 작업 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS improvement_tasks (
                task_id TEXT PRIMARY KEY,
                opportunity_id TEXT,
                title TEXT,
                description TEXT,
                task_type TEXT,
                estimated_hours INTEGER,
                required_skills TEXT,
                dependencies TEXT,
                acceptance_criteria TEXT,
                priority INTEGER,
                assigned_to TEXT,
                status TEXT,
                created_date TEXT
            )
        """)
        
        # 개선 효과 추적 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS improvement_results (
                result_id TEXT PRIMARY KEY,
                opportunity_id TEXT,
                implemented_date TEXT,
                before_metrics TEXT,
                after_metrics TEXT,
                actual_impact TEXT,
                roi_calculation REAL,
                lessons_learned TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def load_models(self):
        """ML 모델 로드"""
        try:
            model_dir = Path("ai/models")
            
            # 우선순위 예측 모델
            if (model_dir / "priority_model.pkl").exists():
                import joblib
                self.priority_model = joblib.load(model_dir / "priority_model.pkl")
                logger.info("✅ 우선순위 예측 모델 로드 완료")
            
            # 임팩트 예측 모델
            if (model_dir / "impact_model.pkl").exists():
                import joblib
                self.impact_model = joblib.load(model_dir / "impact_model.pkl")
                logger.info("✅ 임팩트 예측 모델 로드 완료")
                
        except Exception as e:
            logger.warning(f"모델 로드 중 오류: {e}")
            logger.info("새로운 모델을 학습합니다...")
    
    async def start_improvement_engine(self):
        """개선 엔진 시작"""
        logger.info("🚀 기능 개선 추천 엔진 시작")
        
        tasks = [
            asyncio.create_task(self._analyze_user_data()),
            asyncio.create_task(self._identify_pain_points()),
            asyncio.create_task(self._generate_improvement_opportunities()),
            asyncio.create_task(self._prioritize_opportunities()),
            asyncio.create_task(self._create_improvement_tasks()),
            asyncio.create_task(self._monitor_implementation_results()),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _analyze_user_data(self):
        """사용자 데이터 분석"""
        while self.analysis_enabled:
            try:
                # 다양한 데이터 소스에서 데이터 수집
                await self._collect_analytics_data()
                await self._collect_performance_data()
                await self._collect_feedback_data()
                
                # 기능별 사용 패턴 분석
                await self._analyze_feature_usage_patterns()
                
                await asyncio.sleep(3600)  # 1시간마다 분석
                
            except Exception as e:
                logger.error(f"사용자 데이터 분석 오류: {e}")
                await asyncio.sleep(3600)
    
    async def _collect_analytics_data(self):
        """분석 데이터 수집"""
        try:
            # Redis에서 사용자 행동 분석 데이터 조회
            analytics_keys = [
                "feature_usage_analysis",
                "user_journey_patterns", 
                "bounce_rate_analysis",
                "conversion_analysis"
            ]
            
            analytics_data = {}
            for key in analytics_keys:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    analytics_data[key] = json.loads(cached_data)
            
            # 기능별 사용률 분석
            if 'feature_usage_analysis' in analytics_data:
                usage_data = analytics_data['feature_usage_analysis']
                
                for feature_data in usage_data.get('top_features', []):
                    feature_id, stats = feature_data
                    
                    pattern = FeatureUsagePattern(
                        feature_id=feature_id,
                        usage_frequency=stats.get('total_clicks', 0),
                        user_adoption_rate=stats.get('adoption_rate', 0),
                        user_satisfaction=0.0,  # 나중에 피드백 데이터로 업데이트
                        performance_impact=0.0,  # 나중에 성능 데이터로 업데이트
                        business_value=0.0,     # 나중에 비즈니스 메트릭으로 업데이트
                        support_requests=0,
                        error_rate=0.0,
                        abandonment_rate=0.0
                    )
                    
                    self.feature_patterns[feature_id] = pattern
                
                # 사용률이 낮은 기능들도 분석
                for feature_data in usage_data.get('underused_features', []):
                    feature_id, stats = feature_data
                    
                    if feature_id not in self.feature_patterns:
                        pattern = FeatureUsagePattern(
                            feature_id=feature_id,
                            usage_frequency=stats.get('total_clicks', 0),
                            user_adoption_rate=stats.get('adoption_rate', 0),
                            user_satisfaction=0.0,
                            performance_impact=0.0,
                            business_value=0.0,
                            support_requests=0,
                            error_rate=0.0,
                            abandonment_rate=100.0 - stats.get('adoption_rate', 0)  # 추정
                        )
                        
                        self.feature_patterns[feature_id] = pattern
            
        except Exception as e:
            logger.error(f"분석 데이터 수집 오류: {e}")
    
    async def _collect_performance_data(self):
        """성능 데이터 수집"""
        try:
            # Redis에서 성능 분석 데이터 조회
            performance_keys = [
                "page_performance_analysis",
                "query_optimizer_stats"
            ]
            
            performance_data = {}
            for key in performance_keys:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    performance_data[key] = json.loads(cached_data)
            
            # 페이지별 성능 데이터를 기능과 연결
            if 'page_performance_analysis' in performance_data:
                page_perf = performance_data['page_performance_analysis']
                
                for page, stats in page_perf.get('page_performance', {}).items():
                    # 페이지를 기능으로 매핑 (간단화된 버전)
                    feature_id = self._map_page_to_feature(page)
                    
                    if feature_id in self.feature_patterns:
                        # 성능 임팩트 점수 계산 (로딩 시간 기반)
                        avg_load_time = stats.get('avg_load_time', 0)
                        performance_impact = min(avg_load_time / 1000.0, 10.0)  # 0-10 스케일
                        
                        self.feature_patterns[feature_id].performance_impact = performance_impact
            
        except Exception as e:
            logger.error(f"성능 데이터 수집 오류: {e}")
    
    def _map_page_to_feature(self, page_url: str) -> str:
        """페이지 URL을 기능 ID로 매핑"""
        # 간단한 매핑 로직 (실제 환경에서는 더 정교한 매핑 필요)
        url_to_feature = {
            '/dashboard': 'dashboard_main',
            '/admin': 'admin_panel',
            '/reports': 'reporting_system',
            '/settings': 'settings_management',
            '/users': 'user_management',
            '/analytics': 'analytics_dashboard'
        }
        
        for url_pattern, feature_id in url_to_feature.items():
            if url_pattern in page_url:
                return feature_id
        
        # 기본 매핑
        return page_url.replace('/', '_').replace('-', '_')
    
    async def _collect_feedback_data(self):
        """피드백 데이터 수집"""
        try:
            # 사용자 만족도 분석 데이터 조회
            satisfaction_data = self.redis_client.get("user_satisfaction_analysis")
            if satisfaction_data:
                satisfaction_info = json.loads(satisfaction_data)
                
                # 카테고리별 만족도를 기능별 만족도로 매핑
                category_ratings = satisfaction_info.get('category_breakdown', {})
                
                for category, stats in category_ratings.items():
                    feature_id = self._map_category_to_feature(category)
                    
                    if feature_id in self.feature_patterns:
                        avg_rating = stats.get('avg_rating', 3.0)
                        # 1-5 점수를 0-1 점수로 정규화
                        satisfaction_score = (avg_rating - 1) / 4.0
                        
                        self.feature_patterns[feature_id].user_satisfaction = satisfaction_score
            
        except Exception as e:
            logger.error(f"피드백 데이터 수집 오류: {e}")
    
    def _map_category_to_feature(self, category: str) -> str:
        """피드백 카테고리를 기능 ID로 매핑"""
        category_to_feature = {
            'dashboard': 'dashboard_main',
            'admin': 'admin_panel',
            'reports': 'reporting_system',
            'settings': 'settings_management',
            'users': 'user_management',
            'analytics': 'analytics_dashboard',
            'general': 'overall_system'
        }
        
        return category_to_feature.get(category, category.replace(' ', '_').lower())
    
    async def _analyze_feature_usage_patterns(self):
        """기능 사용 패턴 분석"""
        try:
            for feature_id, pattern in self.feature_patterns.items():
                # 비즈니스 가치 계산
                business_value = self._calculate_business_value(pattern)
                pattern.business_value = business_value
                
                # 패턴을 데이터베이스에 저장
                await self._save_feature_pattern(pattern)
            
            logger.info(f"기능 사용 패턴 분석 완료: {len(self.feature_patterns)}개 기능")
            
        except Exception as e:
            logger.error(f"기능 사용 패턴 분석 오류: {e}")
    
    def _calculate_business_value(self, pattern: FeatureUsagePattern) -> float:
        """비즈니스 가치 계산"""
        try:
            # 다양한 요소를 고려한 비즈니스 가치 점수
            factors = [
                pattern.usage_frequency * 0.3,        # 사용 빈도
                pattern.user_adoption_rate * 0.25,    # 사용자 채택률
                pattern.user_satisfaction * 0.25,     # 사용자 만족도
                (10 - pattern.performance_impact) * 0.1,  # 성능 (역수)
                (100 - pattern.abandonment_rate) * 0.1    # 이탈률 (역수)
            ]
            
            # 가중 평균으로 비즈니스 가치 계산
            business_value = sum(factors) / len(factors)
            
            return min(max(business_value, 0.0), 10.0)  # 0-10 범위로 정규화
            
        except Exception as e:
            logger.error(f"비즈니스 가치 계산 오류: {e}")
            return 5.0  # 기본값
    
    async def _identify_pain_points(self):
        """사용자 고충점 식별"""
        while self.analysis_enabled:
            try:
                # 피드백 기반 고충점 식별
                await self._identify_feedback_pain_points()
                
                # 성능 기반 고충점 식별
                await self._identify_performance_pain_points()
                
                # 사용성 기반 고충점 식별
                await self._identify_usability_pain_points()
                
                await asyncio.sleep(7200)  # 2시간마다 식별
                
            except Exception as e:
                logger.error(f"고충점 식별 오류: {e}")
                await asyncio.sleep(7200)
    
    async def _identify_feedback_pain_points(self):
        """피드백 기반 고충점 식별"""
        try:
            # 부정적 피드백 분석
            satisfaction_data = self.redis_client.get("user_satisfaction_analysis")
            if not satisfaction_data:
                return
            
            satisfaction_info = json.loads(satisfaction_data)
            overall_metrics = satisfaction_info.get('overall_metrics', {})
            
            # 낮은 평점이나 부정적 감정의 피드백 식별
            negative_ratio = overall_metrics.get('negative_feedback_ratio', 0)
            avg_rating = overall_metrics.get('avg_rating', 5.0)
            
            if negative_ratio > 0.3 or (avg_rating and avg_rating < 3.0):
                pain_point_id = f"feedback_negative_{int(datetime.now().timestamp())}"
                
                pain_point = UserPainPoint(
                    pain_point_id=pain_point_id,
                    description="사용자 만족도 저하 - 부정적 피드백 증가",
                    affected_users=int(overall_metrics.get('total_feedback_count', 0) * negative_ratio),
                    severity="high" if negative_ratio > 0.5 else "medium",
                    frequency=int(overall_metrics.get('total_feedback_count', 0)),
                    related_features=["overall_system"],
                    sentiment_score=overall_metrics.get('avg_sentiment', 0),
                    resolution_difficulty="medium",
                    business_impact=negative_ratio * 10  # 0-10 스케일
                )
                
                self.pain_points[pain_point_id] = pain_point
                await self._save_pain_point(pain_point)
                
                logger.warning(f"고충점 식별: {pain_point.description}")
            
        except Exception as e:
            logger.error(f"피드백 기반 고충점 식별 오류: {e}")
    
    async def _identify_performance_pain_points(self):
        """성능 기반 고충점 식별"""
        try:
            # 느린 페이지 식별
            performance_data = self.redis_client.get("page_performance_analysis")
            if not performance_data:
                return
            
            perf_info = json.loads(performance_data)
            slow_pages = perf_info.get('slow_pages', {})
            
            for page, stats in slow_pages.items():
                if stats.get('avg_load_time', 0) > 3000:  # 3초 이상
                    pain_point_id = f"performance_{page}_{int(datetime.now().timestamp())}"
                    
                    feature_id = self._map_page_to_feature(page)
                    
                    pain_point = UserPainPoint(
                        pain_point_id=pain_point_id,
                        description=f"페이지 로딩 속도 저하: {page}",
                        affected_users=stats.get('sample_count', 0),
                        severity="high" if stats.get('avg_load_time', 0) > 5000 else "medium",
                        frequency=stats.get('sample_count', 0),
                        related_features=[feature_id],
                        sentiment_score=-0.5,  # 성능 문제는 부정적
                        resolution_difficulty="medium",
                        business_impact=min(stats.get('avg_load_time', 0) / 1000.0, 10.0)
                    )
                    
                    self.pain_points[pain_point_id] = pain_point
                    await self._save_pain_point(pain_point)
                    
                    logger.warning(f"성능 고충점 식별: {pain_point.description}")
            
        except Exception as e:
            logger.error(f"성능 기반 고충점 식별 오류: {e}")
    
    async def _identify_usability_pain_points(self):
        """사용성 기반 고충점 식별"""
        try:
            # 높은 이탈률 페이지 식별
            bounce_data = self.redis_client.get("bounce_rate_analysis")
            if not bounce_data:
                return
            
            bounce_info = json.loads(bounce_data)
            high_bounce_pages = bounce_info.get('high_bounce_pages', {})
            
            for page, stats in high_bounce_pages.items():
                if stats.get('bounce_rate', 0) > 80:  # 80% 이상 이탈률
                    pain_point_id = f"usability_{page}_{int(datetime.now().timestamp())}"
                    
                    feature_id = self._map_page_to_feature(page)
                    
                    pain_point = UserPainPoint(
                        pain_point_id=pain_point_id,
                        description=f"높은 이탈률 페이지: {page}",
                        affected_users=stats.get('sessions', 0),
                        severity="high" if stats.get('bounce_rate', 0) > 90 else "medium",
                        frequency=stats.get('bounces', 0),
                        related_features=[feature_id],
                        sentiment_score=-0.3,  # 사용성 문제는 부정적
                        resolution_difficulty="medium",
                        business_impact=stats.get('bounce_rate', 0) / 10.0  # 0-10 스케일
                    )
                    
                    self.pain_points[pain_point_id] = pain_point
                    await self._save_pain_point(pain_point)
                    
                    logger.warning(f"사용성 고충점 식별: {pain_point.description}")
            
        except Exception as e:
            logger.error(f"사용성 기반 고충점 식별 오류: {e}")
    
    async def _generate_improvement_opportunities(self):
        """개선 기회 생성"""
        while self.analysis_enabled:
            try:
                # 기능 사용 패턴 기반 개선 기회
                await self._generate_usage_based_opportunities()
                
                # 고충점 기반 개선 기회
                await self._generate_pain_point_based_opportunities()
                
                # 성능 기반 개선 기회
                await self._generate_performance_based_opportunities()
                
                # A/B 테스트 기회
                await self._generate_ab_test_opportunities()
                
                await asyncio.sleep(10800)  # 3시간마다 생성
                
            except Exception as e:
                logger.error(f"개선 기회 생성 오류: {e}")
                await asyncio.sleep(10800)
    
    async def _generate_usage_based_opportunities(self):
        """사용 패턴 기반 개선 기회 생성"""
        try:
            for feature_id, pattern in self.feature_patterns.items():
                opportunities = []
                
                # 낮은 채택률 기능 개선
                if pattern.user_adoption_rate < 20:  # 20% 미만
                    opportunities.append({
                        'title': f'기능 채택률 개선: {feature_id}',
                        'description': f'{feature_id} 기능의 사용자 채택률이 {pattern.user_adoption_rate:.1f}%로 낮습니다.',
                        'category': 'usability',
                        'recommendations': [
                            '사용자 온보딩 개선',
                            'UI/UX 재설계',
                            '기능 발견성 향상',
                            '사용자 가이드 추가'
                        ]
                    })
                
                # 높은 이탈률 기능 개선
                if pattern.abandonment_rate > 50:  # 50% 이상
                    opportunities.append({
                        'title': f'기능 이탈률 감소: {feature_id}',
                        'description': f'{feature_id} 기능의 이탈률이 {pattern.abandonment_rate:.1f}%로 높습니다.',
                        'category': 'usability',
                        'recommendations': [
                            '사용자 플로우 최적화',
                            '복잡성 감소',
                            '에러 처리 개선',
                            '피드백 메커니즘 강화'
                        ]
                    })
                
                # 낮은 만족도 기능 개선
                if pattern.user_satisfaction < 0.6:  # 60% 미만
                    opportunities.append({
                        'title': f'사용자 만족도 향상: {feature_id}',
                        'description': f'{feature_id} 기능의 사용자 만족도가 {pattern.user_satisfaction*100:.1f}%로 낮습니다.',
                        'category': 'feature',
                        'recommendations': [
                            '사용자 피드백 심층 분석',
                            '기능 재설계',
                            '성능 최적화',
                            '사용자 테스트 수행'
                        ]
                    })
                
                # 개선 기회 저장
                for opp_data in opportunities:
                    await self._create_improvement_opportunity(
                        feature_id, pattern, opp_data
                    )
            
        except Exception as e:
            logger.error(f"사용 패턴 기반 개선 기회 생성 오류: {e}")
    
    async def _generate_pain_point_based_opportunities(self):
        """고충점 기반 개선 기회 생성"""
        try:
            for pain_point_id, pain_point in self.pain_points.items():
                opportunity_id = f"pain_point_{pain_point_id}"
                
                # 이미 존재하는 기회인지 확인
                if opportunity_id in self.improvement_opportunities:
                    continue
                
                # 심각도에 따른 우선순위 계산
                severity_scores = {'low': 3, 'medium': 6, 'high': 9, 'critical': 10}
                base_priority = severity_scores.get(pain_point.severity, 5)
                
                # 영향받는 사용자 수를 고려한 우선순위 조정
                user_impact_factor = min(pain_point.affected_users / 100.0, 2.0)
                priority_score = base_priority * (1 + user_impact_factor)
                
                opportunity = ImprovementOpportunity(
                    opportunity_id=opportunity_id,
                    title=f"고충점 해결: {pain_point.description}",
                    description=f"사용자 고충점을 해결하여 {pain_point.affected_users}명의 사용자 경험을 개선합니다.",
                    category="bug_fix" if "오류" in pain_point.description else "usability",
                    priority_score=priority_score,
                    impact_estimate=pain_point.severity,
                    effort_estimate=pain_point.resolution_difficulty,
                    confidence=0.8,
                    data_sources=["user_feedback", "analytics"],
                    evidence={
                        "affected_users": pain_point.affected_users,
                        "severity": pain_point.severity,
                        "frequency": pain_point.frequency,
                        "sentiment_score": pain_point.sentiment_score
                    },
                    recommendations=self._generate_pain_point_recommendations(pain_point),
                    success_metrics=[
                        "사용자 만족도 증가",
                        "고객 지원 요청 감소",
                        "기능 사용률 증가"
                    ],
                    created_date=datetime.now(),
                    status="identified"
                )
                
                self.improvement_opportunities[opportunity_id] = opportunity
                await self._save_improvement_opportunity(opportunity)
                
                logger.info(f"고충점 기반 개선 기회 생성: {opportunity.title}")
            
        except Exception as e:
            logger.error(f"고충점 기반 개선 기회 생성 오류: {e}")
    
    def _generate_pain_point_recommendations(self, pain_point: UserPainPoint) -> List[str]:
        """고충점에 대한 추천사항 생성"""
        recommendations = []
        
        if "성능" in pain_point.description or "속도" in pain_point.description:
            recommendations.extend([
                "페이지 로딩 속도 최적화",
                "데이터베이스 쿼리 최적화",
                "캐싱 전략 구현",
                "CDN 활용"
            ])
        
        if "이탈률" in pain_point.description:
            recommendations.extend([
                "사용자 플로우 분석 및 개선",
                "페이지 콘텐츠 최적화",
                "CTA 버튼 개선",
                "로딩 인디케이터 추가"
            ])
        
        if "만족도" in pain_point.description:
            recommendations.extend([
                "사용자 인터뷰 수행",
                "UI/UX 재설계",
                "기능 사용성 테스트",
                "피드백 수집 강화"
            ])
        
        # 기본 추천사항
        if not recommendations:
            recommendations = [
                "근본 원인 분석",
                "사용자 데이터 심층 분석",
                "A/B 테스트 수행",
                "점진적 개선 적용"
            ]
        
        return recommendations
    
    async def _generate_performance_based_opportunities(self):
        """성능 기반 개선 기회 생성"""
        try:
            # 성능 문제가 있는 기능들 식별
            for feature_id, pattern in self.feature_patterns.items():
                if pattern.performance_impact > 3.0:  # 3초 이상
                    opportunity_id = f"performance_{feature_id}"
                    
                    if opportunity_id in self.improvement_opportunities:
                        continue
                    
                    # 성능 임팩트에 따른 우선순위 계산
                    priority_score = min(pattern.performance_impact * 2, 10.0)
                    
                    opportunity = ImprovementOpportunity(
                        opportunity_id=opportunity_id,
                        title=f"성능 최적화: {feature_id}",
                        description=f"{feature_id} 기능의 성능을 개선하여 사용자 경험을 향상시킵니다.",
                        category="performance",
                        priority_score=priority_score,
                        impact_estimate="high" if pattern.performance_impact > 5 else "medium",
                        effort_estimate="medium",
                        confidence=0.9,
                        data_sources=["performance_monitoring"],
                        evidence={
                            "performance_impact": pattern.performance_impact,
                            "usage_frequency": pattern.usage_frequency,
                            "user_adoption_rate": pattern.user_adoption_rate
                        },
                        recommendations=[
                            "코드 최적화",
                            "데이터베이스 인덱스 추가",
                            "캐싱 구현",
                            "비동기 처리 도입",
                            "리소스 압축"
                        ],
                        success_metrics=[
                            "페이지 로딩 시간 50% 감소",
                            "사용자 만족도 증가",
                            "이탈률 감소"
                        ],
                        created_date=datetime.now(),
                        status="identified"
                    )
                    
                    self.improvement_opportunities[opportunity_id] = opportunity
                    await self._save_improvement_opportunity(opportunity)
                    
                    logger.info(f"성능 기반 개선 기회 생성: {opportunity.title}")
            
        except Exception as e:
            logger.error(f"성능 기반 개선 기회 생성 오류: {e}")
    
    async def _generate_ab_test_opportunities(self):
        """A/B 테스트 기회 생성"""
        try:
            # 불확실한 개선 사항에 대한 A/B 테스트 제안
            for opportunity_id, opportunity in self.improvement_opportunities.items():
                if (opportunity.confidence < 0.8 and 
                    opportunity.status == "identified" and
                    "ab_test" not in opportunity_id):
                    
                    ab_test_opportunity_id = f"ab_test_{opportunity_id}"
                    
                    if ab_test_opportunity_id in self.improvement_opportunities:
                        continue
                    
                    ab_test_opportunity = ImprovementOpportunity(
                        opportunity_id=ab_test_opportunity_id,
                        title=f"A/B 테스트: {opportunity.title}",
                        description=f"{opportunity.title}에 대한 A/B 테스트를 수행하여 효과를 검증합니다.",
                        category="research",
                        priority_score=opportunity.priority_score * 0.8,  # 약간 낮은 우선순위
                        impact_estimate="medium",
                        effort_estimate="small",
                        confidence=0.9,
                        data_sources=opportunity.data_sources,
                        evidence=opportunity.evidence,
                        recommendations=[
                            "A/B 테스트 설계",
                            "테스트 그룹 분할",
                            "성공 메트릭 정의",
                            "통계적 유의성 검증",
                            "결과 분석 및 적용"
                        ],
                        success_metrics=[
                            "통계적 유의한 개선 효과 확인",
                            "사용자 행동 변화 측정",
                            "ROI 계산"
                        ],
                        created_date=datetime.now(),
                        status="identified"
                    )
                    
                    self.improvement_opportunities[ab_test_opportunity_id] = ab_test_opportunity
                    await self._save_improvement_opportunity(ab_test_opportunity)
                    
                    logger.info(f"A/B 테스트 기회 생성: {ab_test_opportunity.title}")
            
        except Exception as e:
            logger.error(f"A/B 테스트 기회 생성 오류: {e}")
    
    async def _create_improvement_opportunity(self, feature_id: str, pattern: FeatureUsagePattern, opp_data: Dict[str, Any]):
        """개선 기회 생성"""
        try:
            opportunity_id = f"usage_{feature_id}_{opp_data['category']}"
            
            if opportunity_id in self.improvement_opportunities:
                return
            
            # 우선순위 점수 계산
            priority_score = self._calculate_priority_score(pattern, opp_data)
            
            opportunity = ImprovementOpportunity(
                opportunity_id=opportunity_id,
                title=opp_data['title'],
                description=opp_data['description'],
                category=opp_data['category'],
                priority_score=priority_score,
                impact_estimate=self._estimate_impact(pattern),
                effort_estimate=self._estimate_effort(opp_data['category']),
                confidence=0.7,
                data_sources=["user_analytics", "feature_usage"],
                evidence={
                    "usage_frequency": pattern.usage_frequency,
                    "user_adoption_rate": pattern.user_adoption_rate,
                    "user_satisfaction": pattern.user_satisfaction,
                    "abandonment_rate": pattern.abandonment_rate
                },
                recommendations=opp_data['recommendations'],
                success_metrics=[
                    "사용자 채택률 증가",
                    "사용자 만족도 향상",
                    "이탈률 감소"
                ],
                created_date=datetime.now(),
                status="identified"
            )
            
            self.improvement_opportunities[opportunity_id] = opportunity
            await self._save_improvement_opportunity(opportunity)
            
        except Exception as e:
            logger.error(f"개선 기회 생성 오류: {e}")
    
    def _calculate_priority_score(self, pattern: FeatureUsagePattern, opp_data: Dict[str, Any]) -> float:
        """우선순위 점수 계산"""
        try:
            # 비즈니스 가치 기반 점수
            business_impact = pattern.business_value
            
            # 사용자 영향 점수
            user_impact = (pattern.usage_frequency / 100.0) * pattern.user_adoption_rate / 100.0
            
            # 문제 심각도 점수
            severity_scores = {
                'usability': 7,
                'performance': 8,
                'feature': 6,
                'bug_fix': 9
            }
            severity_score = severity_scores.get(opp_data['category'], 5)
            
            # 가중 평균으로 우선순위 계산
            priority_score = (
                business_impact * 0.4 +
                user_impact * 0.3 +
                severity_score * 0.3
            )
            
            return min(max(priority_score, 0.0), 10.0)
            
        except Exception as e:
            logger.error(f"우선순위 점수 계산 오류: {e}")
            return 5.0
    
    def _estimate_impact(self, pattern: FeatureUsagePattern) -> str:
        """임팩트 추정"""
        if pattern.business_value > 8:
            return "high"
        elif pattern.business_value > 5:
            return "medium"
        else:
            return "low"
    
    def _estimate_effort(self, category: str) -> str:
        """노력 추정"""
        effort_mapping = {
            'usability': 'medium',
            'performance': 'large',
            'feature': 'large',
            'bug_fix': 'small',
            'research': 'small'
        }
        return effort_mapping.get(category, 'medium')
    
    async def _prioritize_opportunities(self):
        """개선 기회 우선순위 매기기"""
        while self.analysis_enabled:
            try:
                if not self.improvement_opportunities:
                    await asyncio.sleep(14400)  # 4시간
                    continue
                
                # ML 모델을 사용한 우선순위 재계산
                await self._ml_prioritize_opportunities()
                
                # 우선순위 매트릭스 생성
                await self._create_priority_matrix()
                
                await asyncio.sleep(14400)  # 4시간마다 우선순위 재계산
                
            except Exception as e:
                logger.error(f"우선순위 매기기 오류: {e}")
                await asyncio.sleep(14400)
    
    async def _ml_prioritize_opportunities(self):
        """ML을 사용한 우선순위 계산"""
        try:
            if not self.priority_model:
                await self._train_priority_model()
            
            if not self.priority_model:
                return
            
            # 기회들의 특성 벡터 생성
            features = []
            opportunity_ids = []
            
            for opp_id, opportunity in self.improvement_opportunities.items():
                feature_vector = self._extract_opportunity_features(opportunity)
                features.append(feature_vector)
                opportunity_ids.append(opp_id)
            
            if not features:
                return
            
            # 우선순위 예측
            features_array = np.array(features)
            predicted_priorities = self.priority_model.predict(features_array)
            
            # 예측된 우선순위로 업데이트
            for i, opp_id in enumerate(opportunity_ids):
                self.improvement_opportunities[opp_id].priority_score = predicted_priorities[i]
            
            logger.info(f"ML 기반 우선순위 재계산 완료: {len(opportunity_ids)}개 기회")
            
        except Exception as e:
            logger.error(f"ML 우선순위 계산 오류: {e}")
    
    def _extract_opportunity_features(self, opportunity: ImprovementOpportunity) -> List[float]:
        """개선 기회에서 특성 벡터 추출"""
        try:
            # 카테고리 인코딩
            category_encoding = {
                'performance': 1, 'usability': 2, 'feature': 3, 'bug_fix': 4, 'research': 5
            }
            category_score = category_encoding.get(opportunity.category, 0)
            
            # 임팩트 인코딩
            impact_encoding = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            impact_score = impact_encoding.get(opportunity.impact_estimate, 0)
            
            # 노력 인코딩
            effort_encoding = {'small': 1, 'medium': 2, 'large': 3, 'epic': 4}
            effort_score = effort_encoding.get(opportunity.effort_estimate, 0)
            
            # 증거 데이터에서 특성 추출
            evidence = opportunity.evidence
            usage_frequency = evidence.get('usage_frequency', 0)
            user_adoption_rate = evidence.get('user_adoption_rate', 0)
            user_satisfaction = evidence.get('user_satisfaction', 0.5)
            affected_users = evidence.get('affected_users', 0)
            
            # 특성 벡터
            features = [
                category_score,
                impact_score,
                effort_score,
                opportunity.confidence,
                usage_frequency / 100.0,  # 정규화
                user_adoption_rate / 100.0,  # 정규화
                user_satisfaction,
                min(affected_users / 1000.0, 1.0),  # 정규화
                len(opportunity.recommendations),
                (datetime.now() - opportunity.created_date).days
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"특성 벡터 추출 오류: {e}")
            return [0.0] * 10  # 기본값
    
    async def _train_priority_model(self):
        """우선순위 예측 모델 학습"""
        try:
            # 실제 환경에서는 과거 데이터를 사용
            # 여기서는 시뮬레이션 데이터 생성
            training_data = self._generate_training_data()
            
            if len(training_data) < 20:  # 최소 데이터 필요
                logger.warning("우선순위 모델 학습을 위한 데이터 부족")
                return
            
            # 특성과 라벨 분리
            X = np.array([data['features'] for data in training_data])
            y = np.array([data['priority'] for data in training_data])
            
            # 모델 학습
            self.priority_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.priority_model.fit(X, y)
            
            # 모델 저장
            import joblib
            model_dir = Path("ai/models")
            model_dir.mkdir(exist_ok=True)
            joblib.dump(self.priority_model, model_dir / "priority_model.pkl")
            
            logger.info("우선순위 예측 모델 학습 완료")
            
        except Exception as e:
            logger.error(f"우선순위 모델 학습 오류: {e}")
    
    def _generate_training_data(self) -> List[Dict[str, Any]]:
        """학습 데이터 생성 (시뮬레이션)"""
        # 실제 환경에서는 과거 개선 사항의 실제 결과를 사용
        training_data = []
        
        # 샘플 데이터 생성
        for i in range(50):
            features = [
                np.random.randint(1, 6),    # category
                np.random.randint(1, 5),    # impact
                np.random.randint(1, 5),    # effort
                np.random.uniform(0.5, 1.0), # confidence
                np.random.uniform(0, 1),    # usage_frequency
                np.random.uniform(0, 1),    # user_adoption_rate
                np.random.uniform(0, 1),    # user_satisfaction
                np.random.uniform(0, 1),    # affected_users
                np.random.randint(3, 8),    # recommendations_count
                np.random.randint(0, 30)    # days_since_created
            ]
            
            # 우선순위 계산 (간단한 휴리스틱)
            priority = min(10, max(1, 
                features[1] * 2 +  # impact
                (5 - features[2]) +  # effort (역수)
                features[3] * 3 +  # confidence
                features[4] * 2    # usage_frequency
            ))
            
            training_data.append({
                'features': features,
                'priority': int(priority)
            })
        
        return training_data
    
    async def _create_priority_matrix(self):
        """우선순위 매트릭스 생성"""
        try:
            # 임팩트 vs 노력 매트릭스
            matrix = {
                'high_impact_low_effort': [],    # Quick Wins
                'high_impact_high_effort': [],   # Major Projects
                'low_impact_low_effort': [],     # Fill-ins
                'low_impact_high_effort': []     # Thankless Tasks
            }
            
            for opp_id, opportunity in self.improvement_opportunities.items():
                impact = opportunity.impact_estimate
                effort = opportunity.effort_estimate
                
                if impact in ['high', 'critical'] and effort in ['small', 'medium']:
                    matrix['high_impact_low_effort'].append(opp_id)
                elif impact in ['high', 'critical'] and effort in ['large', 'epic']:
                    matrix['high_impact_high_effort'].append(opp_id)
                elif impact in ['low', 'medium'] and effort in ['small', 'medium']:
                    matrix['low_impact_low_effort'].append(opp_id)
                else:
                    matrix['low_impact_high_effort'].append(opp_id)
            
            # Redis에 매트릭스 저장
            self.redis_client.setex(
                "improvement_priority_matrix",
                7200,  # 2시간
                json.dumps(matrix)
            )
            
            logger.info(f"우선순위 매트릭스 생성 완료: {sum(len(v) for v in matrix.values())}개 기회")
            
        except Exception as e:
            logger.error(f"우선순위 매트릭스 생성 오류: {e}")
    
    async def _create_improvement_tasks(self):
        """개선 작업 생성"""
        while self.analysis_enabled:
            try:
                # 승인된 개선 기회에 대한 작업 생성
                for opp_id, opportunity in self.improvement_opportunities.items():
                    if opportunity.status == "approved" and opp_id not in [task.opportunity_id for task in self.improvement_tasks.values()]:
                        await self._generate_tasks_for_opportunity(opportunity)
                
                await asyncio.sleep(21600)  # 6시간마다 작업 생성
                
            except Exception as e:
                logger.error(f"개선 작업 생성 오류: {e}")
                await asyncio.sleep(21600)
    
    async def _generate_tasks_for_opportunity(self, opportunity: ImprovementOpportunity):
        """개선 기회에 대한 작업 생성"""
        try:
            tasks = []
            
            # 카테고리별 작업 템플릿
            if opportunity.category == "performance":
                tasks = [
                    {
                        'title': f'성능 분석: {opportunity.title}',
                        'description': '성능 병목점 상세 분석 및 개선 방안 도출',
                        'task_type': 'analysis',
                        'estimated_hours': 8,
                        'required_skills': ['performance_analysis', 'profiling'],
                        'priority': 1
                    },
                    {
                        'title': f'성능 최적화 구현: {opportunity.title}',
                        'description': '식별된 성능 문제 해결 및 최적화 구현',
                        'task_type': 'development',
                        'estimated_hours': 24,
                        'required_skills': ['backend_development', 'database_optimization'],
                        'priority': 2
                    },
                    {
                        'title': f'성능 테스트: {opportunity.title}',
                        'description': '최적화 효과 검증 및 성능 테스트',
                        'task_type': 'testing',
                        'estimated_hours': 8,
                        'required_skills': ['performance_testing', 'qa'],
                        'priority': 3
                    }
                ]
            
            elif opportunity.category == "usability":
                tasks = [
                    {
                        'title': f'사용성 연구: {opportunity.title}',
                        'description': '사용자 인터뷰 및 사용성 테스트 수행',
                        'task_type': 'research',
                        'estimated_hours': 16,
                        'required_skills': ['ux_research', 'user_testing'],
                        'priority': 1
                    },
                    {
                        'title': f'UI/UX 재설계: {opportunity.title}',
                        'description': '개선된 사용자 인터페이스 설계',
                        'task_type': 'design',
                        'estimated_hours': 20,
                        'required_skills': ['ui_design', 'ux_design'],
                        'priority': 2
                    },
                    {
                        'title': f'UI 구현: {opportunity.title}',
                        'description': '새로운 UI 구현 및 통합',
                        'task_type': 'development',
                        'estimated_hours': 32,
                        'required_skills': ['frontend_development', 'ui_implementation'],
                        'priority': 3
                    }
                ]
            
            elif opportunity.category == "feature":
                tasks = [
                    {
                        'title': f'기능 요구사항 분석: {opportunity.title}',
                        'description': '기능 개선 요구사항 상세 분석',
                        'task_type': 'analysis',
                        'estimated_hours': 12,
                        'required_skills': ['business_analysis', 'requirements_gathering'],
                        'priority': 1
                    },
                    {
                        'title': f'기능 개발: {opportunity.title}',
                        'description': '기능 개선사항 개발 및 구현',
                        'task_type': 'development',
                        'estimated_hours': 40,
                        'required_skills': ['full_stack_development'],
                        'priority': 2
                    }
                ]
            
            # 작업 생성 및 저장
            for i, task_data in enumerate(tasks):
                task_id = f"{opportunity.opportunity_id}_task_{i+1}"
                
                task = ImprovementTask(
                    task_id=task_id,
                    opportunity_id=opportunity.opportunity_id,
                    title=task_data['title'],
                    description=task_data['description'],
                    task_type=task_data['task_type'],
                    estimated_hours=task_data['estimated_hours'],
                    required_skills=task_data['required_skills'],
                    dependencies=[f"{opportunity.opportunity_id}_task_{j}" for j in range(1, task_data['priority'])],
                    acceptance_criteria=self._generate_acceptance_criteria(task_data),
                    priority=task_data['priority'],
                    assigned_to=None,
                    status="created"
                )
                
                self.improvement_tasks[task_id] = task
                await self._save_improvement_task(task)
            
            logger.info(f"개선 작업 생성 완료: {opportunity.title} - {len(tasks)}개 작업")
            
        except Exception as e:
            logger.error(f"개선 기회 작업 생성 오류: {e}")
    
    def _generate_acceptance_criteria(self, task_data: Dict[str, Any]) -> List[str]:
        """작업 완료 기준 생성"""
        criteria = []
        
        task_type = task_data['task_type']
        
        if task_type == "analysis":
            criteria = [
                "상세 분석 보고서 작성 완료",
                "개선 방안 3개 이상 도출",
                "예상 효과 및 리스크 분석 완료"
            ]
        elif task_type == "development":
            criteria = [
                "코드 구현 완료",
                "단위 테스트 통과",
                "코드 리뷰 완료",
                "문서화 완료"
            ]
        elif task_type == "design":
            criteria = [
                "디자인 시안 3개 이상 제작",
                "사용자 테스트 수행",
                "최종 디자인 승인 완료"
            ]
        elif task_type == "research":
            criteria = [
                "사용자 인터뷰 10명 이상 수행",
                "연구 결과 보고서 작성",
                "개선 방향 제시"
            ]
        elif task_type == "testing":
            criteria = [
                "테스트 케이스 작성 완료",
                "모든 테스트 통과",
                "성능 개선 효과 측정 완료"
            ]
        
        return criteria
    
    async def _monitor_implementation_results(self):
        """구현 결과 모니터링"""
        while self.analysis_enabled:
            try:
                # 완료된 개선 사항의 효과 측정
                await self._measure_improvement_impact()
                
                # 학습 데이터 업데이트
                await self._update_learning_data()
                
                await asyncio.sleep(43200)  # 12시간마다 모니터링
                
            except Exception as e:
                logger.error(f"구현 결과 모니터링 오류: {e}")
                await asyncio.sleep(43200)
    
    async def _measure_improvement_impact(self):
        """개선 효과 측정"""
        try:
            for opp_id, opportunity in self.improvement_opportunities.items():
                if opportunity.status == "completed":
                    # 구현 전후 메트릭 비교
                    impact_result = await self._calculate_actual_impact(opportunity)
                    
                    if impact_result:
                        await self._save_improvement_result(opportunity, impact_result)
                        logger.info(f"개선 효과 측정 완료: {opportunity.title}")
            
        except Exception as e:
            logger.error(f"개선 효과 측정 오류: {e}")
    
    async def _calculate_actual_impact(self, opportunity: ImprovementOpportunity) -> Optional[Dict[str, Any]]:
        """실제 개선 효과 계산"""
        try:
            # 구현 전후 30일 데이터 비교
            # 실제 환경에서는 구현 날짜를 기준으로 데이터 수집
            
            # 예시: 성능 개선 효과 측정
            if opportunity.category == "performance":
                # 구현 전후 페이지 로딩 시간 비교
                before_performance = opportunity.evidence.get('performance_impact', 0)
                
                # 현재 성능 데이터 조회 (시뮬레이션)
                current_performance = before_performance * 0.7  # 30% 개선 가정
                
                improvement_percentage = ((before_performance - current_performance) / before_performance) * 100
                
                return {
                    'category': 'performance',
                    'before_metrics': {'load_time': before_performance},
                    'after_metrics': {'load_time': current_performance},
                    'improvement_percentage': improvement_percentage,
                    'roi': improvement_percentage * 0.1  # 단순 ROI 계산
                }
            
            # 다른 카테고리들도 유사하게 구현
            return None
            
        except Exception as e:
            logger.error(f"실제 개선 효과 계산 오류: {e}")
            return None
    
    # 저장 메서드들
    async def _save_improvement_opportunity(self, opportunity: ImprovementOpportunity):
        """개선 기회 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO improvement_opportunities 
                (opportunity_id, title, description, category, priority_score,
                 impact_estimate, effort_estimate, confidence, data_sources,
                 evidence, recommendations, success_metrics, created_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opportunity.opportunity_id,
                opportunity.title,
                opportunity.description,
                opportunity.category,
                opportunity.priority_score,
                opportunity.impact_estimate,
                opportunity.effort_estimate,
                opportunity.confidence,
                json.dumps(opportunity.data_sources),
                json.dumps(opportunity.evidence),
                json.dumps(opportunity.recommendations),
                json.dumps(opportunity.success_metrics),
                opportunity.created_date.isoformat(),
                opportunity.status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"개선 기회 저장 오류: {e}")
    
    async def _save_feature_pattern(self, pattern: FeatureUsagePattern):
        """기능 패턴 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO feature_usage_patterns 
                (feature_id, usage_frequency, user_adoption_rate, user_satisfaction,
                 performance_impact, business_value, support_requests, error_rate,
                 abandonment_rate, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.feature_id,
                pattern.usage_frequency,
                pattern.user_adoption_rate,
                pattern.user_satisfaction,
                pattern.performance_impact,
                pattern.business_value,
                pattern.support_requests,
                pattern.error_rate,
                pattern.abandonment_rate,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"기능 패턴 저장 오류: {e}")
    
    async def _save_pain_point(self, pain_point: UserPainPoint):
        """고충점 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_pain_points 
                (pain_point_id, description, affected_users, severity, frequency,
                 related_features, sentiment_score, resolution_difficulty,
                 business_impact, identified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pain_point.pain_point_id,
                pain_point.description,
                pain_point.affected_users,
                pain_point.severity,
                pain_point.frequency,
                json.dumps(pain_point.related_features),
                pain_point.sentiment_score,
                pain_point.resolution_difficulty,
                pain_point.business_impact,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"고충점 저장 오류: {e}")
    
    async def _save_improvement_task(self, task: ImprovementTask):
        """개선 작업 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO improvement_tasks 
                (task_id, opportunity_id, title, description, task_type,
                 estimated_hours, required_skills, dependencies, acceptance_criteria,
                 priority, assigned_to, status, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.opportunity_id,
                task.title,
                task.description,
                task.task_type,
                task.estimated_hours,
                json.dumps(task.required_skills),
                json.dumps(task.dependencies),
                json.dumps(task.acceptance_criteria),
                task.priority,
                task.assigned_to,
                task.status,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"개선 작업 저장 오류: {e}")
    
    async def _save_improvement_result(self, opportunity: ImprovementOpportunity, result: Dict[str, Any]):
        """개선 결과 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            result_id = f"result_{opportunity.opportunity_id}_{int(datetime.now().timestamp())}"
            
            cursor.execute("""
                INSERT INTO improvement_results 
                (result_id, opportunity_id, implemented_date, before_metrics,
                 after_metrics, actual_impact, roi_calculation, lessons_learned)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result_id,
                opportunity.opportunity_id,
                datetime.now().isoformat(),
                json.dumps(result.get('before_metrics', {})),
                json.dumps(result.get('after_metrics', {})),
                result.get('category', ''),
                result.get('roi', 0.0),
                json.dumps([])  # 학습 내용은 나중에 추가
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"개선 결과 저장 오류: {e}")
    
    async def _update_learning_data(self):
        """학습 데이터 업데이트"""
        try:
            # 완료된 개선 사항의 결과를 학습 데이터에 추가
            # 모델 재학습을 위한 데이터 준비
            
            # 실제 구현에서는 결과 데이터를 수집하여 모델 성능 개선
            pass
            
        except Exception as e:
            logger.error(f"학습 데이터 업데이트 오류: {e}")
    
    async def generate_improvement_report(self) -> Dict[str, Any]:
        """개선 추천 보고서 생성"""
        try:
            # 우선순위 매트릭스 조회
            priority_matrix = self.redis_client.get("improvement_priority_matrix")
            matrix_data = json.loads(priority_matrix) if priority_matrix else {}
            
            # 카테고리별 통계
            category_stats = defaultdict(int)
            status_stats = defaultdict(int)
            
            for opportunity in self.improvement_opportunities.values():
                category_stats[opportunity.category] += 1
                status_stats[opportunity.status] += 1
            
            # 상위 우선순위 기회들
            top_opportunities = sorted(
                self.improvement_opportunities.values(),
                key=lambda x: x.priority_score,
                reverse=True
            )[:10]
            
            # 보고서 생성
            report = {
                'generated_at': datetime.now().isoformat(),
                'total_opportunities': len(self.improvement_opportunities),
                'category_breakdown': dict(category_stats),
                'status_breakdown': dict(status_stats),
                'priority_matrix': matrix_data,
                'top_opportunities': [
                    {
                        'id': opp.opportunity_id,
                        'title': opp.title,
                        'category': opp.category,
                        'priority_score': opp.priority_score,
                        'impact': opp.impact_estimate,
                        'effort': opp.effort_estimate,
                        'confidence': opp.confidence
                    }
                    for opp in top_opportunities
                ],
                'total_tasks': len(self.improvement_tasks),
                'feature_patterns_analyzed': len(self.feature_patterns),
                'pain_points_identified': len(self.pain_points)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"개선 보고서 생성 오류: {e}")
            return {}

# 메인 실행
async def main():
    """메인 실행 함수"""
    engine = FeatureImprovementEngine()
    
    try:
        logger.info("🚀 기능 개선 추천 엔진 시작")
        await engine.start_improvement_engine()
    except KeyboardInterrupt:
        logger.info("⏹️ 시스템 종료")
        engine.analysis_enabled = False
    except Exception as e:
        logger.error(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 