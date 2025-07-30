# Your Program 시스템 관리자 가이드

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [설치 및 초기 설정](#설치-및-초기-설정)
3. [시스템 구성 요소](#시스템-구성-요소)
4. [운영 관리](#운영-관리)
5. [모니터링 및 알림](#모니터링-및-알림)
6. [보안 관리](#보안-관리)
7. [백업 및 복구](#백업-및-복구)
8. [문제 해결](#문제-해결)
9. [성능 최적화](#성능-최적화)
10. [유지보수](#유지보수)

---

## 시스템 개요

### 아키텍처 개요

Your Program은 마이크로서비스 아키텍처 기반의 엔터프라이즈급 통합 플랫폼입니다.

```
┌─────────────────────────────────────────────────┐
│                Frontend Layer                   │
│  Next.js 14 + React 18 + Tailwind CSS         │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│                API Gateway                      │
│  통합 API 서버 (Port 8000)                     │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│             Microservices Layer                 │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │   AI    │ │  Data   │ │Security │ │  IoT    │ │
│ │   ML    │ │Analysis │ │Monitor  │ │Platform │ │
│ │ (8001)  │ │ (8002)  │ │ (8007)  │ │ (8004)  │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│              Data Layer                         │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │PostgreSQL│ │ Redis   │ │ SQLite  │ │Blockchain│ │
│ │         │ │ Cache   │ │ Local   │ │ Ledger  │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────────────────┘
```

### 주요 구성 요소

| 구성 요소 | 포트 | 설명 |
|-----------|------|------|
| API Gateway | 8000 | 통합 API 엔드포인트 |
| AI/ML Platform | 8001 | 인공지능 및 머신러닝 서비스 |
| Data Analysis | 8002 | 데이터 분석 및 시각화 |
| Blockchain | 8003 | 블록체인 및 분산 원장 |
| IoT Platform | 8004 | IoT 디바이스 관리 |
| Security Monitor | 8007 | 보안 모니터링 및 감사 |
| Performance Monitor | 별도 프로세스 | 성능 모니터링 |

---

## 설치 및 초기 설정

### 시스템 요구사항

**최소 요구사항:**
- OS: Ubuntu 20.04 LTS 또는 CentOS 8+
- CPU: 4 cores
- RAM: 8GB
- Storage: 100GB SSD
- Network: 1Gbps

**권장 사양:**
- OS: Ubuntu 22.04 LTS
- CPU: 8 cores
- RAM: 16GB
- Storage: 500GB NVMe SSD
- Network: 10Gbps

### 1. 기본 환경 설정

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y curl wget git vim htop tree

# Python 3.9+ 설치 확인
python3 --version

# Node.js 18+ 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Docker 설치 (선택사항)
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2. 데이터베이스 설정

#### PostgreSQL 설정
```bash
# PostgreSQL 설치
sudo apt install -y postgresql postgresql-contrib

# 데이터베이스 생성
sudo -u postgres createdb your_program

# 사용자 생성 및 권한 부여
sudo -u postgres psql
CREATE USER your_program_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE your_program TO your_program_user;
\q
```

#### Redis 설정
```bash
# Redis 설치
sudo apt install -y redis-server

# Redis 설정 편집
sudo vim /etc/redis/redis.conf

# 설정 변경사항:
# maxmemory 2gb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# save 60 10000

# Redis 재시작
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 3. 애플리케이션 설치

```bash
# 프로젝트 클론
git clone https://github.com/your-org/your-program.git
cd your-program

# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# Python 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
vim .env
```

#### 환경 변수 설정 (.env)
```bash
# 데이터베이스 설정
DATABASE_URL=postgresql://your_program_user:secure_password@localhost:5432/your_program

# Redis 설정
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 보안 설정
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# API 설정
API_GATEWAY_URL=http://localhost:8000
AI_ML_URL=http://localhost:8001
DATA_ANALYSIS_URL=http://localhost:8002
BLOCKCHAIN_URL=http://localhost:8003
IOT_URL=http://localhost:8004
SECURITY_URL=http://localhost:8007

# 로그 설정
LOG_LEVEL=INFO
LOG_FILE=/var/log/your_program/app.log

# 모니터링 설정
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### 4. 데이터베이스 초기화

```bash
# 데이터베이스 마이그레이션
python manage.py migrate

# 초기 데이터 로드
python manage.py loaddata initial_data.json

# 관리자 계정 생성
python manage.py createsuperuser
```

---

## 시스템 구성 요소

### 1. API Gateway 설정

**설정 파일**: `config/api_gateway.yml`

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

services:
  ai_ml:
    url: "http://localhost:8001"
    timeout: 30
    retry: 3
  
  data_analysis:
    url: "http://localhost:8002"
    timeout: 30
    retry: 3
  
  security:
    url: "http://localhost:8007"
    timeout: 30
    retry: 3

middleware:
  - cors
  - rate_limiting
  - authentication
  - logging

rate_limiting:
  requests_per_minute: 1000
  burst: 100

authentication:
  jwt_secret: "${JWT_SECRET}"
  token_expiry: 3600
```

### 2. 마이크로서비스 설정

각 마이크로서비스는 독립적으로 실행되며, 다음과 같이 시작할 수 있습니다:

```bash
# AI/ML 서비스 시작
cd ai_ml
python app.py &

# 데이터 분석 서비스 시작
cd data_analysis
python app.py &

# 보안 모니터링 서비스 시작
cd security
python security_api_server.py &

# IoT 플랫폼 서비스 시작
cd iot
python iot_platform.py &
```

### 3. 프론트엔드 설정

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm run dev

# 프로덕션 빌드
npm run build
npm start
```

---

## 운영 관리

### 1. 서비스 관리

#### Systemd 서비스 설정

각 서비스를 systemd로 관리하기 위한 설정 파일을 생성합니다.

**예시: `/etc/systemd/system/your-program-api.service`**

```ini
[Unit]
Description=Your Program API Gateway
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=your_program
Group=your_program
WorkingDirectory=/opt/your_program
Environment=PATH=/opt/your_program/venv/bin
ExecStart=/opt/your_program/venv/bin/python api_gateway.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable your-program-api
sudo systemctl start your-program-api

# 서비스 상태 확인
sudo systemctl status your-program-api

# 로그 확인
sudo journalctl -u your-program-api -f
```

### 2. 로그 관리

#### 로그 설정 (`config/logging.yml`)

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  detailed:
    format: '%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: detailed
    filename: /var/log/your_program/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: /var/log/your_program/error.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  your_program:
    level: INFO
    handlers: [console, file, error_file]
    propagate: false

root:
  level: INFO
  handlers: [console, file]
```

#### 로그 로테이션 설정

**`/etc/logrotate.d/your-program`**

```
/var/log/your_program/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 your_program your_program
    postrotate
        systemctl reload your-program-*
    endscript
}
```

### 3. 프로세스 모니터링

#### Supervisor 설정 (선택사항)

```bash
# Supervisor 설치
sudo apt install -y supervisor

# 설정 파일 생성
sudo vim /etc/supervisor/conf.d/your-program.conf
```

**설정 내용:**

```ini
[group:your-program]
programs=api-gateway,ai-ml,data-analysis,security-monitor

[program:api-gateway]
command=/opt/your_program/venv/bin/python api_gateway.py
directory=/opt/your_program
user=your_program
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/your_program/api-gateway.log

[program:ai-ml]
command=/opt/your_program/venv/bin/python ai_ml/app.py
directory=/opt/your_program
user=your_program
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/your_program/ai-ml.log

[program:data-analysis]
command=/opt/your_program/venv/bin/python data_analysis/app.py
directory=/opt/your_program
user=your_program
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/your_program/data-analysis.log

[program:security-monitor]
command=/opt/your_program/venv/bin/python security/security_api_server.py
directory=/opt/your_program
user=your_program
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/your_program/security.log
```

```bash
# Supervisor 설정 재로드
sudo supervisorctl reread
sudo supervisorctl update

# 모든 프로그램 시작
sudo supervisorctl start your-program:*

# 상태 확인
sudo supervisorctl status
```

---

## 모니터링 및 알림

### 1. 시스템 메트릭 모니터링

#### Prometheus 설정

**`config/prometheus.yml`**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'your-program-api'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'your-program-security'
    static_configs:
      - targets: ['localhost:8007']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:9187']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "alerts.yml"
```

#### 알림 규칙 설정

**`config/alerts.yml`**

```yaml
groups:
  - name: your-program-alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"

      - alert: ServiceDown
        expr: up{job=~"your-program-.*"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.job }} service is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 10% for more than 5 minutes"

      - alert: SecurityThreatDetected
        expr: security_threats_total > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Security threats detected"
          description: "Multiple security threats detected in the last minute"
```

### 2. 애플리케이션 모니터링

#### 헬스 체크 엔드포인트

각 서비스에 헬스 체크 엔드포인트를 구현합니다:

```python
# health_check.py
from fastapi import FastAPI, HTTPException
import psutil
import redis
import psycopg2
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    """종합 헬스 체크"""
    checks = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "checks": {}
    }
    
    try:
        # CPU 사용률 확인
        cpu_percent = psutil.cpu_percent(interval=1)
        checks["checks"]["cpu"] = {
            "status": "healthy" if cpu_percent < 80 else "warning",
            "value": cpu_percent,
            "unit": "percent"
        }
        
        # 메모리 사용률 확인
        memory = psutil.virtual_memory()
        checks["checks"]["memory"] = {
            "status": "healthy" if memory.percent < 85 else "warning",
            "value": memory.percent,
            "unit": "percent"
        }
        
        # 디스크 사용률 확인
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        checks["checks"]["disk"] = {
            "status": "healthy" if disk_percent < 90 else "warning",
            "value": disk_percent,
            "unit": "percent"
        }
        
        # Redis 연결 확인
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            checks["checks"]["redis"] = {"status": "healthy"}
        except Exception as e:
            checks["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
            checks["status"] = "unhealthy"
        
        # PostgreSQL 연결 확인
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="your_program",
                user="your_program_user",
                password="secure_password"
            )
            conn.close()
            checks["checks"]["postgresql"] = {"status": "healthy"}
        except Exception as e:
            checks["checks"]["postgresql"] = {"status": "unhealthy", "error": str(e)}
            checks["status"] = "unhealthy"
        
        return checks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/health/ready")
async def readiness_check():
    """준비 상태 확인"""
    # 의존성 서비스 확인
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

@app.get("/health/live")
async def liveness_check():
    """생존 상태 확인"""
    # 기본적인 응답 확인
    return {"status": "alive", "timestamp": datetime.now().isoformat()}
```

### 3. 알림 설정

#### Alertmanager 설정

**`config/alertmanager.yml`**

```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourcompany.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/alert'

  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@yourcompany.com'
        subject: 'CRITICAL Alert: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Instance: {{ .Labels.instance }}
          Severity: {{ .Labels.severity }}
          {{ end }}
    webhook_configs:
      - url: 'http://localhost:5001/critical-alert'

  - name: 'warning-alerts'
    email_configs:
      - to: 'ops@yourcompany.com'
        subject: 'Warning Alert: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Instance: {{ .Labels.instance }}
          Severity: {{ .Labels.severity }}
          {{ end }}
```

---

## 보안 관리

### 1. 접근 제어

#### 방화벽 설정

```bash
# UFW 활성화
sudo ufw enable

# SSH 접근 허용 (포트 변경 권장)
sudo ufw allow 22/tcp

# 애플리케이션 포트 허용
sudo ufw allow 8000/tcp  # API Gateway
sudo ufw allow 8001/tcp  # AI/ML
sudo ufw allow 8002/tcp  # Data Analysis
sudo ufw allow 8007/tcp  # Security Monitor

# 모니터링 포트 (내부 네트워크만)
sudo ufw allow from 192.168.1.0/24 to any port 9090  # Prometheus
sudo ufw allow from 192.168.1.0/24 to any port 3000  # Grafana

# 상태 확인
sudo ufw status numbered
```

#### SSL/TLS 설정

```bash
# Certbot 설치 (Let's Encrypt)
sudo apt install -y certbot

# SSL 인증서 발급
sudo certbot certonly --standalone -d your-domain.com

# 인증서 자동 갱신 설정
sudo crontab -e
# 다음 라인 추가:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

**Nginx 설정 (`/etc/nginx/sites-available/your-program`)**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /security/ {
        proxy_pass http://localhost:8007/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 인증 및 권한 관리

#### JWT 토큰 설정

```python
# auth_config.py
JWT_CONFIG = {
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "REFRESH_TOKEN_EXPIRE_DAYS": 7,
    "SECRET_KEY": "your-super-secret-key-here",
    "ISSUER": "your-program",
    "AUDIENCE": "your-program-users"
}

ROLE_PERMISSIONS = {
    "admin": [
        "read:all",
        "write:all",
        "delete:all",
        "manage:users",
        "manage:system"
    ],
    "operator": [
        "read:all",
        "write:monitoring",
        "write:analysis"
    ],
    "user": [
        "read:own",
        "write:own"
    ],
    "readonly": [
        "read:dashboard"
    ]
}
```

### 3. 보안 모니터링

#### 보안 이벤트 모니터링

보안 모니터링 시스템이 자동으로 다음을 탐지합니다:

- **침입 시도**: 무차별 대입 공격, 비정상적 로그인 패턴
- **악성 코드**: SQL 인젝션, XSS, 경로 탐색 공격
- **이상 행위**: 비정상적 API 호출 패턴, 대량 데이터 접근
- **시스템 변경**: 파일 무결성, 권한 변경, 설정 수정

#### 보안 감사 실행

```bash
# 수동 보안 감사 실행
cd security
python security_audit.py

# 정기 감사 스케줄링 (crontab)
sudo crontab -e
# 매일 오전 2시에 보안 감사 실행
# 0 2 * * * /opt/your_program/venv/bin/python /opt/your_program/security/security_audit.py
```

---

## 백업 및 복구

### 1. 데이터베이스 백업

#### PostgreSQL 백업 스크립트

```bash
#!/bin/bash
# backup_postgres.sh

BACKUP_DIR="/opt/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="your_program"
DB_USER="your_program_user"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# 데이터베이스 백업
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/your_program_$DATE.sql.gz

# 30일 이상된 백업 파일 삭제
find $BACKUP_DIR -name "your_program_*.sql.gz" -mtime +30 -delete

echo "Backup completed: your_program_$DATE.sql.gz"
```

#### Redis 백업 스크립트

```bash
#!/bin/bash
# backup_redis.sh

BACKUP_DIR="/opt/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# Redis 백업
redis-cli BGSAVE
sleep 5

# RDB 파일 복사
cp /var/lib/redis/dump.rdb $BACKUP_DIR/dump_$DATE.rdb

# 30일 이상된 백업 파일 삭제
find $BACKUP_DIR -name "dump_*.rdb" -mtime +30 -delete

echo "Redis backup completed: dump_$DATE.rdb"
```

### 2. 애플리케이션 백업

```bash
#!/bin/bash
# backup_application.sh

BACKUP_DIR="/opt/backups/application"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/your_program"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# 애플리케이션 코드 백업 (설정 파일 포함)
tar -czf $BACKUP_DIR/application_$DATE.tar.gz \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    $APP_DIR

# 로그 파일 백업
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/your_program/

# 30일 이상된 백업 파일 삭제
find $BACKUP_DIR -name "application_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "logs_*.tar.gz" -mtime +30 -delete

echo "Application backup completed: application_$DATE.tar.gz"
```

### 3. 자동 백업 스케줄링

```bash
# crontab 설정
sudo crontab -e

# 매일 오전 1시에 데이터베이스 백업
0 1 * * * /opt/scripts/backup_postgres.sh

# 매일 오전 1시 30분에 Redis 백업
30 1 * * * /opt/scripts/backup_redis.sh

# 매주 일요일 오전 2시에 애플리케이션 백업
0 2 * * 0 /opt/scripts/backup_application.sh
```

### 4. 복구 절차

#### 데이터베이스 복구

```bash
# PostgreSQL 복구
gunzip -c /opt/backups/postgresql/your_program_20240119_020000.sql.gz | psql -U your_program_user -d your_program

# Redis 복구
sudo systemctl stop redis-server
cp /opt/backups/redis/dump_20240119_020000.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb
sudo systemctl start redis-server
```

#### 애플리케이션 복구

```bash
# 현재 애플리케이션 백업
sudo mv /opt/your_program /opt/your_program_backup_$(date +%Y%m%d_%H%M%S)

# 백업에서 복구
sudo tar -xzf /opt/backups/application/application_20240119_020000.tar.gz -C /opt/

# 권한 설정
sudo chown -R your_program:your_program /opt/your_program

# 서비스 재시작
sudo systemctl restart your-program-*
```

---

## 문제 해결

### 1. 일반적인 문제

#### 서비스 시작 실패

**증상**: 서비스가 시작되지 않음

**진단**:
```bash
# 서비스 상태 확인
sudo systemctl status your-program-api

# 로그 확인
sudo journalctl -u your-program-api -n 50

# 설정 파일 검증
python -c "import yaml; yaml.safe_load(open('config/api_gateway.yml'))"
```

**해결 방법**:
1. 포트 충돌 확인: `sudo netstat -tlnp | grep :8000`
2. 권한 확인: `ls -la /opt/your_program`
3. 환경 변수 확인: `cat .env`
4. 의존성 확인: `pip check`

#### 데이터베이스 연결 실패

**증상**: `psycopg2.OperationalError` 또는 연결 타임아웃

**진단**:
```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql

# 연결 테스트
psql -U your_program_user -h localhost -d your_program -c "SELECT 1;"

# 로그 확인
sudo tail -f /var/log/postgresql/postgresql-*.log
```

**해결 방법**:
1. PostgreSQL 서비스 재시작: `sudo systemctl restart postgresql`
2. 연결 설정 확인: `/etc/postgresql/*/main/pg_hba.conf`
3. 방화벽 확인: `sudo ufw status`

#### 메모리 부족

**증상**: `MemoryError` 또는 시스템 응답 없음

**진단**:
```bash
# 메모리 사용량 확인
free -h
ps aux --sort=-%mem | head

# 스왑 사용량 확인
swapon --show
```

**해결 방법**:
1. 메모리 집약적 프로세스 종료
2. 스왑 공간 추가
3. 애플리케이션 메모리 설정 조정

### 2. 성능 문제

#### 높은 CPU 사용률

**진단**:
```bash
# CPU 사용률 모니터링
top -p $(pgrep -d',' python)
htop

# 프로파일링
python -m cProfile -o profile.stats your_app.py
```

**해결 방법**:
1. 비효율적 코드 최적화
2. 워커 프로세스 수 조정
3. 캐싱 추가

#### 느린 응답 시간

**진단**:
```bash
# API 응답 시간 측정
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/health"

# 데이터베이스 쿼리 분석
psql -U your_program_user -d your_program -c "EXPLAIN ANALYZE SELECT * FROM your_table LIMIT 10;"
```

**해결 방법**:
1. 데이터베이스 인덱스 추가
2. 쿼리 최적화
3. 캐싱 전략 개선

### 3. 보안 이슈

#### 의심스러운 활동 탐지

**대응 절차**:
1. 보안 대시보드 확인: `http://localhost:8007/dashboard`
2. 로그 분석: `grep "CRITICAL\|ERROR" /var/log/your_program/*.log`
3. 네트워크 트래픽 모니터링: `sudo netstat -tulnp`
4. 필요시 IP 차단: `sudo ufw deny from suspicious.ip.address`

#### 인증 문제

**진단**:
```bash
# JWT 토큰 검증
python -c "
import jwt
token = 'your-jwt-token-here'
secret = 'your-secret-key'
print(jwt.decode(token, secret, algorithms=['HS256']))
"
```

### 4. 로그 분석 도구

#### 실시간 로그 모니터링

```bash
# 모든 서비스 로그 실시간 확인
sudo tail -f /var/log/your_program/*.log

# 에러만 필터링
sudo tail -f /var/log/your_program/*.log | grep -i error

# 특정 IP 활동 추적
sudo grep "192.168.1.100" /var/log/your_program/*.log
```

#### 로그 분석 스크립트

```python
#!/usr/bin/env python3
# log_analyzer.py

import re
import sys
from collections import Counter
from datetime import datetime

def analyze_logs(log_file):
    """로그 파일 분석"""
    
    error_counts = Counter()
    ip_counts = Counter()
    endpoint_counts = Counter()
    
    with open(log_file, 'r') as f:
        for line in f:
            # 에러 패턴 찾기
            if 'ERROR' in line or 'CRITICAL' in line:
                error_match = re.search(r'(\w+Error|Exception)', line)
                if error_match:
                    error_counts[error_match.group(1)] += 1
            
            # IP 주소 찾기
            ip_match = re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', line)
            if ip_match:
                ip_counts[ip_match.group(1)] += 1
            
            # API 엔드포인트 찾기
            endpoint_match = re.search(r'(GET|POST|PUT|DELETE)\s+(/[^\s]*)', line)
            if endpoint_match:
                endpoint_counts[endpoint_match.group(2)] += 1
    
    print("=== 로그 분석 결과 ===")
    print(f"\n상위 에러 타입:")
    for error, count in error_counts.most_common(5):
        print(f"  {error}: {count}")
    
    print(f"\n상위 접속 IP:")
    for ip, count in ip_counts.most_common(5):
        print(f"  {ip}: {count}")
    
    print(f"\n상위 API 엔드포인트:")
    for endpoint, count in endpoint_counts.most_common(5):
        print(f"  {endpoint}: {count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python log_analyzer.py <log_file>")
        sys.exit(1)
    
    analyze_logs(sys.argv[1])
```

---

## 성능 최적화

### 1. 데이터베이스 최적화

#### PostgreSQL 설정 튜닝

**`/etc/postgresql/*/main/postgresql.conf`**

```ini
# 메모리 설정
shared_buffers = 256MB                  # 시스템 RAM의 25%
effective_cache_size = 1GB             # 시스템 RAM의 50-75%
work_mem = 4MB                         # 복잡한 쿼리용
maintenance_work_mem = 64MB            # 인덱스 생성, VACUUM용

# 연결 설정
max_connections = 100                  # 동시 연결 수
max_prepared_transactions = 0         # 2PC 사용 안함

# 로깅 설정
log_statement = 'mod'                 # 모든 수정 쿼리 로깅
log_min_duration_statement = 1000     # 1초 이상 걸리는 쿼리 로깅
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# 체크포인트 설정
checkpoint_completion_target = 0.7
wal_buffers = 16MB
checkpoint_timeout = 10min

# 자동 VACUUM 설정
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
```

#### 인덱스 최적화

```sql
-- 자주 조회되는 컬럼에 인덱스 생성
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX CONCURRENTLY idx_events_severity ON security_events(severity, timestamp);

-- 복합 인덱스 생성
CREATE INDEX CONCURRENTLY idx_events_composite ON security_events(source_ip, event_type, timestamp);

-- 부분 인덱스 생성
CREATE INDEX CONCURRENTLY idx_active_users ON users(id) WHERE is_active = true;

-- 인덱스 사용량 확인
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 사용되지 않는 인덱스 찾기
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexname NOT LIKE '%_pkey';
```

### 2. 애플리케이션 최적화

#### 캐싱 전략

```python
# redis_cache.py
import redis
import json
from functools import wraps
from typing import Any, Optional
import hashlib

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """캐시에 데이터 저장"""
        try:
            self.redis_client.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass
    
    def delete(self, key: str):
        """캐시에서 데이터 삭제"""
        try:
            self.redis_client.delete(key)
        except Exception:
            pass

# 캐시 데코레이터
def cache_result(prefix: str, ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = RedisCache()
            cache_key = cache.get_cache_key(prefix, *args, **kwargs)
            
            # 캐시에서 조회
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # 캐시 미스 시 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# 사용 예시
@cache_result("user_profile", ttl=1800)  # 30분 캐싱
def get_user_profile(user_id: int):
    # 데이터베이스에서 사용자 프로필 조회
    return fetch_user_from_db(user_id)
```

#### 비동기 처리

```python
# async_processor.py
import asyncio
import aioredis
import asyncpg
from typing import List
import logging

class AsyncProcessor:
    def __init__(self):
        self.redis = None
        self.db_pool = None
        self.logger = logging.getLogger(__name__)
    
    async def init_connections(self):
        """비동기 연결 초기화"""
        self.redis = await aioredis.create_redis_pool('redis://localhost')
        self.db_pool = await asyncpg.create_pool(
            database="your_program",
            user="your_program_user",
            password="secure_password",
            host="localhost",
            min_size=5,
            max_size=20
        )
    
    async def process_batch(self, items: List[dict]):
        """배치 처리"""
        tasks = []
        for item in items:
            task = asyncio.create_task(self.process_item(item))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 에러 처리
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Item {i} processing failed: {result}")
        
        return results
    
    async def process_item(self, item: dict):
        """개별 아이템 처리"""
        async with self.db_pool.acquire() as conn:
            # 데이터베이스 작업
            result = await conn.fetchrow(
                "SELECT * FROM process_item($1)", 
                item['id']
            )
            
            # Redis 캐시 업데이트
            await self.redis.setex(
                f"item:{item['id']}", 
                3600, 
                str(result)
            )
            
            return result
    
    async def close_connections(self):
        """연결 종료"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
        
        if self.db_pool:
            await self.db_pool.close()
```

### 3. 시스템 최적화

#### 시스템 파라미터 튜닝

**`/etc/sysctl.conf`**

```ini
# 네트워크 최적화
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3

# 파일 디스크립터 한계
fs.file-max = 100000

# 메모리 관리
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# 커널 보안
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 1
```

**적용**:
```bash
sudo sysctl -p
```

#### 파일 디스크립터 한계 설정

**`/etc/security/limits.conf`**

```
your_program soft nofile 65535
your_program hard nofile 65535
your_program soft nproc 4096
your_program hard nproc 4096
```

#### Nginx 최적화

**`/etc/nginx/nginx.conf`**

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 30;
    keepalive_requests 100;
    
    client_max_body_size 100M;
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;
    
    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 캐싱
    open_file_cache max=200000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
}
```

---

## 유지보수

### 1. 정기 점검 체크리스트

#### 일일 점검
- [ ] 시스템 상태 확인 (CPU, 메모리, 디스크)
- [ ] 서비스 상태 확인 (모든 마이크로서비스)
- [ ] 에러 로그 검토
- [ ] 보안 알림 확인
- [ ] 백업 상태 확인

#### 주간 점검
- [ ] 성능 트렌드 분석
- [ ] 보안 감사 실행
- [ ] 로그 로테이션 확인
- [ ] 디스크 사용량 정리
- [ ] 업데이트 확인

#### 월간 점검
- [ ] 시스템 업데이트 적용
- [ ] 보안 패치 적용
- [ ] 데이터베이스 최적화 (VACUUM, REINDEX)
- [ ] 성능 벤치마크 실행
- [ ] 재해 복구 테스트

### 2. 업데이트 절차

#### 애플리케이션 업데이트

```bash
#!/bin/bash
# update_application.sh

# 백업 생성
sudo /opt/scripts/backup_application.sh

# 새 코드 다운로드
cd /opt/your_program
git fetch origin
git checkout main
git pull origin main

# 의존성 업데이트
source venv/bin/activate
pip install -r requirements.txt

# 데이터베이스 마이그레이션
python manage.py migrate

# 프론트엔드 빌드
cd frontend
npm install
npm run build

# 서비스 재시작
sudo systemctl restart your-program-*

# 헬스 체크
sleep 30
curl -f http://localhost:8000/health || echo "Health check failed!"
```

#### 시스템 업데이트

```bash
#!/bin/bash
# system_update.sh

# 보안 업데이트만 설치
sudo apt update
sudo apt list --upgradable | grep -i security

# 보안 업데이트 적용
sudo apt upgrade -y

# 시스템 재부팅이 필요한지 확인
if [ -f /var/run/reboot-required ]; then
    echo "System reboot required"
    # 예약된 시간에 재부팅 스케줄링
    sudo shutdown -r +60 "System will reboot in 1 hour for security updates"
fi
```

### 3. 성능 벤치마크

#### API 성능 테스트

```bash
#!/bin/bash
# benchmark_api.sh

echo "=== API 성능 벤치마크 ==="

# 기본 헬스 체크
echo "1. Health Check Test:"
ab -n 1000 -c 10 http://localhost:8000/health

# 인증 API 테스트
echo "2. Authentication Test:"
ab -n 500 -c 5 -p auth_data.json -T application/json http://localhost:8000/auth/login

# 데이터 조회 API 테스트
echo "3. Data Query Test:"
ab -n 1000 -c 10 -H "Authorization: Bearer $JWT_TOKEN" http://localhost:8000/api/data

# 보안 이벤트 API 테스트
echo "4. Security Events Test:"
ab -n 200 -c 5 -H "Authorization: Bearer $JWT_TOKEN" http://localhost:8007/security/events

echo "Benchmark completed at $(date)"
```

#### 데이터베이스 성능 테스트

```sql
-- database_benchmark.sql

-- 쿼리 성능 측정
EXPLAIN (ANALYZE, BUFFERS, TIMING, SUMMARY) 
SELECT 
    se.id,
    se.source_ip,
    se.threat_type,
    se.severity,
    se.timestamp
FROM security_events se
WHERE se.timestamp >= NOW() - INTERVAL '1 day'
    AND se.severity IN ('critical', 'high')
ORDER BY se.timestamp DESC
LIMIT 100;

-- 인덱스 효율성 확인
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename IN ('security_events', 'performance_metrics', 'audit_results')
ORDER BY tablename, attname;

-- 테이블 크기 확인
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 4. 문서 관리

#### 변경 사항 추적

모든 설정 변경, 업데이트, 문제 해결 사항을 문서화합니다:

```markdown
# 변경 로그 템플릿

## 날짜: 2024-01-19

### 변경 유형: [시스템/애플리케이션/보안/설정]

### 변경 내용:
- 구체적인 변경 사항 설명

### 변경 이유:
- 변경이 필요한 이유

### 영향도:
- [ ] 낮음 - 일반 사용자에게 영향 없음
- [ ] 보통 - 일부 기능에 제한적 영향
- [ ] 높음 - 서비스 중단 또는 주요 기능 변경

### 테스트 결과:
- 변경 후 수행한 테스트 및 결과

### 롤백 절차:
- 필요시 이전 상태로 되돌리는 방법

### 후속 조치:
- 추가로 필요한 작업이나 모니터링 항목
```

---

**이 문서는 Your Program 시스템 관리자를 위한 종합 가이드입니다. 시스템 운영 중 문제가 발생하거나 추가 지원이 필요한 경우 개발팀에 문의하시기 바랍니다.**

**최종 업데이트**: 2024년 1월 19일  
**문서 버전**: 1.0.0  
**담당자**: 시스템 관리팀 