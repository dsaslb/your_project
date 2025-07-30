"""
실제 AI 모델 API
TensorFlow와 scikit-learn 모델을 위한 REST API
"""

from flask import Blueprint, request, jsonify
import logging
import json
from datetime import datetime
from typing import Dict, Any

from ai.real_ai_models import ai_model_manager

logger = logging.getLogger(__name__)

real_ai_models_api = Blueprint('real_ai_models_api', __name__)

@real_ai_models_api.route('/api/ai/models/status', methods=['GET'])
def get_models_status():
    """모든 AI 모델 상태 조회"""
    try:
        status = ai_model_manager.get_model_status()
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"모델 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@real_ai_models_api.route('/api/ai/models/train', methods=['POST'])
def train_model():
    """모델 학습"""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': 'model_name이 필요합니다.'
            }), 400
        
        if model_name not in ai_model_manager.model_configs:
            return jsonify({
                'success': False,
                'error': f'지원하지 않는 모델: {model_name}'
            }), 400
        
        # 모델 학습
        result = ai_model_manager.train_model(model_name)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result,
                'message': f'모델 {model_name} 학습 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"모델 학습 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@real_ai_models_api.route('/api/ai/models/<model_name>/predict', methods=['POST'])
def predict(model_name):
    """모델 예측"""
    try:
        if model_name not in ai_model_manager.model_configs:
            return jsonify({
                'success': False,
                'error': f'지원하지 않는 모델: {model_name}'
            }), 400
        
        data = request.get_json()
        input_data = data.get('input_data', {})
        
        if not input_data:
            return jsonify({
                'success': False,
                'error': 'input_data가 필요합니다.'
            }), 400
        
        # 예측 수행
        result = ai_model_manager.predict(model_name, input_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result,
                'message': f'모델 {model_name} 예측 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"예측 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@real_ai_models_api.route('/api/ai/models/<model_name>/retrain', methods=['POST'])
def retrain_model(model_name):
    """모델 재학습"""
    try:
        if model_name not in ai_model_manager.model_configs:
            return jsonify({
                'success': False,
                'error': f'지원하지 않는 모델: {model_name}'
            }), 400
        
        # 모델 재학습
        result = ai_model_manager.retrain_model(model_name)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result,
                'message': f'모델 {model_name} 재학습 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"모델 재학습 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@real_ai_models_api.route('/api/ai/models/<model_name>', methods=['DELETE'])
def delete_model(model_name):
    """모델 삭제"""
    try:
        if model_name not in ai_model_manager.model_configs:
            return jsonify({
                'success': False,
                'error': f'지원하지 않는 모델: {model_name}'
            }), 400
        
        # 모델 삭제
        result = ai_model_manager.delete_model(model_name)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"모델 삭제 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@real_ai_models_api.route('/api/ai/models/config', methods=['GET'])
def get_model_configs():
    """모델 설정 조회"""
    try:
        return jsonify({
            'success': True,
            'data': ai_model_manager.model_configs,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"모델 설정 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@real_ai_models_api.route('/api/ai/models/batch-predict', methods=['POST'])
def batch_predict():
    """배치 예측"""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        input_data_list = data.get('input_data_list', [])
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': 'model_name이 필요합니다.'
            }), 400
        
        if not input_data_list:
            return jsonify({
                'success': False,
                'error': 'input_data_list가 필요합니다.'
            }), 400
        
        if model_name not in ai_model_manager.model_configs:
            return jsonify({
                'success': False,
                'error': f'지원하지 않는 모델: {model_name}'
            }), 400
        
        # 배치 예측 수행
        results = []
        for input_data in input_data_list:
            result = ai_model_manager.predict(model_name, input_data)
            results.append(result)
        
        return jsonify({
            'success': True,
            'data': {
                'model_name': model_name,
                'predictions': results,
                'total_predictions': len(results)
            },
            'message': f'배치 예측 완료: {len(results)}개'
        })
        
    except Exception as e:
        logger.error(f"배치 예측 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@real_ai_models_api.route('/api/ai/models/performance', methods=['GET'])
def get_model_performance():
    """모델 성능 조회"""
    try:
        performance_data = {}
        
        for model_name, metadata in ai_model_manager.model_metadata.items():
            if 'performance' in metadata:
                performance_data[model_name] = {
                    'trained_at': metadata.get('trained_at'),
                    'performance': metadata['performance'],
                    'data_samples': metadata.get('data_samples', 0)
                }
        
        return jsonify({
            'success': True,
            'data': performance_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"모델 성능 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 