# 🚀 Your Program 운영 가이드

**버전**: 1.0  
**최종 업데이트**: 2025년 7월 29일  
**작성자**: AI Assistant

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [환경 설정](#환경-설정)
3. [배포 가이드](#배포-가이드)
4. [모니터링 및 로깅](#모니터링-및-로깅)
5. [보안 관리](#보안-관리)
6. [백업 및 복구](#백업-및-복구)
7. [문제 해결](#문제-해결)
8. [성능 최적화](#성능-최적화)
9. [API 문서](#api-문서)
10. [자주 묻는 질문](#자주-묻는-질문)

## 🏗️ 시스템 개요

### 아키텍처
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │◄──►│   (Flask)       │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 5000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   WebSocket     │◄─────────────┘
                        │   (Socket.IO)   │
                        │   Port: 5000    │
                        └─────────────────┘
```

### 주요 구성 요소
- **Frontend**: Next.js 기반 React 애플리케이션
- **Backend**: Flask 기반 Python API 서버
- **Database**: PostgreSQL 데이터베이스
- **Cache**: Redis 캐시 서버
- **WebSocket**: 실시간 알림 시스템
- **AI Models**: TensorFlow/Scikit-learn 기반 AI 모델
- **Monitoring**: Grafana + Prometheus 모니터링

## ⚙️ 환경 설정

### 1. 시스템 요구사항

#### 최소 요구사항
- **CPU**: 2코어 이상
- **RAM**: 4GB 이상
- **Storage**: 20GB 이상
- **OS**: Ubuntu 20.04+, CentOS 8+, Windows 10+

#### 권장 요구사항
- **CPU**: 4코어 이상
- **RAM**: 8GB 이상
- **Storage**: 50GB 이상 (SSD 권장)
- **Network**: 100Mbps 이상

### 2. 환경변수 설정

#### 개발 환경 설정
```bash
# 환경변수 관리자 사용
python -c "
from config.environment_manager import env_manager
env_manager.create_env_file('development', {
    'DATABASE_URL': 'postgresql://postgres:postgres@localhost:5432/your_program_dev',
    'SECRET_KEY': 'your-secret-key-here',
    'FLASK_ENV': 'development',
    'DEBUG': True,
    'LOG_LEVEL': 'DEBUG'
})
"
```

#### 프로덕션 환경 설정
```bash
# 프로덕션 환경변수 설정
python -c "
from config.environment_manager import env_manager
env_manager.create_env_file('production', {
    'DATABASE_URL': 'postgresql://user:password@prod-db:5432/your_program',
    'SECRET_KEY': 'your-production-secret-key',
    'FLASK_ENV': 'production',
    'DEBUG': False,
    'LOG_LEVEL': 'INFO',
    'SESSION_COOKIE_SECURE': True,
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'your-email@gmail.com',
    'MAIL_PASSWORD': 'your-app-password'
})
"
```

### 3. 데이터베이스 설정

#### PostgreSQL 설치 및 설정
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# PostgreSQL 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 데이터베이스 생성
sudo -u postgres psql
CREATE DATABASE your_program;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_program TO your_user;
\q
```

#### Redis 설치 및 설정
```bash
# Ubuntu/Debian
sudo apt install redis-server

# Redis 서비스 시작
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Redis 설정 확인
redis-cli ping
```

## 🚀 배포 가이드

### 1. Docker를 사용한 배포

#### 개발 환경 배포
```bash
# 개발 환경 시작
docker-compose --profile dev up -d

# 로그 확인
docker-compose logs -f app
```

#### 프로덕션 환경 배포
```bash
# 프로덕션 환경 배포
./scripts/deploy.sh production v1.0.0

# 또는 Docker Compose 사용
docker-compose -f docker-compose.production.yml up -d
```

### 2. 수동 배포

#### 백엔드 배포
```bash
# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
python -m alembic upgrade head

# 애플리케이션 시작
python app.py
```

#### 프론트엔드 배포
```bash
# 의존성 설치
cd frontend
npm install

# 빌드
npm run build

# 개발 서버 시작
npm run dev
```

### 3. CI/CD 파이프라인 배포

#### GitHub Actions를 통한 자동 배포
```bash
# develop 브랜치 푸시 (개발 환경 배포)
git push origin develop

# main 브랜치 푸시 (프로덕션 환경 배포)
git push origin main
```

## 📊 모니터링 및 로깅

### 1. 시스템 모니터링

#### Grafana 대시보드 접근
- **URL**: http://localhost:3001
- **기본 계정**: admin / admin
- **대시보드**: 시스템 성능, 애플리케이션 메트릭, 사용자 활동

#### Prometheus 메트릭
- **URL**: http://localhost:9090
- **메트릭**: CPU, 메모리, 디스크, 네트워크, 애플리케이션 성능

### 2. 로그 관리

#### 로그 파일 위치
```
logs/
├── app.log              # 애플리케이션 로그
├── error.log            # 오류 로그
├── access.log           # 접근 로그
├── security.log         # 보안 로그
└── websocket.log        # WebSocket 로그
```

#### 로그 레벨 설정
```python
# 환경변수로 로그 레벨 설정
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

#### 로그 로테이션
```bash
# 로그 파일 크기 제한 및 자동 로테이션
logrotate /etc/logrotate.d/your_program
```

### 3. 알림 설정

#### WebSocket 실시간 알림
- **시스템 알림**: 서버 상태, 오류, 성능 이슈
- **사용자 알림**: 로그인, 데이터 업데이트, 권한 변경
- **AI 알림**: 모델 학습 완료, 예측 결과

#### 외부 알림 서비스
```python
# Slack 알림 설정
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# 이메일 알림 설정
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 🔒 보안 관리

### 1. 보안 정책 설정

#### 비밀번호 정책
```python
# 보안 정책 업데이트
from config.security_config import security_config

security_config.update_security_policy({
    'password_policy': {
        'min_length': 12,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_digits': True,
        'require_special_chars': True,
        'max_age_days': 90
    }
})
```

#### 세션 보안
```python
# 세션 보안 설정
security_config.update_security_policy({
    'session_policy': {
        'max_session_duration_hours': 24,
        'inactive_timeout_minutes': 30,
        'require_secure_cookies': True,
        'require_http_only': True,
        'same_site_policy': 'Lax'
    }
})
```

### 2. API 보안

#### Rate Limiting
```python
# API 요청 제한 설정
security_config.update_security_policy({
    'api_security': {
        'rate_limit_requests': 100,
        'rate_limit_window_minutes': 15,
        'require_api_key': True
    }
})
```

#### CORS 설정
```python
# CORS 정책 설정
security_config.update_security_policy({
    'network_security': {
        'cors_allowed_origins': ['https://yourdomain.com'],
        'cors_allowed_methods': ['GET', 'POST', 'PUT', 'DELETE'],
        'cors_allowed_headers': ['Content-Type', 'Authorization']
    }
})
```

### 3. 데이터 보안

#### 암호화 설정
```python
# 데이터 암호화 설정
security_config.update_security_policy({
    'data_protection': {
        'encrypt_sensitive_data': True,
        'encryption_algorithm': 'AES-256-GCM',
        'key_rotation_days': 90,
        'secure_deletion': True
    }
})
```

## 💾 백업 및 복구

### 1. 자동 백업 설정

#### 데이터베이스 백업
```bash
# PostgreSQL 백업 스크립트
#!/bin/bash
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U postgres your_program > "$BACKUP_DIR/backup_$DATE.sql"

# 30일 이상 된 백업 삭제
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

#### 파일 백업
```bash
# 업로드 파일 백업
#!/bin/bash
BACKUP_DIR="/backups/files"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" uploads/

# 로그 파일 백업
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/
```

### 2. 복구 절차

#### 데이터베이스 복구
```bash
# PostgreSQL 복구
psql -h localhost -U postgres your_program < backup_20250729_143000.sql
```

#### 파일 복구
```bash
# 업로드 파일 복구
tar -xzf uploads_20250729_143000.tar.gz

# 로그 파일 복구
tar -xzf logs_20250729_143000.tar.gz
```

### 3. 재해 복구 계획

#### 백업 검증
```bash
# 백업 파일 무결성 검사
md5sum backup_*.sql > backup_checksums.md5
md5sum -c backup_checksums.md5
```

#### 복구 테스트
```bash
# 정기적인 복구 테스트 수행
# 1. 테스트 환경에 백업 복원
# 2. 애플리케이션 기능 테스트
# 3. 데이터 무결성 검증
```

## 🔧 문제 해결

### 1. 일반적인 문제

#### 애플리케이션 시작 실패
```bash
# 로그 확인
tail -f logs/app.log

# 포트 사용 확인
netstat -tulpn | grep :5000

# 프로세스 확인
ps aux | grep python
```

#### 데이터베이스 연결 오류
```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 연결 테스트
psql -h localhost -U postgres -d your_program

# 방화벽 설정 확인
sudo ufw status
```

#### WebSocket 연결 오류
```bash
# WebSocket 서버 상태 확인
curl -I http://localhost:5000/socket.io/

# 브라우저 개발자 도구에서 WebSocket 연결 확인
# Network 탭 > WS 필터
```

### 2. 성능 문제

#### 메모리 사용량 높음
```bash
# 메모리 사용량 확인
free -h
ps aux --sort=-%mem | head -10

# Redis 메모리 사용량 확인
redis-cli info memory
```

#### CPU 사용량 높음
```bash
# CPU 사용량 확인
top
htop

# 프로세스별 CPU 사용량
ps aux --sort=-%cpu | head -10
```

#### 디스크 공간 부족
```bash
# 디스크 사용량 확인
df -h

# 큰 파일 찾기
find / -type f -size +100M -exec ls -lh {} \;

# 로그 파일 정리
find logs/ -name "*.log" -mtime +7 -delete
```

### 3. 보안 문제

#### 무단 접근 시도
```bash
# 로그인 실패 로그 확인
grep "Failed login" logs/security.log

# 의심스러운 IP 차단
sudo ufw deny from 192.168.1.100
```

#### API 남용
```bash
# API 요청 로그 확인
grep "API" logs/access.log | tail -50

# Rate limiting 설정 확인
redis-cli get "rate_limit:user:123"
```

## ⚡ 성능 최적화

### 1. 데이터베이스 최적화

#### 인덱스 최적화
```sql
-- 느린 쿼리 분석
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 인덱스 생성
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

#### 쿼리 최적화
```sql
-- 페이지네이션 최적화
SELECT * FROM orders 
ORDER BY created_at DESC 
LIMIT 20 OFFSET 40;

-- 조인 최적화
SELECT u.name, o.total 
FROM users u 
INNER JOIN orders o ON u.id = o.user_id 
WHERE o.status = 'completed';
```

### 2. 캐시 최적화

#### Redis 캐시 설정
```python
# 캐시 설정
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_DEFAULT_TIMEOUT = 300
CACHE_KEY_PREFIX = 'your_program:'
```

#### 캐시 전략
```python
# 자주 사용되는 데이터 캐싱
@cache.memoize(timeout=3600)
def get_user_profile(user_id):
    return User.query.get(user_id)

# 캐시 무효화
cache.delete_memoized(get_user_profile, user_id)
```

### 3. 프론트엔드 최적화

#### 번들 최적화
```javascript
// Next.js 설정
module.exports = {
  experimental: {
    optimizeCss: true,
    optimizeImages: true,
  },
  webpack: (config) => {
    config.optimization.splitChunks = {
      chunks: 'all',
    }
    return config
  },
}
```

#### 이미지 최적화
```javascript
// Next.js Image 컴포넌트 사용
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={100}
  priority
/>
```

## 📚 API 문서

### 1. 인증 API

#### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### 토큰 갱신
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

### 2. 사용자 API

#### 사용자 정보 조회
```http
GET /api/users/profile
Authorization: Bearer <access_token>
```

#### 사용자 정보 수정
```http
PUT /api/users/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "New Name",
  "email": "newemail@example.com"
}
```

### 3. AI 모델 API

#### 예측 요청
```http
POST /api/ai/predict
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "model": "sales_prediction",
  "data": {
    "feature1": 100,
    "feature2": 200
  }
}
```

#### 모델 상태 조회
```http
GET /api/ai/models/status
Authorization: Bearer <access_token>
```

### 4. WebSocket API

#### 연결
```javascript
const socket = io('http://localhost:5000', {
  query: { user_id: 'user123' }
})
```

#### 알림 구독
```javascript
socket.emit('subscribe_notifications', {
  types: ['system_alert', 'ai_prediction']
})
```

## ❓ 자주 묻는 질문

### Q1: 시스템을 처음 설치할 때 필요한 단계는?
A1: 
1. 시스템 요구사항 확인
2. 환경변수 설정 (`python -c "from config.environment_manager import env_manager; env_manager.create_env_file('development')"`)
3. 데이터베이스 설정
4. 의존성 설치 (`pip install -r requirements.txt`)
5. 마이그레이션 실행 (`python -m alembic upgrade head`)
6. 애플리케이션 시작 (`python app.py`)

### Q2: 프로덕션 환경에서 성능을 최적화하는 방법은?
A2:
1. 데이터베이스 인덱스 최적화
2. Redis 캐시 활용
3. CDN 사용 (정적 파일)
4. 로드 밸런서 설정
5. 모니터링 도구 활용

### Q3: 보안을 강화하는 방법은?
A3:
1. 강력한 비밀번호 정책 설정
2. HTTPS 강제
3. Rate limiting 설정
4. 정기적인 보안 업데이트
5. 로그 모니터링

### Q4: 백업은 어떻게 설정하나요?
A4:
1. 자동 백업 스크립트 설정
2. 정기적인 백업 테스트
3. 여러 위치에 백업 저장
4. 백업 파일 암호화
5. 복구 절차 문서화

### Q5: 문제가 발생했을 때 어떻게 해결하나요?
A5:
1. 로그 파일 확인
2. 모니터링 대시보드 확인
3. 시스템 리소스 상태 확인
4. 데이터베이스 연결 확인
5. 필요시 백업에서 복구

## 📞 지원 및 연락처

### 기술 지원
- **이메일**: support@yourprogram.com
- **문서**: https://docs.yourprogram.com
- **GitHub**: https://github.com/yourprogram/issues

### 긴급 상황
- **24/7 지원**: +82-2-1234-5678
- **긴급 이메일**: emergency@yourprogram.com

---

**© 2025 Your Program. All rights reserved.** 