"""
IoT 디바이스 관리 시스템
디바이스 등록, 인증, 상태 모니터링, 원격 제어를 포함한 완전한 IoT 디바이스 관리 플랫폼
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
import hashlib
import hmac
import base64
import secrets
import sqlite3
from pathlib import Path
import requests
from requests.exceptions import RequestException
import paho.mqtt.client as mqtt
import ssl
import socket
import struct
import pickle

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """디바이스 타입"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"
    CAMERA = "camera"
    CONTROLLER = "controller"
    SMART_DEVICE = "smart_device"

class DeviceStatus(Enum):
    """디바이스 상태"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UPDATING = "updating"

class ConnectionType(Enum):
    """연결 타입"""
    MQTT = "mqtt"
    HTTP = "http"
    WEBSOCKET = "websocket"
    COAP = "coap"
    LORA = "lora"
    ZIGBEE = "zigbee"

class SecurityLevel(Enum):
    """보안 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Device:
    """IoT 디바이스"""
    device_id: str
    name: str
    device_type: DeviceType
    model: str
    manufacturer: str
    firmware_version: str
    hardware_version: str
    ip_address: str
    mac_address: str
    location: Dict[str, float]  # lat, lng, alt
    status: DeviceStatus
    connection_type: ConnectionType
    security_level: SecurityLevel
    capabilities: List[str]
    configuration: Dict[str, Any]
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

@dataclass
class DeviceAuthentication:
    """디바이스 인증"""
    device_id: str
    api_key: str
    certificate: str
    token: str
    token_expires: datetime
    permissions: List[str]
    created_at: datetime

@dataclass
class DeviceCommand:
    """디바이스 명령"""
    command_id: str
    device_id: str
    command_type: str
    parameters: Dict[str, Any]
    priority: int
    timeout: int
    status: str
    result: Any
    created_at: datetime
    executed_at: datetime = None

@dataclass
class DeviceTelemetry:
    """디바이스 원격 측정"""
    telemetry_id: str
    device_id: str
    timestamp: datetime
    data: Dict[str, Any]
    quality: float
    location: Dict[str, float] = None

class IoTDeviceManager:
    """IoT 디바이스 관리 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.devices: Dict[str, Device] = {}
        self.authentications: Dict[str, DeviceAuthentication] = {}
        self.commands: Dict[str, DeviceCommand] = {}
        self.telemetry_data: Dict[str, List[DeviceTelemetry]] = {}
        self.device_handlers: Dict[str, Callable] = {}
        
        # MQTT 클라이언트
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # WebSocket 연결
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # 명령 큐
        self.command_queue = asyncio.Queue()
        
        # 모니터링 스레드
        self.monitoring_thread = None
        self.is_running = False
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './iot_devices.db'))
        self._init_database()
        
        # MQTT 초기화
        self._init_mqtt()
        
        logger.info("IoT 디바이스 관리 시스템 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 디바이스 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    name TEXT,
                    device_type TEXT,
                    model TEXT,
                    manufacturer TEXT,
                    firmware_version TEXT,
                    hardware_version TEXT,
                    ip_address TEXT,
                    mac_address TEXT,
                    location TEXT,
                    status TEXT,
                    connection_type TEXT,
                    security_level TEXT,
                    capabilities TEXT,
                    configuration TEXT,
                    last_seen TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 인증 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_authentications (
                    device_id TEXT PRIMARY KEY,
                    api_key TEXT,
                    certificate TEXT,
                    token TEXT,
                    token_expires TEXT,
                    permissions TEXT,
                    created_at TEXT,
                    FOREIGN KEY (device_id) REFERENCES devices (device_id)
                )
            ''')
            
            # 명령 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_commands (
                    command_id TEXT PRIMARY KEY,
                    device_id TEXT,
                    command_type TEXT,
                    parameters TEXT,
                    priority INTEGER,
                    timeout INTEGER,
                    status TEXT,
                    result TEXT,
                    created_at TEXT,
                    executed_at TEXT,
                    FOREIGN KEY (device_id) REFERENCES devices (device_id)
                )
            ''')
            
            # 원격 측정 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_telemetry (
                    telemetry_id TEXT PRIMARY KEY,
                    device_id TEXT,
                    timestamp TEXT,
                    data TEXT,
                    quality REAL,
                    location TEXT,
                    FOREIGN KEY (device_id) REFERENCES devices (device_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("IoT 디바이스 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _init_mqtt(self):
        """MQTT 클라이언트 초기화"""
        try:
            mqtt_config = self.config.get('mqtt', {})
            
            self.mqtt_client = mqtt.Client(
                client_id=f"iot_manager_{uuid.uuid4().hex[:8]}",
                clean_session=True
            )
            
            # 콜백 설정
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_message = self._on_mqtt_message
            
            # TLS 설정 (필요한 경우)
            if mqtt_config.get('use_tls', False):
                self.mqtt_client.tls_set(
                    ca_certs=mqtt_config.get('ca_cert'),
                    certfile=mqtt_config.get('client_cert'),
                    keyfile=mqtt_config.get('client_key'),
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2
                )
            
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
                
                # 디바이스 토픽 구독
                client.subscribe("devices/+/status")
                client.subscribe("devices/+/telemetry")
                client.subscribe("devices/+/response")
                
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
                device_id = parts[1]
                message_type = parts[2]
                
                if message_type == 'status':
                    self._handle_device_status(device_id, payload)
                elif message_type == 'telemetry':
                    self._handle_device_telemetry(device_id, payload)
                elif message_type == 'response':
                    self._handle_device_response(device_id, payload)
                    
        except Exception as e:
            logger.error(f"MQTT 메시지 처리 오류: {e}")
    
    def register_device(self, device_info: Dict[str, Any]) -> str:
        """디바이스 등록"""
        try:
            device_id = str(uuid.uuid4())
            
            device = Device(
                device_id=device_id,
                name=device_info['name'],
                device_type=DeviceType(device_info['device_type']),
                model=device_info['model'],
                manufacturer=device_info['manufacturer'],
                firmware_version=device_info.get('firmware_version', '1.0.0'),
                hardware_version=device_info.get('hardware_version', '1.0.0'),
                ip_address=device_info.get('ip_address', ''),
                mac_address=device_info.get('mac_address', ''),
                location=device_info.get('location', {'lat': 0, 'lng': 0, 'alt': 0}),
                status=DeviceStatus.OFFLINE,
                connection_type=ConnectionType(device_info.get('connection_type', 'mqtt')),
                security_level=SecurityLevel(device_info.get('security_level', 'medium')),
                capabilities=device_info.get('capabilities', []),
                configuration=device_info.get('configuration', {}),
                last_seen=datetime.now(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.devices[device_id] = device
            
            # 인증 정보 생성
            auth = self._create_device_authentication(device_id)
            self.authentications[device_id] = auth
            
            # 데이터베이스에 저장
            self._save_device_to_db(device)
            self._save_authentication_to_db(auth)
            
            logger.info(f"디바이스 등록 완료: {device_id}")
            return device_id
            
        except Exception as e:
            logger.error(f"디바이스 등록 오류: {e}")
            raise
    
    def _create_device_authentication(self, device_id: str) -> DeviceAuthentication:
        """디바이스 인증 정보 생성"""
        try:
            # API 키 생성
            api_key = secrets.token_urlsafe(32)
            
            # 인증서 생성 (간단한 예시)
            certificate = f"cert_{device_id}_{secrets.token_hex(16)}"
            
            # 토큰 생성
            token = secrets.token_urlsafe(32)
            token_expires = datetime.now() + timedelta(days=30)
            
            auth = DeviceAuthentication(
                device_id=device_id,
                api_key=api_key,
                certificate=certificate,
                token=token,
                token_expires=token_expires,
                permissions=['read', 'write', 'control'],
                created_at=datetime.now()
            )
            
            return auth
            
        except Exception as e:
            logger.error(f"인증 정보 생성 오류: {e}")
            raise
    
    def authenticate_device(self, device_id: str, api_key: str) -> bool:
        """디바이스 인증"""
        try:
            auth = self.authentications.get(device_id)
            if not auth:
                return False
            
            if auth.api_key != api_key:
                return False
            
            # 토큰 만료 확인
            if datetime.now() > auth.token_expires:
                return False
            
            # 디바이스 상태 업데이트
            if device_id in self.devices:
                self.devices[device_id].status = DeviceStatus.ONLINE
                self.devices[device_id].last_seen = datetime.now()
                self.devices[device_id].updated_at = datetime.now()
                self._save_device_to_db(self.devices[device_id])
            
            logger.info(f"디바이스 인증 성공: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"디바이스 인증 오류: {e}")
            return False
    
    def send_command(self, device_id: str, command_type: str, 
                    parameters: Dict[str, Any], priority: int = 1, 
                    timeout: int = 30) -> str:
        """디바이스 명령 전송"""
        try:
            if device_id not in self.devices:
                raise ValueError(f"디바이스를 찾을 수 없습니다: {device_id}")
            
            command_id = str(uuid.uuid4())
            
            command = DeviceCommand(
                command_id=command_id,
                device_id=device_id,
                command_type=command_type,
                parameters=parameters,
                priority=priority,
                timeout=timeout,
                status="pending",
                result=None,
                created_at=datetime.now()
            )
            
            self.commands[command_id] = command
            self._save_command_to_db(command)
            
            # 명령 전송
            self._send_command_to_device(device_id, command)
            
            logger.info(f"디바이스 명령 전송: {command_id}")
            return command_id
            
        except Exception as e:
            logger.error(f"디바이스 명령 전송 오류: {e}")
            raise
    
    def _send_command_to_device(self, device_id: str, command: DeviceCommand):
        """디바이스로 명령 전송"""
        try:
            device = self.devices[device_id]
            
            if device.connection_type == ConnectionType.MQTT:
                # MQTT로 명령 전송
                topic = f"devices/{device_id}/command"
                payload = {
                    'command_id': command.command_id,
                    'command_type': command.command_type,
                    'parameters': command.parameters,
                    'priority': command.priority,
                    'timeout': command.timeout
                }
                
                if self.mqtt_connected:
                    self.mqtt_client.publish(topic, json.dumps(payload))
                    
            elif device.connection_type == ConnectionType.HTTP:
                # HTTP로 명령 전송
                asyncio.create_task(self._send_http_command(device_id, command))
                
            elif device.connection_type == ConnectionType.WEBSOCKET:
                # WebSocket으로 명령 전송
                asyncio.create_task(self._send_websocket_command(device_id, command))
                
        except Exception as e:
            logger.error(f"디바이스 명령 전송 오류: {e}")
    
    async def _send_http_command(self, device_id: str, command: DeviceCommand):
        """HTTP 명령 전송"""
        try:
            device = self.devices[device_id]
            auth = self.authentications[device_id]
            
            url = f"http://{device.ip_address}/api/command"
            headers = {
                'Authorization': f'Bearer {auth.token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'command_id': command.command_id,
                'command_type': command.command_type,
                'parameters': command.parameters
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        command.status = "completed"
                        command.result = result
                        command.executed_at = datetime.now()
                    else:
                        command.status = "failed"
                        command.result = f"HTTP {response.status}"
                    
                    self._save_command_to_db(command)
                    
        except Exception as e:
            logger.error(f"HTTP 명령 전송 오류: {e}")
            command.status = "failed"
            command.result = str(e)
            self._save_command_to_db(command)
    
    async def _send_websocket_command(self, device_id: str, command: DeviceCommand):
        """WebSocket 명령 전송"""
        try:
            if device_id in self.websocket_connections:
                websocket = self.websocket_connections[device_id]
                
                payload = {
                    'type': 'command',
                    'command_id': command.command_id,
                    'command_type': command.command_type,
                    'parameters': command.parameters
                }
                
                await websocket.send(json.dumps(payload))
                
        except Exception as e:
            logger.error(f"WebSocket 명령 전송 오류: {e}")
    
    def _handle_device_status(self, device_id: str, payload: str):
        """디바이스 상태 처리"""
        try:
            status_data = json.loads(payload)
            
            if device_id in self.devices:
                device = self.devices[device_id]
                device.status = DeviceStatus(status_data.get('status', 'offline'))
                device.last_seen = datetime.now()
                device.updated_at = datetime.now()
                
                # IP 주소 업데이트
                if 'ip_address' in status_data:
                    device.ip_address = status_data['ip_address']
                
                self._save_device_to_db(device)
                
                logger.info(f"디바이스 상태 업데이트: {device_id} - {device.status.value}")
                
        except Exception as e:
            logger.error(f"디바이스 상태 처리 오류: {e}")
    
    def _handle_device_telemetry(self, device_id: str, payload: str):
        """디바이스 원격 측정 처리"""
        try:
            telemetry_data = json.loads(payload)
            
            telemetry = DeviceTelemetry(
                telemetry_id=str(uuid.uuid4()),
                device_id=device_id,
                timestamp=datetime.now(),
                data=telemetry_data.get('data', {}),
                quality=telemetry_data.get('quality', 1.0),
                location=telemetry_data.get('location')
            )
            
            if device_id not in self.telemetry_data:
                self.telemetry_data[device_id] = []
            
            self.telemetry_data[device_id].append(telemetry)
            
            # 최근 1000개만 유지
            if len(self.telemetry_data[device_id]) > 1000:
                self.telemetry_data[device_id] = self.telemetry_data[device_id][-1000:]
            
            # 데이터베이스에 저장
            self._save_telemetry_to_db(telemetry)
            
            logger.debug(f"원격 측정 데이터 수신: {device_id}")
            
        except Exception as e:
            logger.error(f"원격 측정 처리 오류: {e}")
    
    def _handle_device_response(self, device_id: str, payload: str):
        """디바이스 응답 처리"""
        try:
            response_data = json.loads(payload)
            command_id = response_data.get('command_id')
            
            if command_id in self.commands:
                command = self.commands[command_id]
                command.status = "completed"
                command.result = response_data.get('result')
                command.executed_at = datetime.now()
                
                self._save_command_to_db(command)
                
                logger.info(f"디바이스 응답 수신: {command_id}")
                
        except Exception as e:
            logger.error(f"디바이스 응답 처리 오류: {e}")
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """디바이스 정보 조회"""
        try:
            device = self.devices.get(device_id)
            if not device:
                return None
            
            auth = self.authentications.get(device_id)
            
            return {
                'device_id': device.device_id,
                'name': device.name,
                'device_type': device.device_type.value,
                'model': device.model,
                'manufacturer': device.manufacturer,
                'firmware_version': device.firmware_version,
                'hardware_version': device.hardware_version,
                'ip_address': device.ip_address,
                'mac_address': device.mac_address,
                'location': device.location,
                'status': device.status.value,
                'connection_type': device.connection_type.value,
                'security_level': device.security_level.value,
                'capabilities': device.capabilities,
                'configuration': device.configuration,
                'last_seen': device.last_seen.isoformat(),
                'created_at': device.created_at.isoformat(),
                'updated_at': device.updated_at.isoformat(),
                'api_key': auth.api_key if auth else None,
                'token': auth.token if auth else None,
                'token_expires': auth.token_expires.isoformat() if auth else None
            }
            
        except Exception as e:
            logger.error(f"디바이스 정보 조회 오류: {e}")
            return None
    
    def get_device_telemetry(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """디바이스 원격 측정 데이터 조회"""
        try:
            telemetry_list = self.telemetry_data.get(device_id, [])
            
            # 최신 데이터부터 정렬
            telemetry_list.sort(key=lambda x: x.timestamp, reverse=True)
            
            result = []
            for telemetry in telemetry_list[:limit]:
                result.append({
                    'telemetry_id': telemetry.telemetry_id,
                    'device_id': telemetry.device_id,
                    'timestamp': telemetry.timestamp.isoformat(),
                    'data': telemetry.data,
                    'quality': telemetry.quality,
                    'location': telemetry.location
                })
            
            return result
            
        except Exception as e:
            logger.error(f"원격 측정 데이터 조회 오류: {e}")
            return []
    
    def get_device_commands(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """디바이스 명령 내역 조회"""
        try:
            device_commands = [cmd for cmd in self.commands.values() if cmd.device_id == device_id]
            
            # 최신 명령부터 정렬
            device_commands.sort(key=lambda x: x.created_at, reverse=True)
            
            result = []
            for command in device_commands[:limit]:
                result.append({
                    'command_id': command.command_id,
                    'device_id': command.device_id,
                    'command_type': command.command_type,
                    'parameters': command.parameters,
                    'priority': command.priority,
                    'timeout': command.timeout,
                    'status': command.status,
                    'result': command.result,
                    'created_at': command.created_at.isoformat(),
                    'executed_at': command.executed_at.isoformat() if command.executed_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"디바이스 명령 내역 조회 오류: {e}")
            return []
    
    def update_device_configuration(self, device_id: str, configuration: Dict[str, Any]) -> bool:
        """디바이스 설정 업데이트"""
        try:
            if device_id not in self.devices:
                return False
            
            device = self.devices[device_id]
            device.configuration.update(configuration)
            device.updated_at = datetime.now()
            
            self._save_device_to_db(device)
            
            logger.info(f"디바이스 설정 업데이트: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"디바이스 설정 업데이트 오류: {e}")
            return False
    
    def _save_device_to_db(self, device: Device):
        """디바이스를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO devices 
                (device_id, name, device_type, model, manufacturer, firmware_version, hardware_version,
                 ip_address, mac_address, location, status, connection_type, security_level,
                 capabilities, configuration, last_seen, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device.device_id,
                device.name,
                device.device_type.value,
                device.model,
                device.manufacturer,
                device.firmware_version,
                device.hardware_version,
                device.ip_address,
                device.mac_address,
                json.dumps(device.location),
                device.status.value,
                device.connection_type.value,
                device.security_level.value,
                json.dumps(device.capabilities),
                json.dumps(device.configuration),
                device.last_seen.isoformat(),
                device.created_at.isoformat(),
                device.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"디바이스 데이터베이스 저장 오류: {e}")
    
    def _save_authentication_to_db(self, auth: DeviceAuthentication):
        """인증 정보를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO device_authentications 
                (device_id, api_key, certificate, token, token_expires, permissions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                auth.device_id,
                auth.api_key,
                auth.certificate,
                auth.token,
                auth.token_expires.isoformat(),
                json.dumps(auth.permissions),
                auth.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"인증 정보 데이터베이스 저장 오류: {e}")
    
    def _save_command_to_db(self, command: DeviceCommand):
        """명령을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO device_commands 
                (command_id, device_id, command_type, parameters, priority, timeout, status, result, created_at, executed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                command.command_id,
                command.device_id,
                command.command_type,
                json.dumps(command.parameters),
                command.priority,
                command.timeout,
                command.status,
                json.dumps(command.result) if command.result else None,
                command.created_at.isoformat(),
                command.executed_at.isoformat() if command.executed_at else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"명령 데이터베이스 저장 오류: {e}")
    
    def _save_telemetry_to_db(self, telemetry: DeviceTelemetry):
        """원격 측정을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO device_telemetry 
                (telemetry_id, device_id, timestamp, data, quality, location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                telemetry.telemetry_id,
                telemetry.device_id,
                telemetry.timestamp.isoformat(),
                json.dumps(telemetry.data),
                telemetry.quality,
                json.dumps(telemetry.location) if telemetry.location else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"원격 측정 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            logger.info("IoT 디바이스 관리 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './iot_devices.db',
        'mqtt': {
            'host': 'localhost',
            'port': 1883,
            'keepalive': 60,
            'use_tls': False
        }
    }
    
    # IoT 디바이스 관리자 생성
    device_manager = IoTDeviceManager(config)
    
    # 디바이스 등록
    device_info = {
        'name': 'Temperature Sensor 1',
        'device_type': 'sensor',
        'model': 'TEMP-001',
        'manufacturer': 'IoT Corp',
        'firmware_version': '1.2.0',
        'hardware_version': '1.0.0',
        'ip_address': '192.168.1.100',
        'mac_address': '00:11:22:33:44:55',
        'location': {'lat': 37.7749, 'lng': -122.4194, 'alt': 10},
        'connection_type': 'mqtt',
        'security_level': 'medium',
        'capabilities': ['temperature', 'humidity'],
        'configuration': {'sampling_rate': 60}
    }
    
    device_id = device_manager.register_device(device_info)
    print(f"디바이스 등록 완료: {device_id}")
    
    # 디바이스 정보 조회
    device_info = device_manager.get_device_info(device_id)
    print(f"디바이스 정보: {device_info}")
    
    # 명령 전송
    command_id = device_manager.send_command(
        device_id=device_id,
        command_type='read_sensor',
        parameters={'sensor': 'temperature'},
        priority=1
    )
    print(f"명령 전송: {command_id}")
    
    # 잠시 대기
    time.sleep(5)
    
    # 명령 내역 조회
    commands = device_manager.get_device_commands(device_id)
    print(f"명령 내역: {commands}") 