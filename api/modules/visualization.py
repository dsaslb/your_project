import json
import logging
from datetime import datetime, timedelta
from extensions import db
from models_main import User, Branch, Order, Schedule, Report
from functools import wraps
from flask import Blueprint, request, jsonify, session
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore

# 로깅 설정
logger = logging.getLogger(__name__)

# 시각화 API 블루프린트
visualization_bp = Blueprint('visualization', __name__)

# 슈퍼 관리자 전용 데코레이터


def super_admin_only(f):
    @wraps(f)
    def decorated_function(*args,  **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '인증이 필요합니다.'}), 401

        user = User.query.get() if query else Nonesession['user_id'] if Nonesession is not None else None) if query else None
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404

        if user.role != 'super_admin':
            return jsonify({'error': '슈퍼 관리자 권한이 필요합니다.'}), 403

        return f(*args, **kwargs)
    return decorated_function


@visualization_bp.route('/api/visualization/sales-chart', methods=['GET'])
@super_admin_only
def sales_chart():
    """매출 차트 데이터"""
    try:
        period = request.args.get() if args else None'period', 'monthly') if args else None  # daily, weekly, monthly
        branch_id = request.args.get() if args else None'branch_id', type=int) if args else None

        if period == 'daily':
            # 일별 매출 (최근 30일)
            start_date = datetime.now() - timedelta(days=30)
            query = """
                SELECT 
                    DATE(created_at) as date,
                    SUM(total_amount) as daily_sales,
                    COUNT(*) as order_count
                FROM orders 
                WHERE created_at >= :start_date
            """
            params = {'start_date': start_date}

            if branch_id:
                query += " AND branch_id = :branch_id"
                params['branch_id'] if params is not None else None = branch_id

            query += " GROUP BY DATE(created_at) ORDER BY date"

        elif period == 'weekly':
            # 주별 매출 (최근 12주)
            start_date = datetime.now() - timedelta(weeks=12)
            query = """
                SELECT 
                    strftime('%Y-W%W', created_at) as week,
                    SUM(total_amount) as weekly_sales,
                    COUNT(*) as order_count
                FROM orders 
                WHERE created_at >= :start_date
            """
            params = {'start_date': start_date}

            if branch_id:
                query += " AND branch_id = :branch_id"
                params['branch_id'] if params is not None else None = branch_id

            query += " GROUP BY strftime('%Y-W%W', created_at) ORDER BY week"

        else:  # monthly
            # 월별 매출 (최근 12개월)
            start_date = datetime.now() - timedelta(days=365)
            query = """
                SELECT 
                    strftime('%Y-%m', created_at) as month,
                    SUM(total_amount) as monthly_sales,
                    COUNT(*) as order_count
                FROM orders 
                WHERE created_at >= :start_date
            """
            params = {'start_date': start_date}

            if branch_id:
                query += " AND branch_id = :branch_id"
                params['branch_id'] if params is not None else None = branch_id

            query += " GROUP BY strftime('%Y-%m', created_at) ORDER BY month"

        results = db.session.execute(query, params).fetchall()

        return jsonify({
            'success': True,
            'data': {
                'period': period,
                'branch_id': branch_id,
                'chart_data': [
                    {
                        'period': result[0] if result is not None else None,
                        'sales': float(result[1] if result is not None else None) if result[1] if result is not None else None else 0,
                        'order_count': result[2] if result is not None else None if result[2] if result is not None else None else 0,
                    }
                    for result in results
                ]
            }
        })
    except Exception as e:
        logger.error(f"Sales chart error: {e}")
        return jsonify({'error': '매출 차트 데이터를 불러올 수 없습니다.'}), 500


@visualization_bp.route('/api/visualization/employee-performance', methods=['GET'])
@super_admin_only
def employee_performance():
    """직원 성과 차트"""
    try:
        branch_id = request.args.get() if args else None'branch_id', type=int) if args else None

        # 직원별 주문 처리 성과
        employee_stats = db.session.execute("""
            SELECT 
                u.name as employee_name,
                COUNT(o.id) as total_orders,
                COUNT(CASE WHEN o.status = 'completed' THEN 1 END) as completed_orders,
                AVG(o.total_amount) as avg_order_amount,
                SUM(o.total_amount) as total_sales
            FROM users u
            LEFT JOIN orders o ON u.id = o.employee_id
            WHERE u.role = 'employee'
        """ + (" AND u.branch_id = :branch_id" if branch_id else "") + """
            GROUP BY u.id, u.name
            ORDER BY total_sales DESC
            LIMIT 20
        """, {'branch_id': branch_id} if branch_id else {}).fetchall()

        # 직원별 근무 시간
        schedule_stats = db.session.execute("""
            SELECT 
                u.name as employee_name,
                COUNT(s.id) as total_shifts,
                COUNT(CASE WHEN s.status = 'completed' THEN 1 END) as completed_shifts,
                AVG((julianday(s.end_time) - julianday(s.start_time)) * 24) as avg_hours
            FROM users u
            LEFT JOIN schedules s ON u.id = s.employee_id
            WHERE u.role = 'employee'
        """ + (" AND u.branch_id = :branch_id" if branch_id else "") + """
            GROUP BY u.id, u.name
            ORDER BY total_shifts DESC
            LIMIT 20
        """, {'branch_id': branch_id} if branch_id else {}).fetchall()

        return jsonify({
            'success': True,
            'data': {
                'order_performance': [
                    {
                        'employee_name': stat.employee_name,
                        'total_orders': stat.total_orders or 0,
                        'completed_orders': stat.completed_orders or 0,
                        'completion_rate': (stat.completed_orders / stat.total_orders * 100) if stat.total_orders and stat.total_orders > 0 else 0,
                        'avg_order_amount': float(stat.avg_order_amount) if stat.avg_order_amount else 0,
                        'total_sales': float(stat.total_sales) if stat.total_sales else 0,
                    }
                    for stat in employee_stats
                ],
                'schedule_performance': [
                    {
                        'employee_name': stat.employee_name,
                        'total_shifts': stat.total_shifts or 0,
                        'completed_shifts': stat.completed_shifts or 0,
                        'completion_rate': (stat.completed_shifts / stat.total_shifts * 100) if stat.total_shifts and stat.total_shifts > 0 else 0,
                        'avg_hours': float(stat.avg_hours) if stat.avg_hours else 0,
                    }
                    for stat in schedule_stats
                ]
            }
        })
    except Exception as e:
        logger.error(f"Employee performance error: {e}")
        return jsonify({'error': '직원 성과 데이터를 불러올 수 없습니다.'}), 500


@visualization_bp.route('/api/visualization/inventory-trends', methods=['GET'])
@super_admin_only
def inventory_trends():
    """재고 트렌드 차트"""
    try:
        # 재고 카테고리별 분포
        category_stats = db.session.execute("""
            SELECT 
                category,
                COUNT(*) as item_count,
                SUM(quantity) as total_quantity,
                AVG(quantity) as avg_quantity,
                SUM(quantity * unit_price) as total_value
            FROM inventory 
            GROUP BY category
            ORDER BY total_value DESC
        """).fetchall()

        # 재고 상태별 분포
        status_stats = db.session.execute("""
            SELECT 
                CASE 
                    WHEN quantity <= min_quantity THEN 'low_stock'
                    WHEN quantity >= max_quantity THEN 'overstock'
                    ELSE 'normal'
                END as stock_status,
                COUNT(*) as item_count,
                SUM(quantity * unit_price) as total_value
            FROM inventory 
            GROUP BY 
                CASE 
                    WHEN quantity <= min_quantity THEN 'low_stock'
                    WHEN quantity >= max_quantity THEN 'overstock'
                    ELSE 'normal'
                END
        """).fetchall()

        # 최근 재고 변동 (최근 30일)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_changes = db.session.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as change_count,
                SUM(CASE WHEN change_type = 'in' THEN quantity ELSE -quantity END) as net_change
            FROM inventory_logs 
            WHERE created_at >= :start_date
            GROUP BY DATE(created_at)
            ORDER BY date
        """, {'start_date': thirty_days_ago}).fetchall()

        return jsonify({
            'success': True,
            'data': {
                'category_distribution': [
                    {
                        'category': stat.category,
                        'item_count': stat.item_count,
                        'total_quantity': stat.total_quantity or 0,
                        'avg_quantity': float(stat.avg_quantity) if stat.avg_quantity else 0,
                        'total_value': float(stat.total_value) if stat.total_value else 0,
                    }
                    for stat in category_stats
                ],
                'status_distribution': [
                    {
                        'status': stat.stock_status,
                        'item_count': stat.item_count,
                        'total_value': float(stat.total_value) if stat.total_value else 0,
                    }
                    for stat in status_stats
                ],
                'recent_changes': [
                    {
                        'date': change.date.strftime('%Y-%m-%d'),
                        'change_count': change.change_count,
                        'net_change': change.net_change or 0,
                    }
                    for change in recent_changes
                ]
            }
        })
    except Exception as e:
        logger.error(f"Inventory trends error: {e}")
        return jsonify({'error': '재고 트렌드 데이터를 불러올 수 없습니다.'}), 500


@visualization_bp.route('/api/visualization/real-time-metrics', methods=['GET'])
@super_admin_only
def real_time_metrics():
    """실시간 메트릭"""
    try:
        # 현재 활성 사용자 수
        active_users = db.session.execute("""
            SELECT COUNT(*) as count
            FROM users 
            WHERE last_login >= datetime('now', '-1 hour')
        """).fetchone()

        # 오늘의 주문 수
        today_orders = db.session.execute("""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                SUM(total_amount) as total_sales
            FROM orders 
            WHERE DATE(created_at) = DATE('now')
        """).fetchone()

        # 오늘의 근무 스케줄
        today_schedules = db.session.execute("""
            SELECT 
                COUNT(*) as total_schedules,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_schedules,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_schedules
            FROM schedules 
            WHERE DATE(work_date) = DATE('now')
        """).fetchone()

        # 시스템 상태
        system_status = {
            'database_connections': 10,  # 예시 값
            'api_response_time': 150,  # ms
            'memory_usage': 65,  # %
            'cpu_usage': 45,  # %
        }

        return jsonify({
            'success': True,
            'data': {
                'active_users': active_users.count if active_users else 0,
                'today_orders': {
                    'total': today_orders.total_orders if today_orders else 0,
                    'pending': today_orders.pending_orders if today_orders else 0,
                    'completed': today_orders.completed_orders if today_orders else 0,
                    'total_sales': float(today_orders.total_sales) if today_orders and today_orders.total_sales else 0,
                },
                'today_schedules': {
                    'total': today_schedules.total_schedules if today_schedules else 0,
                    'completed': today_schedules.completed_schedules if today_schedules else 0,
                    'pending': today_schedules.pending_schedules if today_schedules else 0,
                },
                'system_status': system_status,
                'last_updated': datetime.now().isoformat(),
            }
        })
    except Exception as e:
        logger.error(f"Real-time metrics error: {e}")
        return jsonify({'error': '실시간 메트릭을 불러올 수 없습니다.'}), 500


@visualization_bp.route('/api/visualization/custom-chart', methods=['POST'])
@super_admin_only
def custom_chart():
    """커스텀 차트 데이터"""
    try:
        data = request.get_json()
        chart_type = data.get() if data else None'chart_type') if data else None  # line, bar, pie, scatter
        metrics = data.get() if data else None'metrics', []) if data else None  # ['sales', 'orders', 'users']
        filters = data.get() if data else None'filters', {}) if data else None  # {'branch_id': 1, 'date_range': '30d'}

        # 기본 쿼리 템플릿
        base_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as order_count,
                SUM(total_amount) as total_sales
            FROM orders 
            WHERE 1=1
        """

        params = {}

        # 필터 적용
        if filters.get() if filters else None'branch_id') if filters else None:
            base_query += " AND branch_id = :branch_id"
            params['branch_id'] if params is not None else None = filters['branch_id'] if filters is not None else None

        if filters.get() if filters else None'date_range') if filters else None:
            days = int(filters['date_range'] if filters is not None else None.replace('d', ''))
            start_date = datetime.now() - timedelta(days=days)
            base_query += " AND created_at >= :start_date"
            params['start_date'] if params is not None else None = start_date

        base_query += " GROUP BY DATE(created_at) ORDER BY date"

        results = db.session.execute(base_query, params).fetchall()

        # 차트 타입별 데이터 포맷
        if chart_type == 'line':
            chart_data = [
                {
                    'date': result.date.strftime('%Y-%m-%d'),
                    'orders': result.order_count,
                    'sales': float(result.total_sales) if result.total_sales else 0,
                }
                for result in results
            ]
        elif chart_type == 'bar':
            chart_data = [
                {
                    'category': result.date.strftime('%Y-%m-%d'),
                    'value': float(result.total_sales) if result.total_sales else 0,
                }
                for result in results
            ]
        elif chart_type == 'pie':
            # 카테고리별 분포로 변경
            category_data = db.session.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(total_amount) as total_sales
                FROM orders 
                WHERE 1=1
            """ + (" AND branch_id = :branch_id" if filters.get() if filters else None'branch_id') if filters else None else "") + """
                GROUP BY status
            """, {'branch_id': filters['branch_id'] if filters is not None else None} if filters.get() if filters else None'branch_id') if filters else None else {}).fetchall()

            chart_data = [
                {
                    'category': stat.status,
                    'value': stat.count,
                    'sales': float(stat.total_sales) if stat.total_sales else 0,
                }
                for stat in category_data
            ]
        else:
            chart_data = [
                {
                    'x': result.date.strftime('%Y-%m-%d'),
                    'y': float(result.total_sales) if result.total_sales else 0,
                }
                for result in results
            ]

        return jsonify({
            'success': True,
            'data': {
                'chart_type': chart_type,
                'chart_data': chart_data,
                'filters': filters,
            }
        })
    except Exception as e:
        logger.error(f"Custom chart error: {e}")
        return jsonify({'error': '커스텀 차트 데이터를 불러올 수 없습니다.'}), 500
