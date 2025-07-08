from flask import Blueprint, request, jsonify, g, current_app, Response
from functools import wraps
from models import User, Order, Attendance, Schedule, InventoryItem, Notification, db
from extensions import db
import logging
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import joblib
import os
from sqlalchemy import func, and_, or_, desc
from api.gateway import token_required, role_required, admin_required, manager_required, employee_required, log_request
from typing import Dict, Any, Optional, Union

# 로깅 설정
logger = logging.getLogger(__name__)

# AI 예측 및 자동화 API Blueprint
ai_prediction = Blueprint('ai_prediction', __name__, url_prefix='/api/ai')

# 모델 저장 디렉토리
MODEL_DIR = 'models'
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# 전역 변수로 모델 저장 (타입 힌트 추가)
models: Dict[str, Optional[Union[RandomForestRegressor, RandomForestClassifier, LinearRegression, LogisticRegression]]] = {
    'sales_prediction': None,
    'staff_optimization': None,
    'inventory_forecast': None,
    'customer_behavior': None,
    'order_prediction': None,
    'attendance_prediction': None
}

# 스케일러 저장 (타입 힌트 추가)
scalers: Dict[str, Optional[StandardScaler]] = {}

def generate_sample_data():
    """샘플 데이터 생성 (실제로는 DB에서 가져옴)"""
    np.random.seed(42)
    
    # 매출 예측 데이터
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    sales_data = []
    
    for date in dates:
        # 계절성과 요일 효과 추가
        day_of_week = date.weekday()
        month = date.month
        
        # 기본 매출
        base_sales = 1000000
        
        # 요일 효과 (주말이 더 높음)
        day_effect = 1.3 if day_of_week >= 5 else 1.0
        
        # 계절성 효과
        seasonal_effect = 1.2 if month in [7, 8, 12] else 0.9 if month in [1, 2] else 1.0
        
        # 랜덤 노이즈
        noise = np.random.normal(0, 0.1)
        
        sales = base_sales * day_effect * seasonal_effect * (1 + noise)
        
        sales_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': day_of_week,
            'month': month,
            'is_weekend': 1 if day_of_week >= 5 else 0,
            'is_holiday': 1 if date.month == 12 and date.day == 25 else 0,
            'temperature': np.random.normal(20, 10),
            'sales': int(sales)
        })
    
    return pd.DataFrame(sales_data)

def train_sales_prediction_model():
    """매출 예측 모델 훈련"""
    try:
        # 샘플 데이터 생성
        df = generate_sample_data()
        
        # 특성 선택
        features = ['day_of_week', 'month', 'is_weekend', 'is_holiday', 'temperature']
        X = df[features]
        y = df['sales']
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 스케일링
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 모델 훈련
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # 예측 및 평가
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # 모델 저장
        models['sales_prediction'] = model
        scalers['sales_prediction'] = scaler
        
        # 모델 파일로 저장
        joblib.dump(model, os.path.join(MODEL_DIR, 'sales_prediction_model.pkl'))
        joblib.dump(scaler, os.path.join(MODEL_DIR, 'sales_prediction_scaler.pkl'))
        
        return {
            'success': True,
            'rmse': rmse,
            'feature_importance': dict(zip(features, model.feature_importances_))
        }
        
    except Exception as e:
        logger.error(f"매출 예측 모델 훈련 오류: {str(e)}")
        return {'success': False, 'error': str(e)}

def train_staff_optimization_model():
    """직원 최적화 모델 훈련"""
    try:
        # 샘플 데이터 생성
        np.random.seed(42)
        n_samples = 1000
        
        # 특성 생성
        data = {
            'order_volume': np.random.poisson(50, n_samples),
            'time_of_day': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'is_weekend': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            'weather': np.random.choice(['sunny', 'rainy', 'cloudy'], n_samples),
            'special_event': np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
        }
        
        df = pd.DataFrame(data)
        
        # 목표 변수 생성 (필요한 직원 수)
        df['required_staff'] = (
            df['order_volume'] // 10 + 
            (df['time_of_day'] >= 11).astype(int) + 
            (df['time_of_day'] <= 14).astype(int) +
            df['is_weekend'] * 2 +
            (df['special_event'] * 3)
        ).clip(lower=1, upper=10)
        
        # 특성 선택
        features = ['order_volume', 'time_of_day', 'day_of_week', 'is_weekend', 'special_event']
        X = df[features]
        y = df['required_staff']
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 모델 훈련
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 예측 및 평가
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # 모델 저장
        models['staff_optimization'] = model
        
        # 모델 파일로 저장
        joblib.dump(model, os.path.join(MODEL_DIR, 'staff_optimization_model.pkl'))
        
        return {
            'success': True,
            'rmse': rmse,
            'feature_importance': dict(zip(features, model.feature_importances_))
        }
        
    except Exception as e:
        logger.error(f"직원 최적화 모델 훈련 오류: {str(e)}")
        return {'success': False, 'error': str(e)}

def train_inventory_forecast_model():
    """재고 예측 모델 훈련"""
    try:
        # 샘플 데이터 생성
        np.random.seed(42)
        n_samples = 1000
        
        # 특성 생성
        data = {
            'days_since_order': np.random.randint(1, 30, n_samples),
            'current_stock': np.random.randint(0, 100, n_samples),
            'daily_usage': np.random.poisson(10, n_samples),
            'season': np.random.choice(['spring', 'summer', 'fall', 'winter'], n_samples),
            'is_weekend': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            'special_event': np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
        }
        
        df = pd.DataFrame(data)
        
        # 목표 변수 생성 (재주문 필요 여부)
        df['need_reorder'] = (
            (df['current_stock'] < 20) | 
            (df['current_stock'] < df['daily_usage'] * 3)
        ).astype(int)
        
        # 특성 선택
        features = ['days_since_order', 'current_stock', 'daily_usage', 'is_weekend', 'special_event']
        X = df[features]
        y = df['need_reorder']
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 모델 훈련
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 예측 및 평가
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 모델 저장
        models['inventory_forecast'] = model
        
        # 모델 파일로 저장
        joblib.dump(model, os.path.join(MODEL_DIR, 'inventory_forecast_model.pkl'))
        
        return {
            'success': True,
            'accuracy': accuracy,
            'feature_importance': dict(zip(features, model.feature_importances_))
        }
        
    except Exception as e:
        logger.error(f"재고 예측 모델 훈련 오류: {str(e)}")
        return {'success': False, 'error': str(e)}

@ai_prediction.route('/train-models', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def train_models():
    """모든 AI 모델 훈련"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        model_type = data.get('model_type', 'all')
        
        results = {}
        
        if model_type == 'all' or model_type == 'sales':
            results['sales_prediction'] = train_sales_prediction_model()
        
        if model_type == 'all' or model_type == 'staff':
            results['staff_optimization'] = train_staff_optimization_model()
        
        if model_type == 'all' or model_type == 'inventory':
            results['inventory_forecast'] = train_inventory_forecast_model()
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"모델 훈련 오류: {str(e)}")
        return jsonify({'error': 'Failed to train models'}), 500

@ai_prediction.route('/predict-sales', methods=['POST'])
@token_required
@role_required(['admin', 'manager', 'super_admin'])
@log_request
def predict_sales():
    """매출 예측"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 모델 로드
        model = models.get('sales_prediction')
        scaler = scalers.get('sales_prediction')
        
        if model is None or scaler is None:
            # 모델이 없으면 훈련
            result = train_sales_prediction_model()
            if not result['success']:
                return jsonify({'error': 'Failed to train model'}), 500
            model = models.get('sales_prediction')
            scaler = scalers.get('sales_prediction')
            if model is None or scaler is None:
                return jsonify({'error': 'Model training failed'}), 500
        
        # 입력 데이터 준비
        features = ['day_of_week', 'month', 'is_weekend', 'is_holiday', 'temperature']
        input_data = []
        
        for feature in features:
            if feature not in data:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
            input_data.append(data[feature])
        
        # 예측
        input_scaled = scaler.transform([input_data])
        prediction = model.predict(input_scaled)[0]
        
        # 신뢰 구간 계산 (간단한 방법)
        confidence_interval = prediction * 0.1  # 10% 오차
        
        return jsonify({
            'predicted_sales': int(prediction),
            'confidence_interval': {
                'lower': int(prediction - confidence_interval),
                'upper': int(prediction + confidence_interval)
            },
            'features_used': features
        })
        
    except Exception as e:
        logger.error(f"매출 예측 오류: {str(e)}")
        return jsonify({'error': 'Failed to predict sales'}), 500

@ai_prediction.route('/optimize-staff', methods=['POST'])
@token_required
@role_required(['admin', 'manager', 'super_admin'])
@log_request
def optimize_staff():
    """직원 최적화"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 모델 로드
        model = models.get('staff_optimization')
        
        if model is None:
            # 모델이 없으면 훈련
            result = train_staff_optimization_model()
            if not result['success']:
                return jsonify({'error': 'Failed to train model'}), 500
            model = models.get('staff_optimization')
            if model is None:
                return jsonify({'error': 'Model training failed'}), 500
        
        # 입력 데이터 준비
        features = ['order_volume', 'time_of_day', 'day_of_week', 'is_weekend', 'special_event']
        input_data = []
        
        for feature in features:
            if feature not in data:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
            input_data.append(data[feature])
        
        # 예측
        prediction = model.predict([input_data])[0]
        
        # 권장사항 생성
        recommendations = []
        if prediction > 8:
            recommendations.append("매우 바쁜 시간대입니다. 추가 직원 배치를 고려하세요.")
        elif prediction > 5:
            recommendations.append("보통 수준의 업무량입니다. 현재 인력으로 충분합니다.")
        else:
            recommendations.append("업무량이 적습니다. 인력 조정을 고려하세요.")
        
        return jsonify({
            'recommended_staff': int(prediction),
            'recommendations': recommendations,
            'features_used': features
        })
        
    except Exception as e:
        logger.error(f"직원 최적화 오류: {str(e)}")
        return jsonify({'error': 'Failed to optimize staff'}), 500

@ai_prediction.route('/forecast-inventory', methods=['POST'])
@token_required
@role_required(['admin', 'manager', 'super_admin'])
@log_request
def forecast_inventory():
    """재고 예측"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 모델 로드
        model = models.get('inventory_forecast')
        
        if model is None:
            # 모델이 없으면 훈련
            result = train_inventory_forecast_model()
            if not result['success']:
                return jsonify({'error': 'Failed to train model'}), 500
            model = models.get('inventory_forecast')
            if model is None:
                return jsonify({'error': 'Model training failed'}), 500
        
        # 입력 데이터 검증
        features = ['days_since_order', 'current_stock', 'daily_usage', 'is_weekend', 'special_event']
        input_data = []
        
        for feature in features:
            if feature not in data:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
            input_data.append(data[feature])
        
        # 예측
        prediction = model.predict([input_data])[0]
        
        # predict_proba는 분류 모델에서만 사용 가능
        # RandomForestClassifier만 predict_proba를 지원
        confidence = 0.8  # 기본값
        try:
            if (hasattr(model, 'predict_proba') and 
                hasattr(model, '_estimator_type') and 
                model._estimator_type == 'classifier' and
                isinstance(model, RandomForestClassifier)):
                probability = model.predict_proba([input_data])[0]
                confidence = float(max(probability))
        except (AttributeError, TypeError):
            # predict_proba가 없거나 호출할 수 없는 경우 기본값 사용
            pass
        
        return jsonify({
            'need_reorder': bool(prediction),
            'confidence': confidence,
            'recommendations': [
                "재주문이 필요합니다." if prediction else "현재 재고가 충분합니다.",
                f"현재 재고: {data['current_stock']}개",
                f"일일 사용량: {data['daily_usage']}개"
            ]
        })
        
    except Exception as e:
        logger.error(f"재고 예측 오류: {str(e)}")
        return jsonify({'error': 'Failed to forecast inventory'}), 500

@ai_prediction.route('/automation-rules', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def automation_rules():
    """자동화 규칙 관리"""
    try:
        if request.method == 'GET':
            # 자동화 규칙 조회
            rules = [
                {
                    'id': 1,
                    'name': '재고 부족 알림',
                    'type': 'inventory_alert',
                    'condition': 'current_stock < threshold',
                    'action': 'send_notification',
                    'enabled': True,
                    'threshold': 20
                },
                {
                    'id': 2,
                    'name': '매출 예측 알림',
                    'type': 'sales_prediction',
                    'condition': 'predicted_sales > threshold',
                    'action': 'send_notification',
                    'enabled': True,
                    'threshold': 1500000
                },
                {
                    'id': 3,
                    'name': '직원 부족 알림',
                    'type': 'staff_shortage',
                    'condition': 'required_staff > available_staff',
                    'action': 'send_notification',
                    'enabled': True
                }
            ]
            
            return jsonify({'rules': rules})
        
        elif request.method == 'POST':
            # 새 규칙 생성
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # 실제로는 데이터베이스에 저장
            new_rule = {
                'id': 4,  # 실제로는 자동 생성
                'name': data.get('name'),
                'type': data.get('type'),
                'condition': data.get('condition'),
                'action': data.get('action'),
                'enabled': data.get('enabled', True),
                'threshold': data.get('threshold')
            }
            
            return jsonify({
                'success': True,
                'rule': new_rule
            })
        
        elif request.method == 'PUT':
            # 규칙 업데이트
            data = request.get_json()
            rule_id = request.args.get('id')
            
            if not data or not rule_id:
                return jsonify({'error': 'Missing data or rule ID'}), 400
            
            # 실제로는 데이터베이스에서 업데이트
            updated_rule = {
                'id': int(rule_id),
                'name': data.get('name'),
                'type': data.get('type'),
                'condition': data.get('condition'),
                'action': data.get('action'),
                'enabled': data.get('enabled'),
                'threshold': data.get('threshold')
            }
            
            return jsonify({
                'success': True,
                'rule': updated_rule
            })
        
        elif request.method == 'DELETE':
            # 규칙 삭제
            rule_id = request.args.get('id')
            
            if not rule_id:
                return jsonify({'error': 'Missing rule ID'}), 400
            
            # 실제로는 데이터베이스에서 삭제
            return jsonify({
                'success': True,
                'message': f'Rule {rule_id} deleted successfully'
            })
    
    except Exception as e:
        logger.error(f"자동화 규칙 관리 오류: {str(e)}")
        return jsonify({'error': 'Failed to manage automation rules'}), 500

@ai_prediction.route('/predict-customer-behavior', methods=['POST'])
@token_required
@role_required(['admin', 'manager', 'super_admin'])
@log_request
def predict_customer_behavior():
    """고객 행동 예측"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 고객 행동 예측 (샘플)
        customer_id = data.get('customer_id')
        order_history = data.get('order_history', [])
        visit_frequency = data.get('visit_frequency', 0)
        avg_order_value = data.get('avg_order_value', 0)
        
        # 간단한 예측 로직
        if visit_frequency > 10 and avg_order_value > 50000:
            segment = 'VIP'
            next_visit_probability = 0.9
        elif visit_frequency > 5 and avg_order_value > 30000:
            segment = 'Regular'
            next_visit_probability = 0.7
        else:
            segment = 'Occasional'
            next_visit_probability = 0.4
        
        # 추천 상품
        recommendations = [
            '시즌 메뉴',
            '프리미엄 음료',
            '디저트 세트'
        ]
        
        return jsonify({
            'customer_segment': segment,
            'next_visit_probability': next_visit_probability,
            'recommended_products': recommendations,
            'lifetime_value_prediction': avg_order_value * visit_frequency * 12
        })
        
    except Exception as e:
        logger.error(f"고객 행동 예측 오류: {str(e)}")
        return jsonify({'error': 'Failed to predict customer behavior'}), 500

@ai_prediction.route('/model-performance', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def model_performance():
    """모델 성능 모니터링"""
    try:
        performance_data = {
            'sales_prediction': {
                'accuracy': 0.85,
                'last_updated': '2024-01-15',
                'training_samples': 1000,
                'prediction_count': 150
            },
            'staff_optimization': {
                'accuracy': 0.78,
                'last_updated': '2024-01-15',
                'training_samples': 800,
                'prediction_count': 120
            },
            'inventory_forecast': {
                'accuracy': 0.92,
                'last_updated': '2024-01-15',
                'training_samples': 600,
                'prediction_count': 90
            }
        }
        
        return jsonify({
            'performance': performance_data,
            'overall_accuracy': 0.85
        })
        
    except Exception as e:
        logger.error(f"모델 성능 모니터링 오류: {str(e)}")
        return jsonify({'error': 'Failed to get model performance'}), 500

@ai_prediction.route('/auto-schedule', methods=['POST'])
@token_required
@role_required(['admin', 'manager', 'super_admin'])
@log_request
def auto_schedule():
    """AI 기반 자동 스케줄링"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 입력 데이터
        date = data.get('date')
        expected_orders = data.get('expected_orders', 50)
        available_staff = data.get('available_staff', [])
        special_events = data.get('special_events', [])
        
        # AI 기반 스케줄 생성
        schedule = []
        
        # 시간대별 필요 인력 계산
        time_slots = [
            {'start': '09:00', 'end': '12:00', 'multiplier': 0.5},
            {'start': '12:00', 'end': '15:00', 'multiplier': 1.5},
            {'start': '15:00', 'end': '18:00', 'multiplier': 0.8},
            {'start': '18:00', 'end': '21:00', 'multiplier': 1.2},
            {'start': '21:00', 'end': '24:00', 'multiplier': 0.6}
        ]
        
        for slot in time_slots:
            base_staff = max(1, int(expected_orders * slot['multiplier'] / 20))
            
            # 특별 이벤트 고려
            event_multiplier = 1.5 if special_events else 1.0
            
            required_staff = int(base_staff * event_multiplier)
            
            schedule.append({
                'time_slot': f"{slot['start']} - {slot['end']}",
                'required_staff': required_staff,
                'assigned_staff': min(required_staff, len(available_staff)),
                'workload': 'High' if required_staff > 5 else 'Medium' if required_staff > 3 else 'Low'
            })
        
        return jsonify({
            'date': date,
            'schedule': schedule,
            'total_required_staff': sum(slot['required_staff'] for slot in schedule),
            'available_staff_count': len(available_staff)
        })
        
    except Exception as e:
        logger.error(f"자동 스케줄링 오류: {str(e)}")
        return jsonify({'error': 'Failed to generate auto schedule'}), 500 