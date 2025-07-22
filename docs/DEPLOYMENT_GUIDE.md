# 배포 및 운영 가이드

이 문서는 Your Program의 배포 및 운영에 대한 상세한 가이드를 제공합니다.

## 🚀 배포 아키텍처

### 전체 아키텍처
```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                    │
│  - SSL/TLS 종료                                             │
│  - 정적 파일 서빙                                           │
│  - Rate Limiting                                            │
│  - 보안 헤더                                                │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  - Flask Application (Gunicorn)                             │
│  - JWT Authentication                                       │
│  - OAuth2 Integration                                       │
│  - 2FA Support                                              │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  - PostgreSQL Database                                      │
│  - Redis Cache                                              │
│  - Elasticsearch (Logs)                                     │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Layer                         │
│  - Prometheus (Metrics)                                     │
│  - Grafana (Dashboards)                                     │
│  - Logstash (Log Processing)                                │
│  - Kibana (Log Visualization)                               │
└─────────────────────────────────────────────────────────────┘
```

## 🐳 Docker 배포

### 1. Docker 이미지 빌드

```bash
# 개발 환경 빌드
docker build -t your_program:dev .

# 프로덕션 환경 빌드
docker build --target production -t your_program:latest .
```

### 2. Docker Compose 실행

```bash
# 전체 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d app db redis

# 로그 확인
docker-compose logs -f app

# 서비스 상태 확인
docker-compose ps
```

### 3. 환경별 배포

#### 개발 환경
```bash
# 개발 환경 설정
cp config/development.env .env
docker-compose -f docker-compose.yml up -d
```

#### 스테이징 환경
```bash
# 스테이징 환경 설정
cp config/staging.env .env
docker-compose -f docker-compose.staging.yml up -d
```

#### 프로덕션 환경
```bash
# 프로덕션 환경 설정
cp config/production.env .env
docker-compose -f docker-compose.production.yml up -d
```

## 🔄 CI/CD 파이프라인

### GitHub Actions 워크플로우

#### 1. 자동 테스트
```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest tests/ -v
```

#### 2. 자동 배포
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./scripts/deploy.sh production latest
```

### 배포 스크립트 사용법

```bash
# 프로덕션 배포
./scripts/deploy.sh production latest

# 스테이징 배포
./scripts/deploy.sh staging develop

# 롤백
./scripts/deploy.sh production previous
```

## 📊 모니터링 및 로깅

### 1. Prometheus 메트릭 수집

#### 애플리케이션 메트릭
```python
# app.py
from prometheus_client import Counter, Histogram, generate_latest

# 요청 카운터
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])

# 응답 시간 히스토그램
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

#### Nginx 메트릭
```nginx
# nginx.conf
location /nginx_status {
    stub_status on;
    access_log off;
}
```

### 2. Grafana 대시보드

#### 주요 대시보드
- **시스템 대시보드**: CPU, 메모리, 디스크 사용량
- **애플리케이션 대시보드**: 요청 수, 응답 시간, 에러율
- **데이터베이스 대시보드**: 연결 수, 쿼리 성능
- **보안 대시보드**: 로그인 실패, 의심스러운 활동

### 3. 로그 수집 및 분석

#### ELK 스택 설정
```yaml
# docker-compose.yml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false

logstash:
  image: docker.elastic.co/logstash/logstash:8.8.0
  volumes:
    - ./monitoring/logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: docker.elastic.co/kibana/kibana:8.8.0
  environment:
    - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

## 🔧 운영 자동화

### 1. 로그 로테이션

```bash
# 로그 로테이션 실행
./scripts/operations.sh rotate-logs

# 자동 로테이션 (cron)
0 0 * * * /path/to/your_program/scripts/operations.sh rotate-logs
```

### 2. 시스템 모니터링

```bash
# 전체 모니터링 실행
./scripts/operations.sh monitor-all

# 특정 모니터링만 실행
./scripts/operations.sh monitor-system
./scripts/operations.sh monitor-app
./scripts/operations.sh monitor-db
```

### 3. 성능 최적화

```bash
# 성능 최적화 실행
./scripts/operations.sh optimize

# 시스템 정리
./scripts/operations.sh cleanup
```

### 4. 상태 리포트 생성

```bash
# 상태 리포트 생성
./scripts/operations.sh report

# 자동 리포트 (cron)
0 8 * * * /path/to/your_program/scripts/operations.sh report
```

## 💾 백업 및 복구

### 1. 자동 백업

```bash
# 전체 백업
./scripts/backup.sh backup full

# 데이터베이스만 백업
./scripts/backup.sh backup database

# 파일만 백업
./scripts/backup.sh backup files
```

### 2. 백업 복구

```bash
# 전체 복구
./scripts/backup.sh restore full /path/to/backup/directory

# 데이터베이스 복구
./scripts/backup.sh restore database /path/to/backup.sql.gz

# 파일 복구
./scripts/backup.sh restore files /path/to/backup.tar.gz
```

### 3. 백업 관리

```bash
# 백업 목록 확인
./scripts/backup.sh list

# 백업 검증
./scripts/backup.sh verify /path/to/backup.sql.gz

# 오래된 백업 정리
./scripts/backup.sh cleanup 30
```

## 🚨 알림 및 알림

### 1. 알림 설정

#### 이메일 알림
```bash
# 환경 변수 설정
export ALERT_EMAIL=admin@yourprogram.com

# 알림 전송
./scripts/operations.sh alert "High CPU Usage" "CPU usage is 90%"
```

#### Slack 알림
```bash
# 환경 변수 설정
export SLACK_WEBHOOK_URL=your_slack_webhook_url

# 알림 전송
./scripts/operations.sh alert "System Alert" "Database connection failed"
```

### 2. Prometheus 알림 규칙

```yaml
# monitoring/alerts.yml
groups:
  - name: your_program_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
```

## 🔒 보안 설정

### 1. SSL/TLS 설정

```bash
# Let's Encrypt 인증서 발급
sudo certbot certonly --standalone -d yourprogram.com

# 인증서 자동 갱신
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. 방화벽 설정

```bash
# UFW 방화벽 설정
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. 보안 스캔

```bash
# 취약점 스캔
./scripts/security_scan.sh

# 의존성 취약점 검사
safety check

# 코드 보안 검사
bandit -r . -f json -o security_report.json
```

## 📈 성능 최적화

### 1. 애플리케이션 최적화

#### Gunicorn 설정
```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
```

#### 데이터베이스 최적화
```sql
-- 인덱스 생성
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_brands_name ON brands(name);

-- 통계 업데이트
ANALYZE users;
ANALYZE brands;
```

### 2. 캐시 최적화

#### Redis 캐시 설정
```python
# 캐시 설정
CACHE_TYPE = "redis"
CACHE_REDIS_URL = "redis://redis:6379/1"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_KEY_PREFIX = "your_program_"
```

### 3. CDN 설정

```bash
# 정적 파일 CDN 업로드
aws s3 sync static/ s3://your-cdn-bucket/static/ --delete

# 캐시 무효화
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

## 🔄 롤백 전략

### 1. 자동 롤백

```bash
# 배포 실패 시 자동 롤백
./scripts/deploy.sh production rollback

# 특정 버전으로 롤백
./scripts/deploy.sh production v1.2.3
```

### 2. 데이터베이스 롤백

```bash
# 데이터베이스 롤백
./scripts/backup.sh restore database /path/to/backup.sql.gz

# 마이그레이션 롤백
flask db downgrade
```

## 📋 운영 체크리스트

### 일일 체크리스트
- [ ] 시스템 리소스 모니터링
- [ ] 애플리케이션 헬스체크
- [ ] 데이터베이스 성능 확인
- [ ] 로그 분석
- [ ] 백업 상태 확인

### 주간 체크리스트
- [ ] 성능 리포트 생성
- [ ] 보안 스캔 실행
- [ ] 백업 복구 테스트
- [ ] 시스템 업데이트
- [ ] 용량 계획 검토

### 월간 체크리스트
- [ ] 전체 시스템 감사
- [ ] 성능 최적화
- [ ] 보안 정책 검토
- [ ] 재해 복구 테스트
- [ ] 비용 분석

## 🆘 문제 해결

### 1. 일반적인 문제

#### 애플리케이션 다운
```bash
# 로그 확인
docker-compose logs app

# 컨테이너 재시작
docker-compose restart app

# 헬스체크
curl -f http://localhost:5000/health
```

#### 데이터베이스 연결 실패
```bash
# 데이터베이스 상태 확인
docker-compose exec db pg_isready

# 연결 테스트
docker-compose exec db psql -U your_program -d your_program -c "SELECT 1;"
```

#### Redis 연결 실패
```bash
# Redis 상태 확인
docker-compose exec redis redis-cli ping

# 메모리 사용량 확인
docker-compose exec redis redis-cli info memory
```

### 2. 성능 문제

#### 느린 응답 시간
```bash
# 로그 분석
grep "slow" logs/app.log

# 데이터베이스 쿼리 분석
docker-compose exec db psql -U your_program -d your_program -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

#### 높은 메모리 사용량
```bash
# 메모리 사용량 확인
docker stats

# 프로세스 분석
docker-compose exec app ps aux
```

### 3. 보안 문제

#### 의심스러운 활동
```bash
# 로그인 실패 확인
grep "LOGIN_FAILED" logs/app.log

# IP 차단
iptables -A INPUT -s SUSPICIOUS_IP -j DROP
```

## 📞 지원 및 연락처

### 기술 지원
- **이메일**: support@yourprogram.com
- **슬랙**: #your-program-support
- **문서**: https://docs.yourprogram.com

### 긴급 연락처
- **시스템 관리자**: admin@yourprogram.com
- **보안 담당자**: security@yourprogram.com
- **24/7 지원**: +82-2-1234-5678

이 가이드를 따라 안전하고 효율적인 배포 및 운영을 수행할 수 있습니다. 