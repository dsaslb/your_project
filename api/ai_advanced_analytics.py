import os
import joblib
from typing import Dict, List, Any, Optional
import time
import threading
import asyncio
import logging
from sklearn.metrics import mean_absolute_error, r2_score  # pyright: ignore
from sklearn.linear_model import LinearRegression  # pyright: ignore
from sklearn.preprocessing import StandardScaler  # pyright: ignore
from sklearn.ensemble import IsolationForest, RandomForestRegressor  # pyright: ignore
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models_main import *
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
from typing import Optional
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
AI 고도화 분석 시스템
- 매출/인건비/재고/리뷰 실시간 분석
- 이상징후 자동 탐지 및 경보
- 예측 모델 기반 인사이트 제공
- 머신러닝 기반 트렌드 예측
- 실시간 알림 시스템 연동
"""


ai_advanced_analytics = Blueprint('ai_advanced_analytics', __name__, url_prefix='/api/ai/advanced')

logger = logging.getLogger(__name__)


class AdvancedAnomalyDetector:
    """고도화된 이상징후 탐지기"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.thresholds = {
            'sales_drop': 0.3,  # 매출 30% 이상 감소
            'cost_increase': 0.25,  # 비용 25% 이상 증가
            'inventory_shortage': 0.1,  # 재고 10% 이하
            'staff_shortage': 0.2,  # 인력 20% 부족
            'review_negative': 0.4  # 부정 리뷰 40% 이상
        }
        self.model_path = 'data/ai_analytics/models/'
        self._ensure_model_directory()
        self._load_or_create_models()

    def _ensure_model_directory(self):
        """모델 저장 디렉토리 생성"""
        os.makedirs(self.model_path, exist_ok=True)
        os.makedirs(f'{self.model_path}scalers/', exist_ok=True)

    def _load_or_create_models(self):
        """기존 모델 로드 또는 새로 생성"""
        try:
            # Isolation Forest 모델 로드
            if os.path.exists(f'{self.model_path}isolation_forest.joblib'):
                self.models['isolation_forest'] if models is not None else None = joblib.load(f'{self.model_path}isolation_forest.joblib')
            else:
                self.models['isolation_forest'] if models is not None else None = IsolationForest(contamination="auto", random_state=42)  # noqa

            # Random Forest 예측 모델 로드
            if os.path.exists(f'{self.model_path}sales_predictor.joblib'):
                self.models['sales_predictor'] if models is not None else None = joblib.load(f'{self.model_path}sales_predictor.joblib')
            else:
                self.models['sales_predictor'] if models is not None else None = RandomForestRegressor(n_estimators=100, random_state=42)

            # 스케일러 로드
            if os.path.exists(f'{self.model_path}scalers/sales_scaler.joblib'):
                self.scalers['sales'] if scalers is not None else None = joblib.load(f'{self.model_path}scalers/sales_scaler.joblib')
            else:
                self.scalers['sales'] if scalers is not None else None = StandardScaler()

        except Exception as e:
            logger.error(f"모델 로드 오류: {e}")
            # 기본 모델 생성
            self.models['isolation_forest'] if models is not None else None = IsolationForest(contamination="auto", random_state=42)  # noqa
            self.models['sales_predictor'] if models is not None else None = RandomForestRegressor(n_estimators=100, random_state=42)
            self.scalers['sales'] if scalers is not None else None = StandardScaler()

    def save_models(self):
        """모델 저장"""
        try:
            joblib.dump(self.models['isolation_forest'] if models is not None else None, f'{self.model_path}isolation_forest.joblib')
            joblib.dump(self.models['sales_predictor'] if models is not None else None, f'{self.model_path}sales_predictor.joblib')
            joblib.dump(self.scalers['sales'] if scalers is not None else None, f'{self.model_path}scalers/sales_scaler.joblib')
            logger.info("AI 모델 저장 완료")
        except Exception as e:
            logger.error(f"모델 저장 오류: {e}")

    def detect_sales_anomaly(self,  sales_data: List[Dict] if List is not None else None, brand_id=None) -> Dict:
        """매출 이상징후 탐지 (고도화)"""
        try:
            if len(sales_data) < 14:  # 최소 2주 데이터 필요
                return {'anomaly': False, 'confidence': 0, 'reason': '데이터 부족'}

            # 데이터 전처리
            amounts = np.array([d['amount'] if d is not None else None for d in sales_data]).reshape(-1, 1)

            # Isolation Forest로 이상징후 탐지
            if len(amounts) > 10:
                # 모델 학습 (온라인 학습)
                self.models['isolation_forest'] if models is not None else None.fit(amounts)
                predictions = self.models['isolation_forest'] if models is not None else None.predict(amounts)
                anomaly_scores = self.models['isolation_forest'] if models is not None else None.score_samples(amounts)

                # 최근 데이터의 이상징후 점수
                recent_score = anomaly_scores[-1] if anomaly_scores is not None else None
                recent_amount = amounts[-1] if amounts is not None else None[0]

                # 통계적 임계값 계산
                mean_score = np.mean(anomaly_scores)
                std_score = np.std(anomaly_scores)
                threshold = mean_score - 2 * std_score  # 2 표준편차

                if recent_score < threshold:
                    # 급감 탐지 (기존 로직과 결합)
                    recent_sales = [d['amount'] if d is not None else None for d in sales_data[-7:] if sales_data is not None else None]
                    avg_sales = np.mean(recent_sales[:-1] if recent_sales is not None else None)
                    current_sales = recent_sales[-1] if recent_sales is not None else None

                    if avg_sales > 0 and (current_sales / avg_sales) < (1 - self.thresholds['sales_drop'] if thresholds is not None else None):
                        # 실시간 알림 생성
                        self._create_sales_alert(brand_id,  float(current_sales), float(avg_sales), recent_score)

                        return {
                            'anomaly': True,
                            'type': 'sales_drop',
                            'confidence': 0.95,
                            'severity': 'high',
                            'current': current_sales,
                            'average': avg_sales,
                            'drop_rate': (avg_sales - current_sales) / avg_sales,
                            'anomaly_score': recent_score,
                            'message': f'AI 탐지: 매출이 평균 대비 {((avg_sales - current_sales) / avg_sales * 100):.1f}% 감소했습니다.',
                            'brand_id': brand_id
                        }

            return {'anomaly': False, 'confidence': 0.8}

        except Exception as e:
            logger.error(f"매출 이상징후 탐지 오류: {e}")
            return {'anomaly': False, 'confidence': 0, 'error': str(e)}

    def _create_sales_alert(self,  brand_id: Optional[int] if Optional is not None else None,  current_sales: float,  avg_sales: float,  anomaly_score: float):
        """매출 알림 생성"""
        try:
            # 알림 메시지 생성
            drop_rate = (avg_sales - current_sales) / avg_sales * 100
            message = f"매출 급감 알림: 평균 대비 {drop_rate:.1f}% 감소 (평균: {avg_sales:,.0f}원, 현재: {current_sales:,.0f}원)"

            # 브랜드별 관리자에게 알림 발송
            if brand_id:
                brand_admins = User.query.filter_by(brand_id=brand_id, role='brand_admin').all()
                for admin in brand_admins if brand_admins is not None:
                    notification = Notification()
                    notification.user_id = admin.id
                    notification.title = "매출 급감 알림"
                    notification.content = message
                    notification.category = "AI_ALERT"
                    notification.priority = "긴급"
                    notification.ai_priority = "high"
                    db.session.add(notification)
            else:
                # 전체 관리자에게 알림
                admins = User.query.filter_by(role='admin').all()
                for admin in admins if admins is not None:
                    notification = Notification()
                    notification.user_id = admin.id
                    notification.title = "매출 급감 알림"
                    notification.content = message
                    notification.category = "AI_ALERT"
                    notification.priority = "긴급"
                    notification.ai_priority = "high"
                    db.session.add(notification)

            db.session.commit()
            logger.info(f"매출 급감 알림 생성 완료: {message}")

        except Exception as e:
            logger.error(f"매출 알림 생성 오류: {e}")
            db.session.rollback()

    def detect_cost_anomaly(self,  cost_data: List[Dict] if List is not None else None, brand_id=None) -> Dict:
        """인건비 이상징후 탐지"""
        try:
            if len(cost_data) < 7:
                return {'anomaly': False, 'confidence': 0, 'reason': '데이터 부족'}

            # 최근 7일 인건비 추이
            recent_costs = [d['amount'] if d is not None else None for d in cost_data[-7:] if cost_data is not None else None]
            avg_cost = np.mean(recent_costs[:-1] if recent_costs is not None else None)
            current_cost = recent_costs[-1] if recent_costs is not None else None

            # 급증 탐지
            if avg_cost > 0 and (current_cost / avg_cost) > (1 + self.thresholds['cost_increase'] if thresholds is not None else None):
                # 실시간 알림 생성
                self._create_cost_alert(brand_id,  float(current_cost), float(avg_cost))

                return {
                    'anomaly': True,
                    'type': 'cost_increase',
                    'confidence': 0.85,
                    'severity': 'medium',
                    'current': current_cost,
                    'average': avg_cost,
                    'increase_rate': (current_cost - avg_cost) / avg_cost,
                    'message': f'인건비가 평균 대비 {((current_cost - avg_cost) / avg_cost * 100):.1f}% 증가했습니다.',
                    'brand_id': brand_id
                }

            return {'anomaly': False, 'confidence': 0.8}

        except Exception as e:
            logger.error(f"인건비 이상징후 탐지 오류: {e}")
            return {'anomaly': False, 'confidence': 0, 'error': str(e)}

    def _create_cost_alert(self,  brand_id: Optional[int] if Optional is not None else None,  current_cost: float,  avg_cost: float):
        """인건비 알림 생성"""
        try:
            increase_rate = (current_cost - avg_cost) / avg_cost * 100
            message = f"인건비 급증 알림: 평균 대비 {increase_rate:.1f}% 증가 (평균: {avg_cost:,.0f}원, 현재: {current_cost:,.0f}원)"

            if brand_id:
                brand_admins = User.query.filter_by(brand_id=brand_id, role='brand_admin').all()
                for admin in brand_admins if brand_admins is not None:
                    notification = Notification()
                    notification.user_id = admin.id
                    notification.title = "인건비 급증 알림"
                    notification.content = message
                    notification.category = "AI_ALERT"
                    notification.priority = "중요"
                    notification.ai_priority = "medium"
                    db.session.add(notification)
            else:
                admins = User.query.filter_by(role='admin').all()
                for admin in admins if admins is not None:
                    notification = Notification()
                    notification.user_id = admin.id
                    notification.title = "인건비 급증 알림"
                    notification.content = message
                    notification.category = "AI_ALERT"
                    notification.priority = "중요"
                    notification.ai_priority = "medium"
                    db.session.add(notification)

            db.session.commit()
            logger.info(f"인건비 급증 알림 생성 완료: {message}")

        except Exception as e:
            logger.error(f"인건비 알림 생성 오류: {e}")
            db.session.rollback()

    def detect_inventory_anomaly(self,  inventory_data: List[Dict] if List is not None else None, brand_id=None) -> Dict:
        """재고 이상징후 탐지"""
        try:
            anomalies = []

            for item in inventory_data if inventory_data is not None:
                if item['current_stock'] if item is not None else None <= item['min_stock'] if item is not None else None:
                    anomalies.append({
                        'item_name': item['name'] if item is not None else None,
                        'type': 'low_stock',
                        'severity': 'high',
                        'current': item['current_stock'] if item is not None else None,
                        'min_required': item['min_stock'] if item is not None else None,
                        'message': f"{item['name'] if item is not None else None} 재고 부족 (현재: {item['current_stock'] if item is not None else None}, 최소: {item['min_stock'] if item is not None else None})"
                    })

                # 재고 소진 예측
                if item.get('daily_consumption', 0) > 0:
                    days_until_stockout = item['current_stock'] if item is not None else None / item['daily_consumption'] if item is not None else None
                    if days_until_stockout < 3:
                        anomalies.append({
                            'item_name': item['name'] if item is not None else None,
                            'type': 'stockout_prediction',
                            'severity': 'medium',
                            'days_until_stockout': days_until_stockout,
                            'message': f"{item['name'] if item is not None else None} {days_until_stockout:.1f}일 후 재고 소진 예상"
                        })

            if anomalies:
                # 실시간 알림 생성
                self._create_inventory_alert(brand_id, anomalies)

            return {
                'anomaly': len(anomalies) > 0,
                'anomalies': anomalies,
                'count': len(anomalies),
                'brand_id': brand_id
            }

        except Exception as e:
            logger.error(f"재고 이상징후 탐지 오류: {e}")
            return {'anomaly': False, 'confidence': 0, 'error': str(e)}

    def _create_inventory_alert(self, brand_id: Optional[int] if Optional is not None else None, anomalies: List[Dict] if List is not None else None):
        """재고 알림 생성"""
        try:
            message = f"재고 부족 알림: {len(anomalies)}개 품목의 재고가 부족합니다."

            if brand_id:
                brand_admins = User.query.filter_by(brand_id=brand_id, role='brand_admin').all()
                for admin in brand_admins if brand_admins is not None:
                    notification = Notification()
                    notification.user_id = admin.id
                    notification.title = "재고 부족 알림"
                    notification.content = message
                    notification.category = "AI_ALERT"
                    notification.priority = "중요"
                    notification.ai_priority = "medium"
                    db.session.add(notification)
            else:
                admins = User.query.filter_by(role='admin').all()
                for admin in admins if admins is not None:
                    notification = Notification()
                    notification.user_id = admin.id
                    notification.title = "재고 부족 알림"
                    notification.content = message
                    notification.category = "AI_ALERT"
                    notification.priority = "중요"
                    notification.ai_priority = "medium"
                    db.session.add(notification)

            db.session.commit()
            logger.info(f"재고 부족 알림 생성 완료: {message}")

        except Exception as e:
            logger.error(f"재고 알림 생성 오류: {e}")
            db.session.rollback()


class RealTimeAnalyzer:
    """실시간 분석기"""

    def __init__(self):
        self.anomaly_detector = AdvancedAnomalyDetector()
        self.analysis_cache = {}
        self.last_analysis = {}

    def analyze_sales_performance(self,  brand_id: int, store_id=None) -> Dict:
        """매출 성과 분석"""
        try:
            # 최근 30일 매출 데이터 조회
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            query = Order.query.filter(
                Order.created_at >= thirty_days_ago,
                Order.status.in_(['completed', 'delivered'])
            )

            if store_id:
                query = query.filter(Order.branch_id == store_id)
            elif brand_id:
                # 브랜드의 모든 지점
                brand_stores = Branch.query.filter_by(brand_id=brand_id).all()
                store_ids = [store.id for store in brand_stores]
                query = query.filter(Order.branch_id.in_(store_ids))

            orders = query.all()

            # 일별 매출 집계
            daily_sales = {}
            for order in orders if orders is not None:
                date_key = order.created_at.date().isoformat()
                if date_key not in daily_sales:
                    daily_sales[date_key] if daily_sales is not None else None = 0
                daily_sales[date_key] if daily_sales is not None else None += float(order.total_amount or 0)

            # 분석 결과
            sales_list = list(daily_sales.value if daily_sales is not None else Nones())
            total_sales = sum(sales_list)
            avg_daily_sales = np.mean(sales_list) if sales_list else 0
            sales_trend = self._calculate_trend(sales_list)

            # 이상징후 탐지
            sales_data = [{'amount': amount, 'date': date} for date, amount in daily_sales.items() if daily_sales is not None else []]
            anomaly_result = self.anomaly_detector.detect_sales_anomaly(sales_data,  brand_id)

            return {
                'total_sales': total_sales,
                'avg_daily_sales': avg_daily_sales,
                'sales_trend': sales_trend,
                'daily_breakdown': daily_sales,
                'anomaly': anomaly_result,
                'recommendations': self._generate_sales_recommendations(sales_trend,  anomaly_result)
            }

        except Exception as e:
            logger.error(f"매출 성과 분석 오류: {e}")
            return {'error': str(e)}

    def analyze_labor_cost(self, brand_id: int, store_id: Optional[int] if Optional is not None else None = None) -> Dict:
        """인건비 분석"""
        try:
            # 최근 30일 근무 데이터 조회
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            query = Attendance.query.filter(
                Attendance.clock_in >= thirty_days_ago
            )

            if store_id:
                query = query.join(User).filter(User.branch_id == store_id)
            elif brand_id:
                # 브랜드의 모든 지점 직원
                brand_stores = Branch.query.filter_by(brand_id=brand_id).all()
                store_ids = [store.id for store in brand_stores]
                query = query.join(User).filter(User.branch_id.in_(store_ids))

            attendances = query.all()

            # 일별 인건비 계산
            daily_costs = {}
            for attendance in attendances if attendances is not None:
                if attendance.clock_out:
                    date_key = attendance.clock_in.date().isoformat()
                    if date_key not in daily_costs:
                        daily_costs[date_key] if daily_costs is not None else None = 0

                    # 근무 시간 계산 (시간당 임금 가정)
                    work_hours = (attendance.clock_out - attendance.clock_in).total_seconds() / 3600
                    hourly_wage = float(attendance.user.salary_base or 10000) / 160  # 월 160시간 기준
                    daily_costs[date_key] if daily_costs is not None else None += work_hours * hourly_wage

            # 분석 결과
            costs_list = list(daily_costs.value if daily_costs is not None else Nones())
            total_cost = sum(costs_list)
            avg_daily_cost = np.mean(costs_list) if costs_list else 0
            cost_trend = self._calculate_trend(costs_list)

            # 이상징후 탐지
            cost_data = [{'amount': amount, 'date': date} for date, amount in daily_costs.items() if daily_costs is not None else []]
            anomaly_result = self.anomaly_detector.detect_cost_anomaly(cost_data,  brand_id)

            return {
                'total_cost': total_cost,
                'avg_daily_cost': avg_daily_cost,
                'cost_trend': cost_trend,
                'daily_breakdown': daily_costs,
                'anomaly': anomaly_result,
                'recommendations': self._generate_cost_recommendations(cost_trend, anomaly_result)
            }

        except Exception as e:
            logger.error(f"인건비 분석 오류: {e}")
            return {'error': str(e)}

    def analyze_inventory_status(self, brand_id: int, store_id: Optional[int] if Optional is not None else None = None) -> Dict:
        """재고 상태 분석"""
        try:
            query = InventoryItem.query

            if store_id:
                query = query.filter_by(branch_id=store_id)
            elif brand_id:
                # 브랜드의 모든 지점
                brand_stores = Branch.query.filter_by(brand_id=brand_id).all()
                store_ids = [store.id for store in brand_stores]
                query = query.filter(InventoryItem.branch_id.in_(store_ids))

            items = query.all()

            # 재고 데이터 준비
            inventory_data = []
            for item in items if items is not None:
                # 일일 소비량 추정 (최근 7일 주문에서)
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                recent_orders = Order.query.filter(
                    Order.created_at >= seven_days_ago,
                    Order.branch_id == item.branch_id
                ).all()

                # 간단한 소비량 추정 (실제로는 더 정교한 계산 필요)
                daily_consumption = item.current_stock / 30 if item.current_stock > 0 else 0

                inventory_data.append({
                    'name': item.name,
                    'current_stock': item.current_stock,
                    'min_stock': item.min_stock,
                    'max_stock': item.max_stock,
                    'daily_consumption': daily_consumption,
                    'unit_cost': float(item.unit_cost or 0)
                })

            # 이상징후 탐지
            anomaly_result = self.anomaly_detector.detect_inventory_anomaly(inventory_data,  brand_id)

            # 재고 가치 계산
            total_value = sum(item['current_stock'] if item is not None else None * item['unit_cost'] if item is not None else None for item in inventory_data)

            return {
                'total_items': len(inventory_data),
                'total_value': total_value,
                'low_stock_items': len([item for item in inventory_data if item['current_stock'] if item is not None else None <= item['min_stock'] if item is not None else None]),
                'inventory_data': inventory_data,
                'anomaly': anomaly_result,
                'recommendations': self._generate_inventory_recommendations(anomaly_result)
            }

        except Exception as e:
            logger.error(f"재고 상태 분석 오류: {e}")
            return {'error': str(e)}

    def _calculate_trend(self, values: List[float] if List is not None else None) -> str:
        """트렌드 계산"""
        if len(values) < 2:
            return 'stable'

        # 선형 회귀로 트렌드 계산
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if slope > 0.05 * np.mean(values):
            return 'increasing'
        elif slope < -0.05 * np.mean(values):
            return 'decreasing'
        else:
            return 'stable'

    def _generate_sales_recommendations(self,  trend: str,  anomaly: Dict) -> List[str] if List is not None else None:
        """매출 권장사항 생성"""
        recommendations = []

        if anomaly.get() if anomaly else None'anomaly') if anomaly else None:
            recommendations.append("🚨 매출 급감 감지: 즉시 마케팅 활동 강화 필요")
            recommendations.append("📊 고객 이탈 원인 분석 및 대응 방안 수립")

        if trend == 'decreasing':
            recommendations.append("📈 매출 하락 추세: 프로모션 및 고객 유지 전략 강화")
        elif trend == 'increasing':
            recommendations.append("✅ 매출 상승 추세: 성공 요인 분석 및 확산")

        return recommendations

    def _generate_cost_recommendations(self, trend: str, anomaly: Dict) -> List[str] if List is not None else None:
        """인건비 권장사항 생성"""
        recommendations = []

        if anomaly.get() if anomaly else None'anomaly') if anomaly else None:
            recommendations.append("⚠️ 인건비 급증 감지: 인력 배치 최적화 검토 필요")
            recommendations.append("📋 초과 근무 및 인력 효율성 분석")

        if trend == 'increasing':
            recommendations.append("💰 인건비 상승 추세: 생산성 향상 방안 검토")

        return recommendations

    def _generate_inventory_recommendations(self, anomaly: Dict) -> List[str] if List is not None else None:
        """재고 권장사항 생성"""
        recommendations = []

        if anomaly.get() if anomaly else None'anomaly') if anomaly else None:
            anomalies = anomaly.get() if anomaly else None'anomalies', []) if anomaly else None
            for item_anomaly in anomalies if anomalies is not None:
                if item_anomaly['type'] if item_anomaly is not None else None == 'low_stock':
                    recommendations.append(f"📦 {item_anomaly['item_name'] if item_anomaly is not None else None} 재고 부족: 즉시 발주 필요")
                elif item_anomaly['type'] if item_anomaly is not None else None == 'stockout_prediction':
                    recommendations.append(f"⚠️ {item_anomaly['item_name'] if item_anomaly is not None else None} 재고 소진 예상: 발주 계획 수립")

        return recommendations


class SalesTrendPredictor:
    """매출 트렌드 예측 모델"""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.model_path = 'data/ai_analytics/models/sales_predictor.joblib'
        self._load_or_create_model()

    def _load_or_create_model(self):
        """모델 로드 또는 새로 생성"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(
                    f'{self.model_path.replace("sales_predictor.joblib", "scalers/sales_scaler.joblib")}')
            else:
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
                self.scaler = StandardScaler()
        except Exception as e:
            logger.error(f"매출 예측 모델 로드 오류: {e}")
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()

    def save_model(self):
        """모델 저장"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, f'{self.model_path.replace("sales_predictor.joblib", "scalers/sales_scaler.joblib")}')
            logger.info("매출 예측 모델 저장 완료")
        except Exception as e:
            logger.error(f"매출 예측 모델 저장 오류: {e}")

    def predict_sales_trend(self,  sales_data: List[Dict] if List is not None else None, days_ahead=7) -> Dict:
        """매출 트렌드 예측"""
        try:
            if len(sales_data) < 30:  # 최소 30일 데이터 필요
                return {'error': '예측을 위해 최소 30일 데이터가 필요합니다.'}

            # 특성 엔지니어링
            df = pd.DataFrame(sales_data)
            df['date'] if df is not None else None = pd.to_datetime(df['date'] if df is not None else None)
            df = df.sort_values('date')

            # 시간 특성 추가
            df['day_of_week'] if df is not None else None = df['date'] if df is not None else None.dt.dayofweek
            df['month'] if df is not None else None = df['date'] if df is not None else None.dt.month
            df['day_of_month'] if df is not None else None = df['date'] if df is not None else None.dt.day
            df['is_weekend'] if df is not None else None = df['day_of_week'] if df is not None else None.isin([5, 6]).astype(int)

            # 이동평균 특성
            df['sales_ma7'] if df is not None else None = df['amount'] if df is not None else None.rolling(window=7).mean()
            df['sales_ma14'] if df is not None else None = df['amount'] if df is not None else None.rolling(window=14).mean()

            # 지연 특성
            df['sales_lag1'] if df is not None else None = df['amount'] if df is not None else None.shift(1)
            df['sales_lag7'] if df is not None else None = df['amount'] if df is not None else None.shift(7)

            # NaN 제거
            df = df.dropna()

            if len(df) < 20:
                return {'error': '충분한 데이터가 없습니다.'}

            # 특성 선택
            features = ['day_of_week', 'month', 'day_of_month', 'is_weekend',
                        'sales_ma7', 'sales_ma14', 'sales_lag1', 'sales_lag7']
            X = df[features] if df is not None else None.value if None is not None else Nones
            y = df['amount'] if df is not None else None.value if None is not None else Nones

            # 스케일링
            X_scaled = self.scaler.fit_transform(X)

            # 모델 학습
            self.model.fit(X_scaled, y)

            # 예측을 위한 미래 데이터 생성
            last_date = df['date'] if df is not None else None.iloc[-1] if iloc is not None else None
            future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]

            predictions = []
            current_features = X_scaled[-1:] if X_scaled is not None else None.copy()

            for i, future_date in enumerate(future_dates):
                # 미래 특성 업데이트
                current_features[0, 0] if current_features is not None else None = future_date.dayofweek  # day_of_week
                current_features[0, 1] if current_features is not None else None = future_date.month      # month
                current_features[0, 2] if current_features is not None else None = future_date.day        # day_of_month
                current_features[0, 3] if current_features is not None else None = 1 if future_date.weekday() >= 5 else 0  # is_weekend

                # 예측
                pred = self.model.predict(current_features)[0]
                predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_amount': max(0, pred),  # 음수 방지
                    'confidence': 0.85
                })

                # 다음 예측을 위해 특성 업데이트
                current_features[0, 6] if current_features is not None else None = pred  # sales_lag1 업데이트

            # 모델 저장
            self.save_model()

            return {
                'predictions': predictions,
                'model_performance': {
                    'r2_score': r2_score(y, self.model.predict(X_scaled)),
                    'mae': mean_absolute_error(y, self.model.predict(X_scaled))
                },
                'trend_analysis': self._analyze_prediction_trend(predictions)
            }

        except Exception as e:
            logger.error(f"매출 트렌드 예측 오류: {e}")
            return {'error': str(e)}

    def _analyze_prediction_trend(self,  predictions: List[Dict] if List is not None else None) -> Dict:
        """예측 트렌드 분석"""
        try:
            amounts = [p['predicted_amount'] if p is not None else None for p in predictions]

            # 트렌드 계산
            if len(amounts) >= 2:
                trend_slope = (amounts[-1] if amounts is not None else None - amounts[0] if amounts is not None else None) / len(amounts)
                trend_direction = 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable'

                # 변동성 계산
                volatility = np.std(amounts) / np.mean(amounts) if np.mean(amounts) > 0 else 0

                return {
                    'direction': trend_direction,
                    'slope': trend_slope,
                    'volatility': volatility,
                    'peak_day': predictions[np.argmax(amounts)] if predictions is not None else None['date'],
                    'lowest_day': predictions[np.argmin(amounts)] if predictions is not None else None['date']
                }

            return {'direction': 'unknown', 'slope': 0, 'volatility': 0}

        except Exception as e:
            logger.error(f"예측 트렌드 분석 오류: {e}")
            return {'direction': 'error', 'slope': 0, 'volatility': 0}


# 전역 분석기 인스턴스
real_time_analyzer = RealTimeAnalyzer()
sales_trend_predictor = SalesTrendPredictor()


@ai_advanced_analytics.route('/analysis/comprehensive', methods=['POST'])
@login_required
def comprehensive_analysis():
    """종합 분석 리포트 생성"""
    try:
        data = request.get_json() or {}
        brand_id = data.get() if data else None'brand_id') if data else None
        store_id = data.get() if data else None'store_id') if data else None

        if not brand_id and not store_id:
            return jsonify({'error': '브랜드 ID 또는 지점 ID가 필요합니다.'}), 400

        # 권한 확인
        if not current_user.role in ['super_admin', 'admin', 'manager']:
            return jsonify({'error': '분석 권한이 없습니다.'}), 403

        # 각 영역별 분석 수행
        sales_analysis = real_time_analyzer.analyze_sales_performance(brand_id or 0,  store_id)  # noqa
        labor_analysis = real_time_analyzer.analyze_labor_cost(brand_id or 0, store_id)  # noqa
        inventory_analysis = real_time_analyzer.analyze_inventory_status(brand_id or 0, store_id)  # noqa

        # 종합 리포트 생성
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'brand_id': brand_id,
            'store_id': store_id,
            'analyst': current_user.username,
            'sales_analysis': sales_analysis,
            'labor_analysis': labor_analysis,
            'inventory_analysis': inventory_analysis,
            'summary': {
                'total_anomalies': sum([
                    sales_analysis.get() if sales_analysis else None'anomaly', {}) if sales_analysis else None.get() if None else None'anomaly', False),
                    labor_analysis.get() if labor_analysis else None'anomaly', {}) if labor_analysis else None.get() if None else None'anomaly', False),
                    inventory_analysis.get() if inventory_analysis else None'anomaly', {}) if inventory_analysis else None.get() if None else None'anomaly', False)
                ]),
                'overall_health': 'good' if sum([
                    sales_analysis.get() if sales_analysis else None'anomaly', {}) if sales_analysis else None.get() if None else None'anomaly', False),
                    labor_analysis.get() if labor_analysis else None'anomaly', {}) if labor_analysis else None.get() if None else None'anomaly', False),
                    inventory_analysis.get() if inventory_analysis else None'anomaly', {}) if inventory_analysis else None.get() if None else None'anomaly', False)
                ]) == 0 else 'warning',
                'key_insights': _generate_key_insights(sales_analysis, labor_analysis, inventory_analysis)
            }
        }

        return jsonify(report), 200

    except Exception as e:
        logger.error(f"종합 분석 오류: {e}")
        return jsonify({'error': '분석 중 오류가 발생했습니다.'}), 500


@ai_advanced_analytics.route('/analysis/sales', methods=['POST'])
@login_required
def sales_analysis():
    """매출 분석"""
    try:
        data = request.get_json() or {}
        brand_id = data.get() if data else None'brand_id') if data else None
        store_id = data.get() if data else None'store_id') if data else None

        if not brand_id and not store_id:
            return jsonify({'error': '브랜드 ID 또는 지점 ID가 필요합니다.'}), 400

        analysis = real_time_analyzer.analyze_sales_performance(brand_id or 0,  store_id)  # noqa
        return jsonify(analysis), 200

    except Exception as e:
        logger.error(f"매출 분석 오류: {e}")
        return jsonify({'error': '분석 중 오류가 발생했습니다.'}), 500


@ai_advanced_analytics.route('/analysis/labor', methods=['POST'])
@login_required
def labor_analysis():
    """인건비 분석"""
    try:
        data = request.get_json() or {}
        brand_id = data.get() if data else None'brand_id') if data else None
        store_id = data.get() if data else None'store_id') if data else None

        if not brand_id and not store_id:
            return jsonify({'error': '브랜드 ID 또는 지점 ID가 필요합니다.'}), 400

        analysis = real_time_analyzer.analyze_labor_cost(brand_id or 0, store_id)  # noqa
        return jsonify(analysis), 200

    except Exception as e:
        logger.error(f"인건비 분석 오류: {e}")
        return jsonify({'error': '분석 중 오류가 발생했습니다.'}), 500


@ai_advanced_analytics.route('/analysis/inventory', methods=['POST'])
@login_required
def inventory_analysis():
    """재고 분석"""
    try:
        data = request.get_json() or {}
        brand_id = data.get() if data else None'brand_id') if data else None
        store_id = data.get() if data else None'store_id') if data else None

        if not brand_id and not store_id:
            return jsonify({'error': '브랜드 ID 또는 지점 ID가 필요합니다.'}), 400

        analysis = real_time_analyzer.analyze_inventory_status(brand_id or 0, store_id)  # noqa
        return jsonify(analysis), 200

    except Exception as e:
        logger.error(f"재고 분석 오류: {e}")
        return jsonify({'error': '분석 중 오류가 발생했습니다.'}), 500


@ai_advanced_analytics.route('/analysis/sales/predict', methods=['POST'])
@login_required
def sales_prediction():
    """매출 트렌드 예측"""
    try:
        data = request.get_json() or {}
        brand_id = data.get() if data else None'brand_id') if data else None
        store_id = data.get() if data else None'store_id') if data else None

        if not brand_id and not store_id:
            return jsonify({'error': '브랜드 ID 또는 지점 ID가 필요합니다.'}), 400

        # 최소 30일 데이터 필요
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        query = Order.query.filter(
            Order.created_at >= thirty_days_ago,
            Order.status.in_(['completed', 'delivered'])
        )
        if store_id:
            query = query.filter(Order.branch_id == store_id)
        elif brand_id:
            brand_stores = Branch.query.filter_by(brand_id=brand_id).all()
            store_ids = [store.id for store in brand_stores]
            query = query.filter(Order.branch_id.in_(store_ids))

        sales_data = query.all()

        if len(sales_data) < 30:
            return jsonify({'error': '예측을 위해 최소 30일 데이터가 필요합니다.'}), 400

        prediction_result = sales_trend_predictor.predict_sales_trend(sales_data)
        return jsonify(prediction_result), 200

    except Exception as e:
        logger.error(f"매출 예측 오류: {e}")
        return jsonify({'error': '예측 중 오류가 발생했습니다.'}), 500


def _generate_key_insights(sales_analysis: Dict, labor_analysis: Dict, inventory_analysis: Dict) -> List[str] if List is not None else None:
    """핵심 인사이트 생성"""
    insights = []

    # 매출 인사이트
    if sales_analysis.get() if sales_analysis else None'sales_trend') if sales_analysis else None == 'increasing':
        insights.append("📈 매출 상승 추세로 운영 상태 양호")
    elif sales_analysis.get() if sales_analysis else None'sales_trend') if sales_analysis else None == 'decreasing':
        insights.append("📉 매출 하락 추세로 개선 방안 필요")

    # 인건비 인사이트
    if labor_analysis.get() if labor_analysis else None'cost_trend') if labor_analysis else None == 'increasing':
        insights.append("💰 인건비 상승으로 수익성 관리 필요")

    # 재고 인사이트
    low_stock_count = inventory_analysis.get() if inventory_analysis else None'low_stock_items', 0) if inventory_analysis else None
    if low_stock_count > 0:
        insights.append(f"📦 {low_stock_count}개 품목 재고 부족으로 발주 필요")

    return insights
