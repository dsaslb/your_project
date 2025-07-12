"""
플러그인 AI 분석 및 예측 시스템 테스트
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import numpy as np

from core.backend.plugin_ai_analytics import (
    PluginAIAnalytics,
    PluginMetrics,
    PredictionResult,
    AnomalyDetection,
    OptimizationSuggestion
)

class TestPluginAIAnalytics:
    """플러그인 AI 분석 시스템 테스트"""
    
    @pytest.fixture
    def ai_analytics(self):
        """테스트용 AI 분석 시스템 인스턴스"""
        return PluginAIAnalytics(data_dir="test_data/ai_analytics")
    
    @pytest.fixture
    def sample_metrics(self):
        """샘플 메트릭 데이터"""
        return [
            PluginMetrics(
                plugin_id="test_plugin",
                timestamp=datetime.now() - timedelta(hours=i),
                cpu_usage=30 + np.random.normal(0, 5),
                memory_usage=50 + np.random.normal(0, 10),
                response_time=200 + np.random.normal(0, 50),
                error_rate=2 + np.random.normal(0, 1),
                request_count=np.random.poisson(100),
                active_users=np.random.poisson(50),
                uptime=98 + np.random.normal(0, 1)
            )
            for i in range(168)  # 7일간 데이터
        ]
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, ai_analytics):
        """메트릭 수집 테스트"""
        plugin_id = "test_plugin"
        
        # 메트릭 수집
        metrics = await ai_analytics.collect_metrics(plugin_id)
        
        # 검증
        assert metrics.plugin_id == plugin_id
        assert isinstance(metrics.timestamp, datetime)
        assert 0 <= metrics.cpu_usage <= 100
        assert 0 <= metrics.memory_usage <= 100
        assert metrics.response_time > 0
        assert 0 <= metrics.error_rate <= 100
        assert metrics.request_count >= 0
        assert metrics.active_users >= 0
        assert 0 <= metrics.uptime <= 100
        
        # 히스토리에 저장되었는지 확인
        assert len(ai_analytics.metrics_history[plugin_id]) > 0
    
    @pytest.mark.asyncio
    async def test_prepare_features(self, ai_analytics, sample_metrics):
        """특성 데이터 준비 테스트"""
        plugin_id = "test_plugin"
        
        # 샘플 데이터 추가
        ai_analytics.metrics_history[plugin_id] = sample_metrics
        
        # 특성 준비
        features, targets = ai_analytics.prepare_features(plugin_id)
        
        # 검증
        assert len(features) > 0
        assert len(targets) > 0
        assert features.shape[1] == 192  # 24시간 * 8특성
        assert targets.shape[1] == 4  # 4개 타겟
    
    @pytest.mark.asyncio
    async def test_train_models(self, ai_analytics, sample_metrics):
        """모델 학습 테스트"""
        plugin_id = "test_plugin"
        
        # 샘플 데이터 추가
        ai_analytics.metrics_history[plugin_id] = sample_metrics
        
        # 모델 학습
        success = await ai_analytics.train_models(plugin_id)
        
        # 검증
        assert success is True
        assert plugin_id in ai_analytics.models
        assert plugin_id in ai_analytics.scalers
        assert plugin_id in ai_analytics.anomaly_detectors
        assert plugin_id in ai_analytics.last_training
        
        # 모델 구조 검증
        models = ai_analytics.models[plugin_id]
        assert 'cpu_usage' in models
        assert 'memory_usage' in models
        assert 'response_time' in models
        assert 'error_rate' in models
    
    @pytest.mark.asyncio
    async def test_predict_performance(self, ai_analytics, sample_metrics):
        """성능 예측 테스트"""
        plugin_id = "test_plugin"
        
        # 샘플 데이터 추가 및 모델 학습
        ai_analytics.metrics_history[plugin_id] = sample_metrics
        await ai_analytics.train_models(plugin_id)
        
        # 성능 예측
        predictions = await ai_analytics.predict_performance(plugin_id)
        
        # 검증
        assert len(predictions) == 4  # 4개 타겟
        assert all(isinstance(p, PredictionResult) for p in predictions)
        
        # 예측 타입 검증
        prediction_types = [p.prediction_type for p in predictions]
        assert 'cpu_usage' in prediction_types
        assert 'memory_usage' in prediction_types
        assert 'response_time' in prediction_types
        assert 'error_rate' in prediction_types
        
        # 예측값 범위 검증
        for pred in predictions:
            assert pred.predicted_value >= 0
            assert 0 <= pred.confidence <= 100
            assert isinstance(pred.factors, dict)
    
    @pytest.mark.asyncio
    async def test_detect_anomalies(self, ai_analytics, sample_metrics):
        """이상 탐지 테스트"""
        plugin_id = "test_plugin"
        
        # 샘플 데이터 추가 및 모델 학습
        ai_analytics.metrics_history[plugin_id] = sample_metrics
        await ai_analytics.train_models(plugin_id)
        
        # 이상 탐지
        anomalies = await ai_analytics.detect_anomalies(plugin_id)
        
        # 검증
        assert isinstance(anomalies, list)
        assert all(isinstance(a, AnomalyDetection) for a in anomalies)
        
        # 이상 탐지 결과 검증
        for anomaly in anomalies:
            assert anomaly.plugin_id == plugin_id
            assert anomaly.anomaly_type in [
                'high_cpu_usage', 'high_memory_usage', 
                'slow_response', 'high_error_rate'
            ]
            assert anomaly.severity in ['low', 'medium', 'high']
            assert isinstance(anomaly.description, str)
            assert isinstance(anomaly.recommendations, list)
            assert len(anomaly.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_generate_optimization_suggestions(self, ai_analytics, sample_metrics):
        """최적화 제안 생성 테스트"""
        plugin_id = "test_plugin"
        
        # 샘플 데이터 추가
        ai_analytics.metrics_history[plugin_id] = sample_metrics
        
        # 최적화 제안 생성
        suggestions = await ai_analytics.generate_optimization_suggestions(plugin_id)
        
        # 검증
        assert isinstance(suggestions, list)
        assert all(isinstance(s, OptimizationSuggestion) for s in suggestions)
        
        # 제안 내용 검증
        for suggestion in suggestions:
            assert suggestion.plugin_id == plugin_id
            assert suggestion.suggestion_type in [
                'cpu_optimization', 'memory_optimization',
                'response_optimization', 'error_optimization'
            ]
            assert suggestion.priority in ['low', 'medium', 'high']
            assert isinstance(suggestion.description, str)
            assert suggestion.expected_improvement > 0
            assert isinstance(suggestion.implementation_steps, list)
            assert len(suggestion.implementation_steps) > 0
    
    @pytest.mark.asyncio
    async def test_get_analytics_summary(self, ai_analytics, sample_metrics):
        """분석 요약 테스트"""
        plugin_id = "test_plugin"
        
        # 샘플 데이터 추가
        ai_analytics.metrics_history[plugin_id] = sample_metrics
        
        # 분석 요약
        summary = await ai_analytics.get_analytics_summary(plugin_id)
        
        # 검증
        assert isinstance(summary, dict)
        assert summary['plugin_id'] == plugin_id
        assert summary['total_metrics'] == len(sample_metrics)
        assert summary['analysis_period'] == '7일'
        assert summary['current_status'] == 'active'
        
        # 성능 메트릭 검증
        performance_metrics = summary['performance_metrics']
        assert 'avg_cpu_usage' in performance_metrics
        assert 'avg_memory_usage' in performance_metrics
        assert 'avg_response_time' in performance_metrics
        assert 'avg_error_rate' in performance_metrics
        assert 'total_requests' in performance_metrics
        assert 'avg_uptime' in performance_metrics
        
        # 트렌드 검증
        trends = summary['trends']
        assert 'cpu_trend' in trends
        assert 'memory_trend' in trends
        assert 'response_trend' in trends
        assert 'error_trend' in trends
    
    @pytest.mark.asyncio
    async def test_export_analytics_data(self, ai_analytics, sample_metrics):
        """데이터 내보내기 테스트"""
        plugin_id = "test_plugin"
        
        # 샘플 데이터 추가
        ai_analytics.metrics_history[plugin_id] = sample_metrics
        
        # 데이터 내보내기
        filepath = await ai_analytics.export_analytics_data(plugin_id, 'json')
        
        # 검증
        assert isinstance(filepath, str)
        assert filepath.endswith('.json')
        assert 'analytics_' in filepath
        assert plugin_id in filepath
    
    @pytest.mark.asyncio
    async def test_insufficient_data_handling(self, ai_analytics):
        """데이터 부족 상황 처리 테스트"""
        plugin_id = "test_plugin"
        
        # 데이터가 없는 경우
        features, targets = ai_analytics.prepare_features(plugin_id)
        assert len(features) == 0
        assert len(targets) == 0
        
        # 모델 학습 실패
        success = await ai_analytics.train_models(plugin_id)
        assert success is False
        
        # 예측 실패
        predictions = await ai_analytics.predict_performance(plugin_id)
        assert len(predictions) == 0
        
        # 이상 탐지 실패
        anomalies = await ai_analytics.detect_anomalies(plugin_id)
        assert len(anomalies) == 0
    
    @pytest.mark.asyncio
    async def test_data_cleanup(self, ai_analytics):
        """데이터 정리 테스트"""
        plugin_id = "test_plugin"
        
        # 오래된 데이터 생성
        old_metrics = [
            PluginMetrics(
                plugin_id=plugin_id,
                timestamp=datetime.now() - timedelta(days=31),
                cpu_usage=30,
                memory_usage=50,
                response_time=200,
                error_rate=2,
                request_count=100,
                active_users=50,
                uptime=98
            )
        ]
        
        # 최신 데이터 생성
        recent_metrics = [
            PluginMetrics(
                plugin_id=plugin_id,
                timestamp=datetime.now(),
                cpu_usage=30,
                memory_usage=50,
                response_time=200,
                error_rate=2,
                request_count=100,
                active_users=50,
                uptime=98
            )
        ]
        
        # 데이터 추가
        ai_analytics.metrics_history[plugin_id] = old_metrics + recent_metrics
        
        # 메트릭 수집 (정리 트리거)
        await ai_analytics.collect_metrics(plugin_id)
        
        # 오래된 데이터가 정리되었는지 확인
        remaining_metrics = ai_analytics.metrics_history[plugin_id]
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for metric in remaining_metrics:
            assert metric.timestamp > cutoff_date

class TestPluginMetrics:
    """플러그인 메트릭 테스트"""
    
    def test_plugin_metrics_creation(self):
        """메트릭 생성 테스트"""
        timestamp = datetime.now()
        metrics = PluginMetrics(
            plugin_id="test_plugin",
            timestamp=timestamp,
            cpu_usage=30.5,
            memory_usage=45.2,
            response_time=250.0,
            error_rate=1.5,
            request_count=150,
            active_users=75,
            uptime=99.5
        )
        
        assert metrics.plugin_id == "test_plugin"
        assert metrics.timestamp == timestamp
        assert metrics.cpu_usage == 30.5
        assert metrics.memory_usage == 45.2
        assert metrics.response_time == 250.0
        assert metrics.error_rate == 1.5
        assert metrics.request_count == 150
        assert metrics.active_users == 75
        assert metrics.uptime == 99.5

class TestPredictionResult:
    """예측 결과 테스트"""
    
    def test_prediction_result_creation(self):
        """예측 결과 생성 테스트"""
        timestamp = datetime.now()
        factors = {"trend": "stable", "confidence": 0.85}
        
        prediction = PredictionResult(
            plugin_id="test_plugin",
            prediction_type="cpu_usage",
            predicted_value=35.2,
            confidence=85.5,
            timestamp=timestamp,
            factors=factors
        )
        
        assert prediction.plugin_id == "test_plugin"
        assert prediction.prediction_type == "cpu_usage"
        assert prediction.predicted_value == 35.2
        assert prediction.confidence == 85.5
        assert prediction.timestamp == timestamp
        assert prediction.factors == factors

class TestAnomalyDetection:
    """이상 탐지 테스트"""
    
    def test_anomaly_detection_creation(self):
        """이상 탐지 결과 생성 테스트"""
        detected_at = datetime.now()
        recommendations = ["리소스 증가", "코드 최적화"]
        
        anomaly = AnomalyDetection(
            plugin_id="test_plugin",
            anomaly_type="high_cpu_usage",
            severity="high",
            detected_at=detected_at,
            description="CPU 사용률이 90%를 초과했습니다",
            recommendations=recommendations
        )
        
        assert anomaly.plugin_id == "test_plugin"
        assert anomaly.anomaly_type == "high_cpu_usage"
        assert anomaly.severity == "high"
        assert anomaly.detected_at == detected_at
        assert anomaly.description == "CPU 사용률이 90%를 초과했습니다"
        assert anomaly.recommendations == recommendations

class TestOptimizationSuggestion:
    """최적화 제안 테스트"""
    
    def test_optimization_suggestion_creation(self):
        """최적화 제안 생성 테스트"""
        implementation_steps = ["캐싱 도입", "쿼리 최적화"]
        
        suggestion = OptimizationSuggestion(
            plugin_id="test_plugin",
            suggestion_type="cpu_optimization",
            priority="high",
            description="CPU 사용률 최적화가 필요합니다",
            expected_improvement=25.0,
            implementation_steps=implementation_steps
        )
        
        assert suggestion.plugin_id == "test_plugin"
        assert suggestion.suggestion_type == "cpu_optimization"
        assert suggestion.priority == "high"
        assert suggestion.description == "CPU 사용률 최적화가 필요합니다"
        assert suggestion.expected_improvement == 25.0
        assert suggestion.implementation_steps == implementation_steps

# 통합 테스트
class TestIntegration:
    """통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_full_analytics_workflow(self):
        """전체 분석 워크플로우 테스트"""
        ai_analytics = PluginAIAnalytics(data_dir="test_data/integration")
        plugin_id = "integration_test_plugin"
        
        # 1. 메트릭 수집
        metrics = await ai_analytics.collect_metrics(plugin_id)
        assert metrics is not None
        
        # 2. 충분한 데이터 수집 (24시간)
        for _ in range(25):
            await ai_analytics.collect_metrics(plugin_id)
        
        # 3. 모델 학습
        success = await ai_analytics.train_models(plugin_id)
        assert success is True
        
        # 4. 성능 예측
        predictions = await ai_analytics.predict_performance(plugin_id)
        assert len(predictions) > 0
        
        # 5. 이상 탐지
        anomalies = await ai_analytics.detect_anomalies(plugin_id)
        assert isinstance(anomalies, list)
        
        # 6. 최적화 제안
        suggestions = await ai_analytics.generate_optimization_suggestions(plugin_id)
        assert isinstance(suggestions, list)
        
        # 7. 분석 요약
        summary = await ai_analytics.get_analytics_summary(plugin_id)
        assert summary is not None
        assert 'error' not in summary
        
        # 8. 데이터 내보내기
        filepath = await ai_analytics.export_analytics_data(plugin_id)
        assert filepath is not None
        assert filepath != ""

if __name__ == "__main__":
    pytest.main([__file__]) 