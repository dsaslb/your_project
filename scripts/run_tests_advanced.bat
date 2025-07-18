@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 고급 테스트 실행 스크립트
echo ========================================

:: 현재 디렉토리를 프로젝트 루트로 설정
cd /d "%~dp0.."

:: 설정 변수
set VENV_PATH=venv
set TEST_DIR=tests
set COVERAGE_REPORT=htmlcov

:: 사용법 표시
if "%1"=="help" (
    echo 사용법:
    echo   run_tests_advanced.bat [옵션]
    echo.
    echo 옵션:
    echo   help          - 이 도움말 표시
    echo   coverage      - 커버리지 리포트 생성
    echo   fast          - 빠른 테스트 (실패한 테스트만)
    echo   specific      - 특정 테스트 파일 실행
    echo   verbose       - 상세한 출력
    echo   parallel      - 병렬 테스트 실행
    echo.
    pause
    exit /b 0
)

:: 가상환경 확인 및 활성화
if not exist "%VENV_PATH%" (
    echo [오류] 가상환경을 찾을 수 없습니다: %VENV_PATH%
    echo 가상환경을 생성하시겠습니까? (y/n)
    set /p create_venv=
    if /i "!create_venv!"=="y" (
        echo 가상환경을 생성합니다...
        python -m venv %VENV_PATH%
        if errorlevel 1 (
            echo [오류] 가상환경 생성 실패
            pause
            exit /b 1
        )
    ) else (
        echo 스크립트를 종료합니다.
        pause
        exit /b 1
    )
)

echo 가상환경을 활성화합니다...
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo [오류] 가상환경 활성화 실패
    pause
    exit /b 1
)

:: 필요한 패키지 설치
echo 필요한 패키지를 확인합니다...
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo pytest를 설치합니다...
    pip install pytest
)

:: 커버리지 옵션 확인
if "%1"=="coverage" (
    python -c "import coverage" 2>nul
    if errorlevel 1 (
        echo pytest-cov를 설치합니다...
        pip install pytest-cov
    )
)

:: 병렬 테스트 옵션 확인
if "%1"=="parallel" (
    python -c "import xdist" 2>nul
    if errorlevel 1 (
        echo pytest-xdist를 설치합니다...
        pip install pytest-xdist
    )
)

:: 환경 변수 설정
set FLASK_ENV=testing
set PYTHONPATH=%CD%
set PYTHONDONTWRITEBYTECODE=1

:: 테스트 실행 옵션 설정
set PYTEST_ARGS=%TEST_DIR%

:: 옵션에 따른 인수 설정
if "%1"=="coverage" (
    set PYTEST_ARGS=%TEST_DIR% --cov=. --cov-report=html --cov-report=term-missing
    echo 커버리지 리포트를 생성합니다...
) else if "%1"=="fast" (
    set PYTEST_ARGS=%TEST_DIR% --lf -v
    echo 실패한 테스트만 실행합니다...
) else if "%1"=="specific" (
    echo 실행할 테스트 파일을 입력하세요 (예: test_auth.py):
    set /p test_file=
    set PYTEST_ARGS=%TEST_DIR%\!test_file! -v
) else if "%1"=="verbose" (
    set PYTEST_ARGS=%TEST_DIR% -v -s --tb=long
    echo 상세한 출력으로 테스트를 실행합니다...
) else if "%1"=="parallel" (
    set PYTEST_ARGS=%TEST_DIR% -n auto -v
    echo 병렬로 테스트를 실행합니다...
) else (
    set PYTEST_ARGS=%TEST_DIR% -v
    echo 기본 테스트를 실행합니다...
)

:: 테스트 실행
echo ========================================
echo pytest 실행: !PYTEST_ARGS!
echo ========================================

pytest !PYTEST_ARGS!

:: 결과 확인
if errorlevel 1 (
    echo ========================================
    echo [경고] 일부 테스트가 실패했습니다.
    echo ========================================
    set TEST_RESULT=FAILED
) else (
    echo ========================================
    echo [성공] 모든 테스트가 통과했습니다!
    echo ========================================
    set TEST_RESULT=PASSED
)

:: 커버리지 리포트 열기 (커버리지 옵션 사용 시)
if "%1"=="coverage" (
    if exist "%COVERAGE_REPORT%\index.html" (
        echo 커버리지 리포트를 엽니다...
        start "" "%COVERAGE_REPORT%\index.html"
    )
)

:: 가상환경 비활성화
echo 가상환경을 비활성화합니다...
deactivate

:: 최종 결과 표시
echo ========================================
echo 테스트 결과: !TEST_RESULT!
echo ========================================

:: 로그 파일 생성 (선택사항)
echo %date% %time% - Test Result: !TEST_RESULT! >> test_log.txt

pause 