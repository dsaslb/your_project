"""
접근 제어 및 권한 관리 시스템
"""

import jwt
import bcrypt
import hashlib
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import sqlite3
from functools import wraps
import re

logger = logging.getLogger(__name__)

class PermissionLevel(Enum):
    """권한 레벨"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ResourceType(Enum):
    """리소스 타입"""
    USER = "user"
    EMPLOYEE = "employee"
    SCHEDULE = "schedule"
    BRAND = "brand"
    BRANCH = "branch"
    REPORT = "report"
    SYSTEM = "system"
    CONFIG = "config"

@dataclass
class Permission:
    """권한 정의"""
    resource_type: str
    resource_id: Optional[str]
    permission_level: str
    conditions: Dict[str, Any]

@dataclass
class Role:
    """역할 정의"""
    name: str
    description: str
    permissions: List[Permission]
    is_active: bool
    created_at: str
    updated_at: str

@dataclass
class User:
    """사용자 정의"""
    id: str
    username: str
    email: str
    password_hash: str
    roles: List[str]
    is_active: bool
    last_login: Optional[str]
    failed_attempts: int
    locked_until: Optional[str]
    created_at: str
    updated_at: str

@dataclass
class Session:
    """세션 정의"""
    session_id: str
    user_id: str
    token: str
    ip_address: str
    user_agent: str
    created_at: str
    expires_at: str
    is_active: bool

class AccessControl:
    """접근 제어 시스템"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'jwt_secret': 'your-secret-key-change-this',
            'jwt_expiration': 3600,  # 1시간
            'max_failed_attempts': 5,
            'lockout_duration': 1800,  # 30분
            'password_min_length': 8,
            'password_require_special': True,
            'session_timeout': 7200,  # 2시간
            'database_file': 'security/access_control.db'
        }
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 기본 역할 및 권한 초기화
        self._init_default_roles()
        
        # 세션 관리
        self.active_sessions = {}
        self.session_lock = {}
        
        # 보안 정책
        self.security_policies = self._init_security_policies()
        
        # 감사 로거 (외부에서 주입)
        self.audit_logger = None
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            # 사용자 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    roles TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    last_login TEXT,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 역할 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    permissions TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 세션 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"접근 제어 데이터베이스 초기화 실패: {e}")
    
    def _init_default_roles(self):
        """기본 역할 초기화"""
        default_roles = {
            'super_admin': {
                'description': '시스템 최고 관리자',
                'permissions': [
                    {'resource_type': '*', 'resource_id': None, 'permission_level': 'super_admin', 'conditions': {}}
                ]
            },
            'admin': {
                'description': '시스템 관리자',
                'permissions': [
                    {'resource_type': 'user', 'resource_id': None, 'permission_level': 'admin', 'conditions': {}},
                    {'resource_type': 'employee', 'resource_id': None, 'permission_level': 'admin', 'conditions': {}},
                    {'resource_type': 'schedule', 'resource_id': None, 'permission_level': 'admin', 'conditions': {}},
                    {'resource_type': 'brand', 'resource_id': None, 'permission_level': 'admin', 'conditions': {}},
                    {'resource_type': 'branch', 'resource_id': None, 'permission_level': 'admin', 'conditions': {}}
                ]
            },
            'manager': {
                'description': '매니저',
                'permissions': [
                    {'resource_type': 'employee', 'resource_id': None, 'permission_level': 'write', 'conditions': {'department': 'own'}},
                    {'resource_type': 'schedule', 'resource_id': None, 'permission_level': 'write', 'conditions': {'branch': 'own'}},
                    {'resource_type': 'report', 'resource_id': None, 'permission_level': 'read', 'conditions': {'scope': 'branch'}}
                ]
            },
            'employee': {
                'description': '일반 직원',
                'permissions': [
                    {'resource_type': 'schedule', 'resource_id': None, 'permission_level': 'read', 'conditions': {'user_id': 'own'}},
                    {'resource_type': 'employee', 'resource_id': None, 'permission_level': 'read', 'conditions': {'user_id': 'own'}}
                ]
            }
        }
        
        for role_name, role_data in default_roles.items():
            self.create_role(role_name, role_data['description'], role_data['permissions'])
    
    def _init_security_policies(self) -> Dict[str, Any]:
        """보안 정책 초기화"""
        return {
            'password_policy': {
                'min_length': self.config['password_min_length'],
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special': self.config['password_require_special'],
                'max_age_days': 90,
                'history_count': 5
            },
            'session_policy': {
                'max_concurrent_sessions': 3,
                'timeout_minutes': self.config['session_timeout'] // 60,
                'inactivity_timeout_minutes': 30
            },
            'access_policy': {
                'max_failed_attempts': self.config['max_failed_attempts'],
                'lockout_duration_minutes': self.config['lockout_duration'] // 60,
                'require_mfa': False,
                'ip_whitelist': [],
                'ip_blacklist': []
            }
        }
    
    def create_user(self, username: str, email: str, password: str, roles: List[str] = None) -> str:
        """사용자 생성"""
        try:
            # 비밀번호 정책 검증
            if not self._validate_password_policy(password):
                raise ValueError("비밀번호가 정책을 만족하지 않습니다.")
            
            # 비밀번호 해시화
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # 사용자 ID 생성
            user_id = hashlib.sha256(f"{username}{email}{time.time()}".encode()).hexdigest()[:16]
            
            # 기본 역할 설정
            if roles is None:
                roles = ['employee']
            
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, roles, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, json.dumps(roles), True))
            
            conn.commit()
            conn.close()
            
            # 감사 로그
            if self.audit_logger:
                self.audit_logger.log_event(
                    level='INFO',
                    category='AUTHENTICATION',
                    action='user_created',
                    resource=f'user:{user_id}',
                    user_id=user_id,
                    details={'username': username, 'email': email, 'roles': roles}
                )
            
            logger.info(f"사용자 생성 완료: {username}")
            return user_id
            
        except Exception as e:
            logger.error(f"사용자 생성 실패: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> Optional[str]:
        """사용자 인증"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            # 사용자 조회
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user_data = cursor.fetchone()
            
            if not user_data:
                self._record_failed_attempt(username, ip_address)
                return None
            
            # 컬럼명 가져오기
            columns = [description[0] for description in cursor.description]
            user = dict(zip(columns, user_data))
            
            # 계정 잠금 확인
            if user['locked_until'] and datetime.fromisoformat(user['locked_until']) > datetime.now():
                logger.warning(f"잠긴 계정 로그인 시도: {username}")
                return None
            
            # 비밀번호 검증
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                self._record_failed_attempt(username, ip_address)
                return None
            
            # 로그인 성공 - 실패 횟수 초기화
            cursor.execute('''
                UPDATE users 
                SET failed_attempts = 0, locked_until = NULL, last_login = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (datetime.now().isoformat(), user['id']))
            
            conn.commit()
            conn.close()
            
            # 세션 생성
            session_id = self._create_session(user['id'], ip_address, user_agent)
            
            # 감사 로그
            if self.audit_logger:
                self.audit_logger.log_event(
                    level='INFO',
                    category='AUTHENTICATION',
                    action='login_success',
                    resource=f'user:{user["id"]}',
                    user_id=user['id'],
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            
            logger.info(f"사용자 로그인 성공: {username}")
            return session_id
            
        except Exception as e:
            logger.error(f"사용자 인증 실패: {e}")
            return None
    
    def _record_failed_attempt(self, username: str, ip_address: str = None):
        """실패한 로그인 시도 기록"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET failed_attempts = failed_attempts + 1, updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            ''', (username,))
            
            # 실패 횟수 확인
            cursor.execute('SELECT failed_attempts FROM users WHERE username = ?', (username,))
            failed_attempts = cursor.fetchone()[0]
            
            # 계정 잠금
            if failed_attempts >= self.config['max_failed_attempts']:
                lockout_until = (datetime.now() + timedelta(seconds=self.config['lockout_duration'])).isoformat()
                cursor.execute('''
                    UPDATE users 
                    SET locked_until = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE username = ?
                ''', (lockout_until, username))
                
                logger.warning(f"계정 잠금: {username} (IP: {ip_address})")
            
            conn.commit()
            conn.close()
            
            # 감사 로그
            if self.audit_logger:
                self.audit_logger.log_event(
                    level='WARNING',
                    category='AUTHENTICATION',
                    action='login_failure',
                    resource=f'user:{username}',
                    ip_address=ip_address,
                    details={'failed_attempts': failed_attempts}
                )
                
        except Exception as e:
            logger.error(f"실패한 로그인 시도 기록 실패: {e}")
    
    def _create_session(self, user_id: str, ip_address: str = None, user_agent: str = None) -> str:
        """세션 생성"""
        try:
            # JWT 토큰 생성
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds=self.config['jwt_expiration']),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.config['jwt_secret'], algorithm='HS256')
            
            # 세션 ID 생성
            session_id = hashlib.sha256(f"{user_id}{token}{time.time()}".encode()).hexdigest()[:16]
            
            # 세션 만료 시간
            expires_at = (datetime.now() + timedelta(seconds=self.config['session_timeout'])).isoformat()
            
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (session_id, user_id, token, ip_address, user_agent, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, token, ip_address, user_agent, expires_at))
            
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            logger.error(f"세션 생성 실패: {e}")
            raise
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 검증"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.*, u.username, u.roles, u.is_active 
                FROM sessions s 
                JOIN users u ON s.user_id = u.id 
                WHERE s.session_id = ? AND s.is_active = 1
            ''', (session_id,))
            
            session_data = cursor.fetchone()
            conn.close()
            
            if not session_data:
                return None
            
            # 컬럼명 가져오기
            columns = ['session_id', 'user_id', 'token', 'ip_address', 'user_agent', 
                      'created_at', 'expires_at', 'is_active', 'username', 'roles', 'is_active_user']
            session = dict(zip(columns, session_data))
            
            # 만료 확인
            if datetime.fromisoformat(session['expires_at']) < datetime.now():
                self._invalidate_session(session_id)
                return None
            
            # 사용자 활성 상태 확인
            if not session['is_active_user']:
                self._invalidate_session(session_id)
                return None
            
            # JWT 토큰 검증
            try:
                payload = jwt.decode(session['token'], self.config['jwt_secret'], algorithms=['HS256'])
                if payload['user_id'] != session['user_id']:
                    return None
            except jwt.ExpiredSignatureError:
                self._invalidate_session(session_id)
                return None
            except jwt.InvalidTokenError:
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"세션 검증 실패: {e}")
            return None
    
    def _invalidate_session(self, session_id: str):
        """세션 무효화"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('UPDATE sessions SET is_active = 0 WHERE session_id = ?', (session_id,))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"세션 무효화 실패: {e}")
    
    def logout(self, session_id: str):
        """로그아웃"""
        try:
            session = self.validate_session(session_id)
            if session:
                self._invalidate_session(session_id)
                
                # 감사 로그
                if self.audit_logger:
                    self.audit_logger.log_event(
                        level='INFO',
                        category='AUTHENTICATION',
                        action='logout',
                        resource=f'user:{session["user_id"]}',
                        user_id=session['user_id']
                    )
                
                logger.info(f"사용자 로그아웃: {session['username']}")
            
        except Exception as e:
            logger.error(f"로그아웃 실패: {e}")
    
    def check_permission(self, user_id: str, resource_type: str, resource_id: str, permission_level: str) -> bool:
        """권한 확인"""
        try:
            # 사용자 정보 조회
            user = self.get_user_by_id(user_id)
            if not user or not user['is_active']:
                return False
            
            # 사용자 역할 조회
            roles = json.loads(user['roles'])
            
            # 각 역할의 권한 확인
            for role_name in roles:
                role = self.get_role(role_name)
                if not role or not role['is_active']:
                    continue
                
                permissions = json.loads(role['permissions'])
                
                for permission in permissions:
                    if self._check_single_permission(permission, resource_type, resource_id, permission_level, user):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"권한 확인 실패: {e}")
            return False
    
    def _check_single_permission(self, permission: Dict[str, Any], resource_type: str, resource_id: str, 
                                permission_level: str, user: Dict[str, Any]) -> bool:
        """단일 권한 확인"""
        # 리소스 타입 확인
        if permission['resource_type'] != '*' and permission['resource_type'] != resource_type:
            return False
        
        # 리소스 ID 확인
        if permission['resource_id'] and permission['resource_id'] != resource_id:
            return False
        
        # 권한 레벨 확인
        if not self._check_permission_level(permission['permission_level'], permission_level):
            return False
        
        # 조건 확인
        conditions = permission.get('conditions', {})
        if conditions and not self._check_conditions(conditions, user, resource_id):
            return False
        
        return True
    
    def _check_permission_level(self, required_level: str, requested_level: str) -> bool:
        """권한 레벨 확인"""
        level_hierarchy = {
            'read': 1,
            'write': 2,
            'delete': 3,
            'admin': 4,
            'super_admin': 5
        }
        
        required = level_hierarchy.get(required_level, 0)
        requested = level_hierarchy.get(requested_level, 0)
        
        return requested >= required
    
    def _check_conditions(self, conditions: Dict[str, Any], user: Dict[str, Any], resource_id: str) -> bool:
        """권한 조건 확인"""
        for key, value in conditions.items():
            if key == 'user_id' and value == 'own':
                # 자신의 리소스만 접근 가능
                if resource_id != user['id']:
                    return False
            elif key == 'department' and value == 'own':
                # 자신의 부서 리소스만 접근 가능
                # 실제 구현에서는 사용자의 부서 정보를 확인
                pass
            elif key == 'branch' and value == 'own':
                # 자신의 지점 리소스만 접근 가능
                # 실제 구현에서는 사용자의 지점 정보를 확인
                pass
        
        return True
    
    def create_role(self, name: str, description: str, permissions: List[Dict[str, Any]]) -> bool:
        """역할 생성"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO roles (name, description, permissions, is_active)
                VALUES (?, ?, ?, ?)
            ''', (name, description, json.dumps(permissions), True))
            
            conn.commit()
            conn.close()
            
            logger.info(f"역할 생성 완료: {name}")
            return True
            
        except Exception as e:
            logger.error(f"역할 생성 실패: {e}")
            return False
    
    def get_role(self, name: str) -> Optional[Dict[str, Any]]:
        """역할 조회"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM roles WHERE name = ?', (name,))
            role_data = cursor.fetchone()
            conn.close()
            
            if not role_data:
                return None
            
            columns = [description[0] for description in cursor.description]
            role = dict(zip(columns, role_data))
            
            return role
            
        except Exception as e:
            logger.error(f"역할 조회 실패: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 ID로 조회"""
        try:
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                return None
            
            columns = [description[0] for description in cursor.description]
            user = dict(zip(columns, user_data))
            
            return user
            
        except Exception as e:
            logger.error(f"사용자 조회 실패: {e}")
            return None
    
    def _validate_password_policy(self, password: str) -> bool:
        """비밀번호 정책 검증"""
        policy = self.security_policies['password_policy']
        
        if len(password) < policy['min_length']:
            return False
        
        if policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            return False
        
        if policy['require_lowercase'] and not re.search(r'[a-z]', password):
            return False
        
        if policy['require_digits'] and not re.search(r'\d', password):
            return False
        
        if policy['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """비밀번호 변경"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            # 기존 비밀번호 확인
            if not bcrypt.checkpw(old_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return False
            
            # 새 비밀번호 정책 검증
            if not self._validate_password_policy(new_password):
                return False
            
            # 새 비밀번호 해시화
            new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            conn = sqlite3.connect(self.config['database_file'])
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_password_hash, user_id))
            
            conn.commit()
            conn.close()
            
            # 감사 로그
            if self.audit_logger:
                self.audit_logger.log_event(
                    level='INFO',
                    category='AUTHENTICATION',
                    action='password_change',
                    resource=f'user:{user_id}',
                    user_id=user_id
                )
            
            logger.info(f"비밀번호 변경 완료: {user['username']}")
            return True
            
        except Exception as e:
            logger.error(f"비밀번호 변경 실패: {e}")
            return False
    
    def require_permission(self, resource_type: str, permission_level: str = 'read'):
        """권한 요구 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 세션에서 사용자 ID 추출 (실제 구현에서는 request에서 추출)
                user_id = kwargs.get('user_id') or args[0].get('user_id') if args else None
                
                if not user_id:
                    raise PermissionError("사용자 인증이 필요합니다.")
                
                # 리소스 ID 추출 (실제 구현에서는 request에서 추출)
                resource_id = kwargs.get('resource_id') or args[0].get('resource_id') if args else None
                
                if not self.check_permission(user_id, resource_type, resource_id, permission_level):
                    raise PermissionError(f"{resource_type}에 대한 {permission_level} 권한이 없습니다.")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

# 전역 접근 제어 인스턴스
access_control = AccessControl() 