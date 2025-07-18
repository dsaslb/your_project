import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import psutil

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
    """플러그인 AI 분석 시스템"""

    def __init__(self, data_dir="data/ai_analytics"):
        self.data_dir = data_dir
        self.models_dir = os.path.join(data_dir, "models")
        self.scalers_dir = os.path.join(data_dir, "scalers")
        
        # 데이터 저장소
        self.metrics_history: Dict[str, List[PluginMetrics]] = {}
        self.models: Dict[str, Dict[str, Any]] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        self.predictions: Dict[str, List[PredictionResult]] = {}
        self.anomalies: Dict[str, List[AnomalyDetection]] = {}
        self.optimization_suggestions: Dict[str, List[OptimizationSuggestion]] = {}
        self.last_training: Dict[str, datetime] = {}
        
        # 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.scalers_dir, exist_ok=True)
        
        # 기존 모델 로드
        self._load_existing_models()

    def _load_existing_models(self):
        """기존 모델 로드"""
        try:
            for filename in os.listdir(self.models_dir):
                if filename.endswith('.joblib'):
                    plugin_id = filename.split('_')[0]
                    if plugin_id not in self.models:
                        self.models[plugin_id] = {}
                    
                    model_path = os.path.join(self.models_dir, filename)
                    model = joblib.load(model_path)
                    target_name = filename.split('_')[1].replace('.joblib', '')
                    self.models[plugin_id][target_name] = model
                    
            for filename in os.listdir(self.scalers_dir):
                if filename.endswith('.joblib'):
                    plugin_id = filename.split('_')[0]
                    scaler_path = os.path.join(self.scalers_dir, filename)
                    self.scalers[plugin_id] = joblib.load(scaler_path)
                    
        except Exception as e:
            logger.error(f"기존 모델 로드 실패: {e}")

    async def collect_metrics(self, plugin_id: str) -> PluginMetrics:
        """플러그인 메트릭 수집"""
        try:
            current_time = datetime.now()
            
            # 시스템 메트릭 수집
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 플러그인별 메트릭 (실제 구현에서는 플러그인별로 수집)
            response_time = np.random.uniform(0.1, 2.0)  # 예시 데이터
            error_rate = np.random.uniform(0.0, 0.05)    # 예시 데이터
            request_count = np.random.randint(100, 1000) # 예시 데이터
            active_users = np.random.randint(10, 100)    # 예시 데이터
            uptime = np.random.uniform(0.95, 0.999)      # 예시 데이터
            
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

            if plugin_id not in self.metrics_history:
                self.metrics_history[plugin_id] = []
            
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
            if plugin_id not in self.metrics_history:
                return np.array([]), np.array([])
            
            metrics = self.metrics_history[plugin_id]
            if len(metrics) < 24:  # 최소 24시간 데이터 필요
                return np.array([]), np.array([])

            # 시간 윈도우 데이터 준비
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in metrics if m.timestamp > cutoff_time]

            if len(recent_metrics) < 24:
                return np.array([]), np.array([])

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

            if plugin_id not in self.predictions:
                self.predictions[plugin_id] = []
            
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
            if plugin_id in self.metrics_history and self.metrics_history[plugin_id]:
                latest_metrics = self.metrics_history[plugin_id][-1]

                # CPU 사용률 이상
                if latest_metrics.cpu_usage > 90:
                    anomaly = AnomalyDetection(
                        plugin_id=plugin_id,
                        anomaly_type="high_cpu_usage",
                        severity="high",
                        detected_at=datetime.now(),
                        description=f"CPU 사용률이 {latest_metrics.cpu_usage:.1f}%로 높습니다",
                        recommendations=[
                            "플러그인 최적화 검토",
                            "서버 리소스 증설 고려",
                            "불필요한 프로세스 종료"
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
                        description=f"메모리 사용률이 {latest_metrics.memory_usage:.1f}%로 높습니다",
                        recommendations=[
                            "메모리 누수 검사",
                            "캐시 정리",
                            "메모리 최적화"
                        ]
                    )
                    anomalies.append(anomaly)

                # 응답 시간 이상
                if latest_metrics.response_time > 5.0:
                    anomaly = AnomalyDetection(
                        plugin_id=plugin_id,
                        anomaly_type="slow_response_time",
                        severity="medium",
                        detected_at=datetime.now(),
                        description=f"응답 시간이 {latest_metrics.response_time:.2f}초로 느립니다",
                        recommendations=[
                            "데이터베이스 쿼리 최적화",
                            "캐싱 전략 개선",
                            "서버 성능 점검"
                        ]
                    )
                    anomalies.append(anomaly)

                # 오류율 이상
                if latest_metrics.error_rate > 0.05:
                    anomaly = AnomalyDetection(
                        plugin_id=plugin_id,
                        anomaly_type="high_error_rate",
                        severity="high",
                        detected_at=datetime.now(),
                        description=f"오류율이 {latest_metrics.error_rate:.3f}로 높습니다",
                        recommendations=[
                            "오류 로그 분석",
                            "코드 품질 검토",
                            "예외 처리 개선"
                        ]
                    )
                    anomalies.append(anomaly)

            if plugin_id not in self.anomalies:
                self.anomalies[plugin_id] = []
            
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
                    expected_improvement=15.0,
                    implementation_steps=[
                        "비동기 처리 도입",
                        "캐싱 전략 개선",
                        "불필요한 연산 제거"
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
                    expected_improvement=20.0,
                    implementation_steps=[
                        "메모리 누수 검사",
                        "객체 풀링 도입",
                        "가비지 컬렉션 최적화"
                    ]
                )
                suggestions.append(suggestion)

            # 응답 시간 최적화 제안
            if avg_response > 2.0:
                suggestion = OptimizationSuggestion(
                    plugin_id=plugin_id,
                    suggestion_type="response_time_optimization",
                    priority="medium",
                    description=f"평균 응답 시간이 {avg_response:.2f}초로 느립니다",
                    expected_improvement=30.0,
                    implementation_steps=[
                        "데이터베이스 인덱스 최적화",
                        "API 응답 캐싱",
                        "비동기 처리 개선"
                    ]
                )
                suggestions.append(suggestion)

            if plugin_id not in self.optimization_suggestions:
                self.optimization_suggestions[plugin_id] = []
            
            self.optimization_suggestions[plugin_id].extend(suggestions)
            logger.info(f"플러그인 {plugin_id} 최적화 제안 생성 완료: {len(suggestions)}개")
            return suggestions

        except Exception as e:
            logger.error(f"최적화 제안 생성 실패: {e}")
            return []

    async def get_analytics_summary(self, plugin_id: str) -> Dict[str, Any]:
        """분석 요약 조회"""
        try:
            summary = {
                "plugin_id": plugin_id,
                "last_updated": datetime.now().isoformat(),
                "metrics_count": 0,
                "predictions_count": 0,
                "anomalies_count": 0,
                "suggestions_count": 0,
                "performance_trend": "stable",
                "health_score": 85.0
            }

            if plugin_id in self.metrics_history:
                summary["metrics_count"] = len(self.metrics_history[plugin_id])
                
                if self.metrics_history[plugin_id]:
                    latest_metrics = self.metrics_history[plugin_id][-1]
                    summary["current_cpu"] = latest_metrics.cpu_usage
                    summary["current_memory"] = latest_metrics.memory_usage
                    summary["current_response_time"] = latest_metrics.response_time
                    summary["current_error_rate"] = latest_metrics.error_rate

            if plugin_id in self.predictions:
                summary["predictions_count"] = len(self.predictions[plugin_id])

            if plugin_id in self.anomalies:
                summary["anomalies_count"] = len(self.anomalies[plugin_id])

            if plugin_id in self.optimization_suggestions:
                summary["suggestions_count"] = len(self.optimization_suggestions[plugin_id])

            return summary

        except Exception as e:
            logger.error(f"분석 요약 조회 실패: {e}")
            return {}

    async def export_analytics_data(self, plugin_id: str, format: str = "json") -> str:
        """분석 데이터 내보내기"""
        try:
            export_data = {
                "plugin_id": plugin_id,
                "exported_at": datetime.now().isoformat(),
                "metrics": [],
                "predictions": [],
                "anomalies": [],
                "suggestions": []
            }

            if plugin_id in self.metrics_history:
                export_data["metrics"] = [
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
                    for m in self.metrics_history[plugin_id]
                ]

            if plugin_id in self.predictions:
                export_data["predictions"] = [
                    {
                        "prediction_type": p.prediction_type,
                        "predicted_value": p.predicted_value,
                        "confidence": p.confidence,
                        "timestamp": p.timestamp.isoformat(),
                        "factors": p.factors
                    }
                    for p in self.predictions[plugin_id]
                ]

            if plugin_id in self.anomalies:
                export_data["anomalies"] = [
                    {
                        "anomaly_type": a.anomaly_type,
                        "severity": a.severity,
                        "detected_at": a.detected_at.isoformat(),
                        "description": a.description,
                        "recommendations": a.recommendations
                    }
                    for a in self.anomalies[plugin_id]
                ]

            if plugin_id in self.optimization_suggestions:
                export_data["suggestions"] = [
                    {
                        "suggestion_type": s.suggestion_type,
                        "priority": s.priority,
                        "description": s.description,
                        "expected_improvement": s.expected_improvement,
                        "implementation_steps": s.implementation_steps
                    }
                    for s in self.optimization_suggestions[plugin_id]
                ]

            if format.lower() == "json":
                export_path = os.path.join(self.data_dir, f"{plugin_id}_analytics_export.json")
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                return export_path

            return ""

        except Exception as e:
            logger.error(f"분석 데이터 내보내기 실패: {e}")
            return ""
