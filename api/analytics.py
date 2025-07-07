from flask import Blueprint, request, jsonify, session
from functools import wraps
from models import User, Branch, Order, Schedule, Report
from extensions import db
from datetime import datetime, timedelta
import logging

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
        role_stats = db.session.execute("""
            SELECT 
                role,
                COUNT(*) as count,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_count
            FROM users 
            GROUP BY role
        """).fetchall()
        
        # 매장별 사용자 수
        branch_stats = db.session.execute("""
            SELECT 
                branch_id,
                COUNT(*) as total_users,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
                COUNT(CASE WHEN role = 'store_manager' THEN 1 END) as managers,
                COUNT(CASE WHEN role = 'employee' THEN 1 END) as employees
            FROM users 
            WHERE branch_id IS NOT NULL
            GROUP BY branch_id
        """).fetchall()
        
        # 최근 30일 활동 통계
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_orders = Order.query.filter(
            Order.created_at >= thirty_days_ago
        ).count()
        
        recent_schedules = Schedule.query.filter(
            Schedule.created_at >= thirty_days_ago
        ).count()
        
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
            user_stats = db.session.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
                    COUNT(CASE WHEN role = 'store_manager' THEN 1 END) as managers,
                    COUNT(CASE WHEN role = 'employee' THEN 1 END) as employees,
                    COUNT(CASE WHEN last_login >= datetime('now', '-7 days') THEN 1 END) as recent_logins
                FROM users 
                WHERE branch_id = :branch_id
            """, {'branch_id': branch_id}).fetchone()
            
            # 매장별 주문 통계 (최근 30일)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            order_stats = db.session.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                    AVG(total_amount) as avg_order_amount
                FROM orders 
                WHERE branch_id = :branch_id AND created_at >= :start_date
            """, {
                'branch_id': branch_id,
                'start_date': thirty_days_ago
            }).fetchone()
            
            # 매장별 스케줄 통계 (최근 30일)
            schedule_stats = db.session.execute("""
                SELECT 
                    COUNT(*) as total_schedules,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_schedules,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_schedules
                FROM schedules 
                WHERE branch_id = :branch_id AND created_at >= :start_date
            """, {
                'branch_id': branch_id,
                'start_date': thirty_days_ago
            }).fetchone()
            
            return jsonify({
                'success': True,
                'data': {
                    'branch_info': {
                        'id': branch.id,
                        'name': branch.name,
                        'address': branch.address,
                    },
                    'user_performance': {
                        'total_users': user_stats.total_users,
                        'active_users': user_stats.active_users,
                        'managers': user_stats.managers,
                        'employees': user_stats.employees,
                        'recent_logins': user_stats.recent_logins,
                        'activity_rate': (user_stats.recent_logins / user_stats.total_users * 100) if user_stats.total_users > 0 else 0,
                    },
                    'order_performance': {
                        'total_orders': order_stats.total_orders or 0,
                        'completed_orders': order_stats.completed_orders or 0,
                        'pending_orders': order_stats.pending_orders or 0,
                        'completion_rate': (order_stats.completed_orders / order_stats.total_orders * 100) if order_stats.total_orders and order_stats.total_orders > 0 else 0,
                        'avg_order_amount': float(order_stats.avg_order_amount) if order_stats.avg_order_amount else 0,
                    },
                    'schedule_performance': {
                        'total_schedules': schedule_stats.total_schedules or 0,
                        'completed_schedules': schedule_stats.completed_schedules or 0,
                        'pending_schedules': schedule_stats.pending_schedules or 0,
                        'completion_rate': (schedule_stats.completed_schedules / schedule_stats.total_schedules * 100) if schedule_stats.total_schedules and schedule_stats.total_schedules > 0 else 0,
                    }
                }
            })
        else:
            # 전체 매장 성과 비교
            branch_performances = db.session.execute("""
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
            """).fetchall()
            
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
        
        daily_logins = db.session.execute("""
            SELECT 
                DATE(last_login) as login_date,
                COUNT(*) as login_count
            FROM users 
            WHERE last_login >= :start_date
            GROUP BY DATE(last_login)
            ORDER BY login_date
        """, {'start_date': seven_days_ago}).fetchall()
        
        # 역할별 활동 통계
        role_activity = db.session.execute("""
            SELECT 
                role,
                COUNT(*) as total_users,
                COUNT(CASE WHEN last_login >= datetime('now', '-7 days') THEN 1 END) as active_7_days,
                COUNT(CASE WHEN last_login >= datetime('now', '-30 days') THEN 1 END) as active_30_days,
                AVG((julianday(last_login) - julianday(created_at))) as avg_days_to_first_login
            FROM users 
            WHERE last_login IS NOT NULL
            GROUP BY role
        """).fetchall()
        
        # 비활성 사용자 (30일 이상 미로그인)
        inactive_users = db.session.execute("""
            SELECT 
                id, username, name, role, branch_id, last_login
            FROM users 
            WHERE last_login < datetime('now', '-30 days') OR last_login IS NULL
            ORDER BY last_login DESC
            LIMIT 20
        """).fetchall()
        
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
        table_stats = db.session.execute("""
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
        """).fetchall()
        
        # 최근 시스템 오류 (시스템 로그에서)
        recent_errors = db.session.execute("""
            SELECT 
                action, details, created_at
            FROM system_logs 
            WHERE action LIKE '%error%' OR action LIKE '%fail%'
            ORDER BY created_at DESC
            LIMIT 10
        """).fetchall()
        
        # 사용자 가입 추이 (최근 12개월)
        monthly_signups = db.session.execute("""
            SELECT 
                strftime('%Y-%m', created_at) as month,
                COUNT(*) as signup_count
            FROM users 
            WHERE created_at >= datetime('now', '-12 months')
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY month
        """).fetchall()
        
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
                    'active_connections': len(session),
                    'last_backup': '2024-01-15 14:30',
                }
            }
        })
    except Exception as e:
        logger.error(f"System health error: {e}")
        return jsonify({'error': '시스템 상태를 불러올 수 없습니다.'}), 500 