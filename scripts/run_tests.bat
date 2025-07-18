@echo off
echo ========================================
echo 테스트 실행 스크립트 시작
echo ========================================

:: 현재 디렉토리를 프로젝트 루트로 설정
cd /d "%~dp0.."

:: 가상환경 경로 설정 (venv 폴더가 있다고 가정)
set VENV_PATH=venv

:: 가상환경이 존재하는지 확인
if not exist "%VENV_PATH%" (
    echo 가상환경을 찾을 수 없습니다: %VENV_PATH%
    echo 가상환경을 생성하시겠습니까? (y/n)
    set /p create_venv=
    if /i "%create_venv%"=="y" (
        echo 가상환경을 생성합니다...
        python -m venv %VENV_PATH%
        if errorlevel 1 (
            echo 가상환경 생성에 실패했습니다.
            pause
            exit /b 1
        )
    ) else (
        echo 스크립트를 종료합니다.
        pause
        exit /b 1
    )
)

:: 가상환경 활성화
echo 가상환경을 활성화합니다...
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)

:: 필요한 패키지 설치 확인
echo 필요한 패키지를 확인합니다...
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo pytest가 설치되지 않았습니다. 설치합니다...
    pip install pytest
    if errorlevel 1 (
        echo pytest 설치에 실패했습니다.
        pause
        exit /b 1
    )
)

:: 환경 변수 설정 (필요한 경우)
set FLASK_ENV=testing
set PYTHONPATH=%CD%

:: 테스트 실행
echo ========================================
echo pytest를 실행합니다...
echo ========================================

:: 기본 테스트 실행
pytest tests/ -v

:: 특정 테스트 파일만 실행하려면 아래 주석을 해제하고 사용
:: pytest tests/test_specific_file.py -v

:: 특정 테스트 함수만 실행하려면 아래 주석을 해제하고 사용
:: pytest tests/ -k "test_function_name" -v

:: 테스트 결과 확인
if errorlevel 1 (
    echo ========================================
    echo 일부 테스트가 실패했습니다.
    echo ========================================
) else (
    echo ========================================
    echo 모든 테스트가 성공했습니다!
    echo ========================================
)

:: 가상환경 비활성화
echo 가상환경을 비활성화합니다...
deactivate

echo ========================================
echo 테스트 실행 완료
echo ========================================
pause 