"""
고급 데이터 분석 및 비즈니스 인텔리전스 API
"""
from flask import Blueprint, request, jsonify
from analytics.analytics_manager import AnalyticsManager, AnalyticsConfig
import os
from datetime import datetime

# 분석 관리자 초기화
analytics_config = AnalyticsConfig(
    data_dir="data/analytics",
    model_dir="models",
    cache_dir="cache",
    max_cache_size=1000,
    prediction_horizon=30,
    update_frequency=3600,
    enable_ml=True,
    enable_realtime=True
)

analytics_manager = AnalyticsManager(analytics_config)

# Blueprint 생성
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    """분석 시스템 상태 확인"""
    try:
        summary = analytics_manager.get_analytics_summary()
        return jsonify({
            'status': 'success',
            'message': '분석 시스템이 정상적으로 작동합니다',
            'data': {
                'total_analyses': summary['total_analyses'],
                'total_models': summary['total_models'],
                'total_insights': summary['total_insights'],
                'realtime_metrics': summary['realtime_metrics']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'분석 시스템 상태 확인 실패: {str(e)}'
        }), 500

@analytics_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    """분석 요약 정보 조회"""
    try:
        summary = analytics_manager.get_analytics_summary()
        return jsonify({
            'status': 'success',
            'data': summary
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'분석 요약 조회 실패: {str(e)}'
        }), 500

@analytics_bp.route('/trends', methods=['POST'])
def analyze_trends():
    """트렌드 분석"""
    try:
        data = request.get_json()
        
        if not data or 'data_source' not in data or 'metric' not in data:
            return jsonify({
                'status': 'error',
                'message': 'data_source와 metric 필드가 필요합니다'
            }), 400
        
        data_source = data['data_source']
        metric = data['metric']
        time_period = data.get('time_period', '30d')
        
        analysis = analytics_manager.analyze_trends(data_source, metric, time_period)
        
        return jsonify({
            'status': 'success',
            'message': f'{metric} 트렌드 분석이 완료되었습니다',
            'data': {
                'analysis_id': analysis.analysis_id,
                'name': analysis.name,
                'type': analysis.type,
                'results': analysis.results,
                'created_at': analysis.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'트렌드 분석 실패: {str(e)}'
        }), 500

@analytics_bp.route('/predictions/sales', methods=['POST'])
def predict_sales():
    """매출 예측"""
    try:
        data = request.get_json() or {}
        days_ahead = data.get('days_ahead', 30)
        
        predictions = analytics_manager.predict_sales(days_ahead)
        
        return jsonify({
            'status': 'success',
            'message': f'{days_ahead}일 매출 예측이 완료되었습니다',
            'data': predictions
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'매출 예측 실패: {str(e)}'
        }), 500

@analytics_bp.route('/correlations', methods=['POST'])
def analyze_correlations():
    """상관관계 분석"""
    try:
        data = request.get_json()
        
        if not data or 'data_source' not in data or 'variables' not in data:
            return jsonify({
                'status': 'error',
                'message': 'data_source와 variables 필드가 필요합니다'
            }), 400
        
        data_source = data['data_source']
        variables = data['variables']
        
        if not isinstance(variables, list) or len(variables) < 2:
            return jsonify({
                'status': 'error',
                'message': 'variables는 최소 2개 이상의 변수가 필요합니다'
            }), 400
        
        analysis = analytics_manager.analyze_correlations(data_source, variables)
        
        return jsonify({
            'status': 'success',
            'message': '상관관계 분석이 완료되었습니다',
            'data': {
                'analysis_id': analysis.analysis_id,
                'name': analysis.name,
                'type': analysis.type,
                'results': analysis.results,
                'created_at': analysis.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'상관관계 분석 실패: {str(e)}'
        }), 500

@analytics_bp.route('/clustering', methods=['POST'])
def perform_clustering():
    """클러스터링 분석"""
    try:
        data = request.get_json()
        
        if not data or 'data_source' not in data or 'features' not in data:
            return jsonify({
                'status': 'error',
                'message': 'data_source와 features 필드가 필요합니다'
            }), 400
        
        data_source = data['data_source']
        features = data['features']
        n_clusters = data.get('n_clusters', 3)
        
        if not isinstance(features, list) or len(features) < 1:
            return jsonify({
                'status': 'error',
                'message': 'features는 최소 1개 이상의 특성이 필요합니다'
            }), 400
        
        analysis = analytics_manager.perform_clustering(data_source, features, n_clusters)
        
        return jsonify({
            'status': 'success',
            'message': '클러스터링 분석이 완료되었습니다',
            'data': {
                'analysis_id': analysis.analysis_id,
                'name': analysis.name,
                'type': analysis.type,
                'results': analysis.results,
                'created_at': analysis.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'클러스터링 분석 실패: {str(e)}'
        }), 500

@analytics_bp.route('/anomalies', methods=['POST'])
def detect_anomalies():
    """이상 탐지"""
    try:
        data = request.get_json()
        
        if not data or 'data_source' not in data or 'metric' not in data:
            return jsonify({
                'status': 'error',
                'message': 'data_source와 metric 필드가 필요합니다'
            }), 400
        
        data_source = data['data_source']
        metric = data['metric']
        threshold = data.get('threshold', 2.0)
        
        analysis = analytics_manager.detect_anomalies(data_source, metric, threshold)
        
        return jsonify({
            'status': 'success',
            'message': f'{metric} 이상 탐지가 완료되었습니다',
            'data': {
                'analysis_id': analysis.analysis_id,
                'name': analysis.name,
                'type': analysis.type,
                'results': analysis.results,
                'created_at': analysis.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'이상 탐지 실패: {str(e)}'
        }), 500

@analytics_bp.route('/insights', methods=['GET'])
def get_insights():
    """인사이트 조회"""
    try:
        limit = request.args.get('limit', 50, type=int)
        category = request.args.get('category')
        
        insights = analytics_manager.insights[:limit]
        
        if category:
            insights = [i for i in insights if i.category == category]
        
        insights_data = []
        for insight in insights:
            insight_dict = {
                'insight_id': insight.insight_id,
                'title': insight.title,
                'description': insight.description,
                'category': insight.category,
                'confidence': insight.confidence,
                'impact': insight.impact,
                'recommendations': insight.recommendations,
                'data_sources': insight.data_sources,
                'created_at': insight.created_at.isoformat()
            }
            insights_data.append(insight_dict)
        
        return jsonify({
            'status': 'success',
            'data': insights_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'인사이트 조회 실패: {str(e)}'
        }), 500

@analytics_bp.route('/insights/generate', methods=['POST'])
def generate_insights():
    """인사이트 자동 생성"""
    try:
        insights = analytics_manager.generate_insights()
        
        insights_data = []
        for insight in insights:
            insight_dict = {
                'insight_id': insight.insight_id,
                'title': insight.title,
                'description': insight.description,
                'category': insight.category,
                'confidence': insight.confidence,
                'impact': insight.impact,
                'recommendations': insight.recommendations,
                'data_sources': insight.data_sources,
                'created_at': insight.created_at.isoformat()
            }
            insights_data.append(insight_dict)
        
        return jsonify({
            'status': 'success',
            'message': f'{len(insights)}개의 인사이트가 생성되었습니다',
            'data': insights_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'인사이트 생성 실패: {str(e)}'
        }), 500

@analytics_bp.route('/realtime', methods=['GET'])
def get_realtime_metrics():
    """실시간 메트릭 조회"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        metrics = analytics_manager.realtime_metrics[:limit]
        
        metrics_data = []
        for metric in metrics:
            metric_dict = {
                'metric_id': metric.metric_id,
                'name': metric.name,
                'value': metric.value,
                'unit': metric.unit,
                'trend': metric.trend,
                'threshold': metric.threshold,
                'alert_level': metric.alert_level,
                'timestamp': metric.timestamp.isoformat()
            }
            metrics_data.append(metric_dict)
        
        return jsonify({
            'status': 'success',
            'data': metrics_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'실시간 메트릭 조회 실패: {str(e)}'
        }), 500

@analytics_bp.route('/realtime/update', methods=['POST'])
def update_realtime_metrics():
    """실시간 메트릭 업데이트"""
    try:
        analytics_manager.update_realtime_metrics()
        
        return jsonify({
            'status': 'success',
            'message': '실시간 메트릭이 업데이트되었습니다',
            'data': {
                'updated_at': datetime.utcnow().isoformat(),
                'metrics_count': len(analytics_manager.realtime_metrics)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'실시간 메트릭 업데이트 실패: {str(e)}'
        }), 500

@analytics_bp.route('/models', methods=['GET'])
def get_prediction_models():
    """예측 모델 조회"""
    try:
        models_data = []
        for model in analytics_manager.prediction_models.values():
            model_dict = {
                'model_id': model.model_id,
                'name': model.name,
                'type': model.type,
                'algorithm': model.algorithm,
                'features': model.features,
                'target': model.target,
                'accuracy': model.accuracy,
                'created_at': model.created_at.isoformat(),
                'last_updated': model.last_updated.isoformat()
            }
            models_data.append(model_dict)
        
        return jsonify({
            'status': 'success',
            'data': models_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'예측 모델 조회 실패: {str(e)}'
        }), 500

@analytics_bp.route('/models', methods=['POST'])
def create_prediction_model():
    """예측 모델 생성"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'type', 'algorithm', 'features', 'target']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} 필드가 필요합니다'
                }), 400
        
        model_id = analytics_manager.create_prediction_model(
            name=data['name'],
            model_type=data['type'],
            algorithm=data['algorithm'],
            features=data['features'],
            target=data['target']
        )
        
        return jsonify({
            'status': 'success',
            'message': f'예측 모델 {data["name"]}이(가) 생성되었습니다',
            'data': {
                'model_id': model_id
            }
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'예측 모델 생성 실패: {str(e)}'
        }), 500

@analytics_bp.route('/analyses', methods=['GET'])
def get_analysis_results():
    """분석 결과 조회"""
    try:
        limit = request.args.get('limit', 50, type=int)
        analysis_type = request.args.get('type')
        
        analyses = list(analytics_manager.analysis_results.values())[:limit]
        
        if analysis_type:
            analyses = [a for a in analyses if a.type == analysis_type]
        
        analyses_data = []
        for analysis in analyses:
            analysis_dict = {
                'analysis_id': analysis.analysis_id,
                'name': analysis.name,
                'type': analysis.type,
                'data_source': analysis.data_source,
                'parameters': analysis.parameters,
                'results': analysis.results,
                'accuracy': analysis.accuracy,
                'created_at': analysis.created_at.isoformat(),
                'updated_at': analysis.updated_at.isoformat()
            }
            analyses_data.append(analysis_dict)
        
        return jsonify({
            'status': 'success',
            'data': analyses_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'분석 결과 조회 실패: {str(e)}'
        }), 500

@analytics_bp.route('/analyses/<analysis_id>', methods=['GET'])
def get_analysis_result(analysis_id):
    """특정 분석 결과 조회"""
    try:
        if analysis_id not in analytics_manager.analysis_results:
            return jsonify({
                'status': 'error',
                'message': f'분석 결과를 찾을 수 없습니다: {analysis_id}'
            }), 404
        
        analysis = analytics_manager.analysis_results[analysis_id]
        analysis_dict = {
            'analysis_id': analysis.analysis_id,
            'name': analysis.name,
            'type': analysis.type,
            'data_source': analysis.data_source,
            'parameters': analysis.parameters,
            'results': analysis.results,
            'accuracy': analysis.accuracy,
            'created_at': analysis.created_at.isoformat(),
            'updated_at': analysis.updated_at.isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': analysis_dict
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'분석 결과 조회 실패: {str(e)}'
        }), 500

@analytics_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """캐시 정리"""
    try:
        analytics_manager.cache.clear()
        
        return jsonify({
            'status': 'success',
            'message': '분석 캐시가 정리되었습니다',
            'data': {
                'cleared_at': datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 정리 실패: {str(e)}'
        }), 500 