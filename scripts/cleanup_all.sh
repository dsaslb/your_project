#!/bin/bash

# Your Program 전체 프로젝트 정리 스크립트
# 사용법: ./scripts/cleanup_all.sh [type]
# type: all, cache, build, test, node_modules, python, docker (기본값: all)

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

# 정리 타입 설정
CLEANUP_TYPE=${1:-all}

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 정리할 디렉토리/파일 목록
CACHE_DIRS=(
    ".next"
    ".cache"
    ".parcel-cache"
    ".eslintcache"
    ".stylelintcache"
    "node_modules/.cache"
    "coverage"
    ".nyc_output"
    ".jest"
    "__pycache__"
    "*.pyc"
    "*.pyo"
    "*.pyd"
    ".pytest_cache"
    ".mypy_cache"
    ".coverage"
    "htmlcov"
    ".tox"
    ".venv"
    "venv"
    "env"
    ".env"
    ".env.local"
    ".env.development.local"
    ".env.test.local"
    ".env.production.local"
)

BUILD_DIRS=(
    "dist"
    "build"
    "out"
    ".next"
    "target"
    "*.egg-info"
    "*.egg"
    "*.whl"
    "*.tar.gz"
    "*.zip"
)

TEST_DIRS=(
    "coverage"
    ".nyc_output"
    ".jest"
    "test-results"
    "playwright-report"
    ".pytest_cache"
    "htmlcov"
    "*.coverage"
)

NODE_MODULES_DIRS=(
    "node_modules"
    "package-lock.json"
    "yarn.lock"
    "pnpm-lock.yaml"
    "bun.lockb"
)

PYTHON_DIRS=(
    "__pycache__"
    "*.pyc"
    "*.pyo"
    "*.pyd"
    ".pytest_cache"
    ".mypy_cache"
    ".coverage"
    "htmlcov"
    ".tox"
    "*.egg-info"
    "*.egg"
    "*.whl"
    "*.tar.gz"
    "*.zip"
)

DOCKER_DIRS=(
    "Dockerfile.dev"
    "docker-compose.override.yml"
    "docker-compose.dev.yml"
    "docker-compose.test.yml"
    ".dockerignore.dev"
)

TEMP_FILES=(
    "*.log"
    "*.tmp"
    "*.temp"
    ".DS_Store"
    "Thumbs.db"
    "*.swp"
    "*.swo"
    "*~"
    "*.bak"
    "*.backup"
    "*.orig"
    "*.rej"
)

# 정리 함수들
clean_cache() {
    log_info "캐시 파일 정리 중..."
    for pattern in "${CACHE_DIRS[@]}"; do
        if [[ $pattern == *"*"* ]]; then
            # 와일드카드 패턴
            find . -name "$pattern" -type f -delete 2>/dev/null || true
            find . -name "$pattern" -type d -exec rm -rf {} + 2>/dev/null || true
        else
            # 일반 디렉토리/파일
            if [ -d "$pattern" ]; then
                rm -rf "$pattern"
                log_success "제거됨: $pattern"
            elif [ -f "$pattern" ]; then
                rm -f "$pattern"
                log_success "제거됨: $pattern"
            fi
        fi
    done
}

clean_build() {
    log_info "빌드 파일 정리 중..."
    for pattern in "${BUILD_DIRS[@]}"; do
        if [[ $pattern == *"*"* ]]; then
            find . -name "$pattern" -type f -delete 2>/dev/null || true
            find . -name "$pattern" -type d -exec rm -rf {} + 2>/dev/null || true
        else
            if [ -d "$pattern" ]; then
                rm -rf "$pattern"
                log_success "제거됨: $pattern"
            fi
        fi
    done
}

clean_test() {
    log_info "테스트 파일 정리 중..."
    for pattern in "${TEST_DIRS[@]}"; do
        if [[ $pattern == *"*"* ]]; then
            find . -name "$pattern" -type f -delete 2>/dev/null || true
            find . -name "$pattern" -type d -exec rm -rf {} + 2>/dev/null || true
        else
            if [ -d "$pattern" ]; then
                rm -rf "$pattern"
                log_success "제거됨: $pattern"
            fi
        fi
    done
}

clean_node_modules() {
    log_info "Node.js 관련 파일 정리 중..."
    for pattern in "${NODE_MODULES_DIRS[@]}"; do
        if [ -d "$pattern" ]; then
            rm -rf "$pattern"
            log_success "제거됨: $pattern"
        elif [ -f "$pattern" ]; then
            rm -f "$pattern"
            log_success "제거됨: $pattern"
        fi
    done
}

clean_python() {
    log_info "Python 관련 파일 정리 중..."
    for pattern in "${PYTHON_DIRS[@]}"; do
        if [[ $pattern == *"*"* ]]; then
            find . -name "$pattern" -type f -delete 2>/dev/null || true
            find . -name "$pattern" -type d -exec rm -rf {} + 2>/dev/null || true
        else
            if [ -d "$pattern" ]; then
                rm -rf "$pattern"
                log_success "제거됨: $pattern"
            elif [ -f "$pattern" ]; then
                rm -f "$pattern"
                log_success "제거됨: $pattern"
            fi
        fi
    done
}

clean_docker() {
    log_info "Docker 관련 파일 정리 중..."
    for pattern in "${DOCKER_DIRS[@]}"; do
        if [ -f "$pattern" ]; then
            rm -f "$pattern"
            log_success "제거됨: $pattern"
        fi
    done
}

clean_temp_files() {
    log_info "임시 파일 정리 중..."
    for pattern in "${TEMP_FILES[@]}"; do
        find . -name "$pattern" -type f -delete 2>/dev/null || true
    done
    log_success "임시 파일 정리 완료"
}

clean_backups() {
    log_info "백업 파일 정리 중..."
    # 7일 이상 된 백업 파일 삭제
    find . -name "backup_*" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.backup" -type f -mtime +7 -delete 2>/dev/null || true
    log_success "7일 이상 된 백업 파일 정리 완료"
}

clean_logs() {
    log_info "로그 파일 정리 중..."
    find . -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    find . -name "logs" -type d -exec rm -rf {} + 2>/dev/null || true
    log_success "로그 파일 정리 완료"
}

# 디스크 사용량 확인
check_disk_usage() {
    log_info "정리 전 디스크 사용량:"
    du -sh . 2>/dev/null || echo "디스크 사용량 확인 불가"
}

# 정리 후 디스크 사용량 확인
check_disk_usage_after() {
    log_info "정리 후 디스크 사용량:"
    du -sh . 2>/dev/null || echo "디스크 사용량 확인 불가"
}

# 특정 디렉토리 정리
clean_directory() {
    local dir="$1"
    local dir_type="$2"
    
    if [ -d "$dir" ]; then
        log_info "$dir_type 디렉토리 정리 중: $dir"
        cd "$dir"
        
        case $CLEANUP_TYPE in
            "cache")
                clean_cache
                clean_temp_files
                ;;
            "build")
                clean_build
                clean_temp_files
                ;;
            "test")
                clean_test
                clean_temp_files
                ;;
            "node_modules")
                clean_node_modules
                ;;
            "python")
                clean_python
                clean_temp_files
                ;;
            "docker")
                clean_docker
                ;;
            "all")
                clean_cache
                clean_build
                clean_test
                clean_temp_files
                clean_backups
                clean_logs
                ;;
        esac
        
        cd "$PROJECT_ROOT"
    fi
}

# 메인 정리 로직
main() {
    log_info "Your Program 전체 프로젝트 정리 시작"
    log_info "정리 타입: $CLEANUP_TYPE"
    log_info "프로젝트 루트: $PROJECT_ROOT"
    
    check_disk_usage
    
    # 루트 디렉토리 정리
    log_info "루트 디렉토리 정리 중..."
    case $CLEANUP_TYPE in
        "cache")
            clean_cache
            clean_temp_files
            ;;
        "build")
            clean_build
            clean_temp_files
            ;;
        "test")
            clean_test
            clean_temp_files
            ;;
        "node_modules")
            clean_node_modules
            ;;
        "python")
            clean_python
            clean_temp_files
            ;;
        "docker")
            clean_docker
            ;;
        "all")
            clean_cache
            clean_build
            clean_test
            clean_temp_files
            clean_backups
            clean_logs
            ;;
        *)
            log_error "잘못된 정리 타입입니다. 사용법: $0 [all|cache|build|test|node_modules|python|docker]"
            exit 1
            ;;
    esac
    
    # 서브 디렉토리 정리
    log_info "서브 디렉토리 정리 중..."
    
    # Frontend 디렉토리
    clean_directory "frontend" "Frontend"
    
    # Mobile 앱 디렉토리
    clean_directory "mobile_app" "Mobile App"
    
    # AI 모듈 디렉토리
    clean_directory "ai_modules" "AI Modules"
    
    # 백업 디렉토리들
    for backup_dir in backup_*; do
        if [ -d "$backup_dir" ]; then
            clean_directory "$backup_dir" "Backup"
        fi
    done
    
    check_disk_usage_after
    
    log_success "전체 프로젝트 정리 완료!"
    
    # 다음 단계 안내
    case $CLEANUP_TYPE in
        "node_modules")
            log_info "다음 단계:"
            log_info "  Frontend: cd frontend && npm install"
            log_info "  Mobile: cd mobile_app && npm install"
            ;;
        "python")
            log_info "다음 단계:"
            log_info "  AI 모듈: pip install -r ai_requirements.txt"
            ;;
        "all")
            log_info "다음 단계:"
            log_info "  Frontend: cd frontend && npm install"
            log_info "  Mobile: cd mobile_app && npm install"
            log_info "  AI 모듈: pip install -r ai_requirements.txt"
            log_info "  전체 실행: ./scripts/start_all.sh"
            ;;
    esac
}

# 스크립트 실행
main "$@" 
