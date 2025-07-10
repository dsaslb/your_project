# 🚀 배포 가이드

## 1. 개발 환경

### 로컬 개발
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집

# 데이터베이스 초기화
python app.py

# 샘플 데이터 생성
python -c "from app import app; from utils.sample_data import create_sample_data; app.app_context().push(); create_sample_data()"

# 개발 서버 실행
python app.py
```

## 2. 운영 환경 (Ubuntu + Nginx + Gunicorn)

### 서버 설정
```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 설치
sudo apt install python3 python3-pip python3-venv -y

# Nginx 설치
sudo apt install nginx -y

# 프로젝트 디렉토리 생성
sudo mkdir -p /var/www/your_program_project
sudo chown $USER:$USER /var/www/your_program_project
```

### 애플리케이션 배포
```bash
# 프로젝트 클론
cd /var/www/your_program_project
git clone <your-repo-url> .

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
nano .env  # 운영 환경에 맞게 수정
```

### Gunicorn 설정
```bash
# Gunicorn 서비스 파일 생성
sudo nano /etc/systemd/system/your_program.service
```

```ini
[Unit]
Description=your_program Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/your_program_project
Environment="PATH=/var/www/your_program_project/venv/bin"
ExecStart=/var/www/your_program_project/venv/bin/gunicorn --workers 4 --bind unix:your_program.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 시작
sudo systemctl start your_program
sudo systemctl enable your_program
```

### Nginx 설정
```bash
# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/your_program
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/your_program_project/your_program.sock;
    }

    location /static {
        alias /var/www/your_program_project/static;
    }
}
```

```bash
# Nginx 설정 활성화
sudo ln -s /etc/nginx/sites-available/your_program /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 3. 데이터베이스 설정

### SQLite (개발용)
```bash
# 기본 설정으로 자동 생성됨
python app.py
```

### PostgreSQL (운영용)
```bash
# PostgreSQL 설치
sudo apt install postgresql postgresql-contrib -y

# 데이터베이스 생성
sudo -u postgres psql
CREATE DATABASE your_program_db;
CREATE USER your_program_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_program_db TO your_program_user;
\q

# .env 파일 수정
DATABASE_URL=postgresql://your_program_user:your_password@localhost/your_program_db
```

## 4. 보안 설정

### 방화벽 설정
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### SSL 인증서 (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 환경변수 보안
```bash
# .env 파일 권한 설정
chmod 600 .env

# 데이터베이스 파일 권한 설정
chmod 600 *.db
```

## 5. 모니터링 및 로그

### 로그 확인
```bash
# Gunicorn 로그
sudo journalctl -u your_program

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 애플리케이션 로그
tail -f logs/your_program.log
```

### 백업 스크립트
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/your_program"

mkdir -p $BACKUP_DIR

# 데이터베이스 백업
pg_dump your_program_db > $BACKUP_DIR/db_backup_$DATE.sql

# 애플리케이션 백업
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /var/www/your_program_project

# 30일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## 6. 업데이트 및 유지보수

### 코드 업데이트
```bash
cd /var/www/your_program_project
git pull origin main

# 가상환경 활성화
source venv/bin/activate

# 패키지 업데이트
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (필요시)
# flask db upgrade

# 서비스 재시작
sudo systemctl restart your_program
```

### 정기 점검
```bash
# 디스크 사용량 확인
df -h

# 메모리 사용량 확인
free -h

# 로그 파일 크기 확인
du -sh /var/log/nginx/*
du -sh logs/*

# 데이터베이스 크기 확인
psql -d your_program_db -c "SELECT pg_size_pretty(pg_database_size('your_program_db'));"
```

## 7. 문제 해결

### 일반적인 문제들
1. **권한 오류**: 파일/폴더 권한 확인
2. **포트 충돌**: 포트 사용 중인 프로세스 확인
3. **데이터베이스 연결 오류**: 연결 문자열 및 권한 확인
4. **메모리 부족**: Gunicorn worker 수 조정

### 로그 분석
```bash
# 에러 로그 필터링
sudo journalctl -u your_program | grep ERROR

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log | grep -i error
```

## 8. 성능 최적화

### Gunicorn 설정 최적화
```bash
# workers 수 조정 (CPU 코어 수 * 2 + 1)
gunicorn --workers 4 --bind unix:your_program.sock --timeout 120 app:app

# 메모리 제한
gunicorn --workers 4 --bind unix:your_program.sock --max-requests 1000 --max-requests-jitter 100 app:app
```

### Nginx 최적화
```nginx
# gzip 압축
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# 캐시 설정
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
