"""
📱 모바일 전용 API 블루프린트

모바일 앱을 위한 JWT 인증, 출퇴근, 재고 조사, 발주 등의 API 엔드포인트
CQRS 라이트 아키텍처 적용: 쓰기와 읽기 분리, 실시간 이벤트 방송
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone, timedelta
from werkzeug.security import check_password_hash
import jwt
import os
from functools import wraps

from extensions import db, socketio
from models import User, Schedule, Order
from utils.idempotency import require_idempotency_key
from utils.events import emit_event

# 모바일 API 블루프린트 생성
mobile_bp = Blueprint("mobile_api", __name__, url_prefix="/api/mobile")

# JWT 설정
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
ALG = "HS256"
EXP_MIN = 60 * 24  # 24시간

def token_for(uid, industry_id=None, brand_id=None, branch_id=None):
    """사용자 ID와 테넌트 정보로 JWT 토큰 생성"""
    payload = {
        "sub": uid, 
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXP_MIN)
    }
    
    # 테넌트 스코프 정보 추가
    if industry_id:
        payload["industry_id"] = industry_id
    if brand_id:
        payload["brand_id"] = brand_id
    if branch_id:
        payload["branch_id"] = branch_id
    
    return jwt.encode(payload, JWT_SECRET, algorithm=ALG)

def auth_required(f):
    """JWT 인증 데코레이터 - 테넌트 스코프 검증 포함"""
    @wraps(f)
    def wrap(*a, **kw):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "no token"}), 401
        
        try:
            payload = jwt.decode(auth.split()[1], JWT_SECRET, algorithms=[ALG])
        except Exception:
            return jsonify({"error": "bad token"}), 401
        
        request.user_id = int(payload["sub"])
        
        # 테넌트 스코프 정보 저장
        request.industry_id = payload.get("industry_id")
        request.brand_id = payload.get("brand_id")
        request.branch_id = payload.get("branch_id")
        
        return f(*a, **kw)
    return wrap

def validate_tenant_scope(required_scope=None):
    """테넌트 스코프 검증 데코레이터"""
    def decorator(f):
        @wraps(f)
        def wrap(*a, **kw):
            if required_scope == "branch" and not request.branch_id:
                return jsonify({"error": "branch_id required"}), 400
            if required_scope == "brand" and not request.brand_id:
                return jsonify({"error": "brand_id required"}), 400
            if required_scope == "industry" and not request.industry_id:
                return jsonify({"error": "industry_id required"}), 400
            return f(*a, **kw)
        return wrap
    return decorator

def log_event(event_type, resource_type=None, resource_id=None, old_values=None, new_values=None, changes=None):
    """이벤트 로깅 헬퍼 함수"""
    try:
        from models.event_log import EventLog
        
        # 디바이스 ID 추출 (헤더에서)
        device_id = request.headers.get('X-Device-ID')
        
        EventLog.log_event(
            event_type=event_type,
            user_id=request.user_id,
            user_role=getattr(request, 'user_role', None),
            industry_id=request.industry_id,
            brand_id=request.brand_id,
            branch_id=request.branch_id,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            device_id=device_id
        )
    except Exception as e:
        print(f"이벤트 로깅 실패: {e}")

@mobile_bp.post("/login")
def login():
    """모바일 로그인"""
    d = request.get_json() or {}
    u = User.query.filter_by(username=d.get("username")).first()
    
    if not u or not check_password_hash(u.password_hash, d.get("password", "")):
        return jsonify({"error": "invalid credentials"}), 401
    
    # 사용자의 테넌트 정보 조회 (실제 구현에서는 User 모델에 이 정보가 있어야 함)
    industry_id = getattr(u, 'industry_id', None)
    brand_id = getattr(u, 'brand_id', None)
    branch_id = getattr(u, 'branch_id', None)
    
    # 로그인 이벤트 기록
    log_event("user:login", "user", u.id, new_values={"username": u.username})
    
    return jsonify({
        "token": token_for(u.id, industry_id, brand_id, branch_id),
        "user": {
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "industry_id": industry_id,
            "brand_id": brand_id,
            "branch_id": branch_id
        }
    })

@mobile_bp.post("/push/register")
@auth_required
def push_register():
    """Expo 푸시 토큰 등록"""
    token = (request.get_json() or {}).get("expo_push_token")
    if not token:
        return jsonify({"error": "no token"}), 400
    
    u = User.query.get(request.user_id)
    if hasattr(u, 'expo_push_token'):
        old_token = u.expo_push_token
        u.expo_push_token = token
        db.session.commit()
        
        # 푸시 토큰 변경 이벤트 기록
        log_event("user:push_token_update", "user", u.id, 
                 old_values={"expo_push_token": old_token}, 
                 new_values={"expo_push_token": token})
    
    return jsonify({"ok": True})

@mobile_bp.post("/attendance/clock")
@auth_required
@validate_tenant_scope("branch")
@require_idempotency_key()
def attendance_clock():
    """출퇴근 체크 - 멱등성 키 적용, 서버 시간 기준"""
    d = request.get_json() or {}
    
    # 서버 시간 기준 (단말 시간 불신)
    server_ts = datetime.now(timezone.utc)
    
    try:
        from models import MobileAttendance
        
        # 기존 출퇴근 기록 확인 (같은 날 같은 타입)
        existing_attendance = MobileAttendance.query.filter_by(
            user_id=request.user_id,
            type=d.get("type"),
            branch_id=request.branch_id,
            date=server_ts.date()
        ).first()
        
        old_values = None
        if existing_attendance:
            old_values = {
                "id": existing_attendance.id,
                "timestamp": existing_attendance.timestamp.isoformat() if existing_attendance.timestamp else None,
                "latitude": existing_attendance.latitude,
                "longitude": existing_attendance.longitude
            }
        
        attendance = MobileAttendance(
            user_id=request.user_id,
            type=d.get("type"),  # 'in' 또는 'out'
            timestamp=server_ts,
            latitude=d.get("lat"),
            longitude=d.get("lng"),
            qr_code=d.get("qr"),
            branch_id=request.branch_id,  # 테넌트 스코프
            brand_id=request.brand_id,
            industry_id=request.industry_id
        )
        db.session.add(attendance)
        db.session.commit()
        
        # 성공적으로 저장된 데이터로 payload 구성
        payload = {
            "id": attendance.id,
            "user_id": attendance.user_id,
            "type": attendance.type,
            "server_timestamp": server_ts.isoformat(),
            "lat": attendance.latitude,
            "lng": attendance.longitude,
            "qr": attendance.qr_code,
            "branch_id": attendance.branch_id,
            "brand_id": attendance.brand_id,
            "industry_id": attendance.industry_id
        }
        
        # 이벤트 방송 (지점별 룸)
        emit_event(
            "attendance:update", 
            payload, 
            room=f"branch:{attendance.branch_id}"
        )
        
        # 출퇴근 이벤트 로깅
        new_values = {
            "id": attendance.id,
            "type": attendance.type,
            "timestamp": server_ts.isoformat(),
            "latitude": attendance.latitude,
            "longitude": attendance.longitude,
            "qr_code": attendance.qr_code
        }
        
        log_event("attendance:update", "attendance", attendance.id, 
                 old_values=old_values, new_values=new_values)
        
        return jsonify({"ok": True, **payload})
        
    except Exception as e:
        db.session.rollback()
        print(f"출퇴근 기록 저장 실패: {e}")
        return jsonify({"error": "attendance save failed"}), 500

@mobile_bp.post("/inventory/check")
@auth_required
@validate_tenant_scope("branch")
@require_idempotency_key()
def inventory_check():
    """재고 조사 - 멱등성 키 적용"""
    d = request.get_json() or {}
    
    # 서버 시간 기준
    server_ts = datetime.now(timezone.utc)
    
    try:
        from models import InventoryLog
        
        # 기존 재고 기록 확인
        existing_log = InventoryLog.query.filter_by(
            barcode=d.get("barcode"),
            branch_id=request.branch_id,
            created_at=server_ts.date()
        ).first()
        
        old_values = None
        if existing_log:
            old_values = {
                "id": existing_log.id,
                "qty": existing_log.qty,
                "photo_url": existing_log.photo_url
            }
        
        log = InventoryLog(
            user_id=request.user_id,
            barcode=d.get("barcode"),
            qty=d.get("qty", 0),
            photo_url=d.get("photo_url"),
            branch_id=request.branch_id,
            brand_id=request.brand_id,
            industry_id=request.industry_id,
            created_at=server_ts
        )
        db.session.add(log)
        db.session.commit()
        
        log_data = {
            "id": log.id,
            "barcode": log.barcode,
            "qty": log.qty,
            "user_id": log.user_id,
            "server_timestamp": server_ts.isoformat(),
            "branch_id": log.branch_id,
            "brand_id": log.brand_id,
            "industry_id": log.industry_id
        }
        
        # 이벤트 방송 (지점별 룸)
        emit_event(
            "inventory:update", 
            log_data, 
            room=f"branch:{log.branch_id}"
        )
        
        # 재고 이벤트 로깅
        new_values = {
            "id": log.id,
            "barcode": log.barcode,
            "qty": log.qty,
            "photo_url": log.photo_url
        }
        
        log_event("inventory:update", "inventory", log.id, 
                 old_values=old_values, new_values=new_values)
        
        return jsonify({"ok": True, **log_data})
        
    except Exception as e:
        db.session.rollback()
        print(f"재고 조사 기록 저장 실패: {e}")
        return jsonify({"error": "inventory save failed"}), 500

@mobile_bp.post("/purchase_orders")
@auth_required
@validate_tenant_scope("branch")
@require_idempotency_key()
def create_po():
    """발주 생성 - 멱등성 키 적용"""
    d = request.get_json() or {}
    
    # 서버 시간 기준
    server_ts = datetime.now(timezone.utc)
    
    try:
        from models import MobilePurchaseOrder
        
        po = MobilePurchaseOrder(
            user_id=request.user_id,
            status="requested",
            items=d.get("items", []),
            branch_id=request.branch_id,
            brand_id=request.brand_id,
            industry_id=request.industry_id,
            created_at=server_ts
        )
        db.session.add(po)
        db.session.commit()
        
        po_data = {
            "id": po.id,
            "status": po.status,
            "user_id": po.user_id,
            "server_timestamp": server_ts.isoformat(),
            "branch_id": po.branch_id,
            "brand_id": po.brand_id,
            "industry_id": po.industry_id
        }
        
        # 이벤트 방송 (지점별 룸)
        emit_event(
            "purchase_order:update", 
            po_data, 
            room=f"branch:{po.branch_id}"
        )
        
        # 발주 이벤트 로깅
        new_values = {
            "id": po.id,
            "status": po.status,
            "items": po.items
        }
        
        log_event("purchase_order:create", "purchase_order", po.id, 
                 new_values=new_values)
        
        return jsonify({"ok": True, **po_data})
        
    except Exception as e:
        db.session.rollback()
        print(f"발주 생성 실패: {e}")
        return jsonify({"error": "purchase order creation failed"}), 500

@mobile_bp.get("/schedule")
@auth_required
def my_schedule():
    """내 스케줄 조회 - 읽기 전용, 캐시 최적화 대상"""
    items = Schedule.query.filter_by(user_id=request.user_id).order_by(Schedule.date.asc()).limit(50).all()
    
    return jsonify([{
        "id": s.id,
        "date": s.date.isoformat() if hasattr(s, 'date') else "",
        "title": getattr(s, "title", "")
    } for s in items])

@mobile_bp.post("/orders/update_status")
@auth_required
@validate_tenant_scope("branch")
@require_idempotency_key()
def order_status():
    """주문 상태 변경 - 멱등성 키 적용"""
    d = request.get_json() or {}
    
    try:
        order = Order.query.get(int(d["order_id"]))
        if not order:
            return jsonify({"error": "order not found"}), 404
        
        # 테넌트 스코프 검증
        if hasattr(order, 'branch_id') and order.branch_id != request.branch_id:
            return jsonify({"error": "unauthorized"}), 403
        
        old_status = order.status
        order.status = d["status"]
        db.session.commit()
        
        # 이벤트 방송
        emit_event("order:update", {
            "id": order.id,
            "status": order.status,
            "old_status": old_status,
            "branch_id": request.branch_id,
            "brand_id": request.brand_id,
            "industry_id": request.industry_id
        }, room=f"branch:{request.branch_id}")
        
        # 주문 상태 변경 이벤트 로깅
        log_event("order:status_update", "order", order.id,
                 old_values={"status": old_status}, 
                 new_values={"status": order.status})
        
        return jsonify({"ok": True, "id": order.id, "status": order.status})
        
    except Exception as e:
        db.session.rollback()
        print(f"주문 상태 변경 실패: {e}")
        return jsonify({"error": "order status update failed"}), 500

@mobile_bp.get("/dashboard")
@auth_required
def dashboard():
    """모바일 대시보드 데이터 - 읽기 전용"""
    # 사용자 정보
    user = User.query.get(request.user_id)
    
    # 임시 대시보드 데이터
    dashboard_data = {
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "industry_id": request.industry_id,
            "brand_id": request.brand_id,
            "branch_id": request.branch_id
        },
        "today_schedule": "09:00-18:00",
        "attendance_status": "출근",
        "pending_orders": 5,
        "inventory_alerts": 2,
        "server_time": datetime.now(timezone.utc).isoformat()
    }
    
    return jsonify(dashboard_data)
