"""
보안 설정 관리 시스템
보안 정책, 암호화, 인증, 권한 관리 설정
"""

import os
import json
import logging
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class SecurityConfig:
    """보안 설정 관리자"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 보안 설정 파일
        self.security_file = self.config_dir / 'security_config.json'
        self.policy_file = self.config_dir / 'security_policy.json'
        self.audit_file = self.config_dir / 'security_audit.log'
        
        # 기본 보안 정책
        self.default_policy = {
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special_chars': True,
                'max_age_days': 90,
                'prevent_reuse_count': 5
            },
            'session_policy': {
                'max_session_duration_hours': 24,
                'inactive_timeout_minutes': 30,
                'max_concurrent_sessions': 3,
                'require_secure_cookies': True,
                'require_http_only': True,
                'same_site_policy': 'Lax'
            },
            'authentication_policy': {
                'max_login_attempts': 5,
                'lockout_duration_minutes': 30,
                'require_mfa': False,
                'mfa_methods': ['totp', 'email', 'sms'],
                'remember_me_days': 30
            },
            'api_security': {
                'rate_limit_requests': 100,
                'rate_limit_window_minutes': 15,
                'require_api_key': True,
                'api_key_expiry_days': 365,
                'max_request_size_mb': 16
            },
            'data_protection': {
                'encrypt_sensitive_data': True,
                'encryption_algorithm': 'AES-256-GCM',
                'key_rotation_days': 90,
                'data_retention_days': 2555,  # 7년
                'secure_deletion': True
            },
            'network_security': {
                'require_https': True,
                'hsts_max_age_seconds': 31536000,  # 1년
                'cors_allowed_origins': ['http://localhost:3000'],
                'cors_allowed_methods': ['GET', 'POST', 'PUT', 'DELETE'],
                'cors_allowed_headers': ['Content-Type', 'Authorization'],
                'block_suspicious_ips': True
            },
            'logging_policy': {
                'log_security_events': True,
                'log_user_actions': True,
                'log_api_calls': True,
                'log_retention_days': 90,
                'log_encryption': True
            }
        }
        
        # 보안 설정 초기화
        self._init_security_config()
    
    def _init_security_config(self):
        """보안 설정 초기화"""
        if not self.security_file.exists():
            self._create_default_security_config()
        
        if not self.policy_file.exists():
            self._create_default_policy()
    
    def _create_default_security_config(self):
        """기본 보안 설정 생성"""
        default_config = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'encryption_keys': {
                'current': self._generate_encryption_key(),
                'previous': None
            },
            'jwt_settings': {
                'algorithm': 'HS256',
                'access_token_expiry_minutes': 30,
                'refresh_token_expiry_days': 30,
                'issuer': 'your_program',
                'audience': 'your_program_users'
            },
            'session_settings': {
                'session_type': 'server-side',
                'session_store': 'redis',
                'session_prefix': 'session:',
                'cleanup_interval_minutes': 60
            },
            'rate_limiting': {
                'enabled': True,
                'storage': 'redis',
                'default_limit': 100,
                'default_window': 900  # 15분
            },
            'audit_settings': {
                'enabled': True,
                'log_level': 'INFO',
                'include_sensitive_data': False,
                'max_log_size_mb': 100
            }
        }
        
        with open(self.security_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        logger.info("기본 보안 설정 생성됨")
    
    def _create_default_policy(self):
        """기본 보안 정책 생성"""
        with open(self.policy_file, 'w', encoding='utf-8') as f:
            json.dump(self.default_policy, f, indent=2, ensure_ascii=False)
        
        logger.info("기본 보안 정책 생성됨")
    
    def _generate_encryption_key(self) -> str:
        """암호화 키 생성"""
        return Fernet.generate_key().decode()
    
    def get_security_config(self) -> Dict[str, Any]:
        """보안 설정 조회"""
        try:
            with open(self.security_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"보안 설정 로드 실패: {e}")
            return {}
    
    def get_security_policy(self) -> Dict[str, Any]:
        """보안 정책 조회"""
        try:
            with open(self.policy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"보안 정책 로드 실패: {e}")
            return self.default_policy
    
    def update_security_config(self, updates: Dict[str, Any]) -> bool:
        """보안 설정 업데이트"""
        try:
            config = self.get_security_config()
            config.update(updates)
            config['last_updated'] = datetime.now().isoformat()
            
            with open(self.security_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("보안 설정 업데이트됨")
            return True
            
        except Exception as e:
            logger.error(f"보안 설정 업데이트 실패: {e}")
            return False
    
    def update_security_policy(self, updates: Dict[str, Any]) -> bool:
        """보안 정책 업데이트"""
        try:
            policy = self.get_security_policy()
            
            # 중첩된 딕셔너리 업데이트
            for key, value in updates.items():
                if key in policy and isinstance(policy[key], dict) and isinstance(value, dict):
                    policy[key].update(value)
                else:
                    policy[key] = value
            
            with open(self.policy_file, 'w', encoding='utf-8') as f:
                json.dump(policy, f, indent=2, ensure_ascii=False)
            
            logger.info("보안 정책 업데이트됨")
            return True
            
        except Exception as e:
            logger.error(f"보안 정책 업데이트 실패: {e}")
            return False
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """비밀번호 정책 검증"""
        policy = self.get_security_policy()['password_policy']
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 길이 검증
        if len(password) < policy['min_length']:
            result['errors'].append(f"비밀번호는 최소 {policy['min_length']}자 이상이어야 합니다.")
            result['valid'] = False
        
        # 대문자 검증
        if policy['require_uppercase'] and not any(c.isupper() for c in password):
            result['errors'].append("비밀번호에 대문자가 포함되어야 합니다.")
            result['valid'] = False
        
        # 소문자 검증
        if policy['require_lowercase'] and not any(c.islower() for c in password):
            result['errors'].append("비밀번호에 소문자가 포함되어야 합니다.")
            result['valid'] = False
        
        # 숫자 검증
        if policy['require_digits'] and not any(c.isdigit() for c in password):
            result['errors'].append("비밀번호에 숫자가 포함되어야 합니다.")
            result['valid'] = False
        
        # 특수문자 검증
        if policy['require_special_chars'] and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            result['errors'].append("비밀번호에 특수문자가 포함되어야 합니다.")
            result['valid'] = False
        
        # 보안 강도 검증
        strength = self._calculate_password_strength(password)
        if strength < 3:
            result['warnings'].append("비밀번호 강도가 낮습니다. 더 복잡한 비밀번호를 사용하세요.")
        
        return result
    
    def _calculate_password_strength(self, password: str) -> int:
        """비밀번호 강도 계산 (1-5)"""
        score = 0
        
        # 길이 점수
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # 문자 종류 점수
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 1
        
        # 중복 문자 감점
        if len(set(password)) < len(password) * 0.8:
            score = max(1, score - 1)
        
        return min(5, score)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """보안 토큰 생성"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해시"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        try:
            salt, hash_hex = hashed.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False
    
    def generate_jwt_token(self, payload: Dict[str, Any], token_type: str = 'access') -> str:
        """JWT 토큰 생성"""
        config = self.get_security_config()
        jwt_settings = config['jwt_settings']
        
        # 토큰 타입별 만료 시간 설정
        if token_type == 'access':
            expiry_minutes = jwt_settings['access_token_expiry_minutes']
            exp = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        else:  # refresh
            expiry_days = jwt_settings['refresh_token_expiry_days']
            exp = datetime.utcnow() + timedelta(days=expiry_days)
        
        # 페이로드 구성
        token_payload = {
            **payload,
            'exp': exp,
            'iat': datetime.utcnow(),
            'iss': jwt_settings['issuer'],
            'aud': jwt_settings['audience'],
            'type': token_type
        }
        
        # 환경변수에서 시크릿 키 가져오기
        secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
        
        return jwt.encode(token_payload, secret_key, algorithm=jwt_settings['algorithm'])
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """JWT 토큰 검증"""
        try:
            config = self.get_security_config()
            jwt_settings = config['jwt_settings']
            secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
            
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=[jwt_settings['algorithm']],
                issuer=jwt_settings['issuer'],
                audience=jwt_settings['audience']
            )
            
            return {'valid': True, 'payload': payload}
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': '토큰이 만료되었습니다.'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': f'유효하지 않은 토큰: {str(e)}'}
        except Exception as e:
            return {'valid': False, 'error': f'토큰 검증 실패: {str(e)}'}
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], user_id: Optional[str] = None):
        """보안 이벤트 로깅"""
        try:
            audit_config = self.get_security_config()['audit_settings']
            
            if not audit_config['enabled']:
                return
            
            event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'user_id': user_id,
                'ip_address': self._get_client_ip(),
                'user_agent': self._get_user_agent(),
                'details': details
            }
            
            # 민감한 데이터 필터링
            if not audit_config['include_sensitive_data']:
                event['details'] = self._filter_sensitive_data(event['details'])
            
            # 로그 파일에 기록
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
            
            logger.info(f"보안 이벤트 로깅: {event_type}")
            
        except Exception as e:
            logger.error(f"보안 이벤트 로깅 실패: {e}")
    
    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """민감한 데이터 필터링"""
        sensitive_keys = ['password', 'token', 'secret', 'key', 'credential']
        filtered_data = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered_data[key] = '***REDACTED***'
            elif isinstance(value, dict):
                filtered_data[key] = self._filter_sensitive_data(value)
            else:
                filtered_data[key] = value
        
        return filtered_data
    
    def _get_client_ip(self) -> str:
        """클라이언트 IP 주소 가져오기"""
        # Flask request context에서 IP 가져오기
        try:
            from flask import request
            return request.remote_addr
        except:
            return 'unknown'
    
    def _get_user_agent(self) -> str:
        """사용자 에이전트 가져오기"""
        try:
            from flask import request
            return request.headers.get('User-Agent', 'unknown')
        except:
            return 'unknown'
    
    def get_security_report(self) -> Dict[str, Any]:
        """보안 상태 리포트 생성"""
        try:
            config = self.get_security_config()
            policy = self.get_security_policy()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'config_version': config.get('version', 'unknown'),
                'last_updated': config.get('last_updated', 'unknown'),
                'security_score': self._calculate_security_score(config, policy),
                'recommendations': self._generate_security_recommendations(config, policy),
                'policy_compliance': self._check_policy_compliance(config, policy)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"보안 리포트 생성 실패: {e}")
            return {'error': str(e)}
    
    def _calculate_security_score(self, config: Dict, policy: Dict) -> int:
        """보안 점수 계산 (0-100)"""
        score = 0
        
        # JWT 설정 점수
        jwt_settings = config.get('jwt_settings', {})
        if jwt_settings.get('algorithm') == 'HS256':
            score += 10
        if jwt_settings.get('access_token_expiry_minutes', 0) <= 30:
            score += 10
        
        # 세션 설정 점수
        session_settings = config.get('session_settings', {})
        if session_settings.get('session_type') == 'server-side':
            score += 15
        
        # 비밀번호 정책 점수
        password_policy = policy.get('password_policy', {})
        if password_policy.get('min_length', 0) >= 12:
            score += 15
        if password_policy.get('require_special_chars', False):
            score += 10
        
        # 네트워크 보안 점수
        network_security = policy.get('network_security', {})
        if network_security.get('require_https', False):
            score += 20
        
        # 감사 로깅 점수
        audit_settings = config.get('audit_settings', {})
        if audit_settings.get('enabled', False):
            score += 10
        
        return min(100, score)
    
    def _generate_security_recommendations(self, config: Dict, policy: Dict) -> List[str]:
        """보안 권장사항 생성"""
        recommendations = []
        
        # JWT 권장사항
        jwt_settings = config.get('jwt_settings', {})
        if jwt_settings.get('access_token_expiry_minutes', 0) > 30:
            recommendations.append("액세스 토큰 만료 시간을 30분 이하로 설정하세요.")
        
        # 비밀번호 정책 권장사항
        password_policy = policy.get('password_policy', {})
        if password_policy.get('min_length', 0) < 12:
            recommendations.append("비밀번호 최소 길이를 12자 이상으로 설정하세요.")
        
        # 네트워크 보안 권장사항
        network_security = policy.get('network_security', {})
        if not network_security.get('require_https', False):
            recommendations.append("프로덕션 환경에서 HTTPS를 강제하세요.")
        
        return recommendations
    
    def _check_policy_compliance(self, config: Dict, policy: Dict) -> Dict[str, bool]:
        """정책 준수 상태 확인"""
        compliance = {}
        
        # 비밀번호 정책 준수
        password_policy = policy.get('password_policy', {})
        compliance['password_policy'] = (
            password_policy.get('min_length', 0) >= 8 and
            password_policy.get('require_uppercase', False) and
            password_policy.get('require_digits', False)
        )
        
        # 세션 정책 준수
        session_policy = policy.get('session_policy', {})
        compliance['session_policy'] = (
            session_policy.get('require_secure_cookies', False) and
            session_policy.get('require_http_only', False)
        )
        
        # 인증 정책 준수
        auth_policy = policy.get('authentication_policy', {})
        compliance['authentication_policy'] = (
            auth_policy.get('max_login_attempts', 0) <= 5
        )
        
        return compliance

# 전역 인스턴스
security_config = SecurityConfig() 