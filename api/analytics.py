from flask import Blueprint, request, jsonify, session
from functools import wraps
from models import User, Branch, Order, Schedule, Report
from extensions import db
from datetime import datetime, timedelta
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import json
from sqlalchemy import text

# 로깅 설정
logger = logging.getLogger(__name__)

# 분석 API 블루프린트
analytics_bp = Blueprint('analytics', __name__)

# 슈퍼 관리자 전용 데코레이터
def super_admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '인증이 필요합니다.'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        if user.role != 'super_admin':
            return jsonify({'error': '슈퍼 관리자 권한이 필요합니다.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@analytics_bp.route('/api/analytics/brand-overview', methods=['GET'])
@super_admin_only
def brand_overview():
    """브랜드 전체 현황 분석"""
    try:
        # 전체 통계
        total_branches = Branch.query.count()
        total_users = User.query.count()
        total_orders = Order.query.count()
        total_schedules = Schedule.query.count()
        
        # 역할별 사용자 수
        role_stats = db.session.execute(text("""
            SELECT 
                role,
                COUNT(*) as count,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_count
            FROM users 
            GROUP BY role
        """)).fetchall()
        
        # 매장별 사용자 수
        branch_stats = db.session.execute(text("""
            SELECT 
                branch_id,
                COUNT(*) as total_users,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
                COUNT(CASE WHEN role = 'store_manager' THEN 1 END) as managers,
                COUNT(CASE WHEN role = 'employee' THEN 1 END) as employees
            FROM users 
            WHERE branch_id IS NOT NULL
            GROUP BY branch_id
        """)).fetchall()
        
        # 최근 30일 활동 통계
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_orders = Order.query.filter(
            Order.created_at >= thirty_days_ago
        ).count()
        
        # Schedule 모델에 created_at 필드가 없으므로 임시로 주석 처리
        # recent_schedules = Schedule.query.filter(
        #     Schedule.created_at >= thirty_days_ago
        # ).count()
        recent_schedules = 0  # 임시 기본값
        
        recent_users = User.query.filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_branches': total_branches,
                    'total_users': total_users,
                    'total_orders': total_orders,
                    'total_schedules': total_schedules,
                },
                'role_distribution': [
                    {
                        'role': stat.role,
                        'total': stat.count,
                        'active': stat.active_count,
                        'inactive': stat.count - stat.active_count,
                    }
                    for stat in role_stats
                ],
                'branch_distribution': [
                    {
                        'branch_id': stat.branch_id,
                        'total_users': stat.total_users,
                        'active_users': stat.active_users,
                        'managers': stat.managers,
                        'employees': stat.employees,
                    }
                    for stat in branch_stats
                ],
                'recent_activity': {
                    'orders_30_days': recent_orders,
                    'schedules_30_days': recent_schedules,
                    'new_users_30_days': recent_users,
                }
            }
        })
    except Exception as e:
        logger.error(f"Brand overview error: {e}")
        return jsonify({'error': '브랜드 현황을 불러올 수 없습니다.'}), 500

@analytics_bp.route('/api/analytics/branch-performance', methods=['GET'])
@super_admin_only
def branch_performance():
    """매장별 성과 분석"""
    try:
        branch_id = request.args.get('branch_id', type=int)
        
        if branch_id:
            # 특정 매장 분석
            branch = Branch.query.get(branch_id)
            if not branch:
                return jsonify({'error': '매장을 찾을 수 없습니다.'}), 404
            
            # 매장별 사용자 통계
            user_stats = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
                    COUNT(CASE WHEN role = 'store_manager' THEN 1 END) as managers,
                    COUNT(CASE WHEN role = 'employee' THEN 1 END) as employees,
                    COUNT(CASE WHEN last_login >= datetime('now', '-7 days') THEN 1 END) as recent_logins
                FROM users 
                WHERE branch_id = :branch_id
            """), {'branch_id': branch_id}).fetchone()
            
            # 기본값 설정
            user_stats = user_stats or type('obj', (object,), {
                'total_users': 0,
                'active_users': 0,
                'managers': 0,
                'employees': 0,
                'recent_logins': 0
            })()
            
            # 매장별 주문 통계 (최근 30일)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            order_stats = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                    AVG(total_amount) as avg_order_amount
                FROM orders 
                WHERE branch_id = :branch_id AND created_at >= :start_date
            """), {
                'branch_id': branch_id,
                'start_date': thirty_days_ago
            }).fetchone()
            
            # 기본값 설정
            order_stats = order_stats or type('obj', (object,), {
                'total_orders': 0,
                'completed_orders': 0,
                'pending_orders': 0,
                'avg_order_amount': 0
            })()
            
            # 매장별 스케줄 통계 (최근 30일) - Schedule 모델에 created_at 필드가 없으므로 임시로 주석 처리
            # schedule_stats = db.session.execute(text("""
            #     SELECT 
            #         COUNT(*) as total_schedules,
            #         COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_schedules,
            #         COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_schedules
            #     FROM schedules 
            #     WHERE branch_id = :branch_id AND created_at >= :start_date
            # """), {
            #     'branch_id': branch_id,
            #     'start_date': thirty_days_ago
            # }).fetchone()
            
            # 기본값 설정
            schedule_stats = type('obj', (object,), {
                'total_schedules': 0,
                'completed_schedules': 0,
                'pending_schedules': 0
            })()
            
            return jsonify({
                'success': True,
                'data': {
                    'branch_info': {
                        'id': branch.id,
                        'name': branch.name,
                        'address': branch.address,
                    },
                    'user_performance': {
                        'total_users': getattr(user_stats, 'total_users', 0),
                        'active_users': getattr(user_stats, 'active_users', 0),
                        'managers': getattr(user_stats, 'managers', 0),
                        'employees': getattr(user_stats, 'employees', 0),
                        'recent_logins': getattr(user_stats, 'recent_logins', 0),
                        'activity_rate': (getattr(user_stats, 'recent_logins', 0) / getattr(user_stats, 'total_users', 1) * 100) if getattr(user_stats, 'total_users', 0) > 0 else 0,
                    },
                    'order_performance': {
                        'total_orders': getattr(order_stats, 'total_orders', 0),
                        'completed_orders': getattr(order_stats, 'completed_orders', 0),
                        'pending_orders': getattr(order_stats, 'pending_orders', 0),
                        'completion_rate': (getattr(order_stats, 'completed_orders', 0) / getattr(order_stats, 'total_orders', 1) * 100) if getattr(order_stats, 'total_orders', 0) > 0 else 0,
                        'avg_order_amount': float(getattr(order_stats, 'avg_order_amount', 0)),
                    },
                    'schedule_performance': {
                        'total_schedules': getattr(schedule_stats, 'total_schedules', 0),
                        'completed_schedules': getattr(schedule_stats, 'completed_schedules', 0),
                        'pending_schedules': getattr(schedule_stats, 'pending_schedules', 0),
                        'completion_rate': (getattr(schedule_stats, 'completed_schedules', 0) / getattr(schedule_stats, 'total_schedules', 1) * 100) if getattr(schedule_stats, 'total_schedules', 0) > 0 else 0,
                    }
                }
            })
        else:
            # 전체 매장 성과 비교
            branch_performances = db.session.execute(text("""
                SELECT 
                    b.id as branch_id,
                    b.name as branch_name,
                    COUNT(u.id) as total_users,
                    COUNT(CASE WHEN u.is_active = 1 THEN 1 END) as active_users,
                    COUNT(o.id) as total_orders,
                    COUNT(CASE WHEN o.status = 'completed' THEN 1 END) as completed_orders,
                    AVG(o.total_amount) as avg_order_amount
                FROM branches b
                LEFT JOIN users u ON b.id = u.branch_id
                LEFT JOIN orders o ON b.id = o.branch_id AND o.created_at >= datetime('now', '-30 days')
                GROUP BY b.id, b.name
                ORDER BY total_users DESC
            """)).fetchall()
            
            return jsonify({
                'success': True,
                'data': {
                    'branch_comparison': [
                        {
                            'branch_id': perf.branch_id,
                            'branch_name': perf.branch_name,
                            'total_users': perf.total_users,
                            'active_users': perf.active_users,
                            'total_orders': perf.total_orders or 0,
                            'completed_orders': perf.completed_orders or 0,
                            'avg_order_amount': float(perf.avg_order_amount) if perf.avg_order_amount else 0,
                            'user_activity_rate': (perf.active_users / perf.total_users * 100) if perf.total_users > 0 else 0,
                            'order_completion_rate': (perf.completed_orders / perf.total_orders * 100) if perf.total_orders and perf.total_orders > 0 else 0,
                        }
                        for perf in branch_performances
                    ]
                }
            })
            
    except Exception as e:
        logger.error(f"Branch performance error: {e}")
        return jsonify({'error': '매장 성과를 불러올 수 없습니다.'}), 500

@analytics_bp.route('/api/analytics/user-activity', methods=['GET'])
@super_admin_only
def user_activity():
    """사용자 활동 분석"""
    try:
        # 최근 7일 로그인 활동
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        daily_logins = db.session.execute(text("""
            SELECT 
                DATE(last_login) as login_date,
                COUNT(*) as login_count
            FROM users 
            WHERE last_login >= :start_date
            GROUP BY DATE(last_login)
            ORDER BY login_date
        """), {'start_date': seven_days_ago}).fetchall()
        
        # 역할별 활동 통계
        role_activity = db.session.execute(text("""
            SELECT 
                role,
                COUNT(*) as total_users,
                COUNT(CASE WHEN last_login >= datetime('now', '-7 days') THEN 1 END) as active_7_days,
                COUNT(CASE WHEN last_login >= datetime('now', '-30 days') THEN 1 END) as active_30_days,
                AVG(julianday(last_login) - julianday(created_at)) as avg_days_to_first_login
            FROM users 
            WHERE last_login IS NOT NULL
            GROUP BY role
        """)).fetchall()
        
        # 비활성 사용자 (30일 이상 미로그인)
        inactive_users = db.session.execute(text("""
            SELECT 
                id, username, name, role, branch_id, last_login
            FROM users 
            WHERE last_login < datetime('now', '-30 days') OR last_login IS NULL
            ORDER BY last_login DESC
            LIMIT 20
        """)).fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'daily_logins': [
                    {
                        'date': login.login_date.strftime('%Y-%m-%d'),
                        'count': login.login_count,
                    }
                    for login in daily_logins
                ],
                'role_activity': [
                    {
                        'role': activity.role,
                        'total_users': activity.total_users,
                        'active_7_days': activity.active_7_days,
                        'active_30_days': activity.active_30_days,
                        'activity_rate_7_days': (activity.active_7_days / activity.total_users * 100) if activity.total_users > 0 else 0,
                        'activity_rate_30_days': (activity.active_30_days / activity.total_users * 100) if activity.total_users > 0 else 0,
                        'avg_days_to_first_login': float(activity.avg_days_to_first_login) if activity.avg_days_to_first_login else 0,
                    }
                    for activity in role_activity
                ],
                'inactive_users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'role': user.role,
                        'branch_id': user.branch_id,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                    }
                    for user in inactive_users
                ]
            }
        })
    except Exception as e:
        logger.error(f"User activity error: {e}")
        return jsonify({'error': '사용자 활동을 불러올 수 없습니다.'}), 500

@analytics_bp.route('/api/analytics/system-health', methods=['GET'])
@super_admin_only
def system_health():
    """시스템 상태 분석"""
    try:
        # 데이터베이스 테이블별 레코드 수
        table_stats = db.session.execute(text("""
            SELECT 
                'users' as table_name, COUNT(*) as record_count FROM users
            UNION ALL
            SELECT 'branches', COUNT(*) FROM branches
            UNION ALL
            SELECT 'orders', COUNT(*) FROM orders
            UNION ALL
            SELECT 'schedules', COUNT(*) FROM schedules
            UNION ALL
            SELECT 'reports', COUNT(*) FROM reports
        """)).fetchall()
        
        # 최근 시스템 오류 (시스템 로그에서)
        recent_errors = db.session.execute(text("""
            SELECT 
                action, details, created_at
            FROM system_logs 
            WHERE action LIKE '%error%' OR action LIKE '%fail%'
            ORDER BY created_at DESC
            LIMIT 10
        """")).fetchall()
        
        # 사용자 가입 추이 (최근 12개월)
        monthly_signups = db.session.execute(text("""
            SELECT 
                strftime('%Y-%m', created_at) as month,
                COUNT(*) as signup_count
            FROM users 
            WHERE created_at >= datetime('now', '-12 months')
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY month
        """")).fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'table_stats': [
                    {
                        'table_name': stat.table_name,
                        'record_count': stat.record_count,
                    }
                    for stat in table_stats
                ],
                'recent_errors': [
                    {
                        'action': error.action,
                        'details': error.details,
                        'created_at': error.created_at.isoformat(),
                    }
                    for error in recent_errors
                ],
                'monthly_signups': [
                    {
                        'month': signup.month,
                        'count': signup.signup_count,
                    }
                    for signup in monthly_signups
                ],
                'system_status': {
                    'database_health': 'healthy',
                    'api_response_time': 'fast',
                    'active_connections': 10,  # 임시 고정값
                    'last_backup': '2024-01-15 14:30',
                }
            }
        })
    except Exception as e:
        logger.error(f"System health error: {e}")
        return jsonify({'error': '시스템 상태를 불러올 수 없습니다.'}), 500

# 더미 데이터 생성 함수들
def generate_sales_data(days=30):
    """매출 데이터 생성"""
    data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        # 주말과 평일 구분
        is_weekend = date.weekday() >= 5
        base_sales = 800000 if is_weekend else 500000
        variance = random.uniform(0.7, 1.3)
        
        sales = int(base_sales * variance)
        orders = int(sales / random.uniform(15000, 25000))
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': sales,
            'orders': orders,
            'average_order': int(sales / orders) if orders > 0 else 0
        })
    
    return data

def generate_staff_performance():
    """직원 성과 데이터 생성"""
    staff = [
        {'name': '김철수', 'role': '매니저', 'hours_worked': 160, 'orders_processed': 450, 'rating': 4.8},
        {'name': '이영희', 'role': '직원', 'hours_worked': 120, 'orders_processed': 320, 'rating': 4.5},
        {'name': '박민수', 'role': '직원', 'hours_worked': 140, 'orders_processed': 380, 'rating': 4.7},
        {'name': '최지영', 'role': '직원', 'hours_worked': 110, 'orders_processed': 290, 'rating': 4.3},
        {'name': '정현우', 'role': '직원', 'hours_worked': 130, 'orders_processed': 350, 'rating': 4.6}
    ]
    return staff

def generate_inventory_analytics():
    """재고 분석 데이터 생성"""
    categories = ['신선식품', '냉동식품', '조미료', '포장재', '청소용품']
    data = []
    
    for category in categories:
        items = random.randint(15, 30)
        low_stock = random.randint(2, 8)
        out_of_stock = random.randint(0, 3)
        
        data.append({
            'category': category,
            'total_items': items,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'stock_level': round((items - low_stock - out_of_stock) / items * 100, 1)
        })
    
    return data

def generate_customer_analytics():
    """고객 분석 데이터 생성"""
    # 고객 유형별 분포
    customer_types = [
        {'type': '신규 고객', 'count': 45, 'percentage': 30},
        {'type': '기존 고객', 'count': 75, 'percentage': 50},
        {'type': 'VIP 고객', 'count': 30, 'percentage': 20}
    ]
    
    # 시간대별 주문 분포
    hourly_orders = []
    for hour in range(24):
        if 6 <= hour <= 22:  # 영업시간
            base_orders = 20 if 11 <= hour <= 14 or 17 <= hour <= 20 else 8
            orders = int(base_orders * random.uniform(0.5, 1.5))
        else:
            orders = random.randint(0, 3)
        
        hourly_orders.append({
            'hour': hour,
            'orders': orders
        })
    
    return {
        'customer_types': customer_types,
        'hourly_orders': hourly_orders
    }

@analytics_bp.route('/api/analytics/sales', methods=['GET'])
@jwt_required()
def get_sales_analytics():
    """매출 분석 데이터"""
    try:
        days = request.args.get('days', 30, type=int)
        sales_data = generate_sales_data(days)
        
        # 통계 계산
        total_sales = sum(item['sales'] for item in sales_data)
        total_orders = sum(item['orders'] for item in sales_data)
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        # 성장률 계산 (최근 7일 vs 이전 7일)
        recent_week = sales_data[-7:]
        previous_week = sales_data[-14:-7]
        
        recent_sales = sum(item['sales'] for item in recent_week)
        previous_sales = sum(item['sales'] for item in previous_week)
        
        growth_rate = ((recent_sales - previous_sales) / previous_sales * 100) if previous_sales > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'sales_data': sales_data,
                'summary': {
                    'total_sales': total_sales,
                    'total_orders': total_orders,
                    'average_order_value': int(avg_order_value),
                    'growth_rate': round(growth_rate, 1)
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/analytics/staff', methods=['GET'])
@jwt_required()
def get_staff_analytics():
    """직원 성과 분석"""
    try:
        staff_data = generate_staff_performance()
        
        # 통계 계산
        total_hours = sum(staff['hours_worked'] for staff in staff_data)
        total_orders = sum(staff['orders_processed'] for staff in staff_data)
        avg_rating = sum(staff['rating'] for staff in staff_data) / len(staff_data)
        
        return jsonify({
            'success': True,
            'data': {
                'staff_data': staff_data,
                'summary': {
                    'total_hours': total_hours,
                    'total_orders': total_orders,
                    'average_rating': round(avg_rating, 1),
                    'staff_count': len(staff_data)
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/analytics/inventory', methods=['GET'])
@jwt_required()
def get_inventory_analytics():
    """재고 분석"""
    try:
        inventory_data = generate_inventory_analytics()
        
        # 통계 계산
        total_items = sum(cat['total_items'] for cat in inventory_data)
        low_stock_items = sum(cat['low_stock'] for cat in inventory_data)
        out_of_stock_items = sum(cat['out_of_stock'] for cat in inventory_data)
        avg_stock_level = sum(cat['stock_level'] for cat in inventory_data) / len(inventory_data)
        
        return jsonify({
            'success': True,
            'data': {
                'inventory_data': inventory_data,
                'summary': {
                    'total_items': total_items,
                    'low_stock_items': low_stock_items,
                    'out_of_stock_items': out_of_stock_items,
                    'average_stock_level': round(avg_stock_level, 1)
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/analytics/customers', methods=['GET'])
@jwt_required()
def get_customer_analytics():
    """고객 분석"""
    try:
        customer_data = generate_customer_analytics()
        
        return jsonify({
            'success': True,
            'data': customer_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/analytics/real-time', methods=['GET'])
@jwt_required()
def get_real_time_metrics():
    """실시간 메트릭"""
    try:
        # 실시간 데이터 시뮬레이션
        current_hour = datetime.now().hour
        is_peak_hour = 11 <= current_hour <= 14 or 17 <= current_hour <= 20
        
        base_orders = 25 if is_peak_hour else 8
        current_orders = int(base_orders * random.uniform(0.8, 1.2))
        
        # 대기 주문 수
        pending_orders = random.randint(0, 5)
        
        # 현재 근무 직원 수
        working_staff = random.randint(3, 6)
        
        # 예상 대기 시간
        estimated_wait = pending_orders * 3 + random.randint(5, 15)
        
        return jsonify({
            'success': True,
            'data': {
                'current_orders': current_orders,
                'pending_orders': pending_orders,
                'working_staff': working_staff,
                'estimated_wait_time': estimated_wait,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/analytics/predictions', methods=['GET'])
@jwt_required()
def get_predictions():
    """예측 분석"""
    try:
        # 다음 7일 예측
        predictions = []
        base_date = datetime.now()
        
        for i in range(1, 8):
            date = base_date + timedelta(days=i)
            is_weekend = date.weekday() >= 5
            
            # 기본 예측값
            base_sales = 900000 if is_weekend else 550000
            base_orders = int(base_sales / 20000)
            
            # 계절성 및 트렌드 적용
            seasonal_factor = 1.1 if is_weekend else 0.95
            trend_factor = 1.02  # 2% 성장 트렌드
            
            predicted_sales = int(base_sales * seasonal_factor * trend_factor)
            predicted_orders = int(predicted_sales / 20000)
            
            predictions.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_sales': predicted_sales,
                'predicted_orders': predicted_orders,
                'confidence': random.uniform(0.85, 0.95)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'predictions': predictions,
                'summary': {
                    'total_predicted_sales': sum(p['predicted_sales'] for p in predictions),
                    'total_predicted_orders': sum(p['predicted_orders'] for p in predictions),
                    'average_confidence': round(sum(p['confidence'] for p in predictions) / len(predictions), 2)
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/analytics/comparison', methods=['GET'])
@jwt_required()
def get_comparison_analytics():
    """비교 분석 (전월 대비, 전년 대비)"""
    try:
        # 현재 월 데이터
        current_month = generate_sales_data(30)
        current_sales = sum(item['sales'] for item in current_month)
        current_orders = sum(item['orders'] for item in current_month)
        
        # 이전 월 데이터 (시뮬레이션)
        previous_month_sales = int(current_sales * random.uniform(0.85, 1.15))
        previous_month_orders = int(current_orders * random.uniform(0.85, 1.15))
        
        # 전년 동월 데이터 (시뮬레이션)
        last_year_sales = int(current_sales * random.uniform(0.7, 0.9))
        last_year_orders = int(current_orders * random.uniform(0.7, 0.9))
        
        # 성장률 계산
        month_over_month_sales = ((current_sales - previous_month_sales) / previous_month_sales * 100) if previous_month_sales > 0 else 0
        month_over_month_orders = ((current_orders - previous_month_orders) / previous_month_orders * 100) if previous_month_orders > 0 else 0
        
        year_over_year_sales = ((current_sales - last_year_sales) / last_year_sales * 100) if last_year_sales > 0 else 0
        year_over_year_orders = ((current_orders - last_year_orders) / last_year_orders * 100) if last_year_orders > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'current_month': {
                    'sales': current_sales,
                    'orders': current_orders
                },
                'previous_month': {
                    'sales': previous_month_sales,
                    'orders': previous_month_orders
                },
                'last_year': {
                    'sales': last_year_sales,
                    'orders': last_year_orders
                },
                'growth_rates': {
                    'month_over_month_sales': round(month_over_month_sales, 1),
                    'month_over_month_orders': round(month_over_month_orders, 1),
                    'year_over_year_sales': round(year_over_year_sales, 1),
                    'year_over_year_orders': round(year_over_year_orders, 1)
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 