"""
레스토랑 특화 관리자 대시보드 라우트
레스토랑 업종에 특화된 실시간 모니터링 및 분석 기능 제공
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc
from models_main import Order, Staff, Branch, Menu, Inventory, Reservation, Customer
from extensions import db
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 생성
restaurant_dashboard = Blueprint('restaurant_dashboard', __name__)


@restaurant_dashboard.route('/restaurant/enhanced-dashboard')
@login_required
def enhanced_dashboard():
    """레스토랑 특화 관리자 대시보드"""
    try:
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        # 현재 시간 기준 데이터
        now = datetime.utcnow()
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        # 사용자 소속 매장 정보
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        # 기본 통계 데이터
        stats = get_restaurant_stats(today, yesterday, user_branch)
        
        # 실시간 데이터
        realtime_data = get_realtime_data(user_branch)
        
        # 차트 데이터
        chart_data = get_chart_data(week_ago, today, user_branch)

        return render_template(
            'restaurant_enhanced_dashboard.html',
            user=current_user,
            stats=stats,
            realtime_data=realtime_data,
            chart_data=chart_data
        )

    except Exception as e:
        logger.error(f"레스토랑 대시보드 오류: {str(e)}")
        return render_template('error.html', error="대시보드 로딩 중 오류가 발생했습니다.")


@restaurant_dashboard.route('/api/restaurant/realtime-data')
@login_required
def get_realtime_data_api():
    """실시간 데이터 API"""
    try:
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        data = get_realtime_data(user_branch)
        return jsonify(data)

    except Exception as e:
        logger.error(f"실시간 데이터 API 오류: {str(e)}")
        return jsonify({'error': '데이터 로딩 실패'}), 500


@restaurant_dashboard.route('/api/restaurant/analytics')
@login_required
def get_analytics_api():
    """분석 데이터 API"""
    try:
        period = request.args.get('period', 'week')
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id

        analytics = get_analytics_data(period, user_branch)
        return jsonify(analytics)

    except Exception as e:
        logger.error(f"분석 데이터 API 오류: {str(e)}")
        return jsonify({'error': '분석 데이터 로딩 실패'}), 500


def get_restaurant_stats(today, yesterday, branch_id=None):
    """레스토랑 통계 데이터 조회"""
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
        logger.error(f"통계 데이터 조회 오류: {str(e)}")
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


def get_realtime_data(branch_id=None):
    """실시간 데이터 조회"""
    try:
        # 최근 주문 (최근 1시간)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        recent_orders = db.session.query(Order).filter(
            and_(Order.created_at >= one_hour_ago, *base_filter)
        ).order_by(desc(Order.created_at)).limit(10).all()

        # 재고 알림 (부족한 재고)
        low_inventory = db.session.query(Inventory).filter(
            and_(Inventory.quantity <= Inventory.min_quantity, *base_filter)
        ).limit(5).all()

        # 직원 현황
        staff_status = db.session.query(Staff).filter(
            and_(Staff.branch_id == branch_id if branch_id else True)
        ).limit(10).all()

        # 오늘 예약
        today = datetime.utcnow().date()
        reservations = db.session.query(Reservation).filter(
            and_(Reservation.reservation_date == today, *base_filter)
        ).order_by(Reservation.reservation_time).limit(5).all()

        return {
            'recent_orders': [
                {
                    'id': order.id,
                    'order_number': f"#{order.id:04d}",
                    'items': get_order_items_summary(order),
                    'total_amount': order.total_amount,
                    'status': order.status,
                    'created_at': order.created_at,
                    'time_ago': get_time_ago(order.created_at)
                }
                for order in recent_orders
            ],
            'low_inventory': [
                {
                    'item_name': inv.item_name,
                    'quantity': inv.quantity,
                    'min_quantity': inv.min_quantity,
                    'level': '부족' if inv.quantity == 0 else '경고'
                }
                for inv in low_inventory
            ],
            'staff_status': [
                {
                    'name': staff.user.username if staff.user else 'Unknown',
                    'position': staff.position,
                    'status': '근무중' if staff.is_active else '휴식'
                }
                for staff in staff_status
            ],
            'reservations': [
                {
                    'time': res.reservation_time.strftime('%H:%M'),
                    'name': res.customer_name,
                    'guests': res.guest_count,
                    'status': res.status
                }
                for res in reservations
            ]
        }

    except Exception as e:
        logger.error(f"실시간 데이터 조회 오류: {str(e)}")
        return {
            'recent_orders': [],
            'low_inventory': [],
            'staff_status': [],
            'reservations': []
        }


def get_chart_data(start_date, end_date, branch_id=None):
    """차트 데이터 조회"""
    try:
        # 매출 트렌드 (최근 7일)
        revenue_data = []
        for i in range(7):
            date = end_date - timedelta(days=i)
            revenue = db.session.query(func.sum(Order.total_amount)).filter(
                and_(
                    func.date(Order.created_at) == date,
                    *(Order.branch_id == branch_id if branch_id else [])
                )
            ).scalar() or 0
            revenue_data.append({
                'date': date.strftime('%m/%d'),
                'revenue': revenue
            })
        revenue_data.reverse()

        # 시간대별 주문 분석
        hourly_orders = []
        for hour in range(11, 24):  # 11시부터 23시까지
            count = db.session.query(func.count(Order.id)).filter(
                and_(
                    func.extract('hour', Order.created_at) == hour,
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    *(Order.branch_id == branch_id if branch_id else [])
                )
            ).scalar() or 0
            hourly_orders.append({
                'hour': f"{hour:02d}시",
                'count': count
            })

        # 고객 유형 분석
        customer_types = [
            {'type': '신규 고객', 'count': 30, 'percentage': 30},
            {'type': '재방문 고객', 'count': 55, 'percentage': 55},
            {'type': 'VIP 고객', 'count': 15, 'percentage': 15}
        ]

        return {
            'revenue_trend': revenue_data,
            'hourly_orders': hourly_orders,
            'customer_types': customer_types
        }

    except Exception as e:
        logger.error(f"차트 데이터 조회 오류: {str(e)}")
        return {
            'revenue_trend': [],
            'hourly_orders': [],
            'customer_types': []
        }


def get_analytics_data(period, branch_id=None):
    """분석 데이터 조회"""
    try:
        end_date = datetime.utcnow().date()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)

        # 인기 메뉴 분석
        popular_menus = db.session.query(
            Menu.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_revenue')
        ).join(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *(Order.branch_id == branch_id if branch_id else [])
            )
        ).group_by(Menu.name).order_by(desc('order_count')).limit(10).all()

        # 고객 행동 분석
        customer_behavior = {
            'avg_order_value': 25000,
            'peak_hours': ['18:00-20:00', '12:00-14:00'],
            'popular_days': ['토요일', '금요일', '일요일'],
            'repeat_customer_rate': 65.5
        }

        return {
            'popular_menus': [
                {
                    'name': menu.name,
                    'order_count': menu.order_count,
                    'total_revenue': menu.total_revenue
                }
                for menu in popular_menus
            ],
            'customer_behavior': customer_behavior
        }

    except Exception as e:
        logger.error(f"분석 데이터 조회 오류: {str(e)}")
        return {
            'popular_menus': [],
            'customer_behavior': {}
        }


def get_order_items_summary(order):
    """주문 아이템 요약"""
    try:
        # 주문 아이템 정보 조회 (실제 구현에서는 OrderItem 모델 사용)
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


# 블루프린트 등록
def init_app(app):
    app.register_blueprint(restaurant_dashboard) 