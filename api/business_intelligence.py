from extensions import redis_client  # pyright: ignore
from models_main import Order, User, InventoryItem, Schedule, SystemLog, db  # pyright: ignore
import joblib  # pyright: ignore
import pickle  # pyright: ignore
from dataclasses import dataclass, asdict  # pyright: ignore
import aiohttp
import asyncio
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import time
import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
"""
AI 기반 비즈니스 인텔리전스 시스템
데이터 기반 인사이트 생성 및 자동화된 의사결정 지원
"""


# 데이터베이스 모델 import

logger = logging.getLogger(__name__)

business_intelligence_bp = Blueprint('business_intelligence', __name__)


@dataclass
class BusinessInsight:
    """비즈니스 인사이트 데이터 클래스"""
    insight_id: str
    category: str  # 'sales', 'inventory', 'customer', 'operations', 'market'
    title: str
    description: str
    impact_score: float  # 0.0 ~ 1.0
    confidence: float  # 0.0 ~ 1.0
    action_items: Optional[List[str]]
    metrics: Optional[Dict[str, Any]]
    created_at: datetime
    expires_at: Optional[datetime]
    priority: str  # 'low', 'medium', 'high', 'critical'


@dataclass
class MarketTrend:
    """시장 트렌드 데이터 클래스"""
    trend_id: str
    category: str
    trend_type: str  # 'increasing', 'decreasing', 'stable', 'volatile'
    description: str
    confidence: float
    data_points: Optional[List[Dict[str, Any]]]
    prediction_horizon: int  # 일 단위
    impact_analysis: Optional[Dict[str, Any]]


@dataclass
class CompetitiveAnalysis:
    """경쟁사 분석 데이터 클래스"""
    competitor_id: str
    competitor_name: str
    analysis_date: datetime
    market_share: float
    pricing_strategy: str
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    opportunities: Optional[List[str]]
    threats: Optional[List[str]]
    recommendations: Optional[List[str]]


class BusinessIntelligenceService:
    """비즈니스 인텔리전스 서비스"""

    def __init__(self):
        self.insights_cache = {}
        self.trends_cache = {}
        self.competitive_data = {}
        self.insight_generators = {
            'sales': self._generate_sales_insights,
            'inventory': self._generate_inventory_insights,
            'customer': self._generate_customer_insights,
            'operations': self._generate_operations_insights,
            'market': self._generate_market_insights
        }
        self.trend_analyzers = {
            'sales_trend': self._analyze_sales_trends,
            'customer_trend': self._analyze_customer_trends,
            'market_trend': self._analyze_market_trends,
            'competition_trend': self._analyze_competition_trends
        }

        # 인사이트 생성 스케줄러 시작
        self._start_insight_scheduler()

    def _start_insight_scheduler(self):
        """인사이트 생성 스케줄러 시작"""
        def insight_scheduler():
            while True:
                try:
                    # 매일 자정에 인사이트 생성
                    now = datetime.now()
                    if now.hour == 0 and now.minute == 0:
                        self._generate_daily_insights()

                    # 매시간 트렌드 분석
                    if now.minute == 0:
                        self._analyze_real_time_trends()

                    time.sleep(60)  # 1분마다 체크

                except Exception as e:
                    logger.error(f"인사이트 스케줄러 오류: {e}")
                    time.sleep(300)  # 5분 대기

        # 비즈니스 인사이트 스케줄러 비활성화됨 (서버는 계속 실행)
        # import threading
        # thread = threading.Thread(target=insight_scheduler, daemon=True)
        # thread.start()
        logger.info("비즈니스 인사이트 스케줄러 비활성화됨")

    def generate_comprehensive_insights(self) -> Dict[str, Any]:
        """종합 비즈니스 인사이트 생성"""
        try:
            all_insights = {}

            # 각 카테고리별 인사이트 생성
            for category, generator in self.insight_generators.items():
                insights = generator()
                all_insights[category] = insights

            # 종합 분석
            summary = self._create_insight_summary(all_insights)

            # 우선순위별 정렬
            prioritized_insights = self._prioritize_insights(all_insights)

            return {
                'success': True,
                'insights': all_insights,
                'summary': summary,
                'prioritized_insights': prioritized_insights,
                'generated_at': datetime.now().isoformat(),
                'total_insights': sum(len(insights) for insights in all_insights.values())
            }

        except Exception as e:
            logger.error(f"종합 인사이트 생성 실패: {e}")
            return {'error': f'인사이트 생성 실패: {str(e)}'}

    def _generate_sales_insights(self) -> List[BusinessInsight]:
        """매출 관련 인사이트 생성"""
        try:
            insights = []

            # 최근 30일 매출 데이터 분석
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            orders = db.session.query(Order).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).all()

            if not orders:
                return insights

            # 매출 데이터 분석
            daily_sales = defaultdict(float)
            hourly_sales = defaultdict(float)
            category_sales = defaultdict(float)

            for order in orders:
                date = order.created_at.date()  # pyright: ignore
                hour = order.created_at.hour  # pyright: ignore
                daily_sales[date] += getattr(order, 'total_amount', 0)  # pyright: ignore
                hourly_sales[hour] += getattr(order, 'total_amount', 0)  # pyright: ignore

                # 카테고리별 매출 (시뮬레이션)
                category = self._get_order_category(order)
                category_sales[category] += getattr(order, 'total_amount', 0)  # pyright: ignore

            # 평균 일일 매출
            avg_daily_sales = np.mean(list(daily_sales.values()))
            sales_trend = self._calculate_trend(list(daily_sales.values()))

            # 피크 시간대 분석
            peak_hour = max(list(hourly_sales.items()), key=lambda x: x[1])[0]
            peak_sales = hourly_sales[peak_hour]

            # 인사이트 1: 매출 트렌드
            if sales_trend > 0.1:
                insights.append(BusinessInsight(
                    insight_id=f"sales_trend_{int(time.time())}",
                    category='sales',
                    title='매출 상승 트렌드 감지',
                    description=f'최근 30일간 매출이 {sales_trend*100:.1f}% 상승하고 있습니다.',
                    impact_score=0.8,
                    confidence=0.85,
                    action_items=[
                        '재고 확충 고려',
                        '마케팅 캠페인 강화',
                        '직원 스케줄 최적화'
                    ],
                    metrics={
                        'avg_daily_sales': avg_daily_sales,
                        'sales_trend': sales_trend,
                        'total_orders': len(orders)
                    },
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=7),
                    priority='high'
                ))

            # 인사이트 2: 피크 시간대
            insights.append(BusinessInsight(
                insight_id=f"peak_hours_{int(time.time())}",
                category='sales',
                title='피크 시간대 최적화 기회',
                description=f'{peak_hour}시에 매출이 가장 높습니다. ({peak_sales:,.0f}원)',
                impact_score=0.6,
                confidence=0.9,
                action_items=[
                    f'{peak_hour}시대 인력 배치 강화',
                    '피크 시간대 특별 메뉴 고려',
                    '예약 시스템 최적화'
                ],
                metrics={
                    'peak_hour': peak_hour,
                    'peak_sales': peak_sales,
                    'hourly_distribution': dict(hourly_sales)
                },
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=14),
                priority='medium'
            ))

            # 인사이트 3: 카테고리별 성과
            top_category = max(list(category_sales.items()), key=lambda x: x[1])
            insights.append(BusinessInsight(
                insight_id=f"category_performance_{int(time.time())}",
                category='sales',
                title='카테고리별 성과 분석',
                description=f'{top_category[0]} 카테고리가 가장 높은 매출을 기록했습니다.',
                impact_score=0.7,
                confidence=0.8,
                action_items=[
                    f'{top_category[0]} 카테고리 확장 고려',
                    '인기 메뉴 마케팅 강화',
                    '재고 관리 최적화'
                ],
                metrics={
                    'top_category': top_category[0],
                    'top_category_sales': top_category[1],
                    'category_breakdown': dict(category_sales)
                },
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=10),
                priority='medium'
            ))

            return insights

        except Exception as e:
            logger.error(f"매출 인사이트 생성 실패: {e}")
            return []

    def _generate_inventory_insights(self) -> List[BusinessInsight]:
        """재고 관련 인사이트 생성"""
        try:
            insights = []

            # 재고 데이터 분석
            inventory_items = db.session.query(InventoryItem).all()

            if not inventory_items:
                return insights

            # 재고 상태 분석
            low_stock_items = []
            overstock_items = []
            total_inventory_value = 0

            for item in inventory_items:
                total_inventory_value += getattr(item, 'current_stock', 0) * (getattr(item, 'unit_price', 0) or 0)

                # 재고 부족 아이템
                if getattr(item, 'current_stock', 0) < (getattr(item, 'reorder_point', 10) or 10):
                    low_stock_items.append(item)

                # 과잉 재고 아이템
                if getattr(item, 'current_stock', 0) > (getattr(item, 'max_stock', 100) or 100):
                    overstock_items.append(item)

            # 인사이트 1: 재고 부족
            if low_stock_items:
                insights.append(BusinessInsight(
                    insight_id=f"low_stock_{int(time.time())}",
                    category='inventory',
                    title='재고 부족 위험',
                    description=f'{len(low_stock_items)}개 품목의 재고가 부족합니다.',
                    impact_score=0.9,
                    confidence=0.95,
                    action_items=[
                        '긴급 재주문 실행',
                        '공급업체 연락',
                        '대체 품목 검토'
                    ],
                    metrics={
                        'low_stock_count': len(low_stock_items),
                        'affected_items': [item.name for item in low_stock_items[:5]]
                    },
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=1),
                    priority='critical'
                ))

            # 인사이트 2: 과잉 재고
            if overstock_items:
                insights.append(BusinessInsight(
                    insight_id=f"overstock_{int(time.time())}",
                    category='inventory',
                    title='과잉 재고 관리',
                    description=f'{len(overstock_items)}개 품목의 재고가 과다합니다.',
                    impact_score=0.6,
                    confidence=0.85,
                    action_items=[
                        '프로모션 캠페인 실행',
                        '재고 할인 고려',
                        '주문량 조정'
                    ],
                    metrics={
                        'overstock_count': len(overstock_items),
                        'total_inventory_value': total_inventory_value
                    },
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=7),
                    priority='medium'
                ))

            return insights

        except Exception as e:
            logger.error(f"재고 인사이트 생성 실패: {e}")
            return []

    def _generate_customer_insights(self) -> List[BusinessInsight]:
        """고객 관련 인사이트 생성"""
        try:
            insights = []

            # 고객 데이터 분석
            customers = db.session.query(User).filter(
                User.role == 'customer'
            ).all()

            if not customers:
                return insights

            # 고객 행동 분석
            customer_orders = defaultdict(list)
            customer_values = defaultdict(float)

            for customer in customers:
                orders = db.session.query(Order).filter(
                    getattr(Order, 'user_id', None) == customer.id  # pyright: ignore
                ).all()

                customer_orders[customer.id] = orders
                customer_values[customer.id] = sum(getattr(o, 'total_amount', 0) for o in orders)

            # 고객 세분화
            high_value_customers = [cid for cid, value in customer_values.items() if value > 100000]
            frequent_customers = [cid for cid, orders in customer_orders.items() if len(orders) > 5]

            # 인사이트 1: 고가치 고객
            if high_value_customers:
                insights.append(BusinessInsight(
                    insight_id=f"high_value_customers_{int(time.time())}",
                    category='customer',
                    title='고가치 고객 관리',
                    description=f'{len(high_value_customers)}명의 고가치 고객이 전체 매출의 상당 부분을 차지합니다.',
                    impact_score=0.8,
                    confidence=0.9,
                    action_items=[
                        'VIP 고객 전용 서비스 개발',
                        '개인화된 마케팅 캠페인',
                        '로열티 프로그램 강화'
                    ],
                    metrics={
                        'high_value_count': len(high_value_customers),
                        'total_high_value': sum(customer_values[cid] for cid in high_value_customers)
                    },
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=30),
                    priority='high'
                ))

            # 인사이트 2: 고객 이탈 위험
            recent_customers = [cid for cid, orders in customer_orders.items()
                                if orders and (datetime.now() - orders[-1].created_at).days > 30]

            if recent_customers:
                insights.append(BusinessInsight(
                    insight_id=f"customer_churn_risk_{int(time.time())}",
                    category='customer',
                    title='고객 이탈 위험',
                    description=f'{len(recent_customers)}명의 고객이 30일 이상 방문하지 않았습니다.',
                    impact_score=0.7,
                    confidence=0.8,
                    action_items=[
                        '재방문 유도 캠페인',
                        '개인화된 할인 쿠폰 제공',
                        '고객 만족도 조사'
                    ],
                    metrics={
                        'churn_risk_count': len(recent_customers),
                        'avg_days_since_last_visit': 45
                    },
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=14),
                    priority='high'
                ))

            return insights

        except Exception as e:
            logger.error(f"고객 인사이트 생성 실패: {e}")
            return []

    def _generate_operations_insights(self) -> List[BusinessInsight]:
        """운영 관련 인사이트 생성"""
        try:
            insights = []

            # 운영 데이터 분석
            schedules = db.session.query(Schedule).filter(
                getattr(Schedule, 'work_date', datetime.now()) >= datetime.now() - timedelta(days=30)  # pyright: ignore
            ).all()

            if not schedules:
                return insights

            # 인력 효율성 분석
            total_required = sum(getattr(s, 'required_staff', 0) or 0 for s in schedules)
            total_actual = sum(getattr(s, 'actual_staff', 0) or 0 for s in schedules)
            efficiency_ratio = total_actual / total_required if total_required > 0 else 1.0

            # 인사이트 1: 인력 효율성
            if efficiency_ratio > 1.2:
                insights.append(BusinessInsight(
                    insight_id=f"staff_efficiency_{int(time.time())}",
                    category='operations',
                    title='인력 효율성 개선 기회',
                    description=f'인력 배치가 필요 인력보다 {((efficiency_ratio-1)*100):.1f}% 많습니다.',
                    impact_score=0.6,
                    confidence=0.85,
                    action_items=[
                        '인력 배치 최적화',
                        '스케줄 조정',
                        '업무 프로세스 개선'
                    ],
                    metrics={
                        'efficiency_ratio': efficiency_ratio,
                        'total_required': total_required,
                        'total_actual': total_actual
                    },
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=7),
                    priority='medium'
                ))

            return insights

        except Exception as e:
            logger.error(f"운영 인사이트 생성 실패: {e}")
            return []

    def _generate_market_insights(self) -> List[BusinessInsight]:
        """시장 관련 인사이트 생성"""
        try:
            insights = []

            # 시장 데이터 분석 (시뮬레이션)
            market_data = self._get_market_data()

            # 시장 트렌드 분석
            mg = market_data.get('market_growth')
            if mg is not None and isinstance(mg, (int, float)) and mg > 0.05:
                insights.append(BusinessInsight(
                    insight_id=f"market_growth_{int(time.time())}",
                    category='market',
                    title='시장 성장 기회',
                    description=f'시장이 {market_data["market_growth"]*100:.1f}% 성장하고 있습니다.',
                    impact_score=0.8,
                    confidence=0.75,
                    action_items=[
                        '시장 확장 전략 수립',
                        '신규 메뉴 개발',
                        '마케팅 투자 확대'
                    ],
                    metrics=market_data,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=30),
                    priority='high'
                ))

            return insights

        except Exception as e:
            logger.error(f"시장 인사이트 생성 실패: {e}")
            return []

    def analyze_market_trends(self, category: str = 'all') -> Dict[str, Any]:
        """시장 트렌드 분석"""
        try:
            trends = {}

            if category == 'all' or category == 'sales':
                trends['sales_trend'] = self._analyze_sales_trends()

            if category == 'all' or category == 'customer':
                trends['customer_trend'] = self._analyze_customer_trends()

            if category == 'all' or category == 'market':
                trends['market_trend'] = self._analyze_market_trends()

            if category == 'all' or category == 'competition':
                trends['competition_trend'] = self._analyze_competition_trends()

            return {
                'success': True,
                'trends': trends,
                'analyzed_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"시장 트렌드 분석 실패: {e}")
            return {'error': f'트렌드 분석 실패: {str(e)}'}

    def _analyze_sales_trends(self) -> MarketTrend:
        """매출 트렌드 분석"""
        try:
            # 최근 90일 매출 데이터
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            orders = db.session.query(Order).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).all()

            # 일별 매출 집계
            daily_sales = defaultdict(float)
            for order in orders:
                date = order.created_at.date()  # pyright: ignore
                daily_sales[date] += getattr(order, 'total_amount', 0)  # pyright: ignore

            # 트렌드 계산
            sales_values = list(daily_sales.values())
            trend_type = self._determine_trend_type(sales_values)
            prediction = self._predict_future_sales(sales_values)
            return MarketTrend(
                trend_id=f"sales_trend_{int(time.time())}",
                category='sales',
                trend_type=trend_type,
                description=f'매출이 {trend_type} 추세를 보이고 있습니다.',
                confidence=0.8,
                data_points=[
                    {'date': str(date), 'value': value}
                    for date, value in list(daily_sales.items())[-30:]
                ],
                prediction_horizon=30,
                impact_analysis={
                    'trend_strength': self._calculate_trend_strength(sales_values),
                    'seasonality': self._detect_seasonality(sales_values),
                    'prediction': prediction
                }
            )
        except Exception as e:
            logger.error(f"매출 트렌드 분석 실패: {e}")
            return MarketTrend(
                trend_id="error",
                category="sales",
                trend_type="stable",
                description=str(e),
                confidence=0.0,
                data_points=[],
                prediction_horizon=0,
                impact_analysis={}
            )

    def _analyze_customer_trends(self) -> MarketTrend:
        """고객 트렌드 분석"""
        try:
            # 고객 행동 트렌드 분석
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            # 일별 고객 수
            daily_customers = defaultdict(set)
            orders = db.session.query(Order).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).all()
            for order in orders:
                date = order.created_at.date()
                daily_customers[date].add(getattr(order, 'user_id', None))
            customer_counts = [float(len(customers)) for customers in list(daily_customers.values())]
            trend_type = self._determine_trend_type(customer_counts)
            return MarketTrend(
                trend_id=f"customer_trend_{int(time.time())}",
                category='customer',
                trend_type=trend_type,
                description=f'고객 수가 {trend_type} 추세를 보이고 있습니다.',
                confidence=0.75,
                data_points=[
                    {'date': str(date), 'value': float(len(customers))}
                    for date, customers in list(daily_customers.items())[-30:]
                ],
                prediction_horizon=30,
                impact_analysis={
                    'trend_strength': self._calculate_trend_strength(customer_counts),
                    'customer_retention': self._calculate_retention_rate(orders),
                    'avg_order_value': float(np.mean([getattr(o, 'total_amount', 0) for o in orders])) if orders else 0.0
                }
            )
        except Exception as e:
            logger.error(f"고객 트렌드 분석 실패: {e}")
            return MarketTrend(
                trend_id="error",
                category="customer",
                trend_type="stable",
                description=str(e),
                confidence=0.0,
                data_points=[],
                prediction_horizon=0,
                impact_analysis={}
            )

    def _analyze_market_trends(self) -> MarketTrend:
        """시장 트렌드 분석"""
        try:
            # 시장 데이터 (시뮬레이션)
            market_data = self._get_market_data()

            return MarketTrend(
                trend_id=f"market_trend_{int(time.time())}",
                category='market',
                trend_type='increasing' if market_data['market_growth'] > 0 else 'decreasing',
                description=f'시장이 {market_data["market_growth"]*100:.1f}% 성장하고 있습니다.',
                confidence=0.7,
                data_points=market_data.get('historical_data', []),
                prediction_horizon=90,
                impact_analysis={
                    'market_size': market_data['market_size'],
                    'growth_rate': market_data['market_growth'],
                    'competition_level': market_data['competition_level']
                }
            )
        except Exception as e:
            logger.error(f"시장 트렌드 분석 실패: {e}")
            return MarketTrend(
                trend_id="error",
                category="market",
                trend_type="stable",
                description=str(e),
                confidence=0.0,
                data_points=[],
                prediction_horizon=0,
                impact_analysis={}
            )

    def _analyze_competition_trends(self) -> MarketTrend:
        """경쟁사 트렌드 분석"""
        try:
            # 경쟁사 데이터 (시뮬레이션)
            competitors = [
                {'name': 'Competitor A', 'market_share': 0.25, 'growth': 0.05},
                {'name': 'Competitor B', 'market_share': 0.20, 'growth': 0.03},
                {'name': 'Competitor C', 'market_share': 0.15, 'growth': 0.08}
            ]

            avg_growth = np.mean([
                float(c['growth'])
                for c in competitors
                if (
                    (isinstance(c['growth'], (int, float, str)) and not isinstance(c['growth'], list))
                )
            ])
            trend_type = 'increasing' if avg_growth > 0.02 else 'stable'

            return MarketTrend(
                trend_id=f"competition_trend_{int(time.time())}",
                category='competition',
                trend_type=trend_type,
                description=f'경쟁사들이 평균 {avg_growth*100:.1f}% 성장하고 있습니다.',
                confidence=0.6,
                data_points=[
                    {'competitor': c['name'], 'market_share': c['market_share'], 'growth': c['growth']}
                    for c in competitors
                ],
                prediction_horizon=60,
                impact_analysis={
                    'competition_intensity': 'high' if avg_growth > 0.05 else 'medium',
                    'market_consolidation': False,
                    'price_pressure': 'medium'
                }
            )
        except Exception as e:
            logger.error(f"경쟁사 트렌드 분석 실패: {e}")
            return MarketTrend(
                trend_id="error",
                category="competition",
                trend_type="stable",
                description=str(e),
                confidence=0.0,
                data_points=[],
                prediction_horizon=0,
                impact_analysis={}
            )

    def generate_competitive_analysis(self) -> Dict[str, Any]:
        """경쟁사 분석 생성"""
        try:
            # 경쟁사 데이터 수집 (시뮬레이션)
            competitors = [
                {
                    'name': '스타벅스',
                    'market_share': 0.35,
                    'pricing': 'premium',
                    'strengths': ['브랜드 인지도', '글로벌 네트워크', '품질 관리'],
                    'weaknesses': ['높은 가격', '개인화 부족'],
                    'opportunities': ['디지털 혁신', '건강 메뉴'],
                    'threats': ['경제 불황', '원료 가격 상승']
                },
                {
                    'name': '투썸플레이스',
                    'market_share': 0.25,
                    'pricing': 'mid-range',
                    'strengths': ['다양한 메뉴', '편안한 분위기'],
                    'weaknesses': ['브랜드 차별화 부족'],
                    'opportunities': ['테마 카페', '디저트 강화'],
                    'threats': ['대형 체인 진입']
                }
            ]

            analyses = []
            for comp in competitors:
                analysis = CompetitiveAnalysis(
                    competitor_id=f"comp_{len(analyses)}",
                    competitor_name=str(comp['name']),
                    analysis_date=datetime.now(),
                    market_share=float(comp['market_share']),
                    pricing_strategy=str(comp['pricing']),
                    strengths=list(comp['strengths']) if isinstance(comp['strengths'], list) else [],
                    weaknesses=list(comp['weaknesses']) if isinstance(comp['weaknesses'], list) else [],
                    opportunities=list(comp['opportunities']) if isinstance(comp['opportunities'], list) else [],
                    threats=list(comp['threats']) if isinstance(comp['threats'], list) else [],
                    recommendations=self._generate_competitive_recommendations(comp)
                )
                analyses.append(analysis)

            return {
                'success': True,
                'analyses': [asdict(analysis) for analysis in analyses],
                'summary': {
                    'total_competitors': len(analyses),
                    'market_leader': max(analyses, key=lambda x: x.market_share).competitor_name,
                    'average_market_share': np.mean([a.market_share for a in analyses])
                },
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"경쟁사 분석 생성 실패: {e}")
            return {'error': f'경쟁사 분석 실패: {str(e)}'}

    def _generate_competitive_recommendations(self, competitor: Dict[str, Any]) -> List[str]:
        """경쟁사별 권장사항 생성"""
        recommendations = []

        if competitor['pricing'] == 'premium':
            recommendations.extend([
                '가격 경쟁력 강화',
                '고급 서비스 차별화',
                '프리미엄 고객 타겟팅'
            ])
        else:
            recommendations.extend([
                '품질 경쟁력 강화',
                '서비스 차별화',
                '고객 경험 개선'
            ])

        # 기회 요인 활용
        for opportunity in competitor['opportunities']:
            recommendations.append(f'{opportunity} 분야 선점')

        return recommendations

    def _create_insight_summary(self, all_insights: Dict[str, List[BusinessInsight]]) -> Dict[str, Any]:
        """인사이트 요약 생성"""
        try:
            total_insights = sum(len(insights) for insights in all_insights.values())
            critical_insights = sum(
                len([i for i in insights if i.priority == 'critical'])
                for insights in all_insights.values()
            )
            high_priority_insights = sum(
                len([i for i in insights if i.priority in ['critical', 'high']])
                for insights in all_insights.values()
            )

            avg_impact = np.mean([
                insight.impact_score
                for insights in all_insights.values()
                for insight in insights
            ]) if total_insights > 0 else 0

            return {
                'total_insights': total_insights,
                'critical_insights': critical_insights,
                'high_priority_insights': high_priority_insights,
                'average_impact_score': avg_impact,
                'insights_by_category': {
                    category: len(insights) for category, insights in all_insights.items()
                },
                'priority_distribution': {
                    'critical': critical_insights,
                    'high': high_priority_insights - critical_insights,
                    'medium': total_insights - high_priority_insights
                }
            }

        except Exception as e:
            logger.error(f"인사이트 요약 생성 실패: {e}")
            return {}

    def _prioritize_insights(self, all_insights: Dict[str, List[BusinessInsight]]) -> List[BusinessInsight]:
        """인사이트 우선순위 정렬"""
        try:
            all_insights_list = []
            for insights in all_insights.values():
                all_insights_list.extend(insights)

            # 우선순위 및 영향도 기반 정렬
            priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}

            sorted_insights = sorted(
                all_insights_list,
                key=lambda x: (priority_order.get(x.priority, 0), x.impact_score, x.confidence),
                reverse=True
            )

            return sorted_insights

        except Exception as e:
            logger.error(f"인사이트 우선순위 정렬 실패: {e}")
            return []

    def _generate_daily_insights(self):
        """일일 인사이트 생성"""
        try:
            insights = self.generate_comprehensive_insights()

            # Redis에 캐시
            redis_client.setex(
                'daily_insights',
                86400,  # 24시간
                json.dumps(insights, default=str)
            )

            logger.info("일일 인사이트 생성 완료")

        except Exception as e:
            logger.error(f"일일 인사이트 생성 실패: {e}")

    def _analyze_real_time_trends(self):
        """실시간 트렌드 분석"""
        try:
            trends = self.analyze_market_trends()

            # Redis에 캐시
            redis_client.setex(
                'real_time_trends',
                3600,  # 1시간
                json.dumps(trends, default=str)
            )

            logger.info("실시간 트렌드 분석 완료")

        except Exception as e:
            logger.error(f"실시간 트렌드 분석 실패: {e}")

    # 헬퍼 메서드들
    def _get_order_category(self,  order: Order) -> str:
        """주문 카테고리 분류"""
        # 시뮬레이션 - 실제로는 주문 상세에서 분류
        categories = ['음료', '음식', '디저트', '기타']
        return np.random.choice(categories)

    def _calculate_trend(self, values: List[float]) -> float:
        """트렌드 계산"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return slope / np.mean(values) if np.mean(values) > 0 else 0.0

    def _determine_trend_type(self, values: List[float]) -> str:
        """트렌드 타입 결정"""
        if len(values) < 2:
            return 'stable'

        trend = self._calculate_trend(values)

        if trend > 0.05:
            return 'increasing'
        elif trend < -0.05:
            return 'decreasing'
        else:
            return 'stable'

    def _calculate_trend_strength(self, values: List[float]) -> float:
        """트렌드 강도 계산"""
        if len(values) < 2:
            return 0.0

        trend = abs(self._calculate_trend(values))
        return min(1.0, trend * 10)  # 0.1 이상을 강한 트렌드로 간주

    def _detect_seasonality(self, values: List[float]) -> Dict[str, Any]:
        """계절성 감지"""
        if len(values) < 7:
            return {'has_seasonality': False}

        # 간단한 주간 패턴 감지
        weekly_pattern = []
        for i in range(7):
            if i < len(values):
                weekly_pattern.append(values[i])

        return {
            'has_seasonality': True,
            'pattern_length': 7,
            'pattern_strength': 0.6  # 시뮬레이션
        }

    def _predict_future_sales(self,  values: List[float]) -> List[float]:
        """미래 매출 예측"""
        if len(values) < 7:
            return []
        window = 7
        last_values = values[-window:]
        avg = np.mean([float(v) for v in last_values if isinstance(v, (int, float))])
        return [float(avg * (1 + 0.02 * i)) for i in range(1, 31)]  # 30일 예측

    def _calculate_retention_rate(self, orders: List[Order]) -> float:
        """고객 유지율 계산"""
        if not orders:
            return 0.0
        unique_customers = set(getattr(order, 'user_id', None) for order in orders)
        repeat_customers = len([cid for cid in unique_customers
                                if len([o for o in orders if getattr(o, 'user_id', None) == cid]) > 1])
        return repeat_customers / len(unique_customers) if unique_customers else 0.0

    def _get_market_data(self) -> Dict[str, Any]:
        """시장 데이터 조회 (시뮬레이션)"""
        return {
            'market_size': 1000000000,  # 10억원
            'market_growth': 0.08,  # 8% 성장
            'competition_level': 'high',
            'historical_data': [
                {'date': '2024-01-01', 'value': 1000000000},
                {'date': '2024-01-15', 'value': 1080000000}
            ]
        }


# 전역 서비스 인스턴스
bi_service = BusinessIntelligenceService()

# API 엔드포인트들


@business_intelligence_bp.route('/api/bi/insights', methods=['GET'])
@login_required
def get_business_insights():
    """비즈니스 인사이트 조회"""
    try:
        # 캐시된 인사이트 확인
        cached_insights = redis_client.get('daily_insights')
        if cached_insights:
            return jsonify(json.loads(cached_insights))

        # 새로 생성
        result = bi_service.generate_comprehensive_insights()
        return jsonify(result)

    except Exception as e:
        logger.error(f"비즈니스 인사이트 조회 API 오류: {e}")
        return jsonify({'error': '인사이트 조회에 실패했습니다.'}), 500


@business_intelligence_bp.route('/api/bi/trends', methods=['GET'])
@login_required
def get_market_trends():
    """시장 트렌드 조회"""
    try:
        category = request.args.get('category', 'all')

        # 캐시된 트렌드 확인
        cached_trends = redis_client.get('real_time_trends')
        if cached_trends:
            trends_data = json.loads(cached_trends)
            if category == 'all':
                return jsonify(trends_data)
            else:
                return jsonify({
                    'success': True,
                    'trends': {category: trends_data['trends']},
                    'analyzed_at': trends_data['analyzed_at']
                })

        # 새로 분석
        result = bi_service.analyze_market_trends(category)
        return jsonify(result)

    except Exception as e:
        logger.error(f"시장 트렌드 조회 API 오류: {e}")
        return jsonify({'error': '트렌드 조회에 실패했습니다.'}), 500


@business_intelligence_bp.route('/api/bi/competition', methods=['GET'])
@login_required
def get_competitive_analysis():
    """경쟁사 분석 조회"""
    try:
        result = bi_service.generate_competitive_analysis()
        return jsonify(result)

    except Exception as e:
        logger.error(f"경쟁사 분석 조회 API 오류: {e}")
        return jsonify({'error': '경쟁사 분석에 실패했습니다.'}), 500


@business_intelligence_bp.route('/api/bi/insights/generate', methods=['POST'])
@login_required
def generate_insights():
    """인사이트 수동 생성"""
    try:
        result = bi_service.generate_comprehensive_insights()

        # 캐시 업데이트
        redis_client.setex(
            'daily_insights',
            86400,
            json.dumps(result, default=str)
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"인사이트 생성 API 오류: {e}")
        return jsonify({'error': '인사이트 생성에 실패했습니다.'}), 500
