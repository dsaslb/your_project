@echo off
echo ========================================
echo 레스토랑 관리 시스템 마이크로서비스 시작
echo ========================================

echo.
echo 1. Docker Compose로 마이크로서비스 빌드 및 실행...
docker-compose up --build -d

echo.
echo 2. 서비스 상태 확인...
timeout /t 10 /nobreak > nul
docker-compose ps

echo.
echo 3. 서비스 로그 확인...
echo API Gateway: http://localhost:5000
echo User Service: http://localhost:5001
echo Staff Service: http://localhost:5002
echo Inventory Service: http://localhost:5003
echo Order Service: http://localhost:5004
echo Analytics Service: http://localhost:5005
echo IoT Service: http://localhost:5006
echo Notification Service: http://localhost:5007
echo AI Service: http://localhost:5008
echo Redis: localhost:6379
echo PostgreSQL: localhost:5432

echo.
echo 모든 서비스가 시작되었습니다!
echo API Gateway를 통해 모든 서비스에 접근할 수 있습니다: http://localhost:5000
echo.
echo 서비스 중지하려면: docker-compose down
echo 로그 확인하려면: docker-compose logs -f [서비스명] 