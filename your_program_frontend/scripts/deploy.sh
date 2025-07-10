#!/bin/bash

# Your Program Frontend 배포 스크립트
# 사용법: ./scripts/deploy.sh [environment]
# environment: dev, staging, prod (기본값: dev)

set -e  # 에러 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 설정
ENVIRONMENT=${1:-dev}
PROJECT_NAME="your_program_frontend"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BUILD_DIR="dist"
BACKUP_DIR="backups"

# 환경별 설정
case $ENVIRONMENT in
    "dev")
        NODE_ENV="development"
        API_URL="http://localhost:5001"
        WS_URL="ws://localhost:5001"
        ;;
    "staging")
        NODE_ENV="staging"
        API_URL="https://staging-api.yourprogram.com"
        WS_URL="wss://staging-api.yourprogram.com"
        ;;
    "prod")
        NODE_ENV="production"
        API_URL="https://api.yourprogram.com"
        WS_URL="wss://api.yourprogram.com"
        ;;
    *)
        log_error "잘못된 환경입니다. 사용법: $0 [dev|staging|prod]"
        exit 1
        ;;
esac

log_info "배포 환경: $ENVIRONMENT"
log_info "프로젝트: $PROJECT_NAME"
log_info "타임스탬프: $TIMESTAMP"

# 1. 의존성 설치
log_info "의존성 설치 중..."
npm ci --silent
log_success "의존성 설치 완료"

# 2. 타입 체크
log_info "TypeScript 타입 체크 중..."
npm run type-check
log_success "타입 체크 완료"

# 3. 린트 검사
log_info "코드 린트 검사 중..."
npm run lint
log_success "린트 검사 완료"

# 4. 테스트 실행
log_info "테스트 실행 중..."
npm run test:ci
log_success "테스트 완료"

# 5. E2E 테스트 (프로덕션 환경에서만)
if [ "$ENVIRONMENT" = "prod" ]; then
    log_info "E2E 테스트 실행 중..."
    npm run test:e2e
    log_success "E2E 테스트 완료"
fi

# 6. 환경 변수 설정
log_info "환경 변수 설정 중..."
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=$API_URL
NEXT_PUBLIC_WS_URL=$WS_URL
NODE_ENV=$NODE_ENV
EOF
log_success "환경 변수 설정 완료"

# 7. 빌드
log_info "프로덕션 빌드 중..."
npm run build
log_success "빌드 완료"

# 8. 백업 생성
log_info "기존 배포 백업 중..."
mkdir -p $BACKUP_DIR
if [ -d "$BUILD_DIR" ]; then
    tar -czf "$BACKUP_DIR/${PROJECT_NAME}_${ENVIRONMENT}_${TIMESTAMP}.tar.gz" -C $BUILD_DIR .
    log_success "백업 생성 완료: $BACKUP_DIR/${PROJECT_NAME}_${ENVIRONMENT}_${TIMESTAMP}.tar.gz"
fi

# 9. 배포 디렉토리 정리
log_info "배포 디렉토리 정리 중..."
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# 10. 빌드 결과 복사
log_info "빌드 결과 복사 중..."
cp -r .next $BUILD_DIR/
cp -r public $BUILD_DIR/
cp package.json $BUILD_DIR/
cp next.config.js $BUILD_DIR/
log_success "빌드 결과 복사 완료"

# 11. 배포 스크립트 생성
log_info "배포 스크립트 생성 중..."
cat > $BUILD_DIR/start.sh << 'EOF'
#!/bin/bash
export NODE_ENV=production
export PORT=${PORT:-3000}
npm start
EOF
chmod +x $BUILD_DIR/start.sh

# 12. Docker 이미지 빌드 (선택사항)
if command -v docker &> /dev/null; then
    log_info "Docker 이미지 빌드 중..."
    docker build -t $PROJECT_NAME:$ENVIRONMENT-$TIMESTAMP .
    docker tag $PROJECT_NAME:$ENVIRONMENT-$TIMESTAMP $PROJECT_NAME:$ENVIRONMENT-latest
    log_success "Docker 이미지 빌드 완료"
fi

# 13. 배포 완료
log_success "배포 준비 완료!"
log_info "배포 디렉토리: $BUILD_DIR"
log_info "환경: $ENVIRONMENT"
log_info "API URL: $API_URL"

# 14. 배포 통계
log_info "배포 통계:"
echo "  - 빌드 크기: $(du -sh $BUILD_DIR | cut -f1)"
echo "  - 백업 파일: $BACKUP_DIR/${PROJECT_NAME}_${ENVIRONMENT}_${TIMESTAMP}.tar.gz"
echo "  - 타임스탬프: $TIMESTAMP"

# 15. 정리
log_info "임시 파일 정리 중..."
rm -f .env.local
log_success "정리 완료"

log_success "배포 프로세스가 성공적으로 완료되었습니다!" 