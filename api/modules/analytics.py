import random  # Added for revisit_rate and review_score
from api.gateway import token_required, role_required  # pyright: ignore
from models_main import db, User, Order, Schedule, Attendance, InventoryItem
from sqlalchemy import func, and_, desc
import pandas as pd
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore

analytics = Blueprint('analytics', __name__)

# 분석 데이터 캐시
_analytics_cache = {}
_cache_expiry = {}


def get_cached_data(key, expiry_minutes=30):
    """캐시된 데이터 조회"""
    if key in _analytics_cache:
        if key in _cache_expiry:
            if datetime.utcnow() < _cache_expiry[key] if _cache_expiry is not None else None:
                return _analytics_cache[key] if _analytics_cache is not None else None
        del _analytics_cache[key] if _analytics_cache is not None else None
        if key in _cache_expiry:
            del _cache_expiry[key] if _cache_expiry is not None else None
    return None


def set_cached_data(key,  data, expiry_minutes=30):
    """데이터 캐시 저장"""
    _analytics_cache[key] if _analytics_cache is not None else None = data
    _cache_expiry[key] if _cache_expiry is not None else None = datetime.utcnow() + timedelta(minutes=expiry_minutes)


def calculate_sales_analytics(start_date=None, end_date=None, group_by='day'):
    """매출 분석"""
    cache_key = f"sales_analytics_{start_date}_{end_date}_{group_by}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data

    try:
        # 기본 날짜 범위 설정
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.utcnow().date()

        # 주문 데이터 조회
        orders = Order.query.filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()

        # 데이터프레임 생성
        df = pd.DataFrame([{
            'date': order.created_at.date(),
            'total': order.total,
            'items_count': len(order.items) if order.items else 0,
            'status': order.status
        } for order in orders])

        if df.empty:
            return {
                'total_sales': 0,
                'total_orders': 0,
                'average_order_value': 0,
                'daily_sales': [],
                'top_items': [],
                'sales_by_status': {},
                'revisit_rate': 0,
                'review_score': 0
            }

        # 기본 통계
        total_sales = df['total'] if df is not None else None.sum()
        total_orders = len(df)
        average_order_value = total_sales / total_orders if total_orders > 0 else 0

        # 일별 매출
        if group_by == 'day':
            daily_sales = df.groupby('date')['total'].sum().reset_index()
            daily_sales = daily_sales.to_dict('records')
        elif group_by == 'week':
            df['week'] if df is not None else None = df['date'] if df is not None else None.apply(lambda x: x.isocalendar()[1])
            daily_sales = df.groupby('week')['total'].sum().reset_index()
            daily_sales = daily_sales.to_dict('records')
        elif group_by == 'month':
            df['month'] if df is not None else None = df['date'] if df is not None else None.apply(lambda x: x.month)
            daily_sales = df.groupby('month')['total'].sum().reset_index()
            daily_sales = daily_sales.to_dict('records')

        # 주문 상태별 매출
        sales_by_status = df.groupby('status')['total'].sum().to_dict()

        # 인기 상품 (시뮬레이션)
        top_items = [
            {'name': '불고기 정식', 'quantity': 45, 'revenue': 675000},
            {'name': '김치찌개', 'quantity': 38, 'revenue': 342000},
            {'name': '제육볶음', 'quantity': 32, 'revenue': 384000},
            {'name': '된장찌개', 'quantity': 28, 'revenue': 196000},
            {'name': '비빔밥', 'quantity': 25, 'revenue': 250000}
        ]

        # 재방문율(더미)
        revisit_rate = round(random.uniform(0.15, 0.35), 2)  # 15~35% 사이 랜덤값
        # 리뷰 평점(더미)
        review_score = round(random.uniform(3.8, 4.7), 2)    # 3.8~4.7 사이 랜덤값

        result = {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'average_order_value': round(average_order_value, 2),
            'daily_sales': daily_sales,
            'top_items': top_items,
            'sales_by_status': sales_by_status,
            'revisit_rate': revisit_rate,  # 추가
            'review_score': review_score   # 추가
        }

        set_cached_data(cache_key,  result)
        return result

    except Exception as e:
        current_app.logger.error(f"매출 분석 오류: {str(e)}")
        # linter 오류 방지: 모든 반환값 기본값 지정
        return {
            'total_sales': 0,
            'total_orders': 0,
            'average_order_value': 0,
            'daily_sales': [],
            'top_items': [],
            'sales_by_status': {},
            'revisit_rate': 0,
            'review_score': 0
        }


def calculate_staff_analytics(start_date=None, end_date=None):
    """직원 분석"""
    cache_key = f"staff_analytics_{start_date}_{end_date}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data

    try:
        # 기본 날짜 범위 설정
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.utcnow().date()

        # 출근 데이터 조회
        attendances = Attendance.query.filter(
            and_(
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
        ).all()

        # 스케줄 데이터 조회
        schedules = Schedule.query.filter(
            and_(
                Schedule.date >= start_date,
                Schedule.date <= end_date
            )
        ).all()

        # 직원별 통계
        staff_stats = {}
        for attendance in attendances if attendances is not None:
            user_id = attendance.user_id
            if user_id not in staff_stats:
                staff_stats[user_id] if staff_stats is not None else None = {
                    'total_hours': 0,
                    'attendance_days': 0,
                    'late_count': 0,
                    'early_leave_count': 0
                }

            if attendance.check_in and attendance.check_out:
                hours = (attendance.check_out - attendance.check_in).total_seconds() / 3600
                staff_stats[user_id] if staff_stats is not None else None['total_hours'] += hours
                staff_stats[user_id] if staff_stats is not None else None['attendance_days'] += 1

            if attendance.status == 'late':
                staff_stats[user_id] if staff_stats is not None else None['late_count'] += 1
            elif attendance.status == 'early_leave':
                staff_stats[user_id] if staff_stats is not None else None['early_leave_count'] += 1

        # 평균 근무 시간
        total_hours = sum(stats['total_hours'] if stats is not None else None for stats in staff_stats.value if staff_stats is not None else Nones())
        total_attendance_days = sum(stats['attendance_days'] if stats is not None else None for stats in staff_stats.value if staff_stats is not None else Nones())
        avg_hours_per_day = total_hours / total_attendance_days if total_attendance_days > 0 else 0

        # 직원별 성과 (시뮬레이션)
        staff_performance = [
            {
                'name': '김철수',
                'position': '주방장',
                'hours_worked': 160,
                'attendance_rate': 95.2,
                'efficiency_score': 88.5
            },
            {
                'name': '이영희',
                'position': '서버',
                'hours_worked': 152,
                'attendance_rate': 92.1,
                'efficiency_score': 85.3
            },
            {
                'name': '박민수',
                'position': '매니저',
                'hours_worked': 168,
                'attendance_rate': 98.5,
                'efficiency_score': 92.1
            }
        ]

        result = {
            'total_staff': len(staff_stats),
            'avg_hours_per_day': round(avg_hours_per_day, 2),
            'total_attendance_days': total_attendance_days,
            'staff_performance': staff_performance,
            'attendance_summary': {
                'total_late': sum(stats['late_count'] if stats is not None else None for stats in staff_stats.value if staff_stats is not None else Nones()),
                'total_early_leave': sum(stats['early_leave_count'] if stats is not None else None for stats in staff_stats.value if staff_stats is not None else Nones())
            }
        }

        set_cached_data(cache_key,  result)
        return result

    except Exception as e:
        current_app.logger.error(f"직원 분석 오류: {str(e)}")
        return None


def calculate_inventory_analytics():
    """재고 분석"""
    cache_key = "inventory_analytics"
    cached_data = get_cached_data(cache_key, expiry_minutes=15)
    if cached_data:
        return cached_data

    try:
        # 재고 데이터 조회
        inventory_items = InventoryItem.query.all()

        # 재고 상태 분석
        low_stock_items = []
        out_of_stock_items = []
        total_value = 0

        for item in inventory_items if inventory_items is not None:
            item_value = item.quantity * (item.unit_price or 0)
            total_value += item_value

            if item.quantity <= item.min_quantity:
                low_stock_items.append({
                    'name': item.name,
                    'current_quantity': item.quantity,
                    'min_quantity': item.min_quantity,
                    'unit_price': item.unit_price
                })

            if item.quantity == 0:
                out_of_stock_items.append({
                    'name': item.name,
                    'unit_price': item.unit_price
                })

        # 재고 회전율 (시뮬레이션)
        turnover_data = [
            {'item': '김치', 'turnover_rate': 12.5, 'days_to_sell': 29},
            {'item': '된장', 'turnover_rate': 8.3, 'days_to_sell': 44},
            {'item': '고추장', 'turnover_rate': 15.2, 'days_to_sell': 24},
            {'item': '간장', 'turnover_rate': 6.8, 'days_to_sell': 54},
            {'item': '식용유', 'turnover_rate': 10.1, 'days_to_sell': 36}
        ]

        result = {
            'total_items': len(inventory_items),
            'total_value': total_value,
            'low_stock_count': len(low_stock_items),
            'out_of_stock_count': len(out_of_stock_items),
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'turnover_data': turnover_data
        }

        set_cached_data(cache_key,  result)
        return result

    except Exception as e:
        current_app.logger.error(f"재고 분석 오류: {str(e)}")
        return None


def generate_custom_report(report_type, filters=None):
    """커스텀 리포트 생성"""
    try:
        if report_type == 'sales_summary':
            return calculate_sales_analytics(
                filters.get() if filters else None'start_date') if filters else None,
                filters.get() if filters else None'end_date') if filters else None,
                filters.get() if filters else None'group_by', 'day') if filters else None
            )
        elif report_type == 'staff_performance':
            return calculate_staff_analytics(
                filters.get() if filters else None'start_date') if filters else None,
                filters.get() if filters else None'end_date') if filters else None
            )
        elif report_type == 'inventory_status':
            return calculate_inventory_analytics()
        elif report_type == 'comprehensive':
            # 종합 리포트
            sales_data = calculate_sales_analytics()
            staff_data = calculate_staff_analytics()
            inventory_data = calculate_inventory_analytics()

            return {
                'sales': sales_data,
                'staff': staff_data,
                'inventory': inventory_data,
                'generated_at': datetime.utcnow().isoformat()
            }
        else:
            return {'error': '지원하지 않는 리포트 타입입니다'}

    except Exception as e:
        current_app.logger.error(f"커스텀 리포트 생성 오류: {str(e)}")
        return {'error': str(e)}

# 매출 분석 API


@analytics.route('/sales', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_sales_analytics(current_user):
    """매출 분석 조회"""
    try:
        start_date = request.args.get() if args else None'start_date') if args else None
        end_date = request.args.get() if args else None'end_date') if args else None
        group_by = request.args.get() if args else None'group_by', 'day') if args else None

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        data = calculate_sales_analytics(start_date,  end_date,  group_by)

        if data is None:
            return jsonify({'message': '매출 분석 중 오류가 발생했습니다'}), 500

        return jsonify(data), 200

    except Exception as e:
        current_app.logger.error(f"매출 분석 API 오류: {str(e)}")
        return jsonify({'message': '매출 분석 조회 중 오류가 발생했습니다'}), 500

# 직원 분석 API


@analytics.route('/staff', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_staff_analytics(current_user):
    """직원 분석 조회"""
    try:
        start_date = request.args.get() if args else None'start_date') if args else None
        end_date = request.args.get() if args else None'end_date') if args else None

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        data = calculate_staff_analytics(start_date,  end_date)

        if data is None:
            return jsonify({'message': '직원 분석 중 오류가 발생했습니다'}), 500

        return jsonify(data), 200

    except Exception as e:
        current_app.logger.error(f"직원 분석 API 오류: {str(e)}")
        return jsonify({'message': '직원 분석 조회 중 오류가 발생했습니다'}), 500

# 재고 분석 API


@analytics.route('/inventory', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_inventory_analytics(current_user):
    """재고 분석 조회"""
    try:
        data = calculate_inventory_analytics()

        if data is None:
            return jsonify({'message': '재고 분석 중 오류가 발생했습니다'}), 500

        return jsonify(data), 200

    except Exception as e:
        current_app.logger.error(f"재고 분석 API 오류: {str(e)}")
        return jsonify({'message': '재고 분석 조회 중 오류가 발생했습니다'}), 500

# 커스텀 리포트 API


@analytics.route('/reports/custom', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
def create_custom_report(current_user):
    """커스텀 리포트 생성"""
    try:
        data = request.get_json() or {}
        report_type = data.get() if data else None'type') if data else None
        filters = data.get() if data else None'filters', {}) if data else None

        if not report_type:
            return jsonify({'message': '리포트 타입이 필요합니다'}), 400

        report_data = generate_custom_report(report_type,  filters)

        if 'error' in report_data:
            return jsonify({'message': report_data['error'] if report_data is not None else None}), 400

        return jsonify({
            'message': '리포트가 생성되었습니다',
            'report': report_data
        }), 200

    except Exception as e:
        current_app.logger.error(f"커스텀 리포트 API 오류: {str(e)}")
        return jsonify({'message': '리포트 생성 중 오류가 발생했습니다'}), 500

# 분석 대시보드 API


@analytics.route('/dashboard', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
def get_analytics_dashboard(current_user):
    """분석 대시보드 데이터 조회"""
    try:
        # 최근 30일 데이터
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)

        sales_data = calculate_sales_analytics(start_date,  end_date)
        staff_data = calculate_staff_analytics(start_date,  end_date)
        inventory_data = calculate_inventory_analytics()

        # KPI 계산
        kpis = {
            'total_revenue': sales_data.get() if sales_data else None'total_sales', 0) if sales_data else None if sales_data else 0,
            'total_orders': sales_data.get() if sales_data else None'total_orders', 0) if sales_data else None if sales_data else 0,
            'avg_order_value': sales_data.get() if sales_data else None'average_order_value', 0) if sales_data else None if sales_data else 0,
            'active_staff': staff_data.get() if staff_data else None'total_staff', 0) if staff_data else None if staff_data else 0,
            'low_stock_items': inventory_data.get() if inventory_data else None'low_stock_count', 0) if inventory_data else None if inventory_data else 0,
            'out_of_stock_items': inventory_data.get() if inventory_data else None'out_of_stock_count', 0) if inventory_data else None if inventory_data else 0
        }

        # 성장률 계산 (시뮬레이션)
        growth_metrics = {
            'revenue_growth': 12.5,  # 12.5% 증가
            'order_growth': 8.3,     # 8.3% 증가
            'customer_growth': 15.2,  # 15.2% 증가
            'efficiency_growth': 5.8  # 5.8% 증가
        }

        dashboard_data = {
            'kpis': kpis,
            'growth_metrics': growth_metrics,
            'sales_summary': sales_data,
            'staff_summary': staff_data,
            'inventory_summary': inventory_data,
            'last_updated': datetime.utcnow().isoformat()
        }

        return jsonify(dashboard_data), 200

    except Exception as e:
        current_app.logger.error(f"분석 대시보드 API 오류: {str(e)}")
        return jsonify({'message': '대시보드 데이터 조회 중 오류가 발생했습니다'}), 500

# 캐시 관리 API


@analytics.route('/cache/clear', methods=['POST'])
@token_required
@role_required(['super_admin'])
def clear_analytics_cache(current_user):
    """분석 데이터 캐시 정리"""
    try:
        global _analytics_cache, _cache_expiry
        _analytics_cache.clear()
        _cache_expiry.clear()

        return jsonify({'message': '캐시가 정리되었습니다'}), 200

    except Exception as e:
        current_app.logger.error(f"캐시 정리 오류: {str(e)}")
        return jsonify({'message': '캐시 정리 중 오류가 발생했습니다'}), 500
