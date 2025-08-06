import os
import jwt
import bcrypt
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AuthConfig:
    """인증 설정 클래스"""
    secret_key: str
    token_expiry_hours: int = 24
    refresh_token_expiry_days: int = 7
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    password_min_length: int = 8
    require_special_chars: bool = True
    require_numbers: bool = True
    require_uppercase: bool = True
    session_timeout_minutes: int = 60

@dataclass
class User:
    """사용자 정보"""
    user_id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool = True
    is_locked: bool = False
    failed_login_attempts: int = 0
    last_login: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Role:
    """역할 정보"""
    role_id: str
    name: str
    description: str
    permissions: List[str]
    is_active: bool = True
    created_at: datetime = None

@dataclass
class Permission:
    """권한 정보"""
    permission_id: str
    name: str
    description: str
    resource: str
    action: str
    is_active: bool = True

@dataclass
class UserSession:
    """사용자 세션 정보"""
    session_id: str
    user_id: str
    token: str
    refresh_token: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    is_active: bool = True

@dataclass
class SecurityEvent:
    """보안 이벤트 정보"""
    event_id: str
    user_id: Optional[str]
    event_type: str  # login_success, login_failed, logout, password_change, etc.
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    timestamp: datetime
    severity: str = "info"  # info, warning, error, critical

class AuthManager:
    """인증 및 권한 관리자 클래스"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self.sessions: Dict[str, UserSession] = {}
        self.security_events: List[SecurityEvent] = []
        
        # 인증 디렉토리 생성
        os.makedirs("./auth/data", exist_ok=True)
        
        # 데이터베이스 초기화
        self.init_database()
        
        # 기본 역할 및 권한 생성
        self.create_default_roles_and_permissions()
        
        # 기본 관리자 사용자 생성
        self.create_default_admin()
    
    def init_database(self):
        """인증 데이터베이스 초기화"""
        db_path = "./auth/data/auth.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 사용자 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                is_locked INTEGER DEFAULT 0,
                failed_login_attempts INTEGER DEFAULT 0,
                last_login TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 역할 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                permissions TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 권한 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                resource TEXT NOT NULL,
                action TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # 세션 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 보안 이벤트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT,
                event_type TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_default_roles_and_permissions(self):
        """기본 역할 및 권한 생성"""
        # 기본 권한 생성
        default_permissions = [
            {
                'name': 'dashboard_read',
                'description': '대시보드 조회',
                'resource': 'dashboard',
                'action': 'read'
            },
            {
                'name': 'users_manage',
                'description': '사용자 관리',
                'resource': 'users',
                'action': 'manage'
            },
            {
                'name': 'stores_manage',
                'description': '매장 관리',
                'resource': 'stores',
                'action': 'manage'
            },
            {
                'name': 'inventory_manage',
                'description': '재고 관리',
                'resource': 'inventory',
                'action': 'manage'
            },
            {
                'name': 'orders_manage',
                'description': '주문 관리',
                'resource': 'orders',
                'action': 'manage'
            },
            {
                'name': 'reports_view',
                'description': '보고서 조회',
                'resource': 'reports',
                'action': 'read'
            },
            {
                'name': 'settings_manage',
                'description': '설정 관리',
                'resource': 'settings',
                'action': 'manage'
            }
        ]
        
        for perm_data in default_permissions:
            self.create_permission(**perm_data)
        
        # 기본 역할 생성
        admin_permissions = [p['name'] for p in default_permissions]
        manager_permissions = ['dashboard_read', 'stores_manage', 'inventory_manage', 'orders_manage', 'reports_view']
        employee_permissions = ['dashboard_read', 'inventory_manage', 'orders_manage']
        
        self.create_role('admin', '시스템 관리자', '전체 시스템 관리 권한', admin_permissions)
        self.create_role('manager', '매니저', '매장 및 직원 관리 권한', manager_permissions)
        self.create_role('employee', '직원', '기본 업무 권한', employee_permissions)
    
    def create_default_admin(self):
        """기본 관리자 사용자 생성"""
        admin_user = {
            'username': 'admin',
            'email': 'admin@quantum.com',
            'password': 'Admin123!',
            'full_name': '시스템 관리자',
            'role': 'admin'
        }
        
        # 관리자가 없을 때만 생성
        if not self.get_user_by_username('admin'):
            self.create_user(**admin_user)
            logger.info("기본 관리자 사용자가 생성되었습니다")
    
    def create_permission(self, name: str, description: str, resource: str, action: str) -> str:
        """권한 생성"""
        permission_id = str(uuid.uuid4())
        
        permission = Permission(
            permission_id=permission_id,
            name=name,
            description=description,
            resource=resource,
            action=action
        )
        
        self.permissions[permission_id] = permission
        self._save_permission(permission)
        
        logger.info(f"권한 생성: {name}")
        return permission_id
    
    def create_role(self, name: str, description: str, permissions: List[str]) -> str:
        """역할 생성"""
        role_id = str(uuid.uuid4())
        
        role = Role(
            role_id=role_id,
            name=name,
            description=description,
            permissions=permissions,
            created_at=datetime.utcnow()
        )
        
        self.roles[role_id] = role
        self._save_role(role)
        
        logger.info(f"역할 생성: {name}")
        return role_id
    
    def create_user(self, username: str, email: str, password: str, full_name: str, role: str) -> str:
        """사용자 생성"""
        # 비밀번호 검증
        password_validation = self.validate_password(password)
        if not password_validation['valid']:
            raise ValueError(f"비밀번호가 요구사항을 충족하지 않습니다: {password_validation['message']}")
        
        # 비밀번호 해시화
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_id = str(uuid.uuid4())
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.users[user_id] = user
        self._save_user(user, password_hash)
        
        logger.info(f"사용자 생성: {username}")
        return user_id
    
    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[Dict[str, Any]]:
        """사용자 인증"""
        user = self.get_user_by_username(username)
        if not user:
            self._log_security_event(None, 'login_failed', ip_address, user_agent, {
                'username': username,
                'reason': '사용자를 찾을 수 없음'
            }, 'warning')
            return None
        
        # 계정 잠금 확인
        if user.is_locked:
            self._log_security_event(user.user_id, 'login_failed', ip_address, user_agent, {
                'reason': '계정이 잠겨있음'
            }, 'warning')
            return None
        
        # 비밀번호 검증
        stored_hash = self._get_user_password_hash(user.user_id)
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            # 로그인 실패 횟수 증가
            user.failed_login_attempts += 1
            user.updated_at = datetime.utcnow()
            
            # 최대 시도 횟수 초과 시 계정 잠금
            if user.failed_login_attempts >= self.config.max_login_attempts:
                user.is_locked = True
                self._log_security_event(user.user_id, 'account_locked', ip_address, user_agent, {
                    'reason': '최대 로그인 시도 횟수 초과'
                }, 'error')
            
            self._update_user(user)
            
            self._log_security_event(user.user_id, 'login_failed', ip_address, user_agent, {
                'reason': '잘못된 비밀번호',
                'failed_attempts': user.failed_login_attempts
            }, 'warning')
            return None
        
        # 로그인 성공
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        self._update_user(user)
        
        # JWT 토큰 생성
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        
        # 세션 생성
        session = self._create_session(user.user_id, access_token, refresh_token, ip_address, user_agent)
        
        self._log_security_event(user.user_id, 'login_success', ip_address, user_agent, {
            'session_id': session.session_id
        }, 'info')
        
        return {
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            },
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': self.config.token_expiry_hours * 3600
        }
    
    def refresh_token(self, refresh_token: str, ip_address: str, user_agent: str) -> Optional[Dict[str, Any]]:
        """토큰 갱신"""
        try:
            # 리프레시 토큰 검증
            payload = jwt.decode(refresh_token, self.config.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return None
            
            user = self.get_user_by_id(user_id)
            if not user or not user.is_active:
                return None
            
            # 세션 확인
            session = self._get_session_by_refresh_token(refresh_token)
            if not session or not session.is_active:
                return None
            
            # 새로운 토큰 생성
            new_access_token = self._generate_access_token(user)
            new_refresh_token = self._generate_refresh_token(user)
            
            # 세션 업데이트
            session.token = new_access_token
            session.refresh_token = new_refresh_token
            session.expires_at = datetime.utcnow() + timedelta(days=self.config.refresh_token_expiry_days)
            session.updated_at = datetime.utcnow()
            
            self._update_session(session)
            
            return {
                'access_token': new_access_token,
                'refresh_token': new_refresh_token,
                'expires_in': self.config.token_expiry_hours * 3600
            }
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def logout(self, user_id: str, session_id: str, ip_address: str, user_agent: str):
        """로그아웃"""
        # 세션 비활성화
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.is_active = False
            self._update_session(session)
        
        self._log_security_event(user_id, 'logout', ip_address, user_agent, {
            'session_id': session_id
        }, 'info')
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return None
            
            user = self.get_user_by_id(user_id)
            if not user or not user.is_active or user.is_locked:
                return None
            
            # 세션 확인
            session = self._get_session_by_token(token)
            if not session or not session.is_active:
                return None
            
            return {
                'user_id': user_id,
                'username': user.username,
                'role': user.role,
                'permissions': self.get_user_permissions(user_id)
            }
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def check_permission(self, user_id: str, permission_name: str) -> bool:
        """권한 확인"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user_permissions = self.get_user_permissions(user_id)
        return permission_name in user_permissions
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """사용자 권한 조회"""
        user = self.get_user_by_id(user_id)
        if not user:
            return []
        
        role = self.get_role_by_name(user.role)
        if not role:
            return []
        
        return role.permissions
    
    def change_password(self, user_id: str, current_password: str, new_password: str, ip_address: str, user_agent: str) -> bool:
        """비밀번호 변경"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # 현재 비밀번호 확인
        stored_hash = self._get_user_password_hash(user_id)
        if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash.encode('utf-8')):
            self._log_security_event(user_id, 'password_change_failed', ip_address, user_agent, {
                'reason': '현재 비밀번호가 올바르지 않음'
            }, 'warning')
            return False
        
        # 새 비밀번호 검증
        password_validation = self.validate_password(new_password)
        if not password_validation['valid']:
            self._log_security_event(user_id, 'password_change_failed', ip_address, user_agent, {
                'reason': password_validation['message']
            }, 'warning')
            return False
        
        # 새 비밀번호 해시화 및 저장
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self._update_user_password(user_id, new_password_hash)
        
        # 사용자 정보 업데이트
        user.updated_at = datetime.utcnow()
        self._update_user(user)
        
        self._log_security_event(user_id, 'password_change_success', ip_address, user_agent, {}, 'info')
        return True
    
    def unlock_account(self, user_id: str) -> bool:
        """계정 잠금 해제"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_locked = False
        user.failed_login_attempts = 0
        user.updated_at = datetime.utcnow()
        
        self._update_user(user)
        
        logger.info(f"계정 잠금 해제: {user.username}")
        return True
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """비밀번호 정책 검증"""
        if len(password) < self.config.password_min_length:
            return {
                'valid': False,
                'message': f'비밀번호는 최소 {self.config.password_min_length}자 이상이어야 합니다'
            }
        
        if self.config.require_uppercase and not any(c.isupper() for c in password):
            return {
                'valid': False,
                'message': '비밀번호는 대문자를 포함해야 합니다'
            }
        
        if self.config.require_numbers and not any(c.isdigit() for c in password):
            return {
                'valid': False,
                'message': '비밀번호는 숫자를 포함해야 합니다'
            }
        
        if self.config.require_special_chars and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return {
                'valid': False,
                'message': '비밀번호는 특수문자를 포함해야 합니다'
            }
        
        return {'valid': True, 'message': '비밀번호가 요구사항을 충족합니다'}
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """이름으로 역할 조회"""
        for role in self.roles.values():
            if role.name == name:
                return role
        return None
    
    def get_all_users(self) -> List[User]:
        """모든 사용자 조회"""
        return list(self.users.values())
    
    def get_all_roles(self) -> List[Role]:
        """모든 역할 조회"""
        return list(self.roles.values())
    
    def get_security_events(self, user_id: Optional[str] = None, limit: int = 100) -> List[SecurityEvent]:
        """보안 이벤트 조회"""
        events = self.security_events
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        # 최신 순으로 정렬
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]
    
    def _generate_access_token(self, user: User) -> str:
        """액세스 토큰 생성"""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=self.config.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.config.secret_key, algorithm='HS256')
    
    def _generate_refresh_token(self, user: User) -> str:
        """리프레시 토큰 생성"""
        payload = {
            'user_id': user.user_id,
            'exp': datetime.utcnow() + timedelta(days=self.config.refresh_token_expiry_days),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.config.secret_key, algorithm='HS256')
    
    def _create_session(self, user_id: str, token: str, refresh_token: str, ip_address: str, user_agent: str) -> UserSession:
        """세션 생성"""
        session_id = str(uuid.uuid4())
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            token=token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=self.config.refresh_token_expiry_days)
        )
        
        self.sessions[session_id] = session
        self._save_session(session)
        
        return session
    
    def _get_session_by_token(self, token: str) -> Optional[UserSession]:
        """토큰으로 세션 조회"""
        for session in self.sessions.values():
            if session.token == token and session.is_active:
                return session
        return None
    
    def _get_session_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """리프레시 토큰으로 세션 조회"""
        for session in self.sessions.values():
            if session.refresh_token == refresh_token and session.is_active:
                return session
        return None
    
    def _log_security_event(self, user_id: Optional[str], event_type: str, ip_address: str, user_agent: str, details: Dict[str, Any], severity: str):
        """보안 이벤트 로깅"""
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            timestamp=datetime.utcnow(),
            severity=severity
        )
        
        self.security_events.append(event)
        self._save_security_event(event)
        
        logger.info(f"보안 이벤트: {event_type} - {user_id or 'anonymous'}")
    
    # 데이터베이스 저장 메서드들
    def _save_user(self, user: User, password_hash: str):
        """사용자를 데이터베이스에 저장"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, email, password_hash, full_name, role, is_active, is_locked, 
             failed_login_attempts, last_login, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.user_id,
            user.username,
            user.email,
            password_hash,
            user.full_name,
            user.role,
            1 if user.is_active else 0,
            1 if user.is_locked else 0,
            user.failed_login_attempts,
            user.last_login.isoformat() if user.last_login else None,
            user.created_at.isoformat(),
            user.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _update_user(self, user: User):
        """사용자 정보 업데이트"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET is_active = ?, is_locked = ?, failed_login_attempts = ?, last_login = ?, updated_at = ?
            WHERE user_id = ?
        ''', (
            1 if user.is_active else 0,
            1 if user.is_locked else 0,
            user.failed_login_attempts,
            user.last_login.isoformat() if user.last_login else None,
            user.updated_at.isoformat(),
            user.user_id
        ))
        
        conn.commit()
        conn.close()
    
    def _update_user_password(self, user_id: str, password_hash: str):
        """사용자 비밀번호 업데이트"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE user_id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        conn.close()
    
    def _get_user_password_hash(self, user_id: str) -> str:
        """사용자 비밀번호 해시 조회"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else ""
    
    def _save_role(self, role: Role):
        """역할을 데이터베이스에 저장"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO roles 
            (role_id, name, description, permissions, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            role.role_id,
            role.name,
            role.description,
            ','.join(role.permissions),
            1 if role.is_active else 0,
            role.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_permission(self, permission: Permission):
        """권한을 데이터베이스에 저장"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO permissions 
            (permission_id, name, description, resource, action, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            permission.permission_id,
            permission.name,
            permission.description,
            permission.resource,
            permission.action,
            1 if permission.is_active else 0
        ))
        
        conn.commit()
        conn.close()
    
    def _save_session(self, session: UserSession):
        """세션을 데이터베이스에 저장"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (session_id, user_id, token, refresh_token, ip_address, user_agent, 
             created_at, expires_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.session_id,
            session.user_id,
            session.token,
            session.refresh_token,
            session.ip_address,
            session.user_agent,
            session.created_at.isoformat(),
            session.expires_at.isoformat(),
            1 if session.is_active else 0
        ))
        
        conn.commit()
        conn.close()
    
    def _update_session(self, session: UserSession):
        """세션 업데이트"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET token = ?, refresh_token = ?, expires_at = ?, is_active = ?
            WHERE session_id = ?
        ''', (
            session.token,
            session.refresh_token,
            session.expires_at.isoformat(),
            1 if session.is_active else 0,
            session.session_id
        ))
        
        conn.commit()
        conn.close()
    
    def _save_security_event(self, event: SecurityEvent):
        """보안 이벤트를 데이터베이스에 저장"""
        db_path = "./auth/data/auth.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_events 
            (event_id, user_id, event_type, ip_address, user_agent, details, timestamp, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.event_id,
            event.user_id,
            event.event_type,
            event.ip_address,
            event.user_agent,
            str(event.details),
            event.timestamp.isoformat(),
            event.severity
        ))
        
        conn.commit()
        conn.close() 