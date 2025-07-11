"""
고급 보안 API
JWT 토큰 관리, API 요청 제한, 데이터 암호화, 보안 헤더 설정
"""

from flask import Blueprint, jsonify, request, current_app, g
from flask_login import current_user
from functools import wraps
import logging
import jwt
import hashlib
import hmac
import time
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import redis
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

security_enhanced_bp = Blueprint('security_enhanced', __name__)

# Redis 연결 (캐시 및 세션 관리)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_available = True
except:
    redis_available = False
    logger.warning("Redis not available, using in-memory storage")

# 메모리 기반 저장소 (Redis 대체)
memory_store = {}

class SecurityManager:
    """보안 관리자"""
    
    def __init__(self):
        # 애플리케이션 컨텍스트가 있을 때만 설정 가져오기
        try:
            self.secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
            self.jwt_secret = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key')
        except RuntimeError:
            # 애플리케이션 컨텍스트가 없을 때 기본값 사용
            self.secret_key = 'default-secret-key'
            self.jwt_secret = 'jwt-secret-key'
        
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # API 요청 제한 설정
        self.rate_limits = {
            'default': {'requests': 100, 'window': 3600},  # 1시간에 100회
            'auth': {'requests': 5, 'window': 300},        # 5분에 5회
            'admin': {'requests': 1000, 'window': 3600},   # 1시간에 1000회
        }
    
    def generate_jwt_token(self, user_id: int, role: str, expires_in: int = 3600) -> str:
        """JWT 토큰 생성"""
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(32)  # JWT ID
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # 토큰을 Redis에 저장 (블랙리스트 관리용)
        if redis_available:
            redis_client.setex(f"jwt:{token}", expires_in, 'valid')
        else:
            memory_store[f"jwt:{token}"] = {
                'valid': True,
                'expires': time.time() + expires_in
            }
        
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWT 토큰 검증"""
        try:
            # 블랙리스트 확인
            if redis_available:
                if not redis_client.exists(f"jwt:{token}"):
                    return None
            else:
                if f"jwt:{token}" not in memory_store:
                    return None
            
            # 토큰 디코딩
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # 만료 확인
            if datetime.utcnow().timestamp() > payload['exp']:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"JWT 토큰 만료: {token[:20]}...")
            return None
        except jwt.InvalidTokenError:
            logger.warning(f"유효하지 않은 JWT 토큰: {token[:20]}...")
            return None
        except Exception as e:
            logger.error(f"JWT 토큰 검증 오류: {e}")
            return None
    
    def revoke_jwt_token(self, token: str) -> bool:
        """JWT 토큰 무효화"""
        try:
            if redis_available:
                redis_client.delete(f"jwt:{token}")
            else:
                memory_store.pop(f"jwt:{token}", None)
            return True
        except Exception as e:
            logger.error(f"JWT 토큰 무효화 오류: {e}")
            return False
    
    def check_rate_limit(self, user_id: int, endpoint: str = 'default') -> bool:
        """API 요청 제한 확인"""
        limit_config = self.rate_limits.get(endpoint, self.rate_limits['default'])
        current_time = int(time.time())
        window_start = current_time - limit_config['window']
        
        # 사용자별 요청 기록 키
        key = f"rate_limit:{user_id}:{endpoint}"
        
        if redis_available:
            # Redis에서 요청 기록 가져오기
            requests = redis_client.zrangebyscore(key, window_start, current_time)
            
            # 요청 수 확인 (requests는 리스트이므로 len() 사용 가능)
            if isinstance(requests, list) and len(requests) >= limit_config['requests']:
                return False
            
            # 새 요청 기록
            redis_client.zadd(key, {str(current_time): current_time})
            redis_client.expire(key, limit_config['window'])
            
        else:
            # 메모리에서 요청 기록 관리
            if key not in memory_store:
                memory_store[key] = []
            
            requests = [req for req in memory_store[key] if req >= window_start]
            
            if len(requests) >= limit_config['requests']:
                return False
            
            requests.append(current_time)
            memory_store[key] = requests
        
        return True
    
    def encrypt_data(self, data: str) -> str:
        """데이터 암호화"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"데이터 암호화 오류: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """데이터 복호화"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"데이터 복호화 오류: {e}")
            return encrypted_data
    
    def generate_secure_hash(self, data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """보안 해시 생성"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # PBKDF2 스타일 해시 생성
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            data.encode(),
            salt.encode(),
            100000  # 반복 횟수
        )
        
        return {
            'hash': hash_obj.hex(),
            'salt': salt
        }
    
    def verify_secure_hash(self, data: str, stored_hash: str, salt: str) -> bool:
        """보안 해시 검증"""
        try:
            computed_hash = self.generate_secure_hash(data, salt)['hash']
            return hmac.compare_digest(computed_hash, stored_hash)
        except Exception as e:
            logger.error(f"해시 검증 오류: {e}")
            return False

# 전역 보안 관리자 인스턴스 (지연 초기화)
security_manager = None

def get_security_manager():
    """보안 관리자 인스턴스 반환 (지연 초기화)"""
    global security_manager
    if security_manager is None:
        security_manager = SecurityManager()
    return security_manager

def jwt_required(f):
    """JWT 토큰 필요 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'JWT 토큰이 필요합니다.'}), 401
        
        # Bearer 토큰 형식 확인
        if token.startswith('Bearer '):
            token = token[7:]
        
        # 토큰 검증
        payload = get_security_manager().verify_jwt_token(token)
        if not payload:
            return jsonify({'error': '유효하지 않은 JWT 토큰입니다.'}), 401
        
        # 사용자 정보를 g에 저장
        g.user_id = payload['user_id']
        g.user_role = payload['role']
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(endpoint: str = 'default'):
    """API 요청 제한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(g, 'user_id', None) or getattr(current_user, 'id', None)
            
            if not user_id:
                return jsonify({'error': '사용자 인증이 필요합니다.'}), 401
            
            # 요청 제한 확인
            if not get_security_manager().check_rate_limit(user_id, endpoint):
                return jsonify({
                    'error': '요청 제한에 도달했습니다. 잠시 후 다시 시도해주세요.',
                    'retry_after': 60
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """관리자 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_role = getattr(g, 'user_role', None) or getattr(current_user, 'role', None)
        
        if not user_role or user_role not in ['admin', 'super_admin']:
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@security_enhanced_bp.route('/api/security/auth/login', methods=['POST'])
@rate_limit('auth')
def secure_login():
    """보안 로그인"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '사용자명과 비밀번호가 필요합니다.'}), 400
        
        # 실제로는 데이터베이스에서 사용자 확인
        # 여기서는 더미 사용자로 테스트
        if username == 'admin' and password == 'admin123':
            user_id = 1
            role = 'admin'
        else:
            return jsonify({'error': '잘못된 사용자명 또는 비밀번호입니다.'}), 401
        
        # JWT 토큰 생성
        token = get_security_manager().generate_jwt_token(user_id, role)
        
        # 로그인 성공 기록
        logger.info(f"보안 로그인 성공: 사용자 {username}")
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'username': username,
                'role': role
            },
            'expires_in': 3600
        })
        
    except Exception as e:
        logger.error(f"보안 로그인 실패: {e}")
        return jsonify({'error': '로그인에 실패했습니다.'}), 500

@security_enhanced_bp.route('/api/security/auth/logout', methods=['POST'])
@jwt_required
def secure_logout():
    """보안 로그아웃"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # 토큰 무효화
        if get_security_manager().revoke_jwt_token(token):
            logger.info(f"보안 로그아웃 성공: 사용자 {g.user_id}")
            return jsonify({
                'success': True,
                'message': '로그아웃되었습니다.'
            })
        else:
            return jsonify({'error': '로그아웃에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"보안 로그아웃 실패: {e}")
        return jsonify({'error': '로그아웃에 실패했습니다.'}), 500

@security_enhanced_bp.route('/api/security/auth/refresh', methods=['POST'])
@jwt_required
def refresh_token():
    """토큰 갱신"""
    try:
        # 새 토큰 생성
        new_token = get_security_manager().generate_jwt_token(g.user_id, g.user_role)
        
        # 기존 토큰 무효화
        old_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        get_security_manager().revoke_jwt_token(old_token)
        
        return jsonify({
            'success': True,
            'token': new_token,
            'expires_in': 3600
        })
        
    except Exception as e:
        logger.error(f"토큰 갱신 실패: {e}")
        return jsonify({'error': '토큰 갱신에 실패했습니다.'}), 500

@security_enhanced_bp.route('/api/security/encrypt', methods=['POST'])
@jwt_required
@admin_required
def encrypt_data():
    """데이터 암호화"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        text = data.get('text')
        if not text:
            return jsonify({'error': '암호화할 텍스트가 필요합니다.'}), 400
        
        encrypted_text = get_security_manager().encrypt_data(text)
        
        return jsonify({
            'success': True,
            'encrypted_data': encrypted_text
        })
        
    except Exception as e:
        logger.error(f"데이터 암호화 실패: {e}")
        return jsonify({'error': '데이터 암호화에 실패했습니다.'}), 500

@security_enhanced_bp.route('/api/security/decrypt', methods=['POST'])
@jwt_required
@admin_required
def decrypt_data():
    """데이터 복호화"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        encrypted_text = data.get('encrypted_data')
        if not encrypted_text:
            return jsonify({'error': '복호화할 데이터가 필요합니다.'}), 400
        
        decrypted_text = get_security_manager().decrypt_data(encrypted_text)
        
        return jsonify({
            'success': True,
            'decrypted_data': decrypted_text
        })
        
    except Exception as e:
        logger.error(f"데이터 복호화 실패: {e}")
        return jsonify({'error': '데이터 복호화에 실패했습니다.'}), 500

@security_enhanced_bp.route('/api/security/hash', methods=['POST'])
@jwt_required
def generate_hash():
    """보안 해시 생성"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        text = data.get('text')
        if not text:
            return jsonify({'error': '해시할 텍스트가 필요합니다.'}), 400
        
        hash_result = get_security_manager().generate_secure_hash(text)
        
        return jsonify({
            'success': True,
            'hash': hash_result['hash'],
            'salt': hash_result['salt']
        })
        
    except Exception as e:
        logger.error(f"해시 생성 실패: {e}")
        return jsonify({'error': '해시 생성에 실패했습니다.'}), 500

@security_enhanced_bp.route('/api/security/verify-hash', methods=['POST'])
@jwt_required
def verify_hash():
    """해시 검증"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        text = data.get('text')
        stored_hash = data.get('hash')
        salt = data.get('salt')
        
        if not all([text, stored_hash, salt]):
            return jsonify({'error': '텍스트, 해시, 솔트가 모두 필요합니다.'}), 400
        
        is_valid = get_security_manager().verify_secure_hash(text, stored_hash, salt)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid
        })
        
    except Exception as e:
        logger.error(f"해시 검증 실패: {e}")
        return jsonify({'error': '해시 검증에 실패했습니다.'}), 500

@security_enhanced_bp.route('/api/security/status', methods=['GET'])
@jwt_required
@admin_required
def security_status():
    """보안 상태 확인"""
    try:
        # Redis 연결 상태
        redis_status = 'connected' if redis_available else 'disconnected'
        
        # 메모리 사용량 (Redis 대체 시)
        memory_usage = len(memory_store) if not redis_available else 0
        
        # 활성 토큰 수
        active_tokens = 0
        if redis_available:
            keys = redis_client.keys('jwt:*')
            active_tokens = len(keys) if isinstance(keys, list) else 0
        else:
            active_tokens = len([k for k in memory_store.keys() if k.startswith('jwt:')])
        
        return jsonify({
            'success': True,
            'security_status': {
                'redis_connection': redis_status,
                'memory_usage': memory_usage,
                'active_tokens': active_tokens,
                'encryption_enabled': True,
                'rate_limiting_enabled': True,
                'jwt_enabled': True
            }
        })
        
    except Exception as e:
        logger.error(f"보안 상태 확인 실패: {e}")
        return jsonify({'error': '보안 상태 확인에 실패했습니다.'}), 500

@security_enhanced_bp.route('/api/security/audit-log', methods=['GET'])
@jwt_required
@admin_required
def security_audit_log():
    """보안 감사 로그"""
    try:
        # 실제로는 데이터베이스에서 감사 로그를 가져옴
        audit_logs = [
            {
                'id': 1,
                'user_id': g.user_id,
                'action': 'login',
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            },
            {
                'id': 2,
                'user_id': g.user_id,
                'action': 'data_encryption',
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                'status': 'success'
            }
        ]
        
        return jsonify({
            'success': True,
            'audit_logs': audit_logs
        })
        
    except Exception as e:
        logger.error(f"보안 감사 로그 조회 실패: {e}")
        return jsonify({'error': '보안 감사 로그 조회에 실패했습니다.'}), 500 