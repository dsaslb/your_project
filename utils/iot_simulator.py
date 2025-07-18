import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import threading
import time
import random
import json
import asyncio
from typing import Optional
form = None  # pyright: ignore
"""
IoT 기기 시뮬레이터
실제 IoT 기기 없이도 테스트할 수 있는 가상 IoT 기기 시스템
"""


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """IoT 기기 타입"""
    TEMPERATURE_SENSOR = "temperature_sensor"
    HUMIDITY_SENSOR = "humidity_sensor"
    LIGHT_SENSOR = "light_sensor"
    NOISE_SENSOR = "noise_sensor"
    WEIGHT_SENSOR = "weight_sensor"
    MOTION_SENSOR = "motion_sensor"
    DOOR_SENSOR = "door_sensor"
    GAS_SENSOR = "gas_sensor"
    SMOKE_SENSOR = "smoke_sensor"
    REFRIGERATOR = "refrigerator"
    OVEN = "oven"
    COOKER = "cooker"
    LIGHT_CONTROLLER = "light_controller"
    VENTILATION = "ventilation"


class DeviceStatus(Enum):
    """기기 상태"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class SensorData:
    """센서 데이터 구조"""
    device_id: str
    device_type: DeviceType
    timestamp: datetime
    value: float
    unit: str
    status: DeviceStatus
    location: str
    metadata: Dict[str, Any] if Dict is not None else None


class IoTDevice:
    """IoT 기기 기본 클래스"""

    def __init__(self,  device_id: str,  device_type: DeviceType,  location: str):
        self.device_id = device_id
        self.device_type = device_type
        self.location = location
        self.status = DeviceStatus.ONLINE
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
                self.status = DeviceStatus.ERROR
                time.sleep(5)

    def _generate_data(self) -> SensorData:
        """데이터 생성 (하위 클래스에서 구현)"""
        raise NotImplementedError

    def _get_interval(self) -> int:
        """데이터 수집 간격 (초)"""
        return 30

    def control(self, action: str, parameters: Dict[str, Any] if Dict is not None else None) -> Dict[str, Any] if Dict is not None else None:
        """기기 제어 (기본 구현)"""
        return {
            'success': False,
            'message': f'기기 {self.device_id}는 제어할 수 없습니다.',
            'action': action,
            'parameters': parameters
        }


class TemperatureSensor(IoTDevice):
    """온도 센서"""

    def __init__(self,  device_id: str,  location: str,  base_temp: float = 20.0):
        super().__init__(device_id,  DeviceType.TEMPERATURE_SENSOR,  location)
        self.base_temp = base_temp
        self.variation = 5.0

    def _generate_data(self) -> SensorData:
        # 현실적인 온도 변화 시뮬레이션
        hour = datetime.now().hour
        if 6 <= hour <= 18:  # 낮 시간대
            temp_variation = random.uniform(-2, 3)
        else:  # 밤 시간대
            temp_variation = random.uniform(-3, 1)

        temperature = self.base_temp + temp_variation + random.uniform(-self.variation, self.variation)

        return SensorData(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.now(),
            value=round(temperature, 1),
            unit="°C",
            status=self.status,
            location=self.location,
            metadata={"base_temp": self.base_temp}
        )

    def _get_interval(self) -> int:
        return 60  # 1분마다


class HumiditySensor(IoTDevice):
    """습도 센서"""

    def __init__(self,  device_id: str,  location: str,  base_humidity: float = 50.0):
        super().__init__(device_id,  DeviceType.HUMIDITY_SENSOR,  location)
        self.base_humidity = base_humidity
        self.variation = 10.0

    def _generate_data(self) -> SensorData:
        # 습도는 온도와 반비례하는 경향
        humidity = self.base_humidity + random.uniform(-self.variation, self.variation)
        humidity = max(20, min(80, humidity))  # 20-80% 범위

        return SensorData(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.now(),
            value=round(humidity, 1),
            unit="%",
            status=self.status,
            location=self.location,
            metadata={"base_humidity": self.base_humidity}
        )

    def _get_interval(self) -> int:
        return 60  # 1분마다


class WeightSensor(IoTDevice):
    """무게 센서 (재고 관리용)"""

    def __init__(self,  device_id: str,  location: str,  initial_weight: float = 100.0):
        super().__init__(device_id,  DeviceType.WEIGHT_SENSOR,  location)
        self.current_weight = initial_weight
        self.initial_weight = initial_weight

    def _generate_data(self) -> SensorData:
        # 재고 감소 시뮬레이션 (시간이 지날수록 감소)
        hours_passed = (datetime.now() - self.last_update).total_seconds() / 3600
        if hours_passed > 1:  # 1시간마다 업데이트
            self.current_weight = max(0, self.current_weight - random.uniform(0, 5))
            self.last_update = datetime.now()

        return SensorData(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.now(),
            value=round(self.current_weight, 2),
            unit="kg",
            status=self.status,
            location=self.location,
            metadata={
                "initial_weight": self.initial_weight,
                "remaining_percentage": round((self.current_weight / self.initial_weight) * 100, 1)
            }
        )

    def _get_interval(self) -> int:
        return 300  # 5분마다


class MotionSensor(IoTDevice):
    """모션 센서"""

    def __init__(self,  device_id: str,  location: str):
        super().__init__(device_id,  DeviceType.MOTION_SENSOR,  location)
        self.motion_detected = False
        self.last_motion = datetime.now()

    def _generate_data(self) -> SensorData:
        # 시간대별 모션 감지 확률
        hour = datetime.now().hour
        if 7 <= hour <= 22:  # 영업 시간
            motion_prob = 0.3
        else:  # 비영업 시간
            motion_prob = 0.05

        if random.random() < motion_prob:
            self.motion_detected = True
            self.last_motion = datetime.now()
        else:
            # 5분 후 모션 해제
            if (datetime.now() - self.last_motion).total_seconds() > 300:
                self.motion_detected = False

        return SensorData(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.now(),
            value=1.0 if self.motion_detected else 0.0,
            unit="boolean",
            status=self.status,
            location=self.location,
            metadata={
                "motion_detected": self.motion_detected,
                "last_motion": self.last_motion.isoformat()
            }
        )

    def _get_interval(self) -> int:
        return 30  # 30초마다


class Refrigerator(IoTDevice):
    """스마트 냉장고"""

    def __init__(self,  device_id: str,  location: str,  target_temp: float = 4.0):
        super().__init__(device_id,  DeviceType.REFRIGERATOR,  location)
        self.target_temp = target_temp
        self.current_temp = target_temp
        self.is_running = True

    def _generate_data(self) -> SensorData:
        # 온도 변화 시뮬레이션
        if self.is_running:
            # 냉장고가 작동 중일 때 온도 변화
            temp_change = random.uniform(-0.5, 0.5)
            self.current_temp = max(-5, min(10, self.current_temp + temp_change))
        else:
            # 냉장고가 꺼져있을 때 온도 상승
            self.current_temp = min(15, self.current_temp + random.uniform(0, 0.2))

        # 온도가 너무 높으면 자동으로 켜기
        if self.current_temp > self.target_temp + 2:
            self.is_running = True

        return SensorData(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.now(),
            value=round(self.current_temp, 1),
            unit="°C",
            status=self.status,
            location=self.location,
            metadata={
                "target_temp": self.target_temp,
                "is_running": self.is_running,
                "compressor_status": "on" if self.is_running else "off"
            }
        )

    def _get_interval(self) -> int:
        return 120  # 2분마다


class LightController(IoTDevice):
    """조명 제어기"""

    def __init__(self,  device_id: str,  location: str):
        super().__init__(device_id,  DeviceType.LIGHT_CONTROLLER,  location)
        self.is_on = False
        self.brightness = 0
        self.color_temp = 4000  # 켈빈

    def _generate_data(self) -> SensorData:
        # 시간대별 조명 상태
        hour = datetime.now().hour
        if 6 <= hour <= 22:  # 영업 시간
            if not self.is_on:
                self.is_on = True
                self.brightness = random.randint(70, 100)
        else:  # 비영업 시간
            if self.is_on:
                self.is_on = False
                self.brightness = 0

        return SensorData(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.now(),
            value=self.brightness,
            unit="%",
            status=self.status,
            location=self.location,
            metadata={
                "is_on": self.is_on,
                "brightness": self.brightness,
                "color_temp": self.color_temp,
                "power_consumption": self.brightness * 0.1  # W
            }
        )

    def _get_interval(self) -> int:
        return 300  # 5분마다


class IoTDeviceManager:
    """IoT 기기 관리자"""

    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}
        self.data_history: List[SensorData] = []
        self.max_history = 10000
        self.callbacks: List[Callable] = []

    def add_device(self,  device: IoTDevice) -> bool:
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
            device.start(self._on_data_received)
        logger.info(f"{len(self.devices)}개 기기 시작됨")

    def stop_all_devices(self):
        """모든 기기 중지"""
        for device in self.devices.values():
            device.stop()
        logger.info("모든 기기 중지됨")

    def get_device_status(self,  device_id: str) -> Optional[Dict[str, Any]]:
        """기기 상태 조회"""
        if device_id not in self.devices:
            return None

        device = self.devices[device_id]
        return {
            "device_id": device.device_id,
            "device_type": device.device_type.value,
            "location": device.location,
            "status": device.status.value,
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

    def get_device_data(self,  device_id: str, limit=100) -> List[Dict[str, Any]]:
        """기기 데이터 조회"""
        device_data = [data for data in self.data_history if data.device_id == device_id]
        result = []
        for data in device_data[-limit:] if device_data is not None else None:
            data_dict = {
                'device_id': data.device_id,
                'device_type': data.device_type.value,
                'timestamp': data.timestamp.isoformat(),
                'value': data.value,
                'unit': data.unit,
                'status': data.status.value,
                'location': data.location,
                'metadata': data.metadata
            }
            result.append(data_dict)
        return result

    def get_latest_data(self) -> List[Dict[str, Any]]:
        """최신 데이터 조회"""
        latest_data = {}
        for data in reversed(self.data_history):
            if data.device_id not in latest_data:
                data_dict = {
                    'device_id': data.device_id,
                    'device_type': data.device_type.value,
                    'timestamp': data.timestamp.isoformat(),
                    'value': data.value,
                    'unit': data.unit,
                    'status': data.status.value,
                    'location': data.location,
                    'metadata': data.metadata
                }
                latest_data[data.device_id] = data_dict
        return list(latest_data.values())

    def add_callback(self,  callback: Callable):
        """데이터 수신 콜백 추가"""
        self.callbacks.append(callback)

    def _on_data_received(self,  data: SensorData):
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
        self.add_device(TemperatureSensor("temp_kitchen",  "주방",  25.0))
        self.add_device(TemperatureSensor("temp_dining",  "매장",  22.0))
        self.add_device(TemperatureSensor("temp_storage",  "창고",  18.0))

        # 습도 센서들
        self.add_device(HumiditySensor("hum_kitchen",  "주방",  60.0))
        self.add_device(HumiditySensor("hum_dining",  "매장",  50.0))

        # 무게 센서들 (재고 관리)
        self.add_device(WeightSensor("weight_meat",  "육류 보관소",  50.0))
        self.add_device(WeightSensor("weight_vegetables",  "채소 보관소",  30.0))
        self.add_device(WeightSensor("weight_dairy",  "유제품 보관소",  20.0))

        # 모션 센서들
        self.add_device(MotionSensor("motion_kitchen",  "주방"))
        self.add_device(MotionSensor("motion_dining",  "매장"))
        self.add_device(MotionSensor("motion_storage",  "창고"))

        # 스마트 기기들
        self.add_device(Refrigerator("fridge_main",  "주방",  4.0))
        self.add_device(Refrigerator("fridge_display",  "매장",  2.0))

        # 조명 제어기들
        self.add_device(LightController("light_kitchen",  "주방"))
        self.add_device(LightController("light_dining",  "매장"))
        self.add_device(LightController("light_storage",  "창고"))

        logger.info("샘플 IoT 기기 생성 완료")


# 전역 IoT 디바이스 매니저 인스턴스
iot_manager = IoTDeviceManager()


def get_iot_manager() -> IoTDeviceManager:
    """IoT 매니저 인스턴스 반환"""
    return iot_manager


def initialize_iot_system():
    """IoT 시스템 초기화"""
    iot_manager.create_sample_devices()
    iot_manager.start_all_devices()
    logger.info("IoT 시스템 초기화 완료")


if __name__ == "__main__":
    # 테스트 실행
    initialize_iot_system()

    try:
        while True:
            time.sleep(10)
            latest_data = iot_manager.get_latest_data()
            print(f"최신 데이터 ({len(latest_data)}개):")
            for data in latest_data[:3] if latest_data is not None else None:  # 처음 3개만 출력
                print(f"  {data['device_id']}: {data['value']} {data['unit']}")
    except KeyboardInterrupt:
        iot_manager.stop_all_devices()
        print("IoT 시스템 종료")
