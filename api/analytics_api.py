"""
고급 데이터 분석 및 비즈니스 인텔리전스 API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS
import json
import logging
from datetime import datetime, timedelta
import traceback
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# 분석 모듈들 import
from analytics.data_pipeline import DataPipeline
from analytics.business_intelligence import BusinessIntelligence
from analytics.predictive_analytics import PredictiveAnalytics
from analytics.data_visualization import DataVisualization

# Blueprint 생성
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')
CORS(analytics_bp)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsAPI:
    """고급 데이터 분석 및 비즈니스 인텔리전스 API 클래스"""
    
    def __init__(self):
        """초기화"""
        self.data_pipeline = DataPipeline()
        self.business_intelligence = BusinessIntelligence()
        self.predictive_analytics = PredictiveAnalytics()
        self.data_visualization = DataVisualization()
        
        # API 상태
        self.api_status = {
            'status': 'active',
            'start_time': datetime.now(),
            'requests_processed': 0,
            'errors': 0
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """API 상태 확인"""
        try:
            # 각 모듈의 상태 확인
            pipeline_status = self.data_pipeline.get_status()
            bi_status = self.business_intelligence.get_status()
            analytics_status = self.predictive_analytics.get_status()
            viz_status = self.data_visualization.get_status()
            
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'modules': {
                    'data_pipeline': pipeline_status,
                    'business_intelligence': bi_status,
                    'predictive_analytics': analytics_status,
                    'data_visualization': viz_status
                },
                'api_stats': self.api_status
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# API 인스턴스 생성
analytics_api = AnalyticsAPI()

# ============================================================================
# 데이터 파이프라인 API 엔드포인트
# ============================================================================

@analytics_bp.route('/pipeline/status', methods=['GET'])
def get_pipeline_status():
    """데이터 파이프라인 상태 확인"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        status = analytics_api.data_pipeline.get_status()
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Pipeline status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/pipeline/stream', methods=['POST'])
def stream_data():
    """실시간 데이터 스트리밍"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '데이터가 필요합니다'
            }), 400
        
        # 데이터 스트리밍 처리
        result = analytics_api.data_pipeline.stream_data(data)
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Data streaming error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/pipeline/batch', methods=['POST'])
def batch_process():
    """배치 데이터 처리"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': '배치 데이터가 필요합니다'
            }), 400
        
        # 배치 처리 실행
        result = analytics_api.data_pipeline.batch_process(data['data'])
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Batch processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/pipeline/etl', methods=['POST'])
def run_etl():
    """ETL 작업 실행"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'ETL 설정이 필요합니다'
            }), 400
        
        # ETL 작업 실행
        result = analytics_api.data_pipeline.run_etl(
            source=data.get('source'),
            destination=data.get('destination'),
            transformations=data.get('transformations', [])
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"ETL error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# 비즈니스 인텔리전스 API 엔드포인트
# ============================================================================

@analytics_bp.route('/bi/dashboard', methods=['GET'])
def get_bi_dashboard():
    """비즈니스 인텔리전스 대시보드 데이터"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        
        # 대시보드 데이터 생성
        dashboard_data = analytics_api.business_intelligence.generate_dashboard()
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"BI dashboard error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/bi/kpi', methods=['POST'])
def update_kpi():
    """KPI 업데이트"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'kpi_name' not in data:
            return jsonify({
                'success': False,
                'error': 'KPI 이름과 값이 필요합니다'
            }), 400
        
        # KPI 업데이트
        result = analytics_api.business_intelligence.update_kpi(
            kpi_name=data['kpi_name'],
            value=data.get('value'),
            target=data.get('target'),
            unit=data.get('unit', ''),
            category=data.get('category', 'general')
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"KPI update error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/bi/trends', methods=['POST'])
def analyze_trends():
    """트렌드 분석"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'metric' not in data:
            return jsonify({
                'success': False,
                'error': '분석할 지표가 필요합니다'
            }), 400
        
        # 트렌드 분석 실행
        result = analytics_api.business_intelligence.analyze_trends(
            metric=data['metric'],
            period=data.get('period', 'daily'),
            window=data.get('window', 30)
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Trend analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/bi/alerts', methods=['GET'])
def get_alerts():
    """알림 목록 조회"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        
        # 알림 목록 조회
        alerts = analytics_api.business_intelligence.get_alerts()
        
        return jsonify({
            'success': True,
            'data': alerts,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Alerts error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# 예측 분석 API 엔드포인트
# ============================================================================

@analytics_bp.route('/predictive/train', methods=['POST'])
def train_model():
    """예측 모델 훈련"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': '훈련 데이터가 필요합니다'
            }), 400
        
        # 모델 훈련 실행
        result = analytics_api.predictive_analytics.train_model(
            data=data['data'],
            target_column=data.get('target_column'),
            model_type=data.get('model_type', 'linear_regression'),
            test_size=data.get('test_size', 0.2)
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Model training error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/predictive/predict', methods=['POST'])
def make_prediction():
    """예측 실행"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({
                'success': False,
                'error': '예측할 특성이 필요합니다'
            }), 400
        
        # 예측 실행
        result = analytics_api.predictive_analytics.predict(
            features=data['features'],
            model_name=data.get('model_name', 'latest')
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/predictive/forecast', methods=['POST'])
def time_series_forecast():
    """시계열 예측"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'time_series' not in data:
            return jsonify({
                'success': False,
                'error': '시계열 데이터가 필요합니다'
            }), 400
        
        # 시계열 예측 실행
        result = analytics_api.predictive_analytics.forecast_time_series(
            time_series=data['time_series'],
            periods=data.get('periods', 12),
            frequency=data.get('frequency', 'D')
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Time series forecast error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/predictive/backtest', methods=['POST'])
def run_backtest():
    """백테스팅 실행"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': '백테스팅 데이터가 필요합니다'
            }), 400
        
        # 백테스팅 실행
        result = analytics_api.predictive_analytics.backtest(
            data=data['data'],
            target_column=data.get('target_column'),
            model_name=data.get('model_name', 'latest'),
            test_size=data.get('test_size', 0.2)
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Backtest error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# 데이터 시각화 API 엔드포인트
# ============================================================================

@analytics_bp.route('/visualization/chart', methods=['POST'])
def create_chart():
    """차트 생성"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'chart_type' not in data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': '차트 타입과 데이터가 필요합니다'
            }), 400
        
        # 차트 생성
        result = analytics_api.data_visualization.create_chart(
            chart_type=data['chart_type'],
            data=data['data'],
            title=data.get('title', ''),
            x_label=data.get('x_label', ''),
            y_label=data.get('y_label', ''),
            config=data.get('config', {})
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Chart creation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/visualization/report', methods=['POST'])
def generate_report():
    """보고서 생성"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'template' not in data:
            return jsonify({
                'success': False,
                'error': '보고서 템플릿이 필요합니다'
            }), 400
        
        # 보고서 생성
        result = analytics_api.data_visualization.generate_report(
            template=data['template'],
            data=data.get('data', {}),
            title=data.get('title', '분석 보고서'),
            output_format=data.get('output_format', 'html')
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/visualization/export', methods=['POST'])
def export_chart():
    """차트 내보내기"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'chart_data' not in data:
            return jsonify({
                'success': False,
                'error': '차트 데이터가 필요합니다'
            }), 400
        
        # 차트 내보내기
        result = analytics_api.data_visualization.export_chart(
            chart_data=data['chart_data'],
            format=data.get('format', 'png'),
            filename=data.get('filename', 'chart')
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Chart export error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# 통합 분석 API 엔드포인트
# ============================================================================

@analytics_bp.route('/integrated/analysis', methods=['POST'])
def integrated_analysis():
    """통합 분석 실행"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'analysis_type' not in data:
            return jsonify({
                'success': False,
                'error': '분석 타입이 필요합니다'
            }), 400
        
        analysis_type = data['analysis_type']
        analysis_data = data.get('data', {})
        
        result = {}
        
        if analysis_type == 'comprehensive':
            # 종합 분석
            result = {
                'pipeline_status': analytics_api.data_pipeline.get_status(),
                'bi_dashboard': analytics_api.business_intelligence.generate_dashboard(),
                'predictions': analytics_api.predictive_analytics.get_latest_predictions(),
                'visualizations': analytics_api.data_visualization.get_recent_charts()
            }
        elif analysis_type == 'performance':
            # 성능 분석
            result = {
                'kpi_summary': analytics_api.business_intelligence.get_kpi_summary(),
                'trends': analytics_api.business_intelligence.get_recent_trends(),
                'predictions': analytics_api.predictive_analytics.get_performance_metrics()
            }
        elif analysis_type == 'custom':
            # 사용자 정의 분석
            custom_config = data.get('config', {})
            result = analytics_api._run_custom_analysis(custom_config)
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Integrated analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/integrated/workflow', methods=['POST'])
def execute_workflow():
    """워크플로우 실행"""
    try:
        analytics_api.api_status['requests_processed'] += 1
        data = request.get_json()
        
        if not data or 'workflow' not in data:
            return jsonify({
                'success': False,
                'error': '워크플로우 정의가 필요합니다'
            }), 400
        
        # 워크플로우 실행
        result = analytics_api._execute_workflow(data['workflow'])
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        analytics_api.api_status['errors'] += 1
        logger.error(f"Workflow execution error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# 시스템 관리 API 엔드포인트
# ============================================================================

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    try:
        status = analytics_api.get_health_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@analytics_bp.route('/config', methods=['GET', 'POST'])
def manage_config():
    """설정 관리"""
    try:
        if request.method == 'GET':
            # 설정 조회
            config = {
                'data_pipeline': analytics_api.data_pipeline.get_config(),
                'business_intelligence': analytics_api.business_intelligence.get_config(),
                'predictive_analytics': analytics_api.predictive_analytics.get_config(),
                'data_visualization': analytics_api.data_visualization.get_config()
            }
            return jsonify({
                'success': True,
                'data': config,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # 설정 업데이트
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '설정 데이터가 필요합니다'
                }), 400
            
            # 각 모듈의 설정 업데이트
            if 'data_pipeline' in data:
                analytics_api.data_pipeline.update_config(data['data_pipeline'])
            if 'business_intelligence' in data:
                analytics_api.business_intelligence.update_config(data['business_intelligence'])
            if 'predictive_analytics' in data:
                analytics_api.predictive_analytics.update_config(data['predictive_analytics'])
            if 'data_visualization' in data:
                analytics_api.data_visualization.update_config(data['data_visualization'])
            
            return jsonify({
                'success': True,
                'message': '설정이 업데이트되었습니다',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Config management error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# AnalyticsAPI 클래스에 추가 메서드들
def _run_custom_analysis(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """사용자 정의 분석 실행"""
    try:
        result = {}
        
        # 데이터 파이프라인 분석
        if config.get('include_pipeline', False):
            result['pipeline'] = self.data_pipeline.analyze_performance()
        
        # 비즈니스 인텔리전스 분석
        if config.get('include_bi', False):
            result['bi'] = self.business_intelligence.run_custom_analysis(config.get('bi_config', {}))
        
        # 예측 분석
        if config.get('include_predictive', False):
            result['predictive'] = self.predictive_analytics.run_custom_analysis(config.get('predictive_config', {}))
        
        # 시각화
        if config.get('include_visualization', False):
            result['visualization'] = self.data_visualization.create_custom_visualizations(config.get('viz_config', {}))
        
        return result
    except Exception as e:
        logger.error(f"Custom analysis error: {str(e)}")
        raise

def _execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
    """워크플로우 실행"""
    try:
        steps = workflow.get('steps', [])
        result = {}
        
        for step in steps:
            step_type = step.get('type')
            step_config = step.get('config', {})
            
            if step_type == 'data_processing':
                result[step['name']] = self.data_pipeline.process_data(step_config)
            elif step_type == 'kpi_calculation':
                result[step['name']] = self.business_intelligence.calculate_kpis(step_config)
            elif step_type == 'prediction':
                result[step['name']] = self.predictive_analytics.run_prediction(step_config)
            elif step_type == 'visualization':
                result[step['name']] = self.data_visualization.create_workflow_chart(step_config)
            else:
                logger.warning(f"Unknown workflow step type: {step_type}")
        
        return result
    except Exception as e:
        logger.error(f"Workflow execution error: {str(e)}")
        raise

# AnalyticsAPI 클래스에 메서드 추가
AnalyticsAPI._run_custom_analysis = _run_custom_analysis
AnalyticsAPI._execute_workflow = _execute_workflow

# 에러 핸들러
@analytics_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '요청한 리소스를 찾을 수 없습니다',
        'timestamp': datetime.now().isoformat()
    }), 404

@analytics_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '내부 서버 오류가 발생했습니다',
        'timestamp': datetime.now().isoformat()
    }), 500

# API 문서화를 위한 엔드포인트
@analytics_bp.route('/docs', methods=['GET'])
def get_api_docs():
    """API 문서 반환"""
    docs = {
        'title': '고급 데이터 분석 및 비즈니스 인텔리전스 API',
        'version': '1.0.0',
        'description': '실시간 데이터 파이프라인, 비즈니스 인텔리전스, 예측 분석, 데이터 시각화를 위한 REST API',
        'endpoints': {
            'data_pipeline': {
                'GET /pipeline/status': '데이터 파이프라인 상태 확인',
                'POST /pipeline/stream': '실시간 데이터 스트리밍',
                'POST /pipeline/batch': '배치 데이터 처리',
                'POST /pipeline/etl': 'ETL 작업 실행'
            },
            'business_intelligence': {
                'GET /bi/dashboard': '비즈니스 인텔리전스 대시보드',
                'POST /bi/kpi': 'KPI 업데이트',
                'POST /bi/trends': '트렌드 분석',
                'GET /bi/alerts': '알림 목록 조회'
            },
            'predictive_analytics': {
                'POST /predictive/train': '예측 모델 훈련',
                'POST /predictive/predict': '예측 실행',
                'POST /predictive/forecast': '시계열 예측',
                'POST /predictive/backtest': '백테스팅 실행'
            },
            'data_visualization': {
                'POST /visualization/chart': '차트 생성',
                'POST /visualization/report': '보고서 생성',
                'POST /visualization/export': '차트 내보내기'
            },
            'integrated': {
                'POST /integrated/analysis': '통합 분석 실행',
                'POST /integrated/workflow': '워크플로우 실행'
            },
            'system': {
                'GET /health': 'API 상태 확인',
                'GET /config': '설정 조회',
                'POST /config': '설정 업데이트'
            }
        }
    }
    
    return jsonify(docs)

if __name__ == '__main__':
    print("고급 데이터 분석 및 비즈니스 인텔리전스 API가 로드되었습니다.")
    print("사용 가능한 엔드포인트:")
    print("- GET /api/analytics/health: API 상태 확인")
    print("- GET /api/analytics/docs: API 문서")
    print("- POST /api/analytics/pipeline/stream: 실시간 데이터 스트리밍")
    print("- GET /api/analytics/bi/dashboard: BI 대시보드")
    print("- POST /api/analytics/predictive/train: 예측 모델 훈련")
    print("- POST /api/analytics/visualization/chart: 차트 생성") 