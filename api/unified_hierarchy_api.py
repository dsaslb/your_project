"""
통합 계층형 관리 시스템 API
업종(Industry) -> 브랜드(Brand) -> 매장(Store) -> 직원(Employee) 계층 구조를 위한 통일된 API

이 모듈은 모든 관리자 페이지에서 일관된 데이터 구조와 API를 사용하도록 보장합니다.
- 데이터 동기화 보장
- 권한별 데이터 필터링
- 실시간 업데이트 지원
- 표준화된 응답 형식
"""

from flask import Blueprint, jsonify, request, g
from flask_login import login_required, current_user
from functools import wraps
import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from models import (
    Industry, Brand, Store, Staff, User, Order, Schedule, 
    AttendanceRecord, Notification, SystemLog
)
from utils.database import db
from utils.caching import cache_manager
from utils.hierarchy_permissions import (
    permission_manager, require_permission, get_accessible_query,
    ResourceType, Permission, has_brand_permission, has_store_permission
)
from utils.data_validator import validate_hierarchy_data
from api.utils import token_required

logger = logging.getLogger(__name__)

# 통합 계층형 API 블루프린트
unified_hierarchy_bp = Blueprint('unified_hierarchy', __name__, url_prefix='/api/unified')

# ==================== 공통 유틸리티 함수 ====================

def get_user_hierarchy_scope(user):
    """사용자의 계층별 접근 범위를 반환 (새로운 권한 시스템 사용)"""
    if not user:
        return None
    
    # 새로운 권한 시스템 사용
    access_scope = permission_manager.get_user_scope(user)
    
    # 기존 형식으로 변환 (하위 호환성)
    return {
        'role': access_scope.role,
        'industries': list(access_scope.industries),
        'brands': list(access_scope.brands),
        'stores': list(access_scope.stores),
        'can_access_all': access_scope.can_access_all
    }

def standardize_response(data, success=True, message=None, pagination=None):
    """표준화된 API 응답 형식"""
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat(),
        'data': data,
    }
    
    if message:
        response['message'] = message
    
    if pagination:
        response['pagination'] = pagination
    
    if not success and isinstance(data, str):
        response['error'] = data
        response['data'] = None
    
    return jsonify(response)

def apply_hierarchy_filter(query, model, user_scope, hierarchy_level=None):
    """계층별 권한에 따라 쿼리 필터 적용"""
    if user_scope['can_access_all']:
        return query
    
    if hierarchy_level == 'industry' and hasattr(model, 'id'):
        return query.filter(model.id.in_(user_scope['industries']))
    elif hierarchy_level == 'brand' and hasattr(model, 'id'):
        return query.filter(model.id.in_(user_scope['brands']))
    elif hierarchy_level == 'store' and hasattr(model, 'id'):
        return query.filter(model.id.in_(user_scope['stores']))
    elif hasattr(model, 'brand_id'):
        return query.filter(model.brand_id.in_(user_scope['brands']))
    elif hasattr(model, 'store_id'):
        return query.filter(model.store_id.in_(user_scope['stores']))
    
    return query

# ==================== 업종(Industry) 관리 API ====================

@unified_hierarchy_bp.route('/industries', methods=['GET'])
@token_required
@require_permission(ResourceType.INDUSTRY, Permission.READ)
def get_industries():
    """업종 목록 조회 (권한별 필터링)"""
    try:
        user_scope = get_user_hierarchy_scope(g.current_user)
        if not user_scope:
            return standardize_response("인증이 필요합니다", False), 401
        
        query = Industry.query
        query = apply_hierarchy_filter(query, Industry, user_scope, 'industry')
        
        # 페이징 처리
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 검색 필터
        search = request.args.get('search', '')
        if search:
            query = query.filter(Industry.name.contains(search))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        industries = []
        for industry in pagination.items:
            # 하위 브랜드 수 계산
            brand_count = Brand.query.filter_by(industry_id=industry.id).count()
            
            industries.append({
                'id': industry.id,
                'name': industry.name,
                'code': industry.code,
                'description': industry.description,
                'brand_count': brand_count,
                'created_at': industry.created_at.isoformat() if industry.created_at else None,
                'updated_at': industry.updated_at.isoformat() if hasattr(industry, 'updated_at') and industry.updated_at else None
            })
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
        
        return standardize_response(industries, True, "업종 목록 조회 성공", pagination_info)
        
    except Exception as e:
        logger.error(f"업종 목록 조회 오류: {str(e)}")
        return standardize_response(f"업종 목록 조회 실패: {str(e)}", False), 500

@unified_hierarchy_bp.route('/industries/<int:industry_id>', methods=['GET'])
@token_required
def get_industry_detail(industry_id):
    """업종 상세 정보 조회"""
    try:
        user_scope = get_user_hierarchy_scope(g.current_user)
        if not user_scope:
            return standardize_response("인증이 필요합니다", False), 401
        
        # 권한 체크
        if not user_scope['can_access_all'] and industry_id not in user_scope['industries']:
            return standardize_response("해당 업종에 대한 접근 권한이 없습니다", False), 403
        
        industry = Industry.query.get_or_404(industry_id)
        
        # 하위 브랜드 정보
        brands_query = Brand.query.filter_by(industry_id=industry_id)
        brands_query = apply_hierarchy_filter(brands_query, Brand, user_scope, 'brand')
        brands = brands_query.all()
        
        # 통계 정보
        total_stores = 0
        total_employees = 0
        for brand in brands:
            brand_stores = Store.query.filter_by(brand_id=brand.id).count()
            total_stores += brand_stores
            
            # 각 매장의 직원 수 합계
            for store in Store.query.filter_by(brand_id=brand.id).all():
                total_employees += Staff.query.filter_by(store_id=store.id).count()
        
        industry_data = {
            'id': industry.id,
            'name': industry.name,
            'code': industry.code,
            'description': industry.description,
            'created_at': industry.created_at.isoformat() if industry.created_at else None,
            'updated_at': industry.updated_at.isoformat() if hasattr(industry, 'updated_at') and industry.updated_at else None,
            'stats': {
                'total_brands': len(brands),
                'total_stores': total_stores,
                'total_employees': total_employees
            },
            'brands': [{
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'description': brand.description,
                'store_count': Store.query.filter_by(brand_id=brand.id).count()
            } for brand in brands]
        }
        
        return standardize_response(industry_data, True, "업종 상세 정보 조회 성공")
        
    except Exception as e:
        logger.error(f"업종 상세 정보 조회 오류: {str(e)}")
        return standardize_response(f"업종 상세 정보 조회 실패: {str(e)}", False), 500

# ==================== 브랜드(Brand) 관리 API ====================

@unified_hierarchy_bp.route('/brands', methods=['GET'])
@token_required
@require_permission(ResourceType.BRAND, Permission.READ)
def get_brands():
    """브랜드 목록 조회 (권한별 필터링)"""
    try:
        user_scope = get_user_hierarchy_scope(g.current_user)
        if not user_scope:
            return standardize_response("인증이 필요합니다", False), 401
        
        query = Brand.query
        query = apply_hierarchy_filter(query, Brand, user_scope, 'brand')
        
        # 업종 필터
        industry_id = request.args.get('industry_id', type=int)
        if industry_id:
            query = query.filter_by(industry_id=industry_id)
        
        # 페이징 처리
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 검색 필터
        search = request.args.get('search', '')
        if search:
            query = query.filter(Brand.name.contains(search))
        
        # 정렬
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        if sort_by == 'name':
            query = query.order_by(Brand.name.asc() if sort_order == 'asc' else Brand.name.desc())
        elif sort_by == 'created_at':
            query = query.order_by(Brand.created_at.desc() if sort_order == 'desc' else Brand.created_at.asc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        brands = []
        for brand in pagination.items:
            # 하위 매장 수 및 직원 수 계산
            store_count = Store.query.filter_by(brand_id=brand.id).count()
            employee_count = 0
            
            for store in Store.query.filter_by(brand_id=brand.id).all():
                employee_count += Staff.query.filter_by(store_id=store.id).count()
            
            # 업종 정보
            industry = Industry.query.get(brand.industry_id) if brand.industry_id else None
            
            brands.append({
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'description': brand.description,
                'industry_id': brand.industry_id,
                'industry_name': industry.name if industry else None,
                'store_count': store_count,
                'employee_count': employee_count,
                'created_at': brand.created_at.isoformat() if brand.created_at else None,
                'updated_at': brand.updated_at.isoformat() if hasattr(brand, 'updated_at') and brand.updated_at else None
            })
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
        
        return standardize_response(brands, True, "브랜드 목록 조회 성공", pagination_info)
        
    except Exception as e:
        logger.error(f"브랜드 목록 조회 오류: {str(e)}")
        return standardize_response(f"브랜드 목록 조회 실패: {str(e)}", False), 500

@unified_hierarchy_bp.route('/brands/<int:brand_id>', methods=['GET'])
@token_required
@require_permission(ResourceType.BRAND, Permission.READ, 'brand_id')
def get_brand_detail(brand_id):
    """브랜드 상세 정보 조회 (매장, 직원, 통계 포함)"""
    try:
        user_scope = get_user_hierarchy_scope(g.current_user)
        if not user_scope:
            return standardize_response("인증이 필요합니다", False), 401
        
        # 권한 체크
        if not user_scope['can_access_all'] and brand_id not in user_scope['brands']:
            return standardize_response("해당 브랜드에 대한 접근 권한이 없습니다", False), 403
        
        brand = Brand.query.get_or_404(brand_id)
        industry = Industry.query.get(brand.industry_id) if brand.industry_id else None
        
        # 하위 매장 정보
        stores_query = Store.query.filter_by(brand_id=brand_id)
        stores_query = apply_hierarchy_filter(stores_query, Store, user_scope, 'store')
        stores = stores_query.all()
        
        # 통계 정보 계산
        total_employees = 0
        total_orders = 0
        today_orders = 0
        today = datetime.now().date()
        
        store_list = []
        for store in stores:
            # 매장별 직원 수
            store_employees = Staff.query.filter_by(store_id=store.id).count()
            total_employees += store_employees
            
            # 매장별 주문 수
            store_orders = Order.query.filter_by(store_id=store.id).count()
            total_orders += store_orders
            
            # 오늘 주문 수
            store_today_orders = Order.query.filter(
                and_(Order.store_id == store.id,
                     func.date(Order.created_at) == today)
            ).count()
            today_orders += store_today_orders
            
            store_list.append({
                'id': store.id,
                'name': store.name,
                'code': store.code,
                'address': store.address,
                'phone': store.phone,
                'manager_name': store.manager_name,
                'employee_count': store_employees,
                'status': store.status if hasattr(store, 'status') else 'active'
            })
        
        # 최근 활동 (주문, 스케줄 등)
        recent_orders = Order.query.filter(
            Order.store_id.in_([s.id for s in stores])
        ).order_by(Order.created_at.desc()).limit(10).all()
        
        recent_schedules = Schedule.query.filter(
            Schedule.store_id.in_([s.id for s in stores])
        ).order_by(Schedule.created_at.desc()).limit(10).all()
        
        brand_data = {
            'id': brand.id,
            'name': brand.name,
            'code': brand.code,
            'description': brand.description,
            'industry_id': brand.industry_id,
            'industry_name': industry.name if industry else None,
            'created_at': brand.created_at.isoformat() if brand.created_at else None,
            'updated_at': brand.updated_at.isoformat() if hasattr(brand, 'updated_at') and brand.updated_at else None,
            'stats': {
                'total_stores': len(stores),
                'total_employees': total_employees,
                'total_orders': total_orders,
                'today_orders': today_orders,
                'active_stores': len([s for s in stores if not hasattr(s, 'status') or s.status == 'active'])
            },
            'stores': store_list,
            'recent_activities': {
                'orders': [{
                    'id': order.id,
                    'store_id': order.store_id,
                    'store_name': next((s.name for s in stores if s.id == order.store_id), '알 수 없음'),
                    'status': order.status,
                    'total_amount': float(order.total_amount) if order.total_amount else 0,
                    'created_at': order.created_at.isoformat()
                } for order in recent_orders],
                'schedules': [{
                    'id': schedule.id,
                    'store_id': schedule.store_id,
                    'store_name': next((s.name for s in stores if s.id == schedule.store_id), '알 수 없음'),
                    'title': schedule.title if hasattr(schedule, 'title') else '스케줄',
                    'start_time': schedule.start_time.isoformat() if hasattr(schedule, 'start_time') and schedule.start_time else None,
                    'created_at': schedule.created_at.isoformat()
                } for schedule in recent_schedules]
            }
        }
        
        return standardize_response(brand_data, True, "브랜드 상세 정보 조회 성공")
        
    except Exception as e:
        logger.error(f"브랜드 상세 정보 조회 오류: {str(e)}")
        return standardize_response(f"브랜드 상세 정보 조회 실패: {str(e)}", False), 500

# ==================== 매장(Store) 관리 API ====================

@unified_hierarchy_bp.route('/stores', methods=['GET'])
@token_required
def get_stores():
    """매장 목록 조회 (권한별 필터링)"""
    try:
        user_scope = get_user_hierarchy_scope(g.current_user)
        if not user_scope:
            return standardize_response("인증이 필요합니다", False), 401
        
        query = Store.query
        query = apply_hierarchy_filter(query, Store, user_scope, 'store')
        
        # 브랜드 필터
        brand_id = request.args.get('brand_id', type=int)
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        # 페이징 처리
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 검색 필터
        search = request.args.get('search', '')
        if search:
            query = query.filter(or_(
                Store.name.contains(search),
                Store.address.contains(search)
            ))
        
        # 정렬
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        if sort_by == 'name':
            query = query.order_by(Store.name.asc() if sort_order == 'asc' else Store.name.desc())
        elif sort_by == 'created_at':
            query = query.order_by(Store.created_at.desc() if sort_order == 'desc' else Store.created_at.asc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        stores = []
        for store in pagination.items:
            # 직원 수 계산
            employee_count = Staff.query.filter_by(store_id=store.id).count()
            
            # 브랜드 정보
            brand = Brand.query.get(store.brand_id) if store.brand_id else None
            
            stores.append({
                'id': store.id,
                'name': store.name,
                'code': store.code,
                'address': store.address,
                'phone': store.phone,
                'manager_name': store.manager_name,
                'brand_id': store.brand_id,
                'brand_name': brand.name if brand else None,
                'employee_count': employee_count,
                'status': store.status if hasattr(store, 'status') else 'active',
                'created_at': store.created_at.isoformat() if store.created_at else None,
                'updated_at': store.updated_at.isoformat() if hasattr(store, 'updated_at') and store.updated_at else None
            })
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
        
        return standardize_response(stores, True, "매장 목록 조회 성공", pagination_info)
        
    except Exception as e:
        logger.error(f"매장 목록 조회 오류: {str(e)}")
        return standardize_response(f"매장 목록 조회 실패: {str(e)}", False), 500

@unified_hierarchy_bp.route('/stores/<int:store_id>', methods=['GET'])
@token_required
def get_store_detail(store_id):
    """매장 상세 정보 조회 (직원, 통계 포함)"""
    try:
        user_scope = get_user_hierarchy_scope(g.current_user)
        if not user_scope:
            return standardize_response("인증이 필요합니다", False), 401
        
        # 권한 체크
        if not user_scope['can_access_all'] and store_id not in user_scope['stores']:
            return standardize_response("해당 매장에 대한 접근 권한이 없습니다", False), 403
        
        store = Store.query.get_or_404(store_id)
        brand = Brand.query.get(store.brand_id) if store.brand_id else None
        industry = Industry.query.get(brand.industry_id) if brand and brand.industry_id else None
        
        # 매장 직원 정보
        employees = Staff.query.filter_by(store_id=store_id).all()
        
        # 통계 정보 계산
        total_orders = Order.query.filter_by(store_id=store_id).count()
        today = datetime.now().date()
        today_orders = Order.query.filter(
            and_(Order.store_id == store_id,
                 func.date(Order.created_at) == today)
        ).count()
        
        # 출근 현황 (오늘)
        today_attendance = AttendanceRecord.query.filter(
            and_(AttendanceRecord.store_id == store_id,
                 func.date(AttendanceRecord.date) == today)
        ).all()
        
        # 최근 활동
        recent_orders = Order.query.filter_by(store_id=store_id)\
            .order_by(Order.created_at.desc()).limit(10).all()
        
        recent_schedules = Schedule.query.filter_by(store_id=store_id)\
            .order_by(Schedule.created_at.desc()).limit(10).all()
        
        employee_list = []
        for employee in employees:
            user = User.query.get(employee.user_id) if employee.user_id else None
            
            employee_list.append({
                'id': employee.id,
                'user_id': employee.user_id,
                'name': employee.name,
                'email': user.email if user else None,
                'phone': employee.phone if hasattr(employee, 'phone') else None,
                'position': employee.position if hasattr(employee, 'position') else '직원',
                'hire_date': employee.hire_date.isoformat() if hasattr(employee, 'hire_date') and employee.hire_date else None,
                'status': employee.status if hasattr(employee, 'status') else 'active'
            })
        
        store_data = {
            'id': store.id,
            'name': store.name,
            'code': store.code,
            'address': store.address,
            'phone': store.phone,
            'manager_name': store.manager_name,
            'brand_id': store.brand_id,
            'brand_name': brand.name if brand else None,
            'industry_name': industry.name if industry else None,
            'status': store.status if hasattr(store, 'status') else 'active',
            'created_at': store.created_at.isoformat() if store.created_at else None,
            'updated_at': store.updated_at.isoformat() if hasattr(store, 'updated_at') and store.updated_at else None,
            'stats': {
                'total_employees': len(employees),
                'total_orders': total_orders,
                'today_orders': today_orders,
                'today_attendance': len(today_attendance),
                'active_employees': len([e for e in employees if not hasattr(e, 'status') or e.status == 'active'])
            },
            'employees': employee_list,
            'recent_activities': {
                'orders': [{
                    'id': order.id,
                    'status': order.status,
                    'total_amount': float(order.total_amount) if order.total_amount else 0,
                    'created_at': order.created_at.isoformat()
                } for order in recent_orders],
                'schedules': [{
                    'id': schedule.id,
                    'title': schedule.title if hasattr(schedule, 'title') else '스케줄',
                    'start_time': schedule.start_time.isoformat() if hasattr(schedule, 'start_time') and schedule.start_time else None,
                    'created_at': schedule.created_at.isoformat()
                } for schedule in recent_schedules],
                'attendance': [{
                    'id': att.id,
                    'employee_name': next((e.name for e in employees if e.id == att.employee_id), '알 수 없음'),
                    'check_in': att.check_in.isoformat() if hasattr(att, 'check_in') and att.check_in else None,
                    'check_out': att.check_out.isoformat() if hasattr(att, 'check_out') and att.check_out else None,
                    'status': att.status if hasattr(att, 'status') else 'present'
                } for att in today_attendance]
            }
        }
        
        return standardize_response(store_data, True, "매장 상세 정보 조회 성공")
        
    except Exception as e:
        logger.error(f"매장 상세 정보 조회 오류: {str(e)}")
        return standardize_response(f"매장 상세 정보 조회 실패: {str(e)}", False), 500

# ==================== 직원(Employee) 관리 API ====================

@unified_hierarchy_bp.route('/employees', methods=['GET'])
@token_required
def get_employees():
    """직원 목록 조회 (권한별 필터링)"""
    try:
        user_scope = get_user_hierarchy_scope(g.current_user)
        if not user_scope:
            return standardize_response("인증이 필요합니다", False), 401
        
        query = Staff.query
        
        # 권한별 필터링
        if not user_scope['can_access_all']:
            if user_scope['stores']:
                query = query.filter(Staff.store_id.in_(user_scope['stores']))
            else:
                query = query.filter(Staff.id == -1)  # 접근 권한 없음
        
        # 매장 필터
        store_id = request.args.get('store_id', type=int)
        if store_id:
            query = query.filter_by(store_id=store_id)
        
        # 브랜드 필터
        brand_id = request.args.get('brand_id', type=int)
        if brand_id:
            # 해당 브랜드의 모든 매장 직원 조회
            brand_stores = Store.query.filter_by(brand_id=brand_id).all()
            store_ids = [s.id for s in brand_stores]
            query = query.filter(Staff.store_id.in_(store_ids))
        
        # 페이징 처리
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 검색 필터
        search = request.args.get('search', '')
        if search:
            query = query.filter(Staff.name.contains(search))
        
        # 정렬
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        if sort_by == 'name':
            query = query.order_by(Staff.name.asc() if sort_order == 'asc' else Staff.name.desc())
        elif sort_by == 'created_at':
            query = query.order_by(Staff.created_at.desc() if sort_order == 'desc' else Staff.created_at.asc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        employees = []
        for employee in pagination.items:
            # 사용자 정보
            user = User.query.get(employee.user_id) if employee.user_id else None
            
            # 매장 정보
            store = Store.query.get(employee.store_id) if employee.store_id else None
            brand = Brand.query.get(store.brand_id) if store and store.brand_id else None
            
            employees.append({
                'id': employee.id,
                'user_id': employee.user_id,
                'name': employee.name,
                'email': user.email if user else None,
                'phone': employee.phone if hasattr(employee, 'phone') else None,
                'position': employee.position if hasattr(employee, 'position') else '직원',
                'store_id': employee.store_id,
                'store_name': store.name if store else None,
                'brand_name': brand.name if brand else None,
                'hire_date': employee.hire_date.isoformat() if hasattr(employee, 'hire_date') and employee.hire_date else None,
                'status': employee.status if hasattr(employee, 'status') else 'active',
                'created_at': employee.created_at.isoformat() if employee.created_at else None,
                'updated_at': employee.updated_at.isoformat() if hasattr(employee, 'updated_at') and employee.updated_at else None
            })
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
        
        return standardize_response(employees, True, "직원 목록 조회 성공", pagination_info)
        
    except Exception as e:
        logger.error(f"직원 목록 조회 오류: {str(e)}")
        return standardize_response(f"직원 목록 조회 실패: {str(e)}", False), 500

# ==================== 통합 대시보드 데이터 API ====================

@unified_hierarchy_bp.route('/dashboard', methods=['GET'])
@token_required
def get_unified_dashboard():
    """통합 대시보드 데이터 (권한별 맞춤형 데이터)"""
    try:
        user_scope = get_user_hierarchy_scope(g.current_user)
        if not user_scope:
            return standardize_response("인증이 필요합니다", False), 401
        
        # 사용자 권한에 따른 데이터 범위 결정
        industries = Industry.query.filter(Industry.id.in_(user_scope['industries'])).all() if user_scope['industries'] else []
        brands = Brand.query.filter(Brand.id.in_(user_scope['brands'])).all() if user_scope['brands'] else []
        stores = Store.query.filter(Store.id.in_(user_scope['stores'])).all() if user_scope['stores'] else []
        
        # 통계 계산
        total_industries = len(industries)
        total_brands = len(brands)
        total_stores = len(stores)
        
        total_employees = 0
        total_orders = 0
        today_orders = 0
        today = datetime.now().date()
        
        for store in stores:
            total_employees += Staff.query.filter_by(store_id=store.id).count()
            store_orders = Order.query.filter_by(store_id=store.id).count()
            total_orders += store_orders
            
            today_store_orders = Order.query.filter(
                and_(Order.store_id == store.id,
                     func.date(Order.created_at) == today)
            ).count()
            today_orders += today_store_orders
        
        # 최근 활동 데이터
        recent_orders = []
        recent_notifications = []
        
        if stores:
            store_ids = [s.id for s in stores]
            recent_orders = Order.query.filter(Order.store_id.in_(store_ids))\
                .order_by(Order.created_at.desc()).limit(10).all()
            
            recent_notifications = Notification.query.filter(
                or_(Notification.target_id.in_(store_ids),
                    Notification.target_type == 'system')
            ).order_by(Notification.created_at.desc()).limit(10).all()
        
        # 브랜드별 통계 (상위 5개)
        brand_stats = []
        for brand in brands[:5]:
            brand_stores = [s for s in stores if s.brand_id == brand.id]
            brand_employees = sum(Staff.query.filter_by(store_id=s.id).count() for s in brand_stores)
            brand_orders = sum(Order.query.filter_by(store_id=s.id).count() for s in brand_stores)
            
            brand_stats.append({
                'id': brand.id,
                'name': brand.name,
                'store_count': len(brand_stores),
                'employee_count': brand_employees,
                'order_count': brand_orders
            })
        
        dashboard_data = {
            'user_info': {
                'id': g.current_user.id,
                'username': g.current_user.username,
                'role': g.current_user.role,
                'scope': user_scope
            },
            'summary_stats': {
                'total_industries': total_industries,
                'total_brands': total_brands,
                'total_stores': total_stores,
                'total_employees': total_employees,
                'total_orders': total_orders,
                'today_orders': today_orders
            },
            'brand_stats': brand_stats,
            'recent_activities': {
                'orders': [{
                    'id': order.id,
                    'store_id': order.store_id,
                    'store_name': next((s.name for s in stores if s.id == order.store_id), '알 수 없음'),
                    'status': order.status,
                    'total_amount': float(order.total_amount) if order.total_amount else 0,
                    'created_at': order.created_at.isoformat()
                } for order in recent_orders],
                'notifications': [{
                    'id': notif.id,
                    'title': notif.title if hasattr(notif, 'title') else '알림',
                    'message': notif.message,
                    'type': notif.type if hasattr(notif, 'type') else 'info',
                    'created_at': notif.created_at.isoformat()
                } for notif in recent_notifications]
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return standardize_response(dashboard_data, True, "통합 대시보드 데이터 조회 성공")
        
    except Exception as e:
        logger.error(f"통합 대시보드 데이터 조회 오류: {str(e)}")
        return standardize_response(f"통합 대시보드 데이터 조회 실패: {str(e)}", False), 500

# ==================== 데이터 동기화 API ====================

@unified_hierarchy_bp.route('/sync/refresh', methods=['POST'])
@token_required
def refresh_data():
    """데이터 강제 새로고침 (캐시 클리어 포함)"""
    try:
        # 캐시 클리어 (캐시 매니저가 있는 경우)
        try:
            cache_manager.clear_all()
        except:
            pass
        
        return standardize_response(
            {'refreshed_at': datetime.now().isoformat()},
            True,
            "데이터가 성공적으로 새로고침되었습니다"
        )
        
    except Exception as e:
        logger.error(f"데이터 새로고침 오류: {str(e)}")
        return standardize_response(f"데이터 새로고침 실패: {str(e)}", False), 500

# ==================== 에러 핸들러 ====================

@unified_hierarchy_bp.errorhandler(404)
def not_found(error):
    return standardize_response("요청한 리소스를 찾을 수 없습니다", False), 404

@unified_hierarchy_bp.errorhandler(403)
def forbidden(error):
    return standardize_response("해당 리소스에 대한 접근 권한이 없습니다", False), 403

@unified_hierarchy_bp.errorhandler(500)
def internal_error(error):
    return standardize_response("서버 내부 오류가 발생했습니다", False), 500