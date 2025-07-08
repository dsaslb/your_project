from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user
from functools import wraps
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User, Order, InventoryItem, Staff, Attendance, Schedule, Notification
from utils.decorators import admin_required, manager_required
from utils.security_manager import security_manager
from utils.external_api_manager import external_api_manager
import logging
from datetime import datetime, timedelta
import json
from api.gateway import token_required, role_required, admin_required, manager_required, employee_required, log_request

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mobile_api = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

def mobile_response(func):
    """모바일 API 응답 포맷 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, dict):
                return jsonify({
                    "success": True,
                    "data": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
            return result
        except Exception as e:
            logger.error(f"모바일 API 에러: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500
    return wrapper

@mobile_api.route('/auth/login', methods=['POST'])
@mobile_response
def mobile_login():
    """모바일 로그인"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return {"error": "사용자명과 비밀번호가 필요합니다."}, 400
    
    username = data['username']
    password = data['password']
    
    # 로그인 시도 제한 확인
    user = User.query.filter_by(username=username).first()
    if user:
        can_login, lockout_time = security_manager.check_login_attempts(user.id)
        if not can_login:
            return {"error": f"계정이 잠겼습니다. {lockout_time}초 후 다시 시도하세요."}, 429
    
    # 사용자 인증
    if user and security_manager.verify_password(password, user.password_hash, user.salt):
        # 로그인 성공 기록
        security_manager.record_login_attempt(user.id, True)
        
        # JWT 토큰 생성
        token = security_manager.generate_jwt_token(user.id, user.role)
        
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "role": user.role,
                "branch_id": user.branch_id
            },
            "token": token,
            "expires_in": 3600
        }
    else:
        # 로그인 실패 기록
        if user:
            security_manager.record_login_attempt(user.id, False)
        
        return {"error": "잘못된 사용자명 또는 비밀번호입니다."}, 401

@mobile_api.route('/auth/refresh', methods=['POST'])
@mobile_response
def mobile_refresh_token():
    """토큰 갱신"""
    data = request.get_json()
    
    if not data or 'token' not in data:
        return {"error": "토큰이 필요합니다."}, 400
    
    # 기존 토큰 검증
    payload = security_manager.verify_jwt_token(data['token'])
    if not payload:
        return {"error": "유효하지 않은 토큰입니다."}, 401
    
    # 새 토큰 생성
    user = User.query.get(payload['user_id'])
    if not user:
        return {"error": "사용자를 찾을 수 없습니다."}, 404
    
    new_token = security_manager.generate_jwt_token(user.id, user.role)
    
    return {
        "token": new_token,
        "expires_in": 3600
    }

@mobile_api.route('/dashboard', methods=['GET'])
@token_required
@log_request
def mobile_dashboard():
    """모바일 대시보드 데이터"""
    try:
        user = g.user
        
        # 사용자별 대시보드 데이터
        if user.role in ['admin', 'super_admin']:
            return jsonify(get_admin_mobile_dashboard(user))
        elif user.role == 'manager':
            return jsonify(get_manager_mobile_dashboard(user))
        else:
            return jsonify(get_employee_mobile_dashboard(user))
            
    except Exception as e:
        logger.error(f"모바일 대시보드 오류: {str(e)}")
        return jsonify({'error': 'Failed to fetch mobile dashboard'}), 500

def get_admin_mobile_dashboard(user):
    """관리자 모바일 대시보드"""
    try:
        # 오늘의 주요 지표
        today = datetime.now().date()
        
        # 주문 현황
        today_orders = Order.query.filter(
            Order.created_at >= today
        ).all()
        
        # 출근 현황
        today_attendances = Attendance.query.filter(
            Attendance.clock_in >= today
        ).all()
        
        # 재고 알림
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).all()
        
        # 미읽 알림
        unread_notifications = Notification.query.filter_by(
            user_id=user.id, is_read=False
        ).count()
        
        return {
            'user_info': {
                'name': user.name,
                'role': user.role,
                'avatar': user.name[0].upper()
            },
            'quick_stats': {
                'today_orders': len(today_orders),
                'today_sales': sum(order.total_amount for order in today_orders),
                'attendance_count': len(today_attendances),
                'low_stock_count': len(low_stock_items),
                'unread_notifications': unread_notifications
            },
            'recent_activities': get_recent_activities(),
            'quick_actions': [
                {'id': 'new_order', 'title': '주문 등록', 'icon': 'shopping-cart'},
                {'id': 'attendance', 'title': '출근 관리', 'icon': 'user-check'},
                {'id': 'inventory', 'title': '재고 확인', 'icon': 'package'},
                {'id': 'reports', 'title': '보고서', 'icon': 'file-text'}
            ]
        }
        
    except Exception as e:
        logger.error(f"관리자 모바일 대시보드 오류: {str(e)}")
        raise

def get_manager_mobile_dashboard(user):
    """매니저 모바일 대시보드"""
    try:
        today = datetime.now().date()
        
        # 팀 출근 현황
        team_attendances = Attendance.query.filter(
            Attendance.clock_in >= today
        ).join(User).filter(User.role == 'employee').all()
        
        # 오늘 주문
        today_orders = Order.query.filter(
            Order.created_at >= today
        ).all()
        
        # 스케줄 확인
        today_schedules = Schedule.query.filter(
            Schedule.date == today
        ).all()
        
        return {
            'user_info': {
                'name': user.name,
                'role': user.role,
                'avatar': user.name[0].upper()
            },
            'quick_stats': {
                'team_attendance': len(team_attendances),
                'today_orders': len(today_orders),
                'scheduled_shifts': len(today_schedules),
                'pending_approvals': 0  # 실제로는 승인 대기 건수
            },
            'recent_activities': get_recent_activities(),
            'quick_actions': [
                {'id': 'team_attendance', 'title': '팀 출근', 'icon': 'users'},
                {'id': 'order_management', 'title': '주문 관리', 'icon': 'shopping-cart'},
                {'id': 'schedule', 'title': '스케줄', 'icon': 'calendar'},
                {'id': 'inventory', 'title': '재고', 'icon': 'package'}
            ]
        }
        
    except Exception as e:
        logger.error(f"매니저 모바일 대시보드 오류: {str(e)}")
        raise

def get_employee_mobile_dashboard(user):
    """직원 모바일 대시보드"""
    try:
        today = datetime.now().date()
        
        # 오늘 출근 기록
        today_attendance = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.clock_in >= today
        ).first()
        
        # 오늘 스케줄
        today_schedule = Schedule.query.filter(
            Schedule.user_id == user.id,
            Schedule.date == today
        ).first()
        
        # 미읽 알림
        unread_notifications = Notification.query.filter_by(
            user_id=user.id, is_read=False
        ).count()
        
        return {
            'user_info': {
                'name': user.name,
                'role': user.role,
                'avatar': user.name[0].upper()
            },
            'quick_stats': {
                'attendance_status': '출근' if today_attendance else '미출근',
                'work_hours': calculate_work_hours(today_attendance) if today_attendance else 0,
                'schedule_time': f"{today_schedule.start_time} - {today_schedule.end_time}" if today_schedule else "스케줄 없음",
                'unread_notifications': unread_notifications
            },
            'recent_activities': get_recent_activities(),
            'quick_actions': [
                {'id': 'clock_in', 'title': '출근', 'icon': 'log-in'},
                {'id': 'clock_out', 'title': '퇴근', 'icon': 'log-out'},
                {'id': 'schedule', 'title': '스케줄', 'icon': 'calendar'},
                {'id': 'notifications', 'title': '알림', 'icon': 'bell'}
            ]
        }
        
    except Exception as e:
        logger.error(f"직원 모바일 대시보드 오류: {str(e)}")
        raise

def calculate_work_hours(attendance):
    """근무 시간 계산"""
    if not attendance or not attendance.clock_out:
        return 0
    
    duration = attendance.clock_out - attendance.clock_in
    return round(duration.total_seconds() / 3600, 1)

def get_recent_activities():
    """최근 활동 조회"""
    try:
        # 최근 10개 활동 (실제로는 Activity 모델에서 조회)
        activities = [
            {
                'id': 1,
                'type': 'order',
                'title': '새 주문 등록',
                'description': '고객 주문이 등록되었습니다.',
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                'icon': 'shopping-cart'
            },
            {
                'id': 2,
                'type': 'attendance',
                'title': '출근 기록',
                'description': '김직원님이 출근했습니다.',
                'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
                'icon': 'user-check'
            },
            {
                'id': 3,
                'type': 'inventory',
                'title': '재고 알림',
                'description': '재료 A의 재고가 부족합니다.',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'icon': 'package'
            }
        ]
        
        return activities
        
    except Exception as e:
        logger.error(f"최근 활동 조회 오류: {str(e)}")
        return []

@mobile_api.route('/attendance/clock-in', methods=['POST'])
@token_required
@log_request
def mobile_clock_in():
    """모바일 출근"""
    try:
        user = g.user
        
        # 이미 출근했는지 확인
        today = datetime.now().date()
        existing_attendance = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.clock_in >= today
        ).first()
        
        if existing_attendance:
            return jsonify({'error': '이미 출근 기록이 있습니다.'}), 400
        
        # 출근 기록 생성
        attendance = Attendance(
            user_id=user.id,
            clock_in=datetime.now(),
            date=today
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '출근이 기록되었습니다.',
            'attendance': {
                'id': attendance.id,
                'clock_in': attendance.clock_in.isoformat(),
                'date': attendance.date.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"모바일 출근 오류: {str(e)}")
        return jsonify({'error': '출근 기록 중 오류가 발생했습니다.'}), 500

@mobile_api.route('/attendance/clock-out', methods=['POST'])
@token_required
@log_request
def mobile_clock_out():
    """모바일 퇴근"""
    try:
        user = g.user
        
        # 오늘 출근 기록 찾기
        today = datetime.now().date()
        attendance = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.clock_in >= today,
            Attendance.clock_out.is_(None)
        ).first()
        
        if not attendance:
            return jsonify({'error': '출근 기록을 찾을 수 없습니다.'}), 400
        
        # 퇴근 기록
        attendance.clock_out = datetime.now()
        db.session.commit()
        
        # 근무 시간 계산
        work_hours = calculate_work_hours(attendance)
        
        return jsonify({
            'success': True,
            'message': '퇴근이 기록되었습니다.',
            'attendance': {
                'id': attendance.id,
                'clock_in': attendance.clock_in.isoformat(),
                'clock_out': attendance.clock_out.isoformat(),
                'work_hours': work_hours
            }
        })
        
    except Exception as e:
        logger.error(f"모바일 퇴근 오류: {str(e)}")
        return jsonify({'error': '퇴근 기록 중 오류가 발생했습니다.'}), 500

@mobile_api.route('/attendance/status', methods=['GET'])
@token_required
@log_request
def mobile_attendance_status():
    """모바일 출근 상태 확인"""
    try:
        user = g.user
        today = datetime.now().date()
        
        # 오늘 출근 기록
        attendance = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.clock_in >= today
        ).first()
        
        if not attendance:
            return jsonify({
                'status': 'not_clocked_in',
                'message': '출근하지 않았습니다.'
            })
        
        if not attendance.clock_out:
            work_hours = calculate_work_hours(attendance)
            return jsonify({
                'status': 'clocked_in',
                'message': '출근 중입니다.',
                'clock_in': attendance.clock_in.isoformat(),
                'work_hours': work_hours
            })
        else:
            work_hours = calculate_work_hours(attendance)
            return jsonify({
                'status': 'clocked_out',
                'message': '퇴근했습니다.',
                'clock_in': attendance.clock_in.isoformat(),
                'clock_out': attendance.clock_out.isoformat(),
                'work_hours': work_hours
            })
            
    except Exception as e:
        logger.error(f"모바일 출근 상태 확인 오류: {str(e)}")
        return jsonify({'error': '출근 상태 확인 중 오류가 발생했습니다.'}), 500

@mobile_api.route('/schedule/today', methods=['GET'])
@token_required
@log_request
def mobile_today_schedule():
    """모바일 오늘 스케줄"""
    try:
        user = g.user
        today = datetime.now().date()
        
        # 오늘 스케줄 조회
        schedules = Schedule.query.filter(
            Schedule.user_id == user.id,
            Schedule.date == today
        ).all()
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'id': schedule.id,
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'position': schedule.position,
                'notes': schedule.notes
            })
        
        return jsonify({
            'date': today.isoformat(),
            'schedules': schedule_data
        })
        
    except Exception as e:
        logger.error(f"모바일 스케줄 조회 오류: {str(e)}")
        return jsonify({'error': '스케줄 조회 중 오류가 발생했습니다.'}), 500

@mobile_api.route('/notifications', methods=['GET'])
@token_required
@log_request
def mobile_notifications():
    """모바일 알림 목록"""
    try:
        user = g.user
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 알림 조회
        notifications = Notification.query.filter_by(
            user_id=user.id
        ).order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        notification_data = []
        for notification in notifications.items:
            notification_data.append({
                'id': notification.id,
                'title': notification.title,
                'content': notification.content,
                'category': notification.category,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat()
            })
        
        return jsonify({
            'notifications': notification_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': notifications.total,
                'pages': notifications.pages,
                'has_next': notifications.has_next,
                'has_prev': notifications.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"모바일 알림 조회 오류: {str(e)}")
        return jsonify({'error': '알림 조회 중 오류가 발생했습니다.'}), 500

@mobile_api.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@token_required
@log_request
def mobile_mark_notification_read(notification_id):
    """모바일 알림 읽음 처리"""
    try:
        user = g.user
        
        # 알림 조회
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user.id
        ).first()
        
        if not notification:
            return jsonify({'error': '알림을 찾을 수 없습니다.'}), 404
        
        # 읽음 처리
        notification.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '알림을 읽음 처리했습니다.'
        })
        
    except Exception as e:
        logger.error(f"모바일 알림 읽음 처리 오류: {str(e)}")
        return jsonify({'error': '알림 읽음 처리 중 오류가 발생했습니다.'}), 500

@mobile_api.route('/orders/quick-add', methods=['POST'])
@token_required
@role_required(['admin', 'manager'])
@log_request
def mobile_quick_add_order():
    """모바일 빠른 주문 등록"""
    try:
        data = request.get_json()
        
        if not data or 'customer_name' not in data:
            return jsonify({'error': '고객명은 필수입니다.'}), 400
        
        # 주문 생성
        order = Order(
            customer_name=data['customer_name'],
            items=data.get('items', []),
            total_amount=data.get('total_amount', 0),
            status='pending',
            created_by=g.user.id
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '주문이 등록되었습니다.',
            'order': {
                'id': order.id,
                'customer_name': order.customer_name,
                'total_amount': order.total_amount,
                'status': order.status,
                'created_at': order.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"모바일 주문 등록 오류: {str(e)}")
        return jsonify({'error': '주문 등록 중 오류가 발생했습니다.'}), 500

@mobile_api.route('/inventory/check', methods=['GET'])
@token_required
@role_required(['admin', 'manager'])
@log_request
def mobile_inventory_check():
    """모바일 재고 확인"""
    try:
        # 재고 부족 품목
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).all()
        
        # 전체 재고 현황
        all_items = InventoryItem.query.all()
        
        inventory_data = []
        for item in all_items:
            inventory_data.append({
                'id': item.id,
                'name': item.name,
                'current_stock': item.current_stock,
                'min_stock': item.min_stock,
                'unit': item.unit,
                'status': 'low' if item.current_stock <= item.min_stock else 'normal'
            })
        
        return jsonify({
            'inventory': inventory_data,
            'low_stock_count': len(low_stock_items),
            'total_items': len(all_items)
        })
        
    except Exception as e:
        logger.error(f"모바일 재고 확인 오류: {str(e)}")
        return jsonify({'error': '재고 확인 중 오류가 발생했습니다.'}), 500

@mobile_api.route('/profile', methods=['GET'])
@token_required
@log_request
def mobile_profile():
    """모바일 프로필 정보"""
    try:
        user = g.user
        
        # 이번 달 출근 통계
        this_month = datetime.now().replace(day=1)
        month_attendances = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.clock_in >= this_month
        ).all()
        
        total_work_hours = sum(calculate_work_hours(att) for att in month_attendances)
        attendance_days = len(month_attendances)
        
        return jsonify({
            'user_info': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'avatar': user.name[0].upper()
            },
            'monthly_stats': {
                'work_days': attendance_days,
                'total_hours': round(total_work_hours, 1),
                'avg_hours': round(total_work_hours / attendance_days, 1) if attendance_days > 0 else 0
            }
        })
        
    except Exception as e:
        logger.error(f"모바일 프로필 조회 오류: {str(e)}")
        return jsonify({'error': '프로필 조회 중 오류가 발생했습니다.'}), 500 