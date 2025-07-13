import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from models import User, db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def jwt_required(f):
    """JWT 토큰 검증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Authorization 헤더에서 토큰 추출
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer <token>"
            except IndexError:
                return jsonify({'message': '유효하지 않은 토큰 형식입니다.'}), 401
        
        if not token:
            return jsonify({'message': '토큰이 필요합니다.'}), 401
        
        try:
            # 토큰 디코딩
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 토큰 만료 확인
            if 'exp' in payload:
                exp_timestamp = payload['exp']
                if datetime.utcnow().timestamp() > exp_timestamp:
                    return jsonify({'message': '토큰이 만료되었습니다.'}), 401
            
            # 사용자 조회
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'message': '유효하지 않은 사용자입니다.'}), 401
            
            # 사용자 상태 확인
            if current_user.status != 'approved':
                return jsonify({'message': '승인되지 않은 계정입니다.'}), 401
            
            # 요청 객체에 현재 사용자 추가
            setattr(request, 'current_user', current_user)
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '토큰이 만료되었습니다.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401
        except Exception as e:
            logger.error(f"JWT 토큰 검증 실패: {e}")
            return jsonify({'message': '토큰 검증에 실패했습니다.'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """관리자 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JWT 토큰 검증
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '유효하지 않은 토큰 형식입니다.'}), 401
        
        if not token:
            return jsonify({'message': '토큰이 필요합니다.'}), 401
        
        try:
            # 토큰 디코딩
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 사용자 조회
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'message': '유효하지 않은 사용자입니다.'}), 401
            
            # 관리자 권한 확인
            if current_user.role not in ['admin', 'brand_admin']:
                return jsonify({'message': '관리자 권한이 필요합니다.'}), 403
            
            # 요청 객체에 현재 사용자 추가
            setattr(request, 'current_user', current_user)
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '토큰이 만료되었습니다.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401
        except Exception as e:
            logger.error(f"관리자 권한 확인 실패: {e}")
            return jsonify({'message': '권한 확인에 실패했습니다.'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """로그인 필요 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JWT 토큰 검증
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '유효하지 않은 토큰 형식입니다.'}), 401
        
        if not token:
            return jsonify({'message': '로그인이 필요합니다.'}), 401
        
        try:
            # 토큰 디코딩
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 사용자 조회
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'message': '유효하지 않은 사용자입니다.'}), 401
            
            # 사용자 상태 확인
            if current_user.status != 'approved':
                return jsonify({'message': '승인되지 않은 계정입니다.'}), 401
            
            # 요청 객체에 현재 사용자 추가
            setattr(request, 'current_user', current_user)
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '토큰이 만료되었습니다.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401
        except Exception as e:
            logger.error(f"로그인 확인 실패: {e}")
            return jsonify({'message': '로그인 확인에 실패했습니다.'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """특정 역할 권한 확인 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # JWT 토큰 검증
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({'message': '유효하지 않은 토큰 형식입니다.'}), 401
            
            if not token:
                return jsonify({'message': '토큰이 필요합니다.'}), 401
            
            try:
                # 토큰 디코딩
                secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                
                # 사용자 조회
                current_user = User.query.get(payload['user_id'])
                if not current_user:
                    return jsonify({'message': '유효하지 않은 사용자입니다.'}), 401
                
                # 역할 확인
                if current_user.role not in allowed_roles:
                    return jsonify({'message': '접근 권한이 없습니다.'}), 403
                
                # 요청 객체에 현재 사용자 추가
                setattr(request, 'current_user', current_user)
                g.current_user = current_user
                
            except jwt.ExpiredSignatureError:
                return jsonify({'message': '토큰이 만료되었습니다.'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401
            except Exception as e:
                logger.error(f"역할 권한 확인 실패: {e}")
                return jsonify({'message': '권한 확인에 실패했습니다.'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(module, action="view"):
    """특정 권한 확인 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # JWT 토큰 검증
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({'message': '유효하지 않은 토큰 형식입니다.'}), 401
            
            if not token:
                return jsonify({'message': '토큰이 필요합니다.'}), 401
            
            try:
                # 토큰 디코딩
                secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                
                # 사용자 조회
                current_user = User.query.get(payload['user_id'])
                if not current_user:
                    return jsonify({'message': '유효하지 않은 사용자입니다.'}), 401
                
                # 권한 확인
                if not current_user.has_permission(module, action):
                    return jsonify({'message': f'{module}의 {action} 권한이 없습니다.'}), 403
                
                # 요청 객체에 현재 사용자 추가
                setattr(request, 'current_user', current_user)
                g.current_user = current_user
                
            except jwt.ExpiredSignatureError:
                return jsonify({'message': '토큰이 만료되었습니다.'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401
            except Exception as e:
                logger.error(f"권한 확인 실패: {e}")
                return jsonify({'message': '권한 확인에 실패했습니다.'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def manager_required(f):
    """매니저 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JWT 토큰 검증
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '유효하지 않은 토큰 형식입니다.'}), 401
        
        if not token:
            return jsonify({'message': '토큰이 필요합니다.'}), 401
        
        try:
            # 토큰 디코딩
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 사용자 조회
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'message': '유효하지 않은 사용자입니다.'}), 401
            
            # 매니저 권한 확인
            if current_user.role not in ['admin', 'brand_admin', 'store_admin', 'manager']:
                return jsonify({'message': '매니저 권한이 필요합니다.'}), 403
            
            # 요청 객체에 현재 사용자 추가
            setattr(request, 'current_user', current_user)
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '토큰이 만료되었습니다.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401
        except Exception as e:
            logger.error(f"매니저 권한 확인 실패: {e}")
            return jsonify({'message': '권한 확인에 실패했습니다.'}), 401
        
        return f(*args, **kwargs)
    return decorated_function 