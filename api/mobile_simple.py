"""
📱 간단한 모바일 API 블루프린트 (테스트용)

복잡한 데코레이터와 검증 로직 없이 기본 기능만 제공
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
import jwt
import os
from functools import wraps

from extensions import db, socketio
from models import User, MobileAttendance, InventoryLog, MobilePurchaseOrder
from services.push_notification import (
    send_attendance_notification, 
    send_inventory_notification, 
    send_purchase_order_notification
)

# 간단한 모바일 API 블루프린트 생성
simple_mobile_bp = Blueprint("simple_mobile_api", __name__, url_prefix="/api/mobile")

# 기본 health 엔드포인트
@simple_mobile_bp.route("/health", methods=["GET"])
def health_check():
    """모바일 API 헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'mobile_api',
        'timestamp': datetime.utcnow().isoformat()
    })

@simple_mobile_bp.route("/test", methods=["GET"])
def test_endpoint():
    """모바일 API 테스트 엔드포인트"""
    return jsonify({
        'message': '모바일 API가 정상 작동 중입니다',
        'status': 'success',
        'endpoints': [
            '/api/mobile/health',
            '/api/mobile/purchase_orders',
            '/api/mobile/test'
        ]
    })

# JWT 설정
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
ALG = "HS256"
EXP_MIN = 60 * 24  # 24시간

def token_for(uid):
    """사용자 ID로 JWT 토큰 생성"""
    return jwt.encode(
        {"sub": uid, "exp": datetime.utcnow() + timedelta(minutes=EXP_MIN)},
        JWT_SECRET,
        algorithm=ALG
    )

def auth_required(f):
    """JWT 인증 데코레이터"""
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
        return f(*a, **kw)
    return wrap

@simple_mobile_bp.post("/login")
def login():
    """간단한 모바일 로그인"""
    d = request.get_json() or {}
    u = User.query.filter_by(username=d.get("username")).first()
    
    if not u or not check_password_hash(u.password_hash, d.get("password", "")):
        return jsonify({"error": "invalid credentials"}), 401
    
    return jsonify({
        "token": token_for(u.id),
        "user": {
            "id": u.id,
            "username": u.username,
            "role": u.role
        }
    })

@simple_mobile_bp.post("/attendance/clock")
@auth_required
def attendance_clock():
    """간단한 출퇴근 체크"""
    d = request.get_json() or {}
    
    try:
        # 간단한 출퇴근 기록 생성
        attendance = MobileAttendance(
            user_id=request.user_id,
            type=d.get("type", "in"),
            timestamp=datetime.utcnow(),
            latitude=d.get("lat"),
            longitude=d.get("lng"),
            qr_code=d.get("qr")
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        # 성공 데이터 준비
        result_data = {
            "ok": True,
            "id": attendance.id,
            "user_id": attendance.user_id,
            "type": attendance.type,
            "timestamp": attendance.timestamp.isoformat(),
            "lat": attendance.latitude,
            "lng": attendance.longitude,
            "qr": attendance.qr_code
        }
        
        # 실시간 이벤트 브로드캐스트
        try:
            socketio.emit("attendance:update", result_data, broadcast=True)
            print(f"✅ 실시간 이벤트 전송 성공: {result_data}")
        except Exception as socket_error:
            print(f"⚠️ 실시간 이벤트 전송 실패: {socket_error}")
        
        # 푸시 알림 전송 (관리자들에게)
        try:
            # 관리자들의 푸시 토큰 수집 (실제 구현에서는 데이터베이스에서 조회)
            admin_tokens = []  # 여기에 실제 관리자 푸시 토큰들을 넣어야 함
            
            user = User.query.get(request.user_id)
            action = "출근" if attendance.type == "in" else "퇴근"
            
            if admin_tokens:
                send_attendance_notification(admin_tokens, user.username, action)
            else:
                print(f"📱 푸시 알림: {user.username}님이 {action}했습니다 (관리자 토큰 없음)")
                
        except Exception as push_error:
            print(f"⚠️ 푸시 알림 전송 실패: {push_error}")
        
        return jsonify(result_data)
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ 출퇴근 기록 저장 실패: {e}")
        print(f"상세 오류:\n{error_details}")
        
        return jsonify({
            "error": f"Database error: {str(e)}",
            "details": error_details.split('\n')[-3:-1]  # 마지막 오류 라인만
        }), 500

@simple_mobile_bp.post("/inventory/check")
@auth_required
def inventory_check():
    """간단한 재고 조사"""
    d = request.get_json() or {}
    
    try:
        # 재고 조사 로그 생성
        log = InventoryLog(
            user_id=request.user_id,
            barcode=d.get("barcode"),
            qty=d.get("qty", 0),
            photo_url=d.get("photo_url")
        )
        
        db.session.add(log)
        db.session.commit()
        
        result_data = {
            "ok": True,
            "id": log.id,
            "barcode": log.barcode,
            "qty": log.qty,
            "user_id": log.user_id,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        
        # 실시간 이벤트 브로드캐스트
        try:
            socketio.emit("inventory:update", result_data, broadcast=True)
            print(f"✅ 재고 실시간 이벤트 전송 성공: {result_data}")
        except Exception as socket_error:
            print(f"⚠️ 재고 실시간 이벤트 전송 실패: {socket_error}")
        
        return jsonify(result_data)
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ 재고 조사 저장 실패: {e}")
        print(f"상세 오류:\n{error_details}")
        
        return jsonify({
            "error": f"Database error: {str(e)}",
            "details": error_details.split('\n')[-3:-1]
        }), 500

@simple_mobile_bp.post("/purchase_orders")
@auth_required
def create_po():
    """간단한 발주 생성"""
    d = request.get_json() or {}
    
    try:
        # 발주 생성
        po = MobilePurchaseOrder(
            user_id=request.user_id,
            status="requested",
            items=d.get("items", [])
        )
        
        db.session.add(po)
        db.session.commit()
        
        result_data = {
            "ok": True,
            "id": po.id,
            "status": po.status,
            "user_id": po.user_id,
            "items": po.items,
            "created_at": po.created_at.isoformat() if po.created_at else None
        }
        
        # 실시간 이벤트 브로드캐스트
        try:
            socketio.emit("purchase_order:update", result_data, broadcast=True)
            print(f"✅ 발주 실시간 이벤트 전송 성공: {result_data}")
        except Exception as socket_error:
            print(f"⚠️ 발주 실시간 이벤트 전송 실패: {socket_error}")
        
        return jsonify(result_data)
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ 발주 생성 실패: {e}")
        print(f"상세 오류:\n{error_details}")
        
        return jsonify({
            "error": f"Database error: {str(e)}",
            "details": error_details.split('\n')[-3:-1]
        }), 500

@simple_mobile_bp.get("/dashboard")
@auth_required
def dashboard():
    """간단한 대시보드 데이터"""
    try:
        # 간단한 통계 데이터
        user = User.query.get(request.user_id)
        
        dashboard_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            },
            "today_schedule": "정상 근무",
            "attendance_status": "대기",
            "pending_orders": 0,
            "inventory_alerts": 0
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        print(f"❌ 대시보드 데이터 로드 실패: {e}")
        return jsonify({"error": str(e)}), 500

@simple_mobile_bp.post("/push/test")
@auth_required
def test_push():
    """푸시 알림 테스트"""
    try:
        from services.push_notification import test_push_notification
        
        d = request.get_json() or {}
        test_token = d.get("expo_push_token")
        
        if not test_token:
            return jsonify({"error": "expo_push_token required"}), 400
        
        # 테스트 푸시 알림 전송
        result = test_push_notification(test_token)
        
        return jsonify({
            "ok": True,
            "message": "푸시 알림 테스트 완료",
            "result": result
        })
        
    except Exception as e:
        print(f"❌ 푸시 알림 테스트 실패: {e}")
        return jsonify({"error": str(e)}), 500
