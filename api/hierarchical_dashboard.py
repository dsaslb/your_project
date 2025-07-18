import os
import sqlite3
from enum import Enum
from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime, timedelta
from models_main import *
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
from typing import Optional
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
계층형 대시보드 시스템
- 프랜차이즈/멀티브랜드 계층 구조 지원
- 역할별 맞춤 대시보드
- KPI 정의 및 모니터링
- 정책 템플릿 및 적용
- 실시간 데이터 통합
- 권한 기반 데이터 접근 제어
"""


hierarchical_dashboard = Blueprint('hierarchical_dashboard', __name__, url_prefix='/api/hierarchy')

logger = logging.getLogger(__name__)


class HierarchyLevel(Enum):
    """계층 레벨"""
    SUPER_ADMIN = "super_admin"
    BRAND_ADMIN = "brand_admin"
    STORE_ADMIN = "store_admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class KPIType(Enum):
    """KPI 유형"""
    SALES = "sales"
    COST = "cost"
    PROFIT = "profit"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    EMPLOYEE_SATISFACTION = "employee_satisfaction"
    INVENTORY = "inventory"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"


class PolicyType(Enum):
    """정책 유형"""
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    HR = "hr"
    QUALITY = "quality"
    SAFETY = "safety"
    COMPLIANCE = "compliance"


class AdvancedHierarchyManager:
    """고도화된 계층 관리자"""

    def __init__(self):
        self.hierarchy_config = {}
        self.kpi_definitions = {}
        self.policy_templates = {}
        self.user_hierarchies = {}

        # 계층 구조 로드
        self._load_hierarchy_config()
        self._load_kpi_definitions()
        self._load_policy_templates()

    def _load_hierarchy_config(self):
        """계층 구조 설정 로드"""
        self.hierarchy_config = {
            HierarchyLevel.SUPER_ADMIN: {
                'name': '최고관리자',
                'can_manage': ['brand_admin', 'store_admin', 'manager', 'employee'],
                'can_view': ['all'],
                'dashboard_modules': ['overview', 'brands', 'stores', 'reports', 'analytics', 'settings'],
                'kpi_access': ['all'],
                'policy_access': ['all']
            },
            HierarchyLevel.BRAND_ADMIN: {
                'name': '브랜드 관리자',
                'can_manage': ['store_admin', 'manager', 'employee'],
                'can_view': ['brand', 'stores'],
                'dashboard_modules': ['overview', 'stores', 'reports', 'analytics'],
                'kpi_access': ['brand', 'store'],
                'policy_access': ['brand', 'store']
            },
            HierarchyLevel.STORE_ADMIN: {
                'name': '매장 관리자',
                'can_manage': ['manager', 'employee'],
                'can_view': ['store'],
                'dashboard_modules': ['overview', 'operations', 'reports'],
                'kpi_access': ['store'],
                'policy_access': ['store']
            },
            HierarchyLevel.MANAGER: {
                'name': '매니저',
                'can_manage': ['employee'],
                'can_view': ['store'],
                'dashboard_modules': ['overview', 'operations'],
                'kpi_access': ['store'],
                'policy_access': ['store']
            },
            HierarchyLevel.EMPLOYEE: {
                'name': '직원',
                'can_manage': [],
                'can_view': ['own'],
                'dashboard_modules': ['overview'],
                'kpi_access': ['own'],
                'policy_access': ['own']
            }
        }

    def _load_kpi_definitions(self):
        """KPI 정의 로드"""
        self.kpi_definitions = {
            KPIType.SALES: {
                'name': '매출',
                'unit': '원',
                'calculation': 'sum(total_amount)',
                'target_type': 'daily',
                'thresholds': {
                    'excellent': 0.9,  # 목표의 90% 이상
                    'good': 0.7,       # 목표의 70% 이상
                    'warning': 0.5,    # 목표의 50% 이상
                    'critical': 0.3    # 목표의 30% 이상
                },
                'description': '일일 총 매출액'
            },
            KPIType.COST: {
                'name': '비용',
                'unit': '원',
                'calculation': 'sum(labor_cost + material_cost)',
                'target_type': 'daily',
                'thresholds': {
                    'excellent': 0.6,  # 매출의 60% 이하
                    'good': 0.7,       # 매출의 70% 이하
                    'warning': 0.8,    # 매출의 80% 이하
                    'critical': 0.9    # 매출의 90% 이상
                },
                'description': '일일 총 비용 (인건비 + 재료비)'
            },
            KPIType.PROFIT: {
                'name': '이익',
                'unit': '원',
                'calculation': 'sales - cost',
                'target_type': 'daily',
                'thresholds': {
                    'excellent': 0.4,  # 매출의 40% 이상
                    'good': 0.3,       # 매출의 30% 이상
                    'warning': 0.2,    # 매출의 20% 이상
                    'critical': 0.1    # 매출의 10% 이상
                },
                'description': '일일 순이익'
            },
            KPIType.CUSTOMER_SATISFACTION: {
                'name': '고객 만족도',
                'unit': '점',
                'calculation': 'avg(rating)',
                'target_type': 'weekly',
                'thresholds': {
                    'excellent': 4.5,  # 4.5점 이상
                    'good': 4.0,       # 4.0점 이상
                    'warning': 3.5,    # 3.5점 이상
                    'critical': 3.0    # 3.0점 이상
                },
                'description': '주간 평균 고객 평점'
            },
            KPIType.EMPLOYEE_SATISFACTION: {
                'name': '직원 만족도',
                'unit': '점',
                'calculation': 'avg(satisfaction_score)',
                'target_type': 'monthly',
                'thresholds': {
                    'excellent': 4.5,
                    'good': 4.0,
                    'warning': 3.5,
                    'critical': 3.0
                },
                'description': '월간 평균 직원 만족도'
            },
            KPIType.INVENTORY: {
                'name': '재고 관리',
                'unit': '%',
                'calculation': 'avg(stock_utilization)',
                'target_type': 'daily',
                'thresholds': {
                    'excellent': 0.8,  # 80% 이상 활용
                    'good': 0.7,       # 70% 이상 활용
                    'warning': 0.6,    # 60% 이상 활용
                    'critical': 0.5    # 50% 이상 활용
                },
                'description': '일일 평균 재고 활용률'
            },
            KPIType.QUALITY: {
                'name': '품질 관리',
                'unit': '%',
                'calculation': '1 - (defect_rate)',
                'target_type': 'daily',
                'thresholds': {
                    'excellent': 0.98,  # 98% 이상
                    'good': 0.95,       # 95% 이상
                    'warning': 0.90,    # 90% 이상
                    'critical': 0.85    # 85% 이상
                },
                'description': '일일 품질 합격률'
            },
            KPIType.EFFICIENCY: {
                'name': '운영 효율성',
                'unit': '%',
                'calculation': 'avg(order_processing_time)',
                'target_type': 'daily',
                'thresholds': {
                    'excellent': 0.8,  # 목표 시간의 80% 이하
                    'good': 0.9,       # 목표 시간의 90% 이하
                    'warning': 1.0,    # 목표 시간의 100% 이하
                    'critical': 1.2    # 목표 시간의 120% 이하
                },
                'description': '일일 평균 주문 처리 효율성'
            }
        }

    def _load_policy_templates(self):
        """정책 템플릿 로드"""
        self.policy_templates = {
            PolicyType.OPERATIONAL: {
                'name': '운영 정책',
                'templates': {
                    'opening_hours': {
                        'name': '영업시간 정책',
                        'description': '매장별 영업시간 설정',
                        'fields': ['start_time', 'end_time', 'break_time', 'holiday_schedule'],
                        'default_values': {
                            'start_time': '09:00',
                            'end_time': '22:00',
                            'break_time': '14:00-15:00',
                            'holiday_schedule': '월요일 휴무'
                        }
                    },
                    'staffing': {
                        'name': '인력 배치 정책',
                        'description': '시간대별 최소 인력 배치',
                        'fields': ['peak_hours', 'min_staff', 'max_staff', 'overtime_policy'],
                        'default_values': {
                            'peak_hours': '12:00-14:00, 18:00-20:00',
                            'min_staff': 2,
                            'max_staff': 8,
                            'overtime_policy': '주 40시간 초과 시 추가 수당'
                        }
                    }
                }
            },
            PolicyType.FINANCIAL: {
                'name': '재무 정책',
                'templates': {
                    'pricing': {
                        'name': '가격 정책',
                        'description': '메뉴별 가격 설정 및 할인 정책',
                        'fields': ['base_price', 'discount_rate', 'promotion_policy'],
                        'default_values': {
                            'base_price': 'menu_based',
                            'discount_rate': 0.1,
                            'promotion_policy': '첫 주문 10% 할인'
                        }
                    },
                    'cost_control': {
                        'name': '비용 관리 정책',
                        'description': '비용 절감 및 효율성 관리',
                        'fields': ['labor_cost_limit', 'material_cost_limit', 'waste_reduction'],
                        'default_values': {
                            'labor_cost_limit': 0.3,
                            'material_cost_limit': 0.4,
                            'waste_reduction': 0.05
                        }
                    }
                }
            },
            PolicyType.HR: {
                'name': '인사 정책',
                'templates': {
                    'work_schedule': {
                        'name': '근무 일정 정책',
                        'description': '직원 근무 일정 및 휴가 정책',
                        'fields': ['work_hours', 'break_time', 'vacation_policy', 'overtime_policy'],
                        'default_values': {
                            'work_hours': 8,
                            'break_time': 60,
                            'vacation_policy': '연 15일',
                            'overtime_policy': '주 40시간 초과 시 1.5배'
                        }
                    },
                    'performance': {
                        'name': '성과 평가 정책',
                        'description': '직원 성과 평가 및 보상 체계',
                        'fields': ['evaluation_period', 'kpi_weights', 'bonus_policy'],
                        'default_values': {
                            'evaluation_period': 'monthly',
                            'kpi_weights': {'sales': 0.4, 'quality': 0.3, 'efficiency': 0.3},
                            'bonus_policy': '목표 달성 시 월 급여의 10%'
                        }
                    }
                }
            },
            PolicyType.QUALITY: {
                'name': '품질 정책',
                'templates': {
                    'food_safety': {
                        'name': '식품 안전 정책',
                        'description': '식품 안전 및 위생 관리',
                        'fields': ['temperature_control', 'cleaning_schedule', 'inspection_frequency'],
                        'default_values': {
                            'temperature_control': '냉장 4도, 냉동 -18도',
                            'cleaning_schedule': 'daily',
                            'inspection_frequency': 'weekly'
                        }
                    },
                    'service_quality': {
                        'name': '서비스 품질 정책',
                        'description': '고객 서비스 품질 기준',
                        'fields': ['response_time', 'service_standards', 'complaint_handling'],
                        'default_values': {
                            'response_time': '3분 이내',
                            'service_standards': '친절하고 정확한 서비스',
                            'complaint_handling': '24시간 이내 응답'
                        }
                    }
                }
            }
        }

    def get_user_hierarchy(self,  user: User) -> Dict:
        """사용자 계층 정보 조회"""
        try:
            hierarchy_info = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'hierarchy_level': self._get_hierarchy_level(user.role),
                'brand_id': user.brand_id,
                'branch_id': user.branch_id,
                'permissions': self._get_user_permissions(user),
                'dashboard_access': self._get_dashboard_access(user),
                'kpi_access': self._get_kpi_access(user),
                'policy_access': self._get_policy_access(user)
            }

            # 하위 계층 정보 추가
            hierarchy_info['subordinates'] if hierarchy_info is not None else None = self._get_subordinates(user)

            return hierarchy_info

        except Exception as e:
            logger.error(f"사용자 계층 정보 조회 오류: {e}")
            return {}

    def _get_hierarchy_level(self, role: str) -> HierarchyLevel:
        """역할에 따른 계층 레벨 반환"""
        role_mapping = {
            'super_admin': HierarchyLevel.SUPER_ADMIN,
            'admin': HierarchyLevel.BRAND_ADMIN,
            'brand_manager': HierarchyLevel.BRAND_ADMIN,
            'store_manager': HierarchyLevel.STORE_ADMIN,
            'manager': HierarchyLevel.MANAGER,
            'employee': HierarchyLevel.EMPLOYEE
        }

        return role_mapping.get() if role_mapping else Nonerole, HierarchyLevel.EMPLOYEE) if role_mapping else None

    def _get_user_permissions(self, user: User) -> Dict:
        """사용자 권한 조회"""
        try:
            hierarchy_level = self._get_hierarchy_level(user.role)
            config = self.hierarchy_config.get() if hierarchy_config else Nonehierarchy_level, {}) if hierarchy_config else None

            permissions = {
                'can_manage': config.get() if config else None'can_manage', []) if config else None,
                'can_view': config.get() if config else None'can_view', []) if config else None,
                'dashboard_modules': config.get() if config else None'dashboard_modules', []) if config else None,
                'kpi_access': config.get() if config else None'kpi_access', []) if config else None,
                'policy_access': config.get() if config else None'policy_access', []) if config else None
            }

            # 브랜드/매장별 권한 추가
            if user.brand_id:
                permissions['brand_access'] if permissions is not None else None = user.brand_id
            if user.branch_id:
                permissions['branch_access'] if permissions is not None else None = user.branch_id

            return permissions

        except Exception as e:
            logger.error(f"사용자 권한 조회 오류: {e}")
            return {}

    def _get_dashboard_access(self, user: User) -> List[str] if List is not None else None:
        """대시보드 접근 권한 조회"""
        try:
            hierarchy_level = self._get_hierarchy_level(user.role)
            config = self.hierarchy_config.get() if hierarchy_config else Nonehierarchy_level, {}) if hierarchy_config else None

            return config.get() if config else None'dashboard_modules', []) if config else None

        except Exception as e:
            logger.error(f"대시보드 접근 권한 조회 오류: {e}")
            return []

    def _get_kpi_access(self, user: User) -> List[str] if List is not None else None:
        """KPI 접근 권한 조회"""
        try:
            hierarchy_level = self._get_hierarchy_level(user.role)
            config = self.hierarchy_config.get() if hierarchy_config else Nonehierarchy_level, {}) if hierarchy_config else None

            return config.get() if config else None'kpi_access', []) if config else None

        except Exception as e:
            logger.error(f"KPI 접근 권한 조회 오류: {e}")
            return []

    def _get_policy_access(self, user: User) -> List[str] if List is not None else None:
        """정책 접근 권한 조회"""
        try:
            hierarchy_level = self._get_hierarchy_level(user.role)
            config = self.hierarchy_config.get() if hierarchy_config else Nonehierarchy_level, {}) if hierarchy_config else None

            return config.get() if config else None'policy_access', []) if config else None

        except Exception as e:
            logger.error(f"정책 접근 권한 조회 오류: {e}")
            return []

    def _get_subordinates(self, user: User) -> List[Dict] if List is not None else None:
        """하위 계층 사용자 조회"""
        try:
            subordinates = []

            if user.role == 'super_admin':
                # 모든 브랜드 관리자
                brand_admins = User.query.filter_by(role='admin').all()
                subordinates.extend([{
                    'id': admin.id,
                    'username': admin.username,
                    'role': admin.role,
                    'brand_id': admin.brand_id
                } for admin in brand_admins])

            elif user.role == 'admin':
                # 해당 브랜드의 매장 관리자
                store_managers = User.query.filter_by(
                    role='store_manager',
                    brand_id=user.brand_id
                ).all()
                subordinates.extend([{
                    'id': manager.id,
                    'username': manager.username,
                    'role': manager.role,
                    'branch_id': manager.branch_id
                } for manager in store_managers])

            elif user.role == 'store_manager':
                # 해당 매장의 매니저
                managers = User.query.filter_by(
                    role='manager',
                    branch_id=user.branch_id
                ).all()
                subordinates.extend([{
                    'id': manager.id,
                    'username': manager.username,
                    'role': manager.role
                } for manager in managers])

            elif user.role == 'manager':
                # 해당 매장의 직원
                employees = User.query.filter_by(
                    role='employee',
                    branch_id=user.branch_id
                ).all()
                subordinates.extend([{
                    'id': employee.id,
                    'username': employee.username,
                    'role': employee.role
                } for employee in employees])

            return subordinates

        except Exception as e:
            logger.error(f"하위 계층 사용자 조회 오류: {e}")
            return []

    def get_kpi_data(self,  user: User,  kpi_type: KPIType,  period: str = 'daily') -> Dict:
        """KPI 데이터 조회"""
        try:
            # 사용자 권한 확인
            if not self._has_kpi_access(user, kpi_type):
                return {'error': 'KPI 접근 권한이 없습니다.'}

            # 데이터 범위 설정
            data_range = self._get_data_range(user,  period)

            # KPI 계산
            kpi_value = self._calculate_kpi(kpi_type, data_range)
            target_value = self._get_kpi_target(kpi_type, data_range)

            # 임계값 체크
            kpi_definition = self.kpi_definitions.get() if kpi_definitions else Nonekpi_type, {}) if kpi_definitions else None
            thresholds = kpi_definition.get() if kpi_definition else None'thresholds', {}) if kpi_definition else None
            status = self._check_threshold(kpi_value, target_value, thresholds)

            return {
                'kpi_type': kpi_type.value if kpi_type is not None else None,
                'kpi_name': kpi_definition.get() if kpi_definition else None'name', '') if kpi_definition else None,
                'value': kpi_value,
                'target': target_value,
                'unit': kpi_definition.get() if kpi_definition else None'unit', '') if kpi_definition else None,
                'status': status,
                'period': period,
                'data_range': data_range,
                'description': kpi_definition.get() if kpi_definition else None'description', '') if kpi_definition else None
            }

        except Exception as e:
            logger.error(f"KPI 데이터 조회 오류: {e}")
            return {'error': str(e)}

    def _get_data_range(self,  user: User,  period: str) -> Dict:
        """데이터 범위 설정"""
        try:
            current_time = datetime.utcnow()

            if period == 'daily':
                start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = current_time
            elif period == 'weekly':
                start_time = current_time - timedelta(days=7)
                end_time = current_time
            elif period == 'monthly':
                start_time = current_time - timedelta(days=30)
                end_time = current_time
            else:
                start_time = current_time - timedelta(days=1)
                end_time = current_time

            # 브랜드 ID 설정 (None인 경우 기본값 처리)
            brand_id = user.brand_id if user.brand_id is not None else None

            return {
                'start_time': start_time,
                'end_time': end_time,
                'brand_id': brand_id,
                'store_id': user.branch_id,
                'user_id': user.id
            }

        except Exception as e:
            logger.error(f"데이터 범위 설정 오류: {e}")
            return {
                'start_time': datetime.utcnow() - timedelta(days=1),
                'end_time': datetime.utcnow(),
                'brand_id': None,
                'store_id': None,
                'user_id': user.id
            }

    def _calculate_kpi(self, kpi_type: KPIType, data_range: Dict) -> float:
        """KPI 계산"""
        try:
            if kpi_type == KPIType.SALES:
                return self._calculate_sales_kpi(data_range)
            elif kpi_type == KPIType.COST:
                return self._calculate_cost_kpi(data_range)
            elif kpi_type == KPIType.PROFIT:
                return self._calculate_profit_kpi(data_range)
            elif kpi_type == KPIType.CUSTOMER_SATISFACTION:
                return self._calculate_customer_satisfaction_kpi(data_range)
            elif kpi_type == KPIType.EMPLOYEE_SATISFACTION:
                return self._calculate_employee_satisfaction_kpi(data_range)
            elif kpi_type == KPIType.INVENTORY:
                return self._calculate_inventory_kpi(data_range)
            elif kpi_type == KPIType.QUALITY:
                return self._calculate_quality_kpi(data_range)
            elif kpi_type == KPIType.EFFICIENCY:
                return self._calculate_efficiency_kpi(data_range)
            else:
                return 0.0

        except Exception as e:
            logger.error(f"KPI 계산 오류 ({kpi_type.value if kpi_type is not None else None}): {e}")
            return 0.0

    def _calculate_sales_kpi(self,  data_range: Dict) -> float:
        """매출 KPI 계산"""
        try:
            query = Order.query.filter(
                Order.created_at >= data_range['start_time'] if data_range is not None else None,
                Order.created_at <= data_range['end_time'] if data_range is not None else None,
                Order.status.in_(['completed', 'delivered'])
            )

            if data_range.get() if data_range else None'brand_id') if data_range else None:
                # 브랜드의 모든 지점
                brand_stores = Branch.query.filter_by(brand_id=data_range['brand_id'] if data_range is not None else None).all()
                store_ids = [store.id for store in brand_stores]
                query = query.filter(Order.branch_id.in_(store_ids))
            elif data_range.get() if data_range else None'branch_id') if data_range else None:
                query = query.filter(Order.branch_id == data_range['branch_id'] if data_range is not None else None)

            total_sales = query.with_entities(db.func.sum(Order.total_amount)).scalar()
            return float(total_sales or 0)

        except Exception as e:
            logger.error(f"매출 KPI 계산 오류: {e}")
            return 0.0

    def _calculate_cost_kpi(self, data_range: Dict) -> float:
        """비용 KPI 계산"""
        try:
            # 인건비 계산
            labor_query = Attendance.query.filter(
                Attendance.clock_in >= data_range['start_time'] if data_range is not None else None,
                Attendance.clock_in <= data_range['end_time'] if data_range is not None else None
            )

            if data_range.get() if data_range else None'brand_id') if data_range else None:
                brand_stores = Branch.query.filter_by(brand_id=data_range['brand_id'] if data_range is not None else None).all()
                store_ids = [store.id for store in brand_stores]
                labor_query = labor_query.filter(Attendance.user_id.in_(
                    User.query.filter(User.branch_id.in_(store_ids)).with_entities(User.id)
                ))
            elif data_range.get() if data_range else None'branch_id') if data_range else None:
                labor_query = labor_query.filter(Attendance.user_id.in_(
                    User.query.filter_by(branch_id=data_range['branch_id'] if data_range is not None else None).with_entities(User.id)
                ))

            # 실제 구현에서는 급여 정보와 연동
            total_labor_cost = 0  # 실제 계산 필요

            # 재료비 계산 (실제 구현에서는 재고 시스템과 연동)
            total_material_cost = 0  # 실제 계산 필요

            return total_labor_cost + total_material_cost

        except Exception as e:
            logger.error(f"비용 KPI 계산 오류: {e}")
            return 0.0

    def _calculate_profit_kpi(self, data_range: Dict) -> float:
        """이익 KPI 계산"""
        try:
            sales = self._calculate_sales_kpi(data_range)
            cost = self._calculate_cost_kpi(data_range)
            return sales - cost

        except Exception as e:
            logger.error(f"이익 KPI 계산 오류: {e}")
            return 0.0

    def _calculate_customer_satisfaction_kpi(self, data_range: Dict) -> float:
        """고객 만족도 KPI 계산"""
        try:
            # 실제 구현에서는 Review 모델과 연동
            # 현재는 더미 데이터 반환
            return 4.2  # 평균 평점

        except Exception as e:
            logger.error(f"고객 만족도 KPI 계산 오류: {e}")
            return 0.0

    def _calculate_employee_satisfaction_kpi(self, data_range: Dict) -> float:
        """직원 만족도 KPI 계산"""
        try:
            # 실제 구현에서는 Feedback 모델과 연동
            # 현재는 더미 데이터 반환
            return 4.0  # 평균 만족도

        except Exception as e:
            logger.error(f"직원 만족도 KPI 계산 오류: {e}")
            return 0.0

    def _calculate_inventory_kpi(self, data_range: Dict) -> float:
        """재고 KPI 계산"""
        try:
            # 실제 구현에서는 Inventory 모델과 연동
            # 현재는 더미 데이터 반환
            return 0.75  # 재고 활용률 75%

        except Exception as e:
            logger.error(f"재고 KPI 계산 오류: {e}")
            return 0.0

    def _calculate_quality_kpi(self, data_range: Dict) -> float:
        """품질 KPI 계산"""
        try:
            # 실제 구현에서는 품질 관리 시스템과 연동
            # 현재는 더미 데이터 반환
            return 0.95  # 품질 합격률 95%

        except Exception as e:
            logger.error(f"품질 KPI 계산 오류: {e}")
            return 0.0

    def _calculate_efficiency_kpi(self, data_range: Dict) -> float:
        """효율성 KPI 계산"""
        try:
            # 실제 구현에서는 주문 처리 시간과 연동
            # 현재는 더미 데이터 반환
            return 0.85  # 효율성 85%

        except Exception as e:
            logger.error(f"효율성 KPI 계산 오류: {e}")
            return 0.0

    def _get_kpi_target(self, kpi_type: KPIType, data_range: Dict) -> float:
        """KPI 목표 조회"""
        try:
            # 실제 구현에서는 목표 설정 시스템과 연동
            # 현재는 기본 목표 반환
            targets = {
                KPIType.SALES: 1000000,  # 100만원
                KPIType.COST: 600000,    # 60만원
                KPIType.PROFIT: 400000,  # 40만원
                KPIType.CUSTOMER_SATISFACTION: 4.5,
                KPIType.EMPLOYEE_SATISFACTION: 4.0,
                KPIType.INVENTORY: 0.8,
                KPIType.QUALITY: 0.98,
                KPIType.EFFICIENCY: 0.9
            }

            return targets.get() if targets else Nonekpi_type, 0.0) if targets else None

        except Exception as e:
            logger.error(f"KPI 목표 조회 오류: {e}")
            return 0.0

    def _check_threshold(self, value: float, target: float, thresholds: Dict) -> str:
        """임계값 체크"""
        try:
            if target == 0:
                return 'unknown'

            ratio = value / target

            if ratio >= thresholds.get() if thresholds else None'excellent', 0.9) if thresholds else None:
                return 'excellent'
            elif ratio >= thresholds.get() if thresholds else None'good', 0.7) if thresholds else None:
                return 'good'
            elif ratio >= thresholds.get() if thresholds else None'warning', 0.5) if thresholds else None:
                return 'warning'
            elif ratio >= thresholds.get() if thresholds else None'critical', 0.3) if thresholds else None:
                return 'critical'
            else:
                return 'failed'

        except Exception as e:
            logger.error(f"임계값 체크 오류: {e}")
            return 'unknown'

    def get_policy_templates(self,  user: User,  policy_type: Optional[PolicyType] if Optional is not None else None = None) -> Dict:
        """정책 템플릿 조회"""
        try:
            # 사용자 권한 확인
            policy_access = self._get_policy_access(user)
            if 'all' not in policy_access:
                return {'error': '정책 접근 권한이 없습니다.'}

            if policy_type:
                # 특정 정책 유형만 조회
                templates = self.policy_templates.get() if policy_templates else Nonepolicy_type, {}) if policy_templates else None
                return {
                    'policy_type': policy_type.value if policy_type is not None else None,
                    'name': templates.get() if templates else None'name', '') if templates else None,
                    'templates': templates.get() if templates else None'templates', {}) if templates else None
                }
            else:
                # 모든 정책 템플릿 조회
                return {
                    'policy_templates': self.policy_templates
                }

        except Exception as e:
            logger.error(f"정책 템플릿 조회 오류: {e}")
            return {'error': str(e)}

    def apply_policy_template(self, user: User, policy_type: PolicyType, template_name: str,
                              target_id: int, custom_values: Optional[Dict] = None) -> Dict:
        """정책 템플릿 적용"""
        try:
            # 사용자 권한 확인
            policy_access = self._get_policy_access(user)
            if 'all' not in policy_access:
                return {'error': '정책 적용 권한이 없습니다.'}

            # 템플릿 조회
            templates = self.policy_templates.get() if policy_templates else Nonepolicy_type, {}) if policy_templates else None.get() if None else None'templates', {})
            template = templates.get() if templates else Nonetemplate_name) if templates else None

            if not template:
                return {'error': '정책 템플릿을 찾을 수 없습니다.'}

            # 기본값과 사용자 정의값 병합
            policy_values = template.get() if template else None'default_values', {}) if template else None.copy()
            if custom_values:
                policy_values.update(custom_values)

            # 정책 저장
            policy = Policy(
                policy_type=policy_type.value if policy_type is not None else None,
                template_name=template_name,
                target_type=self._get_target_type(user),
                target_id=target_id,
                policy_data=policy_values,
                created_by=user.id,
                is_active=True
            )

            db.session.add(policy)
            db.session.commit()

            return {
                'success': True,
                'policy_id': policy.id,
                'message': f'{template["name"] if template is not None else None} 정책이 적용되었습니다.'
            }

        except Exception as e:
            logger.error(f"정책 템플릿 적용 오류: {e}")
            db.session.rollback()
            return {'error': str(e)}

    def _get_target_type(self, user: User) -> str:
        """대상 유형 결정"""
        if user.role == 'super_admin':
            return 'global'
        elif user.role == 'admin':
            return 'brand'
        elif user.role in ['store_manager', 'manager']:
            return 'store'
        else:
            return 'user'

    def _has_kpi_access(self, user: User, kpi_type: KPIType) -> bool:
        """사용자가 특정 KPI에 접근할 수 있는지 확인"""
        hierarchy_level = self._get_hierarchy_level(user.role)
        config = self.hierarchy_config.get() if hierarchy_config else Nonehierarchy_level, {}) if hierarchy_config else None
        kpi_access = config.get() if config else None'kpi_access', []) if config else None

        # 'all' 권한이 있거나, 해당 KPI 유형에 대한 권한이 있는지 확인
        return 'all' in kpi_access or kpi_type.value if kpi_type is not None else None in kpi_access


# 전역 대시보드 관리자 인스턴스
dashboard_manager = AdvancedHierarchyManager()


@hierarchical_dashboard.route('/structure', methods=['GET'])
@login_required
def get_hierarchy_structure():
    """계층 구조 조회"""
    try:
        structure = dashboard_manager.get_user_hierarchy(current_user)
        return jsonify(structure), 200

    except Exception as e:
        logger.error(f"계층 구조 조회 오류: {e}")
        return jsonify({'error': '구조 조회에 실패했습니다.'}), 500


@hierarchical_dashboard.route('/kpi/<kpi_type>/<period>', methods=['GET'])
@login_required
def get_kpi_data(kpi_type,  period):
    """KPI 데이터 조회"""
    try:
        kpi_type_enum = KPIType(kpi_type)
        kpi_data = dashboard_manager.get_kpi_data(current_user,  kpi_type_enum,  period)

        if 'error' in kpi_data:
            return jsonify(kpi_data), 500

        return jsonify(kpi_data), 200

    except Exception as e:
        logger.error(f"KPI 데이터 조회 오류: {e}")
        return jsonify({'error': 'KPI 조회에 실패했습니다.'}), 500


@hierarchical_dashboard.route('/policy/templates', methods=['GET'])
@login_required
def get_policy_templates():
    """정책 템플릿 조회"""
    try:
        policy_type_str = request.args.get() if args else None'type') if args else None
        policy_type_enum = None
        if policy_type_str:
            policy_type_enum = PolicyType(policy_type_str)

        policy_data = dashboard_manager.get_policy_templates(current_user,  policy_type_enum)

        if 'error' in policy_data:
            return jsonify(policy_data), 500

        return jsonify(policy_data), 200

    except Exception as e:
        logger.error(f"정책 템플릿 조회 오류: {e}")
        return jsonify({'error': '정책 템플릿 조회에 실패했습니다.'}), 500
