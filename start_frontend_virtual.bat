@echo off
echo ================================
echo 🎨 가상 서버용 프론트엔드 시작
echo ================================

REM 프론트엔드 디렉토리로 이동
cd frontend

echo 📦 의존성 패키지 설치 확인...
npm install

echo 🚀 프론트엔드 서버 시작 중...
echo    백엔드 서버: http://localhost:5000
echo    프론트엔드: http://localhost:3000
echo.

REM 환경변수 설정하고 개발 서버 시작
set NEXT_PUBLIC_API_URL=http://localhost:5000
set NEXT_PUBLIC_ENVIRONMENT=virtual_server
npm run dev

pause