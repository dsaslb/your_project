"""
계층형 권한 관리 시스템
업종/브랜드/매장/직원 계층 구조에 따른 세밀한 권한 제어

특징:
- 역할 기반 접근 제어 (RBAC)
- 계층형 데이터 권한
- 동적 권한 확인
- 권한 캐싱
- 감사 로깅
"""

import logging
from typing import Dict, List, Optional, Set, Any, Tuple
from functools import wraps
from flask import g, request, jsonify
from flask_login import current_user
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from models import User, Industry, Brand, Store, Staff, SystemLog
from utils.database import db

logger = logging.getLogger(__name__)

class Permission(Enum):
    """권한 유형 정의"""
    # 기본 CRUD 권한
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    
    # 관리 권한
    MANAGE = "manage"
    APPROVE = "approve"
    MONITOR = "monitor"
    
    # 시스템 권한
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    
    # 특수 권한
    EXPORT = "export"
    IMPORT = "import"
    BACKUP = "backup"
    RESTORE = "restore"

class ResourceType(Enum):
    """리소스 유형 정의"""
    INDUSTRY = "industry"
    BRAND = "brand"
    STORE = "store"
    EMPLOYEE = "employee"
    ORDER = "order"
    SCHEDULE = "schedule"
    ATTENDANCE = "attendance"
    REPORT = "report"
    SYSTEM = "system"

@dataclass
class PermissionRule:
    """권한 규칙"""
    role: str
    resource_type: ResourceType
    permission: Permission
    conditions: Dict[str, Any] = None
    priority: int = 0

@dataclass
class AccessScope:
    """접근 범위"""
    user_id: int
    role: str
    industries: Set[int]
    brands: Set[int]
    stores: Set[int]
    can_access_all: bool = False

class HierarchyPermissionManager:
    """계층형 권한 관리자"""
    
    def __init__(self):
        self.permission_cache = {}
        self.cache_ttl = 300  # 5분
        self.rules = self._load_permission_rules()
    
    def _load_permission_rules(self) -> List[PermissionRule]:
        """권한 규칙 로드"""
        rules = [
            # 슈퍼 관리자 권한
            PermissionRule("super_admin", ResourceType.INDUSTRY, Permission.SUPER_ADMIN, priority=10),
            PermissionRule("super_admin", ResourceType.BRAND, Permission.SUPER_ADMIN, priority=10),
            PermissionRule("super_admin", ResourceType.STORE, Permission.SUPER_ADMIN, priority=10),
            PermissionRule("super_admin", ResourceType.EMPLOYEE, Permission.SUPER_ADMIN, priority=10),
            PermissionRule("super_admin", ResourceType.SYSTEM, Permission.SUPER_ADMIN, priority=10),
            
            # 일반 관리자 권한
            PermissionRule("admin", ResourceType.INDUSTRY, Permission.READ, priority=8),
            PermissionRule("admin", ResourceType.BRAND, Permission.MANAGE, priority=8),
            PermissionRule("admin", ResourceType.STORE, Permission.MANAGE, priority=8),
            PermissionRule("admin", ResourceType.EMPLOYEE, Permission.MANAGE, priority=8),
            PermissionRule("admin", ResourceType.REPORT, Permission.READ, priority=8),
            
            # 브랜드 관리자 권한
            PermissionRule("brand_manager", ResourceType.BRAND, Permission.READ, 
                          conditions={"own_brand_only": True}, priority=6),
            PermissionRule("brand_manager", ResourceType.STORE, Permission.MANAGE,
                          conditions={"own_brand_only": True}, priority=6),
            PermissionRule("brand_manager", ResourceType.EMPLOYEE, Permission.MANAGE,
                          conditions={"own_brand_only": True}, priority=6),
            PermissionRule("brand_manager", ResourceType.REPORT, Permission.READ,
                          conditions={"own_brand_only": True}, priority=6),
            
            # 매장 관리자 권한
            PermissionRule("store_manager", ResourceType.STORE, Permission.READ,
                          conditions={"own_store_only": True}, priority=4),
            PermissionRule("store_manager", ResourceType.EMPLOYEE, Permission.MANAGE,
                          conditions={"own_store_only": True}, priority=4),
            PermissionRule("store_manager", ResourceType.SCHEDULE, Permission.MANAGE,
                          conditions={"own_store_only": True}, priority=4),
            PermissionRule("store_manager", ResourceType.ATTENDANCE, Permission.MONITOR,
                          conditions={"own_store_only": True}, priority=4),
            
            # 직원 권한
            PermissionRule("employee", ResourceType.EMPLOYEE, Permission.READ,
                          conditions={"self_only": True}, priority=2),
            PermissionRule("employee", ResourceType.SCHEDULE, Permission.READ,
                          conditions={"own_store_only": True}, priority=2),
            PermissionRule("employee", ResourceType.ATTENDANCE, Permission.UPDATE,
                          conditions={"self_only": True}, priority=2),
        ]
        
        return sorted(rules, key=lambda x: x.priority, reverse=True)
    
    def get_user_scope(self, user: User) -> AccessScope:
        """사용자의 접근 범위 계산"""
        cache_key = f"user_scope_{user.id}_{user.role}"
        
        # 캐시 확인
        if cache_key in self.permission_cache:
            cached_data = self.permission_cache[cache_key]
            if datetime.now() < cached_data['expires']:
                return cached_data['scope']
        
        # 접근 범위 계산
        scope = AccessScope(
            user_id=user.id,
            role=user.role,
            industries=set(),
            brands=set(),
            stores=set()
        )
        
        if user.role in ['super_admin', 'admin']:
            # 슈퍼 관리자와 일반 관리자는 모든 데이터 접근 가능
            scope.can_access_all = True
            scope.industries = set(i.id for i in Industry.query.all())
            scope.brands = set(b.id for b in Brand.query.all())
            scope.stores = set(s.id for s in Store.query.all())
            
        elif user.role == 'brand_manager':
            # 브랜드 관리자는 해당 브랜드와 하위 매장 접근
            staff = Staff.query.filter_by(user_id=user.id).first()
            if staff and hasattr(staff, 'brand_id') and staff.brand_id:
                scope.brands.add(staff.brand_id)
                
                # 해당 브랜드의 모든 매장
                brand_stores = Store.query.filter_by(brand_id=staff.brand_id).all()
                scope.stores.update(s.id for s in brand_stores)
                
                # 해당 브랜드의 업종
                brand = Brand.query.get(staff.brand_id)
                if brand and brand.industry_id:
                    scope.industries.add(brand.industry_id)
                    
        elif user.role == 'store_manager':
            # 매장 관리자는 해당 매장만 접근
            staff = Staff.query.filter_by(user_id=user.id).first()
            if staff and hasattr(staff, 'store_id') and staff.store_id:
                scope.stores.add(staff.store_id)
                
                # 해당 매장의 브랜드와 업종
                store = Store.query.get(staff.store_id)
                if store:
                    scope.brands.add(store.brand_id)
                    brand = Brand.query.get(store.brand_id)
                    if brand and brand.industry_id:
                        scope.industries.add(brand.industry_id)
        
        # 캐시 저장
        self.permission_cache[cache_key] = {
            'scope': scope,
            'expires': datetime.now() + timedelta(seconds=self.cache_ttl)
        }
        
        return scope
    
    def has_permission(self, user: User, resource_type: ResourceType, 
                      permission: Permission, resource_id: Optional[int] = None) -> bool:
        """권한 확인"""
        try:
            # 슈퍼 관리자는 모든 권한 보유
            if user.role == 'super_admin':
                return True
            
            # 사용자 범위 가져오기
            scope = self.get_user_scope(user)
            
            # 해당 역할의 권한 규칙 찾기
            applicable_rules = [
                rule for rule in self.rules 
                if rule.role == user.role and rule.resource_type == resource_type
            ]
            
            for rule in applicable_rules:
                if self._check_permission_rule(rule, permission, scope, resource_id):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"권한 확인 오류: {e}")
            return False
    
    def _check_permission_rule(self, rule: PermissionRule, requested_permission: Permission,
                              scope: AccessScope, resource_id: Optional[int]) -> bool:
        """권한 규칙 확인"""
        # 권한 레벨 확인
        if not self._permission_implies(rule.permission, requested_permission):
            return False
        
        # 조건 확인
        if rule.conditions:
            return self._check_conditions(rule, scope, resource_id)
        
        return True
    
    def _permission_implies(self, granted: Permission, requested: Permission) -> bool:
        """권한 포함 관계 확인"""
        # 권한 계층 구조
        hierarchy = {
            Permission.SUPER_ADMIN: [Permission.ADMIN, Permission.MANAGE, Permission.APPROVE, 
                                   Permission.MONITOR, Permission.CREATE, Permission.READ, 
                                   Permission.UPDATE, Permission.DELETE, Permission.EXPORT, 
                                   Permission.IMPORT, Permission.BACKUP, Permission.RESTORE],
            Permission.ADMIN: [Permission.MANAGE, Permission.APPROVE, Permission.MONITOR, 
                             Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.DELETE],
            Permission.MANAGE: [Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.DELETE],
            Permission.APPROVE: [Permission.READ, Permission.UPDATE],
            Permission.MONITOR: [Permission.READ],
            Permission.CREATE: [Permission.READ],
            Permission.UPDATE: [Permission.READ],
            Permission.DELETE: [Permission.READ],
        }
        
        if granted == requested:
            return True
        
        return requested in hierarchy.get(granted, [])
    
    def _check_conditions(self, rule: PermissionRule, scope: AccessScope, 
                         resource_id: Optional[int]) -> bool:
        """조건 확인"""
        conditions = rule.conditions or {}
        
        # 자신의 데이터만 접근 가능
        if conditions.get('self_only') and resource_id:
            # 직원의 경우 자신의 user_id와 비교
            if rule.resource_type == ResourceType.EMPLOYEE:
                staff = Staff.query.filter_by(user_id=scope.user_id).first()
                return staff and staff.id == resource_id
        
        # 자신의 브랜드만 접근 가능
        if conditions.get('own_brand_only') and resource_id:
            if rule.resource_type == ResourceType.BRAND:
                return resource_id in scope.brands
            elif rule.resource_type == ResourceType.STORE:
                store = Store.query.get(resource_id)
                return store and store.brand_id in scope.brands
            elif rule.resource_type == ResourceType.EMPLOYEE:
                staff = Staff.query.get(resource_id)
                if staff and staff.store_id:
                    store = Store.query.get(staff.store_id)
                    return store and store.brand_id in scope.brands
        
        # 자신의 매장만 접근 가능
        if conditions.get('own_store_only') and resource_id:
            if rule.resource_type == ResourceType.STORE:
                return resource_id in scope.stores
            elif rule.resource_type == ResourceType.EMPLOYEE:
                staff = Staff.query.get(resource_id)
                return staff and staff.store_id in scope.stores
        
        return True
    
    def filter_accessible_resources(self, user: User, resource_type: ResourceType, 
                                  resources: List[Any]) -> List[Any]:
        """접근 가능한 리소스만 필터링"""
        scope = self.get_user_scope(user)
        
        if scope.can_access_all:
            return resources
        
        filtered = []
        for resource in resources:
            resource_id = getattr(resource, 'id', None)
            if self.has_permission(user, resource_type, Permission.READ, resource_id):
                filtered.append(resource)
        
        return filtered
    
    def clear_user_cache(self, user_id: int):
        """사용자 권한 캐시 클리어"""
        keys_to_remove = [key for key in self.permission_cache.keys() 
                         if key.startswith(f"user_scope_{user_id}_")]
        for key in keys_to_remove:
            del self.permission_cache[key]
    
    def clear_all_cache(self):
        """모든 권한 캐시 클리어"""
        self.permission_cache.clear()

# 전역 권한 관리자 인스턴스
permission_manager = HierarchyPermissionManager()

def require_permission(resource_type: ResourceType, permission: Permission, 
                      resource_id_param: Optional[str] = None):
    """권한 확인 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({'error': '인증이 필요합니다'}), 401
            
            # 리소스 ID 추출
            resource_id = None
            if resource_id_param:
                if resource_id_param in kwargs:
                    resource_id = kwargs[resource_id_param]
                elif hasattr(request, 'view_args') and resource_id_param in request.view_args:
                    resource_id = request.view_args[resource_id_param]
            
            # 권한 확인
            if not permission_manager.has_permission(g.current_user, resource_type, permission, resource_id):
                return jsonify({'error': '권한이 없습니다'}), 403
            
            # 감사 로그 기록
            log_permission_access(g.current_user, resource_type, permission, resource_id, True)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_accessible_query(user: User, model_class, base_query=None):
    """접근 가능한 데이터만 조회하는 쿼리 생성"""
    if not base_query:
        base_query = model_class.query
    
    scope = permission_manager.get_user_scope(user)
    
    if scope.can_access_all:
        return base_query
    
    # 모델에 따른 필터링
    if model_class.__name__ == 'Industry':
        if scope.industries:
            return base_query.filter(model_class.id.in_(scope.industries))
        else:
            return base_query.filter(model_class.id == -1)  # 접근 불가
    
    elif model_class.__name__ == 'Brand':
        if scope.brands:
            return base_query.filter(model_class.id.in_(scope.brands))
        else:
            return base_query.filter(model_class.id == -1)
    
    elif model_class.__name__ == 'Store':
        if scope.stores:
            return base_query.filter(model_class.id.in_(scope.stores))
        else:
            return base_query.filter(model_class.id == -1)
    
    elif model_class.__name__ == 'Staff':
        if scope.stores:
            return base_query.filter(model_class.store_id.in_(scope.stores))
        else:
            return base_query.filter(model_class.id == -1)
    
    return base_query

def log_permission_access(user: User, resource_type: ResourceType, permission: Permission,
                         resource_id: Optional[int], granted: bool):
    """권한 접근 로그 기록"""
    try:
        log_entry = SystemLog(
            user_id=user.id,
            action=f"permission_check",
            detail=f"Resource: {resource_type.value}, Permission: {permission.value}, "
                  f"ResourceID: {resource_id}, Granted: {granted}",
            ip_address=request.remote_addr if request else None,
            created_at=datetime.now()
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logger.error(f"권한 접근 로그 기록 실패: {e}")

# 편의 함수들
def has_industry_permission(user: User, permission: Permission, industry_id: int = None) -> bool:
    """업종 권한 확인"""
    return permission_manager.has_permission(user, ResourceType.INDUSTRY, permission, industry_id)

def has_brand_permission(user: User, permission: Permission, brand_id: int = None) -> bool:
    """브랜드 권한 확인"""
    return permission_manager.has_permission(user, ResourceType.BRAND, permission, brand_id)

def has_store_permission(user: User, permission: Permission, store_id: int = None) -> bool:
    """매장 권한 확인"""
    return permission_manager.has_permission(user, ResourceType.STORE, permission, store_id)

def has_employee_permission(user: User, permission: Permission, employee_id: int = None) -> bool:
    """직원 권한 확인"""
    return permission_manager.has_permission(user, ResourceType.EMPLOYEE, permission, employee_id)