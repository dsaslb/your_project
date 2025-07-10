#!/bin/bash

# Your Program 전체 프로젝트 시작 스크립트
# 사용법: ./scripts/start_all.sh [environment]
# environment: dev, staging, prod (기본값: dev)

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

# 환경 변수 설정
ENVIRONMENT=${1:-dev}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 환경별 설정
case $ENVIRONMENT in
    "dev")
        NODE_ENV="development"
        FLASK_ENV="development"
        API_URL="http://localhost:5001"
        WS_URL="ws://localhost:5001"
        FRONTEND_PORT=3000
        BACKEND_PORT=5001
        AI_PORT=8002
        MOBILE_PORT=19000
        ;;
    "staging")
        NODE_ENV="staging"
        FLASK_ENV="production"
        API_URL="https://staging-api.yourprogram.com"
        WS_URL="wss://staging-api.yourprogram.com"
        FRONTEND_PORT=3000
        BACKEND_PORT=5001
        AI_PORT=8002
        MOBILE_PORT=19000
        ;;
    "prod")
        NODE_ENV="production"
        FLASK_ENV="production"
        API_URL="https://api.yourprogram.com"
        WS_URL="wss://api.yourprogram.com"
        FRONTEND_PORT=3000
        BACKEND_PORT=5001
        AI_PORT=8002
        MOBILE_PORT=19000
        ;;
    *)
        log_error "잘못된 환경입니다. 사용법: $0 [dev|staging|prod]"
        exit 1
        ;;
esac

# PID 파일 관리
PID_DIR="$PROJECT_ROOT/pids"
mkdir -p "$PID_DIR"

# 프로세스 종료 함수
cleanup() {
    log_info "프로세스 정리 중..."
    
    # PID 파일들에서 프로세스 종료
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                log_info "프로세스 종료: $pid"
                kill "$pid"
                sleep 2
                if kill -0 "$pid" 2>/dev/null; then
                    log_warning "강제 종료: $pid"
                    kill -9 "$pid"
                fi
            fi
            rm -f "$pid_file"
        fi
    done
    
    log_success "프로세스 정리 완료"
}

# 트랩 설정
trap cleanup EXIT INT TERM

# 의존성 확인
check_dependencies() {
    log_info "의존성 확인 중..."
    
    # Node.js 확인
    if ! command -v node &> /dev/null; then
        log_error "Node.js가 설치되지 않았습니다."
        exit 1
    fi
    
    # npm 확인
    if ! command -v npm &> /dev/null; then
        log_error "npm이 설치되지 않았습니다."
        exit 1
    fi
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되지 않았습니다."
        exit 1
    fi
    
    # pip 확인
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3가 설치되지 않았습니다."
        exit 1
    fi
    
    log_success "의존성 확인 완료"
}

# 포트 확인
check_ports() {
    log_info "포트 사용량 확인 중..."
    
    local ports=($FRONTEND_PORT $BACKEND_PORT $AI_PORT $MOBILE_PORT)
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_warning "포트 $port가 이미 사용 중입니다."
            read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    done
    
    log_success "포트 확인 완료"
}

# 환경 변수 파일 생성
setup_environment() {
    log_info "환경 변수 설정 중..."
    
    # Frontend 환경 변수
    cat > "$PROJECT_ROOT/your_program_frontend/.env.local" << EOF
NEXT_PUBLIC_API_URL=$API_URL
NEXT_PUBLIC_WS_URL=$WS_URL
NODE_ENV=$NODE_ENV
EOF
    
    # Backend 환경 변수
    cat > "$PROJECT_ROOT/.env" << EOF
FLASK_ENV=$FLASK_ENV
DATABASE_URL=postgresql://user:password@localhost/your_program
SECRET_KEY=your-secret-key-here
API_URL=$API_URL
WS_URL=$WS_URL
AI_SERVER_URL=http://localhost:$AI_PORT
EOF
    
    # AI 서버 환경 변수
    cat > "$PROJECT_ROOT/.env.ai" << EOF
DATABASE_URL=postgresql://user:password@localhost/your_program_ai
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-ai-secret-key-here
MODEL_PATH=$PROJECT_ROOT/models
EOF
    
    log_success "환경 변수 설정 완료"
}

# 백엔드 시작
start_backend() {
    log_info "백엔드 서버 시작 중..."
    
    cd "$PROJECT_ROOT"
    
    # 가상환경 활성화 (있는 경우)
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # 의존성 설치 확인
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        log_info "Python 가상환경 생성 중..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    # 데이터베이스 마이그레이션
    log_info "데이터베이스 마이그레이션 중..."
    flask db upgrade || log_warning "마이그레이션 실패 (무시됨)"
    
    # 백엔드 서버 시작
    nohup python app.py > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
    echo $! > "$PID_DIR/backend.pid"
    
    log_success "백엔드 서버 시작됨 (PID: $(cat $PID_DIR/backend.pid))"
}

# AI 서버 시작
start_ai_server() {
    log_info "AI 서버 시작 중..."
    
    cd "$PROJECT_ROOT"
    
    # AI 의존성 설치 확인
    if [ ! -f "ai_requirements_installed" ]; then
        log_info "AI 의존성 설치 중..."
        pip install -r ai_requirements.txt
        touch ai_requirements_installed
    fi
    
    # AI 서버 시작
    nohup python ai_server.py > "$PROJECT_ROOT/logs/ai_server.log" 2>&1 &
    echo $! > "$PID_DIR/ai_server.pid"
    
    log_success "AI 서버 시작됨 (PID: $(cat $PID_DIR/ai_server.pid))"
}

# 프론트엔드 시작
start_frontend() {
    log_info "프론트엔드 서버 시작 중..."
    
    cd "$PROJECT_ROOT/your_program_frontend"
    
    # 의존성 설치 확인
    if [ ! -d "node_modules" ]; then
        log_info "프론트엔드 의존성 설치 중..."
        npm install
    fi
    
    # 프론트엔드 서버 시작
    nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
    echo $! > "$PID_DIR/frontend.pid"
    
    log_success "프론트엔드 서버 시작됨 (PID: $(cat $PID_DIR/frontend.pid))"
}

# 모바일 앱 시작
start_mobile() {
    log_info "모바일 앱 개발 서버 시작 중..."
    
    cd "$PROJECT_ROOT/mobile_app"
    
    # 의존성 설치 확인
    if [ ! -d "node_modules" ]; then
        log_info "모바일 앱 의존성 설치 중..."
        npm install
    fi
    
    # Expo 서버 시작
    nohup npx expo start --port $MOBILE_PORT > "$PROJECT_ROOT/logs/mobile.log" 2>&1 &
    echo $! > "$PID_DIR/mobile.pid"
    
    log_success "모바일 앱 서버 시작됨 (PID: $(cat $PID_DIR/mobile.pid))"
}

# 서비스 상태 확인
check_services() {
    log_info "서비스 상태 확인 중..."
    
    local services=(
        "backend:http://localhost:$BACKEND_PORT/health"
        "ai_server:http://localhost:$AI_PORT/health"
        "frontend:http://localhost:$FRONTEND_PORT"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name url <<< "$service"
        
        # 서비스 응답 대기
        log_info "$name 서비스 응답 대기 중..."
        for i in {1..30}; do
            if curl -s "$url" > /dev/null 2>&1; then
                log_success "$name 서비스가 정상적으로 응답합니다."
                break
            fi
            
            if [ $i -eq 30 ]; then
                log_warning "$name 서비스 응답 없음 (무시됨)"
            else
                sleep 2
            fi
        done
    done
}

# 로그 디렉토리 생성
setup_logs() {
    log_info "로그 디렉토리 설정 중..."
    
    mkdir -p "$PROJECT_ROOT/logs"
    
    # 로그 파일 초기화
    touch "$PROJECT_ROOT/logs/backend.log"
    touch "$PROJECT_ROOT/logs/ai_server.log"
    touch "$PROJECT_ROOT/logs/frontend.log"
    touch "$PROJECT_ROOT/logs/mobile.log"
    
    log_success "로그 디렉토리 설정 완료"
}

# 메인 시작 로직
main() {
    log_info "Your Program 전체 프로젝트 시작"
    log_info "환경: $ENVIRONMENT"
    log_info "프로젝트 루트: $PROJECT_ROOT"
    log_info "타임스탬프: $TIMESTAMP"
    
    # 초기 설정
    check_dependencies
    check_ports
    setup_logs
    setup_environment
    
    # 서비스 시작
    start_backend
    sleep 5
    
    start_ai_server
    sleep 3
    
    start_frontend
    sleep 3
    
    start_mobile
    sleep 3
    
    # 서비스 상태 확인
    check_services
    
    # 시작 완료 메시지
    log_success "모든 서비스가 시작되었습니다!"
    echo
    echo "=== Your Program 서비스 정보 ==="
    echo "환경: $ENVIRONMENT"
    echo "프론트엔드: http://localhost:$FRONTEND_PORT"
    echo "백엔드 API: http://localhost:$BACKEND_PORT"
    echo "AI 서버: http://localhost:$AI_PORT"
    echo "모바일 앱: http://localhost:$MOBILE_PORT"
    echo "로그 디렉토리: $PROJECT_ROOT/logs"
    echo "PID 파일: $PID_DIR"
    echo
    echo "서비스 종료: Ctrl+C"
    echo "로그 확인: tail -f $PROJECT_ROOT/logs/*.log"
    echo
    
    # 프로세스 모니터링
    while true; do
        sleep 10
        
        # 프로세스 상태 확인
        for pid_file in "$PID_DIR"/*.pid; do
            if [ -f "$pid_file" ]; then
                pid=$(cat "$pid_file")
                service=$(basename "$pid_file" .pid)
                
                if ! kill -0 "$pid" 2>/dev/null; then
                    log_error "$service 프로세스가 종료되었습니다. (PID: $pid)"
                    rm -f "$pid_file"
                fi
            fi
        done
    done
}

# 스크립트 실행
main "$@" 