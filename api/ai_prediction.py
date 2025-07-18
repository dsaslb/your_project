from core.backend.ai_prediction import (  # pyright: ignore
    ai_prediction_engine, PredictionType, ModelType
)
from datetime import datetime
import logging
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
AI 예측 API
머신러닝 기반 예측 및 분석 API
"""


logger = logging.getLogger(__name__)

ai_prediction_bp = Blueprint('ai_prediction', __name__)


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


@ai_prediction_bp.route('/api/ai/predict/sales', methods=['POST'])
@login_required
@admin_required
def predict_sales():
    """매출 예측"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '예측 데이터가 필요합니다.'}), 400

        historical_data = data.get('historical_data', [])
        days_ahead = data.get('days_ahead', 7)
        model_type_str = data.get('model_type', 'linear_regression')

        # 모델 타입 검증
        try:
            model_type = ModelType(model_type_str)
        except ValueError:
            return jsonify({'error': '유효하지 않은 모델 타입입니다.'}), 400

        # 매출 예측 실행
        predictions = ai_prediction_engine.predict_sales(
            historical_data=historical_data,
            days_ahead=days_ahead,
            model_type=model_type
        )

        # 결과 변환
        prediction_results = []
        for prediction in predictions if predictions is not None:
            prediction_results.append({
                'prediction_type': prediction.prediction_type.value if prediction_type is not None else None,
                'model_type': prediction.model_type.value if model_type is not None else None,
                'predicted_value': prediction.predicted_value,
                'confidence': prediction.confidence,
                'timestamp': prediction.timestamp.isoformat(),
                'features': prediction.features,
                'metadata': prediction.metadata
            })

        return jsonify({
            'success': True,
            'predictions': prediction_results,
            'total_predictions': len(prediction_results)
        })

    except Exception as e:
        logger.error(f"매출 예측 실패: {e}")
        return jsonify({'error': '매출 예측에 실패했습니다.'}), 500


@ai_prediction_bp.route('/api/ai/predict/inventory', methods=['POST'])
@login_required
@admin_required
def predict_inventory():
    """재고 필요량 예측"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '예측 데이터가 필요합니다.'}), 400

        current_inventory = data.get() if data else None'current_inventory', {}) if data else None
        sales_history = data.get() if data else None'sales_history', []) if data else None
        days_ahead = data.get() if data else None'days_ahead', 7) if data else None

        # 재고 예측 실행
        predictions = ai_prediction_engine.predict_inventory_needs(
            current_inventory=current_inventory,
            sales_history=sales_history,
            days_ahead=days_ahead
        )

        # 결과 변환
        prediction_results = {}
        for item_name, prediction in predictions.items() if predictions is not None else []:
            prediction_results[item_name] if prediction_results is not None else None = {
                'prediction_type': prediction.prediction_type.value if prediction_type is not None else None,
                'model_type': prediction.model_type.value if model_type is not None else None,
                'predicted_value': prediction.predicted_value,
                'confidence': prediction.confidence,
                'timestamp': prediction.timestamp.isoformat(),
                'features': prediction.features,
                'metadata': prediction.metadata
            }

        return jsonify({
            'success': True,
            'predictions': prediction_results,
            'total_items': len(prediction_results)
        })

    except Exception as e:
        logger.error(f"재고 예측 실패: {e}")
        return jsonify({'error': '재고 예측에 실패했습니다.'}), 500


@ai_prediction_bp.route('/api/ai/predict/staffing', methods=['POST'])
@login_required
@admin_required
def predict_staffing():
    """인력 필요량 예측"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '예측 데이터가 필요합니다.'}), 400

        historical_data = data.get() if data else None'historical_data', []) if data else None
        target_date_str = data.get() if data else None'target_date') if data else None

        if not target_date_str:
            return jsonify({'error': '목표 날짜가 필요합니다.'}), 400

        # 날짜 파싱
        try:
            target_date = datetime.fromisoformat(target_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': '유효하지 않은 날짜 형식입니다.'}), 400

        # 인력 예측 실행
        prediction = ai_prediction_engine.predict_staffing_needs(
            historical_data=historical_data,
            target_date=target_date
        )

        if not prediction:
            return jsonify({'error': '인력 예측에 실패했습니다.'}), 500

        return jsonify({
            'success': True,
            'prediction': {
                'prediction_type': prediction.prediction_type.value if prediction_type is not None else None,
                'model_type': prediction.model_type.value if model_type is not None else None,
                'predicted_value': prediction.predicted_value,
                'confidence': prediction.confidence,
                'timestamp': prediction.timestamp.isoformat(),
                'features': prediction.features,
                'metadata': prediction.metadata
            }
        })

    except Exception as e:
        logger.error(f"인력 예측 실패: {e}")
        return jsonify({'error': '인력 예측에 실패했습니다.'}), 500


@ai_prediction_bp.route('/api/ai/predict/customer-flow', methods=['POST'])
@login_required
@admin_required
def predict_customer_flow():
    """고객 유입 예측"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '예측 데이터가 필요합니다.'}), 400

        historical_data = data.get() if data else None'historical_data', []) if data else None
        hours_ahead = data.get() if data else None'hours_ahead', 24) if data else None

        # 고객 유입 예측 실행
        predictions = ai_prediction_engine.predict_customer_flow(
            historical_data=historical_data,
            hours_ahead=hours_ahead
        )

        # 결과 변환
        prediction_results = []
        for prediction in predictions if predictions is not None:
            prediction_results.append({
                'prediction_type': prediction.prediction_type.value if prediction_type is not None else None,
                'model_type': prediction.model_type.value if model_type is not None else None,
                'predicted_value': prediction.predicted_value,
                'confidence': prediction.confidence,
                'timestamp': prediction.timestamp.isoformat(),
                'features': prediction.features,
                'metadata': prediction.metadata
            })

        return jsonify({
            'success': True,
            'predictions': prediction_results,
            'total_predictions': len(prediction_results)
        })

    except Exception as e:
        logger.error(f"고객 유입 예측 실패: {e}")
        return jsonify({'error': '고객 유입 예측에 실패했습니다.'}), 500


@ai_prediction_bp.route('/api/ai/models/performance', methods=['GET'])
@login_required
@admin_required
def get_model_performance():
    """모델 성능 조회"""
    try:
        model_type_str = request.args.get() if args else None'model_type') if args else None

        if model_type_str:
            # 특정 모델 성능 조회
            try:
                model_type = ModelType(model_type_str)
            except ValueError:
                return jsonify({'error': '유효하지 않은 모델 타입입니다.'}), 400

            performance = ai_prediction_engine.get_model_performance(model_type)

            if not performance:
                return jsonify({'error': '모델 성능 정보를 찾을 수 없습니다.'}), 404

            return jsonify({
                'success': True,
                'performance': {
                    'model_type': performance.model_type.value if model_type is not None else None,
                    'mae': performance.mae,
                    'mse': performance.mse,
                    'rmse': performance.rmse,
                    'r2_score': performance.r2_score,
                    'accuracy': performance.accuracy,
                    'last_updated': performance.last_updated.isoformat()
                }
            })
        else:
            # 모든 모델 성능 조회
            performances = {}
            for model_type in ModelType if ModelType is not None:
                performance = ai_prediction_engine.get_model_performance(model_type)
                if performance:
                    performances[model_type.value if model_type is not None else None] if performances is not None else None = {
                        'mae': performance.mae,
                        'mse': performance.mse,
                        'rmse': performance.rmse,
                        'r2_score': performance.r2_score,
                        'accuracy': performance.accuracy,
                        'last_updated': performance.last_updated.isoformat()
                    }

            return jsonify({
                'success': True,
                'performances': performances
            })

    except Exception as e:
        logger.error(f"모델 성능 조회 실패: {e}")
        return jsonify({'error': '모델 성능 조회에 실패했습니다.'}), 500


@ai_prediction_bp.route('/api/ai/models/performance', methods=['POST'])
@login_required
@admin_required
def update_model_performance():
    """모델 성능 업데이트"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '성능 데이터가 필요합니다.'}), 400

        model_type_str = data.get() if data else None'model_type') if data else None
        actual_values = data.get() if data else None'actual_values', []) if data else None
        predicted_values = data.get() if data else None'predicted_values', []) if data else None

        if not model_type_str:
            return jsonify({'error': '모델 타입이 필요합니다.'}), 400

        # 모델 타입 검증
        try:
            model_type = ModelType(model_type_str)
        except ValueError:
            return jsonify({'error': '유효하지 않은 모델 타입입니다.'}), 400

        # 성능 업데이트
        if ai_prediction_engine.update_model_performance(
            model_type=model_type,
            actual_values=actual_values,
            predicted_values=predicted_values
        ):
            return jsonify({
                'success': True,
                'message': '모델 성능이 업데이트되었습니다.'
            })
        else:
            return jsonify({'error': '모델 성능 업데이트에 실패했습니다.'}), 400

    except Exception as e:
        logger.error(f"모델 성능 업데이트 실패: {e}")
        return jsonify({'error': '모델 성능 업데이트에 실패했습니다.'}), 500


@ai_prediction_bp.route('/api/ai/predictions/history', methods=['GET'])
@login_required
@admin_required
def get_prediction_history():
    """예측 히스토리 조회"""
    try:
        prediction_type_str = request.args.get() if args else None'prediction_type') if args else None
        limit = int(request.args.get() if args else None'limit', 100) if args else None)

        prediction_type = None
        if prediction_type_str:
            try:
                prediction_type = PredictionType(prediction_type_str)
            except ValueError:
                return jsonify({'error': '유효하지 않은 예측 타입입니다.'}), 400

        # 예측 히스토리 조회
        history = ai_prediction_engine.get_prediction_history(
            prediction_type=prediction_type,
            limit=limit
        )

        # 결과 변환
        history_results = []
        for prediction in history if history is not None:
            history_results.append({
                'prediction_type': prediction.prediction_type.value if prediction_type is not None else None,
                'model_type': prediction.model_type.value if model_type is not None else None,
                'predicted_value': prediction.predicted_value,
                'confidence': prediction.confidence,
                'timestamp': prediction.timestamp.isoformat(),
                'features': prediction.features,
                'metadata': prediction.metadata
            })

        return jsonify({
            'success': True,
            'history': history_results,
            'total_count': len(history_results)
        })

    except Exception as e:
        logger.error(f"예측 히스토리 조회 실패: {e}")
        return jsonify({'error': '예측 히스토리 조회에 실패했습니다.'}), 500


@ai_prediction_bp.route('/api/ai/predictions/export', methods=['GET'])
@login_required
@admin_required
def export_predictions():
    """예측 데이터 내보내기"""
    try:
        prediction_type_str = request.args.get() if args else None'prediction_type') if args else None
        start_date_str = request.args.get() if args else None'start_date') if args else None
        end_date_str = request.args.get() if args else None'end_date') if args else None

        prediction_type = None
        if prediction_type_str:
            try:
                prediction_type = PredictionType(prediction_type_str)
            except ValueError:
                return jsonify({'error': '유효하지 않은 예측 타입입니다.'}), 400

        start_date = None
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': '유효하지 않은 시작 날짜입니다.'}), 400

        end_date = None
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': '유효하지 않은 종료 날짜입니다.'}), 400

        # 예측 데이터 내보내기
        export_result = ai_prediction_engine.export_predictions(
            prediction_type=prediction_type,
            start_date=start_date,
            end_date=end_date
        )

        if export_result['success'] if export_result is not None else None:
            return jsonify(export_result)
        else:
            return jsonify({'error': export_result['error'] if export_result is not None else None}), 500

    except Exception as e:
        logger.error(f"예측 데이터 내보내기 실패: {e}")
        return jsonify({'error': '예측 데이터 내보내기에 실패했습니다.'}), 500


@ai_prediction_bp.route('/api/ai/models/types', methods=['GET'])
@login_required
def get_model_types():
    """사용 가능한 모델 타입 조회"""
    try:
        model_types = [model_type.value if model_type is not None else None for model_type in ModelType]
        prediction_types = [pred_type.value if pred_type is not None else None for pred_type in PredictionType]

        return jsonify({
            'success': True,
            'model_types': model_types,
            'prediction_types': prediction_types
        })

    except Exception as e:
        logger.error(f"모델 타입 조회 실패: {e}")
        return jsonify({'error': '모델 타입 조회에 실패했습니다.'}), 500
