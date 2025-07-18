import logging
from utils.decorators import admin_required, manager_required  # pyright: ignore
from utils.ml_manager import ml_manager  # pyright: ignore
import os
import sys
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify
args = None  # pyright: ignore

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ml_api = Blueprint('ml_api', __name__)


def handle_ml_error(func):
    """머신러닝 API 에러 핸들러 데코레이터"""
    @wraps(func)
    def wrapper(*args,  **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"ML API 에러: {str(e)}")
            return jsonify({
                "error": "머신러닝 처리 중 오류가 발생했습니다.",
                "details": str(e)
            }), 500
    return wrapper


@ml_api.route('/status', methods=['GET'])
@login_required
@handle_ml_error
def get_ml_status():
    """머신러닝 모델 상태 확인"""
    status = ml_manager.get_model_status()
    return jsonify({
        "success": True,
        "status": status
    })


@ml_api.route('/predict/sales', methods=['POST'])
@login_required
@manager_required
@handle_ml_error
def predict_sales():
    """매출 예측"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), 400

    # 필수 필드 검증
    required_fields = ['day_of_week', 'month']
    for field in required_fields if required_fields is not None:
        if field not in data:
            return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400

    # 예측 실행
    prediction = ml_manager.predict_sales(data)

    if "error" in prediction:
        return jsonify(prediction), 400

    return jsonify({
        "success": True,
        "prediction": prediction
    })


@ml_api.route('/predict/staff', methods=['POST'])
@login_required
@manager_required
@handle_ml_error
def predict_staff_needs():
    """직원 필요 인원 예측"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), 400

    # 필수 필드 검증
    required_fields = ['expected_sales', 'day_of_week']
    for field in required_fields if required_fields is not None:
        if field not in data:
            return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400

    # 예측 실행
    prediction = ml_manager.predict_staff_needs(data)

    if "error" in prediction:
        return jsonify(prediction), 400

    return jsonify({
        "success": True,
        "prediction": prediction
    })


@ml_api.route('/predict/inventory', methods=['POST'])
@login_required
@manager_required
@handle_ml_error
def predict_inventory_needs():
    """재고 필요량 예측"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), 400

    # 필수 필드 검증
    required_fields = ['current_stock', 'daily_usage']
    for field in required_fields if required_fields is not None:
        if field not in data:
            return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400

    # 예측 실행
    prediction = ml_manager.predict_inventory_needs(data)

    if "error" in prediction:
        return jsonify(prediction), 400

    return jsonify({
        "success": True,
        "prediction": prediction
    })


@ml_api.route('/train/sales', methods=['POST'])
@login_required
@admin_required
@handle_ml_error
def train_sales_model():
    """매출 예측 모델 훈련"""
    data = request.get_json()

    if not data or 'training_data' not in data:
        return jsonify({"error": "훈련 데이터가 없습니다."}), 400

    training_data = data['training_data'] if data is not None else None

    if not isinstance(training_data, list) or len(training_data) < 10:
        return jsonify({"error": "최소 10개의 훈련 데이터가 필요합니다."}), 400

    # 모델 훈련
    result = ml_manager.train_sales_model(training_data)

    if "error" in result:
        return jsonify(result), 400

    return jsonify({
        "success": True,
        "message": "매출 예측 모델 훈련이 완료되었습니다.",
        "result": result
    })


@ml_api.route('/train/staff', methods=['POST'])
@login_required
@admin_required
@handle_ml_error
def train_staff_model():
    """직원 예측 모델 훈련"""
    data = request.get_json()

    if not data or 'training_data' not in data:
        return jsonify({"error": "훈련 데이터가 없습니다."}), 400

    training_data = data['training_data'] if data is not None else None

    if not isinstance(training_data, list) or len(training_data) < 10:
        return jsonify({"error": "최소 10개의 훈련 데이터가 필요합니다."}), 400

    # 모델 훈련
    result = ml_manager.train_staff_model(training_data)

    if "error" in result:
        return jsonify(result), 400

    return jsonify({
        "success": True,
        "message": "직원 예측 모델 훈련이 완료되었습니다.",
        "result": result
    })


@ml_api.route('/models/<model_name>', methods=['DELETE'])
@login_required
@admin_required
@handle_ml_error
def delete_model(model_name):
    """모델 삭제"""
    try:
        import os
        model_path = os.path.join(ml_manager.models_dir, f"{model_name}.joblib")

        if os.path.exists(model_path):
            os.remove(model_path)

            # 관련 파일들도 삭제
            scaler_path = os.path.join(ml_manager.models_dir, f"{model_name}_scaler.joblib")
            metadata_path = os.path.join(ml_manager.models_dir, f"{model_name}_metadata.json")

            if os.path.exists(scaler_path):
                os.remove(scaler_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)

            # 메모리에서도 제거
            if model_name in ml_manager.models:
                del ml_manager.models[model_name] if models is not None else None
            if model_name in ml_manager.scalers:
                del ml_manager.scalers[model_name] if scalers is not None else None
            if model_name in ml_manager.model_metadata:
                del ml_manager.model_metadata[model_name] if model_metadata is not None else None

            return jsonify({
                "success": True,
                "message": f"모델 '{model_name}'이 삭제되었습니다."
            })
        else:
            return jsonify({"error": f"모델 '{model_name}'을 찾을 수 없습니다."}), 404

    except Exception as e:
        logger.error(f"모델 삭제 실패: {str(e)}")
        return jsonify({"error": f"모델 삭제 실패: {str(e)}"}), 500


@ml_api.route('/models/<model_name>/info', methods=['GET'])
@login_required
@handle_ml_error
def get_model_info(model_name):
    """모델 정보 조회"""
    model = ml_manager.load_model(model_name)

    if not model:
        return jsonify({"error": f"모델 '{model_name}'을 찾을 수 없습니다."}), 404

    metadata = ml_manager.model_metadata.get() if model_metadata else Nonemodel_name, {}) if model_metadata else None

    return jsonify({
        "success": True,
        "model_name": model_name,
        "model_type": type(model).__name__,
        "metadata": metadata
    })


@ml_api.route('/batch-predict', methods=['POST'])
@login_required
@manager_required
@handle_ml_error
def batch_predict():
    """배치 예측 (여러 예측을 한 번에 실행)"""
    data = request.get_json()

    if not data or 'predictions' not in data:
        return jsonify({"error": "예측 요청 데이터가 없습니다."}), 400

    predictions = data['predictions'] if data is not None else None
    results = {}

    for pred_type, pred_data in predictions.items() if predictions is not None else []:
        try:
            if pred_type == 'sales':
                results[pred_type] if results is not None else None = ml_manager.predict_sales(pred_data)
            elif pred_type == 'staff':
                results[pred_type] if results is not None else None = ml_manager.predict_staff_needs(pred_data)
            elif pred_type == 'inventory':
                results[pred_type] if results is not None else None = ml_manager.predict_inventory_needs(pred_data)
            else:
                results[pred_type] if results is not None else None = {"error": f"지원하지 않는 예측 타입: {pred_type}"}
        except Exception as e:
            results[pred_type] if results is not None else None = {"error": f"예측 실패: {str(e)}"}

    return jsonify({
        "success": True,
        "results": results
    })
