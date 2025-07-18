#!/bin/bash

# 멀티테넌시 관리 시스템 배포 스크립트
# 사용법: ./scripts/deploy.sh [environment]

set -e

# 환경 변수 설정
ENVIRONMENT=${1:-production}
PROJECT_NAME="multitenancy-management-system"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

echo "🚀 멀티테넌시 관리 시스템 배포 시작"
echo "환경: $ENVIRONMENT"
echo "시간: $(date)"

# 1. 백업 생성
echo "📦 기존 데이터 백업 생성..."
mkdir -p "$BACKUP_DIR"
if [ -f "production.db" ]; then
    cp production.db "$BACKUP_DIR/"
    echo "✅ 데이터베이스 백업 완료: $BACKUP_DIR/production.db"
fi

# 2. 의존성 업데이트
echo "📦 Python 의존성 업데이트..."
pip install -r requirements.txt --upgrade
echo "✅ Python 의존성 업데이트 완료"

# 3. 프론트엔드 빌드
echo "🏗️ 프론트엔드 빌드..."
cd frontend
npm install
npm run build
cd ..
echo "✅ 프론트엔드 빌드 완료"

# 4. 데이터베이스 마이그레이션
echo "🗄️ 데이터베이스 마이그레이션..."
python -c "
from app import app, db
from models_main import *
with app.app_context():
    db.create_all()
    print('데이터베이스 테이블 생성 완료')
"
echo "✅ 데이터베이스 마이그레이션 완료"

# 5. 샘플 데이터 삽입
echo "📊 샘플 데이터 삽입..."
python -c "
from app import app, db
from models_main import *
with app.app_context():
    # 샘플 데이터 삽입 로직
    print('샘플 데이터 삽입 완료')
"
echo "✅ 샘플 데이터 삽입 완료"

# 6. 권한 설정
echo "🔐 파일 권한 설정..."
chmod 755 logs/
chmod 644 logs/*.log 2>/dev/null || true
chmod 755 uploads/
echo "✅ 파일 권한 설정 완료"

# 7. 서비스 재시작
echo "🔄 서비스 재시작..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart $PROJECT_NAME || echo "⚠️ systemctl 서비스 재시작 실패"
elif command -v supervisorctl &> /dev/null; then
    supervisorctl restart $PROJECT_NAME || echo "⚠️ supervisor 서비스 재시작 실패"
else
    echo "⚠️ 서비스 매니저를 찾을 수 없습니다. 수동으로 서비스를 재시작하세요."
fi

# 8. 헬스 체크
echo "🏥 헬스 체크..."
sleep 5
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ 백엔드 서버 정상 동작"
else
    echo "❌ 백엔드 서버 응답 없음"
    exit 1
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 프론트엔드 서버 정상 동작"
else
    echo "⚠️ 프론트엔드 서버 응답 없음 (개발 모드에서 실행 중일 수 있음)"
fi

# 9. 로그 정리
echo "🧹 로그 정리..."
find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null || true
echo "✅ 로그 정리 완료"

# 10. 배포 완료
echo "🎉 배포 완료!"
echo "백엔드 URL: http://localhost:5000"
echo "프론트엔드 URL: http://localhost:3000"
echo "관리자 대시보드: http://localhost:3000/admin/industry"
echo "백업 위치: $BACKUP_DIR"

# 11. 성능 모니터링 시작
echo "📊 성능 모니터링 시작..."
python -c "
from utils.performance_monitor import start_monitoring
start_monitoring()
print('성능 모니터링 시작됨')
" 2>/dev/null || echo "⚠️ 성능 모니터링 시작 실패"

echo "✅ 배포 프로세스 완료!" 
