#!/bin/bash

# Your Program 성능 최적화 스크립트
# 사용법: ./scripts/performance-optimization.sh [target] [action]
# target: database, cache, frontend, backend, all (기본값: all)
# action: optimize, analyze, benchmark (기본값: optimize)

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 설정
TARGET=${1:-all}
ACTION=${2:-optimize}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPTIMIZATION_LOG="$PROJECT_ROOT/logs/optimization_${TARGET}_$(date +%Y%m%d_%H%M%S).log"

# 데이터베이스 최적화
optimize_database() {
    log_info "Optimizing database performance..."
    
    # PostgreSQL 설정 최적화
    log_info "Optimizing PostgreSQL configuration..."
    
    # postgresql.conf 최적화 설정
    cat > /tmp/postgresql_optimized.conf << EOF
# Memory Settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# WAL Settings
wal_buffers = 16MB
checkpoint_completion_target = 0.9
wal_writer_delay = 200ms

# Query Planner
random_page_cost = 1.1
effective_io_concurrency = 200

# Connection Settings
max_connections = 100
shared_preload_libraries = 'pg_stat_statements'

# Logging
log_statement = 'none'
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# Autovacuum
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50
EOF

    # 설정 적용
    docker cp /tmp/postgresql_optimized.conf postgres:/var/lib/postgresql/data/postgresql.conf
    docker-compose restart postgres
    
    # 인덱스 최적화
    log_info "Creating optimized indexes..."
    
    docker-compose exec -T postgres psql -U your_program your_program << EOF
-- 사용자 테이블 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 주문 테이블 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_total_amount ON orders(total_amount);

-- 제품 테이블 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_stock ON products(stock);

-- 출근 기록 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attendance_user_id ON attendance(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attendance_status ON attendance(status);

-- 복합 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_status ON orders(user_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attendance_user_date ON attendance(user_id, date);

-- 부분 인덱스 (활성 주문만)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_active ON orders(user_id) WHERE status IN ('pending', 'processing');

-- GIN 인덱스 (JSON 필드)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_metadata_gin ON orders USING GIN(metadata);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_tags_gin ON products USING GIN(tags);

-- 통계 업데이트
ANALYZE;
EOF

    # 테이블 파티셔닝 (대용량 데이터용)
    log_info "Setting up table partitioning..."
    
    docker-compose exec -T postgres psql -U your_program your_program << EOF
-- 주문 테이블 월별 파티셔닝
CREATE TABLE IF NOT EXISTS orders_partitioned (
    LIKE orders INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- 2024년 파티션
CREATE TABLE orders_2024_01 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE orders_2024_02 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- 추가 파티션은 필요에 따라 생성

-- 출근 기록 월별 파티셔닝
CREATE TABLE IF NOT EXISTS attendance_partitioned (
    LIKE attendance INCLUDING ALL
) PARTITION BY RANGE (date);

CREATE TABLE attendance_2024_01 PARTITION OF attendance_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE attendance_2024_02 PARTITION OF attendance_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
EOF

    log_success "Database optimization completed"
}

# 캐시 최적화
optimize_cache() {
    log_info "Optimizing cache performance..."
    
    # Redis 설정 최적화
    log_info "Optimizing Redis configuration..."
    
    cat > /tmp/redis_optimized.conf << EOF
# Memory Management
maxmemory 512mb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes

# Network
tcp-keepalive 300
timeout 0
tcp-backlog 511

# Performance
databases 16
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# Logging
loglevel notice
logfile ""
syslog-enabled no
EOF

    # Redis 설정 적용
    docker cp /tmp/redis_optimized.conf redis:/usr/local/etc/redis/redis.conf
    docker-compose restart redis
    
    # 캐시 워밍업 스크립트
    log_info "Creating cache warming script..."
    
    cat > "$PROJECT_ROOT/scripts/cache-warmup.py" << 'EOF'
#!/usr/bin/env python3
import redis
import requests
import json
import time

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

# 캐시할 데이터 목록
cache_targets = [
    '/api/products',
    '/api/categories',
    '/api/users/stats',
    '/api/orders/stats',
    '/api/analytics/dashboard'
]

def warmup_cache():
    print("Starting cache warmup...")
    
    for endpoint in cache_targets:
        try:
            # API 호출
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=10)
            if response.status_code == 200:
                # Redis에 캐시 (1시간)
                cache_key = f'cache:{endpoint}'
                r.setex(cache_key, 3600, response.text)
                print(f"Cached: {endpoint}")
            else:
                print(f"Failed to cache {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"Error caching {endpoint}: {e}")
        
        time.sleep(1)  # 요청 간격
    
    print("Cache warmup completed")

if __name__ == "__main__":
    warmup_cache()
EOF

    chmod +x "$PROJECT_ROOT/scripts/cache-warmup.py"
    
    # 캐시 워밍업 실행
    log_info "Running cache warmup..."
    python3 "$PROJECT_ROOT/scripts/cache-warmup.py"
    
    log_success "Cache optimization completed"
}

# 프론트엔드 최적화
optimize_frontend() {
    log_info "Optimizing frontend performance..."
    
    cd "$PROJECT_ROOT/your_program_frontend"
    
    # Next.js 설정 최적화
    log_info "Optimizing Next.js configuration..."
    
    # next.config.js 최적화
    cat > next.config.js << 'EOF'
const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true,
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  // 성능 최적화
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['@mui/material', '@mui/icons-material', 'lodash'],
  },
  
  // 이미지 최적화
  images: {
    domains: ['localhost', 'yourprogram.com'],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // 번들 분석
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      // 번들 크기 최적화
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            enforce: true,
          },
        },
      }
    }
    return config
  },
  
  // 압축 설정
  compress: true,
  
  // 캐시 설정
  generateEtags: false,
  
  // 보안 헤더
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = withPWA(nextConfig)
EOF

    # 성능 최적화 빌드
    log_info "Building optimized frontend..."
    npm run build
    
    # 번들 분석
    if command -v npx &> /dev/null; then
        log_info "Analyzing bundle size..."
        npx @next/bundle-analyzer
    fi
    
    cd "$PROJECT_ROOT"
    log_success "Frontend optimization completed"
}

# 백엔드 최적화
optimize_backend() {
    log_info "Optimizing backend performance..."
    
    # Flask 설정 최적화
    log_info "Optimizing Flask configuration..."
    
    # app.py 성능 최적화
    cat > "$PROJECT_ROOT/app_optimized.py" << 'EOF'
from flask import Flask
from flask_cors import CORS
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)

# 성능 최적화 설정
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1년
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# 압축 설정
Compress(app)

# CORS 설정
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://yourprogram.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Rate Limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# 로깅 설정
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/your_program.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Your Program startup')

# 데이터베이스 연결 풀 최적화
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    os.environ.get('DATABASE_URL'),
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 캐시 설정
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'your_program_'
})

cache.init_app(app)

# 라우트 최적화 예시
@app.route('/api/optimized/products')
@cache.cached(timeout=300)
@limiter.limit("100 per minute")
def get_products_optimized():
    # 최적화된 제품 조회
    from sqlalchemy.orm import joinedload
    from models import Product
    
    products = Product.query.options(
        joinedload(Product.category)
    ).filter(
        Product.active == True
    ).limit(50).all()
    
    return {'products': [p.to_dict() for p in products]}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True)
EOF

    # Gunicorn 설정 최적화
    cat > "$PROJECT_ROOT/gunicorn.conf.py" << 'EOF'
import multiprocessing

# 서버 소켓
bind = "0.0.0.0:5001"
backlog = 2048

# Worker 프로세스
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 로깅
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 이름
proc_name = "your_program"

# 타임아웃
timeout = 30
keepalive = 2

# 보안
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
EOF

    log_success "Backend optimization completed"
}

# 성능 분석
analyze_performance() {
    log_info "Analyzing system performance..."
    
    # 시스템 리소스 분석
    log_info "Analyzing system resources..."
    
    echo "=== System Performance Analysis ===" > "$OPTIMIZATION_LOG"
    echo "Timestamp: $(date)" >> "$OPTIMIZATION_LOG"
    echo "" >> "$OPTIMIZATION_LOG"
    
    # CPU 사용률
    echo "=== CPU Usage ===" >> "$OPTIMIZATION_LOG"
    top -bn1 | grep "Cpu(s)" >> "$OPTIMIZATION_LOG"
    
    # 메모리 사용률
    echo "" >> "$OPTIMIZATION_LOG"
    echo "=== Memory Usage ===" >> "$OPTIMIZATION_LOG"
    free -h >> "$OPTIMIZATION_LOG"
    
    # 디스크 사용률
    echo "" >> "$OPTIMIZATION_LOG"
    echo "=== Disk Usage ===" >> "$OPTIMIZATION_LOG"
    df -h >> "$OPTIMIZATION_LOG"
    
    # 네트워크 연결
    echo "" >> "$OPTIMIZATION_LOG"
    echo "=== Network Connections ===" >> "$OPTIMIZATION_LOG"
    netstat -tuln | grep -E ":(80|443|5001|8000|8002|3000)" >> "$OPTIMIZATION_LOG"
    
    # 데이터베이스 성능 분석
    log_info "Analyzing database performance..."
    
    docker-compose exec -T postgres psql -U your_program your_program << EOF >> "$OPTIMIZATION_LOG" 2>&1
-- 느린 쿼리 분석
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- 테이블 크기 분석
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- 인덱스 사용률
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
EOF

    # Redis 성능 분석
    log_info "Analyzing Redis performance..."
    
    echo "" >> "$OPTIMIZATION_LOG"
    echo "=== Redis Performance ===" >> "$OPTIMIZATION_LOG"
    docker-compose exec redis redis-cli info memory >> "$OPTIMIZATION_LOG"
    docker-compose exec redis redis-cli info stats >> "$OPTIMIZATION_LOG"
    
    log_success "Performance analysis completed. Results saved to $OPTIMIZATION_LOG"
}

# 성능 벤치마크
run_benchmark() {
    log_info "Running performance benchmarks..."
    
    # Apache Bench 벤치마크
    if command -v ab &> /dev/null; then
        log_info "Running Apache Bench tests..."
        
        echo "=== Performance Benchmarks ===" > "$OPTIMIZATION_LOG"
        echo "Timestamp: $(date)" >> "$OPTIMIZATION_LOG"
        echo "" >> "$OPTIMIZATION_LOG"
        
        # 홈페이지 벤치마크
        echo "=== Homepage Benchmark ===" >> "$OPTIMIZATION_LOG"
        ab -n 1000 -c 10 http://localhost/ >> "$OPTIMIZATION_LOG" 2>&1
        
        # API 벤치마크
        echo "" >> "$OPTIMIZATION_LOG"
        echo "=== API Benchmark ===" >> "$OPTIMIZATION_LOG"
        ab -n 500 -c 5 http://localhost:8000/api/products >> "$OPTIMIZATION_LOG" 2>&1
        
        # 데이터베이스 벤치마크
        echo "" >> "$OPTIMIZATION_LOG"
        echo "=== Database Benchmark ===" >> "$OPTIMIZATION_LOG"
        ab -n 200 -c 2 http://localhost:5001/api/orders >> "$OPTIMIZATION_LOG" 2>&1
    else
        log_warning "Apache Bench not available, using curl for basic tests"
        
        # 기본 성능 테스트
        echo "=== Basic Performance Tests ===" > "$OPTIMIZATION_LOG"
        
        # 응답 시간 측정
        for i in {1..10}; do
            start_time=$(date +%s%N)
            curl -s http://localhost/ > /dev/null
            end_time=$(date +%s%N)
            response_time=$(( (end_time - start_time) / 1000000 ))
            echo "Request $i: ${response_time}ms" >> "$OPTIMIZATION_LOG"
        done
    fi
    
    log_success "Benchmark completed. Results saved to $OPTIMIZATION_LOG"
}

# 메인 로직
main() {
    log_info "Your Program Performance Optimization"
    log_info "Target: $TARGET"
    log_info "Action: $ACTION"
    
    # 로그 디렉토리 생성
    mkdir -p "$PROJECT_ROOT/logs"
    
    case $ACTION in
        "optimize")
            case $TARGET in
                "database")
                    optimize_database
                    ;;
                "cache")
                    optimize_cache
                    ;;
                "frontend")
                    optimize_frontend
                    ;;
                "backend")
                    optimize_backend
                    ;;
                "all")
                    optimize_database
                    optimize_cache
                    optimize_frontend
                    optimize_backend
                    ;;
                *)
                    log_error "Invalid target: $TARGET"
                    exit 1
                    ;;
            esac
            ;;
            
        "analyze")
            analyze_performance
            ;;
            
        "benchmark")
            run_benchmark
            ;;
            
        *)
            log_error "Invalid action: $ACTION"
            exit 1
            ;;
    esac
    
    log_success "Performance optimization process completed"
}

# 스크립트 실행
main "$@" 