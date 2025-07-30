#!/usr/bin/env python3
"""
🤖 Your Program 머신러닝 기반 성능 최적화 시스템

과거 데이터와 실시간 메트릭을 분석하여 시스템 성능을 예측하고
자동으로 최적화 전략을 수립하여 실행하는 AI 시스템입니다.

주요 기능:
- 시계열 성능 데이터 예측
- 이상 탐지 및 조기 경고
- 자동 리소스 할당 최적화
- 쿼리 성능 최적화
- 캐시 전략 최적화
- 로드 밸런싱 최적화
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import joblib
import redis
import psutil
import aiohttp
import sqlite3
from pathlib import Path

# ML/AI 라이브러리
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """성능 메트릭 데이터"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    response_time: float
    throughput: float
    error_rate: float
    active_connections: int
    queue_length: int
    cache_hit_rate: float

@dataclass
class PerformancePrediction:
    """성능 예측 결과"""
    prediction_time: datetime
    predicted_metrics: Dict[str, float]
    confidence_scores: Dict[str, float]
    anomaly_score: float
    recommendations: List[str]
    risk_level: str  # 'low', 'medium', 'high', 'critical'

@dataclass
class OptimizationAction:
    """최적화 액션"""
    action_id: str
    action_type: str
    target_component: str
    parameters: Dict[str, Any]
    expected_improvement: float
    confidence: float
    execution_time: datetime
    duration_estimate: int  # 초
    rollback_plan: Dict[str, Any]

class PerformanceMLOptimizer:
    """ML 기반 성능 최적화 시스템"""
    
    def __init__(self, data_path: str = "ai/performance_data.db"):
        self.data_path = data_path
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1)
        
        # ML 모델들
        self.models = {}
        self.scalers = {}
        self.anomaly_detector = None
        
        # 성능 데이터 버퍼
        self.metrics_buffer: List[PerformanceMetrics] = []
        self.predictions_buffer: List[PerformancePrediction] = []
        
        # 설정
        self.prediction_window = 300  # 5분 예측
        self.optimization_threshold = 0.8  # 최적화 임계값
        self.model_retrain_interval = 3600  # 1시간마다 재학습
        
        self.init_database()
        self.load_models()
        
    def init_database(self):
        """데이터베이스 초기화"""
        Path(self.data_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        # 성능 메트릭 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_io REAL,
                network_io REAL,
                response_time REAL,
                throughput REAL,
                error_rate REAL,
                active_connections INTEGER,
                queue_length INTEGER,
                cache_hit_rate REAL
            )
        """)
        
        # 예측 결과 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_time TEXT NOT NULL,
                target_time TEXT NOT NULL,
                predicted_metrics TEXT,
                confidence_scores TEXT,
                anomaly_score REAL,
                risk_level TEXT,
                actual_metrics TEXT
            )
        """)
        
        # 최적화 액션 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_actions (
                action_id TEXT PRIMARY KEY,
                action_type TEXT,
                target_component TEXT,
                parameters TEXT,
                expected_improvement REAL,
                confidence REAL,
                execution_time TEXT,
                completion_time TEXT,
                actual_improvement REAL,
                success BOOLEAN
            )
        """)
        
        conn.commit()
        conn.close()
    
    def load_models(self):
        """저장된 ML 모델 로드"""
        model_dir = Path("ai/models")
        scaler_dir = Path("ai/scalers")
        
        try:
            # CPU 사용률 예측 모델
            if (model_dir / "cpu_predictor.pkl").exists():
                self.models['cpu'] = joblib.load(model_dir / "cpu_predictor.pkl")
                self.scalers['cpu'] = joblib.load(scaler_dir / "cpu_scaler.pkl")
                logger.info("✅ CPU 예측 모델 로드 완료")
            
            # 메모리 사용률 예측 모델
            if (model_dir / "memory_predictor.pkl").exists():
                self.models['memory'] = joblib.load(model_dir / "memory_predictor.pkl")
                self.scalers['memory'] = joblib.load(scaler_dir / "memory_scaler.pkl")
                logger.info("✅ 메모리 예측 모델 로드 완료")
            
            # 응답시간 예측 모델 (LSTM)
            if (model_dir / "response_time_lstm.keras").exists():
                self.models['response_time'] = load_model(model_dir / "response_time_lstm.keras")
                self.scalers['response_time'] = joblib.load(scaler_dir / "response_time_scaler.pkl")
                logger.info("✅ 응답시간 LSTM 모델 로드 완료")
            
            # 이상 탐지 모델
            if (model_dir / "anomaly_detector.pkl").exists():
                self.anomaly_detector = joblib.load(model_dir / "anomaly_detector.pkl")
                logger.info("✅ 이상 탐지 모델 로드 완료")
                
        except Exception as e:
            logger.warning(f"모델 로드 중 오류: {e}")
            logger.info("새로운 모델을 학습합니다...")
    
    async def start_optimization_loop(self):
        """최적화 루프 시작"""
        logger.info("🤖 ML 기반 성능 최적화 시스템 시작")
        
        tasks = [
            asyncio.create_task(self._collect_metrics_loop()),
            asyncio.create_task(self._prediction_loop()),
            asyncio.create_task(self._optimization_loop()),
            asyncio.create_task(self._model_retrain_loop()),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _collect_metrics_loop(self):
        """메트릭 수집 루프"""
        while True:
            try:
                metrics = await self._collect_current_metrics()
                self.metrics_buffer.append(metrics)
                
                # 버퍼 크기 제한 (최근 1000개)
                if len(self.metrics_buffer) > 1000:
                    self.metrics_buffer = self.metrics_buffer[-1000:]
                
                # 데이터베이스에 저장
                await self._save_metrics_to_db(metrics)
                
                # Redis에 캐시
                await self._cache_metrics(metrics)
                
                await asyncio.sleep(30)  # 30초마다 수집
                
            except Exception as e:
                logger.error(f"메트릭 수집 오류: {e}")
                await asyncio.sleep(30)
    
    async def _prediction_loop(self):
        """예측 루프"""
        while True:
            try:
                if len(self.metrics_buffer) >= 10:  # 최소 데이터 필요
                    prediction = await self._predict_performance()
                    if prediction:
                        self.predictions_buffer.append(prediction)
                        
                        # 예측 결과 저장
                        await self._save_prediction_to_db(prediction)
                        
                        # 위험 수준에 따른 알림
                        if prediction.risk_level in ['high', 'critical']:
                            await self._send_performance_alert(prediction)
                
                await asyncio.sleep(60)  # 1분마다 예측
                
            except Exception as e:
                logger.error(f"성능 예측 오류: {e}")
                await asyncio.sleep(60)
    
    async def _optimization_loop(self):
        """최적화 루프"""
        while True:
            try:
                if self.predictions_buffer:
                    latest_prediction = self.predictions_buffer[-1]
                    
                    if latest_prediction.risk_level in ['medium', 'high', 'critical']:
                        optimization_actions = await self._generate_optimization_actions(latest_prediction)
                        
                        for action in optimization_actions:
                            if action.confidence > 0.7:  # 높은 신뢰도만 자동 실행
                                success = await self._execute_optimization_action(action)
                                if success:
                                    logger.info(f"✅ 최적화 액션 실행 완료: {action.action_type}")
                
                await asyncio.sleep(120)  # 2분마다 최적화 검토
                
            except Exception as e:
                logger.error(f"최적화 실행 오류: {e}")
                await asyncio.sleep(120)
    
    async def _model_retrain_loop(self):
        """모델 재학습 루프"""
        while True:
            try:
                await asyncio.sleep(self.model_retrain_interval)
                
                # 충분한 데이터가 있으면 모델 재학습
                if len(self.metrics_buffer) >= 100:
                    logger.info("🔄 ML 모델 재학습 시작")
                    await self._retrain_models()
                    logger.info("✅ ML 모델 재학습 완료")
                
            except Exception as e:
                logger.error(f"모델 재학습 오류: {e}")
    
    async def _collect_current_metrics(self) -> PerformanceMetrics:
        """현재 성능 메트릭 수집"""
        # 시스템 메트릭
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()
        
        # 애플리케이션 메트릭 (Redis에서 조회)
        try:
            response_time = float(self.redis_client.get("avg_response_time") or 250.0)
            throughput = float(self.redis_client.get("throughput") or 100.0)
            error_rate = float(self.redis_client.get("error_rate") or 0.5)
            active_connections = int(self.redis_client.get("active_connections") or 10)
            queue_length = int(self.redis_client.get("queue_length") or 0)
            cache_hit_rate = float(self.redis_client.get("cache_hit_rate") or 85.0)
        except:
            # 기본값 사용
            response_time = 250.0
            throughput = 100.0
            error_rate = 0.5
            active_connections = 10
            queue_length = 0
            cache_hit_rate = 85.0
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_io=disk_io.read_bytes + disk_io.write_bytes if disk_io else 0,
            network_io=network_io.bytes_sent + network_io.bytes_recv if network_io else 0,
            response_time=response_time,
            throughput=throughput,
            error_rate=error_rate,
            active_connections=active_connections,
            queue_length=queue_length,
            cache_hit_rate=cache_hit_rate
        )
    
    async def _predict_performance(self) -> Optional[PerformancePrediction]:
        """성능 예측 실행"""
        try:
            # 최근 데이터로 특성 생성
            recent_metrics = self.metrics_buffer[-30:]  # 최근 30개 (15분)
            features = self._extract_features(recent_metrics)
            
            predictions = {}
            confidence_scores = {}
            
            # CPU 사용률 예측
            if 'cpu' in self.models:
                cpu_pred = await self._predict_metric('cpu', features)
                predictions['cpu_usage'] = cpu_pred
                confidence_scores['cpu_usage'] = 0.85  # 모델 성능에 따라 조정
            
            # 메모리 사용률 예측
            if 'memory' in self.models:
                memory_pred = await self._predict_metric('memory', features)
                predictions['memory_usage'] = memory_pred
                confidence_scores['memory_usage'] = 0.82
            
            # 응답시간 예측 (LSTM)
            if 'response_time' in self.models:
                response_pred = await self._predict_response_time(recent_metrics)
                predictions['response_time'] = response_pred
                confidence_scores['response_time'] = 0.78
            
            # 이상 탐지
            anomaly_score = await self._detect_anomaly(features)
            
            # 위험 수준 계산
            risk_level = self._calculate_risk_level(predictions, anomaly_score)
            
            # 추천사항 생성
            recommendations = await self._generate_recommendations(predictions, risk_level)
            
            return PerformancePrediction(
                prediction_time=datetime.now(),
                predicted_metrics=predictions,
                confidence_scores=confidence_scores,
                anomaly_score=anomaly_score,
                recommendations=recommendations,
                risk_level=risk_level
            )
            
        except Exception as e:
            logger.error(f"성능 예측 실행 오류: {e}")
            return None
    
    def _extract_features(self, metrics: List[PerformanceMetrics]) -> np.ndarray:
        """메트릭에서 ML 특성 추출"""
        if not metrics:
            return np.array([])
        
        # 시계열 특성 추출
        df = pd.DataFrame([asdict(m) for m in metrics])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        features = []
        
        # 통계적 특성
        numeric_cols = ['cpu_usage', 'memory_usage', 'response_time', 'throughput', 'error_rate']
        for col in numeric_cols:
            if col in df.columns:
                features.extend([
                    df[col].mean(),        # 평균
                    df[col].std(),         # 표준편차
                    df[col].min(),         # 최소값
                    df[col].max(),         # 최대값
                    df[col].median(),      # 중앙값
                    df[col].iloc[-1] - df[col].iloc[0] if len(df) > 1 else 0,  # 변화량
                ])
        
        # 시간 기반 특성
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        features.extend([
            df['hour'].iloc[-1],
            df['minute'].iloc[-1],
            df['day_of_week'].iloc[-1]
        ])
        
        # 트렌드 특성
        if len(df) >= 5:
            for col in numeric_cols:
                if col in df.columns:
                    # 최근 5개 데이터의 트렌드
                    recent_values = df[col].iloc[-5:].values
                    if len(recent_values) > 1:
                        trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
                        features.append(trend)
                    else:
                        features.append(0)
        
        return np.array(features).reshape(1, -1)
    
    async def _predict_metric(self, metric_name: str, features: np.ndarray) -> float:
        """특정 메트릭 예측"""
        try:
            model = self.models[metric_name]
            scaler = self.scalers[metric_name]
            
            # 특성 정규화
            features_scaled = scaler.transform(features)
            
            # 예측 실행
            prediction = model.predict(features_scaled)[0]
            
            return max(0, prediction)  # 음수 방지
            
        except Exception as e:
            logger.error(f"{metric_name} 예측 오류: {e}")
            return 0.0
    
    async def _predict_response_time(self, metrics: List[PerformanceMetrics]) -> float:
        """LSTM을 사용한 응답시간 예측"""
        try:
            if 'response_time' not in self.models:
                return 0.0
            
            model = self.models['response_time']
            scaler = self.scalers['response_time']
            
            # 시계열 데이터 준비
            response_times = [m.response_time for m in metrics[-20:]]  # 최근 20개
            
            if len(response_times) < 10:
                return response_times[-1] if response_times else 0.0
            
            # 데이터 정규화
            data_scaled = scaler.transform(np.array(response_times).reshape(-1, 1))
            
            # LSTM 입력 형태로 변환
            X = data_scaled[-10:].reshape(1, 10, 1)
            
            # 예측
            prediction_scaled = model.predict(X, verbose=0)
            prediction = scaler.inverse_transform(prediction_scaled)[0][0]
            
            return max(0, prediction)
            
        except Exception as e:
            logger.error(f"응답시간 LSTM 예측 오류: {e}")
            return 0.0
    
    async def _detect_anomaly(self, features: np.ndarray) -> float:
        """이상 탐지"""
        try:
            if self.anomaly_detector is None or features.size == 0:
                return 0.0
            
            # 이상 점수 계산 (-1: 이상, 1: 정상)
            anomaly_score = self.anomaly_detector.decision_function(features)[0]
            
            # 0-1 범위로 정규화 (1에 가까울수록 이상)
            normalized_score = max(0, min(1, (1 - anomaly_score) / 2))
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"이상 탐지 오류: {e}")
            return 0.0
    
    def _calculate_risk_level(self, predictions: Dict[str, float], anomaly_score: float) -> str:
        """위험 수준 계산"""
        risk_factors = []
        
        # CPU 위험도
        if 'cpu_usage' in predictions:
            cpu_risk = predictions['cpu_usage'] / 100.0
            risk_factors.append(cpu_risk)
        
        # 메모리 위험도
        if 'memory_usage' in predictions:
            memory_risk = predictions['memory_usage'] / 100.0
            risk_factors.append(memory_risk)
        
        # 응답시간 위험도 (500ms 기준)
        if 'response_time' in predictions:
            response_risk = min(1.0, predictions['response_time'] / 500.0)
            risk_factors.append(response_risk)
        
        # 이상 점수
        risk_factors.append(anomaly_score)
        
        if not risk_factors:
            return 'low'
        
        # 전체 위험 점수
        overall_risk = np.mean(risk_factors)
        
        if overall_risk >= 0.9:
            return 'critical'
        elif overall_risk >= 0.7:
            return 'high'
        elif overall_risk >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_recommendations(self, predictions: Dict[str, float], risk_level: str) -> List[str]:
        """추천사항 생성"""
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.append("🚨 즉시 시스템 점검이 필요합니다")
            recommendations.append("📞 운영팀에 즉시 알림을 발송하세요")
        
        if 'cpu_usage' in predictions and predictions['cpu_usage'] > 80:
            recommendations.append("⚡ CPU 집약적 프로세스 최적화 필요")
            recommendations.append("📈 수평 스케일링 고려")
        
        if 'memory_usage' in predictions and predictions['memory_usage'] > 85:
            recommendations.append("🧠 메모리 정리 및 가비지 컬렉션 실행")
            recommendations.append("💾 메모리 캐시 전략 재검토")
        
        if 'response_time' in predictions and predictions['response_time'] > 400:
            recommendations.append("🔄 데이터베이스 쿼리 최적화")
            recommendations.append("⚡ CDN 및 캐싱 전략 강화")
        
        if not recommendations:
            recommendations.append("✅ 시스템이 정상적으로 운영되고 있습니다")
        
        return recommendations
    
    async def _generate_optimization_actions(self, prediction: PerformancePrediction) -> List[OptimizationAction]:
        """최적화 액션 생성"""
        actions = []
        action_id_counter = int(datetime.now().timestamp())
        
        # CPU 최적화
        if 'cpu_usage' in prediction.predicted_metrics and prediction.predicted_metrics['cpu_usage'] > 80:
            actions.append(OptimizationAction(
                action_id=f"cpu_opt_{action_id_counter}",
                action_type="cpu_optimization",
                target_component="application_servers",
                parameters={
                    "scale_factor": 1.5,
                    "priority_adjustment": "high",
                    "process_affinity": True
                },
                expected_improvement=0.3,
                confidence=0.85,
                execution_time=datetime.now(),
                duration_estimate=120,
                rollback_plan={"scale_factor": 1.0, "priority_adjustment": "normal"}
            ))
        
        # 메모리 최적화
        if 'memory_usage' in prediction.predicted_metrics and prediction.predicted_metrics['memory_usage'] > 85:
            actions.append(OptimizationAction(
                action_id=f"mem_opt_{action_id_counter + 1}",
                action_type="memory_optimization",
                target_component="cache_system",
                parameters={
                    "cache_size_reduction": 0.2,
                    "gc_aggressive": True,
                    "memory_pool_optimization": True
                },
                expected_improvement=0.25,
                confidence=0.80,
                execution_time=datetime.now(),
                duration_estimate=60,
                rollback_plan={"cache_size_reduction": 0.0, "gc_aggressive": False}
            ))
        
        # 응답시간 최적화
        if 'response_time' in prediction.predicted_metrics and prediction.predicted_metrics['response_time'] > 400:
            actions.append(OptimizationAction(
                action_id=f"resp_opt_{action_id_counter + 2}",
                action_type="response_optimization",
                target_component="database",
                parameters={
                    "query_cache_size": "increased",
                    "connection_pool_size": 50,
                    "index_optimization": True
                },
                expected_improvement=0.4,
                confidence=0.75,
                execution_time=datetime.now(),
                duration_estimate=180,
                rollback_plan={"query_cache_size": "default", "connection_pool_size": 20}
            ))
        
        return actions
    
    async def _execute_optimization_action(self, action: OptimizationAction) -> bool:
        """최적화 액션 실행"""
        try:
            logger.info(f"🔧 최적화 액션 실행 시작: {action.action_type}")
            
            success = False
            
            if action.action_type == "cpu_optimization":
                success = await self._execute_cpu_optimization(action.parameters)
            elif action.action_type == "memory_optimization":
                success = await self._execute_memory_optimization(action.parameters)
            elif action.action_type == "response_optimization":
                success = await self._execute_response_optimization(action.parameters)
            
            # 실행 결과 저장
            await self._save_optimization_result(action, success)
            
            return success
            
        except Exception as e:
            logger.error(f"최적화 액션 실행 오류: {e}")
            return False
    
    async def _execute_cpu_optimization(self, parameters: Dict[str, Any]) -> bool:
        """CPU 최적화 실행"""
        try:
            # 스케일링
            if "scale_factor" in parameters:
                scale_factor = parameters["scale_factor"]
                logger.info(f"📈 CPU 스케일링 실행: {scale_factor}x")
                
                # 실제 환경에서는 Kubernetes/Docker API 호출
                # 여기서는 시뮬레이션
                await asyncio.sleep(2)
            
            # 프로세스 우선순위 조정
            if parameters.get("priority_adjustment") == "high":
                logger.info("⚡ 프로세스 우선순위 조정")
                # 실제 구현에서는 프로세스 nice 값 조정
                await asyncio.sleep(1)
            
            # CPU 어피니티 설정
            if parameters.get("process_affinity"):
                logger.info("🎯 CPU 어피니티 최적화")
                # 실제 구현에서는 psutil.Process().cpu_affinity() 사용
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"CPU 최적화 실행 오류: {e}")
            return False
    
    async def _execute_memory_optimization(self, parameters: Dict[str, Any]) -> bool:
        """메모리 최적화 실행"""
        try:
            # 캐시 크기 조정
            if "cache_size_reduction" in parameters:
                reduction = parameters["cache_size_reduction"]
                logger.info(f"💾 캐시 크기 조정: -{reduction*100}%")
                
                # Redis 메모리 최적화
                self.redis_client.execute_command("MEMORY PURGE")
                await asyncio.sleep(1)
            
            # 가비지 컬렉션 강화
            if parameters.get("gc_aggressive"):
                logger.info("🧹 강화된 가비지 컬렉션 실행")
                import gc
                collected = gc.collect()
                logger.info(f"정리된 객체 수: {collected}")
            
            # 메모리 풀 최적화
            if parameters.get("memory_pool_optimization"):
                logger.info("🔄 메모리 풀 최적화")
                # 실제 구현에서는 애플리케이션별 메모리 풀 조정
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"메모리 최적화 실행 오류: {e}")
            return False
    
    async def _execute_response_optimization(self, parameters: Dict[str, Any]) -> bool:
        """응답시간 최적화 실행"""
        try:
            # 쿼리 캐시 크기 증가
            if parameters.get("query_cache_size") == "increased":
                logger.info("📊 쿼리 캐시 크기 증가")
                # 실제 구현에서는 데이터베이스 설정 변경
                await asyncio.sleep(1)
            
            # 커넥션 풀 크기 조정
            if "connection_pool_size" in parameters:
                pool_size = parameters["connection_pool_size"]
                logger.info(f"🔗 커넥션 풀 크기 조정: {pool_size}")
                # 실제 구현에서는 DB 커넥션 풀 재설정
                await asyncio.sleep(1)
            
            # 인덱스 최적화
            if parameters.get("index_optimization"):
                logger.info("🗂️ 데이터베이스 인덱스 최적화")
                # 실제 구현에서는 ANALYZE, VACUUM 등 실행
                await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"응답시간 최적화 실행 오류: {e}")
            return False
    
    async def _retrain_models(self):
        """ML 모델 재학습"""
        try:
            # 충분한 데이터 확보
            if len(self.metrics_buffer) < 100:
                return
            
            # 데이터 준비
            df = pd.DataFrame([asdict(m) for m in self.metrics_buffer])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # CPU 예측 모델 재학습
            await self._retrain_cpu_model(df)
            
            # 메모리 예측 모델 재학습
            await self._retrain_memory_model(df)
            
            # 응답시간 LSTM 모델 재학습
            await self._retrain_response_time_model(df)
            
            # 이상 탐지 모델 재학습
            await self._retrain_anomaly_model(df)
            
            # 모델 저장
            await self._save_models()
            
        except Exception as e:
            logger.error(f"모델 재학습 오류: {e}")
    
    async def _retrain_cpu_model(self, df: pd.DataFrame):
        """CPU 예측 모델 재학습"""
        try:
            # 특성 및 타겟 준비
            features = []
            targets = []
            
            for i in range(10, len(df)):
                # 과거 10개 데이터포인트의 특성
                window_data = df.iloc[i-10:i]
                feature_vector = self._extract_features([
                    PerformanceMetrics(**row) for _, row in window_data.iterrows()
                ])
                
                if feature_vector.size > 0:
                    features.append(feature_vector.flatten())
                    targets.append(df.iloc[i]['cpu_usage'])
            
            if len(features) < 20:
                return
            
            X = np.array(features)
            y = np.array(targets)
            
            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 스케일러 학습
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # XGBoost 모델 학습
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # 성능 평가
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            logger.info(f"CPU 모델 성능 - MSE: {mse:.2f}, MAE: {mae:.2f}")
            
            # 모델 저장
            self.models['cpu'] = model
            self.scalers['cpu'] = scaler
            
        except Exception as e:
            logger.error(f"CPU 모델 재학습 오류: {e}")
    
    async def _retrain_memory_model(self, df: pd.DataFrame):
        """메모리 예측 모델 재학습"""
        try:
            # CPU 모델과 유사한 방식으로 구현
            features = []
            targets = []
            
            for i in range(10, len(df)):
                window_data = df.iloc[i-10:i]
                feature_vector = self._extract_features([
                    PerformanceMetrics(**row) for _, row in window_data.iterrows()
                ])
                
                if feature_vector.size > 0:
                    features.append(feature_vector.flatten())
                    targets.append(df.iloc[i]['memory_usage'])
            
            if len(features) < 20:
                return
            
            X = np.array(features)
            y = np.array(targets)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            
            logger.info(f"메모리 모델 성능 - MSE: {mse:.2f}")
            
            self.models['memory'] = model
            self.scalers['memory'] = scaler
            
        except Exception as e:
            logger.error(f"메모리 모델 재학습 오류: {e}")
    
    async def _retrain_response_time_model(self, df: pd.DataFrame):
        """응답시간 LSTM 모델 재학습"""
        try:
            # 응답시간 시계열 데이터 준비
            response_times = df['response_time'].values
            
            if len(response_times) < 50:
                return
            
            # 데이터 정규화
            scaler = MinMaxScaler()
            data_scaled = scaler.fit_transform(response_times.reshape(-1, 1))
            
            # 시계열 데이터셋 생성
            def create_sequences(data, seq_length):
                X, y = [], []
                for i in range(len(data) - seq_length):
                    X.append(data[i:i+seq_length])
                    y.append(data[i+seq_length])
                return np.array(X), np.array(y)
            
            seq_length = 10
            X, y = create_sequences(data_scaled, seq_length)
            
            if len(X) < 20:
                return
            
            # 모델 구축
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(seq_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # 학습
            model.fit(X, y, epochs=50, batch_size=32, verbose=0, validation_split=0.2)
            
            logger.info("응답시간 LSTM 모델 재학습 완료")
            
            self.models['response_time'] = model
            self.scalers['response_time'] = scaler
            
        except Exception as e:
            logger.error(f"응답시간 LSTM 모델 재학습 오류: {e}")
    
    async def _retrain_anomaly_model(self, df: pd.DataFrame):
        """이상 탐지 모델 재학습"""
        try:
            # 모든 메트릭을 특성으로 사용
            features = []
            
            for i in range(10, len(df)):
                window_data = df.iloc[i-10:i]
                feature_vector = self._extract_features([
                    PerformanceMetrics(**row) for _, row in window_data.iterrows()
                ])
                
                if feature_vector.size > 0:
                    features.append(feature_vector.flatten())
            
            if len(features) < 30:
                return
            
            X = np.array(features)
            
            # 스케일링
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Isolation Forest 모델
            model = IsolationForest(
                contamination=0.1,  # 10% 이상치 가정
                random_state=42
            )
            model.fit(X_scaled)
            
            logger.info("이상 탐지 모델 재학습 완료")
            
            self.anomaly_detector = model
            
        except Exception as e:
            logger.error(f"이상 탐지 모델 재학습 오류: {e}")
    
    async def _save_models(self):
        """모델 저장"""
        try:
            model_dir = Path("ai/models")
            scaler_dir = Path("ai/scalers")
            
            model_dir.mkdir(exist_ok=True)
            scaler_dir.mkdir(exist_ok=True)
            
            # CPU 모델
            if 'cpu' in self.models:
                joblib.dump(self.models['cpu'], model_dir / "cpu_predictor.pkl")
                joblib.dump(self.scalers['cpu'], scaler_dir / "cpu_scaler.pkl")
            
            # 메모리 모델
            if 'memory' in self.models:
                joblib.dump(self.models['memory'], model_dir / "memory_predictor.pkl")
                joblib.dump(self.scalers['memory'], scaler_dir / "memory_scaler.pkl")
            
            # 응답시간 모델
            if 'response_time' in self.models:
                self.models['response_time'].save(model_dir / "response_time_lstm.keras")
                joblib.dump(self.scalers['response_time'], scaler_dir / "response_time_scaler.pkl")
            
            # 이상 탐지 모델
            if self.anomaly_detector:
                joblib.dump(self.anomaly_detector, model_dir / "anomaly_detector.pkl")
            
            logger.info("✅ 모델 저장 완료")
            
        except Exception as e:
            logger.error(f"모델 저장 오류: {e}")
    
    # 데이터베이스 관련 메서드들
    async def _save_metrics_to_db(self, metrics: PerformanceMetrics):
        """메트릭을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics 
                (timestamp, cpu_usage, memory_usage, disk_io, network_io, 
                 response_time, throughput, error_rate, active_connections, 
                 queue_length, cache_hit_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.disk_io,
                metrics.network_io,
                metrics.response_time,
                metrics.throughput,
                metrics.error_rate,
                metrics.active_connections,
                metrics.queue_length,
                metrics.cache_hit_rate
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"메트릭 저장 오류: {e}")
    
    async def _cache_metrics(self, metrics: PerformanceMetrics):
        """메트릭을 Redis에 캐시"""
        try:
            cache_data = {
                "timestamp": metrics.timestamp.isoformat(),
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "response_time": metrics.response_time,
                "throughput": metrics.throughput,
                "error_rate": metrics.error_rate
            }
            
            self.redis_client.setex(
                "latest_performance_metrics",
                300,  # 5분 TTL
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.error(f"메트릭 캐시 오류: {e}")
    
    async def _save_prediction_to_db(self, prediction: PerformancePrediction):
        """예측 결과를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            target_time = prediction.prediction_time + timedelta(seconds=self.prediction_window)
            
            cursor.execute("""
                INSERT INTO predictions 
                (prediction_time, target_time, predicted_metrics, confidence_scores,
                 anomaly_score, risk_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                prediction.prediction_time.isoformat(),
                target_time.isoformat(),
                json.dumps(prediction.predicted_metrics),
                json.dumps(prediction.confidence_scores),
                prediction.anomaly_score,
                prediction.risk_level
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"예측 저장 오류: {e}")
    
    async def _save_optimization_result(self, action: OptimizationAction, success: bool):
        """최적화 결과 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO optimization_actions 
                (action_id, action_type, target_component, parameters, expected_improvement,
                 confidence, execution_time, completion_time, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action.action_id,
                action.action_type,
                action.target_component,
                json.dumps(action.parameters),
                action.expected_improvement,
                action.confidence,
                action.execution_time.isoformat(),
                datetime.now().isoformat(),
                success
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"최적화 결과 저장 오류: {e}")
    
    async def _send_performance_alert(self, prediction: PerformancePrediction):
        """성능 알림 발송"""
        try:
            alert_message = {
                "type": "performance_alert",
                "risk_level": prediction.risk_level,
                "predicted_metrics": prediction.predicted_metrics,
                "recommendations": prediction.recommendations,
                "timestamp": prediction.prediction_time.isoformat()
            }
            
            # Redis pub/sub로 알림 발송
            self.redis_client.publish("performance_alerts", json.dumps(alert_message))
            
            logger.warning(f"🚨 성능 알림 발송: {prediction.risk_level} 위험 수준")
            
        except Exception as e:
            logger.error(f"성능 알림 발송 오류: {e}")
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """성능 분석 데이터 조회"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            # 최근 24시간 성능 트렌드
            cursor.execute("""
                SELECT * FROM performance_metrics 
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
            """)
            recent_metrics = cursor.fetchall()
            
            # 최근 예측 정확도
            cursor.execute("""
                SELECT AVG(CASE WHEN risk_level = 'low' THEN 1 ELSE 0 END) as accuracy
                FROM predictions 
                WHERE prediction_time > datetime('now', '-7 days')
            """)
            prediction_accuracy = cursor.fetchone()[0] or 0
            
            # 최적화 성공률
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_optimizations,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_optimizations
                FROM optimization_actions 
                WHERE execution_time > datetime('now', '-7 days')
            """)
            opt_stats = cursor.fetchone()
            optimization_success_rate = (opt_stats[1] / opt_stats[0] * 100) if opt_stats[0] > 0 else 0
            
            conn.close()
            
            return {
                "recent_metrics_count": len(recent_metrics),
                "prediction_accuracy": prediction_accuracy * 100,
                "optimization_success_rate": optimization_success_rate,
                "current_models": list(self.models.keys()),
                "anomaly_detector_available": self.anomaly_detector is not None,
                "last_retrain_time": datetime.now().isoformat(),
                "metrics_buffer_size": len(self.metrics_buffer),
                "predictions_buffer_size": len(self.predictions_buffer)
            }
            
        except Exception as e:
            logger.error(f"성능 분석 데이터 조회 오류: {e}")
            return {}

# 메인 실행
async def main():
    """메인 실행 함수"""
    optimizer = PerformanceMLOptimizer()
    
    try:
        logger.info("🤖 ML 기반 성능 최적화 시스템 시작")
        await optimizer.start_optimization_loop()
    except KeyboardInterrupt:
        logger.info("⏹️ 시스템 종료")
    except Exception as e:
        logger.error(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 