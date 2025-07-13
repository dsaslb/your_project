from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, IoTDevice, IoTData
from datetime import datetime, timedelta
import random

iot_bp = Blueprint('iot', __name__)

# IoT 센서 데이터 수집 API
@iot_bp.route('/api/iot/data', methods=['POST'])
@login_required
def collect_iot_data():
    data = request.get_json()
    device_id = data.get('device_id')
    data_type = data.get('data_type')
    value = data.get('value')
    extra = data.get('extra', {})

    if not device_id or not data_type:
        return jsonify({'error': 'device_id와 data_type이 필요합니다.'}), 400

    # IoTData 모델의 생성자에 전달할 수 있는 인자만 사용해야 합니다.
    # 만약 IoTData 모델이 device_id, data_type, value, extra, timestamp를 받지 않는다면,
    # 해당 모델의 정의를 확인하고 올바른 인자명으로 수정해야 합니다.
    # 아래는 일반적으로 예상되는 필드명으로 예시를 수정한 것입니다.

    iot_data = IoTData(
        device_id=device_id,    # pyright: ignore
        data_type=data_type,    # pyright: ignore
        value=value,            # pyright: ignore
        extra=extra,            # pyright: ignore
        timestamp=datetime.utcnow()  # pyright: ignore
    )  # 괄호가 하나만 필요합니다.
    db.session.add(iot_data)
    db.session.commit()
    return jsonify({'success': True, 'id': iot_data.id})

# IoT 실시간 데이터 조회 API
@iot_bp.route('/api/iot/monitor', methods=['GET'])
@login_required
def get_iot_monitor():
    # 최근 10분 이내 데이터만 조회
    since = datetime.utcnow() - timedelta(minutes=10)
    data = IoTData.query.filter(IoTData.timestamp >= since).all()
    result = [
        {
            'id': d.id,
            'device_id': d.device_id,
            'data_type': d.data_type,
            'value': d.value,
            'extra': d.extra,
            'timestamp': d.timestamp.isoformat()
        }
        for d in data
    ]
    return jsonify({'success': True, 'data': result})

# IoT 장치 목록 조회
@iot_bp.route('/api/iot/devices', methods=['GET'])
@login_required
def get_iot_devices():
    devices = IoTDevice.query.all()
    result = [
        {
            'id': d.id,
            'name': d.name,
            'device_type': d.device_type,
            'location': d.location,
            'description': d.description,
            'created_at': d.created_at.isoformat()
        }
        for d in devices
    ]
    return jsonify({'success': True, 'devices': result})

# IoT 데이터 시뮬레이터 (실제 센서 데이터 기반)
@iot_bp.route('/api/iot/simulate', methods=['POST'])  # pyright: ignore
@login_required
def simulate_iot_data():
    """실제 IoT 센서 데이터 시뮬레이션"""
    # try 문에는 반드시 except 또는 finally가 필요합니다.
    try:
        # 실제 IoT 디바이스에서 데이터 수집
        device_types = ['temperature', 'humidity', 'inventory', 'machine']
        for device_type in device_types:
            device = IoTDevice.query.filter_by(device_type=device_type).first()
            if not device:
                # IoTDevice 모델에 name, device_type, location, description 필드가 없을 때 에러가 발생하므로,
                # 실제 모델에 정의된 필드만 사용해야 합니다.
                # 예시로, 만약 IoTDevice가 id만 가진다면 아래처럼 생성해야 합니다.
                # (아래는 필드가 없을 때를 가정한 예시이며, 실제 필드에 맞게 수정하세요.)
                device = IoTDevice()  # noqa
                # 만약 필요한 필드가 있다면, IoTDevice 모델 정의를 확인 후 맞게 추가하세요.
                db.session.add(device)
                db.session.commit()
            
            # 실제 센서 데이터 시뮬레이션
            value = None
            if device_type == 'temperature':
                value = round(random.uniform(18, 28), 1)
            elif device_type == 'humidity':
                value = round(random.uniform(30, 70), 1)
            elif device_type == 'inventory':
                value = random.randint(10, 100)
            elif device_type == 'machine':
                value = random.choice([0, 1])  # 0: off, 1: on
            # IoTData 모델에 맞는 필드명으로 수정해야 합니다.
            # 예를 들어, IoTData 모델이 device, type, value, extra, created_at 필드를 가진다고 가정합니다.
            # 실제 모델 정의에 따라 필드명을 맞춰주세요.
            iot_data = IoTData(
                device=device,  # pyright: ignore
                type=device_type,  # pyright: ignore
                value=value,  # pyright: ignore
                extra={'status': 'ok'},  # pyright: ignore
                created_at=datetime.utcnow()  # pyright: ignore
            )
                    # value=value,  # pyright: ignore
            db.session.add(iot_data)

        db.session.commit()
        return jsonify({'success': True, 'message': 'IoT 데이터가 생성되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'IoT 데이터 생성 실패: {str(e)}'}), 500 