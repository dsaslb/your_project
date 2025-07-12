"""
플러그인 AI 분석 및 예측 API
AI 기반 성능 예측, 이상 탐지, 최적화 제안 API 엔드포인트
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from core.backend.plugin_ai_analytics import ai_analytics

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
plugin_ai_analytics_bp = Blueprint('plugin_ai_analytics', __name__, url_prefix='/api/plugin-ai-analytics')

@plugin_ai_analytics_bp.route('/collect-metrics/<plugin_id>', methods=['POST'])
@cross_origin()
async def collect_metrics(plugin_id: str):
    """플러그인 메트릭 수집"""
    try:
        # 비동기 함수 실행
        metrics = await ai_analytics.collect_metrics(plugin_id)
        
        return jsonify({
            "success": True,
            "message": "메트릭 수집 완료",
            "data": {
                "plugin_id": metrics.plugin_id,
                "timestamp": metrics.timestamp.isoformat(),
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "response_time": metrics.response_time,
                "error_rate": metrics.error_rate,
                "request_count": metrics.request_count,
                "active_users": metrics.active_users,
                "uptime": metrics.uptime
            }
        }), 200
        
    except Exception as e:
        logger.error(f"메트릭 수집 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"메트릭 수집 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/train-models/<plugin_id>', methods=['POST'])
@cross_origin()
async def train_models(plugin_id: str):
    """AI 모델 학습"""
    try:
        # 비동기 함수 실행
        success = await ai_analytics.train_models(plugin_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "모델 학습 완료",
                "data": {
                    "plugin_id": plugin_id,
                    "trained_at": datetime.now().isoformat(),
                    "models": ["cpu_usage", "memory_usage", "response_time", "error_rate"],
                    "anomaly_detector": True
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "학습 데이터 부족"
            }), 400
            
    except Exception as e:
        logger.error(f"모델 학습 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"모델 학습 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/predict/<plugin_id>', methods=['GET'])
@cross_origin()
async def predict_performance(plugin_id: str):
    """성능 예측"""
    try:
        hours_ahead = request.args.get('hours', 24, type=int)
        
        # 비동기 함수 실행
        predictions = await ai_analytics.predict_performance(plugin_id, hours_ahead)
        
        return jsonify({
            "success": True,
            "message": "성능 예측 완료",
            "data": {
                "plugin_id": plugin_id,
                "prediction_horizon": hours_ahead,
                "predictions": [
                    {
                        "prediction_type": p.prediction_type,
                        "predicted_value": p.predicted_value,
                        "confidence": p.confidence,
                        "timestamp": p.timestamp.isoformat(),
                        "factors": p.factors
                    }
                    for p in predictions
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"성능 예측 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"성능 예측 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/detect-anomalies/<plugin_id>', methods=['GET'])
@cross_origin()
async def detect_anomalies(plugin_id: str):
    """이상 탐지"""
    try:
        # 비동기 함수 실행
        anomalies = await ai_analytics.detect_anomalies(plugin_id)
        
        return jsonify({
            "success": True,
            "message": "이상 탐지 완료",
            "data": {
                "plugin_id": plugin_id,
                "anomalies_count": len(anomalies),
                "anomalies": [
                    {
                        "anomaly_type": a.anomaly_type,
                        "severity": a.severity,
                        "detected_at": a.detected_at.isoformat(),
                        "description": a.description,
                        "recommendations": a.recommendations
                    }
                    for a in anomalies
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"이상 탐지 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"이상 탐지 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/optimization-suggestions/<plugin_id>', methods=['GET'])
@cross_origin()
async def get_optimization_suggestions(plugin_id: str):
    """최적화 제안 조회"""
    try:
        # 비동기 함수 실행
        suggestions = await ai_analytics.generate_optimization_suggestions(plugin_id)
        
        return jsonify({
            "success": True,
            "message": "최적화 제안 생성 완료",
            "data": {
                "plugin_id": plugin_id,
                "suggestions_count": len(suggestions),
                "suggestions": [
                    {
                        "suggestion_type": s.suggestion_type,
                        "priority": s.priority,
                        "description": s.description,
                        "expected_improvement": s.expected_improvement,
                        "implementation_steps": s.implementation_steps
                    }
                    for s in suggestions
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"최적화 제안 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"최적화 제안 생성 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/analytics-summary/<plugin_id>', methods=['GET'])
@cross_origin()
async def get_analytics_summary(plugin_id: str):
    """분석 요약 정보 조회"""
    try:
        # 비동기 함수 실행
        summary = await ai_analytics.get_analytics_summary(plugin_id)
        
        if "error" in summary:
            return jsonify({
                "success": False,
                "message": summary["error"]
            }), 400
        
        return jsonify({
            "success": True,
            "message": "분석 요약 조회 완료",
            "data": summary
        }), 200
        
    except Exception as e:
        logger.error(f"분석 요약 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"분석 요약 조회 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/export-data/<plugin_id>', methods=['GET'])
@cross_origin()
async def export_analytics_data(plugin_id: str):
    """분석 데이터 내보내기"""
    try:
        format_type = request.args.get('format', 'json')
        
        # 비동기 함수 실행
        filepath = await ai_analytics.export_analytics_data(plugin_id, format_type)
        
        if filepath and filepath != "지원하지 않는 형식입니다":
            return jsonify({
                "success": True,
                "message": "데이터 내보내기 완료",
                "data": {
                    "plugin_id": plugin_id,
                    "format": format_type,
                    "filepath": filepath,
                    "exported_at": datetime.now().isoformat()
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": filepath or "내보내기 실패"
            }), 400
            
    except Exception as e:
        logger.error(f"데이터 내보내기 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"데이터 내보내기 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/batch-analysis', methods=['POST'])
@cross_origin()
async def batch_analysis():
    """배치 분석 실행"""
    try:
        data = request.get_json()
        plugin_ids = data.get('plugin_ids', [])
        
        if not plugin_ids:
            return jsonify({
                "success": False,
                "message": "플러그인 ID 목록이 필요합니다"
            }), 400
        
        results = {}
        
        for plugin_id in plugin_ids:
            try:
                # 메트릭 수집
                await ai_analytics.collect_metrics(plugin_id)
                
                # 모델 학습 (필요시)
                await ai_analytics.train_models(plugin_id)
                
                # 예측
                predictions = await ai_analytics.predict_performance(plugin_id)
                
                # 이상 탐지
                anomalies = await ai_analytics.detect_anomalies(plugin_id)
                
                # 최적화 제안
                suggestions = await ai_analytics.generate_optimization_suggestions(plugin_id)
                
                # 요약
                summary = await ai_analytics.get_analytics_summary(plugin_id)
                
                results[plugin_id] = {
                    "success": True,
                    "predictions_count": len(predictions),
                    "anomalies_count": len(anomalies),
                    "suggestions_count": len(suggestions),
                    "summary": summary
                }
                
            except Exception as e:
                results[plugin_id] = {
                    "success": False,
                    "error": str(e)
                }
        
        return jsonify({
            "success": True,
            "message": "배치 분석 완료",
            "data": {
                "total_plugins": len(plugin_ids),
                "results": results
            }
        }), 200
        
    except Exception as e:
        logger.error(f"배치 분석 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"배치 분석 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/metrics-history/<plugin_id>', methods=['GET'])
@cross_origin()
async def get_metrics_history(plugin_id: str):
    """메트릭 히스토리 조회"""
    try:
        hours = request.args.get('hours', 168, type=int)  # 기본 7일
        
        metrics = ai_analytics.metrics_history.get(plugin_id, [])
        
        # 시간 필터링
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_metrics = [
            m for m in metrics
            if m.timestamp > cutoff_time
        ]
        
        return jsonify({
            "success": True,
            "message": "메트릭 히스토리 조회 완료",
            "data": {
                "plugin_id": plugin_id,
                "period_hours": hours,
                "metrics_count": len(filtered_metrics),
                "metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "cpu_usage": m.cpu_usage,
                        "memory_usage": m.memory_usage,
                        "response_time": m.response_time,
                        "error_rate": m.error_rate,
                        "request_count": m.request_count,
                        "active_users": m.active_users,
                        "uptime": m.uptime
                    }
                    for m in filtered_metrics
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"메트릭 히스토리 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"메트릭 히스토리 조회 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/predictions-history/<plugin_id>', methods=['GET'])
@cross_origin()
async def get_predictions_history(plugin_id: str):
    """예측 히스토리 조회"""
    try:
        predictions = ai_analytics.predictions.get(plugin_id, [])
        
        return jsonify({
            "success": True,
            "message": "예측 히스토리 조회 완료",
            "data": {
                "plugin_id": plugin_id,
                "predictions_count": len(predictions),
                "predictions": [
                    {
                        "prediction_type": p.prediction_type,
                        "predicted_value": p.predicted_value,
                        "confidence": p.confidence,
                        "timestamp": p.timestamp.isoformat(),
                        "factors": p.factors
                    }
                    for p in predictions
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"예측 히스토리 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"예측 히스토리 조회 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/anomalies-history/<plugin_id>', methods=['GET'])
@cross_origin()
async def get_anomalies_history(plugin_id: str):
    """이상 탐지 히스토리 조회"""
    try:
        anomalies = ai_analytics.anomalies.get(plugin_id, [])
        
        return jsonify({
            "success": True,
            "message": "이상 탐지 히스토리 조회 완료",
            "data": {
                "plugin_id": plugin_id,
                "anomalies_count": len(anomalies),
                "anomalies": [
                    {
                        "anomaly_type": a.anomaly_type,
                        "severity": a.severity,
                        "detected_at": a.detected_at.isoformat(),
                        "description": a.description,
                        "recommendations": a.recommendations
                    }
                    for a in anomalies
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"이상 탐지 히스토리 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"이상 탐지 히스토리 조회 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/suggestions-history/<plugin_id>', methods=['GET'])
@cross_origin()
async def get_suggestions_history(plugin_id: str):
    """최적화 제안 히스토리 조회"""
    try:
        suggestions = ai_analytics.suggestions.get(plugin_id, [])
        
        return jsonify({
            "success": True,
            "message": "최적화 제안 히스토리 조회 완료",
            "data": {
                "plugin_id": plugin_id,
                "suggestions_count": len(suggestions),
                "suggestions": [
                    {
                        "suggestion_type": s.suggestion_type,
                        "priority": s.priority,
                        "description": s.description,
                        "expected_improvement": s.expected_improvement,
                        "implementation_steps": s.implementation_steps
                    }
                    for s in suggestions
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"최적화 제안 히스토리 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"최적화 제안 히스토리 조회 실패: {str(e)}"
        }), 500

@plugin_ai_analytics_bp.route('/system-status', methods=['GET'])
@cross_origin()
async def get_system_status():
    """시스템 상태 조회"""
    try:
        total_plugins = len(ai_analytics.metrics_history)
        total_metrics = sum(len(metrics) for metrics in ai_analytics.metrics_history.values())
        total_predictions = sum(len(predictions) for predictions in ai_analytics.predictions.values())
        total_anomalies = sum(len(anomalies) for anomalies in ai_analytics.anomalies.values())
        total_suggestions = sum(len(suggestions) for suggestions in ai_analytics.suggestions.values())
        
        return jsonify({
            "success": True,
            "message": "시스템 상태 조회 완료",
            "data": {
                "total_plugins": total_plugins,
                "total_metrics": total_metrics,
                "total_predictions": total_predictions,
                "total_anomalies": total_anomalies,
                "total_suggestions": total_suggestions,
                "models_trained": len(ai_analytics.models),
                "anomaly_detectors": len(ai_analytics.anomaly_detectors),
                "last_updated": datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"시스템 상태 API 오류: {e}")
        return jsonify({
            "success": False,
            "message": f"시스템 상태 조회 실패: {str(e)}"
        }), 500 