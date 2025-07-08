@echo off
echo ========================================
echo    레스토랑 관리 시스템 서버 시작
echo ========================================
echo.

echo 1. 메인 Flask 서버 시작...
start "Main Server" cmd /k "venv\Scripts\activate && python app.py"

echo 2. AI 예측 서버 시작...
start "AI Server" cmd /k "ai_env\Scripts\activate && python ai_server.py"

echo.
echo 서버가 시작되었습니다!
echo - 메인 서버: http://localhost:5000
echo - AI 서버: http://localhost:8501
echo.
echo 서버를 종료하려면 각 창을 닫으세요.
pause 