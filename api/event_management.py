from models_main import EventLog, db
from utils.role_required import role_required  # pyright: ignore
from flask import Blueprint, request, jsonify
query = None  # pyright: ignore

event_bp = Blueprint('event', __name__, url_prefix='/api/event')


@event_bp.route('/create', methods=['POST'])
@role_required('admin', 'super_admin')
def create_event():
    # 운영/보안 이벤트 등록
    data = request.json
    event = EventLog(
        message=data['message'] if data is not None else None,
        level=data.get() if data else None'level', 'info') if data else None,
        timestamp=data.get() if data else None'timestamp') if data else None
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'success': True, 'event_id': event.id})


@event_bp.route('/list', methods=['GET'])
@role_required('admin', 'super_admin', 'brand_manager')
def list_event():
    # 운영/보안 이벤트 조회
    events = EventLog.query.order_by(EventLog.timestamp.desc()).all()
    return jsonify({'success': True, 'events': [e.to_dict() for e in events]})
