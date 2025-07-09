import jwt
from functools import wraps
from flask import request, jsonify, current_app
from models import User

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
            secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 사용자 조회
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'message': '유효하지 않은 사용자입니다.'}), 401
            
            # 요청 객체에 현재 사용자 추가 (타입 무시)
            setattr(request, 'current_user', current_user)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '토큰이 만료되었습니다.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(allowed_roles):
    """역할 기반 권한 검증 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = getattr(request, 'current_user', None)
            if not current_user:
                return jsonify({'message': '인증이 필요합니다.'}), 401
            
            if current_user.role not in allowed_roles:
                return jsonify({'message': '권한이 없습니다.'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 