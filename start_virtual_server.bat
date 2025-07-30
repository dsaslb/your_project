@echo off
echo ================================
echo 🌐 가상 서버 모드 시작
echo ================================

REM 가상 환경 활성화 (존재하는 경우)
if exist .venv\Scripts\activate.bat (
    echo 🔧 가상 환경 활성화...
    call .venv\Scripts\activate.bat
)

REM 필요한 디렉토리 생성
if not exist instance mkdir instance
if not exist logs mkdir logs

echo 📦 필요한 패키지 설치 확인...
pip install -q python-dotenv flask flask-cors flask-socketio

echo 🚀 백엔드 서버 시작 중...
python start_virtual_server.py

pause