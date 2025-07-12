@echo off
REM Your Program 전체 프로젝트 시작 스크립트 (Windows)
REM 사용법: scripts\start_all.bat [environment]
REM environment: dev, staging, prod (기본값: dev)

setlocal enabledelayedexpansion

REM 색상 정의 (Windows에서는 제한적)
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

REM 환경 변수 설정
set "ENVIRONMENT=%~1"
if "%ENVIRONMENT%"=="" set "ENVIRONMENT=dev"

REM 프로젝트 루트 디렉토리
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM 타임스탬프
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "TIMESTAMP=%dt:~0,8%_%dt:~8,6%"

REM 환경별 설정
if "%ENVIRONMENT%"=="dev" (
    set "NODE_ENV=development"
    set "FLASK_ENV=development"
    set "API_URL=http://localhost:5001"
    set "WS_URL=ws://localhost:5001"
    set "FRONTEND_PORT=3000"
    set "BACKEND_PORT=5001"
    set "AI_PORT=8002"
    set "MOBILE_PORT=19000"
) else if "%ENVIRONMENT%"=="staging" (
    set "NODE_ENV=staging"
    set "FLASK_ENV=production"
    set "API_URL=https://staging-api.yourprogram.com"
    set "WS_URL=wss://staging-api.yourprogram.com"
    set "FRONTEND_PORT=3000"
    set "BACKEND_PORT=5001"
    set "AI_PORT=8002"
    set "MOBILE_PORT=19000"
) else if "%ENVIRONMENT%"=="prod" (
    set "NODE_ENV=production"
    set "FLASK_ENV=production"
    set "API_URL=https://api.yourprogram.com"
    set "WS_URL=wss://api.yourprogram.com"
    set "FRONTEND_PORT=3000"
    set "BACKEND_PORT=5001"
    set "AI_PORT=8002"
    set "MOBILE_PORT=19000"
) else (
    call :log_error "잘못된 환경입니다. 사용법: %0 [dev^|staging^|prod]"
    exit /b 1
)

REM PID 파일 관리
set "PID_DIR=%PROJECT_ROOT%\pids"
if not exist "%PID_DIR%" mkdir "%PID_DIR%"

REM 프로세스 종료 함수
:cleanup
call :log_info "프로세스 정리 중...
for %%f in ("%PID_DIR%\*.pid") do (
    if exist "%%f" (
        set /p pid=<"%%f"
        taskkill /PID !pid! /F >nul 2>&1
        del "%%f"
    )
)
call :log_success "프로세스 정리 완료"
goto :eof

REM 의존성 확인
:check_dependencies
call :log_info "의존성 확인 중...

REM Node.js 확인
node --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Node.js가 설치되지 않았습니다."
    exit /b 1
)

REM npm 확인
npm --version >nul 2>&1
if errorlevel 1 (
    call :log_error "npm이 설치되지 않았습니다."
    exit /b 1
)

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        call :log_error "Python이 설치되지 않았습니다."
        exit /b 1
    )
)

call :log_success "의존성 확인 완료"
goto :eof

REM 포트 확인
:check_ports
call :log_info "포트 사용량 확인 중...

for %%p in (%FRONTEND_PORT% %BACKEND_PORT% %AI_PORT% %MOBILE_PORT%) do (
    netstat -an | find "%%p" | find "LISTENING" >nul
    if not errorlevel 1 (
        call :log_warning "포트 %%p가 이미 사용 중입니다."
        set /p "continue=계속 진행하시겠습니까? (y/N): "
        if /i not "!continue!"=="y" exit /b 1
    )
)

call :log_success "포트 확인 완료"
goto :eof

REM 환경 변수 파일 생성
:setup_environment
call :log_info "환경 변수 설정 중...

REM Frontend 환경 변수
(
echo NEXT_PUBLIC_API_URL=%API_URL%
echo NEXT_PUBLIC_WS_URL=%WS_URL%
echo NODE_ENV=%NODE_ENV%
) > "%PROJECT_ROOT%\frontend\.env.local"

REM Backend 환경 변수
(
echo FLASK_ENV=%FLASK_ENV%
echo DATABASE_URL=postgresql://user:password@localhost/your_program
echo SECRET_KEY=your-secret-key-here
echo API_URL=%API_URL%
echo WS_URL=%WS_URL%
echo AI_SERVER_URL=http://localhost:%AI_PORT%
) > "%PROJECT_ROOT%\.env"

REM AI 서버 환경 변수
(
echo DATABASE_URL=postgresql://user:password@localhost/your_program_ai
echo REDIS_URL=redis://localhost:6379
echo SECRET_KEY=your-ai-secret-key-here
echo MODEL_PATH=%PROJECT_ROOT%\models
) > "%PROJECT_ROOT%\.env.ai"

call :log_success "환경 변수 설정 완료"
goto :eof

REM 백엔드 시작
:start_backend
call :log_info "백엔드 서버 시작 중...

cd /d "%PROJECT_ROOT%"

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 의존성 설치 확인
if not exist "venv" if not exist ".venv" (
    call :log_info "Python 가상환경 생성 중...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

REM 데이터베이스 마이그레이션
call :log_info "데이터베이스 마이그레이션 중...
flask db upgrade >nul 2>&1 || call :log_warning "마이그레이션 실패 (무시됨)"

REM 백엔드 서버 시작
start /B python app.py > "%PROJECT_ROOT%\logs\backend.log" 2>&1
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| find "python.exe"') do (
    echo %%a > "%PID_DIR%\backend.pid"
    goto :backend_started
)
:backend_started

call :log_success "백엔드 서버 시작됨 (PID: %PID_DIR%\backend.pid)"
goto :eof

REM AI 서버 시작
:start_ai_server
call :log_info "AI 서버 시작 중...

cd /d "%PROJECT_ROOT%"

REM AI 의존성 설치 확인
if not exist "ai_requirements_installed" (
    call :log_info "AI 의존성 설치 중...
    pip install -r ai_requirements.txt
    echo. > ai_requirements_installed
)

REM AI 서버 시작
start /B python ai_server.py > "%PROJECT_ROOT%\logs\ai_server.log" 2>&1
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| find "python.exe"') do (
    echo %%a > "%PID_DIR%\ai_server.pid"
    goto :ai_started
)
:ai_started

call :log_success "AI 서버 시작됨 (PID: %PID_DIR%\ai_server.pid)"
goto :eof

REM 프론트엔드 시작
:start_frontend
call :log_info "프론트엔드 서버 시작 중...

cd /d "%PROJECT_ROOT%\frontend"

REM 의존성 설치 확인
if not exist "node_modules" (
    call :log_info "프론트엔드 의존성 설치 중...
    npm install
)

REM 프론트엔드 서버 시작
start /B npm run dev > "%PROJECT_ROOT%\logs\frontend.log" 2>&1
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" /FO CSV ^| find "node.exe"') do (
    echo %%a > "%PID_DIR%\frontend.pid"
    goto :frontend_started
)
:frontend_started

call :log_success "프론트엔드 서버 시작됨 (PID: %PID_DIR%\frontend.pid)"
goto :eof

REM 모바일 앱 시작
:start_mobile
call :log_info "모바일 앱 개발 서버 시작 중...

cd /d "%PROJECT_ROOT%\mobile_app"

REM 의존성 설치 확인
if not exist "node_modules" (
    call :log_info "모바일 앱 의존성 설치 중...
    npm install
)

REM Expo 서버 시작
start /B npx expo start --port %MOBILE_PORT% > "%PROJECT_ROOT%\logs\mobile.log" 2>&1
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" /FO CSV ^| find "node.exe"') do (
    echo %%a > "%PID_DIR%\mobile.pid"
    goto :mobile_started
)
:mobile_started

call :log_success "모바일 앱 서버 시작됨 (PID: %PID_DIR%\mobile.pid)"
goto :eof

REM 서비스 상태 확인
:check_services
call :log_info "서비스 상태 확인 중...

REM 서비스 응답 대기
call :log_info "백엔드 서비스 응답 대기 중...
for /l %%i in (1,1,30) do (
    curl -s "http://localhost:%BACKEND_PORT%/health" >nul 2>&1
    if not errorlevel 1 (
        call :log_success "백엔드 서비스가 정상적으로 응답합니다."
        goto :backend_ok
    )
    timeout /t 2 /nobreak >nul
)
call :log_warning "백엔드 서비스 응답 없음 (무시됨)"
:backend_ok

call :log_info "AI 서버 응답 대기 중...
for /l %%i in (1,1,30) do (
    curl -s "http://localhost:%AI_PORT%/health" >nul 2>&1
    if not errorlevel 1 (
        call :log_success "AI 서버가 정상적으로 응답합니다."
        goto :ai_ok
    )
    timeout /t 2 /nobreak >nul
)
call :log_warning "AI 서버 응답 없음 (무시됨)"
:ai_ok

call :log_info "프론트엔드 서비스 응답 대기 중...
for /l %%i in (1,1,30) do (
    curl -s "http://localhost:%FRONTEND_PORT%" >nul 2>&1
    if not errorlevel 1 (
        call :log_success "프론트엔드 서비스가 정상적으로 응답합니다."
        goto :frontend_ok
    )
    timeout /t 2 /nobreak >nul
)
call :log_warning "프론트엔드 서비스 응답 없음 (무시됨)"
:frontend_ok

goto :eof

REM 로그 디렉토리 생성
:setup_logs
call :log_info "로그 디렉토리 설정 중...

if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"

REM 로그 파일 초기화
echo. > "%PROJECT_ROOT%\logs\backend.log"
echo. > "%PROJECT_ROOT%\logs\ai_server.log"
echo. > "%PROJECT_ROOT%\logs\frontend.log"
echo. > "%PROJECT_ROOT%\logs\mobile.log"

call :log_success "로그 디렉토리 설정 완료"
goto :eof

REM 메인 시작 로직
call :log_info "Your Program 전체 프로젝트 시작"
call :log_info "환경: %ENVIRONMENT%"
call :log_info "프로젝트 루트: %PROJECT_ROOT%"
call :log_info "타임스탬프: %TIMESTAMP%"

REM 초기 설정
call :check_dependencies
call :check_ports
call :setup_logs
call :setup_environment

REM 서비스 시작
call :start_backend
timeout /t 5 /nobreak >nul

call :start_ai_server
timeout /t 3 /nobreak >nul

call :start_frontend
timeout /t 3 /nobreak >nul

call :start_mobile
timeout /t 3 /nobreak >nul

REM 서비스 상태 확인
call :check_services

REM 시작 완료 메시지
call :log_success "모든 서비스가 시작되었습니다!"
echo.
echo === Your Program 서비스 정보 ===
echo 환경: %ENVIRONMENT%
echo 프론트엔드: http://localhost:%FRONTEND_PORT%
echo 백엔드 API: http://localhost:%BACKEND_PORT%
echo AI 서버: http://localhost:%AI_PORT%
echo 모바일 앱: http://localhost:%MOBILE_PORT%
echo 로그 디렉토리: %PROJECT_ROOT%\logs
echo PID 파일: %PID_DIR%
echo.
echo 서비스 종료: Ctrl+C
echo 로그 확인: type %PROJECT_ROOT%\logs\*.log
echo.

REM 프로세스 모니터링
:monitor_loop
timeout /t 10 /nobreak >nul

REM 프로세스 상태 확인
for %%f in ("%PID_DIR%\*.pid") do (
    if exist "%%f" (
        set /p pid=<"%%f"
        tasklist /PID !pid! >nul 2>&1
        if errorlevel 1 (
            call :log_error "!pid! 프로세스가 종료되었습니다."
            del "%%f"
        )
    )
)

goto :monitor_loop 
