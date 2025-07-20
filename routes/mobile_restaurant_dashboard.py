"""
모바일 레스토랑 대시보드 라우트
모바일 환경에 최적화된 레스토랑 대시보드 제공
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc
from models_main import Order, Staff, Branch, Menu, Inventory, Reservation
from extensions import db
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 생성
mobile_restaurant_dashboard = Blueprint('mobile_restaurant_dashboard', __name__)


@mobile_restaurant_dashboard.route('/mobile/restaurant/dashboard')
@login_required
def mobile_dashboard():
    """모바일 레스토랑 대시보드"""
    try:
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        # 현재 시간 기준 데이터
        now = datetime.utcnow()
        today = now.date()
        yesterday = today - timedelta(days=1)

        # 사용자 소속 매장 정보
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        # 기본 통계 데이터
        stats = get_mobile_stats(today, yesterday, user_branch)
        
        # 실시간 데이터
        realtime_data = get_mobile_realtime_data(user_branch)

        return render_template(
            'mobile_restaurant_dashboard.html',
            user=current_user,
            stats=stats,
            realtime_data=realtime_data
        )

    except Exception as e:
        logger.error(f"모바일 대시보드 오류: {str(e)}")
        return render_template('error.html', error="모바일 대시보드 로딩 중 오류가 발생했습니다.")


@mobile_restaurant_dashboard.route('/api/mobile/restaurant/realtime-data')
@login_required
def get_mobile_realtime_data_api():
    """모바일 실시간 데이터 API"""
    try:
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        data = get_mobile_realtime_data(user_branch)
        return jsonify(data)

    except Exception as e:
        logger.error(f"모바일 실시간 데이터 API 오류: {str(e)}")
        return jsonify({'error': '데이터 로딩 실패'}), 500


@mobile_restaurant_dashboard.route('/api/mobile/restaurant/orders')
@login_required
def get_mobile_orders_api():
    """모바일 주문 데이터 API"""
    try:
        status_filter = request.args.get('status', 'all')
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        orders = get_mobile_orders(status_filter, user_branch)
        return jsonify(orders)

    except Exception as e:
        logger.error(f"모바일 주문 데이터 API 오류: {str(e)}")
        return jsonify({'error': '주문 데이터 로딩 실패'}), 500


@mobile_restaurant_dashboard.route('/api/mobile/restaurant/inventory')
@login_required
def get_mobile_inventory_api():
    """모바일 재고 데이터 API"""
    try:
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        inventory = get_mobile_inventory(user_branch)
        return jsonify(inventory)

    except Exception as e:
        logger.error(f"모바일 재고 데이터 API 오류: {str(e)}")
        return jsonify({'error': '재고 데이터 로딩 실패'}), 500


@mobile_restaurant_dashboard.route('/api/mobile/restaurant/staff')
@login_required
def get_mobile_staff_api():
    """모바일 직원 데이터 API"""
    try:
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        staff = get_mobile_staff(user_branch)
        return jsonify(staff)

    except Exception as e:
        logger.error(f"모바일 직원 데이터 API 오류: {str(e)}")
        return jsonify({'error': '직원 데이터 로딩 실패'}), 500


@mobile_restaurant_dashboard.route('/api/mobile/restaurant/analytics')
@login_required
def get_mobile_analytics_api():
    """모바일 분석 데이터 API"""
    try:
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        analytics = get_mobile_analytics(user_branch)
        return jsonify(analytics)

    except Exception as e:
        logger.error(f"모바일 분석 데이터 API 오류: {str(e)}")
        return jsonify({'error': '분석 데이터 로딩 실패'}), 500


def get_mobile_stats(today, yesterday, branch_id=None):
    """모바일용 통계 데이터 조회"""
    try:
        # 기본 필터 조건
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        # 오늘 매출
        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.created_at >= today, *base_filter)
        ).scalar() or 0

        # 어제 매출
        yesterday_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.created_at >= yesterday, Order.created_at < today, *base_filter)
        ).scalar() or 0

        # 오늘 주문 수
        today_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.created_at >= today, *base_filter)
        ).scalar() or 0

        # 어제 주문 수
        yesterday_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.created_at >= yesterday, Order.created_at < today, *base_filter)
        ).scalar() or 0

        # 평균 주문 금액
        avg_order_value = today_revenue / today_orders if today_orders > 0 else 0

        # 고객 만족도 (샘플 데이터)
        customer_satisfaction = 92.5

        # 증감률 계산
        revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0
        orders_change = ((today_orders - yesterday_orders) / yesterday_orders * 100) if yesterday_orders > 0 else 0

        return {
            'today_revenue': today_revenue,
            'yesterday_revenue': yesterday_revenue,
            'revenue_change': round(revenue_change, 1),
            'today_orders': today_orders,
            'yesterday_orders': yesterday_orders,
            'orders_change': round(orders_change, 1),
            'avg_order_value': round(avg_order_value),
            'customer_satisfaction': customer_satisfaction
        }

    except Exception as e:
        logger.error(f"모바일 통계 데이터 조회 오류: {str(e)}")
        return {
            'today_revenue': 0,
            'yesterday_revenue': 0,
            'revenue_change': 0,
            'today_orders': 0,
            'yesterday_orders': 0,
            'orders_change': 0,
            'avg_order_value': 0,
            'customer_satisfaction': 0
        }


def get_mobile_realtime_data(branch_id=None):
    """모바일용 실시간 데이터 조회"""
    try:
        # 최근 주문 (최근 30분)
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        recent_orders = db.session.query(Order).filter(
            and_(Order.created_at >= thirty_minutes_ago, *base_filter)
        ).order_by(desc(Order.created_at)).limit(5).all()

        # 긴급 알림
        urgent_alerts = get_urgent_alerts(branch_id)

        return {
            'recent_orders': [
                {
                    'id': order.id,
                    'order_number': f"#{order.id:04d}",
                    'items': get_order_items_summary(order),
                    'total_amount': order.total_amount,
                    'status': order.status,
                    'time_ago': get_time_ago(order.created_at)
                }
                for order in recent_orders
            ],
            'urgent_alerts': urgent_alerts
        }

    except Exception as e:
        logger.error(f"모바일 실시간 데이터 조회 오류: {str(e)}")
        return {
            'recent_orders': [],
            'urgent_alerts': []
        }


def get_mobile_orders(status_filter, branch_id=None):
    """모바일용 주문 데이터 조회"""
    try:
        # 최근 24시간 주문
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        # 상태별 필터링
        if status_filter != 'all':
            base_filter.append(Order.status == status_filter)

        orders = db.session.query(Order).filter(
            and_(Order.created_at >= one_day_ago, *base_filter)
        ).order_by(desc(Order.created_at)).limit(20).all()

        return {
            'orders': [
                {
                    'id': order.id,
                    'order_number': f"#{order.id:04d}",
                    'items': get_order_items_summary(order),
                    'total_amount': order.total_amount,
                    'status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'time_ago': get_time_ago(order.created_at)
                }
                for order in orders
            ],
            'total_count': len(orders)
        }

    except Exception as e:
        logger.error(f"모바일 주문 데이터 조회 오류: {str(e)}")
        return {'orders': [], 'total_count': 0}


def get_mobile_inventory(branch_id=None):
    """모바일용 재고 데이터 조회"""
    try:
        base_filter = []
        if branch_id:
            base_filter.append(Inventory.branch_id == branch_id)

        # 재고 부족 아이템
        low_stock_items = db.session.query(Inventory).filter(
            and_(Inventory.quantity <= Inventory.min_quantity, *base_filter)
        ).limit(10).all()

        # 전체 재고 현황
        all_inventory = db.session.query(Inventory).filter(*base_filter).limit(20).all()

        return {
            'low_stock_items': [
                {
                    'id': inv.id,
                    'item_name': inv.item_name,
                    'quantity': inv.quantity,
                    'min_quantity': inv.min_quantity,
                    'max_quantity': inv.max_quantity,
                    'status': '부족' if inv.quantity == 0 else '경고'
                }
                for inv in low_stock_items
            ],
            'all_inventory': [
                {
                    'id': inv.id,
                    'item_name': inv.item_name,
                    'quantity': inv.quantity,
                    'min_quantity': inv.min_quantity,
                    'max_quantity': inv.max_quantity,
                    'status': '정상' if inv.quantity > inv.min_quantity else '부족'
                }
                for inv in all_inventory
            ],
            'low_stock_count': len(low_stock_items)
        }

    except Exception as e:
        logger.error(f"모바일 재고 데이터 조회 오류: {str(e)}")
        return {'low_stock_items': [], 'all_inventory': [], 'low_stock_count': 0}


def get_mobile_staff(branch_id=None):
    """모바일용 직원 데이터 조회"""
    try:
        base_filter = []
        if branch_id:
            base_filter.append(Staff.branch_id == branch_id)

        # 현재 근무 중인 직원
        working_staff = db.session.query(Staff).filter(
            and_(Staff.is_active == True, *base_filter)
        ).limit(10).all()

        return {
            'working_staff': [
                {
                    'id': staff.id,
                    'name': staff.user.username if staff.user else 'Unknown',
                    'position': staff.position,
                    'status': '근무중' if staff.is_active else '휴식',
                    'avatar': get_staff_avatar(staff.id)
                }
                for staff in working_staff
            ],
            'working_count': len([s for s in working_staff if s.is_active]),
            'total_count': len(working_staff)
        }

    except Exception as e:
        logger.error(f"모바일 직원 데이터 조회 오류: {str(e)}")
        return {'working_staff': [], 'working_count': 0, 'total_count': 0}


def get_mobile_analytics(branch_id=None):
    """모바일용 분석 데이터 조회"""
    try:
        # 최근 7일 매출 데이터
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        # 일별 매출
        daily_revenue = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(func.date(Order.created_at)).order_by('date').all()

        # 인기 메뉴
        popular_menus = db.session.query(
            Menu.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_revenue')
        ).join(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(Menu.name).order_by(desc('order_count')).limit(5).all()

        return {
            'daily_revenue': [
                {
                    'date': day.date.strftime('%m/%d'),
                    'revenue': day.revenue
                }
                for day in daily_revenue
            ],
            'popular_menus': [
                {
                    'name': menu.name,
                    'order_count': menu.order_count,
                    'total_revenue': menu.total_revenue
                }
                for menu in popular_menus
            ]
        }

    except Exception as e:
        logger.error(f"모바일 분석 데이터 조회 오류: {str(e)}")
        return {'daily_revenue': [], 'popular_menus': []}


def get_urgent_alerts(branch_id=None):
    """긴급 알림 조회"""
    try:
        alerts = []
        
        # 재고 부족 알림
        base_filter = []
        if branch_id:
            base_filter.append(Inventory.branch_id == branch_id)
        
        low_stock_count = db.session.query(Inventory).filter(
            and_(Inventory.quantity == 0, *base_filter)
        ).count()
        
        if low_stock_count > 0:
            alerts.append(f"재고 부족: {low_stock_count}개 아이템")
        
        # 대기 중인 주문 알림
        pending_orders = db.session.query(Order).filter(
            and_(Order.status == 'pending', *base_filter)
        ).count()
        
        if pending_orders > 5:
            alerts.append(f"대기 주문: {pending_orders}개")
        
        return alerts

    except Exception as e:
        logger.error(f"긴급 알림 조회 오류: {str(e)}")
        return []


def get_order_items_summary(order):
    """주문 아이템 요약"""
    try:
        # 실제 구현에서는 OrderItem 모델 사용
        return "스테이크, 파스타"  # 샘플 데이터
    except:
        return "메뉴 정보 없음"


def get_time_ago(datetime_obj):
    """시간 경과 계산"""
    try:
        now = datetime.utcnow()
        diff = now - datetime_obj
        
        if diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours}시간 전"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes}분 전"
        else:
            return "방금 전"
    except:
        return "시간 정보 없음"


def get_staff_avatar(staff_id):
    """직원 아바타 반환"""
    try:
        # 실제 구현에서는 직원 프로필 이미지 반환
        return None
    except:
        return None


# 블루프린트 등록
def init_app(app):
    app.register_blueprint(mobile_restaurant_dashboard) 