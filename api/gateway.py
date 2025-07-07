from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
from models import User
from extensions import db

gateway = Blueprint('gateway', __name__)

# JWT 설정
JWT_SECRET_KEY = 'your-secret-key'  # 실제 운영에서는 환경변수로 관리
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

def token_required(f):
    """JWT 토큰 검증 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': '토큰이 필요합니다'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': '유효하지 않은 토큰입니다'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '토큰이 만료되었습니다'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '유효하지 않은 토큰입니다'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(allowed_roles):
    """역할 기반 접근 제어 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in allowed_roles:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

def generate_tokens(user):
    """JWT 토큰 생성"""
    access_token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES
    }, JWT_SECRET_KEY, algorithm="HS256")
    
    refresh_token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRES
    }, JWT_SECRET_KEY, algorithm="HS256")
    
    return access_token, refresh_token

@gateway.route('/api/auth/login', methods=['POST'])
def login():
    """통합 로그인 API"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': '사용자명과 비밀번호를 입력해주세요'}), 400
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({'message': '잘못된 사용자명 또는 비밀번호입니다'}), 401
        
        if not user.is_active:
            return jsonify({'message': '비활성화된 계정입니다'}), 401
        
        access_token, refresh_token = generate_tokens(user)
        
        # 역할별 리다이렉트 정보
        redirect_info = {
            'super_admin': '/admin-dashboard',
            'brand_manager': '/brand-dashboard', 
            'store_manager': '/store-dashboard',
            'employee': '/dashboard'
        }
        
        return jsonify({
            'message': '로그인 성공',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'name': user.name,
                'email': user.email
            },
            'redirect_to': redirect_info.get(user.role, '/dashboard')
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'message': '로그인 처리 중 오류가 발생했습니다'}), 500

@gateway.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """토큰 갱신 API"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'message': '리프레시 토큰이 필요합니다'}), 400
        
        try:
            payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=["HS256"])
            user = User.query.get(payload['user_id'])
            
            if not user or not user.is_active:
                return jsonify({'message': '유효하지 않은 사용자입니다'}), 401
            
            access_token, new_refresh_token = generate_tokens(user)
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': new_refresh_token
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '리프레시 토큰이 만료되었습니다'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '유효하지 않은 리프레시 토큰입니다'}), 401
            
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'message': '토큰 갱신 중 오류가 발생했습니다'}), 500

@gateway.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """로그아웃 API"""
    # 실제 운영에서는 블랙리스트에 토큰 추가
    return jsonify({'message': '로그아웃되었습니다'}), 200

@gateway.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """사용자 프로필 조회"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'name': current_user.name,
        'email': current_user.email,
        'role': current_user.role,
        'is_active': current_user.is_active
    }), 200

@gateway.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """사용자 프로필 수정"""
    try:
        data = request.get_json()
        
        if 'name' in data:
            current_user.name = data['name']
        if 'email' in data:
            current_user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': '프로필이 업데이트되었습니다',
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'name': current_user.name,
                'email': current_user.email,
                'role': current_user.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile update error: {str(e)}")
        return jsonify({'message': '프로필 업데이트 중 오류가 발생했습니다'}), 500

# 역할별 API 접근 제어 예시
@gateway.route('/api/admin/stats', methods=['GET'])
@token_required
@role_required(['super_admin', 'brand_manager'])
def admin_stats(current_user):
    """관리자 통계 API - 슈퍼 관리자, 브랜드 관리자만 접근 가능"""
    return jsonify({
        'message': '관리자 통계 데이터',
        'role': current_user.role
    }), 200

@gateway.route('/api/store/orders', methods=['GET'])
@token_required
@role_required(['store_manager', 'employee'])
def store_orders(current_user):
    """매장 주문 API - 매장 관리자, 직원만 접근 가능"""
    return jsonify({
        'message': '매장 주문 데이터',
        'role': current_user.role
    }), 200 