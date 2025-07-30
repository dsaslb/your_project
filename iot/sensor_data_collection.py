"""
센서 데이터 수집 시스템
다중 센서 지원, 실시간 데이터 수집, 데이터 전처리, 품질 관리를 포함한 완전한 센서 데이터 수집 플랫폼
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

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorType(Enum):
    """센서 타입"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    LIGHT = "light"
    MOTION = "motion"
    SOUND = "sound"
    VIBRATION = "vibration"
    GAS = "gas"
    PH = "ph"
    CONDUCTIVITY = "conductivity"
    FLOW = "flow"
    LEVEL = "level"
    POSITION = "position"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    MAGNETOMETER = "magnetometer"

class DataQuality(Enum):
    """데이터 품질"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

class CollectionStatus(Enum):
    """수집 상태"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class Sensor:
    """센서 정보"""
    sensor_id: str
    device_id: str
    sensor_type: SensorType
    name: str
    model: str
    manufacturer: str
    unit: str
    range_min: float
    range_max: float
    accuracy: float
    resolution: float
    calibration_date: datetime
    location: Dict[str, float]
    status: str
    sampling_rate: int  # 초 단위
    created_at: datetime
    updated_at: datetime

@dataclass
class SensorData:
    """센서 데이터"""
    data_id: str
    sensor_id: str
    device_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: DataQuality
    confidence: float
    metadata: Dict[str, Any]
    raw_data: bytes
    processed: bool

@dataclass
class DataCollectionConfig:
    """데이터 수집 설정"""
    config_id: str
    sensor_id: str
    sampling_rate: int
    buffer_size: int
    compression_enabled: bool
    encryption_enabled: bool
    quality_threshold: float
    filters: List[Dict[str, Any]]
    transformations: List[Dict[str, Any]]
    created_at: datetime

@dataclass
class DataQualityRule:
    """데이터 품질 규칙"""
    rule_id: str
    sensor_id: str
    rule_type: str
    parameters: Dict[str, Any]
    enabled: bool
    created_at: datetime

class SensorDataCollector:
    """센서 데이터 수집 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sensors: Dict[str, Sensor] = {}
        self.collection_configs: Dict[str, DataCollectionConfig] = {}
        self.quality_rules: Dict[str, List[DataQualityRule]] = defaultdict(list)
        self.data_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.collection_status: Dict[str, CollectionStatus] = {}
        
        # 데이터 처리
        self.data_processors: Dict[str, Callable] = {}
        self.quality_checkers: Dict[str, Callable] = {}
        
        # MQTT 클라이언트
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # WebSocket 서버
        self.websocket_server = None
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './sensor_data.db'))
        self._init_database()
        
        # MQTT 초기화
        self._init_mqtt()
        
        # 기본 데이터 처리기 등록
        self._register_default_processors()
        
        # 수집 스레드
        self.collection_threads: Dict[str, threading.Thread] = {}
        self.is_running = False
        
        logger.info("센서 데이터 수집 시스템 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 센서 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensors (
                    sensor_id TEXT PRIMARY KEY,
                    device_id TEXT,
                    sensor_type TEXT,
                    name TEXT,
                    model TEXT,
                    manufacturer TEXT,
                    unit TEXT,
                    range_min REAL,
                    range_max REAL,
                    accuracy REAL,
                    resolution REAL,
                    calibration_date TEXT,
                    location TEXT,
                    status TEXT,
                    sampling_rate INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 센서 데이터 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    data_id TEXT PRIMARY KEY,
                    sensor_id TEXT,
                    device_id TEXT,
                    timestamp TEXT,
                    value REAL,
                    unit TEXT,
                    quality TEXT,
                    confidence REAL,
                    metadata TEXT,
                    raw_data BLOB,
                    processed INTEGER,
                    FOREIGN KEY (sensor_id) REFERENCES sensors (sensor_id)
                )
            ''')
            
            # 수집 설정 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collection_configs (
                    config_id TEXT PRIMARY KEY,
                    sensor_id TEXT,
                    sampling_rate INTEGER,
                    buffer_size INTEGER,
                    compression_enabled INTEGER,
                    encryption_enabled INTEGER,
                    quality_threshold REAL,
                    filters TEXT,
                    transformations TEXT,
                    created_at TEXT,
                    FOREIGN KEY (sensor_id) REFERENCES sensors (sensor_id)
                )
            ''')
            
            # 품질 규칙 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_rules (
                    rule_id TEXT PRIMARY KEY,
                    sensor_id TEXT,
                    rule_type TEXT,
                    parameters TEXT,
                    enabled INTEGER,
                    created_at TEXT,
                    FOREIGN KEY (sensor_id) REFERENCES sensors (sensor_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("센서 데이터 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _init_mqtt(self):
        """MQTT 클라이언트 초기화"""
        try:
            mqtt_config = self.config.get('mqtt', {})
            
            self.mqtt_client = mqtt.Client(
                client_id=f"sensor_collector_{uuid.uuid4().hex[:8]}",
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
                
                # 센서 데이터 토픽 구독
                client.subscribe("sensors/+/data")
                client.subscribe("sensors/+/status")
                
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
            if len(parts) >= 3:
                sensor_id = parts[1]
                message_type = parts[2]
                
                if message_type == 'data':
                    self._handle_sensor_data(sensor_id, payload)
                elif message_type == 'status':
                    self._handle_sensor_status(sensor_id, payload)
                    
        except Exception as e:
            logger.error(f"MQTT 메시지 처리 오류: {e}")
    
    def register_sensor(self, sensor_info: Dict[str, Any]) -> str:
        """센서 등록"""
        try:
            sensor_id = str(uuid.uuid4())
            
            sensor = Sensor(
                sensor_id=sensor_id,
                device_id=sensor_info['device_id'],
                sensor_type=SensorType(sensor_info['sensor_type']),
                name=sensor_info['name'],
                model=sensor_info['model'],
                manufacturer=sensor_info['manufacturer'],
                unit=sensor_info['unit'],
                range_min=sensor_info.get('range_min', 0.0),
                range_max=sensor_info.get('range_max', 100.0),
                accuracy=sensor_info.get('accuracy', 1.0),
                resolution=sensor_info.get('resolution', 0.1),
                calibration_date=datetime.fromisoformat(sensor_info.get('calibration_date', datetime.now().isoformat())),
                location=sensor_info.get('location', {'lat': 0, 'lng': 0, 'alt': 0}),
                status='active',
                sampling_rate=sensor_info.get('sampling_rate', 60),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.sensors[sensor_id] = sensor
            
            # 기본 수집 설정 생성
            collection_config = DataCollectionConfig(
                config_id=str(uuid.uuid4()),
                sensor_id=sensor_id,
                sampling_rate=sensor.sampling_rate,
                buffer_size=1000,
                compression_enabled=False,
                encryption_enabled=False,
                quality_threshold=0.8,
                filters=[],
                transformations=[],
                created_at=datetime.now()
            )
            
            self.collection_configs[sensor_id] = collection_config
            self.collection_status[sensor_id] = CollectionStatus.ACTIVE
            
            # 기본 품질 규칙 생성
            self._create_default_quality_rules(sensor_id)
            
            # 데이터베이스에 저장
            self._save_sensor_to_db(sensor)
            self._save_collection_config_to_db(collection_config)
            
            # 수집 시작
            self._start_collection(sensor_id)
            
            logger.info(f"센서 등록 완료: {sensor_id}")
            return sensor_id
            
        except Exception as e:
            logger.error(f"센서 등록 오류: {e}")
            raise
    
    def _create_default_quality_rules(self, sensor_id: str):
        """기본 품질 규칙 생성"""
        try:
            sensor = self.sensors[sensor_id]
            
            # 범위 검사 규칙
            range_rule = DataQualityRule(
                rule_id=str(uuid.uuid4()),
                sensor_id=sensor_id,
                rule_type='range_check',
                parameters={
                    'min_value': sensor.range_min,
                    'max_value': sensor.range_max
                },
                enabled=True,
                created_at=datetime.now()
            )
            
            # 이상치 검사 규칙
            outlier_rule = DataQualityRule(
                rule_id=str(uuid.uuid4()),
                sensor_id=sensor_id,
                rule_type='outlier_detection',
                parameters={
                    'method': 'iqr',
                    'threshold': 1.5
                },
                enabled=True,
                created_at=datetime.now()
            )
            
            # 변화율 검사 규칙
            change_rate_rule = DataQualityRule(
                rule_id=str(uuid.uuid4()),
                sensor_id=sensor_id,
                rule_type='change_rate',
                parameters={
                    'max_change_rate': 50.0,  # 50% per sample
                    'window_size': 5
                },
                enabled=True,
                created_at=datetime.now()
            )
            
            self.quality_rules[sensor_id].extend([range_rule, outlier_rule, change_rate_rule])
            
            # 데이터베이스에 저장
            for rule in [range_rule, outlier_rule, change_rate_rule]:
                self._save_quality_rule_to_db(rule)
                
        except Exception as e:
            logger.error(f"기본 품질 규칙 생성 오류: {e}")
    
    def _start_collection(self, sensor_id: str):
        """센서 데이터 수집 시작"""
        try:
            if sensor_id in self.collection_threads:
                return
            
            def collection_worker():
                while self.collection_status.get(sensor_id) == CollectionStatus.ACTIVE:
                    try:
                        # 센서 데이터 수집 (시뮬레이션)
                        sensor_data = self._collect_sensor_data(sensor_id)
                        if sensor_data:
                            self._process_sensor_data(sensor_data)
                        
                        # 수집 간격 대기
                        sensor = self.sensors[sensor_id]
                        time.sleep(sensor.sampling_rate)
                        
                    except Exception as e:
                        logger.error(f"센서 데이터 수집 오류: {e}")
                        time.sleep(5)
            
            thread = threading.Thread(target=collection_worker, daemon=True)
            thread.start()
            self.collection_threads[sensor_id] = thread
            
            logger.info(f"센서 데이터 수집 시작: {sensor_id}")
            
        except Exception as e:
            logger.error(f"센서 데이터 수집 시작 오류: {e}")
    
    def _collect_sensor_data(self, sensor_id: str) -> Optional[SensorData]:
        """센서 데이터 수집 (시뮬레이션)"""
        try:
            sensor = self.sensors[sensor_id]
            
            # 실제 구현에서는 센서 하드웨어에서 데이터를 읽어옴
            # 여기서는 시뮬레이션된 데이터 생성
            
            if sensor.sensor_type == SensorType.TEMPERATURE:
                value = np.random.normal(25.0, 5.0)  # 평균 25°C, 표준편차 5°C
            elif sensor.sensor_type == SensorType.HUMIDITY:
                value = np.random.normal(60.0, 10.0)  # 평균 60%, 표준편차 10%
            elif sensor.sensor_type == SensorType.PRESSURE:
                value = np.random.normal(1013.25, 10.0)  # 평균 1013.25 hPa
            elif sensor.sensor_type == SensorType.LIGHT:
                value = np.random.exponential(500.0)  # 지수 분포
            else:
                value = np.random.uniform(sensor.range_min, sensor.range_max)
            
            # 범위 제한
            value = max(sensor.range_min, min(sensor.range_max, value))
            
            # 원시 데이터 생성
            raw_data = struct.pack('f', value)
            
            sensor_data = SensorData(
                data_id=str(uuid.uuid4()),
                sensor_id=sensor_id,
                device_id=sensor.device_id,
                timestamp=datetime.now(),
                value=value,
                unit=sensor.unit,
                quality=DataQuality.GOOD,
                confidence=0.9,
                metadata={
                    'sensor_type': sensor.sensor_type.value,
                    'accuracy': sensor.accuracy,
                    'resolution': sensor.resolution
                },
                raw_data=raw_data,
                processed=False
            )
            
            return sensor_data
            
        except Exception as e:
            logger.error(f"센서 데이터 수집 오류: {e}")
            return None
    
    def _process_sensor_data(self, sensor_data: SensorData):
        """센서 데이터 처리"""
        try:
            # 품질 검사
            quality = self._check_data_quality(sensor_data)
            sensor_data.quality = quality
            
            # 데이터 필터링
            if self._apply_filters(sensor_data):
                # 데이터 변환
                self._apply_transformations(sensor_data)
                
                # 버퍼에 추가
                self.data_buffers[sensor_data.sensor_id].append(sensor_data)
                
                # 데이터베이스에 저장
                self._save_sensor_data_to_db(sensor_data)
                
                # 실시간 알림
                self._notify_data_received(sensor_data)
                
                sensor_data.processed = True
                
                logger.debug(f"센서 데이터 처리 완료: {sensor_data.data_id}")
            else:
                logger.warning(f"센서 데이터 필터링됨: {sensor_data.data_id}")
                
        except Exception as e:
            logger.error(f"센서 데이터 처리 오류: {e}")
    
    def _check_data_quality(self, sensor_data: SensorData) -> DataQuality:
        """데이터 품질 검사"""
        try:
            sensor_id = sensor_data.sensor_id
            rules = self.quality_rules.get(sensor_id, [])
            
            quality_score = 1.0
            
            for rule in rules:
                if not rule.enabled:
                    continue
                
                if rule.rule_type == 'range_check':
                    score = self._check_range_quality(sensor_data, rule.parameters)
                elif rule.rule_type == 'outlier_detection':
                    score = self._check_outlier_quality(sensor_data, rule.parameters)
                elif rule.rule_type == 'change_rate':
                    score = self._check_change_rate_quality(sensor_data, rule.parameters)
                else:
                    score = 1.0
                
                quality_score *= score
            
            # 품질 등급 결정
            if quality_score >= 0.9:
                return DataQuality.EXCELLENT
            elif quality_score >= 0.7:
                return DataQuality.GOOD
            elif quality_score >= 0.5:
                return DataQuality.FAIR
            elif quality_score >= 0.3:
                return DataQuality.POOR
            else:
                return DataQuality.INVALID
                
        except Exception as e:
            logger.error(f"데이터 품질 검사 오류: {e}")
            return DataQuality.INVALID
    
    def _check_range_quality(self, sensor_data: SensorData, parameters: Dict[str, Any]) -> float:
        """범위 품질 검사"""
        try:
            min_value = parameters.get('min_value', 0.0)
            max_value = parameters.get('max_value', 100.0)
            
            value = sensor_data.value
            
            if min_value <= value <= max_value:
                return 1.0
            else:
                # 범위를 벗어난 정도에 따라 점수 감소
                if value < min_value:
                    deviation = (min_value - value) / (max_value - min_value)
                else:
                    deviation = (value - max_value) / (max_value - min_value)
                
                return max(0.0, 1.0 - deviation)
                
        except Exception as e:
            logger.error(f"범위 품질 검사 오류: {e}")
            return 0.0
    
    def _check_outlier_quality(self, sensor_data: SensorData, parameters: Dict[str, Any]) -> float:
        """이상치 품질 검사"""
        try:
            sensor_id = sensor_data.sensor_id
            recent_data = list(self.data_buffers[sensor_id])
            
            if len(recent_data) < 10:
                return 1.0
            
            values = [data.value for data in recent_data[-10:]]
            current_value = sensor_data.value
            
            # IQR 방법으로 이상치 검사
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            if lower_bound <= current_value <= upper_bound:
                return 1.0
            else:
                # 이상치 정도에 따라 점수 감소
                if current_value < lower_bound:
                    deviation = (lower_bound - current_value) / iqr
                else:
                    deviation = (current_value - upper_bound) / iqr
                
                return max(0.0, 1.0 - deviation * 0.5)
                
        except Exception as e:
            logger.error(f"이상치 품질 검사 오류: {e}")
            return 1.0
    
    def _check_change_rate_quality(self, sensor_data: SensorData, parameters: Dict[str, Any]) -> float:
        """변화율 품질 검사"""
        try:
            sensor_id = sensor_data.sensor_id
            recent_data = list(self.data_buffers[sensor_id])
            
            if len(recent_data) < 2:
                return 1.0
            
            max_change_rate = parameters.get('max_change_rate', 50.0)
            current_value = sensor_data.value
            previous_value = recent_data[-1].value
            
            if previous_value == 0:
                return 1.0
            
            change_rate = abs((current_value - previous_value) / previous_value) * 100
            
            if change_rate <= max_change_rate:
                return 1.0
            else:
                # 변화율 초과 정도에 따라 점수 감소
                return max(0.0, 1.0 - (change_rate - max_change_rate) / max_change_rate)
                
        except Exception as e:
            logger.error(f"변화율 품질 검사 오류: {e}")
            return 1.0
    
    def _apply_filters(self, sensor_data: SensorData) -> bool:
        """데이터 필터 적용"""
        try:
            sensor_id = sensor_data.sensor_id
            config = self.collection_configs.get(sensor_id)
            
            if not config or not config.filters:
                return True
            
            for filter_config in config.filters:
                filter_type = filter_config.get('type')
                
                if filter_type == 'quality_threshold':
                    if sensor_data.quality.value in ['poor', 'invalid']:
                        return False
                        
                elif filter_type == 'value_range':
                    min_val = filter_config.get('min_value')
                    max_val = filter_config.get('max_value')
                    if min_val is not None and sensor_data.value < min_val:
                        return False
                    if max_val is not None and sensor_data.value > max_val:
                        return False
                        
                elif filter_type == 'confidence_threshold':
                    threshold = filter_config.get('threshold', 0.5)
                    if sensor_data.confidence < threshold:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"데이터 필터 적용 오류: {e}")
            return True
    
    def _apply_transformations(self, sensor_data: SensorData):
        """데이터 변환 적용"""
        try:
            sensor_id = sensor_data.sensor_id
            config = self.collection_configs.get(sensor_id)
            
            if not config or not config.transformations:
                return
            
            for transform_config in config.transformations:
                transform_type = transform_config.get('type')
                
                if transform_type == 'scale':
                    factor = transform_config.get('factor', 1.0)
                    sensor_data.value *= factor
                    
                elif transform_type == 'offset':
                    offset = transform_config.get('offset', 0.0)
                    sensor_data.value += offset
                    
                elif transform_type == 'unit_conversion':
                    # 단위 변환 로직
                    pass
                    
                elif transform_type == 'calibration':
                    # 보정 로직
                    pass
            
        except Exception as e:
            logger.error(f"데이터 변환 적용 오류: {e}")
    
    def _notify_data_received(self, sensor_data: SensorData):
        """데이터 수신 알림"""
        try:
            # WebSocket으로 실시간 데이터 전송
            notification = {
                'type': 'sensor_data',
                'sensor_id': sensor_data.sensor_id,
                'device_id': sensor_data.device_id,
                'timestamp': sensor_data.timestamp.isoformat(),
                'value': sensor_data.value,
                'unit': sensor_data.unit,
                'quality': sensor_data.quality.value,
                'confidence': sensor_data.confidence
            }
            
            # 모든 WebSocket 연결에 전송
            for websocket in self.websocket_connections.values():
                asyncio.create_task(websocket.send(json.dumps(notification)))
                
        except Exception as e:
            logger.error(f"데이터 수신 알림 오류: {e}")
    
    def _handle_sensor_data(self, sensor_id: str, payload: str):
        """센서 데이터 처리 (MQTT)"""
        try:
            data = json.loads(payload)
            
            sensor_data = SensorData(
                data_id=str(uuid.uuid4()),
                sensor_id=sensor_id,
                device_id=data.get('device_id', ''),
                timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
                value=data.get('value', 0.0),
                unit=data.get('unit', ''),
                quality=DataQuality(data.get('quality', 'good')),
                confidence=data.get('confidence', 1.0),
                metadata=data.get('metadata', {}),
                raw_data=data.get('raw_data', b'').encode(),
                processed=False
            )
            
            self._process_sensor_data(sensor_data)
            
        except Exception as e:
            logger.error(f"센서 데이터 처리 오류: {e}")
    
    def _handle_sensor_status(self, sensor_id: str, payload: str):
        """센서 상태 처리 (MQTT)"""
        try:
            status_data = json.loads(payload)
            
            if sensor_id in self.sensors:
                sensor = self.sensors[sensor_id]
                sensor.status = status_data.get('status', 'unknown')
                sensor.updated_at = datetime.now()
                
                self._save_sensor_to_db(sensor)
                
                logger.info(f"센서 상태 업데이트: {sensor_id} - {sensor.status}")
                
        except Exception as e:
            logger.error(f"센서 상태 처리 오류: {e}")
    
    def get_sensor_data(self, sensor_id: str, start_time: datetime = None, 
                       end_time: datetime = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """센서 데이터 조회"""
        try:
            if sensor_id not in self.data_buffers:
                return []
            
            data_list = list(self.data_buffers[sensor_id])
            
            # 시간 필터링
            if start_time:
                data_list = [data for data in data_list if data.timestamp >= start_time]
            if end_time:
                data_list = [data for data in data_list if data.timestamp <= end_time]
            
            # 최신 데이터부터 정렬
            data_list.sort(key=lambda x: x.timestamp, reverse=True)
            
            result = []
            for data in data_list[:limit]:
                result.append({
                    'data_id': data.data_id,
                    'sensor_id': data.sensor_id,
                    'device_id': data.device_id,
                    'timestamp': data.timestamp.isoformat(),
                    'value': data.value,
                    'unit': data.unit,
                    'quality': data.quality.value,
                    'confidence': data.confidence,
                    'metadata': data.metadata,
                    'processed': data.processed
                })
            
            return result
            
        except Exception as e:
            logger.error(f"센서 데이터 조회 오류: {e}")
            return []
    
    def get_sensor_statistics(self, sensor_id: str, period: str = '24h') -> Dict[str, Any]:
        """센서 통계 조회"""
        try:
            if sensor_id not in self.data_buffers:
                return {}
            
            data_list = list(self.data_buffers[sensor_id])
            
            # 기간 필터링
            if period == '24h':
                cutoff_time = datetime.now() - timedelta(hours=24)
            elif period == '7d':
                cutoff_time = datetime.now() - timedelta(days=7)
            elif period == '30d':
                cutoff_time = datetime.now() - timedelta(days=30)
            else:
                cutoff_time = datetime.now() - timedelta(hours=24)
            
            recent_data = [data for data in data_list if data.timestamp >= cutoff_time]
            
            if not recent_data:
                return {}
            
            values = [data.value for data in recent_data]
            
            statistics = {
                'count': len(recent_data),
                'min': min(values),
                'max': max(values),
                'mean': np.mean(values),
                'median': np.median(values),
                'std': np.std(values),
                'variance': np.var(values),
                'quality_distribution': {},
                'period': period
            }
            
            # 품질 분포
            quality_counts = defaultdict(int)
            for data in recent_data:
                quality_counts[data.quality.value] += 1
            
            for quality in DataQuality:
                statistics['quality_distribution'][quality.value] = quality_counts[quality.value]
            
            return statistics
            
        except Exception as e:
            logger.error(f"센서 통계 조회 오류: {e}")
            return {}
    
    def _register_default_processors(self):
        """기본 데이터 처리기 등록"""
        try:
            # 온도 센서 처리기
            self.data_processors[SensorType.TEMPERATURE.value] = self._process_temperature_data
            
            # 습도 센서 처리기
            self.data_processors[SensorType.HUMIDITY.value] = self._process_humidity_data
            
            # 압력 센서 처리기
            self.data_processors[SensorType.PRESSURE.value] = self._process_pressure_data
            
            # 조도 센서 처리기
            self.data_processors[SensorType.LIGHT.value] = self._process_light_data
            
            logger.info("기본 데이터 처리기 등록 완료")
            
        except Exception as e:
            logger.error(f"기본 데이터 처리기 등록 오류: {e}")
    
    def _process_temperature_data(self, sensor_data: SensorData):
        """온도 데이터 처리"""
        try:
            # 켈빈로 변환 (필요한 경우)
            if sensor_data.unit.lower() == 'celsius':
                kelvin = sensor_data.value + 273.15
                sensor_data.metadata['kelvin'] = kelvin
            
            # 이상치 검사
            if sensor_data.value < -50 or sensor_data.value > 100:
                sensor_data.quality = DataQuality.POOR
                
        except Exception as e:
            logger.error(f"온도 데이터 처리 오류: {e}")
    
    def _process_humidity_data(self, sensor_data: SensorData):
        """습도 데이터 처리"""
        try:
            # 상대습도 범위 검사
            if sensor_data.value < 0 or sensor_data.value > 100:
                sensor_data.quality = DataQuality.INVALID
                
        except Exception as e:
            logger.error(f"습도 데이터 처리 오류: {e}")
    
    def _process_pressure_data(self, sensor_data: SensorData):
        """압력 데이터 처리"""
        try:
            # 대기압 범위 검사
            if sensor_data.value < 800 or sensor_data.value > 1200:
                sensor_data.quality = DataQuality.POOR
                
        except Exception as e:
            logger.error(f"압력 데이터 처리 오류: {e}")
    
    def _process_light_data(self, sensor_data: SensorData):
        """조도 데이터 처리"""
        try:
            # 음수 값 검사
            if sensor_data.value < 0:
                sensor_data.value = 0
                sensor_data.quality = DataQuality.POOR
                
        except Exception as e:
            logger.error(f"조도 데이터 처리 오류: {e}")
    
    def _save_sensor_to_db(self, sensor: Sensor):
        """센서를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sensors 
                (sensor_id, device_id, sensor_type, name, model, manufacturer, unit,
                 range_min, range_max, accuracy, resolution, calibration_date, location,
                 status, sampling_rate, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sensor.sensor_id,
                sensor.device_id,
                sensor.sensor_type.value,
                sensor.name,
                sensor.model,
                sensor.manufacturer,
                sensor.unit,
                sensor.range_min,
                sensor.range_max,
                sensor.accuracy,
                sensor.resolution,
                sensor.calibration_date.isoformat(),
                json.dumps(sensor.location),
                sensor.status,
                sensor.sampling_rate,
                sensor.created_at.isoformat(),
                sensor.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"센서 데이터베이스 저장 오류: {e}")
    
    def _save_sensor_data_to_db(self, sensor_data: SensorData):
        """센서 데이터를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sensor_data 
                (data_id, sensor_id, device_id, timestamp, value, unit, quality, confidence, metadata, raw_data, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sensor_data.data_id,
                sensor_data.sensor_id,
                sensor_data.device_id,
                sensor_data.timestamp.isoformat(),
                sensor_data.value,
                sensor_data.unit,
                sensor_data.quality.value,
                sensor_data.confidence,
                json.dumps(sensor_data.metadata),
                sensor_data.raw_data,
                1 if sensor_data.processed else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"센서 데이터 데이터베이스 저장 오류: {e}")
    
    def _save_collection_config_to_db(self, config: DataCollectionConfig):
        """수집 설정을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO collection_configs 
                (config_id, sensor_id, sampling_rate, buffer_size, compression_enabled,
                 encryption_enabled, quality_threshold, filters, transformations, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config.config_id,
                config.sensor_id,
                config.sampling_rate,
                config.buffer_size,
                1 if config.compression_enabled else 0,
                1 if config.encryption_enabled else 0,
                config.quality_threshold,
                json.dumps(config.filters),
                json.dumps(config.transformations),
                config.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"수집 설정 데이터베이스 저장 오류: {e}")
    
    def _save_quality_rule_to_db(self, rule: DataQualityRule):
        """품질 규칙을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO quality_rules 
                (rule_id, sensor_id, rule_type, parameters, enabled, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                rule.rule_id,
                rule.sensor_id,
                rule.rule_type,
                json.dumps(rule.parameters),
                1 if rule.enabled else 0,
                rule.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"품질 규칙 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            # 수집 중지
            for sensor_id in self.collection_status:
                self.collection_status[sensor_id] = CollectionStatus.STOPPED
            
            # MQTT 연결 해제
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            logger.info("센서 데이터 수집 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './sensor_data.db',
        'mqtt': {
            'host': 'localhost',
            'port': 1883,
            'keepalive': 60
        }
    }
    
    # 센서 데이터 수집기 생성
    collector = SensorDataCollector(config)
    
    # 온도 센서 등록
    sensor_info = {
        'device_id': 'device_001',
        'sensor_type': 'temperature',
        'name': 'Temperature Sensor 1',
        'model': 'TEMP-001',
        'manufacturer': 'IoT Corp',
        'unit': 'celsius',
        'range_min': -40.0,
        'range_max': 85.0,
        'accuracy': 0.5,
        'resolution': 0.1,
        'calibration_date': datetime.now().isoformat(),
        'location': {'lat': 37.7749, 'lng': -122.4194, 'alt': 10},
        'sampling_rate': 30
    }
    
    sensor_id = collector.register_sensor(sensor_info)
    print(f"센서 등록 완료: {sensor_id}")
    
    # 잠시 대기
    time.sleep(10)
    
    # 센서 데이터 조회
    data = collector.get_sensor_data(sensor_id, limit=10)
    print(f"센서 데이터: {len(data)}개")
    
    # 센서 통계 조회
    stats = collector.get_sensor_statistics(sensor_id, '24h')
    print(f"센서 통계: {stats}") 