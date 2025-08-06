from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import redis
import logging
from contextlib import contextmanager
import time

# 로거 설정
logger = logging.getLogger(__name__)

# 데이터베이스
db = SQLAlchemy()
migrate = Migrate()

# 로그인 매니저
login_manager = LoginManager()

# 요청 제한 (메모리 저장소 명시적 설정)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # 메모리 저장소 명시적 설정
)

# 캐싱
cache = Cache()

# CSRF 보호
csrf = CSRFProtect()

# Redis 클라이언트 (기본 설정)
try:
    redis_client = redis.Redis(
        host='localhost', 
        port=6379, 
        db=0, 
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )
    redis_client.ping()  # 연결 테스트
    logger.info("Redis 연결 성공")
except Exception as e:
    logger.warning(f"Redis 연결 실패: {e}")
    redis_client = None

# 데이터베이스 성능 모니터링
class DatabaseMonitor:
    """데이터베이스 성능 모니터링 클래스"""
    
    def __init__(self):
        self.query_times = []
        self.slow_query_threshold = 1.0  # 1초 이상 쿼리
    
    def record_query_time(self, query_time):
        """쿼리 실행 시간 기록"""
        self.query_times.append(query_time)
        if query_time > self.slow_query_threshold:
            logger.warning(f"Slow query detected: {query_time:.3f}s")
        
        # 최근 100개만 유지
        if len(self.query_times) > 100:
            self.query_times = self.query_times[-100:]
    
    def get_stats(self):
        """성능 통계 반환"""
        if not self.query_times:
            return {}
        
        return {
            'total_queries': len(self.query_times),
            'avg_query_time': sum(self.query_times) / len(self.query_times),
            'max_query_time': max(self.query_times),
            'min_query_time': min(self.query_times),
            'slow_queries': len([t for t in self.query_times if t > self.slow_query_threshold])
        }

db_monitor = DatabaseMonitor()

@contextmanager
def db_performance_monitor():
    """데이터베이스 성능 모니터링 컨텍스트 매니저"""
    start_time = time.time()
    try:
        yield
    finally:
        query_time = time.time() - start_time
        db_monitor.record_query_time(query_time)


def init_extensions(app):
    """모든 확장 기능을 초기화합니다."""
    
    # 데이터베이스 설정 최적화
    app.config.setdefault('SQLALCHEMY_ENGINE_OPTIONS', {
        'pool_size': 10,
        'pool_timeout': 20,
        'pool_recycle': 3600,
        'max_overflow': 20,
        'pool_pre_ping': True
    })
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 로그인 매니저 설정
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    login_manager.login_message_category = 'error'
    
    # 요청 제한 설정
    limiter.init_app(app)
    
    # 캐싱 설정 최적화
    cache_config = {
        'CACHE_TYPE': 'redis' if redis_client else 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_KEY_PREFIX': 'your_program_',
        'CACHE_REDIS_URL': 'redis://localhost:6379/0' if redis_client else None
    }
    cache.init_app(app, config=cache_config)
    
    # CSRF 보호 설정
    csrf.init_app(app)
    
    # 데이터베이스 이벤트 리스너 등록
    @app.before_request
    def before_request():
        """요청 전 처리"""
        pass
    
    @app.after_request
    def after_request(response):
        """요청 후 처리"""
        return response
    
    logger.info("모든 확장 기능 초기화 완료")
