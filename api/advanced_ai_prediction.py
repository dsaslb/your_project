from extensions import db
from models_main import Order, User, Attendance, InventoryItem, Schedule
import warnings
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score  # pyright: ignore
from sklearn.model_selection import train_test_split, cross_val_score  # pyright: ignore
from sklearn.preprocessing import StandardScaler, MinMaxScaler  # pyright: ignore
from sklearn.linear_model import LinearRegression, Ridge  # pyright: ignore
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor  # pyright: ignore
import joblib
import pickle
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
#!/usr/bin/env python3
"""
고급 AI 예측 시스템
머신러닝 기반의 정교한 예측 모델 및 분석 시스템
"""

warnings.filterwarnings('ignore')

# 데이터베이스 모델 import

logger = logging.getLogger(__name__)

advanced_ai_prediction_bp = Blueprint('advanced_ai_prediction', __name__)


class AdvancedAIPredictionService:
    """고급 AI 예측 서비스"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
        self.prediction_cache = {}
        self.last_training = {}

        # 모델 설정
        self.model_configs = {
            'sales_forecast': {
                'model_type': 'gradient_boosting',
                'features': ['day_of_week', 'month', 'season', 'holiday', 'weather', 'previous_sales'],
                'target': 'sales_amount',
                'horizon_days': 30
            },
            'inventory_prediction': {
                'model_type': 'random_forest',
                'features': ['current_stock', 'sales_history', 'lead_time', 'seasonality'],
                'target': 'required_stock',
                'horizon_days': 7
            },
            'customer_behavior': {
                'model_type': 'random_forest',
                'features': ['visit_frequency', 'avg_order_value', 'last_visit', 'preferences'],
                'target': 'churn_probability',
                'horizon_days': 90
            },
            'staff_scheduling': {
                'model_type': 'linear_regression',
                'features': ['historical_demand', 'day_of_week', 'season', 'events'],
                'target': 'required_staff',
                'horizon_days': 14
            }
        }

        # 모델 초기화
        self._initialize_models()

    def _initialize_models(self):
        """모델 초기화"""
        # model_configs는 self. 접두사로 접근
        for model_name, config in self.model_configs.items():
            try:
                # 모델 생성
                if config['model_type'] == 'gradient_boosting':
                    self.models[model_name] = GradientBoostingRegressor(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=5,
                        random_state=42
                    )
                elif config['model_type'] == 'random_forest':
                    self.models[model_name] = RandomForestRegressor(
                        n_estimators=100,
                        max_depth=10,
                        random_state=42
                    )
                elif config['model_type'] == 'linear_regression':
                    self.models[model_name] = Ridge(alpha=1.0)

                # 스케일러 생성
                self.scalers[model_name] = StandardScaler()

                # 메타데이터 초기화
                self.model_metadata[model_name] = {
                    'last_trained': None,
                    'accuracy': 0.0,
                    'training_samples': 0,
                    'features_importance': {},
                    'model_performance': {}
                }

                logger.info(f"모델 초기화 완료: {model_name}")

            except Exception as e:
                logger.error(f"모델 초기화 실패 {model_name}: {e}")

    def prepare_sales_data(self, days_back=365) -> pd.DataFrame:
        """매출 예측용 데이터 준비"""
        try:
            # 과거 주문 데이터 조회
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            orders = db.session.query(Order).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).all()

            # 데이터프레임 생성
            data = []
            for order in orders:  # 불필요한 if orders is not None 제거
                data.append({
                    'date': order.created_at.date(),
                    'sales_amount': getattr(order, 'total_amount', 0),  # pyright: ignore
                    'order_count': 1,
                    'day_of_week': order.created_at.weekday(),
                    'month': order.created_at.month,
                    'season': self._get_season(order.created_at.month),
                    'holiday': self._is_holiday(order.created_at.date()),
                    'weather': self._get_weather_score(order.created_at.date())  # 시뮬레이션
                })

            df = pd.DataFrame(data)

            # 일별 집계
            daily_sales = df.groupby('date').agg({
                'sales_amount': 'sum',
                'order_count': 'sum',
                'day_of_week': 'first',
                'month': 'first',
                'season': 'first',
                'holiday': 'first',
                'weather': 'first'
            }).reset_index()

            # 이전 매출 데이터 추가 (시계열 특성)
            daily_sales['previous_sales'] = daily_sales['sales_amount'].shift(1)
            daily_sales['sales_7d_avg'] = daily_sales['sales_amount'].rolling(7).mean()
            daily_sales['sales_30d_avg'] = daily_sales['sales_amount'].rolling(30).mean()

            # 결측값 처리
            daily_sales = daily_sales.dropna()

            return daily_sales

        except Exception as e:
            logger.error(f"매출 데이터 준비 실패: {e}")
            return pd.DataFrame()

    def prepare_inventory_data(self) -> pd.DataFrame:
        """재고 예측용 데이터 준비"""
        try:
            # 재고 아이템 데이터 조회
            inventory_items = db.session.query(InventoryItem).all()

            data = []
            for item in inventory_items:
                # 관련 주문 데이터 조회
                orders = db.session.query(Order).filter(
                    Order.created_at >= datetime.now() - timedelta(days=30)
                ).all()

                # 아이템별 판매량 계산 (시뮬레이션)
                avg_daily_sales = np.random.randint(1, 10)  # 실제로는 주문 상세에서 계산

                data.append({
                    'item_id': item.id,
                    'item_name': item.name,
                    'current_stock': item.current_stock,
                    'avg_daily_sales': avg_daily_sales,
                    'lead_time_days': np.random.randint(1, 7),
                    'seasonality_factor': self._get_seasonality_factor(item.name),
                    'safety_stock': max(avg_daily_sales * 2, 5),
                    'reorder_point': avg_daily_sales * 3
                })

            return pd.DataFrame(data)

        except Exception as e:
            logger.error(f"재고 데이터 준비 실패: {e}")
            return pd.DataFrame()

    def prepare_customer_data(self) -> pd.DataFrame:
        """고객 행동 예측용 데이터 준비"""
        try:
            # 사용자 데이터 조회
            users = db.session.query(User).filter(
                User.role == 'customer'
            ).all()

            data = []
            for user in users:
                # 사용자별 주문 데이터 조회
                user_orders = db.session.query(Order).filter(
                    Order.user_id == user.id  # pyright: ignore
                ).order_by(Order.created_at.desc()).all()

                if user_orders:
                    visit_frequency = len(user_orders) / max(1, (datetime.now() - user_orders[-1].created_at).days)  # pyright: ignore
                    avg_order_value = sum(o.total_amount or 0 for o in user_orders) / len(user_orders)  # pyright: ignore
                    last_visit_days = (datetime.now() - user_orders[0].created_at).days  # pyright: ignore

                    # 이탈 확률 계산 (시뮬레이션)
                    churn_probability = min(0.9, last_visit_days / 90) if last_visit_days > 30 else 0.1

                    data.append({
                        'user_id': user.id,
                        'visit_frequency': visit_frequency,
                        'avg_order_value': avg_order_value,
                        'last_visit_days': last_visit_days,
                        'total_orders': len(user_orders),
                        'preferences_score': np.random.uniform(0, 1),  # 시뮬레이션
                        'churn_probability': churn_probability
                    })

            return pd.DataFrame(data)

        except Exception as e:
            logger.error(f"고객 데이터 준비 실패: {e}")
            return pd.DataFrame()

    def prepare_staff_data(self) -> pd.DataFrame:
        """직원 스케줄링 예측용 데이터 준비"""
        try:
            # 과거 스케줄 데이터 조회
            schedules = db.session.query(Schedule).filter(
                Schedule.work_date >= datetime.now() - timedelta(days=90)  # pyright: ignore
            ).all()

            data = []
            for schedule in schedules:
                # 해당 날짜의 주문 수 조회
                day_orders = db.session.query(Order).filter(
                    Order.created_at >= schedule.work_date,  # pyright: ignore
                    Order.created_at < schedule.work_date + timedelta(days=1)  # pyright: ignore
                ).count()

                data.append({
                    'date': schedule.work_date.date(),  # pyright: ignore
                    'required_staff': schedule.required_staff or 1,  # pyright: ignore
                    'actual_staff': schedule.actual_staff or 1,  # pyright: ignore
                    'day_of_week': schedule.work_date.weekday(),  # pyright: ignore
                    'month': schedule.work_date.month,  # pyright: ignore
                    'season': self._get_season(schedule.work_date.month),  # pyright: ignore
                    'historical_demand': day_orders,
                    'events': self._has_events(schedule.work_date.date())  # pyright: ignore
                })

            return pd.DataFrame(data)

        except Exception as e:
            logger.error(f"직원 데이터 준비 실패: {e}")
            return pd.DataFrame()

    def train_sales_forecast_model(self) -> Dict[str, Any]:  # 타입힌트 표준화
        """매출 예측 모델 훈련"""
        try:
            # 데이터 준비
            df = self.prepare_sales_data()
            if df.empty:
                return {'error': '훈련 데이터가 부족합니다.'}

            # 특성 선택
            features = ['day_of_week', 'month', 'season', 'holiday', 'weather', 'previous_sales', 'sales_7d_avg']
            X = df[features]
            y = df['sales_amount']

            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # 스케일링
            X_train_scaled = self.scalers['sales_forecast'].fit_transform(X_train)
            X_test_scaled = self.scalers['sales_forecast'].transform(X_test)

            # 모델 훈련
            model = self.models['sales_forecast']
            model.fit(X_train_scaled, y_train)

            # 예측 및 평가
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            # 특성 중요도
            feature_importance = dict(zip(features, getattr(model, 'feature_importances_', [])))  # pyright: ignore

            # 메타데이터 업데이트
            self.model_metadata['sales_forecast'].update({
                'last_trained': datetime.now(),
                'accuracy': r2,
                'training_samples': len(X_train),
                'features_importance': feature_importance,
                'model_performance': {
                    'mse': mse,
                    'mae': mae,
                    'r2': r2
                }
            })

            logger.info(f"매출 예측 모델 훈련 완료: R² = {r2:.3f}")

            return {
                'success': True,
                'accuracy': r2,
                'training_samples': len(X_train),
                'feature_importance': feature_importance,
                'performance': {
                    'mse': mse,
                    'mae': mae,
                    'r2': r2
                }
            }

        except Exception as e:
            logger.error(f"매출 예측 모델 훈련 실패: {e}")
            return {'error': f'모델 훈련 실패: {str(e)}'}

    def predict_sales_forecast(self, days_ahead: int = 30) -> Dict[str, Any]:
        """매출 예측"""
        try:
            if 'sales_forecast' not in self.models:
                return {'error': '매출 예측 모델이 훈련되지 않았습니다.'}
            # 최근 데이터로 예측 데이터 준비
            recent_data = self.prepare_sales_data(days_back=60)
            if recent_data.empty:
                return {'error': '예측 데이터를 준비할 수 없습니다.'}
            # 미래 날짜 생성
            last_date = recent_data['date'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead, freq='D')
            predictions = []
            current_data = recent_data.copy()
            model = self.models['sales_forecast']  # 명확히 정의
            for future_date in future_dates:
                # 특성 준비
                features = {
                    'day_of_week': future_date.weekday(),
                    'month': future_date.month,
                    'season': self._get_season(future_date.month),
                    'holiday': self._is_holiday(future_date.date()),
                    'weather': self._get_weather_score(future_date.date()),
                    'previous_sales': current_data['sales_amount'].iloc[-1] if not current_data.empty else 0,
                    'sales_7d_avg': current_data['sales_amount'].tail(7).mean() if len(current_data) >= 7 else 0
                }
                # 예측
                X_pred = pd.DataFrame([features])
                X_pred_scaled = self.scalers['sales_forecast'].transform(X_pred)
                prediction = model.predict(X_pred_scaled)[0]
                predictions.append({
                    'date': future_date.date().isoformat(),
                    'predicted_sales': max(0, float(prediction)),
                    # pyright: ignore
                    'confidence': self._calculate_confidence(float(prediction), current_data['sales_amount'])
                })
                # 데이터 업데이트 (시뮬레이션)
                current_data = current_data.append({
                    'date': future_date.date(),
                    'sales_amount': prediction,
                    'day_of_week': future_date.weekday(),
                    'month': future_date.month,
                    'season': self._get_season(future_date.month),
                    'holiday': self._is_holiday(future_date.date()),
                    'weather': self._get_weather_score(future_date.date())
                }, ignore_index=True)
            total_predicted = sum(p['predicted_sales'] for p in predictions)
            return {
                'success': True,
                'predictions': predictions,
                'total_predicted_sales': total_predicted,
                'avg_daily_sales': total_predicted / days_ahead,
                'model_accuracy': self.model_metadata['sales_forecast']['accuracy'],
                'last_trained': self.model_metadata['sales_forecast']['last_trained'].isoformat() if self.model_metadata['sales_forecast']['last_trained'] else None
            }
        except Exception as e:
            logger.error(f"매출 예측 실패: {e}")
            return {'error': f'예측 실패: {str(e)}'}

    def predict_inventory_needs(self) -> Dict[str, Any]:
        """재고 필요량 예측"""
        try:
            # 재고 데이터 준비
            df = self.prepare_inventory_data()
            if df.empty:
                return {'error': '재고 데이터를 준비할 수 없습니다.'}
            predictions = []
            for _, item in df.iterrows():
                # 재고 부족 예측
                daily_usage = item['avg_daily_sales']
                days_until_stockout = float(item['current_stock']) / float(daily_usage) if daily_usage > 0 else float('inf')
                # 재주문 필요량 계산
                lead_time_days = item['lead_time_days']
                safety_stock = item['safety_stock']
                required_stock = float(daily_usage) * float(lead_time_days) + float(safety_stock)
                reorder_quantity = max(0, float(required_stock) - float(item['current_stock']))
                # 긴급도 계산
                urgency = 'low'
                if days_until_stockout < 3:
                    urgency = 'critical'
                elif days_until_stockout < 7:
                    urgency = 'high'
                elif days_until_stockout < 14:
                    urgency = 'medium'
                predictions.append({
                    'item_id': item['item_id'],
                    'item_name': item['item_name'],
                    'current_stock': item['current_stock'],
                    'daily_usage': daily_usage,
                    'days_until_stockout': days_until_stockout,
                    'reorder_quantity': reorder_quantity,
                    'urgency': urgency,
                    'recommended_action': self._get_inventory_action(urgency, reorder_quantity)
                })
            # 긴급도별 정렬
            urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            predictions.sort(key=lambda x: urgency_order[x['urgency']])
            total_reorder_value = sum(p['reorder_quantity'] for p in predictions)
            critical_items = [p for p in predictions if p['urgency'] == 'critical']
            return {
                'success': True,
                'predictions': predictions,
                'total_reorder_value': total_reorder_value,
                'critical_items_count': len(critical_items),
                'summary': {
                    'total_items': len(predictions),
                    'need_reorder': len([p for p in predictions if p['reorder_quantity'] > 0]),
                    'critical_items': len(critical_items)
                }
            }
        except Exception as e:
            logger.error(f"재고 예측 실패: {e}")
            return {'error': f'재고 예측 실패: {str(e)}'}

    def predict_customer_churn(self) -> Dict[str, Any]:
        """고객 이탈 예측"""
        try:
            # 고객 데이터 준비
            df = self.prepare_customer_data()
            if df.empty:
                return {'error': '고객 데이터를 준비할 수 없습니다.'}

            # 이탈 위험 고객 식별
            high_risk_threshold = 0.7
            medium_risk_threshold = 0.4

            high_risk_customers = df[df['churn_probability'] >= high_risk_threshold]
            medium_risk_customers = df[(df['churn_probability'] >= medium_risk_threshold)
                                       & (df['churn_probability'] < high_risk_threshold)]

            # 이탈 방지 권장사항 생성
            recommendations = []

            for _, customer in high_risk_customers.iterrows():
                recommendations.append({
                    'user_id': customer['user_id'],
                    'churn_probability': customer['churn_probability'],
                    'risk_level': 'high',
                    'recommendations': [
                        '개인화된 할인 쿠폰 제공',
                        '고객 서비스 연락',
                        '맞춤형 프로모션 제안'
                    ]
                })

            for _, customer in medium_risk_customers.iterrows():
                recommendations.append({
                    'user_id': customer['user_id'],
                    'churn_probability': customer['churn_probability'],
                    'risk_level': 'medium',
                    'recommendations': [
                        '이메일 마케팅 캠페인',
                        '로열티 프로그램 안내'
                    ]
                })

            return {
                'success': True,
                'high_risk_customers': len(high_risk_customers),
                'medium_risk_customers': len(medium_risk_customers),
                'total_customers': len(df),
                'avg_churn_probability': df['churn_probability'].mean(),
                'recommendations': recommendations,
                'summary': {
                    'high_risk_percentage': len(high_risk_customers) / len(df) * 100,
                    'medium_risk_percentage': len(medium_risk_customers) / len(df) * 100
                }
            }

        except Exception as e:
            logger.error(f"고객 이탈 예측 실패: {e}")
            return {'error': f'고객 이탈 예측 실패: {str(e)}'}

    def predict_staff_requirements(self, days_ahead=14) -> Dict[str, Any]:
        """직원 필요량 예측"""
        try:
            # 직원 데이터 준비
            df = self.prepare_staff_data()
            if df.empty:
                return {'error': '직원 데이터를 준비할 수 없습니다.'}

            # 미래 날짜 생성
            future_dates = pd.date_range(start=datetime.now().date(), periods=days_ahead, freq='D')

            predictions = []
            for future_date in future_dates:
                # 해당 요일의 평균 필요 인력 계산
                day_of_week = future_date.weekday()
                day_data = df[df['day_of_week'] == day_of_week]

                if not day_data.empty:
                    avg_required = day_data['required_staff'].mean()
                    avg_demand = day_data['historical_demand'].mean()

                    # 계절성 및 이벤트 요인 적용
                    season_factor = self._get_season_factor(future_date.month)
                    event_factor = 1.5 if self._has_events(future_date.date()) else 1.0

                    predicted_staff = max(1, round(avg_required * season_factor * event_factor))

                    predictions.append({
                        'date': future_date.date().isoformat(),
                        'day_of_week': future_date.strftime('%A'),
                        'predicted_staff': predicted_staff,
                        'avg_demand': avg_demand,
                        'season_factor': season_factor,
                        'event_factor': event_factor
                    })

            total_staff_days = sum(p['predicted_staff'] for p in predictions)
            avg_daily_staff = total_staff_days / days_ahead

            return {
                'success': True,
                'predictions': predictions,
                'total_staff_days': total_staff_days,
                'avg_daily_staff': avg_daily_staff,
                'peak_days': [p for p in predictions if p['predicted_staff'] > avg_daily_staff * 1.2],
                'summary': {
                    'total_days': days_ahead,
                    'avg_staff_per_day': avg_daily_staff,
                    'max_staff_needed': max(p['predicted_staff'] for p in predictions)
                }
            }

        except Exception as e:
            logger.error(f"직원 필요량 예측 실패: {e}")
            return {'error': f'직원 필요량 예측 실패: {str(e)}'}

    # 헬퍼 메서드들
    def _get_season(self, month: int) -> str:
        """계절 반환"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'

    def _is_holiday(self, date) -> int:
        """공휴일 여부 (시뮬레이션)"""
        # 실제로는 공휴일 API나 데이터베이스 사용
        holidays = [1, 1, 3, 1, 5, 5, 6, 6, 8, 15, 10, 3, 10, 9, 12, 25]  # 월,일
        return 1 if date.month in holidays else 0

    def _get_weather_score(self, date) -> float:
        """날씨 점수 (시뮬레이션)"""
        # 실제로는 날씨 API 사용
        return np.random.uniform(0.3, 1.0)

    def _get_seasonality_factor(self, item_name: str) -> float:
        """계절성 요인 (시뮬레이션)"""
        # 실제로는 아이템별 계절성 데이터 사용
        return np.random.uniform(0.8, 1.2)

    def _has_events(self, date) -> int:
        """이벤트 여부 (시뮬레이션)"""
        # 실제로는 이벤트 데이터베이스 사용
        return np.random.choice([0, 1], p=[0.9, 0.1])

    def _get_season_factor(self, month: int) -> float:
        """계절 요인"""
        season_factors = {
            'winter': 0.8,
            'spring': 1.0,
            'summer': 1.2,
            'autumn': 1.1
        }
        season = self._get_season(month)
        return season_factors.get(season, 1.0)

    def _calculate_confidence(self, prediction: float, historical_data: pd.Series) -> float:
        """예측 신뢰도 계산"""
        if len(historical_data) == 0:
            return 0.5

        std = historical_data.std()
        mean = historical_data.mean()

        if std == 0:
            return 0.9

        # 예측값이 평균에서 얼마나 떨어져 있는지에 따라 신뢰도 계산
        z_score = abs(prediction - mean) / std
        confidence = max(0.1, 1.0 - (z_score / 3))  # 3 표준편차 내에 있으면 높은 신뢰도

        return confidence

    def _get_inventory_action(self, urgency: str, reorder_quantity: float) -> str:
        """재고 액션 권장사항"""
        if urgency == 'critical':
            return '즉시 주문 필요'
        elif urgency == 'high':
            return '이번 주 내 주문 권장'
        elif urgency == 'medium':
            return '다음 주 주문 고려'
        else:
            return '현재 상태 유지'


# 전역 서비스 인스턴스
ai_prediction_service = AdvancedAIPredictionService()

# API 엔드포인트들


@advanced_ai_prediction_bp.route('/api/ai/train/sales', methods=['POST'])
@login_required
def train_sales_model():
    """매출 예측 모델 훈련"""
    try:
        result = ai_prediction_service.train_sales_forecast_model()
        return jsonify(result)
    except Exception as e:
        logger.error(f"매출 모델 훈련 API 오류: {e}")
        return jsonify({'error': '모델 훈련에 실패했습니다.'}), 500


@advanced_ai_prediction_bp.route('/api/ai/predict/sales', methods=['GET'])
@login_required
def predict_sales():
    """매출 예측"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        result = ai_prediction_service.predict_sales_forecast(days_ahead)
        return jsonify(result)
    except Exception as e:
        logger.error(f"매출 예측 API 오류: {e}")
        return jsonify({'error': '매출 예측에 실패했습니다.'}), 500


@advanced_ai_prediction_bp.route('/api/ai/predict/inventory', methods=['GET'])
@login_required
def predict_inventory():
    """재고 예측"""
    try:
        result = ai_prediction_service.predict_inventory_needs()
        return jsonify(result)
    except Exception as e:
        logger.error(f"재고 예측 API 오류: {e}")
        return jsonify({'error': '재고 예측에 실패했습니다.'}), 500


@advanced_ai_prediction_bp.route('/api/ai/predict/customer-churn', methods=['GET'])
@login_required
def predict_customer_churn():
    """고객 이탈 예측"""
    try:
        result = ai_prediction_service.predict_customer_churn()
        return jsonify(result)
    except Exception as e:
        logger.error(f"고객 이탈 예측 API 오류: {e}")
        return jsonify({'error': '고객 이탈 예측에 실패했습니다.'}), 500


@advanced_ai_prediction_bp.route('/api/ai/predict/staff', methods=['GET'])
@login_required
def predict_staff():
    """직원 필요량 예측"""
    try:
        days_ahead = request.args.get('days', 14, type=int)
        result = ai_prediction_service.predict_staff_requirements(days_ahead)
        return jsonify(result)
    except Exception as e:
        logger.error(f"직원 예측 API 오류: {e}")
        return jsonify({'error': '직원 예측에 실패했습니다.'}), 500


@advanced_ai_prediction_bp.route('/api/ai/models/status', methods=['GET'])
@login_required
def get_models_status():
    """모델 상태 조회"""
    try:
        status = {}
        for model_name, metadata in ai_prediction_service.model_metadata.items():
            status[model_name] = {
                'last_trained': metadata['last_trained'].isoformat() if metadata['last_trained'] else None,
                'accuracy': metadata['accuracy'],
                'training_samples': metadata['training_samples'],
                'is_trained': metadata['last_trained'] is not None
            }

        return jsonify({
            'success': True,
            'models': status,
            'total_models': len(status)
        })
    except Exception as e:
        logger.error(f"모델 상태 조회 API 오류: {e}")
        return jsonify({'error': '모델 상태 조회에 실패했습니다.'}), 500


@advanced_ai_prediction_bp.route('/api/ai/predict/comprehensive', methods=['GET'])
@login_required
def comprehensive_prediction():
    """종합 예측 (모든 모델)"""
    try:
        results = {
            'sales_forecast': ai_prediction_service.predict_sales_forecast(30),
            'inventory_needs': ai_prediction_service.predict_inventory_needs(),
            'customer_churn': ai_prediction_service.predict_customer_churn(),
            'staff_requirements': ai_prediction_service.predict_staff_requirements(14)
        }

        # 종합 인사이트 생성
        insights = []

        # 매출 인사이트
        if results['sales_forecast'].get('success'):
            sales_data = results['sales_forecast']
            avg_daily = sales_data.get('avg_daily_sales', 0)
            if avg_daily > 1000000:
                insights.append({
                    'type': 'positive',
                    'title': '매출 전망 긍정적',
                    'description': f'향후 30일 평균 일일 매출이 {avg_daily:,.0f}원으로 예측됩니다.',
                    'priority': 'medium'
                })

        # 재고 인사이트
        if results['inventory_needs'].get('success'):
            inventory_data = results['inventory_needs']
            critical_count = inventory_data.get('critical_items_count', 0)
            if critical_count > 0:
                insights.append({
                    'type': 'critical',
                    'title': '긴급 재고 주문 필요',
                    'description': f'{critical_count}개 품목의 긴급 재주문이 필요합니다.',
                    'priority': 'high'
                })

        # 고객 이탈 인사이트
        if results['customer_churn'].get('success'):
            churn_data = results['customer_churn']
            high_risk = churn_data.get('high_risk_customers', 0)
            if high_risk > 5:
                insights.append({
                    'type': 'warning',
                    'title': '고객 이탈 위험',
                    'description': f'{high_risk}명의 고객이 이탈 위험에 있습니다.',
                    'priority': 'high'
                })

        return jsonify({
            'success': True,
            'predictions': results,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"종합 예측 API 오류: {e}")
        return jsonify({'error': '종합 예측에 실패했습니다.'}), 500
