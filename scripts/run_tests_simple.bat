@echo off
echo 테스트 실행 중...

:: 프로젝트 루트로 이동
cd /d "%~dp0.."

:: 가상환경 활성화
call venv\Scripts\activate.bat

:: 환경 변수 설정
set FLASK_ENV=testing
set PYTHONPATH=%CD%

:: pytest 실행
pytest tests/ -v

:: 가상환경 비활성화
deactivate

echo 테스트 완료!
pause 