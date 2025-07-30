"""
실시간 예측 시스템
고성능 실시간 예측, 스트리밍 데이터 처리, 예측 결과 캐싱을 지원하는 시스템
"""

import logging
import json
import asyncio
import aiohttp
from aiohttp import web
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import hashlib
import threading
import queue
import time
import schedule
from collections import defaultdict, deque
import asyncio
import websockets
import json
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pydantic
from pydantic import BaseModel
from pathlib import Path

# ML 라이브러리
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """예측 타입"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    RECOMMENDATION = "recommendation"

class DataSourceType(Enum):
    """데이터 소스 타입"""
    API = "api"
    DATABASE = "database"
    STREAM = "stream"
    FILE = "file"
    WEBSOCKET = "websocket"

@dataclass
class PredictionRequest:
    """예측 요청"""
    id: str
    model_id: str
    data: Union[Dict, List, np.ndarray]
    timestamp: datetime
    priority: int = 1
    metadata: Dict[str, Any] = None

@dataclass
class PredictionResponse:
    """예측 응답"""
    id: str
    request_id: str
    model_id: str
    prediction: Any
    confidence: float
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class ModelCache:
    """모델 캐시"""
    model_id: str
    model: Any
    last_used: datetime
    load_count: int
    memory_usage: int
    is_loaded: bool = True

class PredictionRequestModel(BaseModel):
    """예측 요청 모델"""
    data: Union[Dict, List]
    priority: int = 1
    metadata: Optional[Dict[str, Any]] = None

class RealTimePredictionService:
    """실시간 예측 서비스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.db_connection = None
        self.models: Dict[str, ModelCache] = {}
        self.prediction_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.prediction_workers: List[asyncio.Task] = []
        self.is_running = False
        
        self._initialize_connections()
        self._setup_fastapi()
        self._load_models()
        self._start_workers()
    
    def _initialize_connections(self):
        """연결 초기화"""
        try:
            # Redis 연결
            self.redis_client = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            
            # PostgreSQL 연결
            self.db_connection = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            
            logger.info("실시간 예측 서비스 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"연결 초기화 오류: {e}")
            raise
    
    def _setup_fastapi(self):
        """FastAPI 설정"""
        self.app = FastAPI(
            title="Real-time Prediction API",
            description="실시간 예측 API",
            version="1.0.0"
        )
        
        # CORS 설정
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 라우트 설정
        self._setup_routes()
    
    def _setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.post("/predict/{model_id}")
        async def predict_endpoint(
            model_id: str,
            request: PredictionRequestModel,
            background_tasks: BackgroundTasks
        ):
            """예측 엔드포인트"""
            try:
                prediction_id = str(uuid.uuid4())
                
                # 예측 요청 생성
                pred_request = PredictionRequest(
                    id=prediction_id,
                    model_id=model_id,
                    data=request.data,
                    timestamp=datetime.now(),
                    priority=request.priority,
                    metadata=request.metadata
                )
                
                # 예측 큐에 추가
                await self.prediction_queue.put(pred_request)
                
                # 비동기 예측 처리
                background_tasks.add_task(self._process_prediction, pred_request)
                
                return {
                    "prediction_id": prediction_id,
                    "status": "processing",
                    "message": "예측 요청이 큐에 추가되었습니다"
                }
                
            except Exception as e:
                logger.error(f"예측 엔드포인트 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/predict/{model_id}/result/{prediction_id}")
        async def get_prediction_result(model_id: str, prediction_id: str):
            """예측 결과 조회"""
            try:
                # Redis에서 결과 조회
                result_key = f"prediction_result:{prediction_id}"
                result_data = self.redis_client.get(result_key)
                
                if result_data:
                    result = json.loads(result_data)
                    return result
                else:
                    return {
                        "status": "processing",
                        "message": "예측이 아직 완료되지 않았습니다"
                    }
                    
            except Exception as e:
                logger.error(f"예측 결과 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws/predictions")
        async def websocket_endpoint(websocket: websockets.WebSocketServerProtocol):
            """WebSocket 엔드포인트"""
            try:
                await websocket.accept()
                connection_id = str(uuid.uuid4())
                self.websocket_connections[connection_id] = websocket
                
                try:
                    while True:
                        # 예측 결과 대기
                        response = await self.response_queue.get()
                        
                        # WebSocket으로 결과 전송
                        await websocket.send_text(json.dumps(asdict(response)))
                        
                except websockets.exceptions.ConnectionClosed:
                    pass
                finally:
                    del self.websocket_connections[connection_id]
                    
            except Exception as e:
                logger.error(f"WebSocket 오류: {e}")
        
        @self.app.get("/models")
        async def get_models():
            """모델 목록 조회"""
            try:
                models_info = []
                for model_id, model_cache in self.models.items():
                    models_info.append({
                        "model_id": model_id,
                        "is_loaded": model_cache.is_loaded,
                        "last_used": model_cache.last_used.isoformat(),
                        "load_count": model_cache.load_count,
                        "memory_usage": model_cache.memory_usage
                    })
                
                return {"models": models_info}
                
            except Exception as e:
                logger.error(f"모델 목록 조회 오류: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """헬스 체크"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "queue_size": self.prediction_queue.qsize(),
                "active_models": len([m for m in self.models.values() if m.is_loaded])
            }
    
    def _load_models(self):
        """모델 로드"""
        try:
            models_dir = Path(self.config.get('models_dir', './models'))
            
            for model_file in models_dir.glob('*.pkl'):
                model_id = model_file.stem
                
                # 모델 로드
                with open(model_file, 'rb') as f:
                    model = pickle.load(f)
                
                # 모델 캐시 생성
                model_cache = ModelCache(
                    model_id=model_id,
                    model=model,
                    last_used=datetime.now(),
                    load_count=1,
                    memory_usage=self._estimate_model_size(model),
                    is_loaded=True
                )
                
                self.models[model_id] = model_cache
                
                logger.info(f"모델 로드 완료: {model_id}")
                
        except Exception as e:
            logger.error(f"모델 로드 오류: {e}")
    
    def _estimate_model_size(self, model: Any) -> int:
        """모델 크기 추정"""
        try:
            # 간단한 크기 추정
            if hasattr(model, 'n_features_in_'):
                return model.n_features_in_ * 8  # 바이트 단위
            else:
                return 1024 * 1024  # 1MB 기본값
        except:
            return 1024 * 1024
    
    def _start_workers(self):
        """워커 시작"""
        self.is_running = True
        
        # 예측 워커 시작
        for i in range(self.config.get('num_workers', 4)):
            worker = asyncio.create_task(self._prediction_worker(f"worker-{i}"))
            self.prediction_workers.append(worker)
        
        # 모델 관리 워커 시작
        asyncio.create_task(self._model_manager_worker())
        
        logger.info("실시간 예측 워커 시작 완료")
    
    async def _prediction_worker(self, worker_id: str):
        """예측 워커"""
        while self.is_running:
            try:
                # 예측 요청 대기
                request = await self.prediction_queue.get()
                
                start_time = time.time()
                
                # 모델 가져오기
                model_cache = self.models.get(request.model_id)
                if not model_cache or not model_cache.is_loaded:
                    # 모델 로드
                    await self._load_model(request.model_id)
                    model_cache = self.models.get(request.model_id)
                
                if not model_cache:
                    logger.error(f"모델을 찾을 수 없습니다: {request.model_id}")
                    continue
                
                # 데이터 전처리
                processed_data = await self._preprocess_data(request.data, request.model_id)
                
                # 예측 수행
                prediction = await self._make_prediction(model_cache.model, processed_data)
                
                # 신뢰도 계산
                confidence = await self._calculate_confidence(model_cache.model, processed_data, prediction)
                
                processing_time = time.time() - start_time
                
                # 예측 응답 생성
                response = PredictionResponse(
                    id=str(uuid.uuid4()),
                    request_id=request.id,
                    model_id=request.model_id,
                    prediction=prediction,
                    confidence=confidence,
                    processing_time=processing_time,
                    timestamp=datetime.now(),
                    metadata=request.metadata
                )
                
                # 결과 저장
                await self._save_prediction_result(response)
                
                # 응답 큐에 추가
                await self.response_queue.put(response)
                
                # 모델 사용 통계 업데이트
                model_cache.last_used = datetime.now()
                model_cache.load_count += 1
                
                logger.info(f"예측 완료: {request.id} (시간: {processing_time:.3f}초)")
                
            except Exception as e:
                logger.error(f"예측 워커 오류: {e}")
                await asyncio.sleep(1)
    
    async def _model_manager_worker(self):
        """모델 관리 워커"""
        while self.is_running:
            try:
                # 메모리 사용량 체크
                total_memory = sum(m.memory_usage for m in self.models.values() if m.is_loaded)
                max_memory = self.config.get('max_memory_mb', 1024) * 1024 * 1024  # GB to bytes
                
                if total_memory > max_memory:
                    # 가장 오래된 모델 언로드
                    await self._unload_oldest_model()
                
                # 주기적으로 사용하지 않는 모델 언로드
                await self._cleanup_unused_models()
                
                await asyncio.sleep(60)  # 1분마다 체크
                
            except Exception as e:
                logger.error(f"모델 관리 워커 오류: {e}")
                await asyncio.sleep(60)
    
    async def _load_model(self, model_id: str):
        """모델 로드"""
        try:
            models_dir = Path(self.config.get('models_dir', './models'))
            model_file = models_dir / f"{model_id}.pkl"
            
            if not model_file.exists():
                logger.error(f"모델 파일을 찾을 수 없습니다: {model_file}")
                return
            
            # 모델 로드
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
            
            # 모델 캐시 생성/업데이트
            model_cache = ModelCache(
                model_id=model_id,
                model=model,
                last_used=datetime.now(),
                load_count=1,
                memory_usage=self._estimate_model_size(model),
                is_loaded=True
            )
            
            self.models[model_id] = model_cache
            
            logger.info(f"모델 로드 완료: {model_id}")
            
        except Exception as e:
            logger.error(f"모델 로드 오류: {e}")
    
    async def _unload_oldest_model(self):
        """가장 오래된 모델 언로드"""
        try:
            oldest_model = None
            oldest_time = datetime.now()
            
            for model_cache in self.models.values():
                if model_cache.is_loaded and model_cache.last_used < oldest_time:
                    oldest_time = model_cache.last_used
                    oldest_model = model_cache
            
            if oldest_model:
                oldest_model.is_loaded = False
                oldest_model.model = None
                logger.info(f"모델 언로드: {oldest_model.model_id}")
                
        except Exception as e:
            logger.error(f"모델 언로드 오류: {e}")
    
    async def _cleanup_unused_models(self):
        """사용하지 않는 모델 정리"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)  # 1시간 이상 사용하지 않은 모델
            
            for model_cache in self.models.values():
                if (model_cache.is_loaded and 
                    model_cache.last_used < cutoff_time and
                    model_cache.load_count < 10):  # 10번 미만 사용
                    
                    model_cache.is_loaded = False
                    model_cache.model = None
                    logger.info(f"사용하지 않는 모델 언로드: {model_cache.model_id}")
                    
        except Exception as e:
            logger.error(f"모델 정리 오류: {e}")
    
    async def _preprocess_data(self, data: Union[Dict, List, np.ndarray], model_id: str) -> np.ndarray:
        """데이터 전처리"""
        try:
            # 데이터 타입 변환
            if isinstance(data, dict):
                # 딕셔너리를 배열로 변환
                data_array = np.array(list(data.values())).reshape(1, -1)
            elif isinstance(data, list):
                data_array = np.array(data).reshape(1, -1)
            elif isinstance(data, np.ndarray):
                data_array = data.reshape(1, -1)
            else:
                raise ValueError(f"지원하지 않는 데이터 타입: {type(data)}")
            
            # 특성 스케일링 (필요한 경우)
            # 여기서는 간단한 구현, 실제로는 모델별로 다른 전처리가 필요할 수 있습니다
            
            return data_array
            
        except Exception as e:
            logger.error(f"데이터 전처리 오류: {e}")
            raise
    
    async def _make_prediction(self, model: Any, data: np.ndarray) -> Any:
        """예측 수행"""
        try:
            if TENSORFLOW_AVAILABLE and isinstance(model, keras.Model):
                # TensorFlow 모델 예측
                prediction = model.predict(data, verbose=0)
                return prediction.tolist()
            else:
                # 전통적 ML 모델 예측
                prediction = model.predict(data)
                return prediction.tolist() if hasattr(prediction, 'tolist') else prediction
                
        except Exception as e:
            logger.error(f"예측 수행 오류: {e}")
            raise
    
    async def _calculate_confidence(self, model: Any, data: np.ndarray, prediction: Any) -> float:
        """신뢰도 계산"""
        try:
            if hasattr(model, 'predict_proba'):
                # 확률 기반 신뢰도
                probabilities = model.predict_proba(data)
                confidence = np.max(probabilities)
                return float(confidence)
            else:
                # 기본 신뢰도 (0.8)
                return 0.8
                
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {e}")
            return 0.5
    
    async def _save_prediction_result(self, response: PredictionResponse):
        """예측 결과 저장"""
        try:
            # Redis에 결과 저장 (TTL: 1시간)
            result_key = f"prediction_result:{response.request_id}"
            result_data = asdict(response)
            result_data['timestamp'] = result_data['timestamp'].isoformat()
            
            self.redis_client.setex(
                result_key,
                3600,  # 1시간 TTL
                json.dumps(result_data)
            )
            
            # 데이터베이스에 결과 저장
            await self._save_to_database(response)
            
        except Exception as e:
            logger.error(f"예측 결과 저장 오류: {e}")
    
    async def _save_to_database(self, response: PredictionResponse):
        """데이터베이스에 결과 저장"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO prediction_results 
                    (id, request_id, model_id, prediction, confidence, processing_time, timestamp, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    response.id,
                    response.request_id,
                    response.model_id,
                    json.dumps(response.prediction),
                    response.confidence,
                    response.processing_time,
                    response.timestamp,
                    json.dumps(response.metadata) if response.metadata else None
                ))
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"데이터베이스 저장 오류: {e}")
    
    async def predict(self, model_id: str, data: Union[Dict, List, np.ndarray], 
                     priority: int = 1, metadata: Dict[str, Any] = None) -> str:
        """예측 요청"""
        try:
            prediction_id = str(uuid.uuid4())
            
            request = PredictionRequest(
                id=prediction_id,
                model_id=model_id,
                data=data,
                timestamp=datetime.now(),
                priority=priority,
                metadata=metadata
            )
            
            await self.prediction_queue.put(request)
            
            return prediction_id
            
        except Exception as e:
            logger.error(f"예측 요청 오류: {e}")
            raise
    
    async def get_prediction_result(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """예측 결과 조회"""
        try:
            result_key = f"prediction_result:{prediction_id}"
            result_data = self.redis_client.get(result_key)
            
            if result_data:
                return json.loads(result_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"예측 결과 조회 오류: {e}")
            return None
    
    def get_service_stats(self) -> Dict[str, Any]:
        """서비스 통계"""
        try:
            stats = {
                'queue_size': self.prediction_queue.qsize(),
                'active_models': len([m for m in self.models.values() if m.is_loaded]),
                'total_models': len(self.models),
                'websocket_connections': len(self.websocket_connections),
                'memory_usage': sum(m.memory_usage for m in self.models.values() if m.is_loaded),
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"서비스 통계 조회 오류: {e}")
            return {}
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000):
        """서버 실행"""
        try:
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                log_level="info"
            )
        except Exception as e:
            logger.error(f"서버 실행 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        self.is_running = False
        
        # 워커 정리
        for worker in self.prediction_workers:
            worker.cancel()
        
        # WebSocket 연결 정리
        for websocket in self.websocket_connections.values():
            asyncio.create_task(websocket.close())
        
        logger.info('실시간 예측 서비스 정리 완료')

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 7
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'your_program',
            'user': 'postgres',
            'password': 'password'
        },
        'models_dir': './models',
        'num_workers': 4,
        'max_memory_mb': 1024
    }
    
    # 실시간 예측 서비스 생성
    prediction_service = RealTimePredictionService(config)
    
    # 서버 실행
    prediction_service.run_server(host="0.0.0.0", port=8000) 