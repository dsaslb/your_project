@echo off
echo Flask 앱을 백그라운드에서 실행합니다...
echo.

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM Flask 앱 실행 (백그라운드)
start /B python app.py

echo.
echo Flask 앱이 백그라운드에서 실행 중입니다.
echo 브라우저에서 http://127.0.0.1:5000 으로 접속하세요.
echo.
echo 앱을 중지하려면 작업 관리자에서 python.exe 프로세스를 종료하세요.
echo.
pause 