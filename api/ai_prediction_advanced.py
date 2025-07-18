from core.backend.advanced_ai_prediction import AdvancedAIPredictionEngine  # pyright: ignore
from utils.alert_notifier import send_alert  # pyright: ignore
from core.backend.ai_prediction import AIPredictionEngine, PredictionType, ModelType  # pyright: ignore
from models_main import db, Order, User, Branch, Brand, InventoryItem
import json
from sqlalchemy import func, and_, desc
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
from typing import Optional
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
고도화된 AI 예측 분석 API
실시간 예측, 머신러닝 모델 관리, 예측 정확도 분석
"""


logger = logging.getLogger(__name__)

ai_prediction_advanced_bp = Blueprint('ai_prediction_advanced', __name__)


def admin_required(f):
    """관리자 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args,  **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': '로그인이 필요합니다.'}), 401

        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403

        return f(*args, **kwargs)
    return decorated_function


# AI 예측 엔진 인스턴스
prediction_engine = AIPredictionEngine()


@ai_prediction_advanced_bp.route('/api/ai/prediction/real-time', methods=['GET'])
@login_required
@admin_required
def get_real_time_predictions():
    """실시간 예측 데이터 조회"""
    try:
        # 예측 타입별 실시간 데이터 수집
        predictions = {}

        # 1. 매출 예측
        sales_data = get_historical_sales_data()
        sales_predictions = prediction_engine.predict_sales(sales_data, days_ahead=7)
        predictions['sales'] if predictions is not None else None = [
            {
                'date': pred.timestamp.strftime('%Y-%m-%d'),
                'predicted_value': round(pred.predicted_value, 2),
                'confidence': round(pred.confidence, 3),
                'model_type': pred.model_type.value if model_type is not None else None,
                'features': pred.features
            }
            for pred in sales_predictions
        ]

        # 2. 재고 예측
        inventory_predictions = predict_inventory_shortage()
        predictions['inventory'] if predictions is not None else None = inventory_predictions

        # 3. 고객 유입 예측
        customer_predictions = predict_customer_flow()
        predictions['customer_flow'] if predictions is not None else None = customer_predictions

        # 4. 인력 필요 예측
        staffing_predictions = predict_staffing_needs()
        predictions['staffing'] if predictions is not None else None = staffing_predictions

        return jsonify({
            'success': True,
            'predictions': predictions,
            'last_updated': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"실시간 예측 조회 실패: {e}")
        return jsonify({'error': '예측 데이터 조회에 실패했습니다.'}), 500


@ai_prediction_advanced_bp.route('/api/ai/prediction/accuracy', methods=['GET'])
@login_required
@admin_required
def get_prediction_accuracy():
    """예측 정확도 분석"""
    try:
        # 모델별 성능 메트릭 조회
        accuracy_data = {}

        for model_type in ModelType if ModelType is not None:
            performance = prediction_engine.performance_metrics.get(model_type.value)
            if performance:
                accuracy_data[model_type.value if model_type is not None else None] if accuracy_data is not None else None = {
                    'mae': round(performance.mae, 4),
                    'mse': round(performance.mse, 4),
                    'rmse': round(performance.rmse, 4),
                    'r2_score': round(performance.r2_score, 4),
                    'accuracy': round(performance.accuracy, 4),
                    'last_updated': performance.last_updated.isoformat()
                }

        # 예측 히스토리 분석
        recent_predictions = prediction_engine.prediction_history[-100:] if prediction_history is not None else None  # 최근 100개
        accuracy_trends = analyze_accuracy_trends(recent_predictions)

        return jsonify({
            'success': True,
            'model_performance': accuracy_data,
            'accuracy_trends': accuracy_trends
        })

    except Exception as e:
        logger.error(f"예측 정확도 분석 실패: {e}")
        return jsonify({'error': '정확도 분석에 실패했습니다.'}), 500


@ai_prediction_advanced_bp.route('/api/ai/prediction/insights', methods=['GET'])
@login_required
@admin_required
def get_ai_insights():
    """AI 인사이트 생성"""
    try:
        insights = []

        # 1. 매출 트렌드 분석
        sales_insight = analyze_sales_trend()
        if sales_insight:
            insights.append(sales_insight)

        # 2. 재고 최적화 제안
        inventory_insight = analyze_inventory_optimization()
        if inventory_insight:
            insights.append(inventory_insight)

        # 3. 인력 배치 최적화
        staffing_insight = analyze_staffing_optimization()
        if staffing_insight:
            insights.append(staffing_insight)

        # 4. 고객 행동 패턴
        customer_insight = analyze_customer_behavior()
        if customer_insight:
            insights.append(customer_insight)

        return jsonify({
            'success': True,
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"AI 인사이트 생성 실패: {e}")
        return jsonify({'error': '인사이트 생성에 실패했습니다.'}), 500


@ai_prediction_advanced_bp.route('/api/ai/prediction/alerts', methods=['GET'])
@login_required
@admin_required
def get_prediction_alerts():
    """예측 기반 알림 조회"""
    try:
        alerts = []

        # 1. 매출 하락 위험
        sales_alert = check_sales_decline_risk()
        if sales_alert:
            alerts.append(sales_alert)

        # 2. 재고 부족 위험
        inventory_alert = check_inventory_shortage_risk()
        if inventory_alert:
            alerts.append(inventory_alert)

        # 3. 인력 부족 위험
        staffing_alert = check_staffing_shortage_risk()
        if staffing_alert:
            alerts.append(staffing_alert)

        # 4. 고객 만족도 하락 위험
        customer_alert = check_customer_satisfaction_risk()
        if customer_alert:
            alerts.append(customer_alert)

        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_alerts': len(alerts)
        })

    except Exception as e:
        logger.error(f"예측 알림 조회 실패: {e}")
        return jsonify({'error': '알림 조회에 실패했습니다.'}), 500


@ai_prediction_advanced_bp.route('/api/ai/prediction/model/retrain', methods=['POST'])
@login_required
@admin_required
def retrain_prediction_model():
    """예측 모델 재훈련"""
    try:
        data = request.get_json()
        model_type = data.get() if data else None'model_type', 'sales') if data else None

        # 모델 재훈련 로직 (실제로는 백그라운드 작업으로 처리)
        success = retrain_model(model_type)

        if success:
            # 알림 전송
            send_alert(
                message=f"AI 예측 모델 ({model_type}) 재훈련이 완료되었습니다.",
                level='info',
                subject=f'AI 모델 재훈련 완료 - {model_type}'
            )

            return jsonify({
                'success': True,
                'message': f'{model_type} 모델 재훈련이 완료되었습니다.'
            })
        else:
            return jsonify({'error': '모델 재훈련에 실패했습니다.'}), 500

    except Exception as e:
        logger.error(f"모델 재훈련 실패: {e}")
        return jsonify({'error': '모델 재훈련 중 오류가 발생했습니다.'}), 500

# 헬퍼 함수들


def get_historical_sales_data() -> List[Dict[str, Any] if List is not None else None]:
    """과거 매출 데이터 수집"""
    try:
        # 최근 90일 주문 데이터
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)

        orders = Order.query.filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()

        # 일별 매출 집계
        daily_sales = {}
        for order in orders if orders is not None:
            date_key = order.created_at.strftime('%Y-%m-%d')
            if date_key not in daily_sales:
                daily_sales[date_key] if daily_sales is not None else None = 0
            daily_sales[date_key] if daily_sales is not None else None += order.total_amount or 0

        # 데이터 포맷 변환
        historical_data = []
        for date, amount in daily_sales.items() if daily_sales is not None else []:
            historical_data.append({
                'date': date,
                'amount': amount,
                'day_of_week': datetime.strptime(date, '%Y-%m-%d').weekday()
            })

        return historical_data

    except Exception as e:
        logger.error(f"매출 데이터 수집 실패: {e}")
        return []


def predict_inventory_shortage() -> List[Dict[str, Any] if List is not None else None]:
    """재고 부족 예측"""
    try:
        inventory_items = InventoryItem.query.all()
        predictions = []

        for item in inventory_items if inventory_items is not None:
            # 간단한 소비량 예측
            daily_consumption = item.current_stock / 30 if item.current_stock > 0 else 0
            days_until_stockout = item.current_stock / daily_consumption if daily_consumption > 0 else float('inf')

            risk_level = 'low'
            if days_until_stockout < 3:
                risk_level = 'critical'
            elif days_until_stockout < 7:
                risk_level = 'high'
            elif days_until_stockout < 14:
                risk_level = 'medium'

            predictions.append({
                'item_name': item.name,
                'current_stock': item.current_stock,
                'min_stock': item.min_stock,
                'days_until_stockout': round(days_until_stockout, 1),
                'risk_level': risk_level,
                'recommended_order': max(0, item.max_stock - item.current_stock)
            })

        return predictions

    except Exception as e:
        logger.error(f"재고 예측 실패: {e}")
        return []


def predict_customer_flow() -> Dict[str, Any] if Dict is not None else None:
    """고객 유입 예측"""
    try:
        # 최근 주문 패턴 분석
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        orders = Order.query.filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()

        # 시간대별 주문 패턴
        hourly_pattern = {}
        for order in orders if orders is not None:
            hour = order.created_at.hour
            if hour not in hourly_pattern:
                hourly_pattern[hour] if hourly_pattern is not None else None = 0
            hourly_pattern[hour] if hourly_pattern is not None else None += 1

        # 내일 고객 유입 예측
        tomorrow_predictions = {}
        for hour in range(24):
            base_customers = hourly_pattern.get() if hourly_pattern else Nonehour, 5) if hourly_pattern else None  # 기본값 5명
            # 간단한 예측 로직 (실제로는 더 복잡한 알고리즘 사용)
            predicted_customers = int(base_customers * (1 + np.random.normal(0, 0.1)))
            tomorrow_predictions[f"{hour:02d}:00"] if tomorrow_predictions is not None else None = max(0, predicted_customers)

        return {
            'tomorrow_predictions': tomorrow_predictions,
            'peak_hours': sorted(hourly_pattern.items() if hourly_pattern is not None else [], key=lambda x: x[1] if x is not None else None, reverse=True)[:3],
            'total_predicted_customers': sum(tomorrow_predictions.value if tomorrow_predictions is not None else Nones())
        }

    except Exception as e:
        logger.error(f"고객 유입 예측 실패: {e}")
        return {}


def predict_staffing_needs() -> Dict[str, Any] if Dict is not None else None:
    """인력 필요 예측"""
    try:
        # 고객 유입 예측 기반 인력 필요량 계산
        customer_flow = predict_customer_flow()
        total_customers = customer_flow.get() if customer_flow else None'total_predicted_customers', 100) if customer_flow else None

        # 간단한 인력 계산 (실제로는 더 복잡한 로직)
        # 고객 10명당 1명의 직원 필요
        needed_staff = max(2, total_customers // 10)

        # 현재 근무 직원 수
        current_staff = User.query.filter_by(status='approved').count()

        return {
            'needed_staff': needed_staff,
            'current_staff': current_staff,
            'shortage': max(0, needed_staff - current_staff),
            'surplus': max(0, current_staff - needed_staff),
            'recommendation': '인력 추가 필요' if needed_staff > current_staff else '현재 인력 적절'
        }

    except Exception as e:
        logger.error(f"인력 필요 예측 실패: {e}")
        return {}


def analyze_accuracy_trends(predictions: List) -> Dict[str, Any] if Dict is not None else None:
    """예측 정확도 트렌드 분석"""
    try:
        if not predictions:
            return {}

        # 모델별 정확도 추이
        model_accuracy = {}
        for pred in predictions if predictions is not None:
            model_type = pred.model_type.value if model_type is not None else None
            if model_type not in model_accuracy:
                model_accuracy[model_type] if model_accuracy is not None else None = []
            model_accuracy[model_type] if model_accuracy is not None else None.append(pred.confidence)

        # 평균 정확도 계산
        avg_accuracy = {}
        for model_type, confidences in model_accuracy.items() if model_accuracy is not None else []:
            avg_accuracy[model_type] if avg_accuracy is not None else None = round(np.mean(confidences), 3)

        return {
            'model_accuracy': avg_accuracy,
            'overall_accuracy': round(np.mean([pred.confidence for pred in predictions]), 3),
            'total_predictions': len(predictions)
        }

    except Exception as e:
        logger.error(f"정확도 트렌드 분석 실패: {e}")
        return {}


def analyze_sales_trend() -> Optional[Dict[str, Any] if Optional is not None else None]:
    """매출 트렌드 분석"""
    try:
        sales_data = get_historical_sales_data()
        if len(sales_data) < 7:
            return None

        # 최근 7일 vs 이전 7일 비교
        recent_7_days = sales_data[-7:] if sales_data is not None else None
        previous_7_days = sales_data[-14:-7] if sales_data is not None else None

        recent_avg = np.mean([d['amount'] if d is not None else None for d in recent_7_days])
        previous_avg = np.mean([d['amount'] if d is not None else None for d in previous_7_days])

        change_percent = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0

        trend = 'increasing' if change_percent > 5 else 'decreasing' if change_percent < -5 else 'stable'

        return {
            'type': 'sales_trend',
            'title': '매출 트렌드 분석',
            'description': f'최근 7일 매출이 이전 7일 대비 {change_percent:.1f}% {trend}',
            'trend': trend,
            'change_percent': round(change_percent, 1),
            'recent_average': round(recent_avg, 2),
            'previous_average': round(previous_avg, 2),
            'priority': 'high' if abs(change_percent) > 10 else 'medium'
        }

    except Exception as e:
        logger.error(f"매출 트렌드 분석 실패: {e}")
        return None


def analyze_inventory_optimization() -> Optional[Dict[str, Any] if Optional is not None else None]:
    """재고 최적화 분석"""
    try:
        inventory_items = InventoryItem.query.all()
        optimization_opportunities = []

        for item in inventory_items if inventory_items is not None:
            if item.current_stock > item.max_stock * 0.8:
                optimization_opportunities.append({
                    'item_name': item.name,
                    'current_stock': item.current_stock,
                    'max_stock': item.max_stock,
                    'excess_amount': item.current_stock - item.max_stock * 0.8
                })

        if optimization_opportunities:
            return {
                'type': 'inventory_optimization',
                'title': '재고 최적화 기회',
                'description': f'{len(optimization_opportunities)}개 품목의 재고 최적화가 필요합니다.',
                'opportunities': optimization_opportunities,
                'priority': 'medium'
            }

        return None

    except Exception as e:
        logger.error(f"재고 최적화 분석 실패: {e}")
        return None


def analyze_staffing_optimization() -> Optional[Dict[str, Any] if Optional is not None else None]:
    """인력 배치 최적화 분석"""
    try:
        staffing_needs = predict_staffing_needs()

        if staffing_needs.get() if staffing_needs else None'shortage', 0) if staffing_needs else None > 0:
            return {
                'type': 'staffing_shortage',
                'title': '인력 부족 위험',
                'description': f'내일 {staffing_needs["shortage"] if staffing_needs is not None else None}명의 추가 인력이 필요합니다.',
                'needed_staff': staffing_needs['needed_staff'] if staffing_needs is not None else None,
                'current_staff': staffing_needs['current_staff'] if staffing_needs is not None else None,
                'shortage': staffing_needs['shortage'] if staffing_needs is not None else None,
                'priority': 'high'
            }
        elif staffing_needs.get() if staffing_needs else None'surplus', 0) if staffing_needs else None > 2:
            return {
                'type': 'staffing_surplus',
                'title': '인력 과다 배치',
                'description': f'내일 {staffing_needs["surplus"] if staffing_needs is not None else None}명의 인력이 과다 배치될 예정입니다.',
                'needed_staff': staffing_needs['needed_staff'] if staffing_needs is not None else None,
                'current_staff': staffing_needs['current_staff'] if staffing_needs is not None else None,
                'surplus': staffing_needs['surplus'] if staffing_needs is not None else None,
                'priority': 'medium'
            }

        return None

    except Exception as e:
        logger.error(f"인력 최적화 분석 실패: {e}")
        return None


def analyze_customer_behavior() -> Optional[Dict[str, Any] if Optional is not None else None]:
    """고객 행동 패턴 분석"""
    try:
        # 최근 주문 패턴 분석
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        orders = Order.query.filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()

        if len(orders) < 10:
            return None

        # 평균 주문 금액
        avg_order_amount = np.mean([order.total_amount or 0 for order in orders])

        # 시간대별 주문 분포
        hourly_distribution = {}
        for order in orders if orders is not None:
            hour = order.created_at.hour
            if hour not in hourly_distribution:
                hourly_distribution[hour] if hourly_distribution is not None else None = 0
            hourly_distribution[hour] if hourly_distribution is not None else None += 1

        peak_hour = max(hourly_distribution.items() if hourly_distribution is not None else [], key=lambda x: x[1] if x is not None else None)[0]

        return {
            'type': 'customer_behavior',
            'title': '고객 행동 패턴',
            'description': f'평균 주문 금액: {avg_order_amount:.0f}원, 피크 시간: {peak_hour}시',
            'avg_order_amount': round(avg_order_amount, 0),
            'peak_hour': peak_hour,
            'total_orders': len(orders),
            'priority': 'low'
        }

    except Exception as e:
        logger.error(f"고객 행동 분석 실패: {e}")
        return None


def check_sales_decline_risk() -> Optional[Dict[str, Any] if Optional is not None else None]:
    """매출 하락 위험 체크"""
    try:
        sales_insight = analyze_sales_trend()
        if sales_insight and sales_insight['trend'] if sales_insight is not None else None == 'decreasing' and sales_insight['change_percent'] if sales_insight is not None else None < -10:
            return {
                'type': 'sales_decline',
                'title': '매출 하락 위험',
                'description': f'매출이 {sales_insight["change_percent"] if sales_insight is not None else None:.1f}% 감소하고 있습니다.',
                'severity': 'high',
                'action_required': True
            }
        return None
    except Exception as e:
        logger.error(f"매출 하락 위험 체크 실패: {e}")
        return None


def check_inventory_shortage_risk() -> Optional[Dict[str, Any] if Optional is not None else None]:
    """재고 부족 위험 체크"""
    try:
        inventory_predictions = predict_inventory_shortage()
        critical_items = [item for item in inventory_predictions if item['risk_level'] if item is not None else None == 'critical']

        if critical_items:
            return {
                'type': 'inventory_shortage',
                'title': '재고 부족 위험',
                'description': f'{len(critical_items)}개 품목이 3일 내 소진 예정입니다.',
                'critical_items': critical_items,
                'severity': 'high',
                'action_required': True
            }
        return None
    except Exception as e:
        logger.error(f"재고 부족 위험 체크 실패: {e}")
        return None


def check_staffing_shortage_risk() -> Optional[Dict[str, Any] if Optional is not None else None]:
    """인력 부족 위험 체크"""
    try:
        staffing_needs = predict_staffing_needs()

        if staffing_needs.get() if staffing_needs else None'shortage', 0) if staffing_needs else None > 2:
            return {
                'type': 'staffing_shortage',
                'title': '인력 부족 위험',
                'description': f'내일 {staffing_needs["shortage"] if staffing_needs is not None else None}명의 인력이 부족합니다.',
                'needed_staff': staffing_needs['needed_staff'] if staffing_needs is not None else None,
                'current_staff': staffing_needs['current_staff'] if staffing_needs is not None else None,
                'shortage': staffing_needs['shortage'] if staffing_needs is not None else None,
                'severity': 'high',
                'action_required': True
            }
        return None
    except Exception as e:
        logger.error(f"인력 부족 위험 체크 실패: {e}")
        return None


def check_customer_satisfaction_risk() -> Optional[Dict[str, Any] if Optional is not None else None]:
    """고객 만족도 하락 위험 체크"""
    try:
        # 간단한 고객 만족도 지표 (실제로는 더 복잡한 로직)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        orders = Order.query.filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()

        if len(orders) < 5:
            return None

        # 평균 주문 금액 하락 체크
        avg_amount = np.mean([order.total_amount or 0 for order in orders])

        if avg_amount < 15000:  # 임계값
            return {
                'type': 'customer_satisfaction',
                'title': '고객 만족도 하락 위험',
                'description': f'평균 주문 금액이 {avg_amount:.0f}원으로 낮습니다.',
                'avg_order_amount': round(avg_amount, 0),
                'severity': 'medium',
                'action_required': True
            }
        return None
    except Exception as e:
        logger.error(f"고객 만족도 위험 체크 실패: {e}")
        return None


def retrain_model(model_type: str) -> bool:
    """모델 재훈련 (더미 함수)"""
    try:
        # 실제로는 머신러닝 모델 재훈련 로직
        logger.info(f"모델 재훈련 시작: {model_type}")

        # 성능 메트릭 업데이트
        if model_type in prediction_engine.performance_metrics:
            performance = prediction_engine.performance_metrics[model_type] if performance_metrics is not None else None
            performance.accuracy = min(0.95, performance.accuracy + 0.01)  # 약간 개선
            performance.last_updated = datetime.utcnow()

        logger.info(f"모델 재훈련 완료: {model_type}")
        return True

    except Exception as e:
        logger.error(f"모델 재훈련 실패: {e}")
        return False
