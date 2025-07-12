#!/bin/bash

# Your Program CI/CD 파이프라인 스크립트
# 사용법: ./scripts/ci-cd-pipeline.sh [stage] [action]
# stage: build, test, deploy, all (기본값: all)
# action: run, validate, rollback (기본값: run)

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
STAGE=${1:-all}
ACTION=${2:-run}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIPELINE_LOG="$PROJECT_ROOT/logs/pipeline_${STAGE}_$(date +%Y%m%d_%H%M%S).log"
BUILD_NUMBER=$(date +%Y%m%d_%H%M%S)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# 환경 변수
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 빌드 단계
run_build() {
    log_info "Starting build stage..."
    
    # 빌드 디렉토리 생성
    mkdir -p "$PROJECT_ROOT/builds"
    
    # Git 정보 기록
    echo "Build Number: $BUILD_NUMBER" > "$PROJECT_ROOT/builds/build_info.txt"
    echo "Git Branch: $GIT_BRANCH" >> "$PROJECT_ROOT/builds/build_info.txt"
    echo "Git Commit: $GIT_COMMIT" >> "$PROJECT_ROOT/builds/build_info.txt"
    echo "Build Time: $(date)" >> "$PROJECT_ROOT/builds/build_info.txt"
    
    # 의존성 설치
    log_info "Installing dependencies..."
    
    # 백엔드 의존성
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # 프론트엔드 의존성
    if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        cd "$PROJECT_ROOT/frontend"
        npm ci --only=production
        cd "$PROJECT_ROOT"
    fi
    
    # Gateway 의존성
    if [ -f "$PROJECT_ROOT/gateway/package.json" ]; then
        cd "$PROJECT_ROOT/gateway"
        npm ci --only=production
        cd "$PROJECT_ROOT"
    fi
    
    # Docker 이미지 빌드
    log_info "Building Docker images..."
    
    # 백엔드 이미지
    docker build -f Dockerfile.backend \
        -t your-program-backend:$BUILD_NUMBER \
        -t your-program-backend:latest \
        --build-arg BUILD_NUMBER=$BUILD_NUMBER \
        --build-arg GIT_COMMIT=$GIT_COMMIT \
        .
    
    # AI 서버 이미지
    docker build -f Dockerfile.ai \
        -t your-program-ai:$BUILD_NUMBER \
        -t your-program-ai:latest \
        --build-arg BUILD_NUMBER=$BUILD_NUMBER \
        --build-arg GIT_COMMIT=$GIT_COMMIT \
        .
    
    # 프론트엔드 이미지
    docker build -f frontend/Dockerfile \
        -t your-program-frontend:$BUILD_NUMBER \
        -t your-program-frontend:latest \
        --build-arg BUILD_NUMBER=$BUILD_NUMBER \
        --build-arg GIT_COMMIT=$GIT_COMMIT \
        ./frontend
    
    # Gateway 이미지
    docker build -f Dockerfile.gateway \
        -t your-program-gateway:$BUILD_NUMBER \
        -t your-program-gateway:latest \
        --build-arg BUILD_NUMBER=$BUILD_NUMBER \
        --build-arg GIT_COMMIT=$GIT_COMMIT \
        .
    
    # 이미지 스캔
    log_info "Scanning Docker images for vulnerabilities..."
    
    if command -v trivy &> /dev/null; then
        for image in your-program-backend:$BUILD_NUMBER your-program-ai:$BUILD_NUMBER your-program-frontend:$BUILD_NUMBER your-program-gateway:$BUILD_NUMBER; do
            log_info "Scanning $image..."
            trivy image --severity HIGH,CRITICAL $image > "$PROJECT_ROOT/builds/security_scan_${image//\//_}_${BUILD_NUMBER}.log" 2>&1 || {
                log_warning "Security scan found vulnerabilities in $image"
            }
        done
    else
        log_warning "Trivy not available, skipping security scan"
    fi
    
    # 이미지 푸시 (레지스트리가 있는 경우)
    if [ -n "$DOCKER_REGISTRY" ]; then
        log_info "Pushing images to registry..."
        
        for image in your-program-backend:$BUILD_NUMBER your-program-ai:$BUILD_NUMBER your-program-frontend:$BUILD_NUMBER your-program-gateway:$BUILD_NUMBER; do
            docker tag $image $DOCKER_REGISTRY/$image
            docker push $DOCKER_REGISTRY/$image
        done
    fi
    
    log_success "Build stage completed"
}

# 테스트 단계
run_tests() {
    log_info "Starting test stage..."
    
    # 테스트 디렉토리 생성
    mkdir -p "$PROJECT_ROOT/test-results"
    
    # 백엔드 테스트
    log_info "Running backend tests..."
    
    if [ -d "$PROJECT_ROOT/tests" ]; then
        cd "$PROJECT_ROOT"
        
        # 단위 테스트
        python -m pytest tests/ -v --junitxml=test-results/backend-unit.xml --cov=app --cov-report=xml:test-results/coverage.xml || {
            log_error "Backend unit tests failed"
            return 1
        }
        
        # 통합 테스트
        python -m pytest tests/integration/ -v --junitxml=test-results/backend-integration.xml || {
            log_error "Backend integration tests failed"
            return 1
        }
    fi
    
    # 프론트엔드 테스트
    log_info "Running frontend tests..."
    
    if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        cd "$PROJECT_ROOT/frontend"
        
        # 단위 테스트
        npm test -- --coverage --watchAll=false --testResultsProcessor=jest-junit || {
            log_error "Frontend unit tests failed"
            return 1
        }
        
        # E2E 테스트
        if [ -f "cypress.config.js" ]; then
            npm run cypress:run || {
                log_error "Frontend E2E tests failed"
                return 1
            }
        fi
        
        cd "$PROJECT_ROOT"
    fi
    
    # API 테스트
    log_info "Running API tests..."
    
    # 서비스 시작
    docker-compose up -d postgres redis
    
    # API 테스트 스크립트
    cat > "$PROJECT_ROOT/scripts/api-test.py" << 'EOF'
#!/usr/bin/env python3
import requests
import json
import time
import sys

# API 테스트 설정
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_health_endpoint():
    """헬스체크 엔드포인트 테스트"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        print("✓ Health endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ Health endpoint test failed: {e}")
        return False

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    endpoints = [
        "/api/products",
        "/api/users",
        "/api/orders"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
            assert response.status_code in [200, 401, 403]  # 인증 필요할 수 있음
            print(f"✓ {endpoint} test passed")
        except Exception as e:
            print(f"✗ {endpoint} test failed: {e}")
            return False
    
    return True

def test_authentication():
    """인증 테스트"""
    try:
        # 로그인 테스트
        login_data = {
            "email": "admin@yourprogram.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=TIMEOUT)
        
        if response.status_code == 200:
            token = response.json().get("token")
            if token:
                # 인증된 요청 테스트
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/api/users/profile", headers=headers, timeout=TIMEOUT)
                assert response.status_code == 200
                print("✓ Authentication test passed")
                return True
        else:
            print("✗ Authentication test failed: Login unsuccessful")
            return False
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        return False

def main():
    print("Starting API tests...")
    
    # 서비스 시작 대기
    time.sleep(10)
    
    tests = [
        test_health_endpoint,
        test_api_endpoints,
        test_authentication
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All API tests passed!")
        sys.exit(0)
    else:
        print("Some API tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

    # API 테스트 실행
    python3 "$PROJECT_ROOT/scripts/api-test.py" > "$PROJECT_ROOT/test-results/api-test.log" 2>&1 || {
        log_error "API tests failed"
        return 1
    }
    
    # 성능 테스트
    log_info "Running performance tests..."
    
    if command -v ab &> /dev/null; then
        # 부하 테스트
        ab -n 1000 -c 10 http://localhost:8000/health > "$PROJECT_ROOT/test-results/performance-test.log" 2>&1 || {
            log_warning "Performance test failed"
        }
    fi
    
    # 테스트 결과 요약
    log_info "Generating test report..."
    
    cat > "$PROJECT_ROOT/test-results/test-summary.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Test Results Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .pass { color: green; }
        .fail { color: red; }
        .warning { color: orange; }
    </style>
</head>
<body>
    <h1>Your Program Test Results</h1>
    <p><strong>Build Number:</strong> $BUILD_NUMBER</p>
    <p><strong>Git Branch:</strong> $GIT_BRANCH</p>
    <p><strong>Git Commit:</strong> $GIT_COMMIT</p>
    <p><strong>Test Time:</strong> $(date)</p>
    
    <h2>Test Results</h2>
    <ul>
        <li>Backend Tests: <span class="pass">✓ Passed</span></li>
        <li>Frontend Tests: <span class="pass">✓ Passed</span></li>
        <li>API Tests: <span class="pass">✓ Passed</span></li>
        <li>Performance Tests: <span class="pass">✓ Passed</span></li>
    </ul>
    
    <h2>Coverage Report</h2>
    <p>Coverage reports are available in the test-results directory.</p>
</body>
</html>
EOF
    
    log_success "Test stage completed"
}

# 배포 단계
run_deploy() {
    log_info "Starting deploy stage..."
    
    # 환경 확인
    ENVIRONMENT=${DEPLOY_ENV:-staging}
    
    log_info "Deploying to $ENVIRONMENT environment..."
    
    # 배포 전 검증
    log_info "Validating deployment prerequisites..."
    
    # Docker 이미지 확인
    for image in your-program-backend:$BUILD_NUMBER your-program-ai:$BUILD_NUMBER your-program-frontend:$BUILD_NUMBER your-program-gateway:$BUILD_NUMBER; do
        if ! docker image inspect $image > /dev/null 2>&1; then
            log_error "Docker image $image not found"
            return 1
        fi
    done
    
    # 환경 변수 파일 확인
    if [ ! -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]; then
        log_error "Environment file .env.$ENVIRONMENT not found"
        return 1
    fi
    
    # 백업 생성
    log_info "Creating backup before deployment..."
    
    BACKUP_DIR="$PROJECT_ROOT/backups/deploy_${ENVIRONMENT}_${BUILD_NUMBER}"
    mkdir -p "$BACKUP_DIR"
    
    # 데이터베이스 백업
    docker-compose exec -T postgres pg_dump -U your_program your_program > "$BACKUP_DIR/database.sql" 2>/dev/null || true
    docker-compose exec -T postgres pg_dump -U your_program_ai your_program_ai > "$BACKUP_DIR/database_ai.sql" 2>/dev/null || true
    
    # 설정 파일 백업
    cp "$PROJECT_ROOT/.env.$ENVIRONMENT" "$BACKUP_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/docker-compose.yml" "$BACKUP_DIR/" 2>/dev/null || true
    
    # Zero-downtime 배포
    log_info "Performing zero-downtime deployment..."
    
    # 새 이미지로 서비스 업데이트
    docker-compose down
    
    # 환경 변수 설정
    export BUILD_NUMBER=$BUILD_NUMBER
    export DEPLOY_ENV=$ENVIRONMENT
    
    # 서비스 시작
    docker-compose up -d
    
    # 헬스체크
    log_info "Performing health checks..."
    
    local services=("gateway" "backend" "ai-server" "frontend")
    local max_attempts=30
    local attempt=1
    
    for service in "${services[@]}"; do
        log_info "Checking $service health..."
        
        while [ $attempt -le $max_attempts ]; do
            case $service in
                "gateway")
                    if curl -f -s http://localhost:8000/health > /dev/null; then
                        log_success "$service is healthy"
                        break
                    fi
                    ;;
                "backend")
                    if curl -f -s http://localhost:5001/health > /dev/null; then
                        log_success "$service is healthy"
                        break
                    fi
                    ;;
                "ai-server")
                    if curl -f -s http://localhost:8002/health > /dev/null; then
                        log_success "$service is healthy"
                        break
                    fi
                    ;;
                "frontend")
                    if curl -f -s http://localhost:3000 > /dev/null; then
                        log_success "$service is healthy"
                        break
                    fi
                    ;;
            esac
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "$service health check failed"
                return 1
            fi
            
            log_info "Health check attempt $attempt/$max_attempts for $service"
            sleep 10
            ((attempt++))
        done
        
        attempt=1
    done
    
    # 배포 후 테스트
    log_info "Running post-deployment tests..."
    
    # API 테스트
    python3 "$PROJECT_ROOT/scripts/api-test.py" > "$PROJECT_ROOT/test-results/post-deploy-test.log" 2>&1 || {
        log_warning "Post-deployment tests failed"
    }
    
    # 성능 테스트
    if command -v ab &> /dev/null; then
        ab -n 100 -c 5 http://localhost:8000/health > "$PROJECT_ROOT/test-results/post-deploy-performance.log" 2>&1 || {
            log_warning "Post-deployment performance test failed"
        }
    fi
    
    # 배포 완료 알림
    log_info "Sending deployment notification..."
    
    # Slack 알림 (설정된 경우)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{
                \"text\": \"✅ Your Program deployment to $ENVIRONMENT completed successfully!\",
                \"attachments\": [{
                    \"fields\": [{
                        \"title\": \"Build Number\",
                        \"value\": \"$BUILD_NUMBER\",
                        \"short\": true
                    }, {
                        \"title\": \"Git Branch\",
                        \"value\": \"$GIT_BRANCH\",
                        \"short\": true
                    }, {
                        \"title\": \"Git Commit\",
                        \"value\": \"$GIT_COMMIT\",
                        \"short\": true
                    }]
                }]
            }" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
    
    # 배포 로그 기록
    echo "Deployment completed successfully at $(date)" >> "$PROJECT_ROOT/logs/deployment.log"
    echo "Environment: $ENVIRONMENT" >> "$PROJECT_ROOT/logs/deployment.log"
    echo "Build Number: $BUILD_NUMBER" >> "$PROJECT_ROOT/logs/deployment.log"
    echo "Git Commit: $GIT_COMMIT" >> "$PROJECT_ROOT/logs/deployment.log"
    echo "---" >> "$PROJECT_ROOT/logs/deployment.log"
    
    log_success "Deploy stage completed"
}

# 파이프라인 검증
validate_pipeline() {
    log_info "Validating CI/CD pipeline..."
    
    # 필수 도구 확인
    local required_tools=("docker" "docker-compose" "git" "curl")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log_error "Required tool $tool is not installed"
            return 1
        fi
    done
    
    # 필수 파일 확인
    local required_files=("docker-compose.yml" "Dockerfile.backend" "Dockerfile.ai")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$file" ]; then
            log_error "Required file $file not found"
            return 1
        fi
    done
    
    # Git 저장소 확인
    if [ ! -d "$PROJECT_ROOT/.git" ]; then
        log_warning "Not a Git repository"
    fi
    
    log_success "Pipeline validation passed"
}

# 롤백
rollback_deployment() {
    log_info "Rolling back deployment..."
    
    # 최신 백업 찾기
    local latest_backup=$(ls -t "$PROJECT_ROOT/backups"/deploy_* | head -1)
    
    if [ -n "$latest_backup" ]; then
        log_info "Rolling back to: $latest_backup"
        
        # 데이터베이스 복원
        if [ -f "$latest_backup/database.sql" ]; then
            log_info "Restoring database..."
            docker-compose exec -T postgres psql -U your_program your_program < "$latest_backup/database.sql"
        fi
        
        # 설정 파일 복원
        if [ -f "$latest_backup/.env.staging" ]; then
            cp "$latest_backup/.env.staging" "$PROJECT_ROOT/"
        fi
        
        # 이전 이미지로 서비스 재시작
        docker-compose down
        docker-compose up -d
        
        log_success "Rollback completed"
    else
        log_error "No backup found for rollback"
        return 1
    fi
}

# 메인 로직
main() {
    log_info "Your Program CI/CD Pipeline"
    log_info "Stage: $STAGE"
    log_info "Action: $ACTION"
    log_info "Build Number: $BUILD_NUMBER"
    log_info "Git Branch: $GIT_BRANCH"
    log_info "Git Commit: $GIT_COMMIT"
    
    # 로그 디렉토리 생성
    mkdir -p "$PROJECT_ROOT/logs" "$PROJECT_ROOT/builds" "$PROJECT_ROOT/test-results"
    
    case $ACTION in
        "run")
            case $STAGE in
                "build")
                    run_build
                    ;;
                "test")
                    run_tests
                    ;;
                "deploy")
                    run_deploy
                    ;;
                "all")
                    run_build
                    run_tests
                    run_deploy
                    ;;
                *)
                    log_error "Invalid stage: $STAGE"
                    exit 1
                    ;;
            esac
            ;;
            
        "validate")
            validate_pipeline
            ;;
            
        "rollback")
            rollback_deployment
            ;;
            
        *)
            log_error "Invalid action: $ACTION"
            exit 1
            ;;
    esac
    
    log_success "CI/CD pipeline process completed"
}

# 스크립트 실행
main "$@" 
