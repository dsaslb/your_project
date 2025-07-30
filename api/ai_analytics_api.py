# -*- coding: utf-8 -*-
"""
AI 분석 API
성능 예측, 트렌드 분석, 최적화 권장사항을 제공하는 API
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required
import logging
from datetime import datetime

# AI 분석 도구 import
from ai.performance_predictor import (
    train_performance_models,
    predict_future_performance,
    get_performance_analysis
)

logger = logging.getLogger(__name__)

ai_analytics_api = Blueprint('ai_analytics_api', __name__)


@ai_analytics_api.route('/api/ai/train', methods=['POST'])
@login_required
def train_ai_models():
    """AI 모델 훈련"""
    try:
        result = train_performance_models()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI 모델 훈련 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': 'AI 모델 훈련 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500


@ai_analytics_api.route('/api/ai/predict', methods=['GET'])
@login_required
def predict_performance():
    """성능 예측"""
    try:
        hours = request.args.get('hours', 24, type=int)
        predictions = predict_future_performance(hours)
        
        if not predictions:
            return jsonify({
                'status': 'error',
                'message': '예측을 위한 훈련된 모델이 없습니다. 먼저 모델을 훈련하세요.'
            }), 400
            
        return jsonify(predictions)
        
    except Exception as e:
        logger.error(f"성능 예측 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': '성능 예측 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500


@ai_analytics_api.route('/api/ai/analysis', methods=['GET'])
@login_required
def get_analysis():
    """성능 분석 결과 조회"""
    try:
        analysis = get_performance_analysis()
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"성능 분석 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': '성능 분석 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500


@ai_analytics_api.route('/api/ai/trends', methods=['GET'])
@login_required
def get_trends():
    """성능 트렌드 조회"""
    try:
        from ai.performance_predictor import performance_predictor
        trends = performance_predictor.get_performance_trends()
        return jsonify(trends)
        
    except Exception as e:
        logger.error(f"트렌드 분석 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': '트렌드 분석 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500


@ai_analytics_api.route('/api/ai/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """최적화 권장사항 조회"""
    try:
        from ai.performance_predictor import performance_predictor
        recommendations = performance_predictor.get_optimization_recommendations()
        return jsonify({
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"권장사항 생성 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': '권장사항 생성 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500


@ai_analytics_api.route('/api/ai/models/status', methods=['GET'])
@login_required
def get_model_status():
    """AI 모델 상태 조회"""
    try:
        import os
        from ai.performance_predictor import performance_predictor
        
        model_status = {}
        target_columns = ['cpu_percent', 'memory_percent', 'response_time']
        
        for target in target_columns:
            model_file = f"ai/models/{target}_model.pkl"
            scaler_file = f"ai/scalers/{target}_scaler.pkl"
            
            model_status[target] = {
                'model_exists': os.path.exists(model_file),
                'scaler_exists': os.path.exists(scaler_file),
                'model_size': os.path.getsize(model_file) if os.path.exists(model_file) else 0,
                'scaler_size': os.path.getsize(scaler_file) if os.path.exists(scaler_file) else 0
            }
            
        return jsonify({
            'model_status': model_status,
            'total_models': len([s for s in model_status.values() if s['model_exists']]),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"모델 상태 조회 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': '모델 상태 조회 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500


@ai_analytics_api.route('/api/ai/models/delete', methods=['DELETE'])
@login_required
def delete_models():
    """AI 모델 삭제"""
    try:
        import os
        import glob
        
        # 모델 파일 삭제
        model_files = glob.glob('ai/models/*.pkl')
        scaler_files = glob.glob('ai/scalers/*.pkl')
        
        deleted_count = 0
        for file_path in model_files + scaler_files:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                logger.warning(f"파일 삭제 실패: {file_path} - {e}")
                
        return jsonify({
            'status': 'success',
            'message': f'{deleted_count}개의 모델 파일이 삭제되었습니다.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"모델 삭제 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': '모델 삭제 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500


@ai_analytics_api.route('/api/ai/data/export', methods=['GET'])
@login_required
def export_performance_data():
    """성능 데이터 내보내기"""
    try:
        import pandas as pd
        from ai.performance_predictor import performance_predictor
        
        days = request.args.get('days', 7, type=int)
        df = performance_predictor.load_performance_data(days)
        
        if df.empty:
            return jsonify({
                'status': 'error',
                'message': '내보낼 데이터가 없습니다.'
            }), 400
            
        # CSV 파일로 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'performance_data_{timestamp}.csv'
        filepath = f'data/exports/{filename}'
        
        # 디렉토리 생성
        import os
        os.makedirs('data/exports', exist_ok=True)
        
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return jsonify({
            'status': 'success',
            'message': '성능 데이터가 내보내기되었습니다.',
            'filename': filename,
            'filepath': filepath,
            'rows': len(df),
            'columns': list(df.columns)
        })
        
    except Exception as e:
        logger.error(f"데이터 내보내기 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': '데이터 내보내기 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500


@ai_analytics_api.route('/api/ai/insights', methods=['GET'])
@login_required
def get_ai_insights():
    """AI 인사이트 생성"""
    try:
        from ai.performance_predictor import performance_predictor
        
        # 성능 분석
        analysis = get_performance_analysis()
        
        # 추가 인사이트 생성
        insights = {
            'performance_summary': {
                'overall_health': 'good',
                'main_concerns': [],
                'optimization_opportunities': []
            },
            'predictions': {
                'next_24h_trend': 'stable',
                'potential_issues': [],
                'recommended_actions': []
            },
            'patterns': {
                'peak_usage_times': [],
                'low_usage_times': [],
                'anomaly_detection': []
            }
        }
        
        # 성능 상태 평가
        if analysis.get('trends', {}).get('recent_statistics'):
            stats = analysis['trends']['recent_statistics']
            
            # CPU 상태 평가
            cpu_avg = stats.get('cpu_percent', {}).get('mean', 0)
            if cpu_avg > 70:
                insights['performance_summary']['main_concerns'].append('CPU 사용률이 높습니다')
            elif cpu_avg < 30:
                insights['performance_summary']['optimization_opportunities'].append('CPU 리소스 활용도 개선 가능')
                
            # 메모리 상태 평가
            memory_avg = stats.get('memory_percent', {}).get('mean', 0)
            if memory_avg > 80:
                insights['performance_summary']['main_concerns'].append('메모리 사용률이 높습니다')
                
            # 응답시간 평가
            response_avg = stats.get('response_time', {}).get('mean', 0)
            if response_avg > 3:
                insights['performance_summary']['main_concerns'].append('응답시간이 느립니다')
                
        # 패턴 분석
        if analysis.get('trends', {}).get('patterns'):
            patterns = analysis['trends']['patterns']
            
            # 피크 시간 추가
            if patterns.get('peak_hours'):
                insights['patterns']['peak_usage_times'] = [
                    f"CPU: {patterns['peak_hours']['cpu']}시",
                    f"메모리: {patterns['peak_hours']['memory']}시"
                ]
                
        # 권장사항 기반 인사이트
        if analysis.get('recommendations'):
            recommendations = analysis['recommendations']
            warning_count = len([r for r in recommendations if r['type'] == 'warning'])
            
            if warning_count > 0:
                insights['performance_summary']['overall_health'] = 'attention_needed'
                insights['predictions']['next_24h_trend'] = 'monitoring_required'
                
        return jsonify({
            'insights': insights,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI 인사이트 생성 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': 'AI 인사이트 생성 중 오류가 발생했습니다.',
            'error': str(e)
        }), 500 