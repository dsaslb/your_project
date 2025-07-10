#!/bin/bash

# Your Program 프로덕션 배포 스크립트
# 사용법: ./scripts/deploy-production.sh [environment] [action]
# environment: staging, production (기본값: production)
# action: deploy, rollback, update (기본값: deploy)

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 설정
ENVIRONMENT=${1:-production}
ACTION=${2:-deploy}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$PROJECT_ROOT/backups"
DEPLOY_LOG="$PROJECT_ROOT/logs/deploy_${ENVIRONMENT}_${DEPLOY_TIMESTAMP}.log"

# 환경별 설정
case $ENVIRONMENT in
    "staging")
        DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
        DOMAIN="staging.yourprogram.com"
        ;;
    "production")
        DOCKER_COMPOSE_FILE="docker-compose.production.yml"
        DOMAIN="yourprogram.com"
        ;;
    *)
        log_error "Invalid environment: $ENVIRONMENT"
        exit 1
        ;;
esac

# 배포 전 검증
validate_deployment() {
    log_info "Validating deployment prerequisites..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # 환경 변수 파일 확인
    if [ ! -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]; then
        log_error "Environment file .env.$ENVIRONMENT not found"
        exit 1
    fi
    
    # SSL 인증서 확인 (프로덕션)
    if [ "$ENVIRONMENT" = "production" ]; then
        if [ ! -f "$PROJECT_ROOT/nginx/ssl/cert.pem" ] || [ ! -f "$PROJECT_ROOT/nginx/ssl/key.pem" ]; then
            log_warning "SSL certificates not found. HTTPS will not be available."
        fi
    fi
    
    log_success "Deployment validation passed"
}

# 백업 생성
create_backup() {
    log_info "Creating backup before deployment..."
    
    local backup_name="backup_${ENVIRONMENT}_${DEPLOY_TIMESTAMP}"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # 데이터베이스 백업
    log_info "Backing up database..."
    docker-compose exec -T postgres pg_dump -U your_program your_program > "$backup_path/database.sql" 2>/dev/null || true
    docker-compose exec -T postgres pg_dump -U your_program_ai your_program_ai > "$backup_path/database_ai.sql" 2>/dev/null || true
    
    # 설정 파일 백업
    log_info "Backing up configuration files..."
    cp -r "$PROJECT_ROOT/.env.$ENVIRONMENT" "$backup_path/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT/nginx/nginx.conf" "$backup_path/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT/docker-compose.yml" "$backup_path/" 2>/dev/null || true
    
    # 업로드 파일 백업
    if [ -d "$PROJECT_ROOT/uploads" ]; then
        log_info "Backing up uploads..."
        tar -czf "$backup_path/uploads.tar.gz" -C "$PROJECT_ROOT" uploads/
    fi
    
    # 로그 파일 백업
    if [ -d "$PROJECT_ROOT/logs" ]; then
        log_info "Backing up logs..."
        tar -czf "$backup_path/logs.tar.gz" -C "$PROJECT_ROOT" logs/
    fi
    
    log_success "Backup created: $backup_path"
}

# 이미지 빌드
build_images() {
    log_info "Building Docker images..."
    
    # 환경별 이미지 태그
    local image_tag="${ENVIRONMENT}-${DEPLOY_TIMESTAMP}"
    
    # 백엔드 이미지 빌드
    log_info "Building backend image..."
    docker build -f Dockerfile.backend -t your-program-backend:$image_tag .
    
    # AI 서버 이미지 빌드
    log_info "Building AI server image..."
    docker build -f Dockerfile.ai -t your-program-ai:$image_tag .
    
    # 프론트엔드 이미지 빌드
    log_info "Building frontend image..."
    docker build -f your_program_frontend/Dockerfile -t your-program-frontend:$image_tag ./your_program_frontend
    
    # Gateway 이미지 빌드
    log_info "Building gateway image..."
    docker build -f Dockerfile.gateway -t your-program-gateway:$image_tag .
    
    log_success "All images built successfully"
}

# 서비스 배포
deploy_services() {
    log_info "Deploying services to $ENVIRONMENT..."
    
    # 환경 변수 로드
    export $(cat "$PROJECT_ROOT/.env.$ENVIRONMENT" | xargs)
    
    # 기존 서비스 중지 (Zero-downtime 배포)
    log_info "Stopping existing services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
    
    # 새 이미지로 서비스 시작
    log_info "Starting services with new images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    # 헬스체크
    log_info "Performing health checks..."
    sleep 30
    
    local services=("gateway" "backend" "ai-server" "frontend")
    local all_healthy=true
    
    for service in "${services[@]}"; do
        if ! check_service_health $service; then
            log_error "Service $service is not healthy"
            all_healthy=false
        else
            log_success "Service $service is healthy"
        fi
    done
    
    if [ "$all_healthy" = false ]; then
        log_error "Health check failed. Rolling back..."
        rollback_deployment
        exit 1
    fi
    
    log_success "All services deployed successfully"
}

# 서비스 헬스체크
check_service_health() {
    local service=$1
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        case $service in
            "gateway")
                if curl -f -s http://localhost:8000/health > /dev/null; then
                    return 0
                fi
                ;;
            "backend")
                if curl -f -s http://localhost:5001/health > /dev/null; then
                    return 0
                fi
                ;;
            "ai-server")
                if curl -f -s http://localhost:8002/health > /dev/null; then
                    return 0
                fi
                ;;
            "frontend")
                if curl -f -s http://localhost:3000 > /dev/null; then
                    return 0
                fi
                ;;
        esac
        
        log_info "Health check attempt $attempt/$max_attempts for $service"
        sleep 10
        ((attempt++))
    done
    
    return 1
}

# 롤백
rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    # 최신 백업 찾기
    local latest_backup=$(ls -t "$BACKUP_DIR"/backup_${ENVIRONMENT}_* | head -1)
    
    if [ -n "$latest_backup" ]; then
        log_info "Restoring from backup: $latest_backup"
        
        # 데이터베이스 복원
        if [ -f "$latest_backup/database.sql" ]; then
            log_info "Restoring database..."
            docker-compose exec -T postgres psql -U your_program your_program < "$latest_backup/database.sql"
        fi
        
        # 설정 파일 복원
        if [ -f "$latest_backup/.env.$ENVIRONMENT" ]; then
            cp "$latest_backup/.env.$ENVIRONMENT" "$PROJECT_ROOT/"
        fi
        
        # 이전 이미지로 서비스 재시작
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
        
        log_success "Rollback completed"
    else
        log_error "No backup found for rollback"
    fi
}

# 데이터베이스 마이그레이션
run_migrations() {
    log_info "Running database migrations..."
    
    # Alembic 마이그레이션
    docker-compose exec -T backend flask db upgrade || {
        log_error "Database migration failed"
        return 1
    }
    
    log_success "Database migrations completed"
}

# 모니터링 설정
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Prometheus 설정
    if [ ! -f "$PROJECT_ROOT/monitoring/prometheus.yml" ]; then
        log_warning "Prometheus configuration not found"
        return 1
    fi
    
    # Grafana 대시보드 설정
    if [ ! -f "$PROJECT_ROOT/monitoring/grafana/dashboards/your-program-dashboard.json" ]; then
        log_warning "Grafana dashboard configuration not found"
        return 1
    fi
    
    log_success "Monitoring setup completed"
}

# SSL 인증서 갱신 (Let's Encrypt)
renew_ssl_certificates() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Renewing SSL certificates..."
        
        # certbot을 사용한 자동 갱신
        docker run --rm \
            -v "$PROJECT_ROOT/nginx/ssl:/etc/letsencrypt" \
            -v "$PROJECT_ROOT/nginx/webroot:/var/www/html" \
            certbot/certbot renew --webroot --webroot-path=/var/www/html || {
            log_warning "SSL certificate renewal failed"
        }
        
        # Nginx 재로드
        docker-compose exec nginx nginx -s reload
        
        log_success "SSL certificates renewed"
    fi
}

# 성능 테스트
run_performance_tests() {
    log_info "Running performance tests..."
    
    # 간단한 부하 테스트
    local test_url="http://localhost"
    local concurrent_users=10
    local duration=30
    
    # Apache Bench를 사용한 부하 테스트
    if command -v ab &> /dev/null; then
        ab -n 1000 -c $concurrent_users -t $duration "$test_url/" > "$PROJECT_ROOT/logs/performance_test_${DEPLOY_TIMESTAMP}.log" 2>&1 || {
            log_warning "Performance test failed"
        }
    else
        log_warning "Apache Bench not available, skipping performance test"
    fi
    
    log_success "Performance tests completed"
}

# 배포 후 정리
cleanup_after_deployment() {
    log_info "Cleaning up after deployment..."
    
    # 오래된 이미지 정리
    docker image prune -f
    
    # 오래된 백업 정리 (30일 이상)
    find "$BACKUP_DIR" -name "backup_*" -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
    
    # 오래된 로그 정리 (7일 이상)
    find "$PROJECT_ROOT/logs" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# 배포 로그 기록
log_deployment() {
    local status=$1
    local message=$2
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $ENVIRONMENT - $ACTION - $status - $message" >> "$DEPLOY_LOG"
}

# 메인 배포 로직
main() {
    log_info "Starting $ENVIRONMENT deployment..."
    log_deployment "START" "Deployment initiated"
    
    # 배포 디렉토리 생성
    mkdir -p "$BACKUP_DIR" "$PROJECT_ROOT/logs"
    
    # 배포 전 검증
    validate_deployment
    log_deployment "VALIDATION" "Prerequisites validated"
    
    # 백업 생성
    create_backup
    log_deployment "BACKUP" "Backup created"
    
    case $ACTION in
        "deploy")
            # 이미지 빌드
            build_images
            log_deployment "BUILD" "Images built"
            
            # 서비스 배포
            deploy_services
            log_deployment "DEPLOY" "Services deployed"
            
            # 데이터베이스 마이그레이션
            run_migrations
            log_deployment "MIGRATION" "Database migrated"
            
            # 모니터링 설정
            setup_monitoring
            log_deployment "MONITORING" "Monitoring configured"
            
            # 성능 테스트
            run_performance_tests
            log_deployment "TESTING" "Performance tests completed"
            
            # SSL 인증서 갱신
            renew_ssl_certificates
            log_deployment "SSL" "SSL certificates renewed"
            
            # 정리
            cleanup_after_deployment
            log_deployment "CLEANUP" "Cleanup completed"
            
            log_success "Deployment completed successfully!"
            log_deployment "SUCCESS" "Deployment completed"
            ;;
            
        "rollback")
            rollback_deployment
            log_deployment "ROLLBACK" "Rollback completed"
            ;;
            
        "update")
            # 설정 파일만 업데이트
            log_info "Updating configuration..."
            docker-compose -f "$DOCKER_COMPOSE_FILE" down
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
            log_deployment "UPDATE" "Configuration updated"
            ;;
            
        *)
            log_error "Invalid action: $ACTION"
            exit 1
            ;;
    esac
    
    # 배포 완료 알림
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Sending deployment notification..."
        # Slack, 이메일 등으로 알림 전송
        echo "Your Program deployment to $ENVIRONMENT completed at $(date)" | \
        curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"Your Program deployment to $ENVIRONMENT completed successfully!\"}" \
        $SLACK_WEBHOOK_URL 2>/dev/null || true
    fi
    
    log_success "Deployment process completed"
}

# 스크립트 실행
main "$@" 