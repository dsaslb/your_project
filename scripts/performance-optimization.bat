@echo off
REM Your Program 성능 최적화 스크립트 (Windows)
REM 사용법: scripts\performance-optimization.bat [target] [action]
REM target: database, cache, frontend, backend, all (기본값: all)
REM action: optimize, analyze, benchmark (기본값: optimize)

setlocal enabledelayedexpansion

REM 색상 정의
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 로그 함수
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 설정
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=all"

set "ACTION=%~2"
if "%ACTION%"=="" set "ACTION=optimize"

set "PROJECT_ROOT=%~dp0.."
set "OPTIMIZATION_LOG=%PROJECT_ROOT%\logs\optimization_%TARGET%_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"

REM 로그 디렉토리 생성
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"

call :log_info "Your Program Performance Optimization"
call :log_info "Target: %TARGET%"
call :log_info "Action: %ACTION%"

REM 메인 로직
if "%ACTION%"=="optimize" (
    if "%TARGET%"=="database" (
        call :optimize_database
    ) else if "%TARGET%"=="cache" (
        call :optimize_cache
    ) else if "%TARGET%"=="frontend" (
        call :optimize_frontend
    ) else if "%TARGET%"=="backend" (
        call :optimize_backend
    ) else if "%TARGET%"=="all" (
        call :optimize_database
        call :optimize_cache
        call :optimize_frontend
        call :optimize_backend
    ) else (
        call :log_error "Invalid target: %TARGET%"
        exit /b 1
    )
) else if "%ACTION%"=="analyze" (
    call :analyze_performance
) else if "%ACTION%"=="benchmark" (
    call :run_benchmark
) else (
    call :log_error "Invalid action: %ACTION%"
    exit /b 1
)

call :log_success "Performance optimization process completed"
exit /b 0

REM 데이터베이스 최적화
:optimize_database
call :log_info "Optimizing database performance..."

REM PostgreSQL 설정 최적화
call :log_info "Optimizing PostgreSQL configuration..."

REM postgresql.conf 최적화 설정
(
echo # Memory Settings
echo shared_buffers = 256MB
echo effective_cache_size = 1GB
echo work_mem = 4MB
echo maintenance_work_mem = 64MB
echo.
echo # WAL Settings
echo wal_buffers = 16MB
echo checkpoint_completion_target = 0.9
echo wal_writer_delay = 200ms
echo.
echo # Query Planner
echo random_page_cost = 1.1
echo effective_io_concurrency = 200
echo.
echo # Connection Settings
echo max_connections = 100
echo shared_preload_libraries = 'pg_stat_statements'
echo.
echo # Logging
echo log_statement = 'none'
echo log_min_duration_statement = 1000
echo log_checkpoints = on
echo log_connections = on
echo log_disconnections = on
echo log_lock_waits = on
echo.
echo # Autovacuum
echo autovacuum = on
echo autovacuum_max_workers = 3
echo autovacuum_naptime = 1min
echo autovacuum_vacuum_threshold = 50
echo autovacuum_analyze_threshold = 50
) > "%TEMP%\postgresql_optimized.conf"

REM 설정 적용
docker cp "%TEMP%\postgresql_optimized.conf" postgres:/var/lib/postgresql/data/postgresql.conf
docker-compose restart postgres

REM 인덱스 최적화
call :log_info "Creating optimized indexes..."

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

call :log_success "Database optimization completed"
goto :eof

REM 캐시 최적화
:optimize_cache
call :log_info "Optimizing cache performance..."

REM Redis 설정 최적화
call :log_info "Optimizing Redis configuration..."

(
echo # Memory Management
echo maxmemory 512mb
echo maxmemory-policy allkeys-lru
echo maxmemory-samples 5
echo.
echo # Persistence
echo save 900 1
echo save 300 10
echo save 60 10000
echo stop-writes-on-bgsave-error yes
echo rdbcompression yes
echo rdbchecksum yes
echo.
echo # Network
echo tcp-keepalive 300
echo timeout 0
echo tcp-backlog 511
echo.
echo # Performance
echo databases 16
echo hash-max-ziplist-entries 512
echo hash-max-ziplist-value 64
echo list-max-ziplist-size -2
echo set-max-intset-entries 512
echo zset-max-ziplist-entries 128
echo zset-max-ziplist-value 64
echo.
echo # Logging
echo loglevel notice
echo logfile ""
echo syslog-enabled no
) > "%TEMP%\redis_optimized.conf"

REM Redis 설정 적용
docker cp "%TEMP%\redis_optimized.conf" redis:/usr/local/etc/redis/redis.conf
docker-compose restart redis

call :log_success "Cache optimization completed"
goto :eof

REM 프론트엔드 최적화
:optimize_frontend
call :log_info "Optimizing frontend performance..."

cd /d "%PROJECT_ROOT%\your_program_frontend"

REM Next.js 설정 최적화
call :log_info "Optimizing Next.js configuration..."

REM next.config.js 최적화
(
echo const withPWA = require^('next-pwa'^)({
echo   dest: 'public',
echo   disable: process.env.NODE_ENV === 'development',
echo   register: true,
echo   skipWaiting: true,
echo })
echo.
echo /** @type {import^('next'^).NextConfig} */
echo const nextConfig = {
echo   // 성능 최적화
echo   experimental: {
echo     optimizeCss: true,
echo     optimizePackageImports: ['@mui/material', '@mui/icons-material', 'lodash'],
echo   },
echo   
echo   // 이미지 최적화
echo   images: {
echo     domains: ['localhost', 'yourprogram.com'],
echo     formats: ['image/webp', 'image/avif'],
echo     deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
echo     imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
echo   },
echo   
echo   // 번들 분석
echo   webpack: ^(config, { dev, isServer }^) =^> {
echo     if ^(!dev ^&^& !isServer^) {
echo       // 번들 크기 최적화
echo       config.optimization.splitChunks = {
echo         chunks: 'all',
echo         cacheGroups: {
echo           vendor: {
echo             test: /[\\/]node_modules[\\/]/,
echo             name: 'vendors',
echo             chunks: 'all',
echo           },
echo           common: {
echo             name: 'common',
echo             minChunks: 2,
echo             chunks: 'all',
echo             enforce: true,
echo           },
echo         },
echo       }
echo     }
echo     return config
echo   },
echo   
echo   // 압축 설정
echo   compress: true,
echo   
echo   // 캐시 설정
echo   generateEtags: false,
echo }
echo.
echo module.exports = withPWA^(nextConfig^)
) > next.config.js

REM 성능 최적화 빌드
call :log_info "Building optimized frontend..."
npm run build

cd /d "%PROJECT_ROOT%"
call :log_success "Frontend optimization completed"
goto :eof

REM 백엔드 최적화
:optimize_backend
call :log_info "Optimizing backend performance..."

REM Flask 설정 최적화
call :log_info "Optimizing Flask configuration..."

REM app.py 성능 최적화
(
echo from flask import Flask
echo from flask_cors import CORS
echo from flask_compress import Compress
echo from flask_limiter import Limiter
echo from flask_limiter.util import get_remote_address
echo import logging
echo from logging.handlers import RotatingFileHandler
echo import os
echo.
echo app = Flask^(__name__^)
echo.
echo # 성능 최적화 설정
echo app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1년
echo app.config['TEMPLATES_AUTO_RELOAD'] = False
echo app.config['JSON_SORT_KEYS'] = False
echo app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
echo.
echo # 압축 설정
echo Compress^(app^)
echo.
echo # CORS 설정
echo CORS^(app, resources={
echo     r"/api/*": {
echo         "origins": ["http://localhost:3000", "https://yourprogram.com"],
echo         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
echo         "allow_headers": ["Content-Type", "Authorization"]
echo     }
echo })
echo.
echo # Rate Limiting
echo limiter = Limiter^(
echo     app,
echo     key_func=get_remote_address,
echo     default_limits=["200 per day", "50 per hour"]
echo )
echo.
echo # 로깅 설정
echo if not app.debug:
echo     if not os.path.exists^('logs'^):
echo         os.mkdir^('logs'^)
echo     file_handler = RotatingFileHandler^('logs/your_program.log', maxBytes=10240, backupCount=10^)
echo     file_handler.setFormatter^(logging.Formatter^(
echo         '%%^(asctime^)s %%^(levelname^)s: %%^(message^)s [in %%^(pathname^)s:%%^(lineno^)d]'
echo     ^)^)
echo     file_handler.setLevel^(logging.INFO^)
echo     app.logger.addHandler^(file_handler^)
echo     app.logger.setLevel^(logging.INFO^)
echo     app.logger.info^('Your Program startup'^)
echo.
echo # 데이터베이스 연결 풀 최적화
echo from sqlalchemy import create_engine
echo from sqlalchemy.pool import QueuePool
echo.
echo engine = create_engine^(
echo     os.environ.get^('DATABASE_URL'^),
echo     poolclass=QueuePool,
echo     pool_size=20,
echo     max_overflow=30,
echo     pool_pre_ping=True,
echo     pool_recycle=3600
echo ^)
echo.
echo # 캐시 설정
echo from flask_caching import Cache
echo.
echo cache = Cache^(config={
echo     'CACHE_TYPE': 'redis',
echo     'CACHE_REDIS_URL': os.environ.get^('REDIS_URL', 'redis://localhost:6379/0'^),
echo     'CACHE_DEFAULT_TIMEOUT': 300,
echo     'CACHE_KEY_PREFIX': 'your_program_'
echo ^)
echo.
echo cache.init_app^(app^)
echo.
echo if __name__ == '__main__':
echo     app.run^(host='0.0.0.0', port=5001, threaded=True^)
) > "%PROJECT_ROOT%\app_optimized.py"

call :log_success "Backend optimization completed"
goto :eof

REM 성능 분석
:analyze_performance
call :log_info "Analyzing system performance..."

echo === System Performance Analysis === > "%OPTIMIZATION_LOG%"
echo Timestamp: %date% %time% >> "%OPTIMIZATION_LOG%"
echo. >> "%OPTIMIZATION_LOG%"

REM 시스템 리소스 분석
call :log_info "Analyzing system resources..."

echo === CPU Usage === >> "%OPTIMIZATION_LOG%"
wmic cpu get loadpercentage >> "%OPTIMIZATION_LOG%" 2>&1

echo. >> "%OPTIMIZATION_LOG%"
echo === Memory Usage === >> "%OPTIMIZATION_LOG%"
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /Value >> "%OPTIMIZATION_LOG%" 2>&1

echo. >> "%OPTIMIZATION_LOG%"
echo === Disk Usage === >> "%OPTIMIZATION_LOG%"
wmic logicaldisk get size,freespace,caption >> "%OPTIMIZATION_LOG%" 2>&1

echo. >> "%OPTIMIZATION_LOG%"
echo === Network Connections === >> "%OPTIMIZATION_LOG%"
netstat -an | findstr ":80\|:443\|:5001\|:8000\|:8002\|:3000\|:5432\|:6379" >> "%OPTIMIZATION_LOG%" 2>&1

call :log_success "Performance analysis completed. Results saved to %OPTIMIZATION_LOG%"
goto :eof

REM 성능 벤치마크
:run_benchmark
call :log_info "Running performance benchmarks..."

echo === Performance Benchmarks === > "%OPTIMIZATION_LOG%"
echo Timestamp: %date% %time% >> "%OPTIMIZATION_LOG%"
echo. >> "%OPTIMIZATION_LOG%"

REM 기본 성능 테스트
call :log_info "Running basic performance tests..."

echo === Basic Performance Tests === >> "%OPTIMIZATION_LOG%"

REM 응답 시간 측정
for /l %%i in (1,1,10) do (
    set "start_time=%time%"
    curl -s http://localhost/ >nul 2>&1
    set "end_time=%time%"
    echo Request %%i: %start_time% - %end_time% >> "%OPTIMIZATION_LOG%"
)

call :log_success "Benchmark completed. Results saved to %OPTIMIZATION_LOG%"
goto :eof 