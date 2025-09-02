"""
백엔드 설정 통합 관리
모든 백엔드 설정을 중앙에서 관리하고 최적화
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BackendConfig:
    """백엔드 설정 관리자"""
    
    def __init__(self):
        self.config = {}
        self.environment = os.getenv('FLASK_ENV', 'development')
        self.load_config()
    
    def load_config(self):
        """설정 로드"""
        # 기본 설정
        self.config = {
            'app': {
                'name': '멀티테넌시 관리 시스템',
                'version': '1.0.0',
                'debug': self.environment == 'development',
                'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-change-this'),
                'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key'),
                'timezone': 'Asia/Seoul'
            },
            'database': {
                'uri': os.getenv('DATABASE_URL', 'sqlite:///app.db'),
                'pool_size': int(os.getenv('DB_POOL_SIZE', '20')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '30')),
                'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
                'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
                'echo': self.environment == 'development'
            },
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', '6379')),
                'db': int(os.getenv('REDIS_DB', '0')),
                'password': os.getenv('REDIS_PASSWORD'),
                'decode_responses': True,
                'fallback_to_memory': True,  # Redis 실패 시 메모리 캐시로 대체
                'connection_timeout': int(os.getenv('REDIS_CONNECTION_TIMEOUT', '5')),
                'retry_on_timeout': True
            },
            'security': {
                'password_min_length': int(os.getenv('PASSWORD_MIN_LENGTH', '12')),
                'password_require_uppercase': True,
                'password_require_lowercase': True,
                'password_require_digits': True,
                'password_require_special_chars': True,
                'session_timeout_hours': int(os.getenv('SESSION_TIMEOUT_HOURS', '24')),
                'max_login_attempts': int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
                'lockout_duration_minutes': int(os.getenv('LOCKOUT_DURATION_MINUTES', '30')),
                'require_https': self.environment == 'production'
            },
            'api': {
                'rate_limit_requests': int(os.getenv('RATE_LIMIT_REQUESTS', '100')),
                'rate_limit_window_minutes': int(os.getenv('RATE_LIMIT_WINDOW_MINUTES', '15')),
                'max_request_size_mb': int(os.getenv('MAX_REQUEST_SIZE_MB', '16')),
                'cors_allowed_origins': os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(','),
                'cors_allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'cors_allowed_headers': ['Content-Type', 'Authorization', 'X-API-Key']
            },
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file_path': os.getenv('LOG_FILE_PATH', 'logs/app.log'),
                'max_file_size_mb': int(os.getenv('LOG_MAX_FILE_SIZE_MB', '100')),
                'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5'))
            },
            'monitoring': {
                'enabled': os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
                'metrics_interval_seconds': int(os.getenv('METRICS_INTERVAL_SECONDS', '60')),
                'health_check_interval_seconds': int(os.getenv('HEALTH_CHECK_INTERVAL_SECONDS', '300')),
                'alert_threshold_cpu_percent': int(os.getenv('ALERT_THRESHOLD_CPU_PERCENT', '80')),
                'alert_threshold_memory_percent': int(os.getenv('ALERT_THRESHOLD_MEMORY_PERCENT', '80'))
            },
            'cache': {
                'default_timeout': int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300')),
                'key_prefix': os.getenv('CACHE_KEY_PREFIX', 'app'),
                'type': os.getenv('CACHE_TYPE', 'redis')
            },
            'websocket': {
                'enabled': os.getenv('WEBSOCKET_ENABLED', 'true').lower() == 'true',
                'cors_allowed_origins': os.getenv('WS_CORS_ALLOWED_ORIGINS', '*').split(','),
                'ping_timeout': int(os.getenv('WS_PING_TIMEOUT', '60')),
                'ping_interval': int(os.getenv('WS_PING_INTERVAL', '25'))
            },
            'email': {
                'smtp_host': os.getenv('SMTP_HOST', 'localhost'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'smtp_username': os.getenv('SMTP_USERNAME'),
                'smtp_password': os.getenv('SMTP_PASSWORD'),
                'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
                'from_email': os.getenv('FROM_EMAIL', 'noreply@example.com'),
                'from_name': os.getenv('FROM_NAME', '시스템 관리자')
            },
            'file_upload': {
                'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', '10')),
                'allowed_extensions': os.getenv('ALLOWED_FILE_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx').split(','),
                'upload_folder': os.getenv('UPLOAD_FOLDER', 'uploads'),
                'temp_folder': os.getenv('TEMP_FOLDER', 'temp')
            },
            'ai': {
                'enabled': os.getenv('AI_ENABLED', 'false').lower() == 'true',
                'model_path': os.getenv('AI_MODEL_PATH', 'models'),
                'max_concurrent_requests': int(os.getenv('AI_MAX_CONCURRENT_REQUESTS', '5')),
                'timeout_seconds': int(os.getenv('AI_TIMEOUT_SECONDS', '30'))
            },
            'backup': {
                'enabled': os.getenv('BACKUP_ENABLED', 'true').lower() == 'true',
                'schedule': os.getenv('BACKUP_SCHEDULE', '0 2 * * *'),  # 매일 새벽 2시
                'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
                'backup_folder': os.getenv('BACKUP_FOLDER', 'backups')
            }
        }
        
        # 환경별 설정 오버라이드
        self._load_environment_config()
        
        logger.info(f"백엔드 설정 로드 완료: {self.environment}")
    
    def _load_environment_config(self):
        """환경별 설정 로드"""
        if self.environment == 'production':
            self.config.update({
                'app': {
                    **self.config['app'],
                    'debug': False,
                    'secret_key': os.getenv('SECRET_KEY'),
                    'jwt_secret_key': os.getenv('JWT_SECRET_KEY')
                },
                'security': {
                    **self.config['security'],
                    'require_https': True,
                    'password_min_length': 16
                },
                'logging': {
                    **self.config['logging'],
                    'level': 'WARNING'
                }
            })
        
        elif self.environment == 'testing':
            self.config.update({
                'database': {
                    **self.config['database'],
                    'uri': 'sqlite:///:memory:'
                },
                'cache': {
                    **self.config['cache'],
                    'type': 'simple'
                },
                'websocket': {
                    **self.config['websocket'],
                    'enabled': False
                }
            })
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 조회"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """설정 값 설정"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_database_config(self) -> Dict[str, Any]:
        """데이터베이스 설정 조회"""
        return self.config['database']
    
    def get_security_config(self) -> Dict[str, Any]:
        """보안 설정 조회"""
        return self.config['security']
    
    def get_api_config(self) -> Dict[str, Any]:
        """API 설정 조회"""
        return self.config['api']
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """모니터링 설정 조회"""
        return self.config['monitoring']
    
    def validate_config(self) -> Dict[str, Any]:
        """설정 유효성 검사"""
        errors = []
        warnings = []
        
        # 필수 설정 검사
        required_settings = [
            ('app.secret_key', 'SECRET_KEY'),
            ('app.jwt_secret_key', 'JWT_SECRET_KEY'),
            ('database.uri', 'DATABASE_URL')
        ]
        
        for config_key, env_key in required_settings:
            value = self.get(config_key)
            if not value or value.startswith('your-'):
                errors.append(f"필수 설정 누락: {env_key}")
        
        # 보안 설정 검사
        if self.environment == 'production':
            if not self.get('security.require_https'):
                warnings.append("프로덕션 환경에서 HTTPS가 비활성화되어 있습니다.")
            
            if self.get('app.debug'):
                errors.append("프로덕션 환경에서 디버그 모드가 활성화되어 있습니다.")
        
        # 데이터베이스 설정 검사
        db_uri = self.get('database.uri')
        if db_uri and 'sqlite' in db_uri and self.environment == 'production':
            warnings.append("프로덕션 환경에서 SQLite를 사용하고 있습니다.")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'environment': self.environment,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """설정 요약 정보"""
        return {
            'environment': self.environment,
            'app_name': self.get('app.name'),
            'version': self.get('app.version'),
            'debug': self.get('app.debug'),
            'database_type': 'sqlite' if 'sqlite' in self.get('database.uri') else 'postgresql',
            'redis_enabled': bool(self.get('redis.host')),
            'websocket_enabled': self.get('websocket.enabled'),
            'monitoring_enabled': self.get('monitoring.enabled'),
            'ai_enabled': self.get('ai.enabled'),
            'backup_enabled': self.get('backup.enabled'),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def export_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """설정 내보내기"""
        config_copy = self.config.copy()
        
        if not include_secrets:
            # 민감한 정보 제거
            sensitive_keys = [
                'app.secret_key',
                'app.jwt_secret_key',
                'redis.password',
                'email.smtp_password'
            ]
            
            for key in sensitive_keys:
                keys = key.split('.')
                config = config_copy
                for k in keys[:-1]:
                    config = config.get(k, {})
                if keys[-1] in config:
                    config[keys[-1]] = '***REDACTED***'
        
        return {
            'environment': self.environment,
            'config': config_copy,
            'exported_at': datetime.utcnow().isoformat()
        }


# 전역 백엔드 설정 인스턴스
backend_config = BackendConfig()


def get_backend_config() -> BackendConfig:
    """백엔드 설정 인스턴스 조회"""
    return backend_config


def validate_backend_setup() -> Dict[str, Any]:
    """백엔드 설정 검증"""
    validation_result = backend_config.validate_config()
    
    if not validation_result['valid']:
        logger.error("백엔드 설정 검증 실패:")
        for error in validation_result['errors']:
            logger.error(f"  - {error}")
    
    if validation_result['warnings']:
        logger.warning("백엔드 설정 경고:")
        for warning in validation_result['warnings']:
            logger.warning(f"  - {warning}")
    
    return validation_result


def get_optimized_config() -> Dict[str, Any]:
    """최적화된 설정 조회"""
    config = backend_config.config.copy()
    
    # 성능 최적화 설정
    if backend_config.environment == 'production':
        config['database']['pool_size'] = max(20, config['database']['pool_size'])
        config['database']['max_overflow'] = max(30, config['database']['max_overflow'])
        config['cache']['default_timeout'] = max(600, config['cache']['default_timeout'])
    
    return config 