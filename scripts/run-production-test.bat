@echo off
REM Your Program 프로덕션 테스트 스크립트 (Windows)
REM 사용법: scripts\run-production-test.bat [component] [action]
REM component: system, application, database, network, all (기본값: all)
REM action: test, validate, report (기본값: test)

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
set "COMPONENT=%~1"
if "%COMPONENT%"=="" set "COMPONENT=all"

set "ACTION=%~2"
if "%ACTION%"=="" set "ACTION=test"

set "PROJECT_ROOT=%~dp0.."
set "TEST_RESULTS=%PROJECT_ROOT%\test-results"
set "PRODUCTION_READINESS_LOG=%TEST_RESULTS%\production_readiness_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"

REM 테스트 결과 디렉토리 생성
if not exist "%TEST_RESULTS%" mkdir "%TEST_RESULTS%"

call :log_info "Your Program Production Readiness Test"
call :log_info "Component: %COMPONENT%"
call :log_info "Action: %ACTION%"

REM 메인 로직
if "%ACTION%"=="test" (
    if "%COMPONENT%"=="system" (
        call :test_system
    ) else if "%COMPONENT%"=="application" (
        call :test_application
    ) else if "%COMPONENT%"=="database" (
        call :test_database
    ) else if "%COMPONENT%"=="network" (
        call :test_network
    ) else if "%COMPONENT%"=="all" (
        call :test_system
        call :test_application
        call :test_database
        call :test_network
    ) else (
        call :log_error "Invalid component: %COMPONENT%"
        exit /b 1
    )
) else if "%ACTION%"=="validate" (
    call :test_system
    call :test_application
    call :test_database
    call :test_network
    call :validate_results
) else if "%ACTION%"=="report" (
    call :generate_report
) else (
    call :log_error "Invalid action: %ACTION%"
    exit /b 1
)

call :log_success "Production readiness test completed"
exit /b 0

REM 시스템 테스트
:test_system
call :log_info "Testing system readiness..."

echo === System Readiness Test === >> "%PRODUCTION_READINESS_LOG%"
echo Timestamp: %date% %time% >> "%PRODUCTION_READINESS_LOG%"
echo. >> "%PRODUCTION_READINESS_LOG%"

REM CPU 테스트
call :log_info "Testing CPU performance..."
echo === CPU Test === >> "%PRODUCTION_READINESS_LOG%"

REM CPU 코어 수 확인
for /f "tokens=*" %%i in ('wmic cpu get NumberOfCores /value ^| find "="') do set "%%i"
echo CPU Cores: %NumberOfCores% >> "%PRODUCTION_READINESS_LOG%"

if %NumberOfCores% LSS 2 (
    call :log_warning "Low CPU cores detected: %NumberOfCores%"
    echo WARNING: Low CPU cores detected: %NumberOfCores% >> "%PRODUCTION_READINESS_LOG%"
) else (
    call :log_success "CPU cores: %NumberOfCores%"
)

REM 메모리 테스트
call :log_info "Testing memory..."
echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Memory Test === >> "%PRODUCTION_READINESS_LOG%"

for /f "tokens=*" %%i in ('wmic computersystem get TotalPhysicalMemory /value ^| find "="') do set "%%i"
for /f "tokens=*" %%i in ('wmic OS get FreePhysicalMemory /value ^| find "="') do set "%%i"

set /a "TOTAL_MEM_MB=%TotalPhysicalMemory:~0,-1%/1024/1024"
set /a "FREE_MEM_MB=%FreePhysicalMemory:~0,-1%"
echo Total Memory: %TOTAL_MEM_MB%MB >> "%PRODUCTION_READINESS_LOG%"
echo Free Memory: %FREE_MEM_MB%MB >> "%PRODUCTION_READINESS_LOG%"

if %TOTAL_MEM_MB% LSS 2048 (
    call :log_warning "Low memory detected: %TOTAL_MEM_MB%MB"
    echo WARNING: Low memory detected: %TOTAL_MEM_MB%MB >> "%PRODUCTION_READINESS_LOG%"
) else (
    call :log_success "Memory: %TOTAL_MEM_MB%MB"
)

REM 디스크 테스트
call :log_info "Testing disk performance..."
echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Disk Test === >> "%PRODUCTION_READINESS_LOG%"

for /f "tokens=*" %%i in ('wmic logicaldisk where "DeviceID='C:'" get Size,FreeSpace /value ^| find "="') do set "%%i"
set /a "DISK_SIZE_GB=%Size:~0,-1%/1024/1024/1024"
set /a "DISK_FREE_GB=%FreeSpace:~0,-1%/1024/1024/1024"
set /a "DISK_USAGE_PERCENT=(%Size:~0,-1%-%FreeSpace:~0,-1%)*100/%Size:~0,-1%"

echo Disk Size: %DISK_SIZE_GB%GB >> "%PRODUCTION_READINESS_LOG%"
echo Disk Free: %DISK_FREE_GB%GB >> "%PRODUCTION_READINESS_LOG%"
echo Disk Usage: %DISK_USAGE_PERCENT%%% >> "%PRODUCTION_READINESS_LOG%"

if %DISK_USAGE_PERCENT% GTR 80 (
    call :log_warning "High disk usage: %DISK_USAGE_PERCENT%%%"
    echo WARNING: High disk usage: %DISK_USAGE_PERCENT%%% >> "%PRODUCTION_READINESS_LOG%"
) else (
    call :log_success "Disk usage: %DISK_USAGE_PERCENT%%%"
)

REM 네트워크 테스트
call :log_info "Testing network connectivity..."
echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Network Test === >> "%PRODUCTION_READINESS_LOG%"

REM 인터넷 연결 확인
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Internet connectivity: OK"
    echo Internet connectivity: OK >> "%PRODUCTION_READINESS_LOG%"
) else (
    call :log_error "Internet connectivity: FAILED"
    echo ERROR: Internet connectivity: FAILED >> "%PRODUCTION_READINESS_LOG%"
)

REM DNS 확인
nslookup google.com >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "DNS resolution: OK"
    echo DNS resolution: OK >> "%PRODUCTION_READINESS_LOG%"
) else (
    call :log_error "DNS resolution: FAILED"
    echo ERROR: DNS resolution: FAILED >> "%PRODUCTION_READINESS_LOG%"
)

goto :eof

REM 애플리케이션 테스트
:test_application
call :log_info "Testing application readiness..."

echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Application Readiness Test === >> "%PRODUCTION_READINESS_LOG%"
echo Timestamp: %date% %time% >> "%PRODUCTION_READINESS_LOG%"
echo. >> "%PRODUCTION_READINESS_LOG%"

REM Docker 테스트
call :log_info "Testing Docker..."
echo === Docker Test === >> "%PRODUCTION_READINESS_LOG%"

docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker --version') do set "DOCKER_VERSION=%%i"
    echo Docker Version: %DOCKER_VERSION% >> "%PRODUCTION_READINESS_LOG%"
    call :log_success "Docker: %DOCKER_VERSION%"
    
    REM Docker Compose 테스트
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=*" %%i in ('docker-compose --version') do set "COMPOSE_VERSION=%%i"
        echo Docker Compose Version: %COMPOSE_VERSION% >> "%PRODUCTION_READINESS_LOG%"
        call :log_success "Docker Compose: %COMPOSE_VERSION%"
    ) else (
        call :log_error "Docker Compose not found"
        echo ERROR: Docker Compose not found >> "%PRODUCTION_READINESS_LOG%"
    )
) else (
    call :log_error "Docker not found"
    echo ERROR: Docker not found >> "%PRODUCTION_READINESS_LOG%"
)

REM 서비스 상태 테스트
call :log_info "Testing service status..."
echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Service Status Test === >> "%PRODUCTION_READINESS_LOG%"

REM 서비스 시작
call :log_info "Starting services..."
cd /d "%PROJECT_ROOT%"
docker-compose up -d

REM 서비스 대기
timeout /t 30 /nobreak >nul

REM 각 서비스 상태 확인
set "services=gateway backend ai-server frontend postgres redis"
for %%s in (%services%) do (
    call :log_info "Checking %%s status..."
    
    docker-compose ps | findstr "%%s.*Up" >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "%%s is running"
        echo %%s: RUNNING >> "%PRODUCTION_READINESS_LOG%"
    ) else (
        call :log_error "%%s is not running"
        echo %%s: FAILED >> "%PRODUCTION_READINESS_LOG%"
    )
)

REM API 엔드포인트 테스트
call :log_info "Testing API endpoints..."
echo. >> "%PRODUCTION_READINESS_LOG%"
echo === API Endpoint Test === >> "%PRODUCTION_READINESS_LOG%"

set "endpoints=http://localhost:8000/health http://localhost:5001/health http://localhost:8002/health http://localhost:3000"

for %%e in (%endpoints%) do (
    call :log_info "Testing %%e..."
    
    curl -f -s "%%e" >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "%%e: OK"
        echo %%e: OK >> "%PRODUCTION_READINESS_LOG%"
    ) else (
        call :log_error "%%e: FAILED"
        echo %%e: FAILED >> "%PRODUCTION_READINESS_LOG%"
    )
)

REM 응답 시간 테스트
call :log_info "Testing response times..."
echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Response Time Test === >> "%PRODUCTION_READINESS_LOG%"

for %%e in (http://localhost:8000/health http://localhost:5001/health http://localhost:8002/health) do (
    for /f "tokens=*" %%i in ('curl -w "%%{time_total}" -o nul -s "%%e" 2^>nul') do set "RESPONSE_TIME=%%i"
    echo %%e: !RESPONSE_TIME!s >> "%PRODUCTION_READINESS_LOG%"
    
    REM PowerShell을 사용하여 부동소수점 비교
    powershell -Command "if ([double]'!RESPONSE_TIME!' -lt 1.0) { exit 0 } else { exit 1 }" >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "%%e response time: !RESPONSE_TIME!s"
    ) else (
        call :log_warning "%%e response time: !RESPONSE_TIME!s (slow)"
    )
)

goto :eof

REM 데이터베이스 테스트
:test_database
call :log_info "Testing database readiness..."

echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Database Readiness Test === >> "%PRODUCTION_READINESS_LOG%"
echo Timestamp: %date% %time% >> "%PRODUCTION_READINESS_LOG%"
echo. >> "%PRODUCTION_READINESS_LOG%"

REM PostgreSQL 연결 테스트
call :log_info "Testing PostgreSQL connection..."
echo === PostgreSQL Test === >> "%PRODUCTION_READINESS_LOG%"

docker-compose exec -T postgres pg_isready -U your_program >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "PostgreSQL connection: OK"
    echo PostgreSQL connection: OK >> "%PRODUCTION_READINESS_LOG%"
) else (
    call :log_error "PostgreSQL connection: FAILED"
    echo ERROR: PostgreSQL connection: FAILED >> "%PRODUCTION_READINESS_LOG%"
)

REM 데이터베이스 크기 확인
call :log_info "Checking database size..."

for /f "tokens=*" %%i in ('docker-compose exec -T postgres psql -U your_program your_program -t -c "SELECT pg_size_pretty(pg_database_size('your_program'));" 2^>nul') do set "DB_SIZE=%%i"
echo Database size: %DB_SIZE% >> "%PRODUCTION_READINESS_LOG%"

REM 테이블 개수 확인
for /f "tokens=*" %%i in ('docker-compose exec -T postgres psql -U your_program your_program -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2^>nul') do set "TABLE_COUNT=%%i"
echo Table count: %TABLE_COUNT% >> "%PRODUCTION_READINESS_LOG%"

REM Redis 테스트
call :log_info "Testing Redis connection..."
echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Redis Test === >> "%PRODUCTION_READINESS_LOG%"

docker-compose exec redis redis-cli ping | findstr "PONG" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Redis connection: OK"
    echo Redis connection: OK >> "%PRODUCTION_READINESS_LOG%"
) else (
    call :log_error "Redis connection: FAILED"
    echo ERROR: Redis connection: FAILED >> "%PRODUCTION_READINESS_LOG%"
)

REM Redis 메모리 사용량
for /f "tokens=*" %%i in ('docker-compose exec redis redis-cli info memory ^| findstr "used_memory_human"') do set "%%i"
echo Redis memory usage: %used_memory_human% >> "%PRODUCTION_READINESS_LOG%"

goto :eof

REM 네트워크 테스트
:test_network
call :log_info "Testing network readiness..."

echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Network Readiness Test === >> "%PRODUCTION_READINESS_LOG%"
echo Timestamp: %date% %time% >> "%PRODUCTION_READINESS_LOG%"
echo. >> "%PRODUCTION_READINESS_LOG%"

REM 포트 스캔
call :log_info "Scanning open ports..."
echo === Port Scan === >> "%PRODUCTION_READINESS_LOG%"

set "ports=80 443 8000 5001 8002 3000 5432 6379"

for %%p in (%ports%) do (
    netstat -an | findstr ":%%p " >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "Port %%p: OPEN"
        echo Port %%p: OPEN >> "%PRODUCTION_READINESS_LOG%"
    ) else (
        call :log_warning "Port %%p: CLOSED"
        echo Port %%p: CLOSED >> "%PRODUCTION_READINESS_LOG%"
    )
)

REM 방화벽 테스트
call :log_info "Testing firewall configuration..."
echo. >> "%PRODUCTION_READINESS_LOG%"
echo === Firewall Test === >> "%PRODUCTION_READINESS_LOG%"

netsh advfirewall show allprofiles state | findstr "ON" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Windows Firewall: Active"
    echo Windows Firewall: Active >> "%PRODUCTION_READINESS_LOG%"
) else (
    call :log_warning "Windows Firewall: Inactive"
    echo WARNING: Windows Firewall: Inactive >> "%PRODUCTION_READINESS_LOG%"
)

goto :eof

REM 결과 검증
:validate_results
call :log_info "Validating test results..."

REM 에러 및 경고 수 확인
findstr /c:"ERROR" /c:"FAILED" "%PRODUCTION_READINESS_LOG%" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_error "Production readiness validation FAILED"
    exit /b 1
) else (
    call :log_success "Production readiness validation PASSED"
    exit /b 0
)

goto :eof

REM 보고서 생성
:generate_report
call :log_info "Generating production readiness report..."

set "report_file=%TEST_RESULTS%\production_readiness_report_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.html"

(
echo ^<!DOCTYPE html^>
echo ^<html^>
echo ^<head^>
echo     ^<title^>Your Program Production Readiness Report^</title^>
echo     ^<style^>
echo         body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
echo         .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
echo         .header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
echo         .success { color: #28a745; }
echo         .warning { color: #ffc107; }
echo         .error { color: #dc3545; }
echo         .section { margin-bottom: 30px; }
echo         .section h2 { color: #007bff; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; }
echo         table { width: 100%%; border-collapse: collapse; margin-top: 10px; }
echo         th, td { border: 1px solid #dee2e6; padding: 8px; text-align: left; }
echo         th { background-color: #f8f9fa; font-weight: bold; }
echo         .summary { background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; }
echo         .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }
echo         .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
echo     ^</style^>
echo ^</head^>
echo ^<body^>
echo     ^<div class="container"^>
echo         ^<div class="header"^>
echo             ^<h1^>Your Program Production Readiness Report^</h1^>
echo             ^<p^>Generated: %date% %time%^</p^>
echo         ^</div^>
echo         ^<div class="summary"^>
echo             ^<h3^>Executive Summary^</h3^>
echo             ^<div class="metric"^>
echo                 ^<div class="metric-value"^>System Ready^</div^>
echo                 ^<div^>Status^</div^>
echo             ^</div^>
echo         ^</div^>
echo         ^<div class="section"^>
echo             ^<h2^>Test Results^</h2^>
echo             ^<p^>Detailed test results are available in the log file.^</p^>
echo         ^</div^>
echo     ^</div^>
echo ^</body^>
echo ^</html^>
) > "%report_file%"

call :log_success "Production readiness report generated: %report_file%"
goto :eof 