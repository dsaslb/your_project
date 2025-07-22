"""
성능 최적화 설정
캐시, 데이터베이스, API 최적화 설정
"""

import os
from typing import Dict, Any

class PerformanceConfig:
    """성능 최적화 기본 설정"""
    
    # 캐시 설정
    CACHE_ENABLED = True
    CACHE_TTL = 3600  # 1시간
    CACHE_MAX_SIZE = 100 * 1024 * 1024  # 100MB
    CACHE_COMPRESSION_ENABLED = True
    CACHE_COMPRESSION_THRESHOLD = 1024  # 1KB 이상 압축
    
    # Redis 설정
    REDIS_POOL_SIZE = 10
    REDIS_MAX_CONNECTIONS = 50
    REDIS_SOCKET_TIMEOUT = 5
    REDIS_SOCKET_CONNECT_TIMEOUT = 5
    REDIS_RETRY_ON_TIMEOUT = True
    
    # 데이터베이스 설정
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 30
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = 3600
    DB_ECHO = False
    DB_ECHO_POOL = False
    
    # 쿼리 최적화 설정
    QUERY_TIMEOUT = 30
    QUERY_MAX_RESULTS = 1000
    QUERY_BATCH_SIZE = 100
    QUERY_PAGE_SIZE = 20
    
    # API 최적화 설정
    API_CACHE_ENABLED = True
    API_CACHE_TTL = 1800  # 30분
    API_COMPRESSION_ENABLED = True
    API_COMPRESSION_THRESHOLD = 1024
    API_RATE_LIMIT_ENABLED = True
    API_RATE_LIMIT_DEFAULT = "100 per minute"
    
    # 응답 최적화 설정
    RESPONSE_COMPRESSION_ENABLED = True
    RESPONSE_COMPRESSION_THRESHOLD = 1024
    RESPONSE_STREAMING_ENABLED = True
    RESPONSE_CHUNK_SIZE = 8192
    
    # 모니터링 설정
    MONITORING_ENABLED = True
    MONITORING_INTERVAL = 60  # 1분
    METRICS_RETENTION_HOURS = 24
    ALERTING_ENABLED = True
    
    # 성능 임계값
    PERFORMANCE_THRESHOLDS = {
        'cpu_usage': 80.0,
        'memory_usage': 85.0,
        'disk_usage': 90.0,
        'response_time': 2.0,
        'error_rate': 5.0,
        'cache_hit_rate': 80.0
    }
    
    # 로드 밸런싱 설정
    LOAD_BALANCING_ENABLED = True
    LOAD_BALANCING_ALGORITHM = "round_robin"
    HEALTH_CHECK_INTERVAL = 30
    HEALTH_CHECK_TIMEOUT = 5
    MAX_FAILURES = 3
    
    # 자동 스케일링 설정
    AUTO_SCALING_ENABLED = True
    AUTO_SCALING_MIN_INSTANCES = 2
    AUTO_SCALING_MAX_INSTANCES = 10
    AUTO_SCALING_CPU_THRESHOLD = 80
    AUTO_SCALING_MEMORY_THRESHOLD = 85
    AUTO_SCALING_SCALE_UP_COOLDOWN = 300
    AUTO_SCALING_SCALE_DOWN_COOLDOWN = 600

class DevelopmentPerformanceConfig(PerformanceConfig):
    """개발 환경 성능 설정"""
    
    # 개발 환경에서는 캐시 비활성화
    CACHE_ENABLED = False
    API_CACHE_ENABLED = False
    
    # 개발 환경에서는 모니터링 간격 단축
    MONITORING_INTERVAL = 30
    
    # 개발 환경에서는 성능 임계값 완화
    PERFORMANCE_THRESHOLDS = {
        'cpu_usage': 90.0,
        'memory_usage': 90.0,
        'disk_usage': 95.0,
        'response_time': 5.0,
        'error_rate': 10.0,
        'cache_hit_rate': 50.0
    }
    
    # 개발 환경에서는 자동 스케일링 비활성화
    AUTO_SCALING_ENABLED = False

class StagingPerformanceConfig(PerformanceConfig):
    """스테이징 환경 성능 설정"""
    
    # 스테이징 환경에서는 캐시 활성화
    CACHE_ENABLED = True
    API_CACHE_ENABLED = True
    
    # 스테이징 환경에서는 모니터링 활성화
    MONITORING_ENABLED = True
    ALERTING_ENABLED = True
    
    # 스테이징 환경에서는 자동 스케일링 제한
    AUTO_SCALING_MAX_INSTANCES = 5

class ProductionPerformanceConfig(PerformanceConfig):
    """프로덕션 환경 성능 설정"""
    
    # 프로덕션 환경에서는 모든 최적화 활성화
    CACHE_ENABLED = True
    API_CACHE_ENABLED = True
    MONITORING_ENABLED = True
    ALERTING_ENABLED = True
    AUTO_SCALING_ENABLED = True
    
    # 프로덕션 환경에서는 더 엄격한 임계값
    PERFORMANCE_THRESHOLDS = {
        'cpu_usage': 75.0,
        'memory_usage': 80.0,
        'disk_usage': 85.0,
        'response_time': 1.5,
        'error_rate': 2.0,
        'cache_hit_rate': 85.0
    }
    
    # 프로덕션 환경에서는 더 큰 풀 크기
    DB_POOL_SIZE = 50
    DB_MAX_OVERFLOW = 100
    REDIS_POOL_SIZE = 20
    REDIS_MAX_CONNECTIONS = 100

def get_performance_config() -> PerformanceConfig:
    """환경에 따른 성능 설정 반환"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionPerformanceConfig()
    elif env == 'staging':
        return StagingPerformanceConfig()
    else:
        return DevelopmentPerformanceConfig()

# 캐시 설정
CACHE_CONFIG = {
    'default': {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'CACHE_DEFAULT_TIMEOUT': 3600,
        'CACHE_KEY_PREFIX': 'your_program_',
        'CACHE_REDIS_DB': 1,
        'CACHE_OPTIONS': {
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True,
            'max_connections': 50
        }
    },
    'session': {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'CACHE_DEFAULT_TIMEOUT': 86400,  # 24시간
        'CACHE_KEY_PREFIX': 'session_',
        'CACHE_REDIS_DB': 2
    },
    'api': {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'CACHE_DEFAULT_TIMEOUT': 1800,  # 30분
        'CACHE_KEY_PREFIX': 'api_',
        'CACHE_REDIS_DB': 3
    }
}

# 데이터베이스 설정
DATABASE_CONFIG = {
    'pool_size': int(os.getenv('DB_POOL_SIZE', 20)),
    'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 30)),
    'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
    'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
    'echo': os.getenv('DB_ECHO', 'false').lower() == 'true',
    'echo_pool': os.getenv('DB_ECHO_POOL', 'false').lower() == 'true',
    'connect_args': {
        'connect_timeout': 10,
        'application_name': 'your_program'
    }
}

# Redis 설정
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'password': os.getenv('REDIS_PASSWORD'),
    'socket_timeout': int(os.getenv('REDIS_SOCKET_TIMEOUT', 5)),
    'socket_connect_timeout': int(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', 5)),
    'retry_on_timeout': os.getenv('REDIS_RETRY_ON_TIMEOUT', 'true').lower() == 'true',
    'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', 50)),
    'decode_responses': True
}

# API 설정
API_CONFIG = {
    'rate_limit': {
        'enabled': os.getenv('API_RATE_LIMIT_ENABLED', 'true').lower() == 'true',
        'default': os.getenv('API_RATE_LIMIT_DEFAULT', '100 per minute'),
        'storage_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'strategy': 'fixed-window'
    },
    'caching': {
        'enabled': os.getenv('API_CACHE_ENABLED', 'true').lower() == 'true',
        'ttl': int(os.getenv('API_CACHE_TTL', 1800)),
        'compression': os.getenv('API_COMPRESSION_ENABLED', 'true').lower() == 'true',
        'compression_threshold': int(os.getenv('API_COMPRESSION_THRESHOLD', 1024))
    },
    'monitoring': {
        'enabled': os.getenv('API_MONITORING_ENABLED', 'true').lower() == 'true',
        'log_slow_queries': os.getenv('API_LOG_SLOW_QUERIES', 'true').lower() == 'true',
        'slow_query_threshold': float(os.getenv('API_SLOW_QUERY_THRESHOLD', 1.0))
    }
}

# 모니터링 설정
MONITORING_CONFIG = {
    'enabled': os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
    'interval': int(os.getenv('MONITORING_INTERVAL', 60)),
    'metrics_retention': int(os.getenv('METRICS_RETENTION_HOURS', 24)),
    'alerting': {
        'enabled': os.getenv('ALERTING_ENABLED', 'true').lower() == 'true',
        'email': os.getenv('ALERT_EMAIL'),
        'slack_webhook': os.getenv('SLACK_WEBHOOK_URL')
    },
    'thresholds': {
        'cpu_usage': float(os.getenv('CPU_THRESHOLD', 80.0)),
        'memory_usage': float(os.getenv('MEMORY_THRESHOLD', 85.0)),
        'disk_usage': float(os.getenv('DISK_THRESHOLD', 90.0)),
        'response_time': float(os.getenv('RESPONSE_TIME_THRESHOLD', 2.0)),
        'error_rate': float(os.getenv('ERROR_RATE_THRESHOLD', 5.0))
    }
}

# 로드 밸런싱 설정
LOAD_BALANCING_CONFIG = {
    'enabled': os.getenv('LOAD_BALANCING_ENABLED', 'true').lower() == 'true',
    'algorithm': os.getenv('LOAD_BALANCING_ALGORITHM', 'round_robin'),
    'health_check': {
        'interval': int(os.getenv('HEALTH_CHECK_INTERVAL', 30)),
        'timeout': int(os.getenv('HEALTH_CHECK_TIMEOUT', 5)),
        'max_failures': int(os.getenv('MAX_FAILURES', 3))
    },
    'servers': [
        {
            'id': 'server-1',
            'host': os.getenv('SERVER1_HOST', 'localhost'),
            'port': int(os.getenv('SERVER1_PORT', 5000)),
            'weight': int(os.getenv('SERVER1_WEIGHT', 1))
        },
        {
            'id': 'server-2',
            'host': os.getenv('SERVER2_HOST', 'localhost'),
            'port': int(os.getenv('SERVER2_PORT', 5001)),
            'weight': int(os.getenv('SERVER2_WEIGHT', 1))
        }
    ]
}

# 자동 스케일링 설정
AUTO_SCALING_CONFIG = {
    'enabled': os.getenv('AUTO_SCALING_ENABLED', 'true').lower() == 'true',
    'min_instances': int(os.getenv('AUTO_SCALING_MIN_INSTANCES', 2)),
    'max_instances': int(os.getenv('AUTO_SCALING_MAX_INSTANCES', 10)),
    'thresholds': {
        'cpu': float(os.getenv('AUTO_SCALING_CPU_THRESHOLD', 80.0)),
        'memory': float(os.getenv('AUTO_SCALING_MEMORY_THRESHOLD', 85.0)),
        'connections': float(os.getenv('AUTO_SCALING_CONNECTION_THRESHOLD', 80.0))
    },
    'cooldown': {
        'scale_up': int(os.getenv('AUTO_SCALING_SCALE_UP_COOLDOWN', 300)),
        'scale_down': int(os.getenv('AUTO_SCALING_SCALE_DOWN_COOLDOWN', 600))
    }
}

# 성능 최적화 설정
OPTIMIZATION_CONFIG = {
    'database': {
        'query_timeout': int(os.getenv('QUERY_TIMEOUT', 30)),
        'max_results': int(os.getenv('QUERY_MAX_RESULTS', 1000)),
        'batch_size': int(os.getenv('QUERY_BATCH_SIZE', 100)),
        'page_size': int(os.getenv('QUERY_PAGE_SIZE', 20))
    },
    'response': {
        'compression_enabled': os.getenv('RESPONSE_COMPRESSION_ENABLED', 'true').lower() == 'true',
        'compression_threshold': int(os.getenv('RESPONSE_COMPRESSION_THRESHOLD', 1024)),
        'streaming_enabled': os.getenv('RESPONSE_STREAMING_ENABLED', 'true').lower() == 'true',
        'chunk_size': int(os.getenv('RESPONSE_CHUNK_SIZE', 8192))
    },
    'caching': {
        'enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
        'ttl': int(os.getenv('CACHE_TTL', 3600)),
        'max_size': int(os.getenv('CACHE_MAX_SIZE', 100 * 1024 * 1024)),
        'compression_enabled': os.getenv('CACHE_COMPRESSION_ENABLED', 'true').lower() == 'true',
        'compression_threshold': int(os.getenv('CACHE_COMPRESSION_THRESHOLD', 1024))
    }
} 