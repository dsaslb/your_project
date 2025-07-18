from api.gateway import token_required, role_required, admin_required, manager_required, employee_required, log_request  # pyright: ignore
from datetime import datetime, timedelta
import logging
from extensions import db
from models_main import User, UserRole, Staff, Order, Schedule, Attendance, db
from functools import wraps
from flask import Blueprint, request, jsonify, session, g
from flask_login import login_required
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore

# 로깅 설정
logger = logging.getLogger(__name__)

# 역할별 라우팅 블루프린트
role_routes = Blueprint('role_routes', __name__)


def role_required(allowed_roles):
    """역할 기반 접근 제어 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,  **kwargs):
            user = getattr(g, 'current_user', None)
            if not user:
                return jsonify({'error': '인증이 필요합니다'}), 401

            # 최고 관리자는 모든 권한 허용
            if user.role == 'super_admin':
                return f(*args, **kwargs)

            if user.role not in allowed_roles:
                return jsonify({'error': '접근 권한이 없습니다'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# 역할 기반 라우팅 - 권한별 API 엔드포인트 분리
super_admin_routes = Blueprint('super_admin', __name__, url_prefix='/api/super-admin')
admin_routes = Blueprint('admin', __name__, url_prefix='/api/admin')
manager_routes = Blueprint('manager', __name__, url_prefix='/api/manager')
employee_routes = Blueprint('employee', __name__, url_prefix='/api/employee')

# ==================== 최고 관리자 (Super Admin) 라우트 ====================


@super_admin_routes.route('/dashboard', methods=['GET'])
@token_required
@role_required(['super_admin'])
@log_request
def super_admin_dashboard_api():
    """최고 관리자 대시보드"""
    try:
        # 전체 시스템 통계
        total_users = User.query.count()
        total_staff = Staff.query.count()
        total_orders = Order.query.count()

        # 최근 활동
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

        return jsonify({
            'stats': {
                'total_users': total_users,
                'total_staff': total_staff,
                'total_orders': total_orders,
                'total_inventory': 0  # Inventory 모델이 없으므로 임시로 0
            },
            'recent_users': [{
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'created_at': user.created_at.isoformat()
            } for user in recent_users],
            'recent_orders': [{
                'id': order.id,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat()
            } for order in recent_orders]
        })
    except Exception as e:
        logger.error(f"Super admin dashboard error: {str(e)}")
        return jsonify({'error': 'Dashboard data fetch failed'}), 500


@super_admin_routes.route('/users', methods=['GET'])
@token_required
@role_required(['super_admin'])
@log_request
def get_all_users():
    """전체 사용자 목록 조회"""
    try:
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 20, type=int) if args else None
        role_filter = request.args.get() if args else None'role') if args else None

        query = User.query

        if role_filter:
            query = query.filter(User.role == role_filter)

        users = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'users': [{
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            } for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        })
    except Exception as e:
        logger.error(f"Get all users error: {str(e)}")
        return jsonify({'error': 'Failed to fetch users'}), 500


@super_admin_routes.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@role_required(['super_admin'])
@log_request
def update_user(user_id):
    """사용자 정보 수정"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if 'role' in data:
            user.role = data['role'] if data is not None else None
        if 'is_active' in data:
            user.is_active = data['is_active'] if data is not None else None
        if 'name' in data:
            user.name = data['name'] if data is not None else None
        if 'email' in data:
            user.email = data['email'] if data is not None else None

        db.session.commit()

        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update user error: {str(e)}")
        return jsonify({'error': 'Failed to update user'}), 500


@super_admin_routes.route('/system/stats', methods=['GET'])
@token_required
@role_required(['super_admin'])
@log_request
def system_stats():
    """시스템 전체 통계"""
    try:
        # 역할별 사용자 수
        role_stats = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()

        # 최근 7일 주문 통계
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_orders = Order.query.filter(Order.created_at >= seven_days_ago).all()

        # 일별 주문 수
        daily_orders = {}
        for order in recent_orders if recent_orders is not None:
            date = order.created_at.date().isoformat()
            daily_orders[date] if daily_orders is not None else None = daily_orders.get() if daily_orders else Nonedate, 0) if daily_orders else None + 1

        return jsonify({
            'role_distribution': dict(role_stats),
            'daily_orders': daily_orders,
            'total_orders_7days': len(recent_orders),
            'total_revenue_7days': sum(order.total_amount for order in recent_orders)
        })
    except Exception as e:
        logger.error(f"System stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch system stats'}), 500

# ==================== 관리자 (Admin) 라우트 ====================


@admin_routes.route('/dashboard', methods=['GET'])
@token_required
@role_required(['admin',  'super_admin'])
@log_request
def admin_dashboard_api():
    """관리자 대시보드"""
    try:
        user = g.current_user

        # 관리자 소속 매장 정보
        if user.role == 'admin':
            # 특정 매장 관리자인 경우 해당 매장 데이터만
            staff = Staff.query.filter_by(user_id=user.id).first()
            if staff and hasattr(staff, 'branch_id') and staff.branch_id:
                orders = Order.query.filter_by(branch_id=staff.branch_id).all()
                staff_list = Staff.query.filter_by(branch_id=staff.branch_id).all()
            else:
                orders = []
                staff_list = []
        else:
            # 최고 관리자인 경우 전체 데이터
            orders = Order.query.all()
            staff_list = Staff.query.all()

        return jsonify({
            'stats': {
                'total_orders': len(orders),
                'total_staff': len(staff_list),
                'pending_orders': len([o for o in orders if o.status == 'pending']),
                'completed_orders': len([o for o in orders if o.status == 'completed'])
            },
            'recent_orders': [{
                'id': order.id,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat()
            } for order in orders[-5:] if orders is not None else None]
        })
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        return jsonify({'error': 'Dashboard data fetch failed'}), 500


@admin_routes.route('/staff', methods=['GET'])
@token_required
@role_required(['admin',  'super_admin'])
@log_request
def get_staff_list():
    """직원 목록 조회"""
    try:
        user = g.current_user
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 20, type=int) if args else None

        if user.role == 'admin':
            # 특정 매장 관리자인 경우 해당 매장 직원만
            staff = Staff.query.filter_by(user_id=user.id).first()
            if staff and hasattr(staff, 'branch_id') and staff.branch_id:
                query = Staff.query.filter_by(branch_id=staff.branch_id)
            else:
                query = Staff.query.filter_by(id=0)  # 빈 결과
        else:
            # 최고 관리자인 경우 전체 직원
            query = Staff.query

        staff_list = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'staff': [{
                'id': s.id,
                'name': s.name,
                'position': s.position,
                'phone': s.phone,
                'email': s.email,
                'hire_date': s.hire_date.isoformat() if s.hire_date else None,
                'is_active': s.is_active
            } for s in staff_list.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': staff_list.total,
                'pages': staff_list.pages
            }
        })
    except Exception as e:
        logger.error(f"Get staff list error: {str(e)}")
        return jsonify({'error': 'Failed to fetch staff list'}), 500


@admin_routes.route('/orders', methods=['GET'])
@token_required
@role_required(['admin',  'super_admin'])
@log_request
def get_orders():
    """주문 목록 조회"""
    try:
        user = g.current_user
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 20, type=int) if args else None
        status_filter = request.args.get() if args else None'status') if args else None

        if user.role == 'admin':
            # 특정 매장 관리자인 경우 해당 매장 주문만
            staff = Staff.query.filter_by(user_id=user.id).first()
            if staff and hasattr(staff, 'branch_id') and staff.branch_id:
                query = Order.query.filter_by(branch_id=staff.branch_id)
            else:
                query = Order.query.filter_by(id=0)  # 빈 결과
        else:
            # 최고 관리자인 경우 전체 주문
            query = Order.query

        if status_filter:
            query = query.filter(Order.status == status_filter)

        orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'orders': [{
                'id': order.id,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat(),
                'customer_name': order.customer_name,
                'items_count': len(order.items) if hasattr(order, 'items') else 0
            } for order in orders.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': orders.total,
                'pages': orders.pages
            }
        })
    except Exception as e:
        logger.error(f"Get orders error: {str(e)}")
        return jsonify({'error': 'Failed to fetch orders'}), 500

# ==================== 매니저 (Manager) 라우트 ====================


@manager_routes.route('/dashboard', methods=['GET'])
@token_required
@role_required(['manager',  'admin',  'super_admin'])
@log_request
def manager_dashboard_api():
    """매니저 대시보드"""
    try:
        user = g.current_user

        # 매니저 소속 매장 정보
        staff = Staff.query.filter_by(user_id=user.id).first()
        if not staff or not hasattr(staff, 'branch_id') or not staff.branch_id:
            return jsonify({'error': 'Branch not assigned'}), 400

        # 간단한 대시보드 데이터
        return jsonify({
            'message': 'Manager dashboard data',
            'staff_id': staff.id,
            'branch_id': staff.branch_id
        })
    except Exception as e:
        logger.error(f"Manager dashboard error: {str(e)}")
        return jsonify({'error': 'Dashboard data fetch failed'}), 500


@manager_routes.route('/schedule', methods=['GET'])
@token_required
@role_required(['manager',  'admin',  'super_admin'])
@log_request
def get_schedule():
    """근무 일정 조회"""
    try:
        user = g.current_user
        staff = Staff.query.filter_by(user_id=user.id).first()

        if not staff:
            return jsonify({'error': 'Staff not found'}), 404

        # 간단한 일정 데이터
        return jsonify({
            'message': 'Schedule data',
            'staff_id': staff.id
        })
    except Exception as e:
        logger.error(f"Get schedule error: {str(e)}")
        return jsonify({'error': 'Failed to fetch schedule'}), 500

# ==================== 직원 (Employee) 라우트 ====================


@employee_routes.route('/dashboard', methods=['GET'])
@token_required
@role_required(['employee',  'manager',  'admin',  'super_admin'])
@log_request
def employee_dashboard_api():
    """직원 대시보드"""
    try:
        user = g.current_user
        staff = Staff.query.filter_by(user_id=user.id).first()

        if not staff:
            return jsonify({'error': 'Staff not found'}), 404

        # 최근 주문 (직원이 처리한)
        recent_orders = Order.query.filter_by(staff_id=staff.id).order_by(Order.created_at.desc()).limit(5).all()

        return jsonify({
            'message': 'Employee dashboard data',
            'staff_id': staff.id,
            'recent_orders': [{
                'id': order.id,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat()
            } for order in recent_orders]
        })
    except Exception as e:
        logger.error(f"Employee dashboard error: {str(e)}")
        return jsonify({'error': 'Dashboard data fetch failed'}), 500


@employee_routes.route('/attendance/check-in', methods=['POST'])
@token_required
@role_required(['employee',  'manager',  'admin',  'super_admin'])
@log_request
def check_in():
    """출근 체크"""
    try:
        user = g.current_user
        staff = Staff.query.filter_by(user_id=user.id).first()

        if not staff:
            return jsonify({'error': 'Staff not found'}), 404

        return jsonify({
            'message': 'Checked in successfully',
            'check_in_time': datetime.utcnow().isoformat(),
            'staff_id': staff.id
        })
    except Exception as e:
        logger.error(f"Check in error: {str(e)}")
        return jsonify({'error': 'Failed to check in'}), 500


@employee_routes.route('/attendance/check-out', methods=['POST'])
@token_required
@role_required(['employee',  'manager',  'admin',  'super_admin'])
@log_request
def check_out():
    """퇴근 체크"""
    try:
        user = g.current_user
        staff = Staff.query.filter_by(user_id=user.id).first()

        if not staff:
            return jsonify({'error': 'Staff not found'}), 404

        return jsonify({
            'message': 'Checked out successfully',
            'check_out_time': datetime.utcnow().isoformat(),
            'staff_id': staff.id
        })
    except Exception as e:
        logger.error(f"Check out error: {str(e)}")
        return jsonify({'error': 'Failed to check out'}), 500


@employee_routes.route('/orders/my', methods=['GET'])
@token_required
@role_required(['employee',  'manager',  'admin',  'super_admin'])
@log_request
def get_my_orders():
    """내가 처리한 주문 목록"""
    try:
        user = g.current_user
        staff = Staff.query.filter_by(user_id=user.id).first()

        if not staff:
            return jsonify({'error': 'Staff not found'}), 404

        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 20, type=int) if args else None
        status_filter = request.args.get() if args else None'status') if args else None

        query = Order.query.filter_by(staff_id=staff.id)

        if status_filter:
            query = query.filter(Order.status == status_filter)

        orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'orders': [{
                'id': order.id,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at.isoformat(),
                'customer_name': order.customer_name
            } for order in orders.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': orders.total,
                'pages': orders.pages
            }
        })
    except Exception as e:
        logger.error(f"Get my orders error: {str(e)}")
        return jsonify({'error': 'Failed to fetch orders'}), 500

# ============================================================================
# 슈퍼 관리자 전용 API
# ============================================================================


@role_routes.route('/api/super-admin/dashboard', methods=['GET'])
@role_required(['super_admin'])
def super_admin_dashboard():
    """슈퍼 관리자 대시보드 데이터"""
    try:
        # 전체 시스템 통계
        total_users = User.query.count()
        total_branches = db.session.execute(
            'SELECT COUNT(DISTINCT branch_id) FROM users WHERE branch_id IS NOT NULL'
        ).scalar()

        # 최근 가입자
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

        # 시스템 로그 (최근 10개)
        system_logs = db.session.execute(
            'SELECT * FROM system_logs ORDER BY created_at DESC LIMIT 10'
        ).fetchall()

        return jsonify({
            'success': True,
            'data': {
                'stats': {
                    'total_users': total_users,
                    'total_branches': total_branches,
                    'active_sessions': len(session),
                },
                'recent_users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'role': user.role,
                        'created_at': user.created_at.isoformat(),
                    }
                    for user in recent_users
                ],
                'system_logs': [
                    {
                        'id': log.id,
                        'action': log.action,
                        'user_id': log.user_id,
                        'details': log.details,
                        'created_at': log.created_at.isoformat(),
                    }
                    for log in system_logs
                ]
            }
        })
    except Exception as e:
        logger.error(f"Super admin dashboard error: {e}")
        return jsonify({'error': '대시보드 데이터를 불러올 수 없습니다.'}), 500


@role_routes.route('/api/super-admin/users', methods=['GET'])
@role_required(['super_admin'])
def super_admin_users():
    """전체 사용자 목록 (슈퍼 관리자만)"""
    try:
        page = request.args.get() if args else None'page', 1, type=int) if args else None
        per_page = request.args.get() if args else None'per_page', 20, type=int) if args else None
        role_filter = request.args.get() if args else None'role') if args else None
        branch_filter = request.args.get() if args else None'branch_id', type=int) if args else None

        query = User.query

        if role_filter:
            query = query.filter(User.role == role_filter)

        if branch_filter:
            query = query.filter(User.branch_id == branch_filter)

        users = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'success': True,
            'data': {
                'users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'email': user.email,
                        'role': user.role,
                        'branch_id': user.branch_id,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat(),
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                    }
                    for user in users.items
                ],
                'pagination': {
                    'page': users.page,
                    'per_page': users.per_page,
                    'total': users.total,
                    'pages': users.pages,
                }
            }
        })
    except Exception as e:
        logger.error(f"Super admin users error: {e}")
        return jsonify({'error': '사용자 목록을 불러올 수 없습니다.'}), 500


@role_routes.route('/api/super-admin/users/<int:user_id>/status', methods=['PUT'])
@role_required(['super_admin'])
def update_user_status(user_id):
    """사용자 상태 변경 (승인/차단)"""
    try:
        data = request.get_json()
        action = data.get() if data else None'action') if data else None  # 'approve' or 'block'

        user = User.query.get() if query else Noneuser_id) if query else None
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404

        if action == 'approve':
            user.is_active = True
            user.is_approved = True
        elif action == 'block':
            user.is_active = False
        else:
            return jsonify({'error': '잘못된 액션입니다.'}), 400

        db.session.commit()

        # 시스템 로그 기록
        logger.info(f"User {user_id} status changed to {action} by super admin")

        return jsonify({
            'success': True,
            'message': f'사용자 상태가 {action}되었습니다.'
        })
    except Exception as e:
        logger.error(f"Update user status error: {e}")
        db.session.rollback()
        return jsonify({'error': '사용자 상태 변경에 실패했습니다.'}), 500

# ============================================================================
# 브랜드 관리자 전용 API
# ============================================================================


@role_routes.route('/api/brand-manager/dashboard', methods=['GET'])
@role_required([UserRole.BRAND_MANAGER])
def brand_manager_dashboard():
    """브랜드 관리자 대시보드 데이터"""
    try:
        user = User.query.get() if query else Nonesession['user_id'] if Nonesession is not None else None) if query else None

        # 브랜드별 통계
        branch_stats = db.session.execute("""
            SELECT 
                branch_id,
                COUNT(*) as total_employees,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_employees,
                COUNT(CASE WHEN is_approved = 0 THEN 1 END) as pending_approvals
            FROM users 
            WHERE role IN ('store_manager', 'employee')
            GROUP BY branch_id
        """).fetchall()

        # 승인 대기 중인 사용자
        pending_users = User.query.filter_by(
            is_approved=False,
            role=UserRole.STORE_MANAGER
        ).limit(10).all()

        return jsonify({
            'success': True,
            'data': {
                'branch_stats': [
                    {
                        'branch_id': stat.branch_id,
                        'total_employees': stat.total_employees,
                        'active_employees': stat.active_employees,
                        'pending_approvals': stat.pending_approvals,
                    }
                    for stat in branch_stats
                ],
                'pending_users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'email': user.email,
                        'branch_id': user.branch_id,
                        'created_at': user.created_at.isoformat(),
                    }
                    for user in pending_users
                ]
            }
        })
    except Exception as e:
        logger.error(f"Brand manager dashboard error: {e}")
        return jsonify({'error': '대시보드 데이터를 불러올 수 없습니다.'}), 500


@role_routes.route('/api/brand-manager/users/<int:user_id>/approve', methods=['PUT'])
@role_required([UserRole.BRAND_MANAGER])
def approve_store_manager(user_id):
    """매장 관리자 승인"""
    try:
        user = User.query.get() if query else Noneuser_id) if query else None
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404

        if user.role != UserRole.STORE_MANAGER:
            return jsonify({'error': '매장 관리자만 승인할 수 있습니다.'}), 400

        user.is_approved = True
        user.is_active = True
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '매장 관리자가 승인되었습니다.'
        })
    except Exception as e:
        logger.error(f"Approve store manager error: {e}")
        db.session.rollback()
        return jsonify({'error': '승인 처리에 실패했습니다.'}), 500

# ============================================================================
# 매장 관리자 전용 API
# ============================================================================


@role_routes.route('/api/store-manager/dashboard', methods=['GET'])
@role_required([UserRole.STORE_MANAGER])
def store_manager_dashboard():
    """매장 관리자 대시보드 데이터"""
    try:
        user = User.query.get() if query else Nonesession['user_id'] if Nonesession is not None else None) if query else None

        # 매장 내 직원 통계
        employee_stats = db.session.execute("""
            SELECT 
                COUNT(*) as total_employees,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_employees,
                COUNT(CASE WHEN last_login >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as recent_logins
            FROM users 
            WHERE branch_id = :branch_id AND role = 'employee'
        """, {'branch_id': user.branch_id}).fetchone()

        # 오늘의 스케줄
        today_schedules = db.session.execute("""
            SELECT * FROM schedules 
            WHERE branch_id = :branch_id 
            AND DATE(work_date) = CURDATE()
        """, {'branch_id': user.branch_id}).fetchall()

        return jsonify({
            'success': True,
            'data': {
                'employee_stats': {
                    'total_employees': employee_stats.total_employees,
                    'active_employees': employee_stats.active_employees,
                    'recent_logins': employee_stats.recent_logins,
                },
                'today_schedules': [
                    {
                        'id': schedule.id,
                        'employee_name': schedule.employee_name,
                        'start_time': schedule.start_time.isoformat(),
                        'end_time': schedule.end_time.isoformat(),
                        'status': schedule.status,
                    }
                    for schedule in today_schedules
                ]
            }
        })
    except Exception as e:
        logger.error(f"Store manager dashboard error: {e}")
        return jsonify({'error': '대시보드 데이터를 불러올 수 없습니다.'}), 500

# ============================================================================
# 직원 전용 API
# ============================================================================


@role_routes.route('/api/employee/dashboard', methods=['GET'])
@role_required([UserRole.EMPLOYEE])
def employee_dashboard():
    """직원 대시보드 데이터"""
    try:
        user = User.query.get() if query else Nonesession['user_id'] if Nonesession is not None else None) if query else None

        # 오늘의 스케줄
        today_schedule = db.session.execute("""
            SELECT * FROM schedules 
            WHERE user_id = :user_id 
            AND DATE(work_date) = CURDATE()
        """, {'user_id': user.id}).fetchone()

        # 최근 출퇴근 기록
        recent_attendance = db.session.execute("""
            SELECT * FROM attendance 
            WHERE user_id = :user_id 
            ORDER BY date DESC LIMIT 5
        """, {'user_id': user.id}).fetchall()

        return jsonify({
            'success': True,
            'data': {
                'today_schedule': {
                    'id': today_schedule.id,
                    'start_time': today_schedule.start_time.isoformat(),
                    'end_time': today_schedule.end_time.isoformat(),
                    'status': today_schedule.status,
                } if today_schedule else None,
                'recent_attendance': [
                    {
                        'id': att.id,
                        'date': att.date.isoformat(),
                        'check_in': att.check_in.isoformat() if att.check_in else None,
                        'check_out': att.check_out.isoformat() if att.check_out else None,
                        'status': att.status,
                    }
                    for att in recent_attendance
                ]
            }
        })
    except Exception as e:
        logger.error(f"Employee dashboard error: {e}")
        return jsonify({'error': '대시보드 데이터를 불러올 수 없습니다.'}), 500

# ============================================================================
# 공통 API (모든 역할 접근 가능)
# ============================================================================


@role_routes.route('/api/common/profile', methods=['GET'])
@login_required
def get_profile():
    """현재 사용자 프로필 정보"""
    try:
        user = getattr(g, 'current_user', None) or current_user
        if not user or not user.is_authenticated:
            return jsonify({'error': '인증이 필요합니다.'}), 401

        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'branch_id': user.branch_id,
                'is_active': getattr(user, 'is_active', True),
                'is_approved': getattr(user, 'is_approved', True),
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
        })
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': '프로필 정보를 불러올 수 없습니다.'}), 500


@role_routes.route('/api/common/profile', methods=['PUT'])
@login_required
def update_profile():
    """프로필 정보 수정"""
    try:
        user = getattr(g, 'current_user', None) or current_user
        if not user or not user.is_authenticated:
            return jsonify({'error': '인증이 필요합니다.'}), 401
        data = request.get_json()
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        db.session.commit()
        return jsonify({'success': True, 'message': '프로필이 수정되었습니다.'})
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({'error': '프로필 정보 수정에 실패했습니다.'}), 500
