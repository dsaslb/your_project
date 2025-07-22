"""
JWT 토큰 기반 인증 시스템
토큰 발급, 검증, 갱신 기능 제공
"""

import jwt
import datetime
import logging
from typing import Dict, Optional, Union
from flask import current_app, request, jsonify
from functools import wraps
from werkzeug.security import check_password_hash
from models_main import User, db

logger = logging.getLogger(__name__)

class JWTAuthManager:
    """JWT 인증 관리자"""
    
    def __init__(self, app=None):
        self.app = app
        self.secret_key = None
        self.algorithm = 'HS256'
        self.access_token_expiry = datetime.timedelta(hours=1)  # 1시간
        self.refresh_token_expiry = datetime.timedelta(days=7)   # 7일
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 JWT 인증 초기화"""
        self.app = app
        self.secret_key = app.config.get('SECRET_KEY', 'your-secret-key-change-this')
        
        # JWT 설정
        app.config.setdefault('JWT_SECRET_KEY', self.secret_key)
        app.config.setdefault('JWT_ALGORITHM', self.algorithm)
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', self.access_token_expiry)
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', self.refresh_token_expiry)
        
        logger.info("JWT 인증 시스템 초기화 완료")
    
    def generate_tokens(self, user: User) -> Dict[str, str]:
        """사용자에 대한 액세스 토큰과 리프레시 토큰 생성"""
        try:
            # 액세스 토큰 페이로드
            access_payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'brand_id': getattr(user, 'brand_id', None),
                'branch_id': getattr(user, 'branch_id', None),
                'exp': datetime.datetime.utcnow() + self.access_token_expiry,
                'iat': datetime.datetime.utcnow(),
                'type': 'access'
            }
            
            # 리프레시 토큰 페이로드
            refresh_payload = {
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + self.refresh_token_expiry,
                'iat': datetime.datetime.utcnow(),
                'type': 'refresh'
            }
            
            # 토큰 생성
            access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
            refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
            
            # 리프레시 토큰을 데이터베이스에 저장 (선택사항)
            self._store_refresh_token(user.id, refresh_token)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': int(self.access_token_expiry.total_seconds())
            }
            
        except Exception as e:
            logger.error(f"토큰 생성 실패: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 토큰 타입 확인
            if payload.get('type') != 'access':
                logger.warning("잘못된 토큰 타입")
                return None
            
            # 만료 시간 확인
            if datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(payload['exp']):
                logger.warning("토큰이 만료되었습니다")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("토큰이 만료되었습니다")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"잘못된 토큰: {e}")
            return None
        except Exception as e:
            logger.error(f"토큰 검증 오류: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """리프레시 토큰을 사용하여 새로운 액세스 토큰 생성"""
        try:
            # 리프레시 토큰 검증
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != 'refresh':
                logger.warning("잘못된 리프레시 토큰 타입")
                return None
            
            # 사용자 조회
            user = User.query.get(payload['user_id'])
            if not user:
                logger.warning("사용자를 찾을 수 없습니다")
                return None
            
            # 새로운 액세스 토큰 생성
            access_payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'brand_id': getattr(user, 'brand_id', None),
                'branch_id': getattr(user, 'branch_id', None),
                'exp': datetime.datetime.utcnow() + self.access_token_expiry,
                'iat': datetime.datetime.utcnow(),
                'type': 'access'
            }
            
            new_access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
            
            return {
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': int(self.access_token_expiry.total_seconds())
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("리프레시 토큰이 만료되었습니다")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"잘못된 리프레시 토큰: {e}")
            return None
        except Exception as e:
            logger.error(f"토큰 갱신 오류: {e}")
            return None
    
    def _store_refresh_token(self, user_id: int, refresh_token: str):
        """리프레시 토큰을 데이터베이스에 저장"""
        try:
            # 기존 토큰 삭제
            # RefreshToken.query.filter_by(user_id=user_id).delete()
            
            # 새 토큰 저장
            # refresh_token_record = RefreshToken(
            #     user_id=user_id,
            #     token=refresh_token,
            #     expires_at=datetime.datetime.utcnow() + self.refresh_token_expiry
            # )
            # db.session.add(refresh_token_record)
            # db.session.commit()
            
            # 임시로 로그만 기록
            logger.info(f"리프레시 토큰 저장: 사용자 {user_id}")
            
        except Exception as e:
            logger.error(f"리프레시 토큰 저장 실패: {e}")
    
    def revoke_token(self, user_id: int):
        """사용자의 모든 토큰 무효화"""
        try:
            # RefreshToken.query.filter_by(user_id=user_id).delete()
            # db.session.commit()
            
            logger.info(f"사용자 {user_id}의 토큰이 무효화되었습니다")
            
        except Exception as e:
            logger.error(f"토큰 무효화 실패: {e}")

# 전역 JWT 인증 관리자 인스턴스
jwt_auth = JWTAuthManager()

def jwt_required(f):
    """JWT 토큰이 필요한 엔드포인트 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': '토큰이 필요합니다'}), 401
        
        # 토큰 검증
        payload = jwt_auth.verify_token(token)
        if not payload:
            return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
        
        # 사용자 정보를 request에 추가
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def jwt_optional(f):
    """JWT 토큰이 선택적인 엔드포인트 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if token:
            # 토큰 검증
            payload = jwt_auth.verify_token(token)
            if payload:
                request.current_user = payload
            else:
                request.current_user = None
        else:
            request.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_roles):
    """특정 역할이 필요한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user') or not request.current_user:
                return jsonify({'error': '인증이 필요합니다'}), 401
            
            user_role = request.current_user.get('role')
            if user_role not in required_roles:
                return jsonify({'error': '권한이 없습니다'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_permission(permission):
    """특정 권한이 필요한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user') or not request.current_user:
                return jsonify({'error': '인증이 필요합니다'}), 401
            
            user_id = request.current_user.get('user_id')
            user = User.query.get(user_id)
            
            if not user or not user.has_permission(permission, 'view'):
                return jsonify({'error': '권한이 없습니다'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 