@echo off
setlocal enabledelayedexpansion

REM Your Program 프로덕션 배포 스크립트 (Windows)
REM 사용법: scripts\deploy-production.bat [environment] [action]
REM environment: staging, production (기본값: production)
REM action: deploy, rollback, update (기본값: deploy)

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
set "ENVIRONMENT=%~1"
if "%ENVIRONMENT%"=="" set "ENVIRONMENT=production"

set "ACTION=%~2"
if "%ACTION%"=="" set "ACTION=deploy"

set "PROJECT_ROOT=%~dp0.."

REM 현재 시간
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DEPLOY_TIMESTAMP=%dt:~0,8%_%dt:~8,6%"

set "BACKUP_DIR=%PROJECT_ROOT%\backups"
set "DEPLOY_LOG=%PROJECT_ROOT%\logs\deploy_%ENVIRONMENT%_%DEPLOY_TIMESTAMP%.log"

REM 환경별 설정
if "%ENVIRONMENT%"=="staging" (
    set "DOCKER_COMPOSE_FILE=docker-compose.staging.yml"
    set "DOMAIN=staging.yourprogram.com"
) else if "%ENVIRONMENT%"=="production" (
    set "DOCKER_COMPOSE_FILE=docker-compose.production.yml"
    set "DOMAIN=yourprogram.com"
) else (
    call :log_error "Invalid environment: %ENVIRONMENT%"
    exit /b 1
)

REM 배포 전 검증
:validate_deployment
call :log_info "Validating deployment prerequisites..."

REM Docker 확인
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Docker is not installed"
    exit /b 1
)

REM Docker Compose 확인
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Docker Compose is not installed"
    exit /b 1
)

REM 환경 변수 파일 확인
if not exist "%PROJECT_ROOT%\.env.%ENVIRONMENT%" (
    call :log_error "Environment file .env.%ENVIRONMENT% not found"
    exit /b 1
)

REM SSL 인증서 확인 (프로덕션)
if "%ENVIRONMENT%"=="production" (
    if not exist "%PROJECT_ROOT%\nginx\ssl\cert.pem" (
        call :log_warning "SSL certificates not found. HTTPS will not be available."
    )
    if not exist "%PROJECT_ROOT%\nginx\ssl\key.pem" (
        call :log_warning "SSL certificates not found. HTTPS will not be available."
    )
)

call :log_success "Deployment validation passed"
goto :eof

REM 백업 생성
:create_backup
call :log_info "Creating backup before deployment..."

set "backup_name=backup_%ENVIRONMENT%_%DEPLOY_TIMESTAMP%"
set "backup_path=%BACKUP_DIR%\%backup_name%"

if not exist "%backup_path%" mkdir "%backup_path%"

REM 데이터베이스 백업
call :log_info "Backing up database..."
docker-compose exec -T postgres pg_dump -U your_program your_program > "%backup_path%\database.sql" 2>nul
docker-compose exec -T postgres pg_dump -U your_program_ai your_program_ai > "%backup_path%\database_ai.sql" 2>nul

REM 설정 파일 백업
call :log_info "Backing up configuration files..."
if exist "%PROJECT_ROOT%\.env.%ENVIRONMENT%" copy "%PROJECT_ROOT%\.env.%ENVIRONMENT%" "%backup_path%\" >nul
if exist "%PROJECT_ROOT%\nginx\nginx.conf" copy "%PROJECT_ROOT%\nginx\nginx.conf" "%backup_path%\" >nul
if exist "%PROJECT_ROOT%\docker-compose.yml" copy "%PROJECT_ROOT%\docker-compose.yml" "%backup_path%\" >nul

REM 업로드 파일 백업
if exist "%PROJECT_ROOT%\uploads" (
    call :log_info "Backing up uploads..."
    powershell -Command "Compress-Archive -Path '%PROJECT_ROOT%\uploads' -DestinationPath '%backup_path%\uploads.zip' -Force"
)

REM 로그 파일 백업
if exist "%PROJECT_ROOT%\logs" (
    call :log_info "Backing up logs..."
    powershell -Command "Compress-Archive -Path '%PROJECT_ROOT%\logs' -DestinationPath '%backup_path%\logs.zip' -Force"
)

call :log_success "Backup created: %backup_path%"
goto :eof

REM 이미지 빌드
:build_images
call :log_info "Building Docker images..."

set "image_tag=%ENVIRONMENT%-%DEPLOY_TIMESTAMP%"

REM 백엔드 이미지 빌드
call :log_info "Building backend image..."
docker build -f Dockerfile.backend -t your-program-backend:%image_tag% .

REM AI 서버 이미지 빌드
call :log_info "Building AI server image..."
docker build -f Dockerfile.ai -t your-program-ai:%image_tag% .

REM 프론트엔드 이미지 빌드
call :log_info "Building frontend image..."
docker build -f your_program_frontend\Dockerfile -t your-program-frontend:%image_tag% .\your_program_frontend

REM Gateway 이미지 빌드
call :log_info "Building gateway image..."
docker build -f Dockerfile.gateway -t your-program-gateway:%image_tag% .

call :log_success "All images built successfully"
goto :eof

REM 서비스 배포
:deploy_services
call :log_info "Deploying services to %ENVIRONMENT%..."

REM 기존 서비스 중지
call :log_info "Stopping existing services..."
docker-compose -f "%DOCKER_COMPOSE_FILE%" down --remove-orphans

REM 새 이미지로 서비스 시작
call :log_info "Starting services with new images..."
docker-compose -f "%DOCKER_COMPOSE_FILE%" up -d

REM 헬스체크
call :log_info "Performing health checks..."
timeout /t 30 /nobreak >nul

set "services=gateway backend ai-server frontend"
set "all_healthy=true"

for %%s in (%services%) do (
    call :check_service_health %%s
    if !errorlevel! neq 0 (
        call :log_error "Service %%s is not healthy"
        set "all_healthy=false"
    ) else (
        call :log_success "Service %%s is healthy"
    )
)

if "%all_healthy%"=="false" (
    call :log_error "Health check failed. Rolling back..."
    call :rollback_deployment
    exit /b 1
)

call :log_success "All services deployed successfully"
goto :eof

REM 서비스 헬스체크
:check_service_health
set "service=%~1"
set "max_attempts=10"
set "attempt=1"

:health_check_loop
if %attempt% gtr %max_attempts% goto :health_check_failed

if "%service%"=="gateway" (
    curl -f -s http://localhost:8000/health >nul 2>&1
    if !errorlevel! equ 0 goto :health_check_success
) else if "%service%"=="backend" (
    curl -f -s http://localhost:5001/health >nul 2>&1
    if !errorlevel! equ 0 goto :health_check_success
) else if "%service%"=="ai-server" (
    curl -f -s http://localhost:8002/health >nul 2>&1
    if !errorlevel! equ 0 goto :health_check_success
) else if "%service%"=="frontend" (
    curl -f -s http://localhost:3000 >nul 2>&1
    if !errorlevel! equ 0 goto :health_check_success
)

call :log_info "Health check attempt %attempt%/%max_attempts% for %service%"
timeout /t 10 /nobreak >nul
set /a "attempt+=1"
goto :health_check_loop

:health_check_success
exit /b 0

:health_check_failed
exit /b 1

REM 롤백
:rollback_deployment
call :log_warning "Rolling back deployment..."

REM 최신 백업 찾기
for /f "delims=" %%i in ('dir /b /o-d "%BACKUP_DIR%\backup_%ENVIRONMENT%_*" 2^>nul') do (
    set "latest_backup=%BACKUP_DIR%\%%i"
    goto :found_backup
)

call :log_error "No backup found for rollback"
goto :eof

:found_backup
call :log_info "Restoring from backup: %latest_backup%"

REM 데이터베이스 복원
if exist "%latest_backup%\database.sql" (
    call :log_info "Restoring database..."
    docker-compose exec -T postgres psql -U your_program your_program < "%latest_backup%\database.sql"
)

REM 설정 파일 복원
if exist "%latest_backup%\.env.%ENVIRONMENT%" (
    copy "%latest_backup%\.env.%ENVIRONMENT%" "%PROJECT_ROOT%\" >nul
)

REM 이전 이미지로 서비스 재시작
docker-compose -f "%DOCKER_COMPOSE_FILE%" down
docker-compose -f "%DOCKER_COMPOSE_FILE%" up -d

call :log_success "Rollback completed"
goto :eof

REM 데이터베이스 마이그레이션
:run_migrations
call :log_info "Running database migrations..."

docker-compose exec -T backend flask db upgrade
if %errorlevel% neq 0 (
    call :log_error "Database migration failed"
    exit /b 1
)

call :log_success "Database migrations completed"
goto :eof

REM 모니터링 설정
:setup_monitoring
call :log_info "Setting up monitoring..."

if not exist "%PROJECT_ROOT%\monitoring\prometheus.yml" (
    call :log_warning "Prometheus configuration not found"
    exit /b 1
)

if not exist "%PROJECT_ROOT%\monitoring\grafana\dashboards\your-program-dashboard.json" (
    call :log_warning "Grafana dashboard configuration not found"
    exit /b 1
)

call :log_success "Monitoring setup completed"
goto :eof

REM 성능 테스트
:run_performance_tests
call :log_info "Running performance tests..."

REM 간단한 부하 테스트 (PowerShell 사용)
powershell -Command "for ($i=0; $i -lt 100; $i++) { Invoke-WebRequest -Uri 'http://localhost' -UseBasicParsing | Out-Null }" > "%PROJECT_ROOT%\logs\performance_test_%DEPLOY_TIMESTAMP%.log" 2>&1

call :log_success "Performance tests completed"
goto :eof

REM 배포 후 정리
:cleanup_after_deployment
call :log_info "Cleaning up after deployment..."

REM 오래된 이미지 정리
docker image prune -f

REM 오래된 백업 정리 (30일 이상)
forfiles /p "%BACKUP_DIR%" /s /m backup_* /d -30 /c "cmd /c if @isdir==TRUE rmdir /s /q @path" 2>nul

REM 오래된 로그 정리 (7일 이상)
forfiles /p "%PROJECT_ROOT%\logs" /s /m *.log /d -7 /c "cmd /c del @path" 2>nul

call :log_success "Cleanup completed"
goto :eof

REM 배포 로그 기록
:log_deployment
set "status=%~1"
set "message=%~2"

echo %date% %time% - %ENVIRONMENT% - %ACTION% - %status% - %message% >> "%DEPLOY_LOG%"
goto :eof

REM 메인 배포 로직
:main
call :log_info "Starting %ENVIRONMENT% deployment..."
call :log_deployment "START" "Deployment initiated"

REM 배포 디렉토리 생성
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"

REM 배포 전 검증
call :validate_deployment
call :log_deployment "VALIDATION" "Prerequisites validated"

REM 백업 생성
call :create_backup
call :log_deployment "BACKUP" "Backup created"

if "%ACTION%"=="deploy" (
    REM 이미지 빌드
    call :build_images
    call :log_deployment "BUILD" "Images built"
    
    REM 서비스 배포
    call :deploy_services
    call :log_deployment "DEPLOY" "Services deployed"
    
    REM 데이터베이스 마이그레이션
    call :run_migrations
    call :log_deployment "MIGRATION" "Database migrated"
    
    REM 모니터링 설정
    call :setup_monitoring
    call :log_deployment "MONITORING" "Monitoring configured"
    
    REM 성능 테스트
    call :run_performance_tests
    call :log_deployment "TESTING" "Performance tests completed"
    
    REM 정리
    call :cleanup_after_deployment
    call :log_deployment "CLEANUP" "Cleanup completed"
    
    call :log_success "Deployment completed successfully!"
    call :log_deployment "SUCCESS" "Deployment completed"
    
) else if "%ACTION%"=="rollback" (
    call :rollback_deployment
    call :log_deployment "ROLLBACK" "Rollback completed"
    
) else if "%ACTION%"=="update" (
    REM 설정 파일만 업데이트
    call :log_info "Updating configuration..."
    docker-compose -f "%DOCKER_COMPOSE_FILE%" down
    docker-compose -f "%DOCKER_COMPOSE_FILE%" up -d
    call :log_deployment "UPDATE" "Configuration updated"
    
) else (
    call :log_error "Invalid action: %ACTION%"
    exit /b 1
)

REM 배포 완료 알림
if "%ENVIRONMENT%"=="production" (
    call :log_info "Sending deployment notification..."
    REM Slack, 이메일 등으로 알림 전송
    echo Your Program deployment to %ENVIRONMENT% completed at %date% %time%
)

call :log_success "Deployment process completed"
goto :eof

REM 스크립트 실행
call :main %* 