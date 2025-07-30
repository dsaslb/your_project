"""
고급 AI API 엔드포인트
엔터프라이즈급 AI 분석 및 예측 서비스
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback
import os
import sys

# AI 엔진 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.advanced_ai_engine import BusinessIntelligenceAI, AdvancedAIEngine

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
advanced_ai_bp = Blueprint('advanced_ai', __name__, url_prefix='/api/v2/ai')

# AI 엔진 인스턴스
bi_ai = BusinessIntelligenceAI()
ai_engine = AdvancedAIEngine()

@advanced_ai_bp.route('/health', methods=['GET'])
@cross_origin()
def ai_health_check():
    """AI 시스템 상태 확인"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'ai_engine': 'operational',
            'models_loaded': len(ai_engine.models),
            'version': '2.0.0'
        }), 200
    except Exception as e:
        logger.error(f"AI 헬스체크 오류: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/sales/analyze', methods=['POST'])
@cross_origin()
def analyze_sales_trends():
    """매출 트렌드 분석"""
    try:
        data = request.get_json()
        
        if not data or 'sales_data' not in data:
            return jsonify({
                'error': '매출 데이터가 필요합니다',
                'required_fields': ['sales_data']
            }), 400
        
        # 데이터 변환
        sales_data = pd.DataFrame(data['sales_data'])
        
        # 필수 컬럼 확인
        required_columns = ['date', 'sales_amount']
        missing_columns = [col for col in required_columns if col not in sales_data.columns]
        
        if missing_columns:
            return jsonify({
                'error': f'필수 컬럼이 누락되었습니다: {missing_columns}',
                'required_columns': required_columns
            }), 400
        
        # 매출 분석 수행
        analysis_result = bi_ai.analyze_sales_trends(sales_data)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"매출 분석 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '매출 분석 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/sales/predict', methods=['POST'])
@cross_origin()
def predict_sales():
    """매출 예측"""
    try:
        data = request.get_json()
        
        if not data or 'historical_data' not in data:
            return jsonify({
                'error': '과거 데이터가 필요합니다',
                'required_fields': ['historical_data']
            }), 400
        
        # 과거 데이터 변환
        historical_data = pd.DataFrame(data['historical_data'])
        
        # 예측 기간 설정
        prediction_days = data.get('prediction_days', 90)
        
        # 매출 분석 및 예측
        analysis_result = bi_ai.analyze_sales_trends(historical_data)
        predictions = analysis_result.get('predictions', {})
        
        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'model_performance': analysis_result.get('model_performance', {}),
            'prediction_days': prediction_days,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"매출 예측 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '매출 예측 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/customer/churn', methods=['POST'])
@cross_origin()
def predict_customer_churn():
    """고객 이탈 예측"""
    try:
        data = request.get_json()
        
        if not data or 'customer_data' not in data:
            return jsonify({
                'error': '고객 데이터가 필요합니다',
                'required_fields': ['customer_data']
            }), 400
        
        # 고객 데이터 변환
        customer_data = pd.DataFrame(data['customer_data'])
        
        # 필수 컬럼 확인
        required_columns = ['churn']
        missing_columns = [col for col in required_columns if col not in customer_data.columns]
        
        if missing_columns:
            return jsonify({
                'error': f'필수 컬럼이 누락되었습니다: {missing_columns}',
                'required_columns': required_columns
            }), 400
        
        # 이탈 예측 수행
        churn_analysis = bi_ai.predict_customer_churn(customer_data)
        
        return jsonify({
            'status': 'success',
            'analysis': churn_analysis,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"고객 이탈 예측 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '고객 이탈 예측 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/inventory/optimize', methods=['POST'])
@cross_origin()
def optimize_inventory():
    """재고 최적화"""
    try:
        data = request.get_json()
        
        if not data or 'inventory_data' not in data:
            return jsonify({
                'error': '재고 데이터가 필요합니다',
                'required_fields': ['inventory_data']
            }), 400
        
        # 재고 데이터 변환
        inventory_data = pd.DataFrame(data['inventory_data'])
        
        # 필수 컬럼 확인
        required_columns = ['optimal_stock']
        missing_columns = [col for col in required_columns if col not in inventory_data.columns]
        
        if missing_columns:
            return jsonify({
                'error': f'필수 컬럼이 누락되었습니다: {missing_columns}',
                'required_columns': required_columns
            }), 400
        
        # 재고 최적화 수행
        inventory_analysis = bi_ai.optimize_inventory(inventory_data)
        
        return jsonify({
            'status': 'success',
            'analysis': inventory_analysis,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"재고 최적화 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '재고 최적화 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/model/train', methods=['POST'])
@cross_origin()
def train_custom_model():
    """커스텀 모델 훈련"""
    try:
        data = request.get_json()
        
        if not data or 'training_data' not in data or 'model_name' not in data:
            return jsonify({
                'error': '훈련 데이터와 모델 이름이 필요합니다',
                'required_fields': ['training_data', 'model_name', 'target_column']
            }), 400
        
        # 데이터 변환
        training_data = pd.DataFrame(data['training_data'])
        model_name = data['model_name']
        target_column = data['target_column']
        
        # 필수 컬럼 확인
        if target_column not in training_data.columns:
            return jsonify({
                'error': f'타겟 컬럼이 데이터에 없습니다: {target_column}',
                'available_columns': training_data.columns.tolist()
            }), 400
        
        # 데이터 준비
        X, y = ai_engine.prepare_data(training_data, target_column)
        
        # 모델 훈련
        model = ai_engine.train_model(model_name, X, y)
        
        # 특성 중요도 분석
        feature_names = training_data.drop(columns=[target_column]).columns.tolist()
        importance_analysis = ai_engine.analyze_feature_importance(model_name, feature_names)
        
        # 모델 저장
        model_path = f"models/{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        os.makedirs("models", exist_ok=True)
        ai_engine.save_model(model_name, model_path)
        
        return jsonify({
            'status': 'success',
            'model_name': model_name,
            'model_path': model_path,
            'performance': ai_engine.get_model_performance(model_name),
            'feature_importance': importance_analysis,
            'training_samples': len(training_data),
            'features_count': len(feature_names),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"모델 훈련 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '모델 훈련 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/model/predict', methods=['POST'])
@cross_origin()
def predict_with_model():
    """훈련된 모델로 예측"""
    try:
        data = request.get_json()
        
        if not data or 'model_name' not in data or 'input_data' not in data:
            return jsonify({
                'error': '모델 이름과 입력 데이터가 필요합니다',
                'required_fields': ['model_name', 'input_data']
            }), 400
        
        model_name = data['model_name']
        input_data = pd.DataFrame(data['input_data'])
        
        # 모델 존재 확인
        if model_name not in ai_engine.models:
            return jsonify({
                'error': f'모델이 훈련되지 않았습니다: {model_name}',
                'available_models': list(ai_engine.models.keys())
            }), 400
        
        # 예측 수행
        X, _ = ai_engine.prepare_data(input_data, input_data.columns[0])  # 임시 타겟 컬럼
        predictions = ai_engine.predict(model_name, X)
        
        return jsonify({
            'status': 'success',
            'model_name': model_name,
            'predictions': predictions.tolist(),
            'prediction_count': len(predictions),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"모델 예측 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '모델 예측 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/model/performance', methods=['GET'])
@cross_origin()
def get_model_performance():
    """모델 성능 정보 조회"""
    try:
        model_name = request.args.get('model_name')
        
        if not model_name:
            return jsonify({
                'error': '모델 이름이 필요합니다',
                'available_models': list(ai_engine.models.keys())
            }), 400
        
        if model_name not in ai_engine.models:
            return jsonify({
                'error': f'모델이 존재하지 않습니다: {model_name}',
                'available_models': list(ai_engine.models.keys())
            }), 404
        
        performance = ai_engine.get_model_performance(model_name)
        report = ai_engine.generate_report(model_name)
        
        return jsonify({
            'status': 'success',
            'model_name': model_name,
            'performance': performance,
            'report': report,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"모델 성능 조회 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '모델 성능 조회 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/models/list', methods=['GET'])
@cross_origin()
def list_models():
    """훈련된 모델 목록 조회"""
    try:
        models_info = {}
        
        for model_name in ai_engine.models:
            performance = ai_engine.get_model_performance(model_name)
            models_info[model_name] = {
                'model_type': type(ai_engine.models[model_name]).__name__,
                'performance': performance,
                'feature_count': len(ai_engine.feature_importance.get(model_name, [])),
                'trained_at': datetime.now().isoformat()  # 실제로는 모델 메타데이터에서 가져와야 함
            }
        
        return jsonify({
            'status': 'success',
            'models': models_info,
            'total_models': len(models_info),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"모델 목록 조회 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '모델 목록 조회 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/analytics/dashboard', methods=['GET'])
@cross_origin()
def get_ai_dashboard():
    """AI 대시보드 데이터"""
    try:
        # 시스템 상태
        system_status = {
            'ai_engine_status': 'operational',
            'models_loaded': len(ai_engine.models),
            'total_predictions': len(ai_engine.predictions_cache),
            'memory_usage': 'normal'
        }
        
        # 모델 성능 요약
        performance_summary = {}
        for model_name in ai_engine.models:
            perf = ai_engine.get_model_performance(model_name)
            performance_summary[model_name] = {
                'r2_score': perf.get('r2', 0),
                'mse': perf.get('mse', 0),
                'mae': perf.get('mae', 0)
            }
        
        # 최근 활동
        recent_activity = [
            {
                'action': 'model_training',
                'model_name': 'sales_prediction',
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            },
            {
                'action': 'prediction',
                'model_name': 'customer_churn',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'status': 'completed'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'system_status': system_status,
            'performance_summary': performance_summary,
            'recent_activity': recent_activity,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"AI 대시보드 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'AI 대시보드 데이터 조회 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@advanced_ai_bp.route('/test/generate-data', methods=['POST'])
@cross_origin()
def generate_test_data():
    """테스트 데이터 생성"""
    try:
        data = request.get_json()
        data_type = data.get('type', 'sales')
        n_samples = data.get('n_samples', 1000)
        
        np.random.seed(42)
        
        if data_type == 'sales':
            test_data = {
                'sales_data': [
                    {
                        'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                        'sales_amount': float(np.random.normal(1000, 200)),
                        'customer_count': int(np.random.poisson(50)),
                        'product_price': float(np.random.uniform(10, 100)),
                        'marketing_budget': float(np.random.uniform(100, 1000))
                    }
                    for i in range(n_samples)
                ]
            }
        elif data_type == 'customer':
            test_data = {
                'customer_data': [
                    {
                        'tenure': float(np.random.exponential(5)),
                        'monthly_charges': float(np.random.normal(50, 15)),
                        'total_charges': float(np.random.normal(1000, 300)),
                        'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year']),
                        'churn': int(np.random.choice([0, 1], p=[0.8, 0.2]))
                    }
                    for _ in range(n_samples)
                ]
            }
        elif data_type == 'inventory':
            test_data = {
                'inventory_data': [
                    {
                        'current_stock': int(np.random.poisson(100)),
                        'demand': int(np.random.poisson(80)),
                        'lead_time': float(np.random.exponential(7)),
                        'holding_cost': float(np.random.uniform(5, 20)),
                        'optimal_stock': int(np.random.poisson(90))
                    }
                    for _ in range(n_samples)
                ]
            }
        else:
            return jsonify({
                'error': '지원하지 않는 데이터 타입입니다',
                'supported_types': ['sales', 'customer', 'inventory']
            }), 400
        
        return jsonify({
            'status': 'success',
            'data_type': data_type,
            'n_samples': n_samples,
            'test_data': test_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"테스트 데이터 생성 오류: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '테스트 데이터 생성 중 오류가 발생했습니다',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 에러 핸들러
@advanced_ai_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'API 엔드포인트를 찾을 수 없습니다',
        'timestamp': datetime.now().isoformat()
    }), 404

@advanced_ai_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': '서버 내부 오류가 발생했습니다',
        'timestamp': datetime.now().isoformat()
    }), 500 