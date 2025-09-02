# -*- coding: utf-8 -*-
"""
모바일 앱 전용 API 블루프린트
출퇴근, 재고 조사, 발주, 스케줄 관리 등 모바일 앱 기능을 위한 REST API
"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from extensions import db, socketio
from models_main import User, Schedule, Order, Attendance, InventoryTransaction, PurchaseOrder, PushToken
import requests

# 블루프린트 생성
mobile_bp = Blueprint("mobile_api", __name__, url_prefix="/api/mobile")

# JWT 설정
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret")
ALG = "HS256"
EXP_MIN = 60 * 24  # 24시간

# Expo Push API 설정
EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def token_for(user_id: int):
    """JWT 토큰 생성"""
    payload = {
        "sub": user_id, 
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXP_MIN)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALG)

def auth_required(fn):
    """JWT 인증 데코레이터"""
    @wraps(fn)
    def wrap(*a, **kw):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "no token"}), 401
        
        try:
            token = auth.split()[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALG])
            user_id = payload.get("sub")
            if not user_id:
                return jsonify({"error": "invalid token"}), 401
            
            # 사용자 정보를 request에 추가
            request.current_user_id = user_id
            return fn(*a, **kw)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "bad token"}), 401
        except Exception as e:
            return jsonify({"error": "authentication failed"}), 401
    
    return wrap

def send_push_notification(to_token: str, title: str, body: str, data: dict = None):
    """Expo Push API를 통해 푸시 알림 발송"""
    try:
        message = {
            "to": to_token,
            "title": title,
            "body": body,
            "sound": "default",
            "badge": 1,
        }
        
        if data:
            message["data"] = data
        
        response = requests.post(EXPO_PUSH_URL, json=message, headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("data", [{}])[0].get("status") == "ok":
                print(f"푸시 알림 발송 성공: {title}")
                return True
            else:
                print(f"푸시 알림 발송 실패: {result}")
                return False
        else:
            print(f"푸시 알림 API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"푸시 알림 발송 중 오류: {e}")
        return False

def send_push_to_user(user_id: int, title: str, body: str, data: dict = None):
    """특정 사용자에게 푸시 알림 발송"""
    try:
        # 사용자의 활성화된 푸시 토큰 조회
        push_tokens = PushToken.query.filter_by(
            user_id=user_id, 
            is_active=True
        ).all()
        
        if not push_tokens:
            print(f"사용자 {user_id}의 활성화된 푸시 토큰이 없습니다.")
            return False
        
        success_count = 0
        for push_token in push_tokens:
            if send_push_notification(push_token.token, title, body, data):
                success_count += 1
        
        print(f"사용자 {user_id}에게 {success_count}/{len(push_tokens)}개 푸시 알림 발송 완료")
        return success_count > 0
        
    except Exception as e:
        print(f"사용자 푸시 알림 발송 실패: {e}")
        return False

@mobile_bp.get("/health")
def health():
    """헬스체크 엔드포인트"""
    return jsonify({
        "ok": True, 
        "service": "mobile",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@mobile_bp.post("/login")
def login():
    """모바일 앱 로그인"""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    
    # 사용자 조회
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401
    
    # JWT 토큰 생성
    token = token_for(user.id)
    
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": getattr(user, 'role', 'employee'),
            "branch_id": getattr(user, 'branch_id', None)
        }
    })

@mobile_bp.get("/auth/me")
@auth_required
def get_me():
    """현재 사용자 정보 조회"""
    user = User.query.get(request.current_user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": getattr(user, 'role', 'employee'),
        "branch_id": getattr(user, 'branch_id', None)
    })

@mobile_bp.post("/attendance/clock-in")
@auth_required
def clock_in():
    """출근 체크"""
    data = request.get_json() or {}
    user_id = request.current_user_id
    
    # 출근 기록 생성
    attendance = Attendance(
        user_id=user_id,
        type='in',
        at=datetime.now(timezone.utc),
        lat=data.get('lat'),
        lng=data.get('lng'),
        qr_code=data.get('qr')
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    # 실시간 이벤트 발송
    socketio.emit("attendance:update", {
        "type": "in",
        "user_id": user_id,
        "timestamp": attendance.at.isoformat(),
        "lat": data.get('lat'),
        "lng": data.get('lng')
    }, broadcast=True)
    
    return jsonify({
        "ok": True,
        "type": "in",
        "at": attendance.at.isoformat(),
        "user_id": user_id
    })

@mobile_bp.post("/attendance/clock-out")
@auth_required
def clock_out():
    """퇴근 체크"""
    data = request.get_json() or {}
    user_id = request.current_user_id
    
    # 퇴근 기록 생성
    attendance = Attendance(
        user_id=user_id,
        type='out',
        at=datetime.now(timezone.utc),
        lat=data.get('lat'),
        lng=data.get('lng')
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    # 실시간 이벤트 발송
    socketio.emit("attendance:update", {
        "type": "out",
        "user_id": user_id,
        "timestamp": attendance.at.isoformat(),
        "lat": data.get('lat'),
        "lng": data.get('lng')
    }, broadcast=True)
    
    return jsonify({
        "ok": True,
        "type": "out",
        "at": attendance.at.isoformat(),
        "user_id": user_id
    })

@mobile_bp.post("/inventory/check")
@auth_required
def inventory_check():
    """재고 조사"""
    data = request.get_json() or {}
    user_id = request.current_user_id
    
    # 재고 기록 생성
    inventory_log = InventoryTransaction(
        user_id=user_id,
        barcode=data.get('barcode'),
        quantity=data.get('qty', 0),
        photo_url=data.get('photo_url'),
        created_at=datetime.now(timezone.utc)
    )
    
    db.session.add(inventory_log)
    db.session.commit()
    
    # 실시간 이벤트 발송
    socketio.emit("inventory:update", {
        "barcode": data.get('barcode'),
        "qty": data.get('qty', 0),
        "user_id": user_id,
        "timestamp": inventory_log.created_at.isoformat()
    }, broadcast=True)
    
    return jsonify({
        "ok": True,
        "barcode": data.get('barcode'),
        "qty": data.get('qty', 0)
    })

@mobile_bp.post("/purchase-orders")
@auth_required
def create_purchase_order():
    """발주 요청 생성"""
    data = request.get_json() or {}
    user_id = request.current_user_id
    
    # 발주 요청 생성
    purchase_order = PurchaseOrder(
        user_id=user_id,
        branch_id=data.get('branch_id'),
        items=data.get('items', []),
        status='requested',
        created_at=datetime.now(timezone.utc)
    )
    
    db.session.add(purchase_order)
    db.session.commit()
    
    # 실시간 이벤트 발송
    socketio.emit("po:created", {
        "branch_id": data.get('branch_id'),
        "user_id": user_id,
        "order_id": purchase_order.id,
        "timestamp": purchase_order.created_at.isoformat()
    }, broadcast=True)
    
    # 관리자에게 푸시 알림 발송 (새로운 발주 요청)
    admin_users = User.query.filter_by(role='admin').all()
    for admin in admin_users:
        send_push_to_user(
            admin.id,
            "새로운 발주 요청",
            f"발주 #{purchase_order.id}이 요청되었습니다.",
            {
                'type': 'new_purchase_order',
                'order_id': purchase_order.id,
                'user_id': user_id
            }
        )
    
    return jsonify({
        "ok": True,
        "order_id": purchase_order.id,
        "status": "requested"
    })

@mobile_bp.get("/dashboard")
@auth_required
def get_dashboard():
    """대시보드 데이터 조회"""
    user_id = request.current_user_id
    
    # 최근 출퇴근 기록
    recent_attendance = Attendance.query.filter_by(user_id=user_id)\
        .order_by(Attendance.at.desc()).limit(5).all()
    
    # 오늘의 스케줄
    today = datetime.now(timezone.utc).date()
    today_schedule = Schedule.query.filter_by(user_id=user_id)\
        .filter(Schedule.date == today).first()
    
    # 대기 중인 발주
    pending_orders = PurchaseOrder.query.filter_by(user_id=user_id)\
        .filter(PurchaseOrder.status == 'requested').count()
    
    return jsonify({
        "user_id": user_id,
        "recent_attendance": [
            {
                "type": att.type,
                "at": att.at.isoformat(),
                "lat": att.lat,
                "lng": att.lng
            } for att in recent_attendance
        ],
        "today_schedule": {
            "date": today_schedule.date.isoformat() if today_schedule else None,
            "start_time": today_schedule.start_time.isoformat() if today_schedule else None,
            "end_time": today_schedule.end_time.isoformat() if today_schedule else None
        } if today_schedule else None,
        "pending_orders": pending_orders,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@mobile_bp.get("/schedules")
@auth_required
def get_schedules():
    """스케줄 조회"""
    user_id = request.current_user_id
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Schedule.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(Schedule.date >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(Schedule.date <= datetime.fromisoformat(end_date).date())
    
    schedules = query.order_by(Schedule.date).all()
    
    return jsonify({
        "schedules": [
            {
                "id": sched.id,
                "date": sched.date.isoformat(),
                "start_time": sched.start_time.isoformat(),
                "end_time": sched.end_time.isoformat(),
                "status": getattr(sched, 'status', 'scheduled')
            } for sched in schedules
        ]
    })

@mobile_bp.post("/notifications/register-token")
@auth_required
def register_push_token():
    """푸시 알림 토큰 등록"""
    data = request.get_json() or {}
    user_id = request.current_user_id
    
    token = data.get('token')
    platform = data.get('platform', 'unknown')
    device_id = data.get('device_id')
    
    if not token:
        return jsonify({"error": "token required"}), 400
    
    try:
        # 기존 토큰이 있는지 확인
        existing_token = PushToken.query.filter_by(
            user_id=user_id, 
            token=token, 
            platform=platform
        ).first()
        
        if existing_token:
            # 기존 토큰 활성화
            existing_token.is_active = True
            existing_token.updated_at = datetime.now(timezone.utc)
        else:
            # 새 토큰 생성
            push_token = PushToken(
                user_id=user_id,
                token=token,
                platform=platform,
                device_id=device_id,
                is_active=True
            )
            db.session.add(push_token)
        
        db.session.commit()
        
        return jsonify({
            "ok": True,
            "message": "Push token registered successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to register token: {str(e)}"}), 500