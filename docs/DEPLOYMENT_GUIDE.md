# Your Program 프로덕션 배포 가이드

## 📋 목차

1. [배포 개요](#배포-개요)
2. [사전 요구사항](#사전-요구사항)
3. [인프라 준비](#인프라-준비)
4. [환경 설정](#환경-설정)
5. [데이터베이스 설정](#데이터베이스-설정)
6. [애플리케이션 배포](#애플리케이션-배포)
7. [로드 밸런서 구성](#로드-밸런서-구성)
8. [모니터링 설정](#모니터링-설정)
9. [보안 설정](#보안-설정)
10. [백업 및 복구](#백업-및-복구)
11. [성능 최적화](#성능-최적화)
12. [운영 가이드](#운영-가이드)

---

## 배포 개요

### 배포 아키텍처

Your Program은 마이크로서비스 아키텍처를 기반으로 하며, 다음과 같은 구조로 배포됩니다:

```
                        ┌─────────────────┐
                        │   Load Balancer │
                        │   (Nginx/HAProxy)│
                        └─────────┬───────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼──────┐ ┌───▼───┐ ┌───────▼──────┐
            │  Web Server  │ │  ...  │ │  Web Server  │
            │   (Node 1)   │ │       │ │   (Node N)   │
            └───────┬──────┘ └───┬───┘ └───────┬──────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Microservices Layer   │
                    │  ┌────┐ ┌────┐ ┌────┐    │
                    │  │API │ │AI  │ │IoT │    │
                    │  │GW  │ │ML  │ │    │ ...│
                    │  └────┘ └────┘ └────┘    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │       Data Layer          │
                    │ ┌──────┐ ┌──────┐ ┌──────┐│
                    │ │PostgreSQL Redis│ │Cache ││
                    │ │      │ │      │ │      ││
                    │ └──────┘ └──────┘ └──────┘│
                    └───────────────────────────┘
```

### 배포 환경

#### 환경별 구성
```
개발 환경 (Development):
- 단일 서버
- 개발 데이터베이스
- 로그 레벨: DEBUG
- 모니터링: 기본

스테이징 환경 (Staging):
- 프로덕션 유사 구성
- 테스트 데이터
- 로그 레벨: INFO
- 모니터링: 활성화

프로덕션 환경 (Production):
- 고가용성 구성
- 실제 데이터
- 로그 레벨: WARNING
- 모니터링: 전체 활성화
```

---

## 사전 요구사항

### 시스템 요구사항

#### 최소 요구사항
```
서버 노드당:
- OS: Ubuntu 22.04 LTS / CentOS 8+
- CPU: 4 vCPU
- RAM: 8GB
- Storage: 100GB SSD
- Network: 1Gbps

전체 클러스터:
- 웹 서버: 2대 이상 (HA 구성)
- 데이터베이스: Master-Slave 구성
- 로드 밸런서: 2대 (Active-Passive)
```

#### 권장 요구사항
```
서버 노드당:
- OS: Ubuntu 22.04 LTS
- CPU: 8+ vCPU
- RAM: 16GB+
- Storage: 500GB NVMe SSD
- Network: 10Gbps

전체 클러스터:
- 웹 서버: 3대 이상
- 데이터베이스: Master + 2 Slaves
- 로드 밸런서: 2대 + Health Check
- 캐시 서버: Redis Cluster (3 Master + 3 Slave)
```

### 네트워크 요구사항

#### 포트 구성
```
외부 접근 포트:
- 80/443: HTTP/HTTPS (Load Balancer)
- 22: SSH (관리용, VPN을 통해서만)

내부 서비스 포트:
- 8000: API Gateway
- 8001: AI/ML Platform
- 8002: Data Analysis
- 8003: Blockchain
- 8004: IoT Platform
- 8007: Security Monitor

데이터베이스 포트:
- 5432: PostgreSQL
- 6379: Redis
- 9090: Prometheus
- 3000: Grafana
```

#### 방화벽 설정
```bash
# 외부 접근 허용
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# SSH (특정 IP만 허용)
sudo ufw allow from 203.0.113.0/24 to any port 22

# 내부 네트워크 (서비스 간 통신)
sudo ufw allow from 10.0.0.0/16 to any port 8000:8010
sudo ufw allow from 10.0.0.0/16 to any port 5432
sudo ufw allow from 10.0.0.0/16 to any port 6379

# 모니터링 (내부만)
sudo ufw allow from 10.0.0.0/16 to any port 9090
sudo ufw allow from 10.0.0.0/16 to any port 3000
```

### 도메인 및 SSL

#### DNS 설정
```
주 도메인: yourprogram.com
API 엔드포인트: api.yourprogram.com
관리 대시보드: admin.yourprogram.com
모니터링: monitor.yourprogram.com

서브도메인 설정:
- www.yourprogram.com → yourprogram.com
- api.yourprogram.com → Load Balancer IP
- admin.yourprogram.com → Load Balancer IP
- monitor.yourprogram.com → Monitoring Server IP
```

#### SSL 인증서
```bash
# Let's Encrypt 인증서 발급
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
  -d yourprogram.com \
  -d "*.yourprogram.com"

# 와일드카드 인증서 자동 갱신 설정
echo "0 2 * * * certbot renew --quiet" | sudo crontab -
```

---

## 인프라 준비

### 클라우드 인프라 (AWS 예시)

#### VPC 및 네트워크 설정
```bash
# VPC 생성
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=YourProgram-VPC}]'

# 서브넷 생성
# Public Subnet (Load Balancer)
aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.1.0/24 --availability-zone us-west-2a

# Private Subnet (Application Servers)
aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.10.0/24 --availability-zone us-west-2a

# Database Subnet
aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.20.0/24 --availability-zone us-west-2a
```

#### Security Groups
```bash
# Web Tier Security Group
aws ec2 create-security-group \
  --group-name YourProgram-Web-SG \
  --description "Security group for web servers" \
  --vpc-id vpc-12345678

# 80, 443 포트 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-web123 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-web123 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Application Tier Security Group
aws ec2 create-security-group \
  --group-name YourProgram-App-SG \
  --description "Security group for application servers" \
  --vpc-id vpc-12345678

# 8000-8010 포트 허용 (Web SG에서만)
aws ec2 authorize-security-group-ingress \
  --group-id sg-app123 \
  --protocol tcp \
  --port 8000-8010 \
  --source-group sg-web123
```

#### 인스턴스 생성
```bash
# 웹 서버 인스턴스 생성
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 2 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-web123 \
  --subnet-id subnet-12345678 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=YourProgram-Web}]'

# 애플리케이션 서버 인스턴스 생성
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 3 \
  --instance-type t3.xlarge \
  --key-name your-key-pair \
  --security-group-ids sg-app123 \
  --subnet-id subnet-10101010 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=YourProgram-App}]'
```

### 온프레미스 인프라

#### 서버 설정
```bash
# 각 서버에서 실행
# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 기본 패키지 설치
sudo apt install -y \
  curl wget git vim htop tree \
  software-properties-common \
  apt-transport-https \
  ca-certificates \
  gnupg \
  lsb-release

# 3. Docker 설치
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose

# 4. Docker 서비스 시작
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

#### 스토리지 설정
```bash
# 데이터 디스크 마운트 (데이터베이스 서버)
# /dev/nvme1n1을 /var/lib/postgresql에 마운트
sudo mkfs.ext4 /dev/nvme1n1
sudo mkdir -p /var/lib/postgresql
echo '/dev/nvme1n1 /var/lib/postgresql ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
sudo mount -a

# 애플리케이션 데이터 디스크
sudo mkdir -p /opt/yourprogram/data
echo '/dev/nvme2n1 /opt/yourprogram/data ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
sudo mount -a
```

---

## 환경 설정

### 환경 변수 설정

#### 프로덕션 환경 변수 (.env.production)
```bash
# 애플리케이션 설정
NODE_ENV=production
DEBUG=false
LOG_LEVEL=warning

# 도메인 및 포트
DOMAIN=yourprogram.com
API_DOMAIN=api.yourprogram.com
ADMIN_DOMAIN=admin.yourprogram.com

# 데이터베이스 설정 (Master)
DATABASE_URL=postgresql://yourprogram:secure_password@db-master.internal:5432/yourprogram
DATABASE_READ_URL=postgresql://yourprogram:secure_password@db-slave.internal:5432/yourprogram

# Redis 설정 (Cluster)
REDIS_CLUSTER_NODES=redis-1.internal:6379,redis-2.internal:6379,redis-3.internal:6379
REDIS_PASSWORD=redis_secure_password

# 보안 설정
JWT_SECRET=your-super-secure-jwt-secret-key-here
SESSION_SECRET=your-super-secure-session-secret-here
ENCRYPTION_KEY=your-32-character-encryption-key

# API 서비스 URL
API_GATEWAY_URL=http://10.0.10.10:8000
AI_ML_URL=http://10.0.10.11:8001
DATA_ANALYSIS_URL=http://10.0.10.12:8002
BLOCKCHAIN_URL=http://10.0.10.13:8003
IOT_URL=http://10.0.10.14:8004
SECURITY_URL=http://10.0.10.15:8007

# 외부 서비스
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=noreply@yourprogram.com
EMAIL_PASSWORD=email_app_password

# 모니터링
PROMETHEUS_URL=http://monitor.internal:9090
GRAFANA_URL=http://monitor.internal:3000

# 로그 설정
LOG_FILE=/var/log/yourprogram/app.log
ERROR_LOG_FILE=/var/log/yourprogram/error.log
ACCESS_LOG_FILE=/var/log/yourprogram/access.log

# 성능 설정
MAX_WORKERS=4
WORKER_TIMEOUT=30
KEEP_ALIVE=2
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50

# 파일 업로드
MAX_FILE_SIZE=100MB
UPLOAD_DIRECTORY=/opt/yourprogram/uploads

# 캐시 설정
CACHE_TTL=3600
SESSION_TTL=86400
API_RATE_LIMIT=1000
```

#### 개발/스테이징 환경별 변수
```bash
# .env.staging
NODE_ENV=staging
DEBUG=true
LOG_LEVEL=info
DOMAIN=staging.yourprogram.com

# .env.development  
NODE_ENV=development
DEBUG=true
LOG_LEVEL=debug
DOMAIN=localhost
```

### 설정 파일 관리

#### 환경별 설정 디렉토리 구조
```
config/
├── production/
│   ├── app.yml
│   ├── database.yml
│   ├── redis.yml
│   ├── logging.yml
│   └── monitoring.yml
├── staging/
│   ├── app.yml
│   ├── database.yml
│   └── ...
└── development/
    ├── app.yml
    └── ...
```

#### 프로덕션 앱 설정 (config/production/app.yml)
```yaml
app:
  name: "Your Program"
  version: "1.0.0"
  environment: "production"
  debug: false
  
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  timeout: 30
  keep_alive: 2
  
security:
  cors:
    allowed_origins:
      - "https://yourprogram.com"
      - "https://admin.yourprogram.com"
    allowed_methods: ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: ["*"]
    credentials: true
  
  rate_limiting:
    enabled: true
    requests_per_minute: 1000
    burst: 100
    
  csrf:
    enabled: true
    secret_key: "${CSRF_SECRET}"
    
features:
  ai_ml:
    enabled: true
    max_concurrent_predictions: 100
    model_cache_ttl: 3600
    
  blockchain:
    enabled: true
    network: "mainnet"
    gas_limit: 21000
    
  iot:
    enabled: true
    max_devices: 10000
    data_retention_days: 365
```

---

## 데이터베이스 설정

### PostgreSQL 클러스터 설정

#### Master 서버 설정
```bash
# PostgreSQL 14 설치
sudo apt install -y postgresql-14 postgresql-contrib-14

# 데이터 디렉토리 설정
sudo systemctl stop postgresql
sudo rsync -av /var/lib/postgresql/ /opt/postgresql-data/
sudo chown -R postgres:postgres /opt/postgresql-data

# postgresql.conf 설정
sudo vim /etc/postgresql/14/main/postgresql.conf
```

**postgresql.conf (Master):**
```ini
# 연결 설정
listen_addresses = '*'
port = 5432
max_connections = 200

# 메모리 설정
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 16MB
maintenance_work_mem = 512MB

# WAL 설정 (복제용)
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB
archive_mode = on
archive_command = 'cp %p /opt/postgresql-archive/%f'

# 로깅 설정
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'mod'
log_min_duration_statement = 1000

# 성능 설정
checkpoint_completion_target = 0.7
wal_buffers = 16MB
random_page_cost = 1.1
effective_io_concurrency = 200
```

**pg_hba.conf:**
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             yourprogram     10.0.0.0/16             md5
host    replication     replica_user    10.0.20.0/24            md5
```

#### Slave 서버 설정
```bash
# Master에서 베이스 백업 생성
sudo -u postgres pg_basebackup -h master-db.internal -D /var/lib/postgresql/14/main -U replica_user -v -P -W

# recovery.conf 설정 (PostgreSQL 12+에서는 postgresql.conf에 포함)
echo "
primary_conninfo = 'host=master-db.internal port=5432 user=replica_user'
restore_command = 'cp /opt/postgresql-archive/%f %p'
recovery_target_timeline = 'latest'
" | sudo -u postgres tee /var/lib/postgresql/14/main/postgresql.auto.conf

# Slave 시작
sudo systemctl start postgresql
```

### Redis 클러스터 설정

#### Redis Cluster 구성 (3 Master + 3 Slave)
```bash
# 각 Redis 노드에서 실행
# redis.conf 설정
sudo vim /etc/redis/redis.conf
```

**redis.conf:**
```ini
# 네트워크 설정
bind 0.0.0.0
port 6379
protected-mode yes
requirepass redis_secure_password

# 클러스터 설정
cluster-enabled yes
cluster-config-file nodes-6379.conf
cluster-node-timeout 5000
cluster-announce-ip 10.0.20.11  # 각 노드의 IP
cluster-announce-port 6379

# 메모리 설정
maxmemory 2gb
maxmemory-policy allkeys-lru

# 퍼시스턴스 설정
save 900 1
save 300 10
save 60 10000
dbfilename dump.rdb
dir /var/lib/redis

# 로그 설정
loglevel notice
logfile /var/log/redis/redis-server.log
```

#### 클러스터 초기화
```bash
# 모든 Redis 노드 시작 후
redis-cli --cluster create \
  10.0.20.11:6379 \
  10.0.20.12:6379 \
  10.0.20.13:6379 \
  10.0.20.14:6379 \
  10.0.20.15:6379 \
  10.0.20.16:6379 \
  --cluster-replicas 1 \
  -a redis_secure_password
```

---

## 애플리케이션 배포

### Docker 컨테이너 배포

#### Docker Compose 설정 (docker-compose.production.yml)
```yaml
version: '3.8'

services:
  api-gateway:
    image: yourprogram/api-gateway:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - /opt/yourprogram/logs:/app/logs
      - /opt/yourprogram/config:/app/config:ro
    networks:
      - yourprogram-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  ai-ml-platform:
    image: yourprogram/ai-ml-platform:latest
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - NODE_ENV=production
      - MODEL_CACHE_DIR=/app/models
    volumes:
      - /opt/yourprogram/models:/app/models
      - /opt/yourprogram/logs:/app/logs
    networks:
      - yourprogram-network
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

  data-analysis:
    image: yourprogram/data-analysis:latest
    restart: unless-stopped
    ports:
      - "8002:8002"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_READ_URL}
    volumes:
      - /opt/yourprogram/data:/app/data
      - /opt/yourprogram/logs:/app/logs
    networks:
      - yourprogram-network

  security-monitor:
    image: yourprogram/security-monitor:latest
    restart: unless-stopped
    ports:
      - "8007:8007"
    environment:
      - NODE_ENV=production
      - SECURITY_DB_PATH=/app/data/security.db
    volumes:
      - /opt/yourprogram/security:/app/data
      - /opt/yourprogram/logs:/app/logs
    networks:
      - yourprogram-network

networks:
  yourprogram-network:
    external: true

volumes:
  app-data:
    driver: local
  logs:
    driver: local
```

#### 배포 스크립트 (deploy.sh)
```bash
#!/bin/bash

set -e

# 설정
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

echo "🚀 Your Program 배포 시작 - 환경: ${ENVIRONMENT}, 버전: ${VERSION}"

# 1. 환경 체크
if [[ ! -f ".env.${ENVIRONMENT}" ]]; then
    echo "❌ 환경 파일이 없습니다: .env.${ENVIRONMENT}"
    exit 1
fi

# 2. 도커 이미지 Pull
echo "📦 도커 이미지 다운로드 중..."
docker-compose -f ${COMPOSE_FILE} pull

# 3. 현재 서비스 백업 (필요시 롤백용)
echo "💾 현재 상태 백업 중..."
docker-compose -f ${COMPOSE_FILE} config > backup/docker-compose-backup-$(date +%Y%m%d-%H%M%S).yml

# 4. 헬스 체크 함수
health_check() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "🏥 ${service} 헬스 체크 중..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$url" >/dev/null 2>&1; then
            echo "✅ ${service} 정상 가동 중"
            return 0
        fi
        
        echo "⏳ ${service} 시작 대기 중... (${attempt}/${max_attempts})"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ ${service} 헬스 체크 실패"
    return 1
}

# 5. 롤링 업데이트 시작
echo "🔄 롤링 업데이트 시작..."

# 서비스별 순차 업데이트
services=("api-gateway" "ai-ml-platform" "data-analysis" "security-monitor")

for service in "${services[@]}"; do
    echo "🔄 ${service} 업데이트 중..."
    
    # 서비스 업데이트
    docker-compose -f ${COMPOSE_FILE} up -d --no-deps ${service}
    
    # 헬스 체크
    case $service in
        "api-gateway")
            health_check $service "http://localhost:8000/health"
            ;;
        "ai-ml-platform")
            health_check $service "http://localhost:8001/health"
            ;;
        "data-analysis")
            health_check $service "http://localhost:8002/health"
            ;;
        "security-monitor")
            health_check $service "http://localhost:8007/security/status"
            ;;
    esac
    
    if [[ $? -ne 0 ]]; then
        echo "❌ ${service} 배포 실패 - 롤백 시작"
        docker-compose -f ${COMPOSE_FILE} restart ${service}
        exit 1
    fi
    
    echo "✅ ${service} 배포 완료"
done

# 6. 정리
echo "🧹 이전 이미지 정리 중..."
docker image prune -f

# 7. 최종 헬스 체크
echo "🔍 전체 시스템 헬스 체크..."
sleep 30

if health_check "전체 시스템" "http://localhost:8000/health"; then
    echo "🎉 배포 완료! 모든 서비스가 정상 가동 중입니다."
    
    # Slack 알림 (선택사항)
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"✅ Your Program 배포 완료 - 환경: '${ENVIRONMENT}', 버전: '${VERSION}'"}' \
            $SLACK_WEBHOOK_URL
    fi
else
    echo "❌ 배포 실패 - 시스템 상태를 확인해 주세요."
    exit 1
fi
```

### 수동 배포 (서비스별)

#### API Gateway 배포
```bash
# 1. 애플리케이션 코드 배포
cd /opt/yourprogram
git pull origin main

# 2. 의존성 설치
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 데이터베이스 마이그레이션
python manage.py migrate

# 4. 정적 파일 수집
python manage.py collectstatic --noinput

# 5. 서비스 재시작
sudo systemctl restart yourprogram-api-gateway
sudo systemctl restart yourprogram-ai-ml
sudo systemctl restart yourprogram-security

# 6. 헬스 체크
curl -f http://localhost:8000/health
```

---

## 로드 밸런서 구성

### Nginx 로드 밸런서 설정

#### 메인 설정 파일 (/etc/nginx/nginx.conf)
```nginx
user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 로그 형식
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for" '
                   'rt=$request_time uct="$upstream_connect_time" '
                   'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    access_log /var/log/nginx/access.log main;
    
    # 기본 설정
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 30;
    keepalive_requests 100;
    
    # 버퍼 설정
    client_max_body_size 100M;
    client_body_buffer_size 1M;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;
    
    # 압축 설정
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
    
    # 업스트림 서버 정의
    upstream api_gateway {
        least_conn;
        server 10.0.10.10:8000 max_fails=3 fail_timeout=30s;
        server 10.0.10.11:8000 max_fails=3 fail_timeout=30s;
        server 10.0.10.12:8000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }
    
    upstream ai_ml_service {
        least_conn;
        server 10.0.10.10:8001 max_fails=3 fail_timeout=30s;
        server 10.0.10.11:8001 max_fails=3 fail_timeout=30s;
        keepalive 16;
    }
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=1r/s;
    
    # SSL 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    
    # 보안 헤더
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    include /etc/nginx/conf.d/*.conf;
}
```

#### 사이트별 설정 (/etc/nginx/conf.d/yourprogram.conf)
```nginx
# HTTP to HTTPS 리다이렉트
server {
    listen 80;
    server_name yourprogram.com www.yourprogram.com api.yourprogram.com admin.yourprogram.com;
    
    # Let's Encrypt ACME 챌린지
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# 메인 웹사이트
server {
    listen 443 ssl http2;
    server_name yourprogram.com www.yourprogram.com;
    
    ssl_certificate /etc/letsencrypt/live/yourprogram.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourprogram.com/privkey.pem;
    
    # 정적 파일 서빙
    location /static/ {
        alias /opt/yourprogram/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /opt/yourprogram/media/;
        expires 7d;
    }
    
    # API 요청은 업스트림으로
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 타임아웃 설정
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 버퍼링 설정
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 16 4k;
    }
    
    # 인증 엔드포인트는 별도 제한
    location /api/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;
        
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 기본 애플리케이션
    location / {
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# API 전용 도메인
server {
    listen 443 ssl http2;
    server_name api.yourprogram.com;
    
    ssl_certificate /etc/letsencrypt/live/yourprogram.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourprogram.com/privkey.pem;
    
    # API 트래픽만 허용
    location / {
        limit_req zone=api_limit burst=50 nodelay;
        
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS 헤더 (필요시)
        add_header Access-Control-Allow-Origin "$http_origin" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}

# 관리자 대시보드
server {
    listen 443 ssl http2;
    server_name admin.yourprogram.com;
    
    ssl_certificate /etc/letsencrypt/live/yourprogram.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourprogram.com/privkey.pem;
    
    # IP 화이트리스트 (관리자 IP만 허용)
    allow 203.0.113.0/24;  # 사무실 IP 대역
    allow 198.51.100.10;   # VPN 서버 IP
    deny all;
    
    location / {
        proxy_pass http://api_gateway/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HAProxy 설정 (대안)

#### haproxy.cfg
```
global
    daemon
    maxconn 4096
    log stdout local0
    stats socket /var/run/haproxy.sock mode 600 level admin
    
    # SSL 설정
    ssl-default-bind-ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog
    option dontlognull
    option redispatch
    retries 3
    
    # 헬스 체크
    option httpchk GET /health
    http-check expect status 200

frontend web_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/yourprogram.pem
    
    # HTTP to HTTPS 리다이렉트
    redirect scheme https if !{ ssl_fc }
    
    # ACL 규칙
    acl is_api hdr(host) -i api.yourprogram.com
    acl is_admin hdr(host) -i admin.yourprogram.com
    acl is_websocket hdr(connection) -i upgrade
    
    # 백엔드 선택
    use_backend api_backend if is_api
    use_backend admin_backend if is_admin
    use_backend websocket_backend if is_websocket
    default_backend web_backend

backend web_backend
    balance roundrobin
    cookie SERVERID insert indirect nocache
    
    server web1 10.0.10.10:8000 check cookie web1
    server web2 10.0.10.11:8000 check cookie web2
    server web3 10.0.10.12:8000 check cookie web3

backend api_backend
    balance leastconn
    
    server api1 10.0.10.10:8000 check
    server api2 10.0.10.11:8000 check
    server api3 10.0.10.12:8000 check

backend admin_backend
    # IP 화이트리스트
    acl admin_ips src 203.0.113.0/24 198.51.100.10
    http-request deny unless admin_ips
    
    server admin1 10.0.10.10:8000 check

# 통계 페이지
listen stats
    bind *:8080
    stats enable
    stats uri /stats
    stats realm HAProxy\ Statistics
    stats auth admin:secure_password
```

---

## 모니터링 설정

### Prometheus 설정

#### prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'yourprogram-monitor'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

rule_files:
  - "alerts/*.yml"

scrape_configs:
  # Your Program 서비스들
  - job_name: 'yourprogram-api'
    static_configs:
      - targets: 
        - '10.0.10.10:8000'
        - '10.0.10.11:8000'
        - '10.0.10.12:8000'
    scrape_interval: 5s
    metrics_path: '/metrics'
    
  - job_name: 'yourprogram-ai-ml'
    static_configs:
      - targets:
        - '10.0.10.10:8001'
        - '10.0.10.11:8001'
    scrape_interval: 10s
    
  - job_name: 'yourprogram-security'
    static_configs:
      - targets:
        - '10.0.10.15:8007'
    scrape_interval: 5s
    
  # 인프라 모니터링
  - job_name: 'node-exporter'
    static_configs:
      - targets:
        - '10.0.10.10:9100'
        - '10.0.10.11:9100'
        - '10.0.10.12:9100'
        - '10.0.20.10:9100'  # DB 서버
        
  - job_name: 'postgres-exporter'
    static_configs:
      - targets:
        - '10.0.20.10:9187'
        
  - job_name: 'redis-exporter'
    static_configs:
      - targets:
        - '10.0.20.11:9121'
        - '10.0.20.12:9121'
        - '10.0.20.13:9121'
        
  - job_name: 'nginx-exporter'
    static_configs:
      - targets:
        - '10.0.1.10:9113'
        - '10.0.1.11:9113'
```

### Grafana 대시보드

#### Grafana 설정 (grafana.ini)
```ini
[server]
http_addr = 0.0.0.0
http_port = 3000
domain = monitor.yourprogram.com
root_url = https://monitor.yourprogram.com/

[security]
admin_user = admin
admin_password = secure_grafana_password
secret_key = your-secret-key-here

[auth]
disable_login_form = false
oauth_auto_login = false

[auth.ldap]
enabled = false

[smtp]
enabled = true
host = smtp.gmail.com:587
user = alerts@yourprogram.com
password = email_app_password
from_address = alerts@yourprogram.com
from_name = Your Program Monitoring

[alerting]
enabled = true
execute_alerts = true

[database]
type = postgres
host = 10.0.20.10:5432
name = grafana
user = grafana_user
password = grafana_password
```

#### 대시보드 JSON (시스템 모니터링)
```json
{
  "dashboard": {
    "id": null,
    "title": "Your Program 시스템 모니터링",
    "tags": ["yourprogram", "system"],
    "timezone": "Asia/Seoul",
    "panels": [
      {
        "id": 1,
        "title": "시스템 상태",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"yourprogram-.*\"}",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "CPU 사용률",
        "type": "timeseries",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "id": 3,
        "title": "메모리 사용률",
        "type": "timeseries",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      }
    ]
  }
}
```

---

## 보안 설정

### 방화벽 설정

#### UFW 규칙 (각 서버별)

**웹 서버:**
```bash
# 기본 정책
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (VPN을 통해서만)
sudo ufw allow from 10.0.0.0/8 to any port 22

# HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 헬스 체크 (로드 밸런서에서)
sudo ufw allow from 10.0.1.0/24 to any port 8000:8010

sudo ufw enable
```

**애플리케이션 서버:**
```bash
# SSH (VPN을 통해서만)
sudo ufw allow from 10.0.0.0/8 to any port 22

# 웹 서버에서의 요청
sudo ufw allow from 10.0.1.0/24 to any port 8000:8010

# 데이터베이스 접근
sudo ufw allow from 10.0.20.0/24 to any port 5432
sudo ufw allow from 10.0.20.0/24 to any port 6379

# 모니터링
sudo ufw allow from 10.0.30.0/24 to any port 9100

sudo ufw enable
```

**데이터베이스 서버:**
```bash
# SSH
sudo ufw allow from 10.0.0.0/8 to any port 22

# 애플리케이션 서버에서만 DB 접근
sudo ufw allow from 10.0.10.0/24 to any port 5432
sudo ufw allow from 10.0.10.0/24 to any port 6379

# 복제 (Master-Slave)
sudo ufw allow from 10.0.20.0/24 to any port 5432

# 백업 서버
sudo ufw allow from 10.0.40.0/24 to any port 5432

sudo ufw enable
```

### SSL/TLS 설정

#### Nginx SSL 최적화
```nginx
# SSL 설정 최적화
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
ssl_prefer_server_ciphers off;

# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/yourprogram.com/chain.pem;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# DH Parameters
ssl_dhparam /etc/ssl/certs/dhparam.pem;
```

#### SSL 인증서 자동 갱신
```bash
# 인증서 갱신 스크립트
#!/bin/bash
# renew-ssl.sh

certbot renew --quiet --nginx

# Nginx 설정 테스트
if nginx -t; then
    systemctl reload nginx
    echo "SSL 인증서 갱신 및 Nginx 리로드 완료"
else
    echo "Nginx 설정 오류 - 리로드 취소"
    exit 1
fi

# 만료일 체크
expiry_date=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/yourprogram.com/cert.pem | cut -d= -f2)
echo "SSL 인증서 만료일: $expiry_date"

# 30일 이내 만료시 알림
if openssl x509 -checkend 2592000 -noout -in /etc/letsencrypt/live/yourprogram.com/cert.pem; then
    echo "SSL 인증서가 30일 이내에 만료됩니다."
fi
```

### 보안 강화

#### 시스템 보안 설정
```bash
# 1. 시스템 업데이트 자동화
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades
sudo systemctl enable unattended-upgrades

# 2. Fail2Ban 설정
sudo apt install -y fail2ban

# /etc/fail2ban/jail.local
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-req-limit]
enabled = true
filter = nginx-req-limit
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 3. 파일 무결성 모니터링 (AIDE)
sudo apt install -y aide
sudo aideinit
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# 일일 체크 크론
echo "0 2 * * * /usr/bin/aide --check" | sudo crontab -
```

---

## 백업 및 복구

### 자동 백업 시스템

#### 데이터베이스 백업 스크립트
```bash
#!/bin/bash
# backup-database.sh

set -e

# 설정
BACKUP_DIR="/opt/backups/database"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="yourprogram"
DB_USER="backup_user"
DB_HOST="db-master.internal"

# S3 설정 (선택사항)
S3_BUCKET="yourprogram-backups"
S3_PREFIX="database"

mkdir -p $BACKUP_DIR

echo "🗃️ 데이터베이스 백업 시작: $DATE"

# 1. PostgreSQL 백업
echo "📦 PostgreSQL 백업 중..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --format=custom \
    --compress=9 \
    --no-owner \
    --no-privileges \
    > $BACKUP_DIR/postgresql_${DATE}.dump

# 백업 파일 압축
gzip $BACKUP_DIR/postgresql_${DATE}.dump

# 2. 백업 검증
echo "🔍 백업 파일 검증 중..."
if [[ -f "$BACKUP_DIR/postgresql_${DATE}.dump.gz" ]]; then
    size=$(stat -f%z "$BACKUP_DIR/postgresql_${DATE}.dump.gz" 2>/dev/null || stat -c%s "$BACKUP_DIR/postgresql_${DATE}.dump.gz")
    if [[ $size -gt 1000000 ]]; then  # 1MB 이상
        echo "✅ 백업 성공: ${size} bytes"
    else
        echo "❌ 백업 파일이 너무 작습니다: ${size} bytes"
        exit 1
    fi
else
    echo "❌ 백업 파일을 찾을 수 없습니다"
    exit 1
fi

# 3. S3 업로드 (선택사항)
if command -v aws &> /dev/null && [[ -n "$S3_BUCKET" ]]; then
    echo "☁️ S3 업로드 중..."
    aws s3 cp $BACKUP_DIR/postgresql_${DATE}.dump.gz \
        s3://$S3_BUCKET/$S3_PREFIX/postgresql_${DATE}.dump.gz \
        --storage-class STANDARD_IA
    
    if [[ $? -eq 0 ]]; then
        echo "✅ S3 업로드 완료"
    else
        echo "⚠️ S3 업로드 실패"
    fi
fi

# 4. 오래된 백업 삭제
echo "🧹 오래된 백업 정리 중..."
find $BACKUP_DIR -name "postgresql_*.dump.gz" -mtime +$RETENTION_DAYS -delete

# 5. Redis 백업
echo "📦 Redis 백업 중..."
redis-cli --rdb $BACKUP_DIR/redis_${DATE}.rdb
gzip $BACKUP_DIR/redis_${DATE}.rdb

# 6. 애플리케이션 데이터 백업
echo "📦 애플리케이션 데이터 백업 중..."
tar -czf $BACKUP_DIR/app_data_${DATE}.tar.gz \
    /opt/yourprogram/uploads \
    /opt/yourprogram/media \
    /opt/yourprogram/logs \
    --exclude='*.tmp' \
    --exclude='*.log'

echo "🎉 백업 완료: $DATE"

# 알림 (선택사항)
if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"✅ Your Program 데이터베이스 백업 완료 - '${DATE}'"}' \
        $SLACK_WEBHOOK_URL
fi
```

#### 시스템 설정 백업
```bash
#!/bin/bash
# backup-system.sh

BACKUP_DIR="/opt/backups/system"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "⚙️ 시스템 설정 백업 시작: $DATE"

# 1. Nginx 설정
tar -czf $BACKUP_DIR/nginx_config_${DATE}.tar.gz /etc/nginx/

# 2. SSL 인증서
tar -czf $BACKUP_DIR/ssl_certs_${DATE}.tar.gz /etc/letsencrypt/

# 3. 애플리케이션 설정
tar -czf $BACKUP_DIR/app_config_${DATE}.tar.gz \
    /opt/yourprogram/config/ \
    /opt/yourprogram/.env.* \
    /opt/yourprogram/docker-compose.*.yml

# 4. 시스템 설정
tar -czf $BACKUP_DIR/system_config_${DATE}.tar.gz \
    /etc/systemd/system/yourprogram* \
    /etc/cron.d/yourprogram* \
    /etc/logrotate.d/yourprogram*

# 5. 방화벽 규칙
ufw status numbered > $BACKUP_DIR/ufw_rules_${DATE}.txt

echo "✅ 시스템 설정 백업 완료: $DATE"
```

### 복구 절차

#### 데이터베이스 복구
```bash
#!/bin/bash
# restore-database.sh

BACKUP_FILE=$1
DB_NAME="yourprogram"
DB_USER="postgres"
DB_HOST="localhost"

if [[ -z "$BACKUP_FILE" ]]; then
    echo "사용법: $0 <backup_file.dump.gz>"
    exit 1
fi

echo "🔄 데이터베이스 복구 시작"

# 1. 백업 파일 압축 해제
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" > "${BACKUP_FILE%.gz}"
    BACKUP_FILE="${BACKUP_FILE%.gz}"
fi

# 2. 기존 데이터베이스 백업 (안전장치)
echo "💾 현재 데이터베이스 백업 중..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --format=custom > /tmp/pre_restore_backup_$(date +%Y%m%d_%H%M%S).dump

# 3. 연결 종료
echo "🔌 기존 연결 종료 중..."
psql -h $DB_HOST -U $DB_USER -d postgres -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"

# 4. 데이터베이스 재생성
echo "🗑️ 데이터베이스 재생성 중..."
dropdb -h $DB_HOST -U $DB_USER $DB_NAME
createdb -h $DB_HOST -U $DB_USER $DB_NAME

# 5. 복구 실행
echo "📥 데이터 복구 중..."
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --verbose \
    --clean \
    --no-owner \
    --no-privileges \
    "$BACKUP_FILE"

if [[ $? -eq 0 ]]; then
    echo "✅ 데이터베이스 복구 완료"
    
    # 6. 애플리케이션 재시작
    echo "🔄 애플리케이션 재시작 중..."
    sudo systemctl restart yourprogram-*
    
    # 7. 헬스 체크
    sleep 30
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 복구 후 시스템 정상 확인"
    else
        echo "⚠️ 복구 후 시스템 상태 확인 필요"
    fi
else
    echo "❌ 데이터베이스 복구 실패"
    exit 1
fi
```

### 재해 복구 계획

#### RTO/RPO 목표
```
Recovery Time Objective (RTO):
- 핵심 서비스: 1시간 이내
- 일반 서비스: 4시간 이내
- 부가 서비스: 1일 이내

Recovery Point Objective (RPO):
- 핵심 데이터: 15분 이내
- 일반 데이터: 1시간 이내
- 로그 데이터: 4시간 이내
```

#### 재해 복구 절차
```bash
#!/bin/bash
# disaster-recovery.sh

echo "🚨 재해 복구 절차 시작"

# 1. 상황 평가
echo "1️⃣ 시스템 상태 평가 중..."
./scripts/health-check.sh

# 2. 백업 서버로 전환
echo "2️⃣ 백업 데이터센터로 DNS 전환..."
# DNS 업데이트 스크립트 실행
./scripts/update-dns-failover.sh

# 3. 데이터베이스 복구
echo "3️⃣ 최신 백업으로 데이터베이스 복구..."
LATEST_BACKUP=$(ls -t /opt/backups/database/postgresql_*.dump.gz | head -1)
./scripts/restore-database.sh "$LATEST_BACKUP"

# 4. 애플리케이션 시작
echo "4️⃣ 애플리케이션 서비스 시작..."
docker-compose -f docker-compose.production.yml up -d

# 5. 헬스 체크
echo "5️⃣ 서비스 상태 확인..."
sleep 60
./scripts/health-check.sh

echo "✅ 재해 복구 절차 완료"
```

---

## 성능 최적화

### 애플리케이션 최적화

#### Python/Django 최적화
```python
# settings/production.py

# 데이터베이스 최적화
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yourprogram',
        'USER': 'yourprogram',
        'PASSWORD': 'password',
        'HOST': 'db-master.internal',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'conn_max_age': 600,
        }
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yourprogram',
        'USER': 'yourprogram',
        'PASSWORD': 'password', 
        'HOST': 'db-slave.internal',
        'PORT': '5432',
    }
}

# 캐시 설정
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis://redis-1.internal:6379/1',
            'redis://redis-2.internal:6379/1',
            'redis://redis-3.internal:6379/1',
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.ShardClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}

# 세션 설정
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24시간

# 로깅 최적화
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/yourprogram/django.log',
            'maxBytes': 1024*1024*100,  # 100MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'WARNING',
    },
}
```

#### Gunicorn 최적화 (gunicorn.conf.py)
```python
import multiprocessing

# 서버 설정
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# 로깅
accesslog = "/var/log/yourprogram/gunicorn-access.log"
errorlog = "/var/log/yourprogram/gunicorn-error.log"
loglevel = "warning"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 관리
preload_app = True
worker_tmp_dir = "/dev/shm"
user = "yourprogram"
group = "yourprogram"

# 성능 최적화
worker_class = "uvicorn.workers.UvicornWorker"  # FastAPI용
```

### 데이터베이스 최적화

#### PostgreSQL 성능 튜닝
```sql
-- 인덱스 최적화
-- 1. 자주 조회되는 컬럼에 인덱스 생성
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);
CREATE INDEX CONCURRENTLY idx_orders_created_at ON orders(created_at DESC);

-- 2. 복합 인덱스 생성
CREATE INDEX CONCURRENTLY idx_orders_user_status ON orders(user_id, status);
CREATE INDEX CONCURRENTLY idx_logs_level_timestamp ON logs(level, timestamp DESC);

-- 3. 부분 인덱스 생성
CREATE INDEX CONCURRENTLY idx_active_users ON users(id) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_pending_orders ON orders(id) WHERE status = 'pending';

-- 쿼리 최적화
-- 1. 통계 정보 업데이트
ANALYZE;

-- 2. 불필요한 인덱스 제거
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 
    AND indexname NOT LIKE '%_pkey';

-- 3. 테이블 파티셔닝 (대용량 테이블)
CREATE TABLE logs_2024 PARTITION OF logs
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 4. 정기 메인터넌스
-- 매주 실행
VACUUM ANALYZE;

-- 매월 실행 (트래픽이 적은 시간)
REINDEX DATABASE yourprogram;
```

### 캐시 전략

#### Redis 캐시 최적화
```python
# cache_utils.py
import redis
import pickle
import json
from functools import wraps
from typing import Any, Optional
import hashlib

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='redis-cluster.internal',
            port=6379,
            password='redis_password',
            decode_responses=False,
            health_check_interval=30
        )
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def set_cache(self, key: str, value: Any, ttl: int = 3600):
        """캐시 설정"""
        try:
            serialized = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"캐시 설정 실패: {e}")
    
    def get_cache(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        try:
            cached = self.redis_client.get(key)
            if cached:
                return pickle.loads(cached)
        except Exception as e:
            print(f"캐시 조회 실패: {e}")
        return None

cache_manager = CacheManager()

def cache_result(prefix: str, ttl: int = 3600):
    """캐시 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cache_manager.generate_key(prefix, *args, **kwargs)
            
            # 캐시에서 조회
            result = cache_manager.get_cache(cache_key)
            if result is not None:
                return result
            
            # 캐시 미스 시 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            cache_manager.set_cache(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# 사용 예시
@cache_result("user_profile", ttl=1800)  # 30분 캐싱
def get_user_profile(user_id: int):
    # 데이터베이스 조회
    return User.objects.get(id=user_id)

@cache_result("dashboard_data", ttl=300)  # 5분 캐싱
def get_dashboard_data(user_id: int, date_range: str):
    # 복잡한 데이터 조회 및 계산
    return calculate_dashboard_metrics(user_id, date_range)
```

---

## 운영 가이드

### 일상 운영 체크리스트

#### 일일 점검 (9:00 AM)
```bash
#!/bin/bash
# daily-check.sh

echo "📋 일일 시스템 점검 시작 - $(date)"

# 1. 시스템 상태 확인
echo "1️⃣ 시스템 상태 점검..."
curl -f http://localhost:8000/health || echo "❌ API Gateway 이상"
curl -f http://localhost:8001/health || echo "❌ AI/ML 서비스 이상"
curl -f http://localhost:8007/security/status || echo "❌ 보안 모니터링 이상"

# 2. 디스크 사용량 확인
echo "2️⃣ 디스크 사용량 점검..."
df -h | awk '$5 > 80 {print "⚠️ 디스크 사용률 80% 초과: " $1 " " $5}'

# 3. 메모리 사용량 확인
echo "3️⃣ 메모리 사용량 점검..."
free -m | awk 'NR==2{printf "메모리 사용률: %.1f%%\n", $3*100/($3+$7)}'

# 4. 로그 에러 확인
echo "4️⃣ 로그 에러 점검..."
tail -n 100 /var/log/yourprogram/*.log | grep -i error | tail -5

# 5. SSL 인증서 만료일 확인
echo "5️⃣ SSL 인증서 점검..."
openssl x509 -enddate -noout -in /etc/letsencrypt/live/yourprogram.com/cert.pem

# 6. 백업 상태 확인
echo "6️⃣ 백업 상태 점검..."
if [[ -f "/opt/backups/database/postgresql_$(date +%Y%m%d)_*.dump.gz" ]]; then
    echo "✅ 당일 데이터베이스 백업 확인됨"
else
    echo "❌ 당일 데이터베이스 백업 없음"
fi

echo "📋 일일 점검 완료 - $(date)"
```

#### 주간 점검 (일요일 오전)
```bash
#!/bin/bash
# weekly-check.sh

echo "📊 주간 시스템 점검 시작 - $(date)"

# 1. 성능 트렌드 분석
echo "1️⃣ 성능 트렌드 분석..."
# Prometheus 쿼리로 주간 성능 데이터 조회
curl -s "http://monitor.internal:9090/api/v1/query_range?query=cpu_usage&start=$(date -d '7 days ago' +%s)&end=$(date +%s)&step=3600" | jq .

# 2. 보안 이벤트 리뷰
echo "2️⃣ 보안 이벤트 리뷰..."
curl -s "http://localhost:8007/security/events?start_time=$(date -d '7 days ago' --iso-8601)&severity=high" | jq '.data.total'

# 3. 데이터베이스 성능 점검
echo "3️⃣ 데이터베이스 성능 점검..."
psql -h db-master.internal -U yourprogram -d yourprogram -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins + n_tup_upd + n_tup_del as total_changes,
    n_tup_hot_upd,
    n_dead_tup
FROM pg_stat_user_tables 
ORDER BY total_changes DESC 
LIMIT 10;"

# 4. 디스크 사용량 트렌드
echo "4️⃣ 디스크 사용량 트렌드..."
du -sh /opt/yourprogram/* | sort -hr

# 5. 로그 로테이션 확인
echo "5️⃣ 로그 로테이션 점검..."
logrotate -d /etc/logrotate.conf

echo "📊 주간 점검 완료 - $(date)"
```

### 문제 해결 가이드

#### 일반적인 문제와 해결책

**1. 높은 CPU 사용률**
```bash
# 원인 파악
top -p $(pgrep -d',' python)
htop

# 프로세스별 CPU 사용률 확인
ps aux --sort=-%cpu | head -10

# 해결 방법
# - 워커 프로세스 수 조정
# - 비효율적 코드 최적화
# - 캐싱 추가
```

**2. 메모리 부족**
```bash
# 메모리 사용량 확인
free -h
ps aux --sort=-%mem | head -10

# 메모리 덤프 분석 (Python)
python -c "
import psutil
for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
    try:
        if proc.info['memory_info'].rss > 100 * 1024 * 1024:  # 100MB 이상
            print(f'{proc.info[\"pid\"]} {proc.info[\"name\"]} {proc.info[\"memory_info\"].rss / 1024 / 1024:.1f}MB')
    except:
        pass
"

# 해결 방법
# - 메모리 누수 코드 수정
# - 가비지 컬렉션 최적화
# - 워커 프로세스 재시작 주기 설정
```

**3. 데이터베이스 연결 문제**
```bash
# 연결 상태 확인
psql -h db-master.internal -U yourprogram -d yourprogram -c "
SELECT 
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit
FROM pg_stat_database 
WHERE datname = 'yourprogram';"

# 활성 연결 확인
psql -h db-master.internal -U yourprogram -d yourprogram -c "
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity 
WHERE datname = 'yourprogram';"

# 해결 방법
# - 연결 풀 설정 조정
# - 오래된 연결 종료
# - 데이터베이스 재시작 (최후 수단)
```

### 배포 롤백 절차

#### 빠른 롤백
```bash
#!/bin/bash
# rollback.sh

ENVIRONMENT=${1:-production}
BACKUP_VERSION=${2}

echo "🔄 롤백 시작 - 환경: ${ENVIRONMENT}"

if [[ -z "$BACKUP_VERSION" ]]; then
    # 최근 백업 찾기
    BACKUP_VERSION=$(ls backup/docker-compose-backup-*.yml | sort -r | head -1)
fi

echo "📦 롤백 대상: $BACKUP_VERSION"

# 1. 현재 상태 백업
docker-compose -f docker-compose.${ENVIRONMENT}.yml config > backup/rollback-from-$(date +%Y%m%d-%H%M%S).yml

# 2. 이전 버전으로 복원
cp $BACKUP_VERSION docker-compose.${ENVIRONMENT}.yml

# 3. 서비스 재시작
docker-compose -f docker-compose.${ENVIRONMENT}.yml down
docker-compose -f docker-compose.${ENVIRONMENT}.yml up -d

# 4. 헬스 체크
sleep 60
./scripts/health-check.sh

if [[ $? -eq 0 ]]; then
    echo "✅ 롤백 완료"
else
    echo "❌ 롤백 실패 - 수동 확인 필요"
fi
```

### 성능 튜닝 가이드

#### 응답 시간 최적화
```bash
# 1. 애플리케이션 성능 분석
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# curl-format.txt 내용:
#     time_namelookup:  %{time_namelookup}\n
#     time_connect:     %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#     time_pretransfer: %{time_pretransfer}\n
#     time_redirect:    %{time_redirect}\n
#     time_starttransfer: %{time_starttransfer}\n
#     ----------\n
#     time_total:       %{time_total}\n

# 2. 데이터베이스 쿼리 분석
psql -h db-master.internal -U yourprogram -d yourprogram -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

---

**이 배포 가이드는 Your Program의 안전하고 효율적인 프로덕션 배포를 위한 완전한 매뉴얼입니다. 배포 과정에서 문제가 발생하거나 추가 지원이 필요한 경우 시스템 관리팀에 문의하시기 바랍니다.**

**문서 버전**: 1.0.0  
**최종 업데이트**: 2024년 1월 19일  
**담당팀**: DevOps팀  
**지원 연락처**: devops@yourcompany.com 