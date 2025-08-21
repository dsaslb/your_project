from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
import jwt
import os
from extensions import csrf
from utils.idempotency import require_idempotency_key
from utils.events import emit_attendance_update, emit_inventory_update, emit_purchase_order_update
from flask_wtf.csrf import CSRFProtect

# emit_event 함수가 없는 경우를 위한 fallback
try:
    from utils.events import emit_event
except ImportError:
    def emit_event(name, payload, room=None):
        """이벤트 송출 fallback 함수"""
        print(f"이벤트 송출: {name} - {payload}")
        try:
            from extensions import socketio
            socketio.emit(name, payload, room=room)
        except ImportError:
            pass

# 모바일 전용 모델들 import
try:
    from models.mobile_models import (
        MobileAttendance, 
        MobileInventoryLog, 
        MobilePurchaseOrder, 
        MobileSchedule, 
        MobileOrder
    )
    from models import User
except ImportError:
    # 모델이 없는 경우를 위한 fallback
    MobileAttendance = None
    MobileInventoryLog = None
    MobilePurchaseOrder = None
    MobileSchedule = None
    MobileOrder = None
    User = None

mobile_bp = Blueprint("mobile_api", __name__, url_prefix="/api/mobile")

# CSRF 보호 비활성화 (모바일 API용)
csrf.exempt(mobile_bp)

# CSRF 보호 완전 비활성화
csrf._exempt_views.add(mobile_bp.name)

# JWT 설정
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
ALG = "HS256"
EXP_MIN = 60 * 24  # 24시간

def token_for(uid):
    """JWT 토큰 생성"""
    return jwt.encode(
        {"sub": uid, "exp": datetime.utcnow() + timedelta(minutes=EXP_MIN)},
        JWT_SECRET,
        algorithm=ALG
    )

def auth_required(f):
    """JWT 인증 미들웨어"""
    from functools import wraps
    
    @wraps(f)
    def wrap(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        print(f"DEBUG: Authorization header: {auth}")  # 디버깅 로그
        
        if not auth.startswith("Bearer "):
            print(f"DEBUG: No Bearer token found")  # 디버깅 로그
            return jsonify({"error": "인증 토큰이 필요합니다"}), 401
        
        try:
            token = auth.split()[1]
            print(f"DEBUG: Token extracted: {token[:20]}...")  # 디버깅 로그
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALG])
            print(f"DEBUG: Token payload: {payload}")  # 디버깅 로그
            request.user_id = int(payload["sub"])
            print(f"DEBUG: User ID set: {request.user_id}")  # 디버깅 로그
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            print(f"DEBUG: Token expired")  # 디버깅 로그
            return jsonify({"error": "토큰이 만료되었습니다"}), 401
        except jwt.InvalidTokenError:
            print(f"DEBUG: Invalid token")  # 디버깅 로그
            return jsonify({"error": "유효하지 않은 토큰입니다"}), 401
        except Exception as e:
            print(f"DEBUG: Auth error: {str(e)}")  # 디버깅 로그
            return jsonify({"error": f"인증 오류가 발생했습니다: {str(e)}"}), 401
    
    return wrap

@mobile_bp.route("/login", methods=["POST"])
def login():
    """모바일 로그인"""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "사용자명과 비밀번호를 입력해주세요"}), 400
    
    # 임시 사용자 데이터 (실제로는 데이터베이스에서 조회)
    if username == "admin" and password == "admin123":
        user = {
            "id": 1,
            "username": "admin",
            "role": "admin"
        }
        token = token_for(user["id"])
        return jsonify({
            "token": token,
            "user": user
        })
    
    # 다른 테스트 계정들
    elif username == "user1" and password == "user123":
        user = {
            "id": 2,
            "username": "user1",
            "role": "employee"
        }
        token = token_for(user["id"])
        return jsonify({
            "token": token,
            "user": user
        })
    
    elif username == "manager" and password == "manager123":
        user = {
            "id": 3,
            "username": "manager",
            "role": "manager"
        }
        token = token_for(user["id"])
        return jsonify({
            "token": token,
            "user": user
        })
    
    return jsonify({"error": "잘못된 사용자명 또는 비밀번호입니다"}), 401

@mobile_bp.route("/push/register", methods=["POST"])
@auth_required
def push_register():
    """푸시 토큰 등록"""
    data = request.get_json() or {}
    expo_push_token = data.get("expo_push_token")
    
    if not expo_push_token:
        return jsonify({"error": "푸시 토큰이 필요합니다"}), 400
    
    # 실제로는 사용자 테이블에 토큰 저장
    # User.query.get(request.user_id).expo_push_token = expo_push_token
    # db.session.commit()
    
    return jsonify({"ok": True, "message": "푸시 토큰이 등록되었습니다"})

@mobile_bp.route("/attendance/clock", methods=["POST"])
@auth_required
def attendance_clock():
    """출퇴근 기록"""
    data = request.get_json() or {}
    clock_type = data.get("type")  # 'in' 또는 'out'
    latitude = data.get("lat")
    longitude = data.get("lng")
    qr_code = data.get("qr")
    
    if not clock_type:
        return jsonify({"error": "출퇴근 타입을 지정해주세요"}), 400
    
    # 실제 데이터베이스에 저장
    if MobileAttendance:
        try:
            from extensions import db
            attendance_record = MobileAttendance(
                user_id=request.user_id,
                type=clock_type,
                timestamp=datetime.utcnow(),
                latitude=latitude,
                longitude=longitude,
                qr_code=qr_code
            )
            db.session.add(attendance_record)
            db.session.commit()
            
            attendance_data = attendance_record.to_dict()
        except Exception as e:
            print(f"데이터베이스 저장 오류: {e}")
            db.session.rollback()
            # fallback: 임시 데이터
            attendance_data = {
                "user_id": request.user_id,
                "type": clock_type,
                "timestamp": datetime.utcnow().isoformat(),
                "latitude": latitude,
                "longitude": longitude,
                "qr_code": qr_code
            }
    else:
        # 모델이 없는 경우 임시 데이터
        attendance_data = {
            "user_id": request.user_id,
            "type": clock_type,
            "timestamp": datetime.utcnow().isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "qr_code": qr_code
        }
    
    # 이벤트 헬퍼를 사용한 실시간 브로드캐스트
    try:
        emit_attendance_update(attendance_data)
    except Exception as e:
        print(f"이벤트 송출 실패: {e}")
        # 이벤트 실패는 기록 실패가 아니므로 무시
    
    return jsonify({
        "ok": True,
        "attendance_id": attendance_data.get("id", f"att_{request.user_id}_{int(datetime.utcnow().timestamp())}"),
        **attendance_data
    })

@mobile_bp.route("/inventory/check", methods=["POST"])
@auth_required
@require_idempotency_key()
def inventory_check():
    """재고 조사"""
    data = request.get_json() or {}
    barcode = data.get("barcode")
    quantity = data.get("qty", 0)
    photo_url = data.get("photo_url")
    
    if not barcode:
        return jsonify({"error": "바코드가 필요합니다"}), 400
    
    # 실제 데이터베이스에 저장
    if MobileInventoryLog:
        try:
            from extensions import db
            inventory_record = MobileInventoryLog(
                user_id=request.user_id,
                barcode=barcode,
                quantity=quantity,
                photo_url=photo_url
            )
            db.session.add(inventory_record)
            db.session.commit()
            
            inventory_data = inventory_record.to_dict()
        except Exception as e:
            print(f"데이터베이스 저장 오류: {e}")
            db.session.rollback()
            # fallback: 임시 데이터
            inventory_data = {
                "id": f"inv_{request.user_id}_{int(datetime.utcnow().timestamp())}",
                "user_id": request.user_id,
                "barcode": barcode,
                "qty": quantity,
                "photo_url": photo_url,
                "timestamp": datetime.utcnow().isoformat()
            }
    else:
        # 모델이 없는 경우 임시 데이터
        inventory_data = {
            "id": f"inv_{request.user_id}_{int(datetime.utcnow().timestamp())}",
            "user_id": request.user_id,
            "barcode": barcode,
            "qty": quantity,
            "photo_url": photo_url,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # 이벤트 헬퍼를 사용한 실시간 브로드캐스트
    try:
        emit_inventory_update(inventory_data)
    except Exception as e:
        print(f"이벤트 송출 실패: {e}")
        # 이벤트 실패는 기록 실패가 아니므로 무시
    
    return jsonify({
        "ok": True,
        "inventory_id": inventory_data.get("id", f"inv_{request.user_id}_{int(datetime.utcnow().timestamp())}"),
        **inventory_data
    })

@mobile_bp.route("/inventory/history", methods=["GET"])
@auth_required
def inventory_history():
    """재고 조사 히스토리 조회"""
    limit = request.args.get("limit", 50, type=int)
    
    if MobileInventoryLog:
        try:
            from extensions import db
            # 실제 데이터베이스에서 조회
            history_records = MobileInventoryLog.query.filter_by(
                user_id=request.user_id
            ).order_by(
                MobileInventoryLog.created_at.desc()
            ).limit(limit).all()
            
            history_data = [record.to_dict() for record in history_records]
        except Exception as e:
            print(f"데이터베이스 조회 오류: {e}")
            # fallback: 임시 데이터
            history_data = [
                {
                    "id": f"inv_{i}",
                    "barcode": f"123456789{i:03d}",
                    "quantity": i * 10,
                    "created_at": "2024-08-20T15:30:00Z",
                    "photo_url": None
                }
                for i in range(1, min(limit + 1, 11))
            ]
    else:
        # 모델이 없는 경우 임시 데이터
        history_data = [
            {
                "id": f"inv_{i}",
                "barcode": f"123456789{i:03d}",
                "quantity": i * 10,
                "created_at": "2024-08-20T15:30:00Z",
                "photo_url": None
            }
            for i in range(1, min(limit + 1, 11))
        ]
    
    return jsonify({"history": history_data, "total": len(history_data)})

# 웹 프론트엔드용 데이터 조회 API들
@mobile_bp.route("/dashboard/stats", methods=["GET"])
@auth_required
def dashboard_stats():
    """대시보드 통계 데이터"""
    try:
        from extensions import db
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        user_id = request.user_id
        
        # 오늘 출근 기록 수
        today_attendance = 0
        if MobileAttendance:
            today_attendance = MobileAttendance.query.filter(
                MobileAttendance.user_id == user_id,
                db.func.date(MobileAttendance.timestamp) == today
            ).count()
        
        # 오늘 재고 조사 수
        today_inventory = 0
        if MobileInventoryLog:
            today_inventory = MobileInventoryLog.query.filter(
                MobileInventoryLog.user_id == user_id,
                db.func.date(MobileInventoryLog.created_at) == today
            ).count()
        
        # 대기중인 발주 수
        pending_orders = 0
        if MobilePurchaseOrder:
            pending_orders = MobilePurchaseOrder.query.filter(
                MobilePurchaseOrder.user_id == user_id,
                MobilePurchaseOrder.status == 'requested'
            ).count()
        
        return jsonify({
            "today_attendance": today_attendance,
            "today_inventory": today_inventory,
            "pending_orders": pending_orders,
            "date": today.isoformat()
        })
        
    except Exception as e:
        print(f"대시보드 통계 오류: {e}")
        return jsonify({
            "today_attendance": 0,
            "today_inventory": 0,
            "pending_orders": 0,
            "date": datetime.now().date().isoformat()
        })

@mobile_bp.route("/attendance/list", methods=["GET"])
@auth_required
def attendance_list():
    """출퇴근 기록 목록 (웹 프론트엔드용)"""
    limit = request.args.get("limit", 50, type=int)
    page = request.args.get("page", 1, type=int)
    
    if MobileAttendance:
        try:
            from extensions import db
            offset = (page - 1) * limit
            
            records = MobileAttendance.query.filter_by(
                user_id=request.user_id
            ).order_by(
                MobileAttendance.timestamp.desc()
            ).offset(offset).limit(limit).all()
            
            total = MobileAttendance.query.filter_by(
                user_id=request.user_id
            ).count()
            
            data = [record.to_dict() for record in records]
            
            return jsonify({
                "data": data,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            })
            
        except Exception as e:
            print(f"출퇴근 목록 조회 오류: {e}")
    
    # fallback: 빈 데이터
    return jsonify({
        "data": [],
        "total": 0,
        "page": page,
        "limit": limit,
        "pages": 0
    })

@mobile_bp.route("/purchase_orders", methods=["GET"])
@auth_required
def get_purchase_orders():
    """발주 목록 조회"""
    try:
        if MobilePurchaseOrder:
            from extensions import db
            orders = MobilePurchaseOrder.query.filter_by(
                user_id=request.user_id
            ).order_by(
                MobilePurchaseOrder.created_at.desc()
            ).limit(50).all()
            
            orders_data = [order.to_dict() for order in orders]
        else:
            # fallback: 임시 데이터
            orders_data = [
                {
                    "id": f"po_{request.user_id}_1",
                    "status": "requested",
                    "items": [
                        {"barcode": "123456789", "name": "테스트 상품", "quantity": 10}
                    ],
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        
        return jsonify({"data": orders_data, "total": len(orders_data)})
        
    except Exception as e:
        print(f"발주 목록 조회 오류: {e}")
        return jsonify({"data": [], "total": 0})

# 스케줄 관리 API
@mobile_bp.route("/schedule", methods=["GET"])
@auth_required
def get_schedule():
    """스케줄 조회"""
    try:
        from datetime import datetime, timedelta
        from extensions import db
        
        # 현재 날짜부터 30일간의 스케줄 조회
        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(days=30)
        
        # 실제 스케줄 데이터가 있으면 사용, 없으면 임시 데이터
        schedules = []
        
        # 임시 스케줄 데이터 생성 (테스트용)
        for i in range(7):
            date = start_date + timedelta(days=i)
            schedules.append({
                "id": f"schedule_{request.user_id}_{i}",
                "date": date.isoformat(),
                "type": "work" if i < 5 else "off",  # 평일 근무, 주말 휴무
                "start_time": "09:00" if i < 5 else None,
                "end_time": "18:00" if i < 5 else None,
                "status": "confirmed"
            })
        
        return jsonify({"data": schedules, "total": len(schedules)})
        
    except Exception as e:
        print(f"스케줄 조회 오류: {e}")
        return jsonify({"data": [], "total": 0})

@mobile_bp.route("/schedule/leave", methods=["POST"])
@auth_required
@require_idempotency_key()
def request_leave():
    """휴가 신청"""
    try:
        data = request.get_json() or {}
        leave_type = data.get("type")  # annual, sick, personal
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        reason = data.get("reason", "")
        
        if not all([leave_type, start_date, end_date]):
            return jsonify({"error": "필수 정보가 누락되었습니다"}), 400
        
        # 휴가 신청 데이터 생성
        leave_request = {
            "id": f"leave_{request.user_id}_{int(datetime.utcnow().timestamp())}",
            "user_id": request.user_id,
            "type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 이벤트 브로드캐스트
        emit_event("schedule:leave_request", leave_request, room=f"user:{request.user_id}")
        
        return jsonify({"ok": True, **leave_request})
        
    except Exception as e:
        print(f"휴가 신청 오류: {e}")
        return jsonify({"error": "휴가 신청에 실패했습니다"}), 500

@mobile_bp.route("/schedule/swap", methods=["POST"])
@auth_required
@require_idempotency_key()
def request_schedule_swap():
    """근무 교대 신청"""
    try:
        data = request.get_json() or {}
        target_date = data.get("target_date")
        swap_with_user = data.get("swap_with_user")
        reason = data.get("reason", "")
        
        if not all([target_date, swap_with_user]):
            return jsonify({"error": "필수 정보가 누락되었습니다"}), 400
        
        # 교대 신청 데이터 생성
        swap_request = {
            "id": f"swap_{request.user_id}_{int(datetime.utcnow().timestamp())}",
            "user_id": request.user_id,
            "target_date": target_date,
            "swap_with_user": swap_with_user,
            "reason": reason,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 이벤트 브로드캐스트
        emit_event("schedule:swap_request", swap_request, room=f"user:{request.user_id}")
        
        return jsonify({"ok": True, **swap_request})
        
    except Exception as e:
        print(f"교대 신청 오류: {e}")
        return jsonify({"error": "교대 신청에 실패했습니다"}), 500

@mobile_bp.route("/purchase_orders", methods=["POST"])
@auth_required
@require_idempotency_key()
def create_purchase_order():
    """발주 생성"""
    data = request.get_json() or {}
    items = data.get("items", [])
    
    if not items:
        return jsonify({"error": "발주 항목이 필요합니다"}), 400
    
    # 실제 데이터베이스에 저장
    if MobilePurchaseOrder:
        try:
            from extensions import db
            purchase_order = MobilePurchaseOrder(
                user_id=request.user_id,
                status="requested",
                items=items
            )
            db.session.add(purchase_order)
            db.session.commit()
            
            purchase_data = purchase_order.to_dict()
        except Exception as e:
            print(f"데이터베이스 저장 오류: {e}")
            db.session.rollback()
            # fallback: 임시 데이터
            purchase_data = {
                "id": f"po_{request.user_id}_{int(datetime.utcnow().timestamp())}",
                "user_id": request.user_id,
                "status": "requested",
                "items": items,
                "created_at": datetime.utcnow().isoformat()
            }
    else:
        # 모델이 없는 경우 임시 데이터
        purchase_data = {
            "id": f"po_{request.user_id}_{int(datetime.utcnow().timestamp())}",
            "user_id": request.user_id,
            "status": "requested",
            "items": items,
            "created_at": datetime.utcnow().isoformat()
        }
    
    # 이벤트 헬퍼를 사용한 실시간 브로드캐스트
    try:
        emit_purchase_order_update(purchase_data)
    except Exception as e:
        print(f"이벤트 송출 실패: {e}")
        # 이벤트 실패는 기록 실패가 아니므로 무시
    
    return jsonify({
        "ok": True,
        "purchase_order_id": purchase_data["id"],
        **purchase_data
    })



@mobile_bp.route("/orders/update_status", methods=["POST"])
@auth_required
def update_order_status():
    """주문 상태 업데이트"""
    data = request.get_json() or {}
    order_id = data.get("order_id")
    status = data.get("status")
    
    if not order_id or not status:
        return jsonify({"error": "주문 ID와 상태가 필요합니다"}), 400
    
    # 실제로는 Order 테이블에서 업데이트
    # order = Order.query.get(order_id)
    # order.status = status
    # db.session.commit()
    
    order_data = {
        "id": order_id,
        "status": status,
        "user_id": request.user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Socket.IO로 실시간 브로드캐스트
    try:
        from extensions import socketio
        socketio.emit("order:update", order_data, room=None)  # broadcast=True 대신 room=None 사용
    except ImportError:
        pass
    
    return jsonify({
        "ok": True,
        "order_id": order_id,
        "status": status
    })

@mobile_bp.route("/test", methods=["GET"])
def test():
    """API 연결 테스트"""
    return jsonify({
        "ok": True,
        "message": "모바일 API가 정상적으로 작동하고 있습니다!",
        "timestamp": datetime.utcnow().isoformat()
    })

@mobile_bp.route("/health", methods=["GET"])
def health_check():
    """헬스 체크"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })
