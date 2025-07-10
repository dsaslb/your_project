"""
IoT Service
IoT 기기 관리, 데이터 수집, 제어 담당 마이크로서비스
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import sqlite3

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 설정
DB_PATH = os.getenv('IOT_DB_PATH', 'iot_service.db')

# IoT 기기 시뮬레이터 (기존 코드 재사용)
class IoTDevice:
    """IoT 기기 기본 클래스"""
    
    def __init__(self, device_id: str, device_type: str, location: str):
        self.device_id = device_id
        self.device_type = device_type
        self.location = location
        self.status = "online"
        self.last_update = datetime.now()
        self.is_running = False
        self.thread = None
        self.callback = None
        
    def start(self, callback=None):
        """기기 시작"""
        if not self.is_running:
            self.is_running = True
            self.callback = callback
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info(f"기기 {self.device_id} 시작됨")
    
    def stop(self):
        """기기 중지"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info(f"기기 {self.device_id} 중지됨")
    
    def _run(self):
        """기기 실행 루프"""
        while self.is_running:
            try:
                data = self._generate_data()
                if self.callback:
                    self.callback(data)
                time.sleep(self._get_interval())
            except Exception as e:
                logger.error(f"기기 {self.device_id} 오류: {e}")
                self.status = "error"
                time.sleep(5)
    
    def _generate_data(self) -> Dict[str, Any]:
        """데이터 생성 (기본 구현)"""
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'timestamp': datetime.now().isoformat(),
            'value': 0.0,
            'unit': '',
            'status': self.status,
            'location': self.location,
            'metadata': {}
        }
    
    def _get_interval(self) -> int:
        """데이터 수집 간격 (초)"""
        return 30
    
    def control(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """기기 제어 (기본 구현)"""
        return {
            'success': False,
            'message': f'기기 {self.device_id}는 제어할 수 없습니다.',
            'action': action,
            'parameters': parameters
        }

class TemperatureSensor(IoTDevice):
    """온도 센서"""
    
    def __init__(self, device_id: str, location: str, base_temp: float = 20.0):
        super().__init__(device_id, "temperature_sensor", location)
        self.base_temp = base_temp
        self.variation = 5.0
    
    def _generate_data(self) -> Dict[str, Any]:
        import random
        # 현실적인 온도 변화 시뮬레이션
        hour = datetime.now().hour
        if 6 <= hour <= 18:  # 낮 시간대
            temp_variation = random.uniform(-2, 3)
        else:  # 밤 시간대
            temp_variation = random.uniform(-3, 1)
        
        temperature = self.base_temp + temp_variation + random.uniform(-self.variation, self.variation)
        
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'timestamp': datetime.now().isoformat(),
            'value': round(temperature, 1),
            'unit': "°C",
            'status': self.status,
            'location': self.location,
            'metadata': {"base_temp": self.base_temp}
        }
    
    def _get_interval(self) -> int:
        return 60  # 1분마다

class IoTDeviceManager:
    """IoT 기기 관리자"""
    
    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}
        self.data_history: List[Dict[str, Any]] = []
        self.max_history = 10000
        self.callbacks: List[Callable] = []
    
    def add_device(self, device: IoTDevice) -> bool:
        """기기 추가"""
        if device.device_id in self.devices:
            logger.warning(f"기기 {device.device_id}가 이미 존재합니다")
            return False
        
        self.devices[device.device_id] = device
        logger.info(f"기기 {device.device_id} 추가됨")
        return True
    
    def remove_device(self, device_id: str) -> bool:
        """기기 제거"""
        if device_id not in self.devices:
            logger.warning(f"기기 {device_id}가 존재하지 않습니다")
            return False
        
        device = self.devices[device_id]
        device.stop()
        del self.devices[device_id]
        logger.info(f"기기 {device_id} 제거됨")
        return True
    
    def start_all_devices(self):
        """모든 기기 시작"""
        for device in self.devices.values():
            device.start(callback=self._on_data_received)
        logger.info(f"{len(self.devices)}개 기기 시작됨")
    
    def stop_all_devices(self):
        """모든 기기 중지"""
        for device in self.devices.values():
            device.stop()
        logger.info("모든 기기 중지됨")
    
    def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """기기 상태 조회"""
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        return {
            "device_id": device.device_id,
            "device_type": device.device_type,
            "location": device.location,
            "status": device.status,
            "is_running": device.is_running,
            "last_update": device.last_update.isoformat()
        }
    
    def get_all_devices_status(self) -> List[Dict[str, Any]]:
        """모든 기기 상태 조회"""
        status_list = []
        for device_id in self.devices.keys():
            status = self.get_device_status(device_id)
            if status is not None:
                status_list.append(status)
        return status_list
    
    def get_device_data(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """기기 데이터 조회"""
        device_data = [data for data in self.data_history if data['device_id'] == device_id]
        return device_data[-limit:]
    
    def get_latest_data(self) -> List[Dict[str, Any]]:
        """최신 데이터 조회"""
        latest_data = {}
        for data in reversed(self.data_history):
            if data['device_id'] not in latest_data:
                latest_data[data['device_id']] = data
        return list(latest_data.values())
    
    def add_callback(self, callback):
        """데이터 수신 콜백 추가"""
        self.callbacks.append(callback)
    
    def _on_data_received(self, data: Dict[str, Any]):
        """데이터 수신 처리"""
        # 데이터 히스토리에 추가
        self.data_history.append(data)
        
        # 히스토리 크기 제한
        if len(self.data_history) > self.max_history:
            self.data_history = self.data_history[-self.max_history:]
        
        # 콜백 호출
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"콜백 실행 오류: {e}")
    
    def create_sample_devices(self):
        """샘플 기기 생성"""
        # 온도 센서들
        self.add_device(TemperatureSensor("temp_kitchen", "주방", 25.0))
        self.add_device(TemperatureSensor("temp_dining", "매장", 22.0))
        self.add_device(TemperatureSensor("temp_storage", "창고", 18.0))
        
        logger.info("샘플 IoT 기기 생성 완료")

def init_db():
    """데이터베이스 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 기기 데이터 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            device_type TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            status TEXT NOT NULL,
            location TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 기기 상태 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_status (
            device_id TEXT PRIMARY KEY,
            device_type TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL,
            is_running BOOLEAN DEFAULT 0,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("IoT Service 데이터베이스 초기화 완료")

def get_db_connection():
    """데이터베이스 연결"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 전역 IoT 디바이스 매니저 인스턴스
iot_manager = IoTDeviceManager()

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'iot-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/iot/devices', methods=['GET'])
def get_devices():
    """모든 기기 상태 조회"""
    try:
        devices = iot_manager.get_all_devices_status()
        return jsonify({
            'devices': devices,
            'total': len(devices)
        })
    except Exception as e:
        logger.error(f"기기 목록 조회 오류: {e}")
        return jsonify({'error': '기기 목록 조회 중 오류가 발생했습니다'}), 500

@app.route('/api/iot/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """특정 기기 상태 조회"""
    try:
        device = iot_manager.get_device_status(device_id)
        if not device:
            return jsonify({'error': '기기를 찾을 수 없습니다'}), 404
        
        return jsonify(device)
    except Exception as e:
        logger.error(f"기기 조회 오류: {e}")
        return jsonify({'error': '기기 조회 중 오류가 발생했습니다'}), 500

@app.route('/api/iot/devices/<device_id>/data', methods=['GET'])
def get_device_data(device_id):
    """기기 데이터 조회"""
    try:
        limit = request.args.get('limit', 100, type=int)
        data = iot_manager.get_device_data(device_id, limit)
        return jsonify({
            'device_id': device_id,
            'data': data,
            'total': len(data)
        })
    except Exception as e:
        logger.error(f"기기 데이터 조회 오류: {e}")
        return jsonify({'error': '기기 데이터 조회 중 오류가 발생했습니다'}), 500

@app.route('/api/iot/devices/<device_id>/control', methods=['POST'])
def control_device(device_id):
    """기기 제어"""
    try:
        data = request.get_json()
        action = data.get('action')
        parameters = data.get('parameters', {})
        
        if not action:
            return jsonify({'error': '제어 액션이 필요합니다'}), 400
        
        if device_id not in iot_manager.devices:
            return jsonify({'error': '기기를 찾을 수 없습니다'}), 404
        
        device = iot_manager.devices[device_id]
        result = device.control(action, parameters)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"기기 제어 오류: {e}")
        return jsonify({'error': '기기 제어 중 오류가 발생했습니다'}), 500

@app.route('/api/iot/data/latest', methods=['GET'])
def get_latest_data():
    """최신 데이터 조회"""
    try:
        data = iot_manager.get_latest_data()
        return jsonify({
            'data': data,
            'total': len(data)
        })
    except Exception as e:
        logger.error(f"최신 데이터 조회 오류: {e}")
        return jsonify({'error': '최신 데이터 조회 중 오류가 발생했습니다'}), 500

@app.route('/api/iot/analytics', methods=['GET'])
def get_analytics():
    """IoT 분석 데이터"""
    try:
        devices = iot_manager.get_all_devices_status()
        
        # 기본 통계
        total_devices = len(devices)
        online_devices = len([d for d in devices if d['status'] == 'online'])
        offline_devices = len([d for d in devices if d['status'] == 'offline'])
        error_devices = len([d for d in devices if d['status'] == 'error'])
        
        # 기기 타입별 통계
        device_types = {}
        for device in devices:
            device_type = device['device_type']
            if device_type not in device_types:
                device_types[device_type] = 0
            device_types[device_type] += 1
        
        return jsonify({
            'summary': {
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': offline_devices,
                'error_devices': error_devices,
                'online_rate': round((online_devices / total_devices * 100), 2) if total_devices > 0 else 0
            },
            'device_types': device_types,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"IoT 분석 오류: {e}")
        return jsonify({'error': 'IoT 분석 중 오류가 발생했습니다'}), 500

@app.route('/api/iot/alerts', methods=['GET'])
def get_alerts():
    """IoT 알림 조회"""
    try:
        # 임계값 기반 알림 생성
        alerts = []
        latest_data = iot_manager.get_latest_data()
        
        for data in latest_data:
            if data['device_type'] == 'temperature_sensor':
                if data['value'] > 30:  # 온도가 30도 이상
                    alerts.append({
                        'device_id': data['device_id'],
                        'type': 'high_temperature',
                        'message': f"온도가 높습니다: {data['value']}°C",
                        'severity': 'warning',
                        'timestamp': data['timestamp']
                    })
                elif data['value'] < 10:  # 온도가 10도 이하
                    alerts.append({
                        'device_id': data['device_id'],
                        'type': 'low_temperature',
                        'message': f"온도가 낮습니다: {data['value']}°C",
                        'severity': 'warning',
                        'timestamp': data['timestamp']
                    })
        
        return jsonify({
            'alerts': alerts,
            'total': len(alerts)
        })
    except Exception as e:
        logger.error(f"IoT 알림 조회 오류: {e}")
        return jsonify({'error': 'IoT 알림 조회 중 오류가 발생했습니다'}), 500

if __name__ == '__main__':
    init_db()
    iot_manager.create_sample_devices()
    iot_manager.start_all_devices()
    
    port = int(os.getenv('IOT_SERVICE_PORT', 5006))
    app.run(host='0.0.0.0', port=port, debug=True) 