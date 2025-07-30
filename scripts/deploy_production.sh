#!/bin/bash

# 프로덕션 배포 스크립트
# 사용법: ./scripts/deploy_production.sh

set -e

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

# 스크립트 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "프로덕션 배포 시작"
log_info "프로젝트 루트: $PROJECT_ROOT"

# 사전 배포 검사
pre_deploy_check() {
    log_info "사전 배포 검사 시작..."
    
    # Docker 설치 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    # Docker Compose 설치 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    # 환경 변수 파일 확인
    if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
        log_warning "프로덕션 환경 변수 파일이 없습니다."
        log_info "config/production.env.example을 .env.production로 복사하세요."
        exit 1
    fi
    
    log_success "사전 배포 검사 완료"
}

# 백업 생성
create_backup() {
    log_info "백업 생성 시작..."
    
    BACKUP_DIR="$PROJECT_ROOT/backups"
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    # 데이터베이스 백업
    if docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T db pg_dump -U your_user your_program_prod > "$BACKUP_DIR/db_backup.sql" 2>/dev/null; then
        log_success "데이터베이스 백업 완료"
    else
        log_warning "데이터베이스 백업 실패 (새 설치인 경우 무시 가능)"
    fi
    
    # 파일 백업
    tar -czf "$BACKUP_DIR/$BACKUP_NAME" \
        --exclude="$PROJECT_ROOT/.git" \
        --exclude="$PROJECT_ROOT/node_modules" \
        --exclude="$PROJECT_ROOT/venv" \
        --exclude="$PROJECT_ROOT/.next" \
        --exclude="$PROJECT_ROOT/logs" \
        --exclude="$PROJECT_ROOT/backups" \
        -C "$PROJECT_ROOT" .
    
    log_success "백업 생성 완료: $BACKUP_NAME"
}

# SSL 인증서 생성
setup_ssl() {
    log_info "SSL 인증서 설정..."
    
    SSL_DIR="$PROJECT_ROOT/nginx/ssl"
    mkdir -p "$SSL_DIR"
    
    # 자체 서명 인증서 생성 (개발용)
    if [ ! -f "$SSL_DIR/cert.pem" ] || [ ! -f "$SSL_DIR/key.pem" ]; then
        log_info "자체 서명 SSL 인증서 생성..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$SSL_DIR/key.pem" \
            -out "$SSL_DIR/cert.pem" \
            -subj "/C=KR/ST=Seoul/L=Seoul/O=YourProgram/CN=your-domain.com"
        log_success "SSL 인증서 생성 완료"
    else
        log_info "기존 SSL 인증서 사용"
    fi
}

# Docker 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 시작..."
    
    cd "$PROJECT_ROOT"
    
    # 백엔드 이미지 빌드
    log_info "백엔드 이미지 빌드..."
    docker build -f Dockerfile.prod -t your_program_backend:latest .
    
    # 프론트엔드 이미지 빌드
    log_info "프론트엔드 이미지 빌드..."
    cd frontend
    docker build -f Dockerfile.prod -t your_program_frontend:latest .
    cd ..
    
    log_success "Docker 이미지 빌드 완료"
}

# 서비스 배포
deploy_services() {
    log_info "서비스 배포 시작..."
    
    cd "$PROJECT_ROOT"
    
    # 기존 서비스 중지 (nginx 제외)
    log_info "기존 서비스 중지..."
    docker-compose -f docker-compose.prod.yml stop app frontend db redis prometheus grafana 2>/dev/null || true
    
    # 새 서비스 시작
    log_info "새 서비스 시작..."
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "서비스 배포 완료"
}

# 헬스체크
health_check() {
    log_info "헬스체크 시작..."
    
    # 서비스 상태 확인
    sleep 30
    
    # 백엔드 헬스체크
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log_success "백엔드 서비스 정상"
    else
        log_error "백엔드 서비스 오류"
        return 1
    fi
    
    # 프론트엔드 헬스체크
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "프론트엔드 서비스 정상"
    else
        log_error "프론트엔드 서비스 오류"
        return 1
    fi
    
    # 데이터베이스 헬스체크
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U your_user -d your_program_prod > /dev/null 2>&1; then
        log_success "데이터베이스 서비스 정상"
    else
        log_error "데이터베이스 서비스 오류"
        return 1
    fi
    
    # Redis 헬스체크
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis 서비스 정상"
    else
        log_error "Redis 서비스 오류"
        return 1
    fi
    
    log_success "모든 서비스 정상 동작"
}

# 데이터베이스 마이그레이션
run_migrations() {
    log_info "데이터베이스 마이그레이션 시작..."
    
    cd "$PROJECT_ROOT"
    
    # Alembic 마이그레이션 실행
    docker-compose -f docker-compose.prod.yml exec -T app alembic upgrade head
    
    log_success "데이터베이스 마이그레이션 완료"
}

# 캐시 초기화
clear_cache() {
    log_info "캐시 초기화..."
    
    cd "$PROJECT_ROOT"
    
    # Redis 캐시 초기화
    docker-compose -f docker-compose.prod.yml exec -T redis redis-cli FLUSHALL
    
    log_success "캐시 초기화 완료"
}

# 배포 후 검증
post_deploy_verification() {
    log_info "배포 후 검증 시작..."
    
    # 서비스 상태 확인
    docker-compose -f docker-compose.prod.yml ps
    
    # 로그 확인
    log_info "최근 로그 확인..."
    docker-compose -f docker-compose.prod.yml logs --tail=20 app
    
    log_success "배포 후 검증 완료"
}

# 롤백 함수
rollback() {
    log_warning "롤백 시작..."
    
    cd "$PROJECT_ROOT"
    
    # 서비스 중지
    docker-compose -f docker-compose.prod.yml down
    
    # 백업에서 복원 (필요한 경우)
    if [ -f "$PROJECT_ROOT/backups/db_backup.sql" ]; then
        log_info "데이터베이스 백업에서 복원..."
        docker-compose -f docker-compose.prod.yml up -d db
        sleep 10
        docker-compose -f docker-compose.prod.yml exec -T db psql -U your_user -d your_program_prod < "$PROJECT_ROOT/backups/db_backup.sql"
    fi
    
    log_warning "롤백 완료"
}

# 메인 함수
main() {
    log_info "프로덕션 배포 프로세스 시작"
    
    # 사전 배포 검사
    pre_deploy_check
    
    # 백업 생성
    create_backup
    
    # SSL 인증서 설정
    setup_ssl
    
    # Docker 이미지 빌드
    build_images
    
    # 서비스 배포
    deploy_services
    
    # 헬스체크
    if health_check; then
        # 데이터베이스 마이그레이션
        run_migrations
        
        # 캐시 초기화
        clear_cache
        
        # 배포 후 검증
        post_deploy_verification
        
        log_success "프로덕션 배포 완료!"
        log_info "애플리케이션 URL: https://your-domain.com"
        log_info "관리자 URL: https://admin.your-domain.com"
        log_info "모니터링 URL: http://localhost:3001 (Grafana)"
    else
        log_error "헬스체크 실패"
        rollback
        exit 1
    fi
}

# 스크립트 실행
main "$@" 