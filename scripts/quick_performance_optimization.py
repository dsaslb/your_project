#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 성능 최적화 스크립트
Redis 없이도 성능을 개선할 수 있는 방법들을 적용
"""

import os
import sys
import json
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def optimize_database_queries():
    """데이터베이스 쿼리 최적화"""
    logger.info("데이터베이스 쿼리 최적화 중...")

    # SQLite 데이터베이스 최적화
    db_path = project_root / "instance" / "your_program.db"
    if db_path.exists():
        try:
            import sqlite3

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # 인덱스 생성
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
                "CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)",
                "CREATE INDEX IF NOT EXISTS idx_brands_name ON brands(name)",
                "CREATE INDEX IF NOT EXISTS idx_branches_brand_id ON branches(brand_id)",
                "CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
                "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)",
            ]

            for index_sql in indexes:
                cursor.execute(index_sql)

            # 통계 업데이트
            cursor.execute("ANALYZE")
            conn.commit()
            conn.close()

            logger.info("✅ 데이터베이스 인덱스 최적화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 최적화 실패: {e}")


def optimize_cache_config():
    """캐시 설정 최적화"""
    logger.info("캐시 설정 최적화 중...")

    # 캐시 설정 파일 생성
    cache_config = {
        "cache_type": "simple",  # Redis 대신 메모리 캐시 사용
        "cache_default_timeout": 300,
        "cache_threshold": 1000,
        "cache_key_prefix": "your_program_",
        "cache_options": {"maxsize": 1000, "ttl": 300},
    }

    config_path = project_root / "cache_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cache_config, f, indent=2, ensure_ascii=False)

    logger.info("✅ 캐시 설정 최적화 완료")


def optimize_app_config():
    """앱 설정 최적화"""
    logger.info("앱 설정 최적화 중...")

    # config.py 최적화
    config_content = """
# -*- coding: utf-8 -*-
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/your_program.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 성능 최적화 설정
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # 캐시 설정 (Redis 없이 메모리 캐시 사용)
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_THRESHOLD = 1000
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # 개발 환경
    SESSION_COOKIE_HTTPONLY = True
    
    # 로깅 설정
    LOG_LEVEL = "INFO"
    
    # 성능 모니터링 설정
    PERFORMANCE_MONITORING = True
    SLOW_QUERY_THRESHOLD = 1.0  # 1초 이상 쿼리 로깅
    
    # 보안 설정
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
"""

    config_path = project_root / "config.py"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    logger.info("✅ 앱 설정 최적화 완료")


def create_performance_monitor():
    """성능 모니터링 유틸리티 생성"""
    logger.info("성능 모니터링 유틸리티 생성 중...")

    monitor_content = '''
# -*- coding: utf-8 -*-
"""
성능 모니터링 유틸리티
Redis 없이도 작동하는 성능 모니터링
"""

import time
import logging
import threading
from functools import wraps
from typing import Dict, Any, Optional
from collections import defaultdict, deque
import psutil
import os

logger = logging.getLogger(__name__)

class SimplePerformanceMonitor:
    """간단한 성능 모니터링 클래스"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.response_times = defaultdict(lambda: deque(maxlen=max_history))
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.slow_queries = deque(maxlen=100)
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 60):
        """모니터링 시작"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("성능 모니터링 시작됨")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("성능 모니터링 중지됨")
    
    def _monitor_loop(self, interval: int):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                self._log_system_stats()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                time.sleep(interval)
    
    def _log_system_stats(self):
        """시스템 통계 로깅"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            logger.info(f"시스템 상태 - CPU: {cpu_percent}%, "
                       f"메모리: {memory.percent}%, "
                       f"활성 요청: {sum(self.request_counts.values())}")
        except Exception as e:
            logger.error(f"시스템 통계 수집 오류: {e}")
    
    def record_request(self, endpoint: str, method: str, response_time: float, 
                      status_code: int, error: Optional[str] = None):
        """요청 기록"""
        key = f"{method} {endpoint}"
        
        self.request_counts[key] += 1
        self.response_times[key].append(response_time)
        
        if status_code >= 400:
            self.error_counts[key] += 1
        
        if response_time > 2.0:  # 2초 이상
            self.slow_queries.append({
                'endpoint': endpoint,
                'method': method,
                'response_time': response_time,
                'timestamp': time.time()
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 조회"""
        stats = {
            'total_requests': sum(self.request_counts.values()),
            'total_errors': sum(self.error_counts.values()),
            'slow_queries_count': len(self.slow_queries),
            'endpoints': {}
        }
        
        for key in self.request_counts:
            response_times = list(self.response_times[key])
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                stats['endpoints'][key] = {
                    'requests': self.request_counts[key],
                    'errors': self.error_counts[key],
                    'avg_response_time': round(avg_time, 3),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times)
                }
        
        return stats
    
    def get_health_status(self) -> Dict[str, Any]:
        """헬스 상태 조회"""
        stats = self.get_stats()
        
        # 성능 등급 평가
        avg_response_time = 0
        if stats['endpoints']:
            total_time = sum(ep['avg_response_time'] for ep in stats['endpoints'].values())
            avg_response_time = total_time / len(stats['endpoints'])
        
        if avg_response_time < 1.0:
            status = "healthy"
        elif avg_response_time < 2.0:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'status': status,
            'avg_response_time': round(avg_response_time, 3),
            'total_requests': stats['total_requests'],
            'error_rate': (stats['total_errors'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0,
            'slow_queries': len(self.slow_queries)
        }

# 전역 인스턴스
performance_monitor = SimplePerformanceMonitor()

def monitor_performance(f):
    """성능 모니터링 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        error = None
        status_code = 200
        
        try:
            result = f(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            status_code = 500
            raise
        finally:
            response_time = time.time() - start_time
            endpoint = f.__name__
            method = "GET"  # 기본값
            
            performance_monitor.record_request(
                endpoint, method, response_time, status_code, error
            )
    
    return decorated_function
'''

    monitor_path = project_root / "utils" / "simple_performance_monitor.py"
    monitor_path.parent.mkdir(exist_ok=True)

    with open(monitor_path, "w", encoding="utf-8") as f:
        f.write(monitor_content)

    logger.info("✅ 성능 모니터링 유틸리티 생성 완료")


def main():
    """메인 실행 함수"""
    logger.info("=== Your Program 성능 최적화 시작 ===")

    try:
        # 1. 데이터베이스 쿼리 최적화
        optimize_database_queries()

        # 2. 캐시 설정 최적화
        optimize_cache_config()

        # 3. 앱 설정 최적화
        optimize_app_config()

        # 4. 성능 모니터링 유틸리티 생성
        create_performance_monitor()

        logger.info("=== 성능 최적화 완료 ===")
        logger.info("✅ 다음 단계:")
        logger.info("1. 서버를 재시작하세요: python app.py")
        logger.info(
            "2. 성능 테스트를 다시 실행하세요: python scripts/performance_test.py"
        )
        logger.info("3. 응답 시간이 개선되었는지 확인하세요")

    except Exception as e:
        logger.error(f"성능 최적화 중 오류 발생: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
