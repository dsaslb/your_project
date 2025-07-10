# Your Program 성능 최적화 및 보안 강화 가이드

## 📋 목차

1. [성능 최적화](#성능-최적화)
2. [보안 강화](#보안-강화)
3. [CI/CD 파이프라인](#cicd-파이프라인)
4. [백업 및 재해 복구](#백업-및-재해-복구)
5. [모니터링 및 알림](#모니터링-및-알림)
6. [운영 체크리스트](#운영-체크리스트)

---

## 🚀 성능 최적화

### 1. 데이터베이스 최적화

#### PostgreSQL 설정 최적화
```bash
# 성능 최적화 스크립트 실행
./scripts/performance-optimization.sh database optimize

# 성능 분석
./scripts/performance-optimization.sh database analyze

# 벤치마크 테스트
./scripts/performance-optimization.sh database benchmark
```

#### 주요 최적화 설정
- **메모리 설정**: `shared_buffers = 256MB`, `effective_cache_size = 1GB`
- **쿼리 플래너**: `random_page_cost = 1.1`, `effective_io_concurrency = 200`
- **연결 풀**: `max_connections = 100`
- **자동 정리**: `autovacuum = on`

#### 인덱스 최적화
```sql
-- 사용자 테이블 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role);

-- 주문 테이블 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status ON orders(status);

-- 복합 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_status ON orders(user_id, status);

-- 부분 인덱스
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_active ON orders(user_id) 
WHERE status IN ('pending', 'processing');
```

### 2. 캐시 최적화

#### Redis 설정 최적화
```bash
# 캐시 최적화 실행
./scripts/performance-optimization.sh cache optimize
```

#### 주요 설정
- **메모리 관리**: `maxmemory 512mb`, `maxmemory-policy allkeys-lru`
- **지속성**: `save 900 1`, `save 300 10`, `save 60 10000`
- **네트워크**: `tcp-keepalive 300`, `timeout 0`

#### 캐시 워밍업
```python
# scripts/cache-warmup.py
import redis
import requests

def warmup_cache():
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    cache_targets = [
        '/api/products',
        '/api/categories',
        '/api/users/stats',
        '/api/orders/stats'
    ]
    
    for endpoint in cache_targets:
        response = requests.get(f'http://localhost:8000{endpoint}')
        if response.status_code == 200:
            cache_key = f'cache:{endpoint}'
            r.setex(cache_key, 3600, response.text)
```

### 3. 프론트엔드 최적화

#### Next.js 설정 최적화
```bash
# 프론트엔드 최적화 실행
./scripts/performance-optimization.sh frontend optimize
```

#### 주요 최적화
- **이미지 최적화**: WebP, AVIF 포맷 지원
- **번들 최적화**: 코드 스플리팅, 트리 쉐이킹
- **캐싱**: 정적 자산 캐싱, ETag 비활성화
- **압축**: gzip, brotli 압축

#### 성능 모니터링
```javascript
// 성능 메트릭 수집
export function reportWebVitals(metric) {
  if (metric.label === 'web-vital') {
    console.log(metric);
    // 분석 서비스로 전송
  }
}
```

### 4. 백엔드 최적화

#### Flask 설정 최적화
```bash
# 백엔드 최적화 실행
./scripts/performance-optimization.sh backend optimize
```

#### 주요 최적화
- **연결 풀**: SQLAlchemy QueuePool 설정
- **캐싱**: Redis 기반 캐싱
- **Rate Limiting**: 요청 제한 설정
- **압축**: gzip 압축 활성화

#### Gunicorn 설정
```python
# gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
preload_app = True
```

---

## 🔒 보안 강화

### 1. 시스템 보안

#### 방화벽 설정
```bash
# 보안 강화 스크립트 실행
./scripts/security-hardening.sh system harden

# 보안 스캔
./scripts/security-hardening.sh system scan

# 보안 감사
./scripts/security-hardening.sh system audit
```

#### UFW 방화벽 설정
```bash
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# 필요한 포트만 허용
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # API Gateway
ufw allow 5001/tcp  # Backend
ufw allow 8002/tcp  # AI Server
ufw allow 3000/tcp  # Frontend
ufw allow 5432/tcp  # PostgreSQL
ufw allow 6379/tcp  # Redis

ufw --force enable
```

#### SSH 보안 강화
```bash
# SSH 설정 파일
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
X11Forwarding no
AllowTcpForwarding no
MaxAuthTries 3
MaxSessions 10
```

### 2. 네트워크 보안

#### 네트워크 인터페이스 보안
```bash
# IP 스푸핑 방지
echo "net.ipv4.conf.all.rp_filter=1" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.rp_filter=1" >> /etc/sysctl.conf

# ICMP 리다이렉트 비활성화
echo "net.ipv4.conf.all.accept_redirects=0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.accept_redirects=0" >> /etc/sysctl.conf

# 소스 라우팅 비활성화
echo "net.ipv4.conf.all.accept_source_route=0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.accept_source_route=0" >> /etc/sysctl.conf

sysctl -p
```

#### DNS 보안
```bash
# DNS 오버 HTTPS 설정
cat > /etc/systemd/resolved.conf << EOF
[Resolve]
DNS=1.1.1.1 1.0.0.1 8.8.8.8 8.8.4.4
DNSOverTLS=yes
DNSSEC=yes
EOF

systemctl restart systemd-resolved
```

### 3. 애플리케이션 보안

#### Docker 보안 설정
```bash
# 애플리케이션 보안 강화
./scripts/security-hardening.sh application harden
```

#### Docker 데몬 보안
```json
{
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp-profile.json"
}
```

#### Nginx 보안 헤더
```nginx
# 보안 헤더 설정
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' ws: wss:;" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Rate Limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
limit_req_zone $binary_remote_addr zone=admin:10m rate=5r/s;
```

### 4. 데이터베이스 보안

#### PostgreSQL 보안 설정
```bash
# 데이터베이스 보안 강화
./scripts/security-hardening.sh database harden
```

#### PostgreSQL 설정
```sql
-- SSL 설정
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on

-- 연결 제한
max_connections = 100
superuser_reserved_connections = 3

-- 로깅
log_statement = 'all'
log_min_duration_statement = 1000
log_connections = on
log_disconnections = on
log_lock_waits = on

-- 인증
password_encryption = scram-sha-256
```

#### Redis 보안 설정
```bash
# Redis 보안 설정
requirepass your_strong_redis_password_here
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command BGSAVE ""
rename-command SAVE ""

bind 127.0.0.1
protected-mode yes
```

---

## 🔄 CI/CD 파이프라인

### 1. GitHub Actions 워크플로우

#### 워크플로우 구성
```yaml
# .github/workflows/ci-cd.yml
name: Your Program CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production
```

#### 주요 단계
1. **코드 품질 검사**: Linting, Type checking
2. **보안 스캔**: Trivy, Snyk
3. **단위 테스트**: Python, Node.js
4. **통합 테스트**: Docker, API 테스트
5. **E2E 테스트**: Cypress
6. **빌드 및 푸시**: Docker 이미지
7. **배포**: Staging, Production
8. **성능 테스트**: 부하 테스트
9. **모니터링**: 헬스체크, 알림

### 2. 로컬 CI/CD 스크립트

#### 파이프라인 실행
```bash
# 전체 파이프라인 실행
./scripts/ci-cd-pipeline.sh all run

# 특정 단계 실행
./scripts/ci-cd-pipeline.sh build run
./scripts/ci-cd-pipeline.sh test run
./scripts/ci-cd-pipeline.sh deploy run

# 파이프라인 검증
./scripts/ci-cd-pipeline.sh all validate

# 롤백
./scripts/ci-cd-pipeline.sh deploy rollback
```

#### 빌드 단계
- 의존성 설치
- Docker 이미지 빌드
- 보안 스캔
- 이미지 푸시

#### 테스트 단계
- 단위 테스트
- 통합 테스트
- API 테스트
- 성능 테스트

#### 배포 단계
- 환경 검증
- 백업 생성
- Zero-downtime 배포
- 헬스체크
- 알림 발송

---

## 💾 백업 및 재해 복구

### 1. 백업 전략

#### 백업 실행
```bash
# 전체 백업
./scripts/backup-disaster-recovery.sh backup all

# 특정 백업
./scripts/backup-disaster-recovery.sh backup database
./scripts/backup-disaster-recovery.sh backup files

# 백업 검증
./scripts/backup-disaster-recovery.sh verify

# 재해 복구 테스트
./scripts/backup-disaster-recovery.sh test-recovery
```

#### 데이터베이스 백업
```bash
# PostgreSQL 백업
docker-compose exec -T postgres pg_dump -U your_program your_program > backup.sql
docker-compose exec -T postgres pg_dump -U your_program_ai your_program_ai > backup_ai.sql

# 글로벌 설정 백업
docker-compose exec -T postgres pg_dumpall -U your_program --globals-only > globals.sql
```

#### 파일 백업
```bash
# 설정 파일 백업
cp .env* backups/
cp docker-compose.yml backups/
cp -r nginx/ backups/
cp -r ssl/ backups/

# 업로드 파일 백업
tar -czf backups/uploads.tar.gz uploads/

# 로그 파일 백업
tar -czf backups/logs.tar.gz logs/
```

### 2. 클라우드 백업

#### AWS S3 백업
```bash
# S3 설정
export S3_BUCKET="your-program-backups"
export S3_REGION="us-east-1"
export CLOUD_PROVIDER="aws"

# 백업 업로드
aws s3 cp backup.tar.gz s3://$S3_BUCKET/$(basename backup.tar.gz) --region $S3_REGION
```

#### 백업 자동화
```bash
# crontab 설정 (매일 새벽 2시)
0 2 * * * /path/to/your_program/scripts/backup-disaster-recovery.sh backup all
```

### 3. 재해 복구

#### 복원 절차
```bash
# 데이터베이스 복원
./scripts/backup-disaster-recovery.sh restore database

# 파일 복원
./scripts/backup-disaster-recovery.sh restore files

# 전체 복원
./scripts/backup-disaster-recovery.sh restore all
```

#### 복원 검증
```bash
# 서비스 상태 확인
docker-compose ps

# 데이터베이스 연결 확인
docker-compose exec postgres pg_isready -U your_program

# API 헬스체크
curl -f http://localhost:8000/health
```

---

## 📊 모니터링 및 알림

### 1. 시스템 모니터링

#### Prometheus 설정
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'your-program-backend'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/metrics'
    
  - job_name: 'your-program-ai'
    static_configs:
      - targets: ['localhost:8002']
    metrics_path: '/metrics'
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:5432']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
```

#### Grafana 대시보드
```json
{
  "dashboard": {
    "title": "Your Program Dashboard",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends"
          }
        ]
      }
    ]
  }
}
```

### 2. 애플리케이션 모니터링

#### 헬스체크 엔드포인트
```python
@app.route('/health')
def health_check():
    try:
        # 데이터베이스 연결 확인
        db.session.execute('SELECT 1')
        
        # Redis 연결 확인
        redis_client.ping()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config.get('VERSION', 'unknown')
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, 503
```

#### 메트릭 수집
```python
from prometheus_client import Counter, Histogram, generate_latest

# 메트릭 정의
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        REQUEST_LATENCY.observe(time.time() - g.start_time)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### 3. 알림 시스템

#### Slack 알림
```python
import requests

def send_slack_notification(message, channel="#alerts"):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    
    if webhook_url:
        payload = {
            "text": message,
            "channel": channel
        }
        
        try:
            requests.post(webhook_url, json=payload)
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
```

#### 이메일 알림
```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, message, recipients):
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = ', '.join(recipients)
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
```

---

## ✅ 운영 체크리스트

### 1. 일일 체크리스트

#### 시스템 상태 확인
- [ ] 서비스 상태 확인 (`docker-compose ps`)
- [ ] 데이터베이스 연결 확인
- [ ] 디스크 사용량 확인
- [ ] 메모리 사용량 확인
- [ ] 로그 파일 확인

#### 성능 모니터링
- [ ] 응답 시간 확인
- [ ] 에러율 확인
- [ ] 트래픽 패턴 확인
- [ ] 리소스 사용량 확인

### 2. 주간 체크리스트

#### 보안 점검
- [ ] 보안 업데이트 확인
- [ ] 로그 분석
- [ ] 접근 권한 검토
- [ ] 백업 상태 확인

#### 성능 최적화
- [ ] 성능 분석 실행
- [ ] 불필요한 데이터 정리
- [ ] 캐시 효율성 확인
- [ ] 인덱스 최적화

### 3. 월간 체크리스트

#### 전체 시스템 점검
- [ ] 재해 복구 테스트
- [ ] 백업 복원 테스트
- [ ] 보안 감사 실행
- [ ] 성능 벤치마크 실행

#### 문서 업데이트
- [ ] 운영 문서 업데이트
- [ ] 프로시저 검토
- [ ] 팀 교육 진행

### 4. 긴급 상황 대응

#### 장애 발생 시
1. **즉시 대응**
   - 서비스 상태 확인
   - 영향도 평가
   - 팀 알림

2. **문제 진단**
   - 로그 분석
   - 메트릭 확인
   - 원인 파악

3. **복구 조치**
   - 서비스 재시작
   - 데이터 복원
   - 설정 복구

4. **사후 조치**
   - 원인 분석
   - 재발 방지
   - 문서화

---

## 📚 추가 리소스

### 도구 및 유틸리티
- **성능 모니터링**: Prometheus, Grafana, New Relic
- **보안 스캔**: Trivy, Snyk, OWASP ZAP
- **로깅**: ELK Stack, Fluentd, Logstash
- **백업**: AWS S3, Google Cloud Storage, Azure Blob

### 문서 및 가이드
- [PostgreSQL 성능 튜닝 가이드](https://www.postgresql.org/docs/current/performance-tips.html)
- [Redis 최적화 가이드](https://redis.io/topics/optimization)
- [Docker 보안 모범 사례](https://docs.docker.com/engine/security/)
- [OWASP 보안 가이드](https://owasp.org/www-project-top-ten/)

### 모니터링 대시보드
- 시스템 리소스 모니터링
- 애플리케이션 성능 모니터링
- 보안 이벤트 모니터링
- 비즈니스 메트릭 모니터링

---

## 🎯 결론

이 가이드는 Your Program의 성능 최적화와 보안 강화를 위한 포괄적인 접근 방법을 제공합니다. 정기적인 모니터링, 자동화된 백업, 그리고 체계적인 보안 관리가 안정적이고 안전한 시스템 운영의 핵심입니다.

모든 스크립트와 설정은 프로덕션 환경에 적용하기 전에 테스트 환경에서 충분히 검증하시기 바랍니다. 