"""
AI 기반 성능 예측 및 이상 탐지 엔진
- 시계열 예측 (미래 부하/리소스)
- 이상 탐지 (성능 저하, 장애 징후)
- 자동화 신호 생성
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class AIPerformanceOptimizer:
    """AI 기반 성능 예측 및 이상 탐지 엔진"""
    def __init__(self):
        self.anomaly_model = None
        self.forecast_model = None
        self.scaler = None
        self.last_train_time = None
        self.train_interval = timedelta(hours=1)

    def fit_anomaly_model(self, metrics: List[Dict[str, Any]]):
        """이상 탐지 모델 학습"""
        if not metrics:
            return
        df = pd.DataFrame(metrics)
        features = ['cpu_usage', 'memory_usage', 'response_time_avg', 'error_count']
        X = df[features].fillna(0)
        self.scaler = StandardScaler().fit(X)
        X_scaled = self.scaler.transform(X)
        self.anomaly_model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.anomaly_model.fit(X_scaled)
        self.last_train_time = datetime.now()
        logger.info("이상 탐지 모델 학습 완료")

    def detect_anomalies(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """이상 탐지 수행"""
        if not self.anomaly_model or not self.scaler:
            self.fit_anomaly_model(metrics)
        if not metrics:
            return []
        df = pd.DataFrame(metrics)
        features = ['cpu_usage', 'memory_usage', 'response_time_avg', 'error_count']
        X = df[features].fillna(0)
        X_scaled = self.scaler.transform(X)
        preds = self.anomaly_model.predict(X_scaled)
        df['anomaly'] = preds == -1
        return df[df['anomaly']].to_dict(orient='records')

    def fit_forecast_model(self, metrics: List[Dict[str, Any]], target: str = 'cpu_usage'):
        """시계열 예측 모델 학습 (단순 선형회귀)"""
        if not metrics:
            return
        df = pd.DataFrame(metrics)
        df = df.sort_values('timestamp')
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[target].fillna(0).values
        self.forecast_model = LinearRegression().fit(X, y)
        logger.info(f"{target} 예측 모델 학습 완료")

    def predict_future(self, metrics: List[Dict[str, Any]], target: str = 'cpu_usage', steps: int = 10) -> List[float]:
        """미래 값 예측 (단순 선형회귀 기반)"""
        if not self.forecast_model:
            self.fit_forecast_model(metrics, target)
        if not metrics or not self.forecast_model:
            return []
        n = len(metrics)
        X_future = np.arange(n, n + steps).reshape(-1, 1)
        preds = self.forecast_model.predict(X_future)
        return preds.tolist()

    def auto_optimize_signal(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """자동화 신호 생성 (예측/이상 기반)"""
        anomalies = self.detect_anomalies(metrics)
        future_cpu = self.predict_future(metrics, 'cpu_usage', steps=5)
        future_mem = self.predict_future(metrics, 'memory_usage', steps=5)
        signal = {
            'anomaly_detected': len(anomalies) > 0,
            'future_cpu': future_cpu,
            'future_memory': future_mem,
            'scale_up': max(future_cpu + future_mem) > 80,
            'scale_down': max(future_cpu + future_mem) < 40,
            'anomaly_details': anomalies
        }
        logger.info(f"자동화 신호: {signal}")
        return signal

# 전역 인스턴스
aio = None

def get_ai_optimizer() -> AIPerformanceOptimizer:
    global aio
    if aio is None:
        aio = AIPerformanceOptimizer()
    return aio 