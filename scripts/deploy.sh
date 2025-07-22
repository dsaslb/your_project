#!/bin/bash

# Your Program 배포 스크립트
# 사용법: ./deploy.sh [environment] [version]

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
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
PROJECT_NAME="your_program"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# 환경별 설정
case $ENVIRONMENT in
    "production")
        DOCKER_COMPOSE_FILE="docker-compose.production.yml"
        DOMAIN="yourprogram.com"
        ;;
    "staging")
        DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
        DOMAIN="staging.yourprogram.com"
        ;;
    "development")
        DOCKER_COMPOSE_FILE="docker-compose.development.yml"
        DOMAIN="dev.yourprogram.com"
        ;;
    *)
        log_error "Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

log_info "Starting deployment for $ENVIRONMENT environment (version: $VERSION)"

# 사전 체크
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Docker 설치 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Docker Compose 설치 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # 환경 변수 파일 확인
    if [ ! -f ".env.$ENVIRONMENT" ]; then
        log_warning "Environment file .env.$ENVIRONMENT not found"
    fi
    
    # SSL 인증서 확인 (프로덕션)
    if [ "$ENVIRONMENT" = "production" ]; then
        if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
            log_warning "SSL certificates not found"
        fi
    fi
    
    log_success "Pre-deployment checks completed"
}

# 백업 생성
create_backup() {
    log_info "Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 데이터베이스 백업
    if docker-compose -f $DOCKER_COMPOSE_FILE exec -T db pg_dump -U your_program your_program > "$BACKUP_DIR/database.sql" 2>/dev/null; then
        log_success "Database backup created: $BACKUP_DIR/database.sql"
    else
        log_warning "Database backup failed"
    fi
    
    # 설정 파일 백업
    cp -r config/ "$BACKUP_DIR/" 2>/dev/null || log_warning "Config backup failed"
    cp -r nginx/ "$BACKUP_DIR/" 2>/dev/null || log_warning "Nginx backup failed"
    
    log_success "Backup completed: $BACKUP_DIR"
}

# 이전 버전 중지
stop_previous_version() {
    log_info "Stopping previous version..."
    
    # 현재 실행 중인 컨테이너 확인
    if docker-compose -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
        docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans
        log_success "Previous version stopped"
    else
        log_info "No previous version running"
    fi
}

# 새 버전 배포
deploy_new_version() {
    log_info "Deploying new version..."
    
    # 환경 변수 설정
    export VERSION=$VERSION
    export ENVIRONMENT=$ENVIRONMENT
    
    # 이미지 풀 (프로덕션)
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Pulling latest images..."
        docker-compose -f $DOCKER_COMPOSE_FILE pull
    fi
    
    # 서비스 시작
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    log_success "New version deployed"
}

# 헬스체크
health_check() {
    log_info "Running health checks..."
    
    local max_attempts=30
    local attempt=1
    local health_url="https://$DOMAIN/health"
    
    # HTTP 헬스체크
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"
        
        if curl -f -s "$health_url" > /dev/null; then
            log_success "Health check passed"
            return 0
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# 성능 테스트
performance_test() {
    log_info "Running performance tests..."
    
    # 간단한 성능 테스트
    local response_time=$(curl -w "%{time_total}" -s -o /dev/null "https://$DOMAIN/api/status")
    
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        log_success "Performance test passed (response time: ${response_time}s)"
    else
        log_warning "Performance test warning (response time: ${response_time}s)"
    fi
}

# 롤백
rollback() {
    log_error "Deployment failed, starting rollback..."
    
    # 이전 버전으로 롤백
    docker-compose -f $DOCKER_COMPOSE_FILE down
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    # 롤백 후 헬스체크
    if health_check; then
        log_success "Rollback completed successfully"
    else
        log_error "Rollback failed"
        exit 1
    fi
}

# 알림 전송
send_notification() {
    local status=$1
    local message=$2
    
    log_info "Sending notification: $status - $message"
    
    # Slack 알림 (예시)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$ENVIRONMENT] Deployment $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || log_warning "Slack notification failed"
    fi
    
    # 이메일 알림 (예시)
    if [ -n "$EMAIL_RECIPIENTS" ]; then
        echo "Deployment $status: $message" | mail -s "[$ENVIRONMENT] Deployment $status" $EMAIL_RECIPIENTS || log_warning "Email notification failed"
    fi
}

# 메인 배포 프로세스
main() {
    local start_time=$(date +%s)
    
    log_info "Starting deployment process..."
    
    # 사전 체크
    pre_deployment_checks
    
    # 백업 생성
    create_backup
    
    # 이전 버전 중지
    stop_previous_version
    
    # 새 버전 배포
    if deploy_new_version; then
        # 헬스체크
        if health_check; then
            # 성능 테스트
            performance_test
            
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            
            log_success "Deployment completed successfully in ${duration} seconds"
            send_notification "SUCCESS" "Deployment completed in ${duration}s"
        else
            log_error "Health check failed"
            rollback
            send_notification "FAILED" "Health check failed, rolled back"
            exit 1
        fi
    else
        log_error "Deployment failed"
        rollback
        send_notification "FAILED" "Deployment failed, rolled back"
        exit 1
    fi
}

# 스크립트 실행
main "$@" 
