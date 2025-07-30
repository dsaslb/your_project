# 🌐 도메인 설정 완전 가이드

**작성일**: 2025년 7월 29일  
**대상**: Your Program 엔터프라이즈급 웹 애플리케이션  
**상태**: 준비 완료 ✅

## 📋 개요

Your Program 애플리케이션을 실제 도메인으로 연결하고 SSL 인증서를 설정하는 완전한 가이드입니다.

## 🎯 설정할 도메인 구조

```
your-domain.com          # 메인 도메인
├── www.your-domain.com  # WWW 서브도메인
├── admin.your-domain.com # 관리자 도메인
└── api.your-domain.com  # API 서브도메인 (선택사항)
```

## 🚀 단계별 설정 가이드

### 1단계: 도메인 준비

#### 1.1 도메인 구매
- **추천 도메인 등록소**:
  - Namecheap (저렴하고 안정적)
  - GoDaddy (인터페이스 친화적)
  - Google Domains (간단하고 안전)

#### 1.2 도메인 선택 팁
- **짧고 기억하기 쉬운 이름**
- **브랜드와 관련된 이름**
- **하이픈(-) 사용 자제**
- **국제화 고려 (.com, .co.kr 등)**

### 2단계: DNS 설정

#### 2.1 DNS 레코드 설정
도메인 관리자 페이지에서 다음 레코드를 설정하세요:

```bash
# A 레코드 (IPv4)
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

# CNAME 레코드 (선택사항)
Type: CNAME
Name: api
Value: your-domain.com
TTL: 300
```

#### 2.2 서버 IP 확인
```bash
# 현재 서버 IP 확인
curl ifconfig.me
# 또는
curl ipinfo.io/ip
```

### 3단계: 도메인 설정 스크립트 실행

#### 3.1 도메인 설정
```bash
# 도메인 설정 스크립트 실행
./scripts/setup_domain.sh your-domain.com
```

이 스크립트는 다음을 수행합니다:
- Nginx 설정 파일 업데이트
- 환경 변수 파일 업데이트
- 프론트엔드 설정 업데이트
- DNS 설정 가이드 생성

#### 3.2 DNS 전파 대기
- **일반적인 전파 시간**: 5분 ~ 24시간
- **확인 방법**: `./scripts/verify_dns.sh your-domain.com`

### 4단계: SSL 인증서 설정

#### 4.1 Let's Encrypt 인증서 설치
```bash
# SSL 인증서 설치
./scripts/manage_ssl.sh install
```

#### 4.2 자동 갱신 설정
```bash
# 자동 갱신 설정
./scripts/manage_ssl.sh auto-renewal
```

#### 4.3 SSL 상태 확인
```bash
# SSL 인증서 상태 확인
./scripts/manage_ssl.sh status
```

### 5단계: 배포 및 검증

#### 5.1 프로덕션 배포
```bash
# 프로덕션 환경 배포
./scripts/deploy_production.sh
```

#### 5.2 도메인 검증
```bash
# DNS 설정 검증
./scripts/verify_dns.sh your-domain.com
```

## 🔧 고급 설정

### CDN 설정 (선택사항)

#### Cloudflare 설정
1. Cloudflare 계정 생성
2. 도메인 추가
3. DNS 레코드 설정
4. SSL/TLS 모드: Full (strict)
5. 캐싱 규칙 설정

#### AWS CloudFront 설정
1. AWS CloudFront 배포 생성
2. 원본 도메인 설정
3. 캐시 동작 설정
4. SSL 인증서 연결

### 로드 밸런서 설정 (선택사항)

#### Nginx Plus
```nginx
upstream backend {
    server backend1:5000;
    server backend2:5000;
    server backend3:5000;
}
```

#### AWS ALB
1. Application Load Balancer 생성
2. 타겟 그룹 설정
3. 리스너 규칙 설정
4. SSL 인증서 연결

## 🔒 보안 설정

### 보안 헤더 설정
```nginx
# Nginx 보안 헤더
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Rate Limiting 설정
```nginx
# Nginx Rate Limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

## 📊 모니터링 설정

### 도메인 모니터링
```bash
# 도메인 상태 모니터링
./scripts/verify_dns.sh your-domain.com

# SSL 인증서 모니터링
./scripts/manage_ssl.sh status
```

### 자동 알림 설정
1. **SSL 만료 알림**: 30일 전 알림
2. **도메인 만료 알림**: 60일 전 알림
3. **DNS 전파 실패 알림**: 즉시 알림

## 🛠️ 문제 해결

### 일반적인 문제들

#### DNS 조회 실패
```bash
# DNS 조회 확인
nslookup your-domain.com
dig your-domain.com

# DNS 전파 확인
nslookup your-domain.com 8.8.8.8
nslookup your-domain.com 1.1.1.1
```

#### SSL 인증서 오류
```bash
# SSL 인증서 확인
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# 인증서 갱신
./scripts/manage_ssl.sh renew
```

#### 포트 연결 실패
```bash
# 포트 확인
nc -zv your-domain.com 80
nc -zv your-domain.com 443

# 방화벽 확인
sudo ufw status
```

### 로그 확인
```bash
# Nginx 로그 확인
docker-compose -f docker-compose.prod.yml logs nginx

# 애플리케이션 로그 확인
docker-compose -f docker-compose.prod.yml logs app
```

## 📈 성능 최적화

### 캐싱 설정
```nginx
# 정적 파일 캐싱
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Gzip 압축
```nginx
# Gzip 압축 설정
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;
```

## 🎯 최종 확인 체크리스트

### 도메인 설정
- [ ] 도메인 구매 완료
- [ ] DNS 레코드 설정 완료
- [ ] DNS 전파 확인 완료
- [ ] 도메인 설정 스크립트 실행 완료

### SSL 인증서
- [ ] Let's Encrypt 인증서 설치 완료
- [ ] 자동 갱신 설정 완료
- [ ] SSL 상태 확인 완료

### 배포 및 검증
- [ ] 프로덕션 배포 완료
- [ ] 도메인 검증 완료
- [ ] SSL 연결 확인 완료
- [ ] 성능 테스트 완료

### 모니터링
- [ ] 모니터링 설정 완료
- [ ] 알림 설정 완료
- [ ] 로그 수집 설정 완료

## 🎉 완료!

모든 설정이 완료되면 다음 URL로 접속할 수 있습니다:

- **메인 사이트**: https://your-domain.com
- **관리자 대시보드**: https://admin.your-domain.com
- **API 문서**: https://your-domain.com/api/docs
- **모니터링**: http://your-server-ip:3001 (Grafana)

---

**🏆 Your Program 도메인 설정 완료!** 