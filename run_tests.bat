@echo off
REM ✅ 현재 폴더로 이동
cd /d %~dp0

REM ✅ PowerShell 프로필 오류 방지
if exist %USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1 (
    echo. > %USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
    echo [INFO] PowerShell 프로필 초기화 완료
)

REM ✅ 가상환경 활성화
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo [INFO] 가상환경 활성화됨
) else (
    echo [ERROR] .venv 가상환경을 찾을 수 없습니다.
    pause
    exit /b
)

REM ✅ 패키지 설치 (처음 한 번만 실행됨)
pip install -r requirements.txt

REM ✅ pytest 실행
pytest --maxfail=10 --disable-warnings -q

echo.
echo [INFO] 모든 작업이 완료되었습니다. 결과를 확인하세요.
pause 