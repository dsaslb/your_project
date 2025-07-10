@echo off
setlocal enabledelayedexpansion

REM Your Program 자동 스케일링 스크립트 (Windows)
REM 사용법: scripts\auto-scale.bat [service] [action]
REM service: backend, ai-server, frontend (기본값: all)
REM action: scale-up, scale-down, check (기본값: check)

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
set "SERVICE=%~1"
if "%SERVICE%"=="" set "SERVICE=all"

set "ACTION=%~2"
if "%ACTION%"=="" set "ACTION=check"

set "PROJECT_ROOT=%~dp0.."

REM 임계값 설정
set "CPU_THRESHOLD=80"
set "MEMORY_THRESHOLD=85"
set "REQUEST_THRESHOLD=1000"
set "ERROR_RATE_THRESHOLD=5"

REM 현재 시간
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "TIMESTAMP=%dt:~0,4%-%dt:~4,2%-%dt:~6,2% %dt:~8,2%:%dt:~10,2%:%dt:~12,2%"

REM 메트릭 수집 함수
:get_cpu_usage
set "service=%~1"
for /f "tokens=*" %%i in ('curl -s "http://localhost:9090/api/v1/query?query=100%%20-%%20(avg%%20by%%20(instance)%%20(irate(node_cpu_seconds_total{mode=\"idle\",job=\"%service%\"}[5m]))%%20*%%20100)" ^| jq -r ".data.result[0].value[1] // \"0\""') do set "cpu_usage=%%i"
goto :eof

:get_memory_usage
set "service=%~1"
for /f "tokens=*" %%i in ('curl -s "http://localhost:9090/api/v1/query?query=(node_memory_MemTotal_bytes%%20-%%20node_memory_MemAvailable_bytes)%%20/%%20node_memory_MemTotal_bytes%%20*%%20100" ^| jq -r ".data.result[0].value[1] // \"0\""') do set "memory_usage=%%i"
goto :eof

:get_request_rate
set "service=%~1"
for /f "tokens=*" %%i in ('curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{job=\"%service%\"}[5m])" ^| jq -r ".data.result[0].value[1] // \"0\""') do set "request_rate=%%i"
goto :eof

:get_error_rate
set "service=%~1"
for /f "tokens=*" %%i in ('curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{job=\"%service%\",status=~\"5..\"}[5m])%%20/%%20rate(http_requests_total{job=\"%service%\"}[5m])%%20*%%20100" ^| jq -r ".data.result[0].value[1] // \"0\""') do set "error_rate=%%i"
goto :eof

:get_current_replicas
set "service=%~1"
for /f "tokens=*" %%i in ('docker-compose ps %service% ^| find /c "Up"') do set "current_replicas=%%i"
if "%current_replicas%"=="" set "current_replicas=0"
goto :eof

REM 스케일링 함수
:scale_service
set "service=%~1"
set "direction=%~2"

call :get_current_replicas %service%
set "current_replicas=%current_replicas%"

if "%direction%"=="up" (
    set /a "new_replicas=%current_replicas% + 1"
    call :log_info "Scaling %service% up from %current_replicas% to %new_replicas% replicas"
    
    REM Docker Compose 스케일링
    docker-compose up -d --scale %service%=%new_replicas%
    
    REM 로드 밸런서 업데이트
    call :update_load_balancer %service% %new_replicas%
    
) else if "%direction%"=="down" (
    if %current_replicas% gtr 1 (
        set /a "new_replicas=%current_replicas% - 1"
        call :log_info "Scaling %service% down from %current_replicas% to %new_replicas% replicas"
        
        REM Docker Compose 스케일링
        docker-compose up -d --scale %service%=%new_replicas%
        
        REM 로드 밸런서 업데이트
        call :update_load_balancer %service% %new_replicas%
    ) else (
        call :log_warning "Cannot scale down %service%: minimum replicas reached"
    )
)
goto :eof

REM 로드 밸런서 업데이트
:update_load_balancer
set "service=%~1"
set "replicas=%~2"

REM Nginx 설정 업데이트 (Windows에서는 sed 대신 PowerShell 사용)
powershell -Command "(Get-Content '%PROJECT_ROOT%\nginx\nginx.conf') -replace 'server %service%:[0-9]*', 'server %service%:%replicas%' | Set-Content '%PROJECT_ROOT%\nginx\nginx.conf'"

REM Nginx 재로드
docker-compose exec nginx nginx -s reload

call :log_success "Load balancer updated for %service% (%replicas% replicas)"
goto :eof

REM 헬스체크 함수
:check_service_health
set "service=%~1"
set "health_url="

if "%service%"=="gateway" set "health_url=http://localhost:8000/health"
if "%service%"=="backend" set "health_url=http://localhost:5001/health"
if "%service%"=="ai-server" set "health_url=http://localhost:8002/health"
if "%service%"=="frontend" set "health_url=http://localhost:3000"

if defined health_url (
    for /f "tokens=*" %%i in ('curl -s -o nul -w "%%{http_code}" %health_url%') do set "response=%%i"
    if "%response%"=="200" (
        exit /b 0
    ) else (
        exit /b 1
    )
) else (
    exit /b 1
)
goto :eof

REM 메트릭 모니터링 함수
:monitor_metrics
set "service=%~1"

call :log_info "Monitoring metrics for %service%..."

call :get_cpu_usage %service%
call :get_memory_usage %service%
call :get_request_rate %service%
call :get_error_rate %service%
call :get_current_replicas %service%

echo === %service% Metrics (%TIMESTAMP%) ===
echo CPU Usage: %cpu_usage%%%
echo Memory Usage: %memory_usage%%%
echo Request Rate: %request_rate% req/s
echo Error Rate: %error_rate%%%
echo Current Replicas: %current_replicas%

call :check_service_health %service%
if %errorlevel% equ 0 (
    echo Health Status: Healthy
) else (
    echo Health Status: Unhealthy
)
echo.

REM 스케일링 결정
set "should_scale_up=false"
set "should_scale_down=false"

REM 스케일 업 조건 (간단한 비교)
if %cpu_usage% gtr %CPU_THRESHOLD% set "should_scale_up=true"
if %memory_usage% gtr %MEMORY_THRESHOLD% set "should_scale_up=true"
if %request_rate% gtr %REQUEST_THRESHOLD% set "should_scale_up=true"

REM 스케일 다운 조건
if %cpu_usage% lss 30 if %memory_usage% lss 40 if %request_rate% lss 100 if %current_replicas% gtr 1 set "should_scale_down=true"

REM 스케일링 실행
if "%should_scale_up%"=="true" (
    call :log_warning "High resource usage detected for %service%"
    call :scale_service %service% up
) else if "%should_scale_down%"=="true" (
    call :log_info "Low resource usage detected for %service%"
    call :scale_service %service% down
) else (
    call :log_success "%service% is running optimally"
)
goto :eof

REM 전체 서비스 모니터링
:monitor_all_services
call :log_info "Starting auto-scaling monitoring..."

set "services=gateway backend ai-server frontend"

for %%s in (%services%) do (
    call :monitor_metrics %%s
    timeout /t 5 /nobreak >nul
)
goto :eof

REM 특정 서비스 스케일링
:scale_specific_service
set "service=%~1"
set "action=%~2"

if "%action%"=="scale-up" (
    call :scale_service %service% up
) else if "%action%"=="scale-down" (
    call :scale_service %service% down
) else if "%action%"=="check" (
    call :monitor_metrics %service%
) else (
    call :log_error "Invalid action: %action%"
    exit /b 1
)
goto :eof

REM 메인 로직
:main
call :log_info "Your Program Auto-Scaling System"
call :log_info "Service: %SERVICE%"
call :log_info "Action: %ACTION%"
call :log_info "Timestamp: %TIMESTAMP%"

REM Prometheus 연결 확인
curl -s http://localhost:9090/api/v1/query >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Prometheus is not accessible. Please ensure monitoring is running."
    exit /b 1
)

if "%SERVICE%"=="all" (
    if "%ACTION%"=="check" (
        call :monitor_all_services
    ) else (
        call :log_error "Action '%ACTION%' is not supported for all services"
        exit /b 1
    )
) else if "%SERVICE%"=="gateway" (
    call :scale_specific_service %SERVICE% %ACTION%
) else if "%SERVICE%"=="backend" (
    call :scale_specific_service %SERVICE% %ACTION%
) else if "%SERVICE%"=="ai-server" (
    call :scale_specific_service %SERVICE% %ACTION%
) else if "%SERVICE%"=="frontend" (
    call :scale_specific_service %SERVICE% %ACTION%
) else (
    call :log_error "Invalid service: %SERVICE%"
    call :log_info "Valid services: gateway, backend, ai-server, frontend, all"
    exit /b 1
)

call :log_success "Auto-scaling operation completed"
goto :eof

REM 스크립트 실행
call :main %* 