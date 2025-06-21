# 🚀 운영 배포 가이드

## 📋 1. 환경 설정 파일 분리

### 개발 환경 (.env.development)
```ini
FLASK_ENV=development
SECRET_KEY=dev-secret-key-1234
DATABASE_URL=sqlite:///core_db.sqlite3
DEBUG=1
LOG_LEVEL=DEBUG
```

### 운영 환경 (.env.production)
```ini
FLASK_ENV=production
SECRET_KEY=prod-secret-key-5678
DATABASE_URL=sqlite:///restaurant_prod.sqlite3
DEBUG=0
LOG_LEVEL=INFO
```

## 📋 2. Gunicorn + Nginx 배포

### requirements.txt에 추가
```txt
gunicorn==21.2.0
```

### 배포 명령
```bash
# Gunicorn으로 실행
gunicorn -w 4 -b 0.0.0.0:8000 app_core:app

# 백그라운드 실행
nohup gunicorn -w 4 -b 0.0.0.0:8000 app_core:app &
```

### Nginx 설정 예시
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/static;
    }
}
```

## 📋 3. 데이터베이스 백업/마이그레이션

### SQLite 백업
```bash
# 백업
cp core_db.sqlite3 backup_$(date +%Y%m%d_%H%M%S).sqlite3

# 복원
cp backup_20241201_143000.sqlite3 core_db.sqlite3
```

### PostgreSQL 마이그레이션
```python
# app_core.py에서 DATABASE_URL 변경
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/restaurant_db'
```

### Alembic 마이그레이션 (권장)
```bash
# 설치
pip install alembic

# 초기화
alembic init migrations

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 실행
alembic upgrade head
```

## 📋 4. 운영/테스트 분리

### 테스트 환경 설정
```python
# test_config.py
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
```

### pytest 테스트
```bash
# 설치
pip install pytest

# 테스트 실행
pytest tests/
```

### 테스트 예시
```python
# tests/test_auth.py
def test_login_success(client):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 302  # 리다이렉트

def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'wrong'
    })
    assert response.status_code == 200  # 로그인 페이지 유지
```

## 📋 5. 로그 관리

### 로그 설정
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/restaurant.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Restaurant startup')
```

### 로그 로테이션
```bash
# logrotate 설정
/path/to/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    notifempty
    create 644 www-data www-data
}
```

## 📋 6. 보안 설정

### HTTPS 설정
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... 기타 설정
}
```

### 보안 헤더
```python
from flask_talisman import Talisman

Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': "'self' 'unsafe-inline'",
    'style-src': "'self' 'unsafe-inline'"
})
```

## 📋 7. 모니터링

### 헬스체크 엔드포인트
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

### 시스템 모니터링
```bash
# 프로세스 확인
ps aux | grep gunicorn

# 포트 확인
netstat -tlnp | grep 8000

# 로그 확인
tail -f logs/restaurant.log
```

## 📋 8. 자동 배포 스크립트

### deploy.sh
```bash
#!/bin/bash
echo "Deploying Restaurant Management System..."

# 코드 업데이트
git pull origin main

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 서비스 재시작
sudo systemctl restart restaurant-app

echo "Deployment completed!"
```

### systemd 서비스
```ini
# /etc/systemd/system/restaurant-app.service
[Unit]
Description=Restaurant Management System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/restaurant_project
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app_core:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## ✅ 배포 체크리스트

- [ ] 환경 설정 파일 분리
- [ ] Gunicorn 설치 및 설정
- [ ] Nginx 설정
- [ ] 데이터베이스 백업
- [ ] 로그 설정
- [ ] HTTPS 설정
- [ ] 모니터링 설정
- [ ] 자동 배포 스크립트
- [ ] 서비스 등록

## 🚨 주의사항

1. **SECRET_KEY**는 운영환경에서 반드시 변경
2. **DEBUG=False**로 설정
3. **데이터베이스 백업** 정기적으로 수행
4. **로그 모니터링** 지속적으로 확인
5. **보안 업데이트** 정기적으로 적용 