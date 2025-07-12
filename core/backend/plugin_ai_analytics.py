"""
플러그인 AI 예측 및 분석 시스템
AI 기반 성능 예측, 사용 패턴 분석, 자동 최적화 제안
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import asyncio
import aiohttp
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PluginMetrics:
    """플러그인 메트릭 데이터"""
    plugin_id: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    request_count: int
    active_users: int
    uptime: float

@dataclass
class PredictionResult:
    """예측 결과"""
    plugin_id: str
    prediction_type: str
    predicted_value: float
    confidence: float
    timestamp: datetime
    factors: Dict[str, float]

@dataclass
class AnomalyDetection:
    """이상 탐지 결과"""
    plugin_id: str
    anomaly_type: str
    severity: str
    detected_at: datetime
    description: str
    recommendations: List[str]

@dataclass
class OptimizationSuggestion:
    """최적화 제안"""
    plugin_id: str
    suggestion_type: str
    priority: str
    description: str
    expected_improvement: float
    implementation_steps: List[str]

class PluginAIAnalytics:
    """플러그인 AI 분석 및 예측 시스템"""
    
    def __init__(self, data_dir: str = "data/ai_analytics"):
        self.data_dir = data_dir
        self.models_dir = os.path.join(data_dir, "models")
        self.scalers_dir = os.path.join(data_dir, "scalers")
        
        # 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.scalers_dir, exist_ok=True)
        
        # 모델 저장소
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        
        # 데이터 저장소
        self.metrics_history: Dict[str, List[PluginMetrics]] = defaultdict(list)
        self.predictions: Dict[str, List[PredictionResult]] = defaultdict(list)
        self.anomalies: Dict[str, List[AnomalyDetection]] = defaultdict(list)
        self.suggestions: Dict[str, List[OptimizationSuggestion]] = defaultdict(list)
        
        # 설정
        self.prediction_horizon = 24  # 24시간 예측
        self.retraining_interval = 168  # 7일마다 재학습
        self.last_training: Dict[str, datetime] = {}
        
        logger.info("플러그인 AI 분석 시스템 초기화 완료")
    
    async def collect_metrics(self, plugin_id: str) -> PluginMetrics:
        """플러그인 메트릭 수집"""
        try:
            # 실제 환경에서는 플러그인 모니터링 시스템에서 데이터를 가져옴
            # 여기서는 시뮬레이션 데이터 생성
            current_time = datetime.now()
            
            # 기본 메트릭 생성
            base_cpu = np.random.normal(30, 10)
            base_memory = np.random.normal(50, 15)
            base_response = np.random.normal(200, 50)
            
            # 시간대별 변동 추가
            hour = current_time.hour
            if 9 <= hour <= 18:  # 업무시간
                cpu_usage = min(100, base_cpu * 1.5)
                memory_usage = min(100, base_memory * 1.3)
                request_count = np.random.poisson(100)
                active_users = np.random.poisson(50)
            else:  # 비업무시간
                cpu_usage = max(5, base_cpu * 0.3)
                memory_usage = max(10, base_memory * 0.5)
                request_count = np.random.poisson(20)
                active_users = np.random.poisson(10)
            
            # 에러율 계산
            error_rate = np.random.beta(2, 98) * 100  # 평균 2% 에러율
            
            # 응답시간 계산
            response_time = base_response * (1 + cpu_usage / 100)
            
            # 가동시간 (시뮬레이션)
            uptime = np.random.uniform(95, 99.9)
            
            metrics = PluginMetrics(
                plugin_id=plugin_id,
                timestamp=current_time,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                response_time=response_time,
                error_rate=error_rate,
                request_count=request_count,
                active_users=active_users,
                uptime=uptime
            )
            
            self.metrics_history[plugin_id].append(metrics)
            
            # 데이터 정리 (최근 30일만 유지)
            cutoff_date = current_time - timedelta(days=30)
            self.metrics_history[plugin_id] = [
                m for m in self.metrics_history[plugin_id]
                if m.timestamp > cutoff_date
            ]
            
            logger.info(f"플러그인 {plugin_id} 메트릭 수집 완료")
            return metrics
            
        except Exception as e:
            logger.error(f"메트릭 수집 실패: {e}")
            raise
    
    def prepare_features(self, plugin_id: str, hours: int = 168) -> Tuple[np.ndarray, np.ndarray]:
        """특성 데이터 준비"""
        try:
            metrics = self.metrics_history[plugin_id]
            if len(metrics) < 24:  # 최소 24시간 데이터 필요
                return np.array([]), np.array([])
            
            # 시간 윈도우 데이터 준비
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in metrics if m.timestamp > cutoff_time]
            
            if len(recent_metrics) < 24:
                return np.array([]), np.ndarray([])
            
            # 특성 추출
            features = []
            targets = []
            
            for i in range(len(recent_metrics) - 24):
                window = recent_metrics[i:i+24]
                next_hour = recent_metrics[i+24]
                
                # 시간 특성
                hour_features = []
                for metric in window:
                    hour_features.extend([
                        metric.cpu_usage,
                        metric.memory_usage,
                        metric.response_time,
                        metric.error_rate,
                        metric.request_count,
                        metric.active_users,
                        metric.timestamp.hour,
                        metric.timestamp.weekday()
                    ])
                
                features.append(hour_features)
                targets.append([
                    next_hour.cpu_usage,
                    next_hour.memory_usage,
                    next_hour.response_time,
                    next_hour.error_rate
                ])
            
            return np.array(features), np.array(targets)
            
        except Exception as e:
            logger.error(f"특성 준비 실패: {e}")
            return np.array([]), np.array([])
    
    async def train_models(self, plugin_id: str) -> bool:
        """AI 모델 학습"""
        try:
            features, targets = self.prepare_features(plugin_id)
            
            if len(features) == 0 or len(targets) == 0:
                logger.warning(f"플러그인 {plugin_id} 학습 데이터 부족")
                return False
            
            # 특성 스케일링
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # 모델 학습
            models = {}
            for i, target_name in enumerate(['cpu_usage', 'memory_usage', 'response_time', 'error_rate']):
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                model.fit(features_scaled, targets[:, i])
                models[target_name] = model
            
            # 이상 탐지 모델
            anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            anomaly_detector.fit(features_scaled)
            
            # 모델 저장
            self.models[plugin_id] = models
            self.scalers[plugin_id] = scaler
            self.anomaly_detectors[plugin_id] = anomaly_detector
            self.last_training[plugin_id] = datetime.now()
            
            # 파일로 저장
            for target_name, model in models.items():
                model_path = os.path.join(self.models_dir, f"{plugin_id}_{target_name}.joblib")
                joblib.dump(model, model_path)
            
            scaler_path = os.path.join(self.scalers_dir, f"{plugin_id}_scaler.joblib")
            joblib.dump(scaler, scaler_path)
            
            logger.info(f"플러그인 {plugin_id} 모델 학습 완료")
            return True
            
        except Exception as e:
            logger.error(f"모델 학습 실패: {e}")
            return False
    
    async def predict_performance(self, plugin_id: str, hours_ahead: int = 24) -> List[PredictionResult]:
        """성능 예측"""
        try:
            if plugin_id not in self.models:
                await self.train_models(plugin_id)
            
            if plugin_id not in self.models:
                return []
            
            # 최근 데이터로 예측
            features, _ = self.prepare_features(plugin_id, hours=24)
            
            if len(features) == 0:
                return []
            
            latest_features = features[-1:].reshape(1, -1)
            features_scaled = self.scalers[plugin_id].transform(latest_features)
            
            predictions = []
            target_names = ['cpu_usage', 'memory_usage', 'response_time', 'error_rate']
            
            for target_name in target_names:
                model = self.models[plugin_id][target_name]
                predicted_value = model.predict(features_scaled)[0]
                
                # 신뢰도 계산 (모델의 feature importance 기반)
                feature_importance = model.feature_importances_
                confidence = np.mean(feature_importance) * 100
                
                prediction = PredictionResult(
                    plugin_id=plugin_id,
                    prediction_type=target_name,
                    predicted_value=predicted_value,
                    confidence=confidence,
                    timestamp=datetime.now(),
                    factors={
                        'recent_trend': 'stable',
                        'seasonal_pattern': 'detected',
                        'load_prediction': 'moderate'
                    }
                )
                predictions.append(prediction)
            
            self.predictions[plugin_id].extend(predictions)
            logger.info(f"플러그인 {plugin_id} 성능 예측 완료")
            return predictions
            
        except Exception as e:
            logger.error(f"성능 예측 실패: {e}")
            return []
    
    async def detect_anomalies(self, plugin_id: str) -> List[AnomalyDetection]:
        """이상 탐지"""
        try:
            if plugin_id not in self.anomaly_detectors:
                await self.train_models(plugin_id)
            
            if plugin_id not in self.anomaly_detectors:
                return []
            
            features, _ = self.prepare_features(plugin_id, hours=24)
            
            if len(features) == 0:
                return []
            
            features_scaled = self.scalers[plugin_id].transform(features)
            anomaly_scores = self.anomaly_detectors[plugin_id].predict(features_scaled)
            
            anomalies = []
            latest_metrics = self.metrics_history[plugin_id][-1] if self.metrics_history[plugin_id] else None
            
            if latest_metrics:
                # CPU 사용률 이상
                if latest_metrics.cpu_usage > 90:
                    anomaly = AnomalyDetection(
                        plugin_id=plugin_id,
                        anomaly_type="high_cpu_usage",
                        severity="high",
                        detected_at=datetime.now(),
                        description=f"CPU 사용률이 90%를 초과했습니다: {latest_metrics.cpu_usage:.1f}%",
                        recommendations=[
                            "플러그인 인스턴스 수 증가",
                            "리소스 할당량 조정",
                            "성능 최적화 검토"
                        ]
                    )
                    anomalies.append(anomaly)
                
                # 메모리 사용률 이상
                if latest_metrics.memory_usage > 85:
                    anomaly = AnomalyDetection(
                        plugin_id=plugin_id,
                        anomaly_type="high_memory_usage",
                        severity="medium",
                        detected_at=datetime.now(),
                        description=f"메모리 사용률이 85%를 초과했습니다: {latest_metrics.memory_usage:.1f}%",
                        recommendations=[
                            "메모리 할당량 증가",
                            "메모리 누수 검사",
                            "캐시 정리"
                        ]
                    )
                    anomalies.append(anomaly)
                
                # 응답시간 이상
                if latest_metrics.response_time > 1000:
                    anomaly = AnomalyDetection(
                        plugin_id=plugin_id,
                        anomaly_type="slow_response",
                        severity="medium",
                        detected_at=datetime.now(),
                        description=f"응답시간이 1초를 초과했습니다: {latest_metrics.response_time:.0f}ms",
                        recommendations=[
                            "데이터베이스 쿼리 최적화",
                            "캐싱 전략 개선",
                            "로드 밸런싱 검토"
                        ]
                    )
                    anomalies.append(anomaly)
                
                # 에러율 이상
                if latest_metrics.error_rate > 5:
                    anomaly = AnomalyDetection(
                        plugin_id=plugin_id,
                        anomaly_type="high_error_rate",
                        severity="high",
                        detected_at=datetime.now(),
                        description=f"에러율이 5%를 초과했습니다: {latest_metrics.error_rate:.1f}%",
                        recommendations=[
                            "에러 로그 분석",
                            "코드 품질 검토",
                            "의존성 업데이트"
                        ]
                    )
                    anomalies.append(anomaly)
            
            self.anomalies[plugin_id].extend(anomalies)
            logger.info(f"플러그인 {plugin_id} 이상 탐지 완료: {len(anomalies)}개 발견")
            return anomalies
            
        except Exception as e:
            logger.error(f"이상 탐지 실패: {e}")
            return []
    
    async def generate_optimization_suggestions(self, plugin_id: str) -> List[OptimizationSuggestion]:
        """최적화 제안 생성"""
        try:
            suggestions = []
            
            if plugin_id not in self.metrics_history:
                return suggestions
            
            metrics = self.metrics_history[plugin_id]
            if len(metrics) < 24:
                return suggestions
            
            # 최근 24시간 평균 계산
            recent_metrics = metrics[-24:]
            avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
            avg_memory = np.mean([m.memory_usage for m in recent_metrics])
            avg_response = np.mean([m.response_time for m in recent_metrics])
            avg_error = np.mean([m.error_rate for m in recent_metrics])
            
            # CPU 최적화 제안
            if avg_cpu > 70:
                suggestion = OptimizationSuggestion(
                    plugin_id=plugin_id,
                    suggestion_type="cpu_optimization",
                    priority="high",
                    description=f"평균 CPU 사용률이 {avg_cpu:.1f}%로 높습니다",
                    expected_improvement=20.0,
                    implementation_steps=[
                        "비동기 처리 도입",
                        "캐싱 레이어 추가",
                        "배치 처리 최적화"
                    ]
                )
                suggestions.append(suggestion)
            
            # 메모리 최적화 제안
            if avg_memory > 75:
                suggestion = OptimizationSuggestion(
                    plugin_id=plugin_id,
                    suggestion_type="memory_optimization",
                    priority="medium",
                    description=f"평균 메모리 사용률이 {avg_memory:.1f}%로 높습니다",
                    expected_improvement=15.0,
                    implementation_steps=[
                        "메모리 풀 도입",
                        "불필요한 객체 정리",
                        "메모리 매핑 최적화"
                    ]
                )
                suggestions.append(suggestion)
            
            # 응답시간 최적화 제안
            if avg_response > 500:
                suggestion = OptimizationSuggestion(
                    plugin_id=plugin_id,
                    suggestion_type="response_optimization",
                    priority="medium",
                    description=f"평균 응답시간이 {avg_response:.0f}ms로 느립니다",
                    expected_improvement=30.0,
                    implementation_steps=[
                        "데이터베이스 인덱스 최적화",
                        "CDN 도입",
                        "API 응답 압축"
                    ]
                )
                suggestions.append(suggestion)
            
            # 에러율 최적화 제안
            if avg_error > 2:
                suggestion = OptimizationSuggestion(
                    plugin_id=plugin_id,
                    suggestion_type="error_optimization",
                    priority="high",
                    description=f"평균 에러율이 {avg_error:.1f}%로 높습니다",
                    expected_improvement=50.0,
                    implementation_steps=[
                        "예외 처리 강화",
                        "입력 검증 개선",
                        "로깅 시스템 개선"
                    ]
                )
                suggestions.append(suggestion)
            
            self.suggestions[plugin_id].extend(suggestions)
            logger.info(f"플러그인 {plugin_id} 최적화 제안 생성 완료: {len(suggestions)}개")
            return suggestions
            
        except Exception as e:
            logger.error(f"최적화 제안 생성 실패: {e}")
            return []
    
    async def get_analytics_summary(self, plugin_id: str) -> Dict[str, Any]:
        """분석 요약 정보"""
        try:
            metrics = self.metrics_history[plugin_id]
            if not metrics:
                return {"error": "데이터가 없습니다"}
            
            # 기본 통계
            recent_metrics = metrics[-168:]  # 최근 7일
            
            summary = {
                "plugin_id": plugin_id,
                "total_metrics": len(metrics),
                "analysis_period": "7일",
                "current_status": "active",
                "performance_metrics": {
                    "avg_cpu_usage": np.mean([m.cpu_usage for m in recent_metrics]),
                    "avg_memory_usage": np.mean([m.memory_usage for m in recent_metrics]),
                    "avg_response_time": np.mean([m.response_time for m in recent_metrics]),
                    "avg_error_rate": np.mean([m.error_rate for m in recent_metrics]),
                    "total_requests": sum([m.request_count for m in recent_metrics]),
                    "avg_uptime": np.mean([m.uptime for m in recent_metrics])
                },
                "trends": {
                    "cpu_trend": "stable",
                    "memory_trend": "stable",
                    "response_trend": "stable",
                    "error_trend": "stable"
                },
                "predictions_count": len(self.predictions[plugin_id]),
                "anomalies_count": len(self.anomalies[plugin_id]),
                "suggestions_count": len(self.suggestions[plugin_id]),
                "last_updated": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"분석 요약 생성 실패: {e}")
            return {"error": str(e)}
    
    async def export_analytics_data(self, plugin_id: str, format: str = "json") -> str:
        """분석 데이터 내보내기"""
        try:
            data = {
                "plugin_id": plugin_id,
                "exported_at": datetime.now().isoformat(),
                "metrics": [asdict(m) for m in self.metrics_history[plugin_id]],
                "predictions": [asdict(p) for p in self.predictions[plugin_id]],
                "anomalies": [asdict(a) for a in self.anomalies[plugin_id]],
                "suggestions": [asdict(s) for s in self.suggestions[plugin_id]]
            }
            
            if format == "json":
                filename = f"analytics_{plugin_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join(self.data_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                
                logger.info(f"분석 데이터 내보내기 완료: {filepath}")
                return filepath
            
            return "지원하지 않는 형식입니다"
            
        except Exception as e:
            logger.error(f"분석 데이터 내보내기 실패: {e}")
            return ""

# 전역 인스턴스
ai_analytics = PluginAIAnalytics() 