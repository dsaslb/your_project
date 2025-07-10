import re
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any

from flask_login import AnonymousUserMixin as BaseAnonymousUserMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


# UserRole enum 추가
class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    BRAND_MANAGER = "brand_manager"
    STORE_MANAGER = "store_manager"
    MANAGER = "manager"
    EMPLOYEE = "employee"


# AnonymousUserMixin에 has_permission 메서드 추가
class AnonymousUserMixin(BaseAnonymousUserMixin):
    """익명 사용자용 권한 체크 메서드"""

    def has_permission(self, module, action="view"):
        return False

    def get_permissions(self):
        return {}

    def get_permission_summary(self):
        return {"role": "anonymous", "grade": "none", "modules": {}}


# 브랜드 모델
class Brand(db.Model):
    __tablename__ = "brands"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'), nullable=True)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(255))
    website = db.Column(db.String(255))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    status = db.Column(db.String(20), default="active", index=True)  # active, inactive, suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    industry = db.relationship('Industry')
    stores = db.relationship("Branch", backref="brand", lazy=True)
    brand_manager = db.relationship("User", backref="managed_brand", foreign_keys="User.brand_id")
    
    def __init__(self, **kwargs):
        super(Brand, self).__init__(**kwargs)
    
    def __repr__(self):
        return f"<Brand {self.name}>"


# 지점 모델 (기존 Branch 모델 확장)
class Branch(db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    processing_time_standard = db.Column(
        db.Integer, default=15
    )  # 기준 주문 처리 시간(분)
    
    # 계층형 구조 필드 추가
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'), nullable=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=True, index=True)
    store_code = db.Column(db.String(20), unique=True)  # 매장 코드
    store_type = db.Column(db.String(20), default="franchise")  # franchise, corporate, independent
    business_hours = db.Column(db.JSON)  # 영업시간 정보
    capacity = db.Column(db.Integer)  # 수용 인원
    status = db.Column(db.String(20), default="active", index=True)  # active, inactive, maintenance
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # 관계 설정
    industry = db.relationship('Industry')

    def __repr__(self):
        return f"<Branch {self.name}>"


# User 모델
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(
        db.String(20), default="employee", index=True
    )  # 'super_admin', 'admin', 'brand_manager', 'store_manager', 'manager', 'employee'
    grade = db.Column(
        db.String(20), default="staff", index=True
    )  # 'ceo', 'director', 'manager', 'staff'
    status = db.Column(
        db.String(20), default="pending", index=True
    )  # 'approved', 'pending', 'rejected', 'suspended'
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), index=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), index=True)  # 브랜드 매니저용
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), index=True)  # 팀 ID 추가
    position = db.Column(db.String(50), index=True)  # 직책 필드 추가
    department = db.Column(db.String(50), index=True)  # 부서 필드 추가
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    attendances = db.relationship(
        "Attendance", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    last_login = db.Column(db.DateTime, index=True)

    # JSON 기반 세밀한 권한 관리
    permissions = db.Column(
        db.JSON,
        default=lambda: {
            # 대시보드 접근 권한
            "dashboard": {"view": True, "edit": False, "admin_only": False},
            # 브랜드 관리 권한
            "brand_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "monitor": False,
            },
            # 매장 관리 권한
            "store_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "monitor": False,
            },
            # 직원 관리 권한
            "employee_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "assign_roles": False,
            },
            # 스케줄 관리 권한
            "schedule_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
            },
            # 발주 관리 권한
            "order_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
            },
            # 재고 관리 권한
            "inventory_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
            },
            # 알림 관리 권한
            "notification_management": {"view": False, "send": False, "delete": False},
            # 시스템 관리 권한
            "system_management": {
                "view": False,
                "backup": False,
                "restore": False,
                "settings": False,
                "monitoring": False,
            },
            # AI 진단 및 개선안 관리 권한
            "ai_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "monitor": False,
            },
            # 보고서 권한
            "reports": {"view": False, "export": False, "admin_only": False},
        },
    )

    # 권한 위임 정보 (최고관리자가 매장관리자에게, 매장관리자가 직원에게)
    delegated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    delegated_at = db.Column(db.DateTime, nullable=True)
    delegation_expires = db.Column(db.DateTime, nullable=True)

    # 관계 설정
    branch = db.relationship("Branch", backref="users")
    industry = db.relationship('Industry', backref='users')
    delegated_users = db.relationship(
        "User",
        backref=db.backref("delegator", remote_side=[id]),
        foreign_keys=[delegated_by],
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = self._get_default_permissions()

    def _get_default_permissions(self):
        """역할별 기본 권한 설정"""
        base_permissions = {
            "dashboard": {"view": True, "edit": False, "admin_only": False},
            "brand_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "monitor": False,
            },
            "store_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "monitor": False,
            },
            "employee_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "assign_roles": False,
            },
            "schedule_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
            },
            "order_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
            },
            "inventory_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
            },
            "notification_management": {"view": False, "send": False, "delete": False},
            "system_management": {
                "view": False,
                "backup": False,
                "restore": False,
                "settings": False,
                "monitoring": False,
            },
            "ai_management": {
                "view": False,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "monitor": False,
            },
            "reports": {"view": False, "export": False, "admin_only": False},
        }

        if self.role == "super_admin":
            # 최고관리자: 모든 권한
            for module in base_permissions:
                for action in base_permissions[module]:
                    base_permissions[module][action] = True
        elif self.role == "admin":
            # 관리자: 브랜드/매장 관리 권한 포함
            base_permissions["dashboard"]["view"] = True
            base_permissions["brand_management"]["view"] = True
            base_permissions["brand_management"]["create"] = True
            base_permissions["brand_management"]["edit"] = True
            base_permissions["brand_management"]["monitor"] = True
            base_permissions["store_management"]["view"] = True
            base_permissions["store_management"]["create"] = True
            base_permissions["store_management"]["edit"] = True
            base_permissions["store_management"]["monitor"] = True
            base_permissions["employee_management"]["view"] = True
            base_permissions["employee_management"]["create"] = True
            base_permissions["employee_management"]["edit"] = True
            base_permissions["employee_management"]["approve"] = True
            base_permissions["schedule_management"]["view"] = True
            base_permissions["schedule_management"]["create"] = True
            base_permissions["schedule_management"]["edit"] = True
            base_permissions["order_management"]["view"] = True
            base_permissions["order_management"]["create"] = True
            base_permissions["order_management"]["approve"] = True
            base_permissions["inventory_management"]["view"] = True
            base_permissions["inventory_management"]["create"] = True
            base_permissions["inventory_management"]["edit"] = True
            base_permissions["notification_management"]["view"] = True
            base_permissions["ai_management"]["view"] = True
            base_permissions["ai_management"]["monitor"] = True
            base_permissions["reports"]["view"] = True
        elif self.role == "brand_manager":
            # 브랜드 매니저: 해당 브랜드의 매장들만 관리
            base_permissions["dashboard"]["view"] = True
            base_permissions["store_management"]["view"] = True
            base_permissions["store_management"]["edit"] = True
            base_permissions["store_management"]["monitor"] = True
            base_permissions["employee_management"]["view"] = True
            base_permissions["employee_management"]["create"] = True
            base_permissions["employee_management"]["edit"] = True
            base_permissions["employee_management"]["approve"] = True
            base_permissions["schedule_management"]["view"] = True
            base_permissions["schedule_management"]["create"] = True
            base_permissions["schedule_management"]["edit"] = True
            base_permissions["order_management"]["view"] = True
            base_permissions["order_management"]["create"] = True
            base_permissions["order_management"]["approve"] = True
            base_permissions["inventory_management"]["view"] = True
            base_permissions["inventory_management"]["create"] = True
            base_permissions["inventory_management"]["edit"] = True
            base_permissions["notification_management"]["view"] = True
            base_permissions["ai_management"]["view"] = True
            base_permissions["reports"]["view"] = True
        elif self.role == "store_manager":
            # 매장 관리자: 해당 매장만 관리
            base_permissions["dashboard"]["view"] = True
            base_permissions["employee_management"]["view"] = True
            base_permissions["employee_management"]["create"] = True
            base_permissions["employee_management"]["edit"] = True
            base_permissions["schedule_management"]["view"] = True
            base_permissions["schedule_management"]["create"] = True
            base_permissions["schedule_management"]["edit"] = True
            base_permissions["order_management"]["view"] = True
            base_permissions["order_management"]["create"] = True
            base_permissions["order_management"]["approve"] = True
            base_permissions["inventory_management"]["view"] = True
            base_permissions["inventory_management"]["create"] = True
            base_permissions["inventory_management"]["edit"] = True
            base_permissions["notification_management"]["view"] = True
            base_permissions["reports"]["view"] = True
        elif self.role == "manager":
            # 매장관리자: 제한된 관리 권한
            base_permissions["dashboard"]["view"] = True
            base_permissions["schedule_management"]["view"] = True
            base_permissions["schedule_management"]["create"] = True
            base_permissions["schedule_management"]["edit"] = True
            base_permissions["order_management"]["view"] = True
            base_permissions["order_management"]["create"] = True
            base_permissions["order_management"]["approve"] = True
            base_permissions["inventory_management"]["view"] = True
            base_permissions["inventory_management"]["create"] = True
            base_permissions["inventory_management"]["edit"] = True
            base_permissions["notification_management"]["view"] = True
            base_permissions["reports"]["view"] = True
        else:
            # 직원: 기본 업무 권한
            base_permissions["dashboard"]["view"] = True
            base_permissions["schedule_management"]["view"] = True
            base_permissions["order_management"]["view"] = True
            base_permissions["order_management"]["create"] = True
            base_permissions["inventory_management"]["view"] = True

        return base_permissions

    def has_permission(self, module, action):
        """특정 모듈의 특정 액션에 대한 권한 확인"""
        if not self.permissions:
            return False

        module_perms = self.permissions.get(module, {})

        # admin_only 체크
        if module_perms.get("admin_only", False) and self.role != "admin":
            return False

        # 특정 액션 권한 확인
        return module_perms.get(action, False)

    def can_access_module(self, module):
        """모듈 접근 권한 확인"""
        return self.has_permission(module, "view")

    def can_edit_module(self, module):
        """모듈 편집 권한 확인"""
        return self.has_permission(module, "edit")

    def can_create_in_module(self, module):
        """모듈 내 생성 권한 확인"""
        return self.has_permission(module, "create")

    def can_delete_in_module(self, module):
        """모듈 내 삭제 권한 확인"""
        return self.has_permission(module, "delete")

    def can_approve_in_module(self, module):
        """모듈 내 승인 권한 확인"""
        return self.has_permission(module, "approve")

    def delegate_permissions(self, target_user, permissions, expires_in_days=30):
        """권한 위임"""
        if not self.has_permission("employee_management", "assign_roles"):
            raise PermissionError("권한 위임 권한이 없습니다.")

        # 위임된 권한 설정
        target_user.permissions.update(permissions)
        target_user.delegated_by = self.id
        target_user.delegated_at = datetime.utcnow()
        target_user.delegation_expires = datetime.utcnow() + timedelta(
            days=expires_in_days
        )

        db.session.commit()

        # 위임 알림 발송
        from utils.notify import send_notification_enhanced

        send_notification_enhanced(
            user_id=target_user.id,
            content=f"[권한 위임] {self.username}님이 {expires_in_days}일간 권한을 위임했습니다.",
        )

    def revoke_delegated_permissions(self, target_user):
        """위임된 권한 회수"""
        if target_user.delegated_by != self.id:
            raise PermissionError("해당 사용자의 권한을 회수할 수 없습니다.")

        # 기본 권한으로 복원
        target_user.permissions = target_user._get_default_permissions()
        target_user.delegated_by = None
        target_user.delegated_at = None
        target_user.delegation_expires = None

        db.session.commit()

        # 회수 알림 발송
        from utils.notify import send_notification_enhanced

        send_notification_enhanced(
            user_id=target_user.id,
            content=f"[권한 회수] {self.username}님이 위임된 권한을 회수했습니다.",
        )

    def get_delegated_users(self):
        """위임받은 사용자 목록"""
        return User.query.filter_by(delegated_by=self.id).all()

    def is_delegation_expired(self):
        """위임 권한 만료 확인"""
        if not self.delegation_expires:
            return False
        return datetime.utcnow() > self.delegation_expires

    def get_effective_permissions(self):
        """실제 적용되는 권한 (만료 체크 포함)"""
        if self.is_delegation_expired():
            return self._get_default_permissions()
        return self.permissions

    def get_permission_summary(self):
        """권한 요약 정보"""
        perms = self.get_effective_permissions()
        summary = {"role": self.role, "grade": self.grade, "modules": {}}

        for module, actions in perms.items():
            summary["modules"][module] = {
                "can_access": actions.get("view", False),
                "can_edit": actions.get("edit", False),
                "can_create": actions.get("create", False),
                "can_delete": actions.get("delete", False),
                "can_approve": actions.get("approve", False),
            }

        return summary

    def set_password(self, pw):
        if len(pw) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        if not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
            raise ValueError("비밀번호는 영문자와 숫자를 포함해야 합니다.")
        self.password_hash = generate_password_hash(pw, method="pbkdf2:sha256")

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def is_admin(self):
        return self.role == "admin"

    def is_manager(self):
        return self.role == "manager"

    def is_employee(self):
        return self.role == "employee"

    def is_owner(self):
        """1인 사장님 여부 확인"""
        return self.role == "admin" and not self.is_group_admin()

    def is_group_admin(self):
        """그룹/프랜차이즈 최고관리자 여부 확인"""
        return self.role == "admin" and self.has_permission("group_admin", "view")

    def is_solo_mode(self):
        """1인 사장님 모드에서 모든 메뉴 접근 가능 여부"""
        return self.is_owner() or self.has_permission("solo_mode", "view")

    def is_franchise_mode(self):
        """그룹/프랜차이즈 모드에서 최고관리자 메뉴만 접근 가능 여부"""
        return self.is_group_admin() or self.has_permission("franchise_mode", "view")

    def can_access_all_menus(self):
        """모든 메뉴에 접근 가능한지 확인 (1인 사장님 모드)"""
        return self.is_solo_mode()

    def can_access_admin_only_menus(self):
        """최고관리자 전용 메뉴에 접근 가능한지 확인 (그룹/프랜차이즈 모드)"""
        return self.is_franchise_mode()

    def get_dashboard_mode(self):
        """현재 사용자의 대시보드 모드 반환"""
        if self.is_solo_mode():
            return "solo"
        elif self.is_franchise_mode():
            return "franchise"
        else:
            return "employee"  # 일반 직원 모드

    def get_permissions(self):
        """현재 사용자의 모든 권한 반환"""
        return self.permissions or {}

    def set_permissions(self, permissions_dict):
        """권한 설정"""
        self.permissions = permissions_dict

    def add_permission(self, permission_name):
        """권한 추가"""
        if not self.permissions:
            self.permissions = {}
        self.permissions[permission_name] = {"view": True}

    def remove_permission(self, permission_name):
        """권한 제거"""
        if self.permissions and permission_name in self.permissions:
            self.permissions.pop(permission_name, None)

    @property
    def is_locked(self):
        if self.delegation_expires and self.delegation_expires > datetime.utcnow():
            return True
        return False

    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:
            from datetime import timedelta

            self.delegation_expires = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.delegation_expires = None
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f"<User {self.username}>"

    # 성능 최적화를 위한 인덱스 추가
    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_role', 'role'),
        db.Index('idx_user_branch_id', 'branch_id'),
        db.Index('idx_user_created_at', 'created_at'),
    )


# 출퇴근 모델
class Attendance(db.Model):
    __tablename__ = "attendances"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    clock_in = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    clock_out = db.Column(db.DateTime, index=True)
    location_in = db.Column(db.String(100))  # 출근 위치 (GPS 등)
    location_out = db.Column(db.String(100))  # 퇴근 위치
    notes = db.Column(db.Text)  # 메모
    reason = db.Column(db.String(200))  # 지각/조퇴/야근 사유 등
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 복합 인덱스 추가 (date 컬럼 관련 인덱스 제거)
    __table_args__ = (
        db.Index("idx_attendance_user_date", "user_id", "clock_in"),
        db.Index("idx_attendance_date_range", "clock_in", "clock_out"),
        db.Index('idx_attendance_user_id', 'user_id'),
        # db.Index('idx_attendance_date', 'date'),
        # db.Index('idx_attendance_date_user', 'date', 'user_id'),
        # db.Index('idx_attendance_branch_id', 'branch_id'),
        # db.Index('idx_attendance_status', 'status'),
    )

    @property
    def work_minutes(self):
        if self.clock_in and self.clock_out:
            return int((self.clock_out - self.clock_in).total_seconds() // 60)
        return 0

    @property
    def work_hours(self):
        return round(self.work_minutes / 60, 2)

    @property
    def status(self):
        from datetime import time

        work_start = time(9, 0)
        work_end = time(18, 0)
        if not self.clock_in or not self.clock_out:
            return "결근" if not self.clock_in and not self.clock_out else "미완료"
        s = []
        if self.clock_in.time() > work_start:
            s.append("지각")
        if self.clock_out.time() < work_end:
            s.append("조퇴")
        if not s:
            return "정상"
        return "/".join(s)

    @property
    def is_late(self):
        from datetime import time

        work_start = time(9, 0)
        return self.clock_in and self.clock_in.time() > work_start

    @property
    def is_early_leave(self):
        from datetime import time

        work_end = time(18, 0)
        return self.clock_out and self.clock_out.time() < work_end

    @property
    def is_overtime(self):
        return self.work_hours > 8

    def __repr__(self):
        return f"<Attendance {self.user_id} {self.clock_in.date()}>"


# 액션로그
class ActionLog(db.Model):
    __tablename__ = "action_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    action = db.Column(db.String(50), nullable=False, index=True)
    message = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))  # IPv6 지원
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_actionlog_user_action", "user_id", "action"),
        db.Index("idx_actionlog_action_date", "action", "created_at"),
    )

    def __repr__(self):
        return f"<ActionLog {self.user_id} {self.action}>"


# 피드백 모델
class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    satisfaction = db.Column(db.Integer)  # 1~5점
    health = db.Column(db.Integer)  # 1~5점
    comment = db.Column(db.String(500))  # 길이 증가
    category = db.Column(db.String(50))  # 피드백 카테고리
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Feedback {self.user_id} {self.satisfaction}>"


# 승인/거절 이력 로그
class ApproveLog(db.Model):
    __tablename__ = "approve_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    action = db.Column(
        db.String(32), nullable=False, index=True
    )  # 'approved' or 'rejected'
    timestamp = db.Column(db.DateTime, default=db.func.now(), index=True)
    admin_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )  # 처리자
    reason = db.Column(db.String(256))  # 선택: 승인/거절 사유 기록용 (옵션)
    ip_address = db.Column(db.String(45))

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_approvelog_user_action", "user_id", "action"),
        db.Index("idx_approvelog_admin_date", "admin_id", "timestamp"),
    )

    def __repr__(self):
        return f"<ApproveLog {self.user_id} {self.action} {self.timestamp}>"


# 근무 변경(교대) 신청 모델
class ShiftRequest(db.Model):
    __tablename__ = "shift_requests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    request_date = db.Column(db.Date, nullable=False, index=True)  # 신청 날짜
    desired_date = db.Column(db.Date, nullable=False, index=True)  # 희망 날짜
    reason = db.Column(db.String(255), nullable=False)  # 사유
    status = db.Column(
        db.String(20), default="pending", index=True
    )  # pending/approved/rejected
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # 관계 설정
    user = db.relationship("User", backref="shift_requests")

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_shiftrequest_user_status", "user_id", "status"),
        db.Index("idx_shiftrequest_date_range", "request_date", "desired_date"),
    )

    def __repr__(self):
        return f"<ShiftRequest {self.user_id} {self.desired_date} {self.status}>"


# 알림 모델
class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    content = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), nullable=True)  # 알림 제목 필드 추가
    category = db.Column(
        db.String(50), nullable=False, default="일반", index=True
    )  # 발주/청소/근무/교대/공지/일반
    related_url = db.Column(db.String(255), nullable=True)  # 알림 클릭 시 이동할 URL
    link = db.Column(db.String(255), nullable=True)  # 상세 페이지 링크 (별칭)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    is_admin_only = db.Column(
        db.Boolean, default=False, index=True
    )  # 관리자만 볼 수 있는 알림

    # 새로운 필드들 추가
    recipient_role = db.Column(db.String(20))  # ex. 'admin', 'manager', 'employee'
    recipient_team = db.Column(db.String(20))  # ex. '주방', '홀'
    priority = db.Column(
        db.String(10), default="일반", index=True
    )  # '긴급', '중요', '일반'
    ai_priority = db.Column(db.String(10), index=True)  # AI가 추천한 우선순위

    # 관계 설정
    user = db.relationship("User", backref="notifications")

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_notification_user_read", "user_id", "is_read"),
        db.Index("idx_notification_category_date", "category", "created_at"),
        db.Index("idx_notification_priority_date", "priority", "created_at"),
        db.Index("idx_notification_team_role", "recipient_team", "recipient_role"),
        db.Index('idx_notification_user_id', 'user_id'),
        db.Index('idx_notification_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Notification {self.id} {self.content[:20]}>"


# 공지사항 모델
class Notice(db.Model):
    __tablename__ = "notices"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255))  # 첨부파일 경로
    file_type = db.Column(db.String(20))  # 파일 확장자
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    category = db.Column(db.String(30), index=True)  # 공지사항, 자료실 등
    is_hidden = db.Column(db.Boolean, default=False, index=True)  # 숨김 처리 여부

    # 관계 설정
    author = db.relationship("User", backref="notices")
    reads = db.relationship(
        "NoticeRead", backref="notice", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "NoticeComment", backref="notice", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.Index("idx_notice_author_category", "author_id", "category"),
        db.Index("idx_notice_created", "created_at"),
    )

    def __repr__(self):
        return f"<Notice {self.title}>"


class NoticeRead(db.Model):
    __tablename__ = "notice_reads"
    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(
        db.Integer, db.ForeignKey("notices.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    read_at = db.Column(db.DateTime, default=db.func.now(), index=True)

    # 복합 인덱스 추가
    __table_args__ = (
        db.UniqueConstraint("notice_id", "user_id", name="uq_notice_user"),
        db.Index("idx_noticeread_user_notice", "user_id", "notice_id"),
    )

    def __repr__(self):
        return f"<NoticeRead {self.user_id} read {self.notice_id}>"


class NoticeComment(db.Model):
    __tablename__ = "notice_comments"
    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(
        db.Integer, db.ForeignKey("notices.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    is_hidden = db.Column(db.Boolean, default=False, index=True)  # 숨김 처리 여부

    # 관계 설정
    user = db.relationship("User", backref="notice_comments")

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_noticecomment_notice_user", "notice_id", "user_id"),
        db.Index("idx_noticecomment_created", "created_at"),
    )

    def __repr__(self):
        return f"<NoticeComment {self.id} on notice {self.notice_id}>"


class NoticeHistory(db.Model):
    __tablename__ = "notice_histories"
    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(
        db.Integer, db.ForeignKey("notices.id"), nullable=False, index=True
    )
    editor_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    before_title = db.Column(db.String(100))
    before_content = db.Column(db.Text)
    before_file_path = db.Column(db.String(255))
    before_file_type = db.Column(db.String(20))
    edited_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    action = db.Column(db.String(10), index=True)  # 'edit'/'delete'/'hide'/'unhide'
    ip_address = db.Column(db.String(45))

    # 관계 설정
    editor = db.relationship("User", backref="notice_histories")
    notice = db.relationship("Notice", backref="histories")

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_noticehistory_notice", "notice_id"),
        db.Index("idx_noticehistory_editor", "editor_id"),
    )

    def __repr__(self):
        return f"<NoticeHistory {self.id} for notice {self.notice_id}>"


class CommentHistory(db.Model):
    __tablename__ = "comment_histories"
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(
        db.Integer, db.ForeignKey("notice_comments.id"), nullable=False, index=True
    )
    editor_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    before_content = db.Column(db.Text)
    edited_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    action = db.Column(db.String(10), index=True)  # 'edit'/'delete'/'hide'/'unhide'
    ip_address = db.Column(db.String(45))

    # 관계 설정
    editor = db.relationship("User", backref="comment_histories")
    comment = db.relationship("NoticeComment", backref="histories")

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_commenthistory_comment", "comment_id"),
        db.Index("idx_commenthistory_editor", "editor_id"),
    )

    def __repr__(self):
        return f"<CommentHistory {self.id} for comment {self.comment_id}>"


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(
        db.String(10), nullable=False, index=True
    )  # 'notice'/'comment'
    target_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    reason = db.Column(db.String(100), nullable=False)
    category = db.Column(
        db.String(20), index=True
    )  # '욕설/비방', '음란', '홍보', '기타'
    detail = db.Column(db.Text)  # 상세 사유
    status = db.Column(
        db.String(20), default="pending", index=True
    )  # 'pending'/'reviewed'/'resolved'
    admin_comment = db.Column(db.Text)  # 관리자 처리 코멘트
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    reviewed_at = db.Column(db.DateTime, index=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    # 관계 설정
    reporter = db.relationship("User", foreign_keys=[user_id], backref="reports")
    reviewer = db.relationship(
        "User", foreign_keys=[reviewed_by], backref="reviewed_reports"
    )

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_report_target", "target_type", "target_id"),
        db.Index("idx_report_status_category", "status", "category"),
    )

    def __repr__(self):
        return f"<Report {self.id} for {self.target_type} {self.target_id}>"


class SystemLog(db.Model):
    """시스템 로그 모델"""

    __tablename__ = "system_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # 관계 설정
    user = db.relationship("User", backref="system_logs")

    def __repr__(self):
        return f"<SystemLog {self.action} by User {self.user_id}>"


class Suggestion(db.Model):
    __tablename__ = "suggestions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    answered_at = db.Column(db.DateTime, index=True)
    is_anonymous = db.Column(db.Boolean, default=True, index=True)

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_suggestion_created", "created_at"),
        db.Index("idx_suggestion_answered", "answered_at"),
    )

    def __repr__(self):
        return f"<Suggestion {self.id}>"


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # 직원 근무 시
    branch_id = db.Column(
        db.Integer, db.ForeignKey("branches.id"), nullable=True
    )  # 매장 정보
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    type = db.Column(db.String(16), default="work")  # 'work', 'clean'
    category = db.Column(db.String(50), nullable=False, default="근무")
    status = db.Column(
        db.String(20), nullable=False, default="대기"
    )  # 대기, 승인, 거절
    memo = db.Column(db.String(200), nullable=True)
    team = db.Column(db.String(30))  # 청소 담당 팀 (ex: "주방", "홀")
    plan = db.Column(db.String(200))  # 청소 계획 내용
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 담당자(청소 시)

    user = db.relationship(
        "User", foreign_keys=[user_id], backref=db.backref("schedules", lazy=True)
    )
    branch = db.relationship("Branch", backref="schedules")
    manager = db.relationship(
        "User", foreign_keys=[manager_id], backref="managed_schedules"
    )

    def __repr__(self):
        return f"<Schedule {self.date} {self.type} {self.user_id}>"

    # 성능 최적화를 위한 인덱스 추가
    __table_args__ = (
        db.Index('idx_schedule_user_id', 'user_id'),
        db.Index('idx_schedule_date', 'date'),
        db.Index('idx_schedule_branch_id', 'branch_id'),
        db.Index('idx_schedule_date_user', 'date', 'user_id'),
    )


class CleaningPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    plan = db.Column(db.String(200), nullable=False)
    team = db.Column(db.String(30))  # ex: "주방", "홀" 등
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 담당자(옵션)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 담당 직원

    user = db.relationship(
        "User", foreign_keys=[user_id], backref="cleaning_assignments"
    )
    manager = db.relationship(
        "User", foreign_keys=[manager_id], backref="managed_cleaning_plans"
    )

    def __repr__(self):
        return f"<CleaningPlan {self.date} {self.plan}>"


class Order(db.Model):
    """발주 모델"""

    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable=False)  # 물품명
    quantity = db.Column(db.Integer, nullable=False, default=1)  # 수량
    unit = db.Column(db.String(20), default="개")  # 단위 (kg, L, 개 등)
    order_date = db.Column(db.Date, nullable=False, default=date.today)  # 발주 날짜
    ordered_by = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )  # 발주자
    status = db.Column(
        db.String(20), default="pending", index=True
    )  # pending/approved/rejected/delivered
    detail = db.Column(db.String(500))  # 상세 설명
    memo = db.Column(db.String(500))  # 메모
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at = db.Column(db.DateTime)
    processing_minutes = db.Column(db.Integer)
    employee_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 직원
    store_id = db.Column(db.Integer, db.ForeignKey("branches.id"))  # 매장
    
    # 재고 연동 필드
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=True)
    supplier = db.Column(db.String(100))  # 공급업체
    unit_price = db.Column(db.Integer)  # 단가
    total_cost = db.Column(db.Integer)  # 총 비용
    
    # 관계 설정
    user = db.relationship("User", foreign_keys=[ordered_by])
    inventory_item = db.relationship("InventoryItem", backref="orders")

    def __repr__(self):
        return f"<Order {self.item} {self.quantity}>"

    # 성능 최적화를 위한 인덱스 추가
    __table_args__ = (
        db.Index('idx_order_store_id', 'store_id'),
        db.Index('idx_order_created_at', 'created_at'),
        db.Index('idx_order_status', 'status'),
        db.Index('idx_order_employee_id', 'employee_id'),
        db.Index('idx_order_date_status', 'created_at', 'status'),
    )


class InventoryItem(db.Model):
    """재고 품목 모델"""
    
    __tablename__ = "inventory_items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)  # 품목명
    category = db.Column(db.String(100), nullable=False, index=True)  # 카테고리 (육류, 채소, 조미료 등)
    current_stock = db.Column(db.Integer, default=0)  # 현재 재고량
    min_stock = db.Column(db.Integer, default=0)  # 최소 재고량
    max_stock = db.Column(db.Integer, default=1000)  # 최대 재고량
    unit = db.Column(db.String(20), default="개")  # 단위
    unit_price = db.Column(db.Integer, default=0)  # 단가
    supplier = db.Column(db.String(100))  # 공급업체
    description = db.Column(db.Text)  # 설명
    expiry_date = db.Column(db.Date)  # 유통기한
    location = db.Column(db.String(100))  # 보관 위치
    status = db.Column(db.String(20), default="active", index=True)  # active, inactive, discontinued
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 매장 정보
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=False)
    branch = db.relationship("Branch", backref="inventory_items")
    
    # 재고 변동 이력
    stock_movements = db.relationship("StockMovement", backref="inventory_item", cascade="all, delete-orphan")
    
    @property
    def stock_status(self):
        """재고 상태"""
        if self.current_stock <= 0:
            return "품절"
        elif self.current_stock <= self.min_stock:
            return "부족"
        elif self.current_stock >= self.max_stock * 0.9:
            return "과다"
        else:
            return "충분"
    
    @property
    def total_value(self):
        """총 재고 가치"""
        return self.current_stock * self.unit_price
    
    @property
    def stock_ratio(self):
        """재고 비율 (최소 재고 대비)"""
        if self.min_stock == 0:
            return 100
        return (self.current_stock / self.min_stock) * 100
    
    def __repr__(self):
        return f"<InventoryItem {self.name} {self.current_stock}/{self.min_stock}>"


class StockMovement(db.Model):
    """재고 변동 이력 모델"""
    
    __tablename__ = "stock_movements"
    id = db.Column(db.Integer, primary_key=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False, index=True)
    movement_type = db.Column(db.String(20), nullable=False, index=True)  # in, out, adjust
    quantity = db.Column(db.Integer, nullable=False)  # 변동 수량 (양수: 입고, 음수: 출고)
    before_stock = db.Column(db.Integer, nullable=False)  # 변동 전 재고
    after_stock = db.Column(db.Integer, nullable=False)  # 변동 후 재고
    reason = db.Column(db.String(200))  # 변동 사유
    reference_type = db.Column(db.String(20))  # 참조 타입 (order, your_program_order, manual)
    reference_id = db.Column(db.Integer)  # 참조 ID
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 관계 설정
    created_by_user = db.relationship("User", backref="stock_movements")
    
    def __repr__(self):
        return f"<StockMovement {self.inventory_item_id} {self.movement_type} {self.quantity}>"


class AttendanceEvaluation(db.Model):
    """근태 평가 모델"""

    __tablename__ = "attendance_evaluations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    date_from = db.Column(db.Date, nullable=False, index=True)
    date_to = db.Column(db.Date, nullable=False, index=True)
    total_days = db.Column(db.Integer, default=0)
    late_count = db.Column(db.Integer, default=0)
    early_leave_count = db.Column(db.Integer, default=0)
    overtime_count = db.Column(db.Integer, default=0)
    normal_count = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)  # 0-100점
    grade = db.Column(db.String(5), default="D")  # A+, A, B+, B, C+, C, D
    comment = db.Column(db.Text)  # 관리자 평가 코멘트
    evaluator_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 관계 설정
    user = db.relationship(
        "User", foreign_keys=[user_id], backref="attendance_evaluations"
    )
    evaluator = db.relationship(
        "User", foreign_keys=[evaluator_id], backref="evaluated_attendance"
    )

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index(
            "idx_attendance_evaluation_user_period", "user_id", "date_from", "date_to"
        ),
        db.Index("idx_attendance_evaluation_score", "score"),
        db.Index("idx_attendance_evaluation_grade", "grade"),
    )

    def __repr__(self):
        return f"<AttendanceEvaluation {self.user_id} {self.date_from}~{self.date_to} {self.grade}>"


class AttendanceReport(db.Model):
    """근태 평가 리포트 모델"""

    __tablename__ = "attendance_reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    period_from = db.Column(db.Date, nullable=False)
    period_to = db.Column(db.Date, nullable=False)
    total = db.Column(db.Integer, default=0)
    late = db.Column(db.Integer, default=0)
    early = db.Column(db.Integer, default=0)
    ot = db.Column(db.Integer, default=0)
    ontime = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    grade = db.Column(db.String(10), default="")
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    warning = db.Column(db.Boolean, default=False)  # 경고 여부 추가

    # 관계
    user = db.relationship("User", foreign_keys=[user_id], backref="attendance_reports")
    creator = db.relationship(
        "User", foreign_keys=[created_by], backref="created_reports"
    )

    def __repr__(self):
        return f"<AttendanceReport {self.user_id} {self.period_from}~{self.period_to}>"


class ReasonTemplate(db.Model):
    """근태 사유 템플릿 모델"""

    __tablename__ = "reason_templates"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), unique=True, nullable=False, comment="사유 텍스트")
    team = db.Column(db.String(30), comment="팀별 템플릿(옵션)")
    status = db.Column(
        db.String(20), default="pending", comment="승인 상태: pending/approved/rejected"
    )
    is_active = db.Column(db.Boolean, default=True, comment="활성화 여부")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), comment="생성자")
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), comment="승인자")
    approved_at = db.Column(db.DateTime, comment="승인일시")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="생성일시")
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="수정일시",
    )
    approval_comment = db.Column(db.String(200))  # 승인/거절 코멘트

    # 관계
    creator = db.relationship(
        "User", foreign_keys=[created_by], backref="created_templates"
    )
    approver = db.relationship(
        "User", foreign_keys=[approved_by], backref="approved_templates"
    )

    def __repr__(self):
        return f"<ReasonTemplate {self.text}>"


class ReasonEditLog(db.Model):
    """근태 사유 변경 이력 모델"""

    __tablename__ = "reason_edit_logs"

    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(
        db.Integer,
        db.ForeignKey("attendances.id"),
        nullable=False,
        comment="근태 기록 ID",
    )
    old_reason = db.Column(db.String(200), comment="이전 사유")
    new_reason = db.Column(db.String(200), comment="새 사유")
    edited_by = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, comment="수정자"
    )
    edited_at = db.Column(db.DateTime, default=datetime.utcnow, comment="수정일시")
    ip_address = db.Column(db.String(45), comment="IP 주소")
    user_agent = db.Column(db.String(500), comment="사용자 에이전트")

    # 관계
    attendance = db.relationship("Attendance", backref="reason_edit_logs")
    editor = db.relationship("User", backref="reason_edits")

    # 복합 인덱스
    __table_args__ = (
        db.Index("idx_reason_edit_attendance", "attendance_id"),
        db.Index("idx_reason_edit_editor", "edited_by"),
        db.Index("idx_reason_edit_date", "edited_at"),
    )

    def __repr__(self):
        return f"<ReasonEditLog {self.attendance_id} {self.edited_at}>"


class Excuse(db.Model):
    """소명(이의제기) 모델"""

    __tablename__ = "excuses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    attendance_report_id = db.Column(
        db.Integer, db.ForeignKey("attendance_reports.id"), nullable=True, index=True
    )
    attendance_evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey("attendance_evaluations.id"),
        nullable=True,
        index=True,
    )
    title = db.Column(db.String(200), nullable=False, comment="소명 제목")
    content = db.Column(db.Text, nullable=False, comment="소명 내용")
    status = db.Column(
        db.String(20),
        default="pending",
        index=True,
        comment="상태: pending/reviewed/accepted/rejected",
    )
    priority = db.Column(
        db.String(10), default="일반", index=True, comment="우선순위: 긴급/중요/일반"
    )
    category = db.Column(db.String(50), default="근태평가", comment="소명 카테고리")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    reviewed_at = db.Column(db.DateTime, index=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    admin_comment = db.Column(db.Text, comment="관리자 답변")

    # 관계
    user = db.relationship("User", foreign_keys=[user_id], backref="excuses")
    reviewer = db.relationship(
        "User", foreign_keys=[reviewed_by], backref="reviewed_excuses"
    )
    attendance_report = db.relationship("AttendanceReport", backref="excuses")
    attendance_evaluation = db.relationship("AttendanceEvaluation", backref="excuses")

    # 복합 인덱스
    __table_args__ = (
        db.Index("idx_excuse_user_status", "user_id", "status"),
        db.Index("idx_excuse_status_date", "status", "created_at"),
        db.Index("idx_excuse_reviewer_date", "reviewed_by", "reviewed_at"),
    )

    def __repr__(self):
        return f"<Excuse {self.user_id} {self.title}>"


class ExcuseResponse(db.Model):
    """소명 답변 모델"""

    __tablename__ = "excuse_responses"

    id = db.Column(db.Integer, primary_key=True)
    excuse_id = db.Column(
        db.Integer, db.ForeignKey("excuses.id"), nullable=False, index=True
    )
    responder_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    content = db.Column(db.Text, nullable=False, comment="답변 내용")
    response_type = db.Column(
        db.String(20),
        default="comment",
        index=True,
        comment="답변 유형: comment/decision/request",
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 관계
    excuse = db.relationship("Excuse", backref="responses")
    responder = db.relationship("User", backref="excuse_responses")

    # 복합 인덱스
    __table_args__ = (
        db.Index("idx_excuseresponse_excuse_date", "excuse_id", "created_at"),
        db.Index("idx_excuseresponse_responder_date", "responder_id", "created_at"),
    )

    def __repr__(self):
        return f"<ExcuseResponse {self.excuse_id} {self.responder_id}>"


class Team(db.Model):
    """팀 모델"""

    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment="팀명")
    description = db.Column(db.String(200), comment="팀 설명")
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), comment="팀장 ID")
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), comment="소속 지점")
    is_active = db.Column(db.Boolean, default=True, comment="활성화 여부")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="생성일시")
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="수정일시",
    )
    permissions = db.Column(db.JSON, default=dict)

    # 관계
    manager = db.relationship(
        "User", foreign_keys=[manager_id], backref="managed_teams"
    )
    branch = db.relationship("Branch", backref="teams")
    members = db.relationship("User", backref="team", foreign_keys="User.team_id")

    def __repr__(self):
        return f"<Team {self.name}>"


# PermissionChangeLog 모델은 User.permissions 기반으로 단순화되어 제거됨


# UserPermission 모델은 User.permissions 기반으로 단순화되어 제거됨


# PermissionTemplate 모델은 User.permissions 기반으로 단순화되어 제거됨


class FeedbackIssue(db.Model):
    __tablename__ = "feedback_issues"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"))
    status = db.Column(
        db.String(32), default="pending"
    )  # 'pending', 'in_progress', 'resolved'

    user = db.relationship("User", backref="feedback_issues")
    branch = db.relationship("Branch", backref="feedback_issues")

    def __repr__(self):
        return f"<FeedbackIssue {self.title}>"


class your_programOrder(db.Model):
    """레스토랑 주문 처리 시간 측정 모델"""

    __tablename__ = "your_program_orders"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(
        db.String(50), unique=True, nullable=False, index=True
    )  # 주문번호
    customer_name = db.Column(db.String(100))  # 고객명
    order_items = db.Column(db.Text, nullable=False)  # 주문 메뉴 (JSON 형태)
    total_amount = db.Column(db.Integer, nullable=False)  # 총 금액
    status = db.Column(
        db.String(20), default="pending", index=True
    )  # pending/processing/completed/cancelled

    # 처리 시간 관련 필드
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )  # 주문 생성 시간
    completed_at = db.Column(db.DateTime, index=True)  # 처리 완료 시간
    processing_minutes = db.Column(db.Integer, index=True)  # 처리 소요 시간(분)

    # 매장/직원 정보
    store_id = db.Column(
        db.Integer, db.ForeignKey("branches.id"), nullable=False, index=True
    )
    employee_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )  # 처리 직원

    # 추가 정보
    notes = db.Column(db.Text)  # 메모
    payment_method = db.Column(db.String(20), default="cash")  # 결제 방법
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 재고 연동 필드
    stock_consumed = db.Column(db.Boolean, default=False)  # 재고 소비 처리 여부

    # 관계 설정
    store = db.relationship("Branch", backref="your_program_orders")
    employee = db.relationship("User", backref="processed_orders")

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_your_program_order_store_status", "store_id", "status"),
        db.Index("idx_your_program_order_employee_date", "employee_id", "created_at"),
        db.Index("idx_your_program_order_processing_time", "processing_minutes"),
        db.Index(
            "idx_your_program_order_created_completed", "created_at", "completed_at"
        ),
    )

    def __repr__(self):
        return f"<your_programOrder {self.order_number} {self.status}>"

    @property
    def is_over_standard(self):
        """기준 시간 초과 여부 확인"""
        if not self.processing_minutes or not self.store:
            return False
        return self.processing_minutes > self.store.processing_time_standard

    @property
    def standard_time(self):
        """매장별 기준 시간 반환"""
        return self.store.processing_time_standard if self.store else 15


class OrderFeedback(db.Model):
    """주문 처리 경고/칭찬 피드백 모델"""

    __tablename__ = "order_feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True
    )
    employee_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    type = db.Column(db.String(16), nullable=False, index=True)  # 'warn', 'praise'
    message = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 관계 설정
    order = db.relationship("Order", backref="feedbacks")
    employee = db.relationship("User", backref="order_feedbacks")

    # 복합 인덱스 추가
    __table_args__ = (
        db.Index("idx_orderfeedback_employee_type", "employee_id", "type"),
        db.Index("idx_orderfeedback_created", "created_at"),
    )

    def __repr__(self):
        return f"<OrderFeedback {self.id} {self.type} for Order {self.order_id}>"


class OrderRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(128))
    quantity = db.Column(db.Integer)
    status = db.Column(
        db.String(32), default="pending"
    )  # 'pending', 'approved', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"))
    # 관계
    user = db.relationship("User", foreign_keys=[requested_by])
    branch = db.relationship("Branch", foreign_keys=[branch_id])
    # 기타 필요 항목 자유롭게 추가


class PayTransfer(db.Model):
    """급여 이체 모델"""
    __tablename__ = "pay_transfers"
    
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)  # 이체 금액
    description = db.Column(db.String(200))  # 이체 설명
    status = db.Column(db.String(20), default="pending", index=True)  # pending/completed/failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, index=True)
    
    # 관계 설정
    from_user = db.relationship("User", foreign_keys=[from_user_id], backref="sent_transfers")
    to_user = db.relationship("User", foreign_keys=[to_user_id], backref="received_transfers")
    
    # 복합 인덱스
    __table_args__ = (
        db.Index("idx_transfer_users", "from_user_id", "to_user_id"),
        db.Index("idx_transfer_status", "status", "created_at"),
    )
    
    def __repr__(self):
        return f"<PayTransfer {self.from_user_id} -> {self.to_user_id}: {self.amount}원>"


class Payroll(db.Model):
    """급여 모델"""
    __tablename__ = "payrolls"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False, index=True)
    base_salary = db.Column(db.Integer, default=0)  # 기본급
    allowance = db.Column(db.Integer, default=0)  # 수당
    deduction = db.Column(db.Integer, default=0)  # 공제
    net_salary = db.Column(db.Integer, default=0)  # 실수령액
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship("User", backref="payrolls")
    
    # 복합 인덱스
    __table_args__ = (
        db.Index('idx_payroll_user_year_month', 'user_id', 'year', 'month'),
    )
    
    def __repr__(self):
        return f"<Payroll {self.user_id} {self.year}-{self.month}>"


class Staff(db.Model):
    """직원 모델"""
    __tablename__ = "staff"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    status = db.Column(db.String(20), default="active", index=True)  # active, on_leave, inactive
    avatar = db.Column(db.String(255))  # 프로필 이미지 경로
    join_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.String(50))  # 급여 정보
    department = db.Column(db.String(100))
    your_program_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)  # 시스템 사용자와 연결
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    your_program = db.relationship("Branch", backref="staff")
    user = db.relationship("User", backref="staff_profile")
    contracts = db.relationship("Contract", back_populates="staff", cascade="all, delete-orphan")
    health_certificates = db.relationship("HealthCertificate", back_populates="staff", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Staff {self.name}>"


class Contract(db.Model):
    """계약서 모델"""
    __tablename__ = "contracts"
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False, index=True)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    renewal_date = db.Column(db.Date, nullable=False)
    contract_type = db.Column(db.String(50), default="정규직")  # 정규직, 계약직, 파트타임 등
    salary_amount = db.Column(db.Integer)  # 계약 급여
    file_path = db.Column(db.String(255))  # 계약서 파일 경로
    file_name = db.Column(db.String(255))  # 원본 파일명
    file_size = db.Column(db.Integer)  # 파일 크기 (bytes)
    notification_sent = db.Column(db.Boolean, default=False, index=True)  # 만료 임박 알림 발송 여부
    expired_notification_sent = db.Column(db.Boolean, default=False, index=True)  # 만료 알림 발송 여부
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    staff = db.relationship("Staff", back_populates="contracts")
    
    # 복합 인덱스
    __table_args__ = (
        db.Index('idx_contract_expiry_notification', 'expiry_date', 'notification_sent'),
        db.Index('idx_contract_expired_notification', 'expiry_date', 'expired_notification_sent'),
    )
    
    @property
    def is_expiring_soon(self):
        """30일 이내에 만료되는지 확인"""
        today = datetime.now().date()
        return self.expiry_date <= today + timedelta(days=30) and self.expiry_date > today
    
    @property
    def is_expired(self):
        """만료되었는지 확인"""
        return self.expiry_date <= datetime.now().date()
    
    @property
    def days_until_expiry(self):
        """만료까지 남은 일수"""
        today = datetime.now().date()
        return (self.expiry_date - today).days
    
    def __repr__(self):
        return f"<Contract {self.contract_number} - {self.staff.name if self.staff else 'Unknown'}>"


class HealthCertificate(db.Model):
    """보건증 모델"""
    __tablename__ = "health_certificates"
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False, index=True)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    renewal_date = db.Column(db.Date, nullable=False)
    issuing_authority = db.Column(db.String(100))  # 발급 기관
    certificate_type = db.Column(db.String(50), default="식품위생교육")  # 보건증 유형
    file_path = db.Column(db.String(255))  # 보건증 파일 경로
    file_name = db.Column(db.String(255))  # 원본 파일명
    file_size = db.Column(db.Integer)  # 파일 크기 (bytes)
    notification_sent = db.Column(db.Boolean, default=False, index=True)  # 만료 임박 알림 발송 여부
    expired_notification_sent = db.Column(db.Boolean, default=False, index=True)  # 만료 알림 발송 여부
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    staff = db.relationship("Staff", back_populates="health_certificates")
    
    # 복합 인덱스
    __table_args__ = (
        db.Index('idx_healthcertificate_expiry_notification', 'expiry_date', 'notification_sent'),
        db.Index('idx_healthcertificate_expired_notification', 'expiry_date', 'expired_notification_sent'),
    )
    
    @property
    def is_expiring_soon(self):
        if self.expiry_date:
            days_left = (self.expiry_date - datetime.utcnow().date()).days
            return 0 < days_left <= 30
        return False
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < datetime.utcnow().date()
        return False
    
    @property
    def days_until_expiry(self):
        if self.expiry_date:
            return (self.expiry_date - datetime.utcnow().date()).days
        return None
    
    def __repr__(self):
        return f"<HealthCertificate {self.certificate_number} - {self.staff.name if self.staff else 'Unknown'}>"


class StaffTemplate(db.Model):
    """직원 등록 템플릿 모델"""
    __tablename__ = 'staff_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    template_type = db.Column(db.String(20), default='position')  # position, store, custom
    
    # 급여 정보
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    salary_base = db.Column(db.Integer)
    
    # 근무 조건
    work_days = db.Column(db.JSON)  # ["월", "화", "수", "목", "금"]
    work_hours_start = db.Column(db.String(5))  # "09:00"
    work_hours_end = db.Column(db.String(5))  # "18:00"
    
    # 복리후생
    benefits = db.Column(db.JSON)  # ["4대보험", "연차휴가", "식대지원"]
    
    # 권한 설정
    permissions = db.Column(db.JSON)
    
    # 필수 서류
    required_documents = db.Column(db.JSON)  # ["health_certificate", "id_card"]
    
    # 기타 설정
    probation_period = db.Column(db.Integer, default=3)  # 수습기간 (개월)
    notice_period = db.Column(db.Integer, default=1)  # 예고기간 (개월)
    
    # 메타데이터
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class StaffRegistrationStep(db.Model):
    """직원 등록 단계별 임시 저장 모델"""
    __tablename__ = 'staff_registration_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    
    # 1단계: 기본 정보
    step1_completed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    position = db.Column(db.String(50))
    department = db.Column(db.String(50))
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(255))
    
    # 2단계: 근무 조건
    step2_completed = db.Column(db.Boolean, default=False)
    work_days = db.Column(db.JSON)
    work_hours_start = db.Column(db.String(5))
    work_hours_end = db.Column(db.String(5))
    salary_base = db.Column(db.Integer)
    salary_allowance = db.Column(db.Integer)
    salary_bonus = db.Column(db.Integer)
    benefits = db.Column(db.JSON)
    
    # 3단계: 서류 정보
    step3_completed = db.Column(db.Boolean, default=False)
    health_certificate_issue_date = db.Column(db.Date)
    health_certificate_expiry_date = db.Column(db.Date)
    health_certificate_renewal_date = db.Column(db.Date)
    required_documents = db.Column(db.JSON)
    
    # 4단계: 권한 설정
    step4_completed = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.JSON)
    role = db.Column(db.String(20), default='employee')
    
    # 메타데이터
    template_id = db.Column(db.Integer, db.ForeignKey('staff_templates.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # 세션 만료 시간
    
    def is_expired(self):
        """세션이 만료되었는지 확인"""
        return datetime.utcnow() > self.expires_at
    
    def to_employee_data(self):
        """직원 데이터로 변환"""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'position': self.position,
            'department': self.department,
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'permissions': self.permissions,
            'work_days': self.work_days,
            'work_hours_start': self.work_hours_start,
            'work_hours_end': self.work_hours_end,
            'salary_base': self.salary_base,
            'salary_allowance': self.salary_allowance,
            'salary_bonus': self.salary_bonus,
            'benefits': self.benefits,
            'health_certificate_issue_date': self.health_certificate_issue_date,
            'health_certificate_expiry_date': self.health_certificate_expiry_date,
            'health_certificate_renewal_date': self.health_certificate_renewal_date,
            'required_documents': self.required_documents
        }


class ChatRoom(db.Model):
    """채팅방 모델"""
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(20), nullable=False, default='group')  # direct, group, department
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    creator = db.relationship('User', backref='created_rooms')
    participants = db.relationship('ChatParticipant', backref='room', cascade='all, delete-orphan')
    messages = db.relationship('ChatMessage', backref='room', cascade='all, delete-orphan')

class ChatMessage(db.Model):
    """채팅 메시지 모델"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.String(36), primary_key=True)
    room_id = db.Column(db.String(36), db.ForeignKey('chat_rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    user = db.relationship('User', backref='chat_messages')

class ChatParticipant(db.Model):
    """채팅방 참가자 모델"""
    __tablename__ = 'chat_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(36), db.ForeignKey('chat_rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    user = db.relationship('User', backref='chat_participations')
    
    # 복합 유니크 제약
    __table_args__ = (db.UniqueConstraint('room_id', 'user_id', name='_room_user_uc'),)


class IoTDevice(db.Model):
    __tablename__ = 'iot_devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    device_type = db.Column(db.String(32), nullable=False)  # 예: temperature, humidity, inventory, machine
    location = db.Column(db.String(128), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 관계
    data = db.relationship('IoTData', backref='device', lazy=True)

class IoTData(db.Model):
    __tablename__ = "iot_data"
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("iot_devices.id"), nullable=False)
    data_type = db.Column(db.String(32), nullable=False)  # 예: temperature, humidity, inventory, status
    value = db.Column(db.Float, nullable=True)
    extra = db.Column(db.JSON, nullable=True)  # 추가 정보(예: 상태, 경고 등)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


# AI 진단 및 개선안 관리 모델들
class AIDiagnosis(db.Model):
    """AI 진단 결과 모델"""
    __tablename__ = "ai_diagnoses"
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=True, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True, index=True)
    diagnosis_type = db.Column(db.String(50), nullable=False, index=True)  # performance, quality, efficiency, safety
    severity = db.Column(db.String(20), default="medium", index=True)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    findings = db.Column(db.JSON)  # AI 분석 결과 데이터
    recommendations = db.Column(db.JSON)  # AI 추천사항
    status = db.Column(db.String(20), default="pending", index=True)  # pending, reviewed, implemented, resolved
    priority = db.Column(db.String(20), default="normal", index=True)  # low, normal, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, index=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    implemented_at = db.Column(db.DateTime, index=True)
    implemented_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    
    # 관계 설정
    brand = db.relationship("Brand", backref="ai_diagnoses")
    store = db.relationship("Branch", backref="ai_diagnoses")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by], backref="reviewed_diagnoses")
    implementer = db.relationship("User", foreign_keys=[implemented_by], backref="implemented_diagnoses")
    
    def __repr__(self):
        return f"<AIDiagnosis {self.title}>"


class ImprovementRequest(db.Model):
    """개선 요청 모델"""
    __tablename__ = "improvement_requests"
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=True, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # system, process, equipment, training, other
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    current_issue = db.Column(db.Text)  # 현재 문제점
    proposed_solution = db.Column(db.Text)  # 제안하는 해결책
    expected_benefits = db.Column(db.Text)  # 기대 효과
    priority = db.Column(db.String(20), default="normal", index=True)  # low, normal, high, urgent
    status = db.Column(db.String(20), default="pending", index=True)  # pending, under_review, approved, rejected, implemented
    estimated_cost = db.Column(db.Integer)  # 예상 비용
    estimated_time = db.Column(db.String(50))  # 예상 소요 시간
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, index=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    admin_comment = db.Column(db.Text)  # 관리자 코멘트
    
    # 관계 설정
    brand = db.relationship("Brand", backref="improvement_requests")
    store = db.relationship("Branch", backref="improvement_requests")
    requester = db.relationship("User", foreign_keys=[requester_id], backref="improvement_requests")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by], backref="reviewed_improvements")
    
    def __repr__(self):
        return f"<ImprovementRequest {self.title}>"


class AIImprovementSuggestion(db.Model):
    """AI 개선 제안 모델"""
    __tablename__ = "ai_improvement_suggestions"
    
    id = db.Column(db.Integer, primary_key=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey("ai_diagnoses.id"), nullable=True, index=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=True, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True, index=True)
    suggestion_type = db.Column(db.String(50), nullable=False, index=True)  # automation, optimization, process, training
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    current_state = db.Column(db.JSON)  # 현재 상태 분석
    proposed_changes = db.Column(db.JSON)  # 제안하는 변경사항
    expected_impact = db.Column(db.JSON)  # 예상 영향도
    implementation_steps = db.Column(db.JSON)  # 구현 단계
    estimated_effort = db.Column(db.String(20))  # 예상 노력 (low, medium, high)
    estimated_roi = db.Column(db.Float)  # 예상 투자수익률
    confidence_score = db.Column(db.Float)  # AI 신뢰도 점수 (0-1)
    status = db.Column(db.String(20), default="suggested", index=True)  # suggested, approved, rejected, implemented
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, index=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    admin_comment = db.Column(db.Text)
    
    # 관계 설정
    diagnosis = db.relationship("AIDiagnosis", backref="suggestions")
    brand = db.relationship("Brand", backref="ai_suggestions")
    store = db.relationship("Branch", backref="ai_suggestions")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by], backref="reviewed_ai_suggestions")
    
    def __repr__(self):
        return f"<AIImprovementSuggestion {self.title}>"


class BrandDataCollection(db.Model):
    """브랜드 데이터 수집 모델"""
    __tablename__ = "brand_data_collections"
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False, index=True)
    data_type = db.Column(db.String(50), nullable=False, index=True)  # sales, performance, quality, customer_feedback
    collection_date = db.Column(db.Date, nullable=False, index=True)
    data_source = db.Column(db.String(100))  # 데이터 소스
    raw_data = db.Column(db.JSON)  # 원시 데이터
    processed_data = db.Column(db.JSON)  # 처리된 데이터
    metrics = db.Column(db.JSON)  # 계산된 지표들
    anomalies = db.Column(db.JSON)  # 이상치 데이터
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    brand = db.relationship("Brand", backref="data_collections")
    
    def __repr__(self):
        return f"<BrandDataCollection {self.brand_id} {self.data_type} {self.collection_date}>"


class StoreDataCollection(db.Model):
    """매장 데이터 수집 모델"""
    __tablename__ = "store_data_collections"
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=False, index=True)
    data_type = db.Column(db.String(50), nullable=False, index=True)  # sales, performance, quality, customer_feedback
    collection_date = db.Column(db.Date, nullable=False, index=True)
    data_source = db.Column(db.String(100))  # 데이터 소스
    raw_data = db.Column(db.JSON)  # 원시 데이터
    processed_data = db.Column(db.JSON)  # 처리된 데이터
    metrics = db.Column(db.JSON)  # 계산된 지표들
    anomalies = db.Column(db.JSON)  # 이상치 데이터
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    store = db.relationship("Branch", backref="data_collections")
    
    def __repr__(self):
        return f"<StoreDataCollection {self.store_id} {self.data_type} {self.collection_date}>"


class SystemHealth(db.Model):
    """시스템 건강도 모델"""
    __tablename__ = "system_health"
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=True, index=True)
    store_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True, index=True)
    health_date = db.Column(db.Date, nullable=False, index=True)
    overall_score = db.Column(db.Float, nullable=False)  # 전체 건강도 점수 (0-100)
    performance_score = db.Column(db.Float)  # 성능 점수
    quality_score = db.Column(db.Float)  # 품질 점수
    efficiency_score = db.Column(db.Float)  # 효율성 점수
    safety_score = db.Column(db.Float)  # 안전성 점수
    customer_satisfaction_score = db.Column(db.Float)  # 고객 만족도 점수
    issues = db.Column(db.JSON)  # 발견된 문제점들
    recommendations = db.Column(db.JSON)  # 개선 권장사항
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    brand = db.relationship("Brand", backref="system_health")
    store = db.relationship("Branch", backref="system_health")
    
    def __repr__(self):
        return f"<SystemHealth {self.brand_id or self.store_id} {self.health_date}>"


class ApprovalWorkflow(db.Model):
    """승인 워크플로우 모델"""
    __tablename__ = "approval_workflows"
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_type = db.Column(db.String(50), nullable=False, index=True)  # user_approval, improvement_approval, ai_suggestion_approval
    target_type = db.Column(db.String(50), nullable=False, index=True)  # user, improvement_request, ai_suggestion
    target_id = db.Column(db.Integer, nullable=False, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    status = db.Column(db.String(20), default="pending", index=True)  # pending, approved, rejected, cancelled
    request_data = db.Column(db.JSON)  # 요청 데이터
    approval_data = db.Column(db.JSON)  # 승인 데이터
    comments = db.Column(db.Text)  # 코멘트
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime, index=True)
    rejected_at = db.Column(db.DateTime, index=True)
    
    # 관계 설정
    requester = db.relationship("User", foreign_keys=[requester_id], backref="workflow_requests")
    approver = db.relationship("User", foreign_keys=[approver_id], backref="workflow_approvals")
    
    def __repr__(self):
        return f"<ApprovalWorkflow {self.workflow_type} {self.target_type} {self.target_id}>"


class Industry(db.Model):
    """업종 모델 (병원, 미용실, 옷가게, 레스토랑 등)"""
    __tablename__ = 'industries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))  # hex color
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    brands_list = db.relationship('Brand', backref='industry_obj', lazy='dynamic')
    plugins = db.relationship('IndustryPlugin', backref='industry', lazy='dynamic')
    
    def __repr__(self):
        return f'<Industry {self.name}>'



class IndustryPlugin(db.Model):
    """업종별 플러그인 모델"""
    __tablename__ = 'industry_plugins'
    
    id = db.Column(db.Integer, primary_key=True)
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default='1.0.0')
    is_active = db.Column(db.Boolean, default=True)
    config = db.Column(db.JSON)  # 플러그인 설정
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<IndustryPlugin {self.name}>'

class BrandPlugin(db.Model):
    """브랜드별 플러그인 모델"""
    __tablename__ = 'brand_plugins'
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default='1.0.0')
    is_active = db.Column(db.Boolean, default=True)
    config = db.Column(db.JSON)  # 플러그인 설정
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BrandPlugin {self.name}>'

class DataSyncLog(db.Model):
    """데이터 동기화 로그 모델"""
    __tablename__ = 'data_sync_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    data_before = db.Column(db.JSON)
    data_after = db.Column(db.JSON)
    sync_status = db.Column(db.String(20), default='pending')  # pending, synced, failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    synced_at = db.Column(db.DateTime)
    
    # 관계
    user = db.relationship('User', backref='sync_logs')
    
    def __repr__(self):
        return f'<DataSyncLog {self.table_name}:{self.record_id}>'

class OfflineData(db.Model):
    """오프라인 데이터 저장 모델"""
    __tablename__ = 'offline_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_id = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    data = db.Column(db.JSON, nullable=False)
    sync_status = db.Column(db.String(20), default='pending')  # pending, synced, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    synced_at = db.Column(db.DateTime)
    
    # 관계
    user = db.relationship('User', backref='offline_data')
    
    def __repr__(self):
        return f'<OfflineData {self.table_name}:{self.record_id}>'

class AIIntegration(db.Model):
    """AI 통합 모델"""
    __tablename__ = 'ai_integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # analysis, chatbot, recommendation
    provider = db.Column(db.String(50), nullable=False)  # openai, anthropic, local
    api_key = db.Column(db.String(255))
    config = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIIntegration {self.name}>'

class AIAnalysisReport(db.Model):
    """AI 분석 리포트 모델"""
    __tablename__ = 'ai_analysis_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # sales, inventory, staff, customer
    period = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    data = db.Column(db.JSON, nullable=False)  # 분석 결과 데이터
    insights = db.Column(db.JSON)  # AI 인사이트
    recommendations = db.Column(db.JSON)  # AI 추천사항
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    branch = db.relationship('Branch', backref='ai_reports')
    
    def __repr__(self):
        return f'<AIAnalysisReport {self.report_type}:{self.period}>'

class AutomationRule(db.Model):
    """자동화 규칙 모델"""
    __tablename__ = 'automation_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    trigger_type = db.Column(db.String(50), nullable=False)  # schedule, event, threshold
    trigger_config = db.Column(db.JSON, nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # notification, report, task
    action_config = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AutomationRule {self.name}>'



