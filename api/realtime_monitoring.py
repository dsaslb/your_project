from flask import Blueprint, request, jsonify, g
from functools import wraps
from models import User, Order, Attendance, Schedule, InventoryItem, Notification, db
from extensions import db
import logging
from datetime import datetime, timedelta
import json
import asyncio
import threading
import time
from collections import defaultdict
from api.gateway import token_required, role_required, admin_required, manager_required, employee_required, log_request
from utils.email_utils import send_email  # 이메일 유틸리티 임포트
import os
from sqlalchemy import text  # SQLAlchemy text 임포트

# 로깅 설정
logger = logging.getLogger(__name__)

# 실시간 모니터링 API Blueprint
realtime_monitoring = Blueprint('realtime_monitoring', __name__, url_prefix='/api/realtime')

# 실시간 데이터 저장소
realtime_data = {
    'active_users': set(),
    'current_orders': [],
    'system_alerts': [],
    'performance_metrics': {},
    'last_update': datetime.utcnow()
}

# 알림 설정
alert_thresholds = {
    'order_processing_time': 30,  # 30분 초과 시 알림
    'low_stock_threshold': 10,    # 10개 이하 시 알림
    'attendance_late_threshold': 15,  # 15분 지각 시 알림
    'system_error_threshold': 5   # 5개 이상 에러 시 알림
}

def update_realtime_data():
    """실시간 데이터 업데이트"""
    try:
        # 현재 활성 주문
        current_orders = Order.query.filter(
            Order.status.in_(['pending', 'processing'])
        ).all()
        
        realtime_data['current_orders'] = [
            {
                'id': order.id,
                'customer_name': order.customer_name,
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'processing_time': (datetime.utcnow() - order.created_at).total_seconds() / 60
            }
            for order in current_orders
        ]
        
        # 시스템 성능 지표
        realtime_data['performance_metrics'] = {
            'total_orders_today': Order.query.filter(
                Order.created_at >= datetime.utcnow().date()
            ).count(),
            'pending_orders': len(realtime_data['current_orders']),
            'active_staff': Attendance.query.filter(
                Attendance.clock_in >= datetime.utcnow() - timedelta(hours=8),
                Attendance.clock_out.is_(None)
            ).count(),
            'low_stock_items': InventoryItem.query.filter(
                InventoryItem.current_stock <= InventoryItem.min_stock
            ).count()
        }
        
        realtime_data['last_update'] = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Real-time data update error: {str(e)}")

def send_critical_alert_email(alert):
    """
    매출 급감 등 critical 알림 발생 시 관리자에게 이메일 자동 발송
    """
    from flask import current_app
    admin_email = (
        current_app.config.get("ADMIN_EMAIL")
        or os.getenv("ADMIN_EMAIL")
        or "admin@example.com"
    )
    subject = f"[경고] {alert.get('type', 'Critical Alert')} 발생"
    body = f"""
[운영 경고]

유형: {alert.get('type')}
메시지: {alert.get('message')}
발생 시각: {alert.get('timestamp')}

상세 정보: {alert}
"""
    html_body = f"""
    <h2>[운영 경고]</h2>
    <ul>
        <li><b>유형:</b> {alert.get('type')}</li>
        <li><b>메시지:</b> {alert.get('message')}</li>
        <li><b>발생 시각:</b> {alert.get('timestamp')}</li>
    </ul>
    <pre>{alert}</pre>
    """
    send_email(admin_email, subject, body, html_body)

def check_alerts():
    """
    알림 조건 확인 (주문 지연, 재고 부족, 지각, 매출 급감 등)
    critical 알림 발생 시 관리자 이메일 자동 발송
    """
    alerts = []
    try:
        # 주문 처리 시간 알림
        for order in realtime_data['current_orders']:
            if order['processing_time'] > alert_thresholds['order_processing_time']:
                alerts.append({
                    'type': 'order_delay',
                    'severity': 'warning',
                    'message': f"주문 #{order['id']} 처리 시간이 {order['processing_time']:.1f}분을 초과했습니다.",
                    'order_id': order['id'],
                    'timestamp': datetime.utcnow().isoformat()
                })

        # 재고 부족 알림
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= alert_thresholds['low_stock_threshold']
        ).all()
        for item in low_stock_items:
            alerts.append({
                'type': 'low_stock',
                'severity': 'critical',
                'message': f"{item.name} 재고가 {item.current_stock}개로 부족합니다.",
                'item_id': item.id,
                'timestamp': datetime.utcnow().isoformat()
            })

        # 지각 알림
        late_attendances = Attendance.query.filter(
            Attendance.clock_in >= datetime.utcnow().date(),
            Attendance.clock_in.time() > datetime.strptime('09:15', '%H:%M').time()
        ).all()
        for attendance in late_attendances:
            late_minutes = (attendance.clock_in.time() - datetime.strptime('09:00', '%H:%M').time()).total_seconds() / 60
            if late_minutes > alert_thresholds['attendance_late_threshold']:
                alerts.append({
                    'type': 'late_attendance',
                    'severity': 'info',
                    'message': f"{attendance.user.name}님이 {late_minutes:.0f}분 지각했습니다.",
                    'user_id': attendance.user_id,
                    'timestamp': datetime.utcnow().isoformat()
                })

        # [AI] 매출 급감 경고 로직 추가
        # 최근 7일 매출 평균 대비 오늘 매출이 30% 이상 급감하면 경고
        today = datetime.utcnow().date()
        seven_days_ago = today - timedelta(days=7)
        # 최근 7일(오늘 제외) 매출 합계
        sales_last_7 = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.created_at >= seven_days_ago,
            Order.created_at < today
        ).scalar() or 0
        days_count = (today - seven_days_ago).days
        avg_sales_7 = sales_last_7 / days_count if days_count > 0 else 0
        # 오늘 매출 합계
        sales_today = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.created_at >= today
        ).scalar() or 0
        # 급감 비율 계산
        if avg_sales_7 > 0 and sales_today < avg_sales_7 * 0.7:
            drop_percent = round((1 - sales_today / avg_sales_7) * 100, 1)
            alert = {
                'type': 'sales_drop',
                'severity': 'critical',
                'message': f"오늘 매출이 최근 7일 평균 대비 {drop_percent}% 급감했습니다.",
                'avg_sales_7days': int(avg_sales_7),
                'sales_today': int(sales_today),
                'timestamp': datetime.utcnow().isoformat()
            }
            alerts.append(alert)
            # === [추가] critical 알림 발생 시 이메일 자동 발송 ===
            send_critical_alert_email(alert)
        realtime_data['system_alerts'] = alerts
    except Exception as e:
        logger.error(f"Alert check error: {str(e)}")

# 백그라운드 업데이트 스레드
def background_updater():
    """백그라운드에서 실시간 데이터 업데이트"""
    while True:
        try:
            update_realtime_data()
            check_alerts()
            time.sleep(30)  # 30초마다 업데이트
        except Exception as e:
            logger.error(f"Background updater error: {str(e)}")
            time.sleep(60)  # 에러 시 1분 대기

# 백그라운드 스레드 시작
update_thread = threading.Thread(target=background_updater, daemon=True)
update_thread.start()

@realtime_monitoring.route('/dashboard', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def realtime_dashboard():
    """실시간 대시보드 데이터"""
    try:
        # 실시간 데이터 업데이트
        update_realtime_data()
        check_alerts()
        
        return jsonify({
            'performance_metrics': realtime_data['performance_metrics'],
            'current_orders': realtime_data['current_orders'],
            'system_alerts': realtime_data['system_alerts'],
            'last_update': realtime_data['last_update'].isoformat() if isinstance(realtime_data['last_update'], datetime) else str(realtime_data['last_update']),
            'active_users_count': len(realtime_data['active_users']) if hasattr(realtime_data['active_users'], '__len__') else 0
        })
    except Exception as e:
        logger.error(f"Real-time dashboard error: {str(e)}")
        return jsonify({'error': 'Failed to fetch real-time data'}), 500

@realtime_monitoring.route('/orders/stream', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def orders_stream():
    """주문 실시간 스트림"""
    try:
        # 최근 1시간 주문
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_orders = Order.query.filter(
            Order.created_at >= one_hour_ago
        ).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in recent_orders:
            processing_time = (datetime.utcnow() - order.created_at).total_seconds() / 60
            orders_data.append({
                'id': order.id,
                'customer_name': order.customer_name,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat(),
                'processing_time': round(processing_time, 1),
                'is_delayed': processing_time > alert_thresholds['order_processing_time']
            })
        
        return jsonify({
            'orders': orders_data,
            'summary': {
                'total_orders': len(orders_data),
                'pending_orders': len([o for o in orders_data if o['status'] == 'pending']),
                'delayed_orders': len([o for o in orders_data if o['is_delayed']]),
                'average_processing_time': sum(o['processing_time'] for o in orders_data) / len(orders_data) if orders_data else 0
            }
        })
    except Exception as e:
        logger.error(f"Orders stream error: {str(e)}")
        return jsonify({'error': 'Failed to fetch orders stream'}), 500

@realtime_monitoring.route('/staff/status', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def staff_status():
    """직원 실시간 상태"""
    try:
        # 현재 근무 중인 직원
        active_attendances = Attendance.query.filter(
            Attendance.clock_in >= datetime.utcnow().date(),
            Attendance.clock_out.is_(None)
        ).all()
        
        # 오늘 출근한 직원
        today_attendances = Attendance.query.filter(
            Attendance.clock_in >= datetime.utcnow().date()
        ).all()
        
        # 지각한 직원
        late_attendances = [
            att for att in today_attendances
            if att.clock_in.time() > datetime.strptime('09:00', '%H:%M').time()
        ]
        
        staff_data = []
        for attendance in active_attendances:
            work_hours = (datetime.utcnow() - attendance.clock_in).total_seconds() / 3600
            staff_data.append({
                'user_id': attendance.user_id,
                'name': attendance.user.name,
                'role': attendance.user.role,
                'clock_in': attendance.clock_in.isoformat(),
                'work_hours': round(work_hours, 1),
                'status': 'active'
            })
        
        return jsonify({
            'active_staff': staff_data,
            'summary': {
                'total_active': len(active_attendances),
                'total_today': len(today_attendances),
                'late_count': len(late_attendances),
                'attendance_rate': round(len(today_attendances) / User.query.filter_by(role='employee').count() * 100, 1) if User.query.filter_by(role='employee').count() > 0 else 0
            }
        })
    except Exception as e:
        logger.error(f"Staff status error: {str(e)}")
        return jsonify({'error': 'Failed to fetch staff status'}), 500

@realtime_monitoring.route('/inventory/alerts', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def inventory_alerts():
    """재고 알림"""
    try:
        # 재고 부족 품목
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).all()
        
        # 곧 소진될 품목 (3일 이내)
        expiring_items = []
        for item in InventoryItem.query.all():
            if item.current_stock > 0:
                # 간단한 소비량 예측 (실제로는 더 복잡한 알고리즘 사용)
                daily_consumption = item.current_stock / 30 if item.current_stock > 0 else 0
                days_until_stockout = item.current_stock / daily_consumption if daily_consumption > 0 else float('inf')
                
                if days_until_stockout <= 3 and days_until_stockout > 0:
                    expiring_items.append({
                        'item_id': item.id,
                        'name': item.name,
                        'current_stock': item.current_stock,
                        'days_until_stockout': round(days_until_stockout, 1)
                    })
        
        alerts_data = []
        for item in low_stock_items:
            alerts_data.append({
                'type': 'low_stock',
                'severity': 'critical',
                'item_id': item.id,
                'item_name': item.name,
                'current_stock': item.current_stock,
                'min_stock': item.min_stock,
                'message': f"{item.name} 재고가 {item.current_stock}개로 최소 기준({item.min_stock}개) 이하입니다.",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        for item in expiring_items:
            alerts_data.append({
                'type': 'expiring_stock',
                'severity': 'warning',
                'item_id': item['item_id'],
                'item_name': item['name'],
                'current_stock': item['current_stock'],
                'days_until_stockout': item['days_until_stockout'],
                'message': f"{item['name']} 재고가 {item['days_until_stockout']}일 후 소진 예상입니다.",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({
            'alerts': alerts_data,
            'summary': {
                'low_stock_count': len(low_stock_items),
                'expiring_count': len(expiring_items),
                'total_alerts': len(alerts_data)
            }
        })
    except Exception as e:
        logger.error(f"Inventory alerts error: {str(e)}")
        return jsonify({'error': 'Failed to fetch inventory alerts'}), 500

@realtime_monitoring.route('/system/health', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def system_health():
    """시스템 상태 체크"""
    try:
        # 데이터베이스 연결 상태
        db_status = 'healthy'
        try:
            db.session.execute(text('SELECT 1'))
        except Exception:
            db_status = 'error'
        
        # 시스템 메트릭
        system_metrics = {
            'database_status': db_status,
            'uptime': '24시간+',  # 실제로는 서버 시작 시간 계산
            'memory_usage': '45%',  # 실제로는 시스템 모니터링
            'disk_usage': '32%',
            'active_connections': len(realtime_data['active_users']) if hasattr(realtime_data['active_users'], '__len__') else 0,
            'last_backup': '2024-01-15 14:30',  # 실제로는 백업 매니저에서 가져옴
            'error_count': len([alert for alert in realtime_data['system_alerts'] if isinstance(alert, dict) and alert.get('severity') == 'critical'])
        }
        
        # 성능 지표
        performance_metrics = realtime_data['performance_metrics']
        
        # 전체 상태 평가
        overall_status = 'healthy'
        if system_metrics['error_count'] > 5:
            overall_status = 'warning'
        if system_metrics['database_status'] == 'error':
            overall_status = 'critical'
        
        return jsonify({
            'status': overall_status,
            'system_metrics': system_metrics,
            'performance_metrics': performance_metrics,
            'last_check': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"System health check error: {str(e)}")
        return jsonify({'error': 'Failed to check system health'}), 500

@realtime_monitoring.route('/notifications/push', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def push_notification():
    """실시간 알림 발송"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        # 알림 생성
        notification = Notification(
            user_id=data.get('user_id'),  # 특정 사용자에게 발송
            content=data['message'],
            title=data.get('title', '실시간 알림'),
            category='실시간',
            priority=data.get('priority', '일반'),
            is_admin_only=data.get('admin_only', False)
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # 실시간 알림 목록에 추가
        realtime_data['system_alerts'].append({
            'type': 'manual_notification',
            'severity': data.get('priority', '일반'),
            'message': data['message'],
            'timestamp': datetime.utcnow().isoformat(),
            'notification_id': notification.id
        })
        
        return jsonify({
            'success': True,
            'notification_id': notification.id,
            'message': 'Notification sent successfully'
        })
    except Exception as e:
        logger.error(f"Push notification error: {str(e)}")
        return jsonify({'error': 'Failed to send notification'}), 500

@realtime_monitoring.route('/alerts/settings', methods=['GET', 'PUT'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def alert_settings():
    """알림 설정 관리"""
    try:
        if request.method == 'GET':
            return jsonify({
                'thresholds': alert_thresholds,
                'available_alerts': [
                    'order_processing_time',
                    'low_stock_threshold',
                    'attendance_late_threshold',
                    'system_error_threshold'
                ]
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # 임계값 업데이트
            for key, value in data.items():
                if key in alert_thresholds:
                    alert_thresholds[key] = value
            
            return jsonify({
                'success': True,
                'message': 'Alert settings updated successfully',
                'thresholds': alert_thresholds
            })
    
    except Exception as e:
        logger.error(f"Alert settings error: {str(e)}")
        return jsonify({'error': 'Failed to manage alert settings'}), 500

@realtime_monitoring.route('/events/stream', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def events_stream():
    """실시간 이벤트 스트림"""
    try:
        # 최근 1시간 이벤트
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        events = []
        
        # 주문 이벤트
        recent_orders = Order.query.filter(
            Order.created_at >= one_hour_ago
        ).order_by(Order.created_at.desc()).limit(10).all()
        
        for order in recent_orders:
            events.append({
                'type': 'order',
                'action': 'created',
                'entity_id': order.id,
                'entity_name': order.customer_name,
                'timestamp': order.created_at.isoformat(),
                'details': f"새 주문: {order.customer_name} - {order.total_amount:,}원"
            })
        
        # 출근 이벤트
        recent_attendances = Attendance.query.filter(
            Attendance.clock_in >= one_hour_ago
        ).order_by(Attendance.clock_in.desc()).limit(10).all()
        
        for attendance in recent_attendances:
            events.append({
                'type': 'attendance',
                'action': 'clock_in',
                'entity_id': attendance.user_id,
                'entity_name': attendance.user.name,
                'timestamp': attendance.clock_in.isoformat(),
                'details': f"출근: {attendance.user.name}"
            })
        
        # 재고 이벤트
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).all()
        
        for item in low_stock_items:
            events.append({
                'type': 'inventory',
                'action': 'low_stock',
                'entity_id': item.id,
                'entity_name': item.name,
                'timestamp': datetime.utcnow().isoformat(),
                'details': f"재고 부족: {item.name} ({item.current_stock}개)"
            })
        
        # 시간순 정렬
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'events': events[:20],  # 최근 20개 이벤트
            'summary': {
                'total_events': len(events),
                'order_events': len([e for e in events if e['type'] == 'order']),
                'attendance_events': len([e for e in events if e['type'] == 'attendance']),
                'inventory_events': len([e for e in events if e['type'] == 'inventory'])
            }
        })
    except Exception as e:
        logger.error(f"Events stream error: {str(e)}")
        return jsonify({'error': 'Failed to fetch events stream'}), 500 