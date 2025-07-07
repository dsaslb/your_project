#!/bin/bash

# 배포 스크립트
set -e

echo "🚀 레스토랑 관리 시스템 배포 시작..."

# 환경 변수 확인
if [ -z "$NODE_ENV" ]; then
    export NODE_ENV=production
fi

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리..."
docker-compose down --remove-orphans

# 이미지 빌드
echo "🔨 Docker 이미지 빌드..."
docker-compose build --no-cache

# 데이터베이스 마이그레이션
echo "🗄️ 데이터베이스 마이그레이션..."
docker-compose up -d db
sleep 10

# 백엔드 마이그레이션 실행
echo "📊 데이터베이스 스키마 업데이트..."
docker-compose run --rm backend python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# 서비스 시작
echo "🚀 서비스 시작..."
docker-compose up -d

# 헬스 체크
echo "🏥 헬스 체크..."
sleep 30

# 백엔드 헬스 체크
if curl -f http://localhost:5000/api/health; then
    echo "✅ 백엔드 서비스 정상"
else
    echo "❌ 백엔드 서비스 오류"
    exit 1
fi

# 프론트엔드 헬스 체크
if curl -f http://localhost:3000; then
    echo "✅ 프론트엔드 서비스 정상"
else
    echo "❌ 프론트엔드 서비스 오류"
    exit 1
fi

echo "🎉 배포 완료!"
echo "📱 프론트엔드: http://localhost:3000"
echo "🔧 백엔드 API: http://localhost:5000"
echo "📊 Grafana: http://localhost:3001"
echo "📈 Prometheus: http://localhost:9090"

# 로그 출력
echo "📋 서비스 로그 확인 중..."
docker-compose logs --tail=50 