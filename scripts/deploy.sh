#!/bin/bash

# 배포 스크립트
# 사용법: ./scripts/deploy.sh [environment] [version]

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

# 환경 변수 설정
ENVIRONMENT=${1:-development}
VERSION=${2:-latest}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "배포 시작: 환경=$ENVIRONMENT, 버전=$VERSION"

# 환경별 설정
case $ENVIRONMENT in
    development)
        DOCKER_COMPOSE_FILE="docker-compose.yml"
        PROFILE="dev"
        DOMAIN="dev.yourprogram.com"
        ;;
    staging)
        DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
        PROFILE="staging"
        DOMAIN="staging.yourprogram.com"
        ;;
    production)
        DOCKER_COMPOSE_FILE="docker-compose.production.yml"
        PROFILE="production"
        DOMAIN="yourprogram.com"
        ;;
    *)
        log_error "지원하지 않는 환경: $ENVIRONMENT"
        exit 1
        ;;
esac

# 배포 전 검사
pre_deploy_check() {
    log_info "배포 전 검사 시작..."
    
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
    if [ ! -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]; then
        log_warning ".env.$ENVIRONMENT 파일이 없습니다. 기본값을 사용합니다."
    fi
    
    log_success "배포 전 검사 완료"
}

# 백업 생성
create_backup() {
    log_info "백업 생성 중..."
    
    BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 데이터베이스 백업
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps -q db > /dev/null 2>&1; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_dump -U postgres your_program > "$BACKUP_DIR/database.sql"
        log_success "데이터베이스 백업 완료: $BACKUP_DIR/database.sql"
    fi
    
    # 업로드 파일 백업
    if [ -d "$PROJECT_ROOT/uploads" ]; then
        tar -czf "$BACKUP_DIR/uploads.tar.gz" -C "$PROJECT_ROOT" uploads/
        log_success "업로드 파일 백업 완료: $BACKUP_DIR/uploads.tar.gz"
    fi
    
    # 로그 파일 백업
    if [ -d "$PROJECT_ROOT/logs" ]; then
        tar -czf "$BACKUP_DIR/logs.tar.gz" -C "$PROJECT_ROOT" logs/
        log_success "로그 파일 백업 완료: $BACKUP_DIR/logs.tar.gz"
    fi
    
    log_success "백업 생성 완료: $BACKUP_DIR"
}

# 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 중..."
    
    cd "$PROJECT_ROOT"
    
    # 환경 변수 로드
    if [ -f ".env.$ENVIRONMENT" ]; then
        export $(cat ".env.$ENVIRONMENT" | grep -v '^#' | xargs)
    fi
    
    # 이미지 빌드
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    log_success "Docker 이미지 빌드 완료"
}

# 서비스 배포
deploy_services() {
    log_info "서비스 배포 중..."
    
    cd "$PROJECT_ROOT"
    
    # 기존 서비스 중지 (데이터베이스 제외)
    log_info "기존 서비스 중지 중..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" stop app nginx grafana prometheus || true
    
    # 새 서비스 시작
    log_info "새 서비스 시작 중..."
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" --profile "$PROFILE" up -d
    else
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    fi
    
    log_success "서비스 배포 완료"
}

# 헬스 체크
health_check() {
    log_info "헬스 체크 시작..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "헬스 체크 시도 $attempt/$max_attempts"
        
        # 애플리케이션 헬스 체크
        if curl -f "http://localhost:5000/health" > /dev/null 2>&1; then
            log_success "애플리케이션 헬스 체크 통과"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "헬스 체크 실패"
            return 1
        fi
        
        sleep 10
        ((attempt++))
    done
    
    # 데이터베이스 헬스 체크
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        log_success "데이터베이스 헬스 체크 통과"
    else
        log_error "데이터베이스 헬스 체크 실패"
        return 1
    fi
    
    # Redis 헬스 체크
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis 헬스 체크 통과"
    else
        log_error "Redis 헬스 체크 실패"
        return 1
    fi
    
    log_success "모든 헬스 체크 통과"
}

# 데이터베이스 마이그레이션
run_migrations() {
    log_info "데이터베이스 마이그레이션 실행 중..."
    
    cd "$PROJECT_ROOT"
    
    # Alembic 마이그레이션 실행
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T app python -m alembic upgrade head
    
    log_success "데이터베이스 마이그레이션 완료"
}

# 캐시 정리
clear_cache() {
    log_info "캐시 정리 중..."
    
    cd "$PROJECT_ROOT"
    
    # Redis 캐시 정리
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli FLUSHALL > /dev/null 2>&1 || true
    
    log_success "캐시 정리 완료"
}

# 로그 정리
cleanup_logs() {
    log_info "오래된 로그 정리 중..."
    
    # 30일 이상 된 로그 파일 삭제
    find "$PROJECT_ROOT/logs" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log_success "로그 정리 완료"
}

# 배포 후 검증
post_deploy_verification() {
    log_info "배포 후 검증 중..."
    
    # 서비스 상태 확인
    cd "$PROJECT_ROOT"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    # 로그 확인
    log_info "최근 로그 확인:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=20 app
    
    log_success "배포 후 검증 완료"
}

# 롤백 함수
rollback() {
    log_error "배포 실패. 롤백 시작..."
    
    cd "$PROJECT_ROOT"
    
    # 이전 버전으로 롤백
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_warning "롤백 완료. 시스템을 확인하세요."
}

# 메인 배포 프로세스
main() {
    local start_time=$(date +%s)
    
    log_info "배포 프로세스 시작"
    
    # 배포 전 검사
    pre_deploy_check
    
    # 백업 생성
    create_backup
    
    # 이미지 빌드
    build_images
    
    # 서비스 배포
    deploy_services
    
    # 헬스 체크
    if ! health_check; then
        rollback
        exit 1
    fi
    
    # 데이터베이스 마이그레이션
    run_migrations
    
    # 캐시 정리
    clear_cache
    
    # 로그 정리
    cleanup_logs
    
    # 배포 후 검증
    post_deploy_verification
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "배포 완료! 소요 시간: ${duration}초"
    log_info "배포된 환경: $ENVIRONMENT"
    log_info "배포된 버전: $VERSION"
    log_info "도메인: $DOMAIN"
}

# 스크립트 실행
main "$@" 
