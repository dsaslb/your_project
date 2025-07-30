#!/bin/bash

# 도메인 설정 스크립트
# 사용법: ./scripts/setup_domain.sh your-domain.com

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

# 도메인 확인
if [ $# -eq 0 ]; then
    log_error "도메인을 입력해주세요."
    log_info "사용법: $0 your-domain.com"
    exit 1
fi

DOMAIN=$1
ADMIN_DOMAIN="admin.$DOMAIN"

log_info "도메인 설정 시작: $DOMAIN"
log_info "관리자 도메인: $ADMIN_DOMAIN"

# DNS 설정 가이드
setup_dns_guide() {
    log_info "DNS 설정 가이드 생성..."
    
    cat > "$PROJECT_ROOT/DNS_SETUP_GUIDE.md" << EOF
# DNS 설정 가이드

## 도메인: $DOMAIN

### A 레코드 설정
다음 A 레코드를 DNS 관리자에서 설정하세요:

\`\`\`
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 300

Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 300

Type: A
Name: admin
Value: YOUR_SERVER_IP
TTL: 300
\`\`\`

### CNAME 레코드 설정 (선택사항)
\`\`\`
Type: CNAME
Name: api
Value: $DOMAIN
TTL: 300
\`\`\`

### 확인 방법
설정 후 다음 명령어로 확인하세요:
\`\`\`
nslookup $DOMAIN
nslookup www.$DOMAIN
nslookup admin.$DOMAIN
\`\`\`

### 서버 IP 확인
현재 서버 IP: \$(curl -s ifconfig.me)
EOF
    
    log_success "DNS 설정 가이드 생성 완료: DNS_SETUP_GUIDE.md"
}

# Nginx 설정 업데이트
update_nginx_config() {
    log_info "Nginx 설정 업데이트..."
    
    # Nginx 설정 파일 백업
    cp "$PROJECT_ROOT/nginx/nginx.conf" "$PROJECT_ROOT/nginx/nginx.conf.backup"
    
    # 도메인으로 설정 파일 업데이트
    sed -i "s/your-domain.com/$DOMAIN/g" "$PROJECT_ROOT/nginx/nginx.conf"
    sed -i "s/admin.your-domain.com/$ADMIN_DOMAIN/g" "$PROJECT_ROOT/nginx/nginx.conf"
    
    log_success "Nginx 설정 업데이트 완료"
}

# Let's Encrypt SSL 인증서 설정
setup_letsencrypt() {
    log_info "Let's Encrypt SSL 인증서 설정..."
    
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
    
    # SSL 인증서 생성
    log_info "SSL 인증서 생성 중..."
    
    # 메인 도메인 인증서
    sudo certbot certonly --standalone \
        --email admin@$DOMAIN \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN \
        -d $ADMIN_DOMAIN
    
    # 인증서 파일 복사
    SSL_DIR="$PROJECT_ROOT/nginx/ssl"
    mkdir -p "$SSL_DIR"
    
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$SSL_DIR/cert.pem"
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem "$SSL_DIR/key.pem"
    
    # 권한 설정
    sudo chown -R $(whoami):$(whoami) "$SSL_DIR"
    chmod 600 "$SSL_DIR/key.pem"
    chmod 644 "$SSL_DIR/cert.pem"
    
    log_success "SSL 인증서 설정 완료"
}

# 자동 갱신 스크립트 생성
setup_auto_renewal() {
    log_info "SSL 인증서 자동 갱신 설정..."
    
    cat > "$PROJECT_ROOT/scripts/renew_ssl.sh" << 'EOF'
#!/bin/bash

# SSL 인증서 자동 갱신 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOMAIN=$(grep -o 'server_name [^;]*' "$PROJECT_ROOT/nginx/nginx.conf" | head -1 | awk '{print $2}')

echo "SSL 인증서 갱신 시작: $DOMAIN"

# 인증서 갱신
sudo certbot renew --quiet

# 인증서 파일 복사
SSL_DIR="$PROJECT_ROOT/nginx/ssl"
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$SSL_DIR/cert.pem"
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem "$SSL_DIR/key.pem"

# 권한 설정
sudo chown -R $(whoami):$(whoami) "$SSL_DIR"
chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"

# Nginx 재시작
cd "$PROJECT_ROOT"
docker-compose -f docker-compose.prod.yml restart nginx

echo "SSL 인증서 갱신 완료"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/renew_ssl.sh"
    
    # Crontab에 자동 갱신 추가
    (crontab -l 2>/dev/null; echo "0 12 * * * $PROJECT_ROOT/scripts/renew_ssl.sh") | crontab -
    
    log_success "SSL 인증서 자동 갱신 설정 완료"
}

# 환경 변수 파일 업데이트
update_env_file() {
    log_info "환경 변수 파일 업데이트..."
    
    if [ -f "$PROJECT_ROOT/.env.production" ]; then
        # 도메인 설정 업데이트
        sed -i "s/your-domain.com/$DOMAIN/g" "$PROJECT_ROOT/.env.production"
        sed -i "s/admin.your-domain.com/$ADMIN_DOMAIN/g" "$PROJECT_ROOT/.env.production"
        
        log_success "환경 변수 파일 업데이트 완료"
    else
        log_warning ".env.production 파일이 없습니다."
        log_info "config/production.env.example을 .env.production로 복사하세요."
    fi
}

# 프론트엔드 설정 업데이트
update_frontend_config() {
    log_info "프론트엔드 설정 업데이트..."
    
    # Next.js 설정 업데이트
    if [ -f "$PROJECT_ROOT/frontend/next.config.js" ]; then
        # API URL 업데이트
        sed -i "s|https://api.your-domain.com|https://$DOMAIN|g" "$PROJECT_ROOT/frontend/next.config.js"
        
        log_success "프론트엔드 설정 업데이트 완료"
    fi
    
    # 환경 변수 파일 업데이트
    if [ -f "$PROJECT_ROOT/frontend/.env.local" ]; then
        sed -i "s|https://api.your-domain.com|https://$DOMAIN|g" "$PROJECT_ROOT/frontend/.env.local"
    fi
}

# 헬스체크 스크립트 생성
create_health_check() {
    log_info "도메인 헬스체크 스크립트 생성..."
    
    cat > "$PROJECT_ROOT/scripts/check_domain.sh" << EOF
#!/bin/bash

# 도메인 헬스체크 스크립트

set -e

DOMAIN="$DOMAIN"
ADMIN_DOMAIN="$ADMIN_DOMAIN"

echo "도메인 헬스체크 시작..."

# DNS 확인
echo "DNS 확인 중..."
nslookup \$DOMAIN
nslookup www.\$DOMAIN
nslookup \$ADMIN_DOMAIN

# SSL 인증서 확인
echo "SSL 인증서 확인 중..."
echo | openssl s_client -servername \$DOMAIN -connect \$DOMAIN:443 2>/dev/null | openssl x509 -noout -dates

# HTTP 응답 확인
echo "HTTP 응답 확인 중..."
curl -I https://\$DOMAIN
curl -I https://www.\$DOMAIN
curl -I https://\$ADMIN_DOMAIN

echo "도메인 헬스체크 완료"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/check_domain.sh"
    
    log_success "도메인 헬스체크 스크립트 생성 완료"
}

# 메인 함수
main() {
    log_info "도메인 설정 프로세스 시작: $DOMAIN"
    
    # DNS 설정 가이드 생성
    setup_dns_guide
    
    # Nginx 설정 업데이트
    update_nginx_config
    
    # 환경 변수 파일 업데이트
    update_env_file
    
    # 프론트엔드 설정 업데이트
    update_frontend_config
    
    # 헬스체크 스크립트 생성
    create_health_check
    
    log_success "도메인 설정 완료!"
    log_info ""
    log_info "다음 단계:"
    log_info "1. DNS_SETUP_GUIDE.md 파일을 확인하여 DNS 설정을 완료하세요"
    log_info "2. DNS 전파 후 SSL 인증서를 설정하세요:"
    log_info "   sudo ./scripts/setup_domain.sh $DOMAIN"
    log_info "3. 도메인 헬스체크를 실행하세요:"
    log_info "   ./scripts/check_domain.sh"
    log_info ""
    log_info "애플리케이션 URL: https://$DOMAIN"
    log_info "관리자 URL: https://$ADMIN_DOMAIN"
}

# 스크립트 실행
main "$@" 