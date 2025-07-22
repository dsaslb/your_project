from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

# AI 모듈들 import
try:
    from ai.ai_controller import AIController
    from ai.prediction_engine import AIPredictionEngine
    from ai.nlp_processor import NLPProcessor
    from ai.anomaly_detection import AnomalyDetectionSystem
    from ai.model_manager import AIModelManager
    from ai.recommendation_system import RecommendationSystem
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# AI 컨트롤러 인스턴스
ai_controller = None

def init_ai_controller():
    """AI 컨트롤러 초기화"""
    global ai_controller
    if AI_AVAILABLE and ai_controller is None:
        try:
            ai_controller = AIController()
            ai_controller.start()
            logging.info("AI 컨트롤러 초기화 완료")
        except Exception as e:
            logging.error(f"AI 컨트롤러 초기화 실패: {e}")

@ai_bp.before_app_first_request
def setup_ai():
    """앱 시작 시 AI 설정"""
    init_ai_controller()

@ai_bp.route('/status', methods=['GET'])
@login_required
def get_ai_status():
    """AI 시스템 상태 조회"""
    if not AI_AVAILABLE:
        return jsonify({
            'error': 'AI 모듈을 사용할 수 없습니다.',
            'available': False
        }), 503
    
    if ai_controller is None:
        return jsonify({
            'error': 'AI 컨트롤러가 초기화되지 않았습니다.',
            'available': False
        }), 503
    
    try:
        status = ai_controller.get_status()
        return jsonify({
            'available': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'error': f'상태 조회 실패: {str(e)}',
            'available': False
        }), 500

@ai_bp.route('/text/analyze', methods=['POST'])
@login_required
def analyze_text():
    """텍스트 분석 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '텍스트가 필요합니다.'}), 400
        
        text = data['text']
        parameters = data.get('parameters', {})
        
        # 요청 제출
        request_id = ai_controller.submit_request(
            'text_analysis',
            text,
            parameters
        )
        
        # 응답 대기
        response = ai_controller.get_response(timeout=30.0)
        
        if response and response.success:
            return jsonify({
                'request_id': request_id,
                'success': True,
                'result': response.result,
                'processing_time': response.processing_time
            })
        else:
            return jsonify({
                'request_id': request_id,
                'success': False,
                'error': response.error_message if response else '응답을 받지 못했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"텍스트 분석 실패: {e}")
        return jsonify({'error': f'텍스트 분석 실패: {str(e)}'}), 500

@ai_bp.route('/prediction/train', methods=['POST'])
@login_required
def train_prediction_model():
    """예측 모델 훈련 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'error': '데이터가 필요합니다.'}), 400
        
        # 데이터를 DataFrame으로 변환
        df_data = pd.DataFrame(data['data'])
        parameters = data.get('parameters', {})
        
        # 요청 제출
        request_id = ai_controller.submit_request(
            'prediction',
            df_data,
            parameters
        )
        
        # 응답 대기
        response = ai_controller.get_response(timeout=60.0)
        
        if response and response.success:
            return jsonify({
                'request_id': request_id,
                'success': True,
                'result': response.result,
                'processing_time': response.processing_time
            })
        else:
            return jsonify({
                'request_id': request_id,
                'success': False,
                'error': response.error_message if response else '응답을 받지 못했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"예측 모델 훈련 실패: {e}")
        return jsonify({'error': f'예측 모델 훈련 실패: {str(e)}'}), 500

@ai_bp.route('/prediction/predict', methods=['POST'])
@login_required
def make_prediction():
    """예측 수행 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'error': '데이터가 필요합니다.'}), 400
        
        # 데이터를 DataFrame으로 변환
        df_data = pd.DataFrame(data['data'])
        parameters = data.get('parameters', {})
        parameters['make_prediction'] = True
        parameters['prediction_data'] = df_data
        
        # 요청 제출
        request_id = ai_controller.submit_request(
            'prediction',
            df_data,
            parameters
        )
        
        # 응답 대기
        response = ai_controller.get_response(timeout=30.0)
        
        if response and response.success:
            return jsonify({
                'request_id': request_id,
                'success': True,
                'result': response.result,
                'processing_time': response.processing_time
            })
        else:
            return jsonify({
                'request_id': request_id,
                'success': False,
                'error': response.error_message if response else '응답을 받지 못했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"예측 실패: {e}")
        return jsonify({'error': f'예측 실패: {str(e)}'}), 500

@ai_bp.route('/anomaly/detect', methods=['POST'])
@login_required
def detect_anomalies():
    """이상 탐지 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'error': '데이터가 필요합니다.'}), 400
        
        # 데이터를 numpy 배열로 변환
        array_data = np.array(data['data'])
        parameters = data.get('parameters', {})
        
        # 요청 제출
        request_id = ai_controller.submit_request(
            'anomaly_detection',
            array_data,
            parameters
        )
        
        # 응답 대기
        response = ai_controller.get_response(timeout=30.0)
        
        if response and response.success:
            return jsonify({
                'request_id': request_id,
                'success': True,
                'result': response.result,
                'processing_time': response.processing_time
            })
        else:
            return jsonify({
                'request_id': request_id,
                'success': False,
                'error': response.error_message if response else '응답을 받지 못했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"이상 탐지 실패: {e}")
        return jsonify({'error': f'이상 탐지 실패: {str(e)}'}), 500

@ai_bp.route('/recommendation/train', methods=['POST'])
@login_required
def train_recommendation_model():
    """추천 모델 훈련 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'interactions_data' not in data:
            return jsonify({'error': '상호작용 데이터가 필요합니다.'}), 400
        
        # 요청 제출
        request_id = ai_controller.submit_request(
            'recommendation',
            data,
            {'train_collaborative': True, 'train_content_based': True}
        )
        
        # 응답 대기
        response = ai_controller.get_response(timeout=60.0)
        
        if response and response.success:
            return jsonify({
                'request_id': request_id,
                'success': True,
                'result': response.result,
                'processing_time': response.processing_time
            })
        else:
            return jsonify({
                'request_id': request_id,
                'success': False,
                'error': response.error_message if response else '응답을 받지 못했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"추천 모델 훈련 실패: {e}")
        return jsonify({'error': f'추천 모델 훈련 실패: {str(e)}'}), 500

@ai_bp.route('/recommendation/recommend', methods=['POST'])
@login_required
def get_recommendations():
    """추천 생성 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': '사용자 ID가 필요합니다.'}), 400
        
        parameters = {
            'n_recommendations': data.get('n_recommendations', 10)
        }
        
        # 요청 제출
        request_id = ai_controller.submit_request(
            'recommendation',
            data,
            parameters
        )
        
        # 응답 대기
        response = ai_controller.get_response(timeout=30.0)
        
        if response and response.success:
            return jsonify({
                'request_id': request_id,
                'success': True,
                'result': response.result,
                'processing_time': response.processing_time
            })
        else:
            return jsonify({
                'request_id': request_id,
                'success': False,
                'error': response.error_message if response else '응답을 받지 못했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"추천 생성 실패: {e}")
        return jsonify({'error': f'추천 생성 실패: {str(e)}'}), 500

@ai_bp.route('/recommendation/interaction', methods=['POST'])
@login_required
def record_interaction():
    """상호작용 기록 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'item_id' not in data:
            return jsonify({'error': '사용자 ID와 아이템 ID가 필요합니다.'}), 400
        
        # 요청 제출
        request_id = ai_controller.submit_request(
            'recommendation',
            {'interaction': data},
            {}
        )
        
        # 응답 대기
        response = ai_controller.get_response(timeout=10.0)
        
        if response and response.success:
            return jsonify({
                'request_id': request_id,
                'success': True,
                'message': '상호작용이 기록되었습니다.'
            })
        else:
            return jsonify({
                'request_id': request_id,
                'success': False,
                'error': response.error_message if response else '응답을 받지 못했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"상호작용 기록 실패: {e}")
        return jsonify({'error': f'상호작용 기록 실패: {str(e)}'}), 500

@ai_bp.route('/workflow/execute', methods=['POST'])
@login_required
def execute_workflow():
    """워크플로우 실행 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'workflow_name' not in data:
            return jsonify({'error': '워크플로우 이름이 필요합니다.'}), 400
        
        workflow_name = data['workflow_name']
        parameters = data.get('parameters', {})
        
        # 요청 제출
        request_id = ai_controller.submit_request(
            'workflow',
            workflow_name,
            parameters
        )
        
        # 응답 대기
        response = ai_controller.get_response(timeout=60.0)
        
        if response and response.success:
            return jsonify({
                'request_id': request_id,
                'success': True,
                'result': response.result,
                'processing_time': response.processing_time
            })
        else:
            return jsonify({
                'request_id': request_id,
                'success': False,
                'error': response.error_message if response else '응답을 받지 못했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"워크플로우 실행 실패: {e}")
        return jsonify({'error': f'워크플로우 실행 실패: {str(e)}'}), 500

@ai_bp.route('/models/list', methods=['GET'])
@login_required
def list_models():
    """모델 목록 조회 API"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI 모듈을 사용할 수 없습니다.'}), 503
    
    try:
        if ai_controller and ai_controller.model_manager:
            models = ai_controller.model_manager.list_models()
            return jsonify({
                'success': True,
                'models': models
            })
        else:
            return jsonify({'error': '모델 매니저를 사용할 수 없습니다.'}), 503
            
    except Exception as e:
        logging.error(f"모델 목록 조회 실패: {e}")
        return jsonify({'error': f'모델 목록 조회 실패: {str(e)}'}), 500

@ai_bp.route('/models/info/<model_name>', methods=['GET'])
@login_required
def get_model_info(model_name):
    """모델 정보 조회 API"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI 모듈을 사용할 수 없습니다.'}), 503
    
    try:
        version = request.args.get('version')
        
        if ai_controller and ai_controller.model_manager:
            model_info = ai_controller.model_manager.get_model_info(model_name, version)
            return jsonify({
                'success': True,
                'model_info': model_info
            })
        else:
            return jsonify({'error': '모델 매니저를 사용할 수 없습니다.'}), 503
            
    except Exception as e:
        logging.error(f"모델 정보 조회 실패: {e}")
        return jsonify({'error': f'모델 정보 조회 실패: {str(e)}'}), 500

@ai_bp.route('/models/save', methods=['POST'])
@login_required
def save_model():
    """모델 저장 API"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI 모듈을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'model_name' not in data:
            return jsonify({'error': '모델 이름이 필요합니다.'}), 400
        
        model_name = data['model_name']
        model = data.get('model')
        metadata = data.get('metadata', {})
        version = data.get('version')
        
        if ai_controller and ai_controller.model_manager:
            result = ai_controller.model_manager.save_model(
                model_name, model, metadata, version
            )
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({'error': '모델 매니저를 사용할 수 없습니다.'}), 503
            
    except Exception as e:
        logging.error(f"모델 저장 실패: {e}")
        return jsonify({'error': f'모델 저장 실패: {str(e)}'}), 500

@ai_bp.route('/models/deploy', methods=['POST'])
@login_required
def deploy_model():
    """모델 배포 API"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI 모듈을 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        if not data or 'model_name' not in data or 'version' not in data:
            return jsonify({'error': '모델 이름과 버전이 필요합니다.'}), 400
        
        model_name = data['model_name']
        version = data['version']
        environment = data.get('environment', 'staging')
        
        if ai_controller and ai_controller.model_manager:
            result = ai_controller.model_manager.deploy_model(
                model_name, version, environment
            )
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({'error': '모델 매니저를 사용할 수 없습니다.'}), 503
            
    except Exception as e:
        logging.error(f"모델 배포 실패: {e}")
        return jsonify({'error': f'모델 배포 실패: {str(e)}'}), 500

@ai_bp.route('/analytics/report', methods=['GET'])
@login_required
def get_ai_report():
    """AI 분석 리포트 API"""
    if not AI_AVAILABLE or ai_controller is None:
        return jsonify({'error': 'AI 시스템을 사용할 수 없습니다.'}), 503
    
    try:
        report_type = request.args.get('type', 'general')
        
        if report_type == 'general':
            report = ai_controller.generate_report()
        elif report_type == 'prediction' and ai_controller.prediction_engine:
            report = ai_controller.prediction_engine.generate_report()
        elif report_type == 'nlp' and ai_controller.nlp_processor:
            report = ai_controller.nlp_processor.generate_report()
        elif report_type == 'anomaly' and ai_controller.anomaly_detector:
            report = ai_controller.anomaly_detector.generate_report()
        elif report_type == 'recommendation' and ai_controller.recommendation_system:
            report = ai_controller.recommendation_system.generate_report()
        else:
            return jsonify({'error': '지원하지 않는 리포트 타입입니다.'}), 400
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        logging.error(f"AI 리포트 생성 실패: {e}")
        return jsonify({'error': f'AI 리포트 생성 실패: {str(e)}'}), 500

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """AI 시스템 헬스 체크"""
    if not AI_AVAILABLE:
        return jsonify({
            'status': 'unhealthy',
            'error': 'AI 모듈을 사용할 수 없습니다.'
        }), 503
    
    if ai_controller is None:
        return jsonify({
            'status': 'unhealthy',
            'error': 'AI 컨트롤러가 초기화되지 않았습니다.'
        }), 503
    
    try:
        health = ai_controller._check_health()
        if health['healthy']:
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'issues': health['issues'],
                'timestamp': datetime.now().isoformat()
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

# 에러 핸들러
@ai_bp.errorhandler(Exception)
def handle_error(error):
    """AI API 에러 핸들러"""
    logging.error(f"AI API 에러: {error}")
    logging.error(traceback.format_exc())
    
    return jsonify({
        'error': 'AI 시스템 내부 오류가 발생했습니다.',
        'details': str(error) if current_app.debug else None
    }), 500 