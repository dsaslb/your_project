"""
API Gateway - 중앙화된 인증/인가 처리 및 역할 기반 라우팅
"""
import time
import logging
from functools import wraps
from flask import Blueprint, request, jsonify, g
from models import User
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# JWT 설정
# JWT_SECRET_KEY = "your-secret-key"  # 기존 하드코딩 제거
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

def generate_tokens(user):
    """JWT 토큰 생성"""
    from flask import current_app
    jwt_secret = current_app.config.get("JWT_SECRET_KEY", "your-secret-key")
    access_token = jwt.encode(
        {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES
        },
        jwt_secret,
        algorithm="HS256"
    )
    
    refresh_token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRES
        },
        jwt_secret,
        algorithm="HS256"
    )
    
    return access_token, refresh_token

def token_required(f):
    """JWT 토큰 필요 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app
        jwt_secret = current_app.config.get("JWT_SECRET_KEY", "your-secret-key")
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
            else:
                token = auth_header
        
        if not token:
            return jsonify({'error': '토큰이 필요합니다'}), 401
        
        try:
            data = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            user = User.query.filter_by(id=data['user_id']).first()
            if not user:
                return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
            
            # 토큰 만료 체크
            if datetime.utcnow() > datetime.fromtimestamp(data.get('exp', 0)):
                return jsonify({'error': '토큰이 만료되었습니다'}), 401
            
            g.current_user = user
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': '토큰이 만료되었습니다'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
    
    return decorated_function

def role_required(allowed_roles):
    """역할 기반 접근 제어 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user:
                return jsonify({'error': '인증이 필요합니다'}), 401
            
            # 최고 관리자는 모든 권한 허용
            if user.role == 'super_admin':
                return f(user, *args, **kwargs)
            
            if user.role not in allowed_roles:
                return jsonify({'error': '접근 권한이 없습니다'}), 403
            
            return f(user, *args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """관리자 권한 필요 데코레이터"""
    return role_required(['admin', 'super_admin'])(f)

def manager_required(f):
    """매니저 권한 필요 데코레이터"""
    return role_required(['manager', 'admin', 'super_admin'])(f)

def employee_required(f):
    """직원 권한 필요 데코레이터"""
    return role_required(['employee', 'manager', 'admin', 'super_admin'])(f)

def log_request(f):
    """요청 로깅 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        user = getattr(g, 'current_user', None)
        username = user.username if user else 'anonymous'
        
        logger.info(f"Request: {request.method} {request.path} - User: {username}")
        
        try:
            response = f(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:
                logger.warning(f"Slow API call: {f.__name__} took {execution_time:.2f}s")
            
            return response
        except Exception as e:
            logger.error(f"API Error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return decorated_function

# API Gateway Blueprint
gateway = Blueprint('gateway', __name__)

@gateway.route('/health', methods=['GET'])
def health():
    """헬스 체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@gateway.route('/login', methods=['POST'])
def login():
    """로그인 API"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token, refresh_token = generate_tokens(user)
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'name': user.name
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@gateway.route('/refresh', methods=['POST'])
def refresh_token():
    """토큰 갱신 API"""
    from flask import current_app
    jwt_secret = current_app.config.get("JWT_SECRET_KEY", "your-secret-key")
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'error': 'Refresh token required'}), 400
    
    try:
        payload = jwt.decode(refresh_token, jwt_secret, algorithms=["HS256"])
        user = User.query.filter_by(id=payload.get('user_id')).first()
        
        if not user:
            return jsonify({'error': 'Invalid user'}), 401
        
        access_token, new_refresh_token = generate_tokens(user)
        return jsonify({
            'access_token': access_token,
            'refresh_token': new_refresh_token
        })
        
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401

@gateway.route('/profile', methods=['GET'])
@token_required
@log_request
def get_profile():
    """사용자 프로필 조회"""
    user = g.current_user
    return jsonify({
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'role': user.role,
        'email': user.email
    })

@gateway.route('/logout', methods=['POST'])
@token_required
def logout():
    """로그아웃 API"""
    # JWT는 stateless이므로 클라이언트에서 토큰 삭제
    return jsonify({'message': 'Logged out successfully'}) 