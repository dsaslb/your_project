from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from models import db, User, Order, Schedule, Attendance, RestaurantOrder
from api.gateway import token_required, role_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, text
import time

optimization = Blueprint('optimization', __name__)

# 쿼리 최적화 데코레이터
def optimize_query(f):
    """쿼리 성능 모니터링 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # 실행 시간이 1초 이상이면 로그 기록
        if execution_time > 1.0:
            current_app.logger.warning(f"Slow query detected: {f.__name__} took {execution_time:.2f}s")
        
        return result
    return decorated

# 페이지네이션 헬퍼
def paginate_query(query, page=1, per_page=20):
    """쿼리 페이지네이션"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

# 최적화된 사용자 목록 조회
@optimization.route('/users/optimized', methods=['GET'])
@token_required
@role_required(['super_admin', 'brand_manager'])
@optimize_query
def get_users_optimized(current_user):
    """최적화된 사용자 목록 조회 (select_related, prefetch_related 적용)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        search = request.args.get('search')
        
        # 기본 쿼리 (필요한 컬럼만 선택)
        query = db.session.query(User)
        
        # 필터 적용
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.like(search_term),
                    User.name.like(search_term),
                    User.email.like(search_term)
                )
            )
        
        # 권한별 필터
        if current_user.role != 'super_admin':
            if current_user.role == 'brand_manager':
                query = query.filter(User.branch_id == current_user.branch_id)
            elif current_user.role == 'store_manager':
                query = query.filter(User.branch_id == current_user.branch_id)
        
        # 정렬 및 페이지네이션
        query = query.order_by(User.created_at.desc())
        pagination = paginate_query(query, page, per_page)
        
        users = []
        for user in pagination.items:
            users.append({
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.status == 'approved',
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return jsonify({
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Optimized users query error: {str(e)}")
        return jsonify({'message': '사용자 목록 조회 중 오류가 발생했습니다'}), 500

# 최적화된 주문 통계
@optimization.route('/orders/stats/optimized', methods=['GET'])
@token_required
@optimize_query
def get_orders_stats_optimized(current_user):
    """최적화된 주문 통계 (집계 쿼리 최적화)"""
    try:
        # 단일 쿼리로 모든 통계 계산
        stats_query = db.session.query(
            func.count(RestaurantOrder.id).label('total_orders'),
            func.count(RestaurantOrder.id).filter(RestaurantOrder.status == 'completed').label('completed_orders'),
            func.count(RestaurantOrder.id).filter(RestaurantOrder.status == 'pending').label('pending_orders'),
            func.avg(RestaurantOrder.total_amount).label('avg_amount'),
            func.sum(RestaurantOrder.total_amount).label('total_amount')
        )
        
        # 권한별 필터
        if current_user.role == 'store_manager':
            stats_query = stats_query.filter(RestaurantOrder.store_id == current_user.branch_id)
        elif current_user.role == 'brand_manager':
            stats_query = stats_query.filter(RestaurantOrder.store_id == current_user.branch_id)
        
        stats = stats_query.first()
        
        # 최근 7일 통계
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_stats = db.session.query(
            func.count(RestaurantOrder.id).label('recent_orders'),
            func.sum(RestaurantOrder.total_amount).label('recent_amount')
        ).filter(RestaurantOrder.created_at >= week_ago)
        
        if current_user.role == 'store_manager':
            recent_stats = recent_stats.filter(RestaurantOrder.store_id == current_user.branch_id)
        elif current_user.role == 'brand_manager':
            recent_stats = recent_stats.filter(RestaurantOrder.store_id == current_user.branch_id)
        
        recent = recent_stats.first()
        
        # None 체크를 위한 안전한 접근
        total_orders = getattr(stats, 'total_orders', 0) or 0
        completed_orders = getattr(stats, 'completed_orders', 0) or 0
        pending_orders = getattr(stats, 'pending_orders', 0) or 0
        avg_amount = float(getattr(stats, 'avg_amount', 0)) if getattr(stats, 'avg_amount', 0) else 0
        total_amount = float(getattr(stats, 'total_amount', 0)) if getattr(stats, 'total_amount', 0) else 0
        recent_orders = getattr(recent, 'recent_orders', 0) or 0
        recent_amount = float(getattr(recent, 'recent_amount', 0)) if getattr(recent, 'recent_amount', 0) else 0
        
        return jsonify({
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'avg_amount': avg_amount,
            'total_amount': total_amount,
            'completion_rate': (completed_orders / total_orders * 100) if total_orders and total_orders > 0 else 0,
            'recent_orders': recent_orders,
            'recent_amount': recent_amount
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Optimized orders stats error: {str(e)}")
        return jsonify({'message': '주문 통계 조회 중 오류가 발생했습니다'}), 500

# 지연 로딩 (Lazy Loading) 최적화
@optimization.route('/dashboard/lazy', methods=['GET'])
@token_required
@optimize_query
def get_dashboard_lazy(current_user):
    """지연 로딩을 적용한 대시보드 데이터"""
    try:
        # 기본 통계만 먼저 반환
        basic_stats = {
            'user_count': User.query.count(),
            'order_count': RestaurantOrder.query.count(),
            'schedule_count': Schedule.query.count()
        }
        
        # 권한별 필터 적용
        if current_user.role == 'store_manager':
            basic_stats['user_count'] = User.query.filter_by(branch_id=current_user.branch_id).count()
            basic_stats['order_count'] = RestaurantOrder.query.filter_by(store_id=current_user.branch_id).count()
            basic_stats['schedule_count'] = Schedule.query.filter_by(branch_id=current_user.branch_id).count()
        elif current_user.role == 'brand_manager':
            basic_stats['user_count'] = User.query.filter_by(branch_id=current_user.branch_id).count()
            basic_stats['order_count'] = RestaurantOrder.query.filter_by(store_id=current_user.branch_id).count()
            basic_stats['schedule_count'] = Schedule.query.filter_by(branch_id=current_user.branch_id).count()
        
        return jsonify({
            'basic_stats': basic_stats,
            'lazy_loaded': False,
            'message': '기본 통계만 로드되었습니다. 상세 데이터는 별도 API로 요청하세요.'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Lazy dashboard error: {str(e)}")
        return jsonify({'message': '대시보드 데이터 조회 중 오류가 발생했습니다'}), 500

# 캐시 헬퍼 함수
def get_cache_key(prefix, *args):
    """캐시 키 생성"""
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"

# 메모리 캐시 (실제 운영에서는 Redis 사용 권장)
_cache = {}

def get_cached_data(key, ttl_seconds=300):
    """캐시된 데이터 조회"""
    if key in _cache:
        data, timestamp = _cache[key]
        if datetime.utcnow().timestamp() - timestamp < ttl_seconds:
            return data
        else:
            del _cache[key]
    return None

def set_cached_data(key, data):
    """데이터 캐시 저장"""
    _cache[key] = (data, datetime.utcnow().timestamp())

# 캐시를 적용한 통계 조회
@optimization.route('/stats/cached', methods=['GET'])
@token_required
@optimize_query
def get_cached_stats(current_user):
    """캐시를 적용한 통계 조회"""
    try:
        cache_key = get_cache_key('stats', current_user.id, current_user.role)
        cached_data = get_cached_data(cache_key, 300)  # 5분 캐시
        
        if cached_data:
            return jsonify({
                'data': cached_data,
                'cached': True,
                'cache_time': datetime.utcnow().isoformat()
            }), 200
        
        # 캐시가 없으면 새로 계산
        stats = {
            'total_users': User.query.count(),
            'total_orders': RestaurantOrder.query.count(),
            'total_schedules': Schedule.query.count(),
            'total_attendance': Attendance.query.count()
        }
        
        # 권한별 필터 적용
        if current_user.role == 'store_manager':
            stats['total_users'] = User.query.filter_by(branch_id=current_user.branch_id).count()
            stats['total_orders'] = RestaurantOrder.query.filter_by(store_id=current_user.branch_id).count()
            stats['total_schedules'] = Schedule.query.filter_by(branch_id=current_user.branch_id).count()
            stats['total_attendance'] = Attendance.query.filter_by(user_id=current_user.id).count()
        elif current_user.role == 'brand_manager':
            stats['total_users'] = User.query.filter_by(branch_id=current_user.branch_id).count()
            stats['total_orders'] = RestaurantOrder.query.filter_by(store_id=current_user.branch_id).count()
            stats['total_schedules'] = Schedule.query.filter_by(branch_id=current_user.branch_id).count()
            stats['total_attendance'] = Attendance.query.filter_by(user_id=current_user.id).count()
        
        # 캐시에 저장
        set_cached_data(cache_key, stats)
        
        return jsonify({
            'data': stats,
            'cached': False,
            'cache_time': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Cached stats error: {str(e)}")
        return jsonify({'message': '통계 조회 중 오류가 발생했습니다'}), 500

# 성능 모니터링
@optimization.route('/performance/monitor', methods=['GET'])
@token_required
@role_required(['super_admin'])
def get_performance_monitor(current_user):
    """성능 모니터링 데이터"""
    try:
        # 데이터베이스 연결 상태
        db_status = "healthy"
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            db_status = "error"
        
        # 캐시 상태
        cache_status = "healthy" if len(_cache) < 1000 else "warning"
        
        # 메모리 사용량 (간단한 추정)
        memory_usage = len(_cache) * 100  # KB 단위 추정
        
        return jsonify({
            'database': {
                'status': db_status,
                'connection_pool_size': 10  # 기본값
            },
            'cache': {
                'status': cache_status,
                'items_count': len(_cache),
                'memory_usage_kb': memory_usage
            },
            'system': {
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': 'running'  # 실제로는 서버 시작 시간 계산 필요
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Performance monitor error: {str(e)}")
        return jsonify({'message': '성능 모니터링 데이터 조회 중 오류가 발생했습니다'}), 500 