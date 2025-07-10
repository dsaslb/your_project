#!/bin/bash

# Your Program Frontend 정리 스크립트
# 사용법: ./scripts/cleanup.sh [type]
# type: all, cache, build, test, node_modules (기본값: all)

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
)

BUILD_DIRS=(
    "dist"
    "build"
    "out"
    ".next"
)

TEST_DIRS=(
    "coverage"
    ".nyc_output"
    ".jest"
    "test-results"
    "playwright-report"
)

NODE_MODULES_DIRS=(
    "node_modules"
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
)

# 정리 함수
clean_cache() {
    log_info "캐시 파일 정리 중..."
    for dir in "${CACHE_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            log_success "제거됨: $dir"
        fi
    done
}

clean_build() {
    log_info "빌드 파일 정리 중..."
    for dir in "${BUILD_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            log_success "제거됨: $dir"
        fi
    done
}

clean_test() {
    log_info "테스트 파일 정리 중..."
    for dir in "${TEST_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            log_success "제거됨: $dir"
        fi
    done
}

clean_node_modules() {
    log_info "node_modules 정리 중..."
    for dir in "${NODE_MODULES_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            log_success "제거됨: $dir"
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

clean_package_lock() {
    log_info "패키지 락 파일 정리 중..."
    if [ -f "package-lock.json" ]; then
        rm -f package-lock.json
        log_success "제거됨: package-lock.json"
    fi
    if [ -f "yarn.lock" ]; then
        rm -f yarn.lock
        log_success "제거됨: yarn.lock"
    fi
    if [ -f "pnpm-lock.yaml" ]; then
        rm -f pnpm-lock.yaml
        log_success "제거됨: pnpm-lock.yaml"
    fi
}

clean_env_files() {
    log_info "환경 변수 파일 정리 중..."
    for env_file in .env.local .env.development.local .env.test.local .env.production.local; do
        if [ -f "$env_file" ]; then
            rm -f "$env_file"
            log_success "제거됨: $env_file"
        fi
    done
}

clean_backups() {
    log_info "백업 파일 정리 중..."
    if [ -d "backups" ]; then
        # 7일 이상 된 백업 파일 삭제
        find backups -name "*.tar.gz" -mtime +7 -delete 2>/dev/null || true
        log_success "7일 이상 된 백업 파일 정리 완료"
    fi
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

# 메인 정리 로직
main() {
    log_info "Your Program Frontend 정리 시작"
    log_info "정리 타입: $CLEANUP_TYPE"
    
    check_disk_usage
    
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
            clean_package_lock
            ;;
        "all")
            clean_cache
            clean_build
            clean_test
            clean_temp_files
            clean_env_files
            clean_backups
            log_warning "node_modules는 수동으로 정리하세요: rm -rf node_modules"
            ;;
        *)
            log_error "잘못된 정리 타입입니다. 사용법: $0 [all|cache|build|test|node_modules]"
            exit 1
            ;;
    esac
    
    check_disk_usage_after
    
    log_success "정리 완료!"
    
    # 다음 단계 안내
    case $CLEANUP_TYPE in
        "node_modules")
            log_info "다음 단계: npm install"
            ;;
        "all")
            log_info "다음 단계: npm install && npm run dev"
            ;;
    esac
}

# 스크립트 실행
main "$@" 