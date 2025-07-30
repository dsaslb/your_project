#!/bin/bash

# SSL 인증서 관리 스크립트
# 사용법: ./scripts/manage_ssl.sh [renew|status|install]

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

# 도메인 추출
get_domain() {
    if [ -f "$PROJECT_ROOT/nginx/nginx.conf" ]; then
        grep -o 'server_name [^;]*' "$PROJECT_ROOT/nginx/nginx.conf" | head -1 | awk '{print $2}'
    else
        echo "your-domain.com"
    fi
}

DOMAIN=$(get_domain)

# SSL 인증서 상태 확인
check_ssl_status() {
    log_info "SSL 인증서 상태 확인 중..."
    
    SSL_DIR="$PROJECT_ROOT/nginx/ssl"
    
    if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
        log_success "SSL 인증서 파일이 존재합니다."
        
        # 인증서 정보 출력
        echo "인증서 정보:"
        openssl x509 -in "$SSL_DIR/cert.pem" -text -noout | grep -E "(Subject:|Not Before:|Not After:|DNS:)"
        
        # 만료일 확인
        EXPIRY=$(openssl x509 -in "$SSL_DIR/cert.pem" -noout -enddate | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
        CURRENT_EPOCH=$(date +%s)
        DAYS_LEFT=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
        
        if [ $DAYS_LEFT -gt 30 ]; then
            log_success "인증서가 $DAYS_LEFT일 후 만료됩니다."
        elif [ $DAYS_LEFT -gt 7 ]; then
            log_warning "인증서가 $DAYS_LEFT일 후 만료됩니다."
        else
            log_error "인증서가 $DAYS_LEFT일 후 만료됩니다. 즉시 갱신이 필요합니다."
        fi
    else
        log_warning "SSL 인증서 파일이 없습니다."
        log_info "인증서를 설치하려면: ./scripts/manage_ssl.sh install"
    fi
}

# Let's Encrypt 인증서 설치
install_letsencrypt() {
    log_info "Let's Encrypt SSL 인증서 설치 중..."
    
    # Certbot 설치 확인
    if ! command -v certbot &> /dev/null; then
        log_info "Certbot 설치 중..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot python3-certbot-nginx
        else
            log_error "패키지 매니저를 찾을 수 없습니다."
            log_info "수동으로 Certbot을 설치하세요: https://certbot.eff.org/"
            return 1
        fi
    fi
    
    # 이메일 주소 입력
    read -p "Let's Encrypt 알림을 받을 이메일 주소를 입력하세요: " EMAIL
    
    # SSL 인증서 생성
    log_info "SSL 인증서 생성 중..."
    
    # 메인 도메인 인증서
    sudo certbot certonly --standalone \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        -d "admin.$DOMAIN"
    
    # 인증서 파일 복사
    SSL_DIR="$PROJECT_ROOT/nginx/ssl"
    mkdir -p "$SSL_DIR"
    
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"
    
    # 권한 설정
    sudo chown -R $(whoami):$(whoami) "$SSL_DIR"
    chmod 600 "$SSL_DIR/key.pem"
    chmod 644 "$SSL_DIR/cert.pem"
    
    log_success "SSL 인증서 설치 완료"
}

# SSL 인증서 갱신
renew_ssl() {
    log_info "SSL 인증서 갱신 중..."
    
    # Certbot으로 갱신
    sudo certbot renew --quiet
    
    # 인증서 파일 복사
    SSL_DIR="$PROJECT_ROOT/nginx/ssl"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"
    
    # 권한 설정
    sudo chown -R $(whoami):$(whoami) "$SSL_DIR"
    chmod 600 "$SSL_DIR/key.pem"
    chmod 644 "$SSL_DIR/cert.pem"
    
    # Nginx 재시작
    cd "$PROJECT_ROOT"
    if [ -f "docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.prod.yml restart nginx
    fi
    
    log_success "SSL 인증서 갱신 완료"
}

# 자체 서명 인증서 생성
create_self_signed() {
    log_info "자체 서명 SSL 인증서 생성 중..."
    
    SSL_DIR="$PROJECT_ROOT/nginx/ssl"
    mkdir -p "$SSL_DIR"
    
    # 자체 서명 인증서 생성
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/key.pem" \
        -out "$SSL_DIR/cert.pem" \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=YourProgram/CN=$DOMAIN"
    
    # 권한 설정
    chmod 600 "$SSL_DIR/key.pem"
    chmod 644 "$SSL_DIR/cert.pem"
    
    log_success "자체 서명 SSL 인증서 생성 완료"
    log_warning "이 인증서는 개발용입니다. 프로덕션에서는 Let's Encrypt를 사용하세요."
}

# SSL 설정 테스트
test_ssl() {
    log_info "SSL 설정 테스트 중..."
    
    # 인증서 유효성 확인
    if [ -f "$PROJECT_ROOT/nginx/ssl/cert.pem" ]; then
        echo "인증서 유효성 확인:"
        openssl x509 -in "$PROJECT_ROOT/nginx/ssl/cert.pem" -text -noout | head -20
        
        echo ""
        echo "SSL 연결 테스트:"
        echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates
    else
        log_error "SSL 인증서 파일이 없습니다."
    fi
}

# 자동 갱신 설정
setup_auto_renewal() {
    log_info "SSL 인증서 자동 갱신 설정 중..."
    
    # 갱신 스크립트 생성
    cat > "$PROJECT_ROOT/scripts/renew_ssl.sh" << 'EOF'
#!/bin/bash

# SSL 인증서 자동 갱신 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOMAIN=$(grep -o 'server_name [^;]*' "$PROJECT_ROOT/nginx/nginx.conf" | head -1 | awk '{print $2}')

echo "$(date): SSL 인증서 갱신 시작 - $DOMAIN"

# 인증서 갱신
sudo certbot renew --quiet

# 인증서 파일 복사
SSL_DIR="$PROJECT_ROOT/nginx/ssl"
sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"

# 권한 설정
sudo chown -R $(whoami):$(whoami) "$SSL_DIR"
chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"

# Nginx 재시작
cd "$PROJECT_ROOT"
if [ -f "docker-compose.prod.yml" ]; then
    docker-compose -f docker-compose.prod.yml restart nginx
fi

echo "$(date): SSL 인증서 갱신 완료"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/renew_ssl.sh"
    
    # Crontab에 자동 갱신 추가
    (crontab -l 2>/dev/null | grep -v "renew_ssl.sh"; echo "0 12 * * * $PROJECT_ROOT/scripts/renew_ssl.sh") | crontab -
    
    log_success "SSL 인증서 자동 갱신 설정 완료"
    log_info "매일 오후 12시에 자동으로 갱신됩니다."
}

# 메인 함수
main() {
    case "${1:-status}" in
        "status")
            check_ssl_status
            ;;
        "install")
            install_letsencrypt
            ;;
        "renew")
            renew_ssl
            ;;
        "self-signed")
            create_self_signed
            ;;
        "test")
            test_ssl
            ;;
        "auto-renewal")
            setup_auto_renewal
            ;;
        *)
            echo "사용법: $0 [status|install|renew|self-signed|test|auto-renewal]"
            echo ""
            echo "명령어:"
            echo "  status       - SSL 인증서 상태 확인"
            echo "  install      - Let's Encrypt 인증서 설치"
            echo "  renew        - SSL 인증서 갱신"
            echo "  self-signed  - 자체 서명 인증서 생성 (개발용)"
            echo "  test         - SSL 설정 테스트"
            echo "  auto-renewal - 자동 갱신 설정"
            ;;
    esac
}

# 스크립트 실행
main "$@" 