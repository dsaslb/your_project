"""
환경변수 관리 시스템
보안 환경변수 관리, 검증, 암호화 기능 제공
"""

import os
import json
import logging
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import string

logger = logging.getLogger(__name__)

class EnvironmentManager:
    """환경변수 관리자"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 환경별 설정 파일 경로
        self.env_files = {
            'development': self.config_dir / '.env.development',
            'staging': self.config_dir / '.env.staging',
            'production': self.config_dir / '.env.production',
            'testing': self.config_dir / '.env.testing'
        }
        
        # 암호화 키 파일
        self.key_file = self.config_dir / '.env.key'
        
        # 환경변수 스키마 정의
        self.env_schema = {
            'required': {
                'DATABASE_URL': {
                    'type': 'string',
                    'description': '데이터베이스 연결 URL',
                    'pattern': r'^(postgresql|mysql|sqlite)://.*$'
                },
                'SECRET_KEY': {
                    'type': 'string',
                    'description': 'Flask 시크릿 키',
                    'min_length': 32
                },
                'FLASK_ENV': {
                    'type': 'string',
                    'description': 'Flask 환경',
                    'enum': ['development', 'production', 'testing']
                }
            },
            'optional': {
                'REDIS_URL': {
                    'type': 'string',
                    'description': 'Redis 연결 URL',
                    'default': 'redis://localhost:6379/0'
                },
                'LOG_LEVEL': {
                    'type': 'string',
                    'description': '로그 레벨',
                    'enum': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    'default': 'INFO'
                },
                'DEBUG': {
                    'type': 'boolean',
                    'description': '디버그 모드',
                    'default': False
                },
                'PORT': {
                    'type': 'integer',
                    'description': '서버 포트',
                    'default': 5000,
                    'min': 1,
                    'max': 65535
                },
                'HOST': {
                    'type': 'string',
                    'description': '서버 호스트',
                    'default': '0.0.0.0'
                },
                'CORS_ORIGINS': {
                    'type': 'list',
                    'description': 'CORS 허용 도메인 목록',
                    'default': ['http://localhost:3000']
                },
                'JWT_SECRET_KEY': {
                    'type': 'string',
                    'description': 'JWT 시크릿 키',
                    'min_length': 32
                },
                'JWT_ACCESS_TOKEN_EXPIRES': {
                    'type': 'integer',
                    'description': 'JWT 액세스 토큰 만료 시간(분)',
                    'default': 30,
                    'min': 1,
                    'max': 1440
                },
                'JWT_REFRESH_TOKEN_EXPIRES': {
                    'type': 'integer',
                    'description': 'JWT 리프레시 토큰 만료 시간(일)',
                    'default': 30,
                    'min': 1,
                    'max': 365
                },
                'MAIL_SERVER': {
                    'type': 'string',
                    'description': '메일 서버 주소'
                },
                'MAIL_PORT': {
                    'type': 'integer',
                    'description': '메일 서버 포트',
                    'default': 587
                },
                'MAIL_USE_TLS': {
                    'type': 'boolean',
                    'description': 'TLS 사용 여부',
                    'default': True
                },
                'MAIL_USERNAME': {
                    'type': 'string',
                    'description': '메일 계정'
                },
                'MAIL_PASSWORD': {
                    'type': 'string',
                    'description': '메일 비밀번호',
                    'sensitive': True
                },
                'SLACK_WEBHOOK_URL': {
                    'type': 'string',
                    'description': 'Slack 웹훅 URL',
                    'sensitive': True
                },
                'TELEGRAM_BOT_TOKEN': {
                    'type': 'string',
                    'description': 'Telegram 봇 토큰',
                    'sensitive': True
                },
                'PUSHOVER_API_TOKEN': {
                    'type': 'string',
                    'description': 'Pushover API 토큰',
                    'sensitive': True
                },
                'AI_MODEL_PATH': {
                    'type': 'string',
                    'description': 'AI 모델 저장 경로',
                    'default': 'ai/models'
                },
                'WEBSOCKET_CORS_ORIGINS': {
                    'type': 'list',
                    'description': 'WebSocket CORS 허용 도메인',
                    'default': ['http://localhost:3000']
                },
                'MAX_UPLOAD_SIZE': {
                    'type': 'integer',
                    'description': '최대 업로드 파일 크기(MB)',
                    'default': 16,
                    'min': 1,
                    'max': 100
                },
                'SESSION_COOKIE_SECURE': {
                    'type': 'boolean',
                    'description': '세션 쿠키 보안 설정',
                    'default': False
                },
                'SESSION_COOKIE_HTTPONLY': {
                    'type': 'boolean',
                    'description': '세션 쿠키 HTTPOnly 설정',
                    'default': True
                },
                'SESSION_COOKIE_SAMESITE': {
                    'type': 'string',
                    'description': '세션 쿠키 SameSite 설정',
                    'enum': ['Lax', 'Strict', 'None'],
                    'default': 'Lax'
                }
            }
        }
        
        # 암호화 키 초기화
        self._init_encryption_key()
    
    def _init_encryption_key(self):
        """암호화 키 초기화"""
        if not self.key_file.exists():
            # 새로운 키 생성
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            logger.info("새로운 암호화 키 생성됨")
        else:
            # 기존 키 로드
            with open(self.key_file, 'rb') as f:
                key = f.read()
        
        self.cipher = Fernet(key)
    
    def _encrypt_value(self, value: str) -> str:
        """값 암호화"""
        if not value:
            return value
        encrypted = self.cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """값 복호화"""
        if not encrypted_value:
            return encrypted_value
        try:
            encrypted = base64.b64decode(encrypted_value.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.warning(f"복호화 실패: {e}")
            return encrypted_value
    
    def _validate_value(self, key: str, value: Any, schema: Dict) -> bool:
        """값 검증"""
        try:
            # 타입 검증
            if schema.get('type') == 'string':
                if not isinstance(value, str):
                    return False
                if 'min_length' in schema and len(value) < schema['min_length']:
                    return False
                if 'pattern' in schema:
                    import re
                    if not re.match(schema['pattern'], value):
                        return False
                if 'enum' in schema and value not in schema['enum']:
                    return False
                    
            elif schema.get('type') == 'integer':
                try:
                    int_value = int(value)
                    if 'min' in schema and int_value < schema['min']:
                        return False
                    if 'max' in schema and int_value > schema['max']:
                        return False
                except (ValueError, TypeError):
                    return False
                    
            elif schema.get('type') == 'boolean':
                if value not in ['true', 'false', True, False, '1', '0', 1, 0]:
                    return False
                    
            elif schema.get('type') == 'list':
                if not isinstance(value, (list, str)):
                    return False
                if isinstance(value, str):
                    try:
                        json.loads(value)
                    except json.JSONDecodeError:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"값 검증 오류 ({key}): {e}")
            return False
    
    def _parse_value(self, value: str, schema: Dict) -> Any:
        """값 파싱"""
        if schema.get('type') == 'integer':
            return int(value)
        elif schema.get('type') == 'boolean':
            if value.lower() in ['true', '1']:
                return True
            return False
        elif schema.get('type') == 'list':
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value.split(',')
            return value
        return value
    
    def create_env_file(self, environment: str, values: Dict[str, Any] = None) -> bool:
        """환경별 .env 파일 생성"""
        try:
            env_file = self.env_files.get(environment)
            if not env_file:
                logger.error(f"지원하지 않는 환경: {environment}")
                return False
            
            # 기본값 설정
            env_vars = {}
            
            # 필수 환경변수 설정
            for key, schema in self.env_schema['required'].items():
                if values and key in values:
                    env_vars[key] = values[key]
                else:
                    # 기본값 생성
                    if key == 'SECRET_KEY':
                        env_vars[key] = self._generate_secret_key()
                    elif key == 'DATABASE_URL':
                        env_vars[key] = f"sqlite:///instance/{environment}.db"
                    elif key == 'FLASK_ENV':
                        env_vars[key] = environment
                    else:
                        logger.warning(f"필수 환경변수 {key}의 값이 제공되지 않았습니다.")
                        return False
            
            # 선택적 환경변수 설정
            for key, schema in self.env_schema['optional'].items():
                if values and key in values:
                    env_vars[key] = values[key]
                elif 'default' in schema:
                    env_vars[key] = schema['default']
            
            # 파일 작성
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(f"# {environment.upper()} 환경 설정\n")
                f.write(f"# 생성일: {self._get_current_timestamp()}\n\n")
                
                for key, value in env_vars.items():
                    # 값 검증
                    schema = self.env_schema['required'].get(key) or self.env_schema['optional'].get(key)
                    if schema and not self._validate_value(key, value, schema):
                        logger.error(f"환경변수 {key}의 값이 유효하지 않습니다.")
                        return False
                    
                    # 민감한 정보 암호화
                    if schema and schema.get('sensitive'):
                        encrypted_value = self._encrypt_value(str(value))
                        f.write(f"{key}={encrypted_value}  # 암호화됨\n")
                    else:
                        if isinstance(value, (list, dict)):
                            f.write(f"{key}={json.dumps(value)}\n")
                        else:
                            f.write(f"{key}={value}\n")
            
            logger.info(f"{environment} 환경 설정 파일 생성 완료: {env_file}")
            return True
            
        except Exception as e:
            logger.error(f"환경 설정 파일 생성 실패: {e}")
            return False
    
    def load_env_file(self, environment: str) -> Dict[str, Any]:
        """환경별 .env 파일 로드"""
        try:
            env_file = self.env_files.get(environment)
            if not env_file or not env_file.exists():
                logger.error(f"환경 설정 파일이 없습니다: {environment}")
                return {}
            
            env_vars = {}
            
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 주석 제거
                        if '#' in value:
                            value = value.split('#')[0].strip()
                        
                        # 암호화된 값 복호화
                        if value.startswith('gAAAAA'):  # Fernet 암호화된 값의 특징
                            value = self._decrypt_value(value)
                        
                        # 값 파싱
                        schema = self.env_schema['required'].get(key) or self.env_schema['optional'].get(key)
                        if schema:
                            parsed_value = self._parse_value(value, schema)
                            env_vars[key] = parsed_value
                        else:
                            env_vars[key] = value
            
            logger.info(f"{environment} 환경 설정 로드 완료: {len(env_vars)}개 변수")
            return env_vars
            
        except Exception as e:
            logger.error(f"환경 설정 파일 로드 실패: {e}")
            return {}
    
    def update_env_file(self, environment: str, updates: Dict[str, Any]) -> bool:
        """환경별 .env 파일 업데이트"""
        try:
            # 기존 설정 로드
            env_vars = self.load_env_file(environment)
            
            # 업데이트 적용
            env_vars.update(updates)
            
            # 파일 재생성
            return self.create_env_file(environment, env_vars)
            
        except Exception as e:
            logger.error(f"환경 설정 파일 업데이트 실패: {e}")
            return False
    
    def validate_env_file(self, environment: str) -> Dict[str, Any]:
        """환경별 .env 파일 검증"""
        try:
            env_vars = self.load_env_file(environment)
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'missing_required': [],
                'invalid_values': []
            }
            
            # 필수 환경변수 검증
            for key, schema in self.env_schema['required'].items():
                if key not in env_vars:
                    validation_result['missing_required'].append(key)
                    validation_result['valid'] = False
                else:
                    if not self._validate_value(key, env_vars[key], schema):
                        validation_result['invalid_values'].append(key)
                        validation_result['valid'] = False
            
            # 선택적 환경변수 검증
            for key, schema in self.env_schema['optional'].items():
                if key in env_vars:
                    if not self._validate_value(key, env_vars[key], schema):
                        validation_result['invalid_values'].append(key)
                        validation_result['warnings'].append(f"선택적 환경변수 {key}의 값이 유효하지 않습니다.")
            
            # 보안 검증
            if environment == 'production':
                if env_vars.get('DEBUG', False):
                    validation_result['warnings'].append("프로덕션 환경에서 DEBUG가 활성화되어 있습니다.")
                if not env_vars.get('SESSION_COOKIE_SECURE', False):
                    validation_result['warnings'].append("프로덕션 환경에서 SESSION_COOKIE_SECURE를 활성화하는 것을 권장합니다.")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"환경 설정 파일 검증 실패: {e}")
            return {'valid': False, 'errors': [str(e)]}
    
    def _generate_secret_key(self, length: int = 64) -> str:
        """시크릿 키 생성"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_env_schema(self) -> Dict[str, Any]:
        """환경변수 스키마 반환"""
        return self.env_schema.copy()
    
    def list_environments(self) -> List[str]:
        """사용 가능한 환경 목록 반환"""
        return list(self.env_files.keys())
    
    def environment_exists(self, environment: str) -> bool:
        """환경 설정 파일 존재 여부 확인"""
        env_file = self.env_files.get(environment)
        return env_file and env_file.exists()

# 전역 인스턴스
env_manager = EnvironmentManager() 