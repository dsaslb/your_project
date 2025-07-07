from flask import Blueprint, request, jsonify, session
from functools import wraps
from models import User, UserRole
from extensions import db
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 역할별 라우팅 블루프린트
role_routes = Blueprint('role_routes', __name__)

# 권한 데코레이터
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': '인증이 필요합니다.'}), 401
            
            user = User.query.get(session['user_id'])
            if not user:
                return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
            
            if user.role != required_role:
                return jsonify({'error': '권한이 없습니다.'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 슈퍼 관리자 전용 데코레이터
def super_admin_only(f):
    return require_role(UserRole.SUPER_ADMIN)(f)

# 브랜드 관리자 전용 데코레이터
def brand_manager_only(f):
    return require_role(UserRole.BRAND_MANAGER)(f)

# 매장 관리자 전용 데코레이터
def store_manager_only(f):
    return require_role(UserRole.STORE_MANAGER)(f)

# 직원 전용 데코레이터
def employee_only(f):
    return require_role(UserRole.EMPLOYEE)(f)

# 관리자 전용 데코레이터 (슈퍼, 브랜드, 매장)
def manager_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '인증이 필요합니다.'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        if user.role not in [UserRole.SUPER_ADMIN, UserRole.BRAND_MANAGER, UserRole.STORE_MANAGER]:
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# 슈퍼 관리자 전용 API
# ============================================================================

@role_routes.route('/api/super-admin/dashboard', methods=['GET'])
@super_admin_only
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
@super_admin_only
def super_admin_users():
    """전체 사용자 목록 (슈퍼 관리자만)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        branch_filter = request.args.get('branch_id', type=int)
        
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
@super_admin_only
def update_user_status(user_id):
    """사용자 상태 변경 (승인/차단)"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'approve' or 'block'
        
        user = User.query.get(user_id)
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
@brand_manager_only
def brand_manager_dashboard():
    """브랜드 관리자 대시보드 데이터"""
    try:
        user = User.query.get(session['user_id'])
        
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
@brand_manager_only
def approve_store_manager(user_id):
    """매장 관리자 승인"""
    try:
        user = User.query.get(user_id)
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
@store_manager_only
def store_manager_dashboard():
    """매장 관리자 대시보드 데이터"""
    try:
        user = User.query.get(session['user_id'])
        
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
@employee_only
def employee_dashboard():
    """직원 대시보드 데이터"""
    try:
        user = User.query.get(session['user_id'])
        
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
def get_profile():
    """현재 사용자 프로필 정보"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': '인증이 필요합니다.'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'branch_id': user.branch_id,
                'is_active': user.is_active,
                'is_approved': user.is_approved,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
        })
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': '프로필 정보를 불러올 수 없습니다.'}), 500

@role_routes.route('/api/common/profile', methods=['PUT'])
def update_profile():
    """프로필 정보 수정"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': '인증이 필요합니다.'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        data = request.get_json()
        
        # 수정 가능한 필드들
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '프로필이 업데이트되었습니다.'
        })
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        db.session.rollback()
        return jsonify({'error': '프로필 업데이트에 실패했습니다.'}), 500 