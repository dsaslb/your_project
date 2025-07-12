#!/bin/bash

# 레스토랑 관리 시스템 배포 스크립트
# 사용법: ./scripts/deploy.sh [staging|production]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 설정
ENVIRONMENT=${1:-staging}
COMPOSE_FILE="docker-compose.prod.yml"

# 환경별 설정
if [ "$ENVIRONMENT" = "production" ]; then
    log_info "배포 환경: Production"
    export POSTGRES_PASSWORD=${PROD_POSTGRES_PASSWORD}
    export SECRET_KEY=${PROD_SECRET_KEY}
    export JWT_SECRET_KEY=${PROD_JWT_SECRET_KEY}
    export GRAFANA_PASSWORD=${PROD_GRAFANA_PASSWORD}
elif [ "$ENVIRONMENT" = "staging" ]; then
    log_info "배포 환경: Staging"
    export POSTGRES_PASSWORD=${STAGING_POSTGRES_PASSWORD:-staging_password}
    export SECRET_KEY=${STAGING_SECRET_KEY:-staging_secret_key}
    export JWT_SECRET_KEY=${STAGING_JWT_SECRET_KEY:-staging_jwt_secret}
    export GRAFANA_PASSWORD=${STAGING_GRAFANA_PASSWORD:-admin}
else
    log_error "잘못된 환경입니다. 'staging' 또는 'production'을 사용하세요."
    exit 1
fi

# 필수 환경 변수 확인
check_environment_variables() {
    log_info "환경 변수 확인 중..."
    
    if [ -z "$POSTGRES_PASSWORD" ]; then
        log_error "POSTGRES_PASSWORD가 설정되지 않았습니다."
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        log_error "SECRET_KEY가 설정되지 않았습니다."
        exit 1
    fi
    
    if [ -z "$JWT_SECRET_KEY" ]; then
        log_error "JWT_SECRET_KEY가 설정되지 않았습니다."
        exit 1
    fi
    
    log_info "환경 변수 확인 완료"
}

# Docker 설치 확인
check_docker() {
    log_info "Docker 설치 확인 중..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    log_info "Docker 확인 완료"
}

# 백업 생성
create_backup() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "데이터베이스 백업 생성 중..."
        
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # PostgreSQL 백업
        docker exec your_program_postgres pg_dump -U your_program_user your_program_db > "$BACKUP_DIR/database.sql"
        
        # Redis 백업
        docker exec your_program_redis redis-cli BGSAVE
        docker cp your_program_redis:/data/dump.rdb "$BACKUP_DIR/redis.rdb"
        
        log_info "백업 완료: $BACKUP_DIR"
    fi
}

# 기존 컨테이너 중지
stop_containers() {
    log_info "기존 컨테이너 중지 중..."
    
    if docker-compose -f "$COMPOSE_FILE" ps -q | grep -q .; then
        docker-compose -f "$COMPOSE_FILE" down
        log_info "기존 컨테이너 중지 완료"
    else
        log_info "실행 중인 컨테이너가 없습니다."
    fi
}

# 새 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 중..."
    
    # 백엔드 이미지 빌드
    docker build -f Dockerfile.backend -t restaurant-backend:latest .
    
    # 프론트엔드 이미지 빌드
    docker build -f restaurant_frontend/Dockerfile -t restaurant-frontend:latest restaurant_frontend/
    
    log_info "이미지 빌드 완료"
}

# 컨테이너 시작
start_containers() {
    log_info "컨테이너 시작 중..."
    
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_info "컨테이너 시작 완료"
}

# 헬스 체크
health_check() {
    log_info "헬스 체크 중..."
    
    # 백엔드 헬스 체크
    for i in {1..30}; do
        if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
            log_info "백엔드 헬스 체크 통과"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "백엔드 헬스 체크 실패"
            exit 1
        fi
        
        sleep 2
    done
    
    # 프론트엔드 헬스 체크
    for i in {1..30}; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            log_info "프론트엔드 헬스 체크 통과"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "프론트엔드 헬스 체크 실패"
            exit 1
        fi
        
        sleep 2
    done
    
    log_info "모든 서비스가 정상적으로 실행 중입니다."
}

# 로그 확인
show_logs() {
    log_info "최근 로그 확인 중..."
    
    echo "=== 백엔드 로그 ==="
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 backend
    
    echo "=== 프론트엔드 로그 ==="
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 frontend
}

# 메인 배포 프로세스
main() {
    log_info "레스토랑 관리 시스템 배포 시작"
    
    check_environment_variables
    check_docker
    create_backup
    stop_containers
    build_images
    start_containers
    health_check
    show_logs
    
    log_info "배포 완료!"
    log_info "백엔드: http://localhost:5000"
    log_info "프론트엔드: http://localhost:3000"
    log_info "Grafana: http://localhost:3001"
    log_info "Prometheus: http://localhost:9090"
}

# 스크립트 실행
main "$@" 
