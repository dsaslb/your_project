#!/usr/bin/env python3
"""
인증 관리자 모듈
"""

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import current_app

logger = logging.getLogger(__name__)

class AuthConfig:
    """인증 설정 클래스"""
    
    def __init__(self, 
                 secret_key: str = None,
                 token_expiry_hours: int = 24,
                 refresh_token_expiry_days: int = 7,
                 max_login_attempts: int = 5,
                 lockout_duration_minutes: int = 30,
                 password_min_length: int = 8,
                 require_special_chars: bool = True,
                 require_numbers: bool = True,
                 require_uppercase: bool = True,
                 session_timeout_minutes: int = 60):
        
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'default-secret-key')
        self.token_expiry_hours = token_expiry_hours
        self.refresh_token_expiry_days = refresh_token_expiry_days
        self.max_login_attempts = max_login_attempts
        self.lockout_duration_minutes = lockout_duration_minutes
        self.password_min_length = password_min_length
        self.require_special_chars = require_special_chars
        self.require_numbers = require_numbers
        self.require_uppercase = require_uppercase
        self.session_timeout_minutes = session_timeout_minutes

class AuthManager:
    """인증 관리자 클래스"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.login_attempts = {}  # 사용자별 로그인 시도 횟수
        self.lockout_times = {}   # 사용자별 계정 잠금 시간
        
    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[Dict[str, Any]]:
        """사용자 인증"""
        try:
            # 계정 잠금 확인
            if self._is_account_locked(username):
                return None
                
            # 사용자 검증 (실제로는 데이터베이스에서 확인)
            if self._validate_credentials(username, password):
                # 로그인 성공 시 시도 횟수 초기화
                self.login_attempts.pop(username, None)
                
                # 토큰 생성
                access_token = self._generate_access_token(username)
                refresh_token = self._generate_refresh_token(username)
                
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': self.config.token_expiry_hours * 3600,
                    'user': {
                        'username': username,
                        'role': 'user'  # 실제로는 데이터베이스에서 가져옴
                    }
                }
            else:
                # 로그인 실패 시 시도 횟수 증가
                self._increment_login_attempts(username)
                return None
                
        except Exception as e:
            logger.error(f"인증 오류: {e}")
            return None
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("토큰이 만료되었습니다")
            return None
        except jwt.InvalidTokenError:
            logger.warning("유효하지 않은 토큰입니다")
            return None
        except Exception as e:
            logger.error(f"토큰 검증 오류: {e}")
            return None
    
    def refresh_token(self, refresh_token: str, ip_address: str, user_agent: str) -> Optional[Dict[str, Any]]:
        """토큰 갱신"""
        try:
            payload = jwt.decode(refresh_token, self.config.secret_key, algorithms=['HS256'])
            username = payload.get('username')
            
            if not username:
                return None
            
            # 새로운 액세스 토큰 생성
            new_access_token = self._generate_access_token(username)
            
            return {
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': self.config.token_expiry_hours * 3600
            }
            
        except Exception as e:
            logger.error(f"토큰 갱신 오류: {e}")
            return None
    
    def logout(self, user_id: str, session_id: str, ip_address: str, user_agent: str) -> bool:
        """사용자 로그아웃"""
        try:
            # 세션 무효화 로직 (실제로는 Redis나 데이터베이스에서 처리)
            logger.info(f"사용자 {user_id} 로그아웃: {ip_address}")
            return True
        except Exception as e:
            logger.error(f"로그아웃 오류: {e}")
            return False
    
    def check_permission(self, user_id: str, permission_name: str) -> bool:
        """사용자 권한 확인"""
        try:
            # 실제로는 데이터베이스에서 사용자 권한 확인
            # 현재는 테스트용으로 True 반환
            return True
        except Exception as e:
            logger.error(f"권한 확인 오류: {e}")
            return False
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """사용자 자격 증명 검증"""
        # 실제로는 데이터베이스에서 사용자 정보 확인
        # 현재는 테스트용으로 간단한 검증
        return username == 'admin' and password == 'password'
    
    def _generate_access_token(self, username: str) -> str:
        """액세스 토큰 생성"""
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=self.config.token_expiry_hours),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, self.config.secret_key, algorithm='HS256')
    
    def _generate_refresh_token(self, username: str) -> str:
        """리프레시 토큰 생성"""
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(days=self.config.refresh_token_expiry_days),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(payload, self.config.secret_key, algorithm='HS256')
    
    def _is_account_locked(self, username: str) -> bool:
        """계정 잠금 상태 확인"""
        if username not in self.lockout_times:
            return False
        
        lockout_time = self.lockout_times[username]
        if datetime.utcnow() < lockout_time:
            return True
        
        # 잠금 시간이 지났으면 해제
        del self.lockout_times[username]
        return False
    
    def _increment_login_attempts(self, username: str):
        """로그인 시도 횟수 증가"""
        current_attempts = self.login_attempts.get(username, 0) + 1
        self.login_attempts[username] = current_attempts
        
        if current_attempts >= self.config.max_login_attempts:
            # 계정 잠금
            lockout_time = datetime.utcnow() + timedelta(minutes=self.config.lockout_duration_minutes)
            self.lockout_times[username] = lockout_time
            logger.warning(f"사용자 {username} 계정 잠금: {self.config.lockout_duration_minutes}분")
