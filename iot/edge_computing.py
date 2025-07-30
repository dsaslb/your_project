"""
엣지 컴퓨팅 시스템
분산 처리, 로컬 분석, 실시간 추론, 데이터 압축을 포함한 완전한 엣지 컴퓨팅 플랫폼
"""

import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import asyncio
import aiohttp
from aiohttp import web
import websockets
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import sqlite3
from pathlib import Path
import pickle
import hashlib
import hmac
import base64
import secrets
import struct
import socket
import ssl
import paho.mqtt.client as mqtt
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import schedule
import zlib
import gzip
import lz4.frame
import joblib
import sklearn
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import torch
import torch.nn as nn

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdgeNodeType(Enum):
    """엣지 노드 타입"""
    GATEWAY = "gateway"
    SENSOR_HUB = "sensor_hub"
    PROCESSING_UNIT = "processing_unit"
    STORAGE_UNIT = "storage_unit"
    AI_UNIT = "ai_unit"

class ProcessingType(Enum):
    """처리 타입"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAM = "stream"
    EVENT_DRIVEN = "event_driven"

class CompressionType(Enum):
    """압축 타입"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZLIB = "zlib"
    CUSTOM = "custom"

@dataclass
class EdgeNode:
    """엣지 노드"""
    node_id: str
    node_type: EdgeNodeType
    name: str
    location: Dict[str, float]
    capabilities: List[str]
    resources: Dict[str, Any]
    status: str
    connected_devices: List[str]
    processing_tasks: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class ProcessingTask:
    """처리 작업"""
    task_id: str
    node_id: str
    task_type: str
    processing_type: ProcessingType
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    status: str
    priority: int
    created_at: datetime
    started_at: datetime = None
    completed_at: datetime = None
    error_message: str = ""

@dataclass
class AIModel:
    """AI 모델"""
    model_id: str
    node_id: str
    name: str
    model_type: str
    model_data: bytes
    input_shape: List[int]
    output_shape: List[int]
    accuracy: float
    created_at: datetime
    updated_at: datetime

@dataclass
class DataStream:
    """데이터 스트림"""
    stream_id: str
    source_node_id: str
    target_node_id: str
    data_type: str
    compression_type: CompressionType
    encryption_enabled: bool
    buffer_size: int
    batch_size: int
    status: str
    created_at: datetime

class EdgeComputingSystem:
    """엣지 컴퓨팅 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.nodes: Dict[str, EdgeNode] = {}
        self.tasks: Dict[str, ProcessingTask] = {}
        self.ai_models: Dict[str, AIModel] = {}
        self.data_streams: Dict[str, DataStream] = {}
        self.task_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        
        # 처리 엔진
        self.processing_engines: Dict[str, Callable] = {}
        self.ai_engines: Dict[str, Any] = {}
        
        # MQTT 클라이언트
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # WebSocket 서버
        self.websocket_server = None
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './edge_computing.db'))
        self._init_database()
        
        # MQTT 초기화
        self._init_mqtt()
        
        # 처리 엔진 등록
        self._register_processing_engines()
        
        # 작업 처리 스레드
        self.processing_threads: Dict[str, threading.Thread] = {}
        self.is_running = False
        
        logger.info("엣지 컴퓨팅 시스템 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 엣지 노드 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS edge_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT,
                    name TEXT,
                    location TEXT,
                    capabilities TEXT,
                    resources TEXT,
                    status TEXT,
                    connected_devices TEXT,
                    processing_tasks TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 처리 작업 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_tasks (
                    task_id TEXT PRIMARY KEY,
                    node_id TEXT,
                    task_type TEXT,
                    processing_type TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    status TEXT,
                    priority INTEGER,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT,
                    FOREIGN KEY (node_id) REFERENCES edge_nodes (node_id)
                )
            ''')
            
            # AI 모델 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_models (
                    model_id TEXT PRIMARY KEY,
                    node_id TEXT,
                    name TEXT,
                    model_type TEXT,
                    model_data BLOB,
                    input_shape TEXT,
                    output_shape TEXT,
                    accuracy REAL,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (node_id) REFERENCES edge_nodes (node_id)
                )
            ''')
            
            # 데이터 스트림 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_streams (
                    stream_id TEXT PRIMARY KEY,
                    source_node_id TEXT,
                    target_node_id TEXT,
                    data_type TEXT,
                    compression_type TEXT,
                    encryption_enabled INTEGER,
                    buffer_size INTEGER,
                    batch_size INTEGER,
                    status TEXT,
                    created_at TEXT,
                    FOREIGN KEY (source_node_id) REFERENCES edge_nodes (node_id),
                    FOREIGN KEY (target_node_id) REFERENCES edge_nodes (node_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("엣지 컴퓨팅 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _init_mqtt(self):
        """MQTT 클라이언트 초기화"""
        try:
            mqtt_config = self.config.get('mqtt', {})
            
            self.mqtt_client = mqtt.Client(
                client_id=f"edge_computing_{uuid.uuid4().hex[:8]}",
                clean_session=True
            )
            
            # 콜백 설정
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_message = self._on_mqtt_message
            
            # 연결
            self.mqtt_client.connect(
                mqtt_config.get('host', 'localhost'),
                mqtt_config.get('port', 1883),
                mqtt_config.get('keepalive', 60)
            )
            
            # 백그라운드 루프 시작
            self.mqtt_client.loop_start()
            
            logger.info("MQTT 클라이언트 초기화 완료")
            
        except Exception as e:
            logger.error(f"MQTT 초기화 오류: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT 연결 콜백"""
        try:
            if rc == 0:
                self.mqtt_connected = True
                logger.info("MQTT 브로커에 연결되었습니다")
                
                # 엣지 노드 토픽 구독
                client.subscribe("edge/nodes/+/status")
                client.subscribe("edge/nodes/+/task")
                client.subscribe("edge/nodes/+/result")
                
            else:
                logger.error(f"MQTT 연결 실패: {rc}")
                
        except Exception as e:
            logger.error(f"MQTT 연결 콜백 오류: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT 연결 해제 콜백"""
        try:
            self.mqtt_connected = False
            logger.warning("MQTT 브로커와 연결이 해제되었습니다")
            
        except Exception as e:
            logger.error(f"MQTT 연결 해제 콜백 오류: {e}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """MQTT 메시지 수신 콜백"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # 토픽 파싱
            parts = topic.split('/')
            if len(parts) >= 4:
                node_id = parts[2]
                message_type = parts[3]
                
                if message_type == 'status':
                    self._handle_node_status(node_id, payload)
                elif message_type == 'task':
                    self._handle_node_task(node_id, payload)
                elif message_type == 'result':
                    self._handle_node_result(node_id, payload)
                    
        except Exception as e:
            logger.error(f"MQTT 메시지 처리 오류: {e}")
    
    def register_edge_node(self, node_info: Dict[str, Any]) -> str:
        """엣지 노드 등록"""
        try:
            node_id = str(uuid.uuid4())
            
            node = EdgeNode(
                node_id=node_id,
                node_type=EdgeNodeType(node_info['node_type']),
                name=node_info['name'],
                location=node_info.get('location', {'lat': 0, 'lng': 0, 'alt': 0}),
                capabilities=node_info.get('capabilities', []),
                resources=node_info.get('resources', {}),
                status='active',
                connected_devices=node_info.get('connected_devices', []),
                processing_tasks=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.nodes[node_id] = node
            
            # 데이터베이스에 저장
            self._save_node_to_db(node)
            
            logger.info(f"엣지 노드 등록 완료: {node_id}")
            return node_id
            
        except Exception as e:
            logger.error(f"엣지 노드 등록 오류: {e}")
            raise
    
    def create_processing_task(self, node_id: str, task_type: str, 
                             input_data: Dict[str, Any], processing_type: ProcessingType = ProcessingType.REAL_TIME,
                             priority: int = 1) -> str:
        """처리 작업 생성"""
        try:
            if node_id not in self.nodes:
                raise ValueError(f"엣지 노드를 찾을 수 없습니다: {node_id}")
            
            task_id = str(uuid.uuid4())
            
            task = ProcessingTask(
                task_id=task_id,
                node_id=node_id,
                task_type=task_type,
                processing_type=processing_type,
                input_data=input_data,
                output_data={},
                status="pending",
                priority=priority,
                created_at=datetime.now()
            )
            
            self.tasks[task_id] = task
            
            # 노드의 작업 목록에 추가
            self.nodes[node_id].processing_tasks.append(task_id)
            self.nodes[node_id].updated_at = datetime.now()
            
            # 데이터베이스에 저장
            self._save_task_to_db(task)
            self._save_node_to_db(self.nodes[node_id])
            
            # 작업 큐에 추가
            asyncio.create_task(self.task_queue.put(task))
            
            logger.info(f"처리 작업 생성 완료: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"처리 작업 생성 오류: {e}")
            raise
    
    async def process_task(self, task: ProcessingTask):
        """작업 처리"""
        try:
            task.status = "processing"
            task.started_at = datetime.now()
            self._save_task_to_db(task)
            
            # 처리 엔진 선택
            processor = self.processing_engines.get(task.task_type)
            if not processor:
                raise ValueError(f"처리 엔진을 찾을 수 없습니다: {task.task_type}")
            
            # 작업 처리
            result = await processor(task.input_data)
            
            task.output_data = result
            task.status = "completed"
            task.completed_at = datetime.now()
            
            self._save_task_to_db(task)
            
            # 결과 큐에 추가
            await self.result_queue.put(task)
            
            logger.info(f"작업 처리 완료: {task.task_id}")
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self._save_task_to_db(task)
            
            logger.error(f"작업 처리 오류: {e}")
    
    def _register_processing_engines(self):
        """처리 엔진 등록"""
        try:
            # 데이터 필터링 엔진
            self.processing_engines['data_filtering'] = self._filter_data
            
            # 데이터 집계 엔진
            self.processing_engines['data_aggregation'] = self._aggregate_data
            
            # 이상 탐지 엔진
            self.processing_engines['anomaly_detection'] = self._detect_anomalies
            
            # 데이터 압축 엔진
            self.processing_engines['data_compression'] = self._compress_data
            
            # 실시간 분석 엔진
            self.processing_engines['real_time_analysis'] = self._analyze_real_time
            
            # 예측 모델 엔진
            self.processing_engines['prediction'] = self._run_prediction
            
            logger.info("처리 엔진 등록 완료")
            
        except Exception as e:
            logger.error(f"처리 엔진 등록 오류: {e}")
    
    async def _filter_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 필터링"""
        try:
            data = input_data.get('data', [])
            filters = input_data.get('filters', {})
            
            filtered_data = []
            
            for item in data:
                include = True
                
                for field, condition in filters.items():
                    if field in item:
                        value = item[field]
                        
                        if 'min' in condition and value < condition['min']:
                            include = False
                        if 'max' in condition and value > condition['max']:
                            include = False
                        if 'equals' in condition and value != condition['equals']:
                            include = False
                        if 'contains' in condition and condition['contains'] not in str(value):
                            include = False
                
                if include:
                    filtered_data.append(item)
            
            return {
                'filtered_data': filtered_data,
                'original_count': len(data),
                'filtered_count': len(filtered_data),
                'filters_applied': filters
            }
            
        except Exception as e:
            logger.error(f"데이터 필터링 오류: {e}")
            raise
    
    async def _aggregate_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 집계"""
        try:
            data = input_data.get('data', [])
            aggregation_type = input_data.get('aggregation_type', 'mean')
            group_by = input_data.get('group_by', None)
            
            if not data:
                return {'aggregated_data': [], 'aggregation_type': aggregation_type}
            
            df = pd.DataFrame(data)
            
            if group_by and group_by in df.columns:
                # 그룹별 집계
                grouped = df.groupby(group_by)
                
                if aggregation_type == 'mean':
                    result = grouped.mean()
                elif aggregation_type == 'sum':
                    result = grouped.sum()
                elif aggregation_type == 'count':
                    result = grouped.count()
                elif aggregation_type == 'min':
                    result = grouped.min()
                elif aggregation_type == 'max':
                    result = grouped.max()
                else:
                    result = grouped.mean()
            else:
                # 전체 집계
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                
                if aggregation_type == 'mean':
                    result = df[numeric_columns].mean()
                elif aggregation_type == 'sum':
                    result = df[numeric_columns].sum()
                elif aggregation_type == 'count':
                    result = df.count()
                elif aggregation_type == 'min':
                    result = df[numeric_columns].min()
                elif aggregation_type == 'max':
                    result = df[numeric_columns].max()
                else:
                    result = df[numeric_columns].mean()
            
            return {
                'aggregated_data': result.to_dict(),
                'aggregation_type': aggregation_type,
                'group_by': group_by,
                'data_count': len(data)
            }
            
        except Exception as e:
            logger.error(f"데이터 집계 오류: {e}")
            raise
    
    async def _detect_anomalies(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """이상 탐지"""
        try:
            data = input_data.get('data', [])
            method = input_data.get('method', 'isolation_forest')
            threshold = input_data.get('threshold', 0.1)
            
            if not data:
                return {'anomalies': [], 'method': method}
            
            # 데이터를 numpy 배열로 변환
            values = np.array([item.get('value', 0) for item in data])
            
            if method == 'isolation_forest':
                # Isolation Forest 사용
                clf = IsolationForest(contamination=threshold, random_state=42)
                predictions = clf.fit_predict(values.reshape(-1, 1))
                
                # -1이 이상치
                anomaly_indices = np.where(predictions == -1)[0]
                
            elif method == 'z_score':
                # Z-score 방법
                mean = np.mean(values)
                std = np.std(values)
                z_scores = np.abs((values - mean) / std)
                anomaly_indices = np.where(z_scores > 2)[0]
                
            elif method == 'iqr':
                # IQR 방법
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                anomaly_indices = np.where((values < lower_bound) | (values > upper_bound))[0]
                
            else:
                anomaly_indices = []
            
            anomalies = []
            for idx in anomaly_indices:
                if idx < len(data):
                    anomalies.append({
                        'index': int(idx),
                        'data_point': data[idx],
                        'value': float(values[idx])
                    })
            
            return {
                'anomalies': anomalies,
                'method': method,
                'threshold': threshold,
                'total_points': len(data),
                'anomaly_count': len(anomalies)
            }
            
        except Exception as e:
            logger.error(f"이상 탐지 오류: {e}")
            raise
    
    async def _compress_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 압축"""
        try:
            data = input_data.get('data', '')
            compression_type = CompressionType(input_data.get('compression_type', 'gzip'))
            
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            elif isinstance(data, dict):
                data_bytes = json.dumps(data).encode('utf-8')
            else:
                data_bytes = str(data).encode('utf-8')
            
            original_size = len(data_bytes)
            
            if compression_type == CompressionType.GZIP:
                compressed_data = gzip.compress(data_bytes)
            elif compression_type == CompressionType.LZ4:
                compressed_data = lz4.frame.compress(data_bytes)
            elif compression_type == CompressionType.ZLIB:
                compressed_data = zlib.compress(data_bytes)
            else:
                compressed_data = data_bytes
            
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return {
                'compressed_data': base64.b64encode(compressed_data).decode('utf-8'),
                'compression_type': compression_type.value,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio
            }
            
        except Exception as e:
            logger.error(f"데이터 압축 오류: {e}")
            raise
    
    async def _analyze_real_time(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """실시간 분석"""
        try:
            data = input_data.get('data', [])
            analysis_type = input_data.get('analysis_type', 'trend')
            
            if not data:
                return {'analysis_result': {}, 'analysis_type': analysis_type}
            
            values = [item.get('value', 0) for item in data]
            timestamps = [item.get('timestamp', '') for item in data]
            
            if analysis_type == 'trend':
                # 트렌드 분석
                if len(values) >= 2:
                    trend = 'increasing' if values[-1] > values[0] else 'decreasing'
                    change_rate = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
                else:
                    trend = 'stable'
                    change_rate = 0
                
                result = {
                    'trend': trend,
                    'change_rate': change_rate,
                    'current_value': values[-1] if values else 0,
                    'average_value': np.mean(values) if values else 0
                }
                
            elif analysis_type == 'statistics':
                # 통계 분석
                result = {
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'count': len(values)
                }
                
            elif analysis_type == 'pattern':
                # 패턴 분석
                result = {
                    'has_pattern': len(set(values)) < len(values),
                    'unique_values': len(set(values)),
                    'most_common': max(set(values), key=values.count) if values else None
                }
                
            else:
                result = {}
            
            return {
                'analysis_result': result,
                'analysis_type': analysis_type,
                'data_points': len(data)
            }
            
        except Exception as e:
            logger.error(f"실시간 분석 오류: {e}")
            raise
    
    async def _run_prediction(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """예측 모델 실행"""
        try:
            model_id = input_data.get('model_id')
            features = input_data.get('features', [])
            
            if not model_id or model_id not in self.ai_models:
                raise ValueError(f"AI 모델을 찾을 수 없습니다: {model_id}")
            
            model = self.ai_models[model_id]
            
            # 모델 로드 및 예측
            if model.model_type == 'sklearn':
                # scikit-learn 모델
                loaded_model = joblib.load(model.model_data)
                prediction = loaded_model.predict([features])
                probabilities = loaded_model.predict_proba([features]) if hasattr(loaded_model, 'predict_proba') else None
                
            elif model.model_type == 'tensorflow':
                # TensorFlow 모델
                loaded_model = tf.keras.models.load_model(model.model_data)
                prediction = loaded_model.predict(np.array([features]))
                
            elif model.model_type == 'pytorch':
                # PyTorch 모델
                loaded_model = torch.load(model.model_data)
                loaded_model.eval()
                with torch.no_grad():
                    input_tensor = torch.tensor([features], dtype=torch.float32)
                    prediction = loaded_model(input_tensor).numpy()
                    
            else:
                raise ValueError(f"지원하지 않는 모델 타입: {model.model_type}")
            
            return {
                'prediction': prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
                'probabilities': probabilities.tolist() if probabilities is not None else None,
                'model_id': model_id,
                'model_accuracy': model.accuracy,
                'features_used': features
            }
            
        except Exception as e:
            logger.error(f"예측 모델 실행 오류: {e}")
            raise
    
    def deploy_ai_model(self, node_id: str, model_info: Dict[str, Any]) -> str:
        """AI 모델 배포"""
        try:
            if node_id not in self.nodes:
                raise ValueError(f"엣지 노드를 찾을 수 없습니다: {node_id}")
            
            model_id = str(uuid.uuid4())
            
            # 모델 데이터 직렬화
            model_data = pickle.dumps(model_info['model'])
            
            model = AIModel(
                model_id=model_id,
                node_id=node_id,
                name=model_info['name'],
                model_type=model_info['model_type'],
                model_data=model_data,
                input_shape=model_info.get('input_shape', []),
                output_shape=model_info.get('output_shape', []),
                accuracy=model_info.get('accuracy', 0.0),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.ai_models[model_id] = model
            
            # 데이터베이스에 저장
            self._save_ai_model_to_db(model)
            
            logger.info(f"AI 모델 배포 완료: {model_id}")
            return model_id
            
        except Exception as e:
            logger.error(f"AI 모델 배포 오류: {e}")
            raise
    
    def create_data_stream(self, source_node_id: str, target_node_id: str, 
                          stream_config: Dict[str, Any]) -> str:
        """데이터 스트림 생성"""
        try:
            if source_node_id not in self.nodes or target_node_id not in self.nodes:
                raise ValueError("소스 또는 타겟 노드를 찾을 수 없습니다")
            
            stream_id = str(uuid.uuid4())
            
            stream = DataStream(
                stream_id=stream_id,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                data_type=stream_config.get('data_type', 'sensor_data'),
                compression_type=CompressionType(stream_config.get('compression_type', 'gzip')),
                encryption_enabled=stream_config.get('encryption_enabled', False),
                buffer_size=stream_config.get('buffer_size', 1000),
                batch_size=stream_config.get('batch_size', 100),
                status='active',
                created_at=datetime.now()
            )
            
            self.data_streams[stream_id] = stream
            
            # 데이터베이스에 저장
            self._save_data_stream_to_db(stream)
            
            logger.info(f"데이터 스트림 생성 완료: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"데이터 스트림 생성 오류: {e}")
            raise
    
    def _handle_node_status(self, node_id: str, payload: str):
        """노드 상태 처리"""
        try:
            status_data = json.loads(payload)
            
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.status = status_data.get('status', 'unknown')
                node.resources = status_data.get('resources', node.resources)
                node.updated_at = datetime.now()
                
                self._save_node_to_db(node)
                
                logger.info(f"노드 상태 업데이트: {node_id} - {node.status}")
                
        except Exception as e:
            logger.error(f"노드 상태 처리 오류: {e}")
    
    def _handle_node_task(self, node_id: str, payload: str):
        """노드 작업 처리"""
        try:
            task_data = json.loads(payload)
            task_id = task_data.get('task_id')
            
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = task_data.get('status', task.status)
                
                if task_data.get('started_at'):
                    task.started_at = datetime.fromisoformat(task_data['started_at'])
                if task_data.get('completed_at'):
                    task.completed_at = datetime.fromisoformat(task_data['completed_at'])
                
                self._save_task_to_db(task)
                
                logger.info(f"노드 작업 업데이트: {task_id} - {task.status}")
                
        except Exception as e:
            logger.error(f"노드 작업 처리 오류: {e}")
    
    def _handle_node_result(self, node_id: str, payload: str):
        """노드 결과 처리"""
        try:
            result_data = json.loads(payload)
            task_id = result_data.get('task_id')
            
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.output_data = result_data.get('result', {})
                task.status = 'completed'
                task.completed_at = datetime.now()
                
                self._save_task_to_db(task)
                
                logger.info(f"노드 결과 수신: {task_id}")
                
        except Exception as e:
            logger.error(f"노드 결과 처리 오류: {e}")
    
    def get_node_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """노드 정보 조회"""
        try:
            node = self.nodes.get(node_id)
            if not node:
                return None
            
            return {
                'node_id': node.node_id,
                'node_type': node.node_type.value,
                'name': node.name,
                'location': node.location,
                'capabilities': node.capabilities,
                'resources': node.resources,
                'status': node.status,
                'connected_devices': node.connected_devices,
                'processing_tasks': node.processing_tasks,
                'created_at': node.created_at.isoformat(),
                'updated_at': node.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"노드 정보 조회 오류: {e}")
            return None
    
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """작업 정보 조회"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                return None
            
            return {
                'task_id': task.task_id,
                'node_id': task.node_id,
                'task_type': task.task_type,
                'processing_type': task.processing_type.value,
                'input_data': task.input_data,
                'output_data': task.output_data,
                'status': task.status,
                'priority': task.priority,
                'created_at': task.created_at.isoformat(),
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'error_message': task.error_message
            }
            
        except Exception as e:
            logger.error(f"작업 정보 조회 오류: {e}")
            return None
    
    def _save_node_to_db(self, node: EdgeNode):
        """노드를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO edge_nodes 
                (node_id, node_type, name, location, capabilities, resources, status,
                 connected_devices, processing_tasks, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                node.node_id,
                node.node_type.value,
                node.name,
                json.dumps(node.location),
                json.dumps(node.capabilities),
                json.dumps(node.resources),
                node.status,
                json.dumps(node.connected_devices),
                json.dumps(node.processing_tasks),
                node.created_at.isoformat(),
                node.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"노드 데이터베이스 저장 오류: {e}")
    
    def _save_task_to_db(self, task: ProcessingTask):
        """작업을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO processing_tasks 
                (task_id, node_id, task_type, processing_type, input_data, output_data,
                 status, priority, created_at, started_at, completed_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.task_id,
                task.node_id,
                task.task_type,
                task.processing_type.value,
                json.dumps(task.input_data),
                json.dumps(task.output_data),
                task.status,
                task.priority,
                task.created_at.isoformat(),
                task.started_at.isoformat() if task.started_at else None,
                task.completed_at.isoformat() if task.completed_at else None,
                task.error_message
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"작업 데이터베이스 저장 오류: {e}")
    
    def _save_ai_model_to_db(self, model: AIModel):
        """AI 모델을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ai_models 
                (model_id, node_id, name, model_type, model_data, input_shape, output_shape,
                 accuracy, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                model.model_id,
                model.node_id,
                model.name,
                model.model_type,
                model.model_data,
                json.dumps(model.input_shape),
                json.dumps(model.output_shape),
                model.accuracy,
                model.created_at.isoformat(),
                model.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"AI 모델 데이터베이스 저장 오류: {e}")
    
    def _save_data_stream_to_db(self, stream: DataStream):
        """데이터 스트림을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO data_streams 
                (stream_id, source_node_id, target_node_id, data_type, compression_type,
                 encryption_enabled, buffer_size, batch_size, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stream.stream_id,
                stream.source_node_id,
                stream.target_node_id,
                stream.data_type,
                stream.compression_type.value,
                1 if stream.encryption_enabled else 0,
                stream.buffer_size,
                stream.batch_size,
                stream.status,
                stream.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"데이터 스트림 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            # MQTT 연결 해제
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            logger.info("엣지 컴퓨팅 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './edge_computing.db',
        'mqtt': {
            'host': 'localhost',
            'port': 1883,
            'keepalive': 60
        }
    }
    
    # 엣지 컴퓨팅 시스템 생성
    edge_system = EdgeComputingSystem(config)
    
    # 엣지 노드 등록
    node_info = {
        'node_type': 'gateway',
        'name': 'Gateway Node 1',
        'location': {'lat': 37.7749, 'lng': -122.4194, 'alt': 10},
        'capabilities': ['data_processing', 'ai_inference', 'data_storage'],
        'resources': {'cpu': 4, 'memory': 8192, 'storage': 1000000},
        'connected_devices': ['device_001', 'device_002']
    }
    
    node_id = edge_system.register_edge_node(node_info)
    print(f"엣지 노드 등록 완료: {node_id}")
    
    # 처리 작업 생성
    task_input = {
        'data': [
            {'timestamp': '2024-01-01T10:00:00', 'value': 25.5},
            {'timestamp': '2024-01-01T10:01:00', 'value': 26.0},
            {'timestamp': '2024-01-01T10:02:00', 'value': 25.8}
        ],
        'filters': {'value': {'min': 20, 'max': 30}}
    }
    
    task_id = edge_system.create_processing_task(
        node_id=node_id,
        task_type='data_filtering',
        input_data=task_input,
        processing_type=ProcessingType.REAL_TIME
    )
    print(f"처리 작업 생성 완료: {task_id}")
    
    # 잠시 대기
    time.sleep(5)
    
    # 작업 정보 조회
    task_info = edge_system.get_task_info(task_id)
    print(f"작업 정보: {task_info}")
    
    # 노드 정보 조회
    node_info = edge_system.get_node_info(node_id)
    print(f"노드 정보: {node_info}") 