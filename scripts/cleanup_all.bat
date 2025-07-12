@echo off
REM Your Program 전체 프로젝트 정리 스크립트 (Windows)
REM 사용법: scripts\cleanup_all.bat [type]
REM type: all, cache, build, test, node_modules, python, docker (기본값: all)

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

REM 정리 타입 설정
set "CLEANUP_TYPE=%~1"
if "%CLEANUP_TYPE%"=="" set "CLEANUP_TYPE=all"

REM 프로젝트 루트 디렉토리
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

call :log_info "Your Program 전체 프로젝트 정리 시작"
call :log_info "정리 타입: %CLEANUP_TYPE%"
call :log_info "프로젝트 루트: %PROJECT_ROOT%"

REM 디스크 사용량 확인
call :log_info "정리 전 디스크 사용량:"
dir /s | find "File(s)"

REM 정리 함수들
:clean_cache
call :log_info "캐시 파일 정리 중..."
if exist ".next" rmdir /s /q ".next"
if exist ".cache" rmdir /s /q ".cache"
if exist ".parcel-cache" rmdir /s /q ".parcel-cache"
if exist ".eslintcache" del /q ".eslintcache"
if exist ".stylelintcache" del /q ".stylelintcache"
if exist "coverage" rmdir /s /q "coverage"
if exist ".nyc_output" rmdir /s /q ".nyc_output"
if exist ".jest" rmdir /s /q ".jest"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
if exist ".mypy_cache" rmdir /s /q ".mypy_cache"
if exist ".coverage" del /q ".coverage"
if exist "htmlcov" rmdir /s /q "htmlcov"
if exist ".tox" rmdir /s /q ".tox"
if exist ".venv" rmdir /s /q ".venv"
if exist "venv" rmdir /s /q "venv"
if exist "env" rmdir /s /q "env"
if exist ".env" del /q ".env"
if exist ".env.local" del /q ".env.local"
if exist ".env.development.local" del /q ".env.development.local"
if exist ".env.test.local" del /q ".env.test.local"
if exist ".env.production.local" del /q ".env.production.local"
call :log_success "캐시 파일 정리 완료"
goto :eof

:clean_build
call :log_info "빌드 파일 정리 중...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "out" rmdir /s /q "out"
if exist ".next" rmdir /s /q ".next"
if exist "target" rmdir /s /q "target"
call :log_success "빌드 파일 정리 완료"
goto :eof

:clean_test
call :log_info "테스트 파일 정리 중...
if exist "coverage" rmdir /s /q "coverage"
if exist ".nyc_output" rmdir /s /q ".nyc_output"
if exist ".jest" rmdir /s /q ".jest"
if exist "test-results" rmdir /s /q "test-results"
if exist "playwright-report" rmdir /s /q "playwright-report"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
if exist "htmlcov" rmdir /s /q "htmlcov"
call :log_success "테스트 파일 정리 완료"
goto :eof

:clean_node_modules
call :log_info "Node.js 관련 파일 정리 중...
if exist "node_modules" rmdir /s /q "node_modules"
if exist "package-lock.json" del /q "package-lock.json"
if exist "yarn.lock" del /q "yarn.lock"
if exist "pnpm-lock.yaml" del /q "pnpm-lock.yaml"
if exist "bun.lockb" del /q "bun.lockb"
call :log_success "Node.js 관련 파일 정리 완료"
goto :eof

:clean_python
call :log_info "Python 관련 파일 정리 중...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
if exist ".mypy_cache" rmdir /s /q ".mypy_cache"
if exist ".coverage" del /q ".coverage"
if exist "htmlcov" rmdir /s /q "htmlcov"
if exist ".tox" rmdir /s /q ".tox"
call :log_success "Python 관련 파일 정리 완료"
goto :eof

:clean_docker
call :log_info "Docker 관련 파일 정리 중...
if exist "Dockerfile.dev" del /q "Dockerfile.dev"
if exist "docker-compose.override.yml" del /q "docker-compose.override.yml"
if exist "docker-compose.dev.yml" del /q "docker-compose.dev.yml"
if exist "docker-compose.test.yml" del /q "docker-compose.test.yml"
if exist ".dockerignore.dev" del /q ".dockerignore.dev"
call :log_success "Docker 관련 파일 정리 완료"
goto :eof

:clean_temp_files
call :log_info "임시 파일 정리 중...
for /r %%f in (*.log) do del /q "%%f"
for /r %%f in (*.tmp) do del /q "%%f"
for /r %%f in (*.temp) do del /q "%%f"
for /r %%f in (.DS_Store) do del /q "%%f"
for /r %%f in (Thumbs.db) do del /q "%%f"
for /r %%f in (*.swp) do del /q "%%f"
for /r %%f in (*.swo) do del /q "%%f"
for /r %%f in (*~) do del /q "%%f"
for /r %%f in (*.bak) do del /q "%%f"
for /r %%f in (*.backup) do del /q "%%f"
for /r %%f in (*.orig) do del /q "%%f"
for /r %%f in (*.rej) do del /q "%%f"
call :log_success "임시 파일 정리 완료"
goto :eof

:clean_backups
call :log_info "백업 파일 정리 중...
REM Windows에서는 날짜 기반 삭제가 복잡하므로 모든 백업 삭제
for /d %%d in (backup_*) do rmdir /s /q "%%d"
for /r %%f in (*.backup) do del /q "%%f"
call :log_success "백업 파일 정리 완료"
goto :eof

:clean_logs
call :log_info "로그 파일 정리 중...
for /r %%f in (*.log) do del /q "%%f"
if exist "logs" rmdir /s /q "logs"
call :log_success "로그 파일 정리 완료"
goto :eof

REM 특정 디렉토리 정리
:clean_directory
set "dir=%~1"
set "dir_type=%~2"

if exist "%dir%" (
    call :log_info "%dir_type% 디렉토리 정리 중: %dir%"
    cd /d "%dir%"
    
    if "%CLEANUP_TYPE%"=="cache" (
        call :clean_cache
        call :clean_temp_files
    ) else if "%CLEANUP_TYPE%"=="build" (
        call :clean_build
        call :clean_temp_files
    ) else if "%CLEANUP_TYPE%"=="test" (
        call :clean_test
        call :clean_temp_files
    ) else if "%CLEANUP_TYPE%"=="node_modules" (
        call :clean_node_modules
    ) else if "%CLEANUP_TYPE%"=="python" (
        call :clean_python
        call :clean_temp_files
    ) else if "%CLEANUP_TYPE%"=="docker" (
        call :clean_docker
    ) else if "%CLEANUP_TYPE%"=="all" (
        call :clean_cache
        call :clean_build
        call :clean_test
        call :clean_temp_files
        call :clean_backups
        call :clean_logs
    )
    
    cd /d "%PROJECT_ROOT%"
)
goto :eof

REM 메인 정리 로직
if "%CLEANUP_TYPE%"=="cache" (
    call :clean_cache
    call :clean_temp_files
) else if "%CLEANUP_TYPE%"=="build" (
    call :clean_build
    call :clean_temp_files
) else if "%CLEANUP_TYPE%"=="test" (
    call :clean_test
    call :clean_temp_files
) else if "%CLEANUP_TYPE%"=="node_modules" (
    call :clean_node_modules
) else if "%CLEANUP_TYPE%"=="python" (
    call :clean_python
    call :clean_temp_files
) else if "%CLEANUP_TYPE%"=="docker" (
    call :clean_docker
) else if "%CLEANUP_TYPE%"=="all" (
    call :clean_cache
    call :clean_build
    call :clean_test
    call :clean_temp_files
    call :clean_backups
    call :clean_logs
) else (
    call :log_error "잘못된 정리 타입입니다. 사용법: %0 [all^|cache^|build^|test^|node_modules^|python^|docker]"
    exit /b 1
)

REM 서브 디렉토리 정리
call :log_info "서브 디렉토리 정리 중...

REM Frontend 디렉토리
call :clean_directory "frontend" "Frontend"

REM Mobile 앱 디렉토리
call :clean_directory "mobile_app" "Mobile App"

REM AI 모듈 디렉토리
call :clean_directory "ai_modules" "AI Modules"

REM 백업 디렉토리들
for /d %%d in (backup_*) do (
    call :clean_directory "%%d" "Backup"
)

REM 디스크 사용량 확인
call :log_info "정리 후 디스크 사용량:"
dir /s | find "File(s)"

call :log_success "전체 프로젝트 정리 완료!"

REM 다음 단계 안내
if "%CLEANUP_TYPE%"=="node_modules" (
    call :log_info "다음 단계:"
    call :log_info "  Frontend: cd frontend ^&^& npm install"
    call :log_info "  Mobile: cd mobile_app ^&^& npm install"
) else if "%CLEANUP_TYPE%"=="python" (
    call :log_info "다음 단계:"
    call :log_info "  AI 모듈: pip install -r ai_requirements.txt"
) else if "%CLEANUP_TYPE%"=="all" (
    call :log_info "다음 단계:"
    call :log_info "  Frontend: cd frontend ^&^& npm install"
    call :log_info "  Mobile: cd mobile_app ^&^& npm install"
    call :log_info "  AI 모듈: pip install -r ai_requirements.txt"
    call :log_info "  전체 실행: scripts\start_all.bat"
)

pause 
