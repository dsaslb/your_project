#!/bin/bash

# DNS 설정 검증 스크립트
# 사용법: ./scripts/verify_dns.sh [your-domain.com]

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

# 도메인 설정
if [ $# -eq 0 ]; then
    # Nginx 설정에서 도메인 추출
    if [ -f "$PROJECT_ROOT/nginx/nginx.conf" ]; then
        DOMAIN=$(grep -o 'server_name [^;]*' "$PROJECT_ROOT/nginx/nginx.conf" | head -1 | awk '{print $2}')
    else
        log_error "도메인을 입력해주세요."
        log_info "사용법: $0 your-domain.com"
        exit 1
    fi
else
    DOMAIN=$1
fi

ADMIN_DOMAIN="admin.$DOMAIN"

log_info "DNS 설정 검증 시작: $DOMAIN"

# DNS 조회 함수
check_dns() {
    local hostname=$1
    local record_type=${2:-A}
    
    log_info "DNS $record_type 레코드 확인: $hostname"
    
    if command -v nslookup &> /dev/null; then
        nslookup -type=$record_type $hostname
    elif command -v dig &> /dev/null; then
        dig $record_type $hostname
    else
        log_error "nslookup 또는 dig 명령어가 없습니다."
        return 1
    fi
}

# HTTP 응답 확인
check_http_response() {
    local url=$1
    local description=$2
    
    log_info "HTTP 응답 확인: $description"
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        if [ "$response" = "200" ] || [ "$response" = "301" ] || [ "$response" = "302" ]; then
            log_success "$description: HTTP $response"
        else
            log_warning "$description: HTTP $response (예상: 200, 301, 302)"
        fi
    else
        log_warning "curl 명령어가 없습니다. 수동으로 확인하세요: $url"
    fi
}

# SSL 인증서 확인
check_ssl_certificate() {
    local hostname=$1
    local description=$2
    
    log_info "SSL 인증서 확인: $description"
    
    if command -v openssl &> /dev/null; then
        cert_info=$(echo | openssl s_client -servername "$hostname" -connect "$hostname:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo "ERROR")
        
        if [ "$cert_info" != "ERROR" ]; then
            log_success "$description: SSL 인증서 유효"
            echo "$cert_info"
        else
            log_warning "$description: SSL 인증서 없음 또는 오류"
        fi
    else
        log_warning "openssl 명령어가 없습니다. 수동으로 확인하세요: https://$hostname"
    fi
}

# 포트 스캔
check_ports() {
    local hostname=$1
    local description=$2
    
    log_info "포트 확인: $description"
    
    # HTTP (80)
    if command -v nc &> /dev/null; then
        if nc -z "$hostname" 80 2>/dev/null; then
            log_success "$description: HTTP (80) 포트 열림"
        else
            log_warning "$description: HTTP (80) 포트 닫힘"
        fi
        
        # HTTPS (443)
        if nc -z "$hostname" 443 2>/dev/null; then
            log_success "$description: HTTPS (443) 포트 열림"
        else
            log_warning "$description: HTTPS (443) 포트 닫힘"
        fi
    else
        log_warning "nc 명령어가 없습니다. 수동으로 포트를 확인하세요."
    fi
}

# 지연 시간 측정
check_latency() {
    local hostname=$1
    local description=$2
    
    log_info "지연 시간 측정: $description"
    
    if command -v ping &> /dev/null; then
        ping_result=$(ping -c 3 "$hostname" 2>/dev/null | tail -1 | awk '{print $4}' | cut -d'/' -f2)
        if [ ! -z "$ping_result" ]; then
            log_success "$description: 평균 지연 시간 ${ping_result}ms"
        else
            log_warning "$description: 지연 시간 측정 실패"
        fi
    else
        log_warning "ping 명령어가 없습니다."
    fi
}

# DNS 전파 확인
check_dns_propagation() {
    log_info "DNS 전파 확인..."
    
    # 여러 DNS 서버에서 확인
    dns_servers=("8.8.8.8" "1.1.1.1" "208.67.222.222")
    
    for dns_server in "${dns_servers[@]}"; do
        log_info "DNS 서버 $dns_server에서 확인:"
        if command -v nslookup &> /dev/null; then
            nslookup "$DOMAIN" "$dns_server" 2>/dev/null || log_warning "DNS 서버 $dns_server에서 조회 실패"
        fi
        echo ""
    done
}

# 메인 검증 함수
main_verification() {
    log_info "=== DNS 설정 검증 시작 ==="
    
    # 기본 도메인 확인
    check_dns "$DOMAIN"
    echo ""
    
    # www 서브도메인 확인
    check_dns "www.$DOMAIN"
    echo ""
    
    # admin 서브도메인 확인
    check_dns "$ADMIN_DOMAIN"
    echo ""
    
    # DNS 전파 확인
    check_dns_propagation
    echo ""
    
    # 포트 확인
    check_ports "$DOMAIN" "메인 도메인"
    echo ""
    check_ports "$ADMIN_DOMAIN" "관리자 도메인"
    echo ""
    
    # 지연 시간 측정
    check_latency "$DOMAIN" "메인 도메인"
    echo ""
    check_latency "$ADMIN_DOMAIN" "관리자 도메인"
    echo ""
    
    # HTTP 응답 확인
    check_http_response "http://$DOMAIN" "메인 도메인 (HTTP)"
    check_http_response "https://$DOMAIN" "메인 도메인 (HTTPS)"
    check_http_response "http://www.$DOMAIN" "WWW 서브도메인 (HTTP)"
    check_http_response "https://www.$DOMAIN" "WWW 서브도메인 (HTTPS)"
    check_http_response "http://$ADMIN_DOMAIN" "관리자 도메인 (HTTP)"
    check_http_response "https://$ADMIN_DOMAIN" "관리자 도메인 (HTTPS)"
    echo ""
    
    # SSL 인증서 확인
    check_ssl_certificate "$DOMAIN" "메인 도메인"
    echo ""
    check_ssl_certificate "$ADMIN_DOMAIN" "관리자 도메인"
    echo ""
    
    log_info "=== DNS 설정 검증 완료 ==="
}

# 문제 해결 가이드 생성
generate_troubleshooting_guide() {
    log_info "문제 해결 가이드 생성..."
    
    cat > "$PROJECT_ROOT/DNS_TROUBLESHOOTING.md" << EOF
# DNS 문제 해결 가이드

## 도메인: $DOMAIN

### 일반적인 문제들

#### 1. DNS 조회 실패
**증상**: nslookup 또는 dig에서 응답 없음
**해결책**:
- DNS 설정이 올바른지 확인
- DNS 전파 대기 (최대 48시간)
- DNS 서버 변경 확인

#### 2. SSL 인증서 오류
**증상**: 브라우저에서 보안 경고
**해결책**:
- Let's Encrypt 인증서 설치: \`./scripts/manage_ssl.sh install\`
- 인증서 갱신: \`./scripts/manage_ssl.sh renew\`

#### 3. 포트 연결 실패
**증상**: 웹사이트 접속 불가
**해결책**:
- 방화벽 설정 확인
- 서버 실행 상태 확인
- 포트 포워딩 설정 확인

#### 4. 지연 시간 높음
**증상**: 웹사이트 로딩 느림
**해결책**:
- CDN 사용 고려
- 서버 위치 최적화
- 네트워크 설정 확인

### 확인 명령어

\`\`\`bash
# DNS 확인
nslookup $DOMAIN
dig $DOMAIN

# 포트 확인
nc -zv $DOMAIN 80
nc -zv $DOMAIN 443

# SSL 인증서 확인
openssl s_client -connect $DOMAIN:443 -servername $DOMAIN

# 지연 시간 확인
ping $DOMAIN
\`\`\`

### 지원 도구

- **DNS 전파 확인**: https://www.whatsmydns.net/
- **SSL 인증서 확인**: https://www.ssllabs.com/ssltest/
- **포트 스캔**: https://www.yougetsignal.com/tools/open-ports/

### 연락처

문제가 지속되면 시스템 관리자에게 문의하세요.
EOF
    
    log_success "문제 해결 가이드 생성 완료: DNS_TROUBLESHOOTING.md"
}

# 메인 함수
main() {
    # 메인 검증 실행
    main_verification
    
    # 문제 해결 가이드 생성
    generate_troubleshooting_guide
    
    log_success "DNS 설정 검증 완료!"
    log_info ""
    log_info "다음 단계:"
    log_info "1. DNS_TROUBLESHOOTING.md 파일을 확인하세요"
    log_info "2. 문제가 있으면 해결 후 다시 검증하세요"
    log_info "3. 모든 검증이 통과하면 SSL 인증서를 설치하세요"
    log_info "   ./scripts/manage_ssl.sh install"
}

# 스크립트 실행
main "$@" 