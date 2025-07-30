# 🐘 PostgreSQL 설치 및 설정 가이드

**작성일**: 2025년 1월 28일  
**대상**: Windows 환경  
**목적**: Your Program 프로젝트의 PostgreSQL 데이터베이스 설정

## 📋 목차

1. [PostgreSQL 설치](#postgresql-설치)
2. [데이터베이스 생성](#데이터베이스-생성)
3. [사용자 계정 설정](#사용자-계정-설정)
4. [연결 테스트](#연결-테스트)
5. [마이그레이션 실행](#마이그레이션-실행)

## 🚀 PostgreSQL 설치

### 방법 1: 공식 설치 프로그램 사용

1. **공식 사이트에서 다운로드**
   ```
   https://www.postgresql.org/download/windows/
   ```

2. **설치 실행**
   - PostgreSQL 15 또는 16 버전 권장
   - 설치 중 비밀번호 설정 (기본값: `password`)
   - 포트: 5432 (기본값)
   - 데이터 디렉토리: 기본값 사용

3. **설치 확인**
   ```powershell
   psql --version
   ```

### 방법 2: Chocolatey 사용 (권장)

1. **Chocolatey 설치** (관리자 권한 PowerShell)
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **PostgreSQL 설치**
   ```powershell
   choco install postgresql
   ```

3. **서비스 시작**
   ```powershell
   net start postgresql-x64-15  # 버전에 따라 다를 수 있음
   ```

### 방법 3: Docker 사용 (개발용)

1. **Docker Compose 파일 생성**
   ```yaml
   # docker-compose.dev.yml
   version: '3.8'
   services:
     postgres:
       image: postgres:15
       container_name: your_program_postgres
       environment:
         POSTGRES_DB: your_program_dev
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: password
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
       restart: unless-stopped
   
   volumes:
     postgres_data:
   ```

2. **컨테이너 실행**
   ```powershell
   docker-compose -f docker-compose.dev.yml up -d
   ```

## 🗄️ 데이터베이스 생성

### PowerShell에서 실행

1. **PostgreSQL 접속**
   ```powershell
   psql -U postgres -h localhost
   # 비밀번호 입력: password
   ```

2. **데이터베이스 생성**
   ```sql
   CREATE DATABASE your_program_dev;
   CREATE DATABASE your_program_test;
   CREATE DATABASE your_program_prod;
   ```

3. **데이터베이스 확인**
   ```sql
   \l
   ```

4. **연결 종료**
   ```sql
   \q
   ```

## 👤 사용자 계정 설정

### 개발용 사용자 생성

```sql
-- PostgreSQL에 접속 후 실행
CREATE USER your_program WITH PASSWORD 'your_program_password';
GRANT ALL PRIVILEGES ON DATABASE your_program_dev TO your_program;
GRANT ALL PRIVILEGES ON DATABASE your_program_test TO your_program;

-- 추가 권한 부여
ALTER USER your_program CREATEDB;
ALTER USER your_program SUPERUSER;
```

### 프로덕션용 사용자 생성

```sql
-- 프로덕션용은 더 제한적인 권한
CREATE USER your_program_prod WITH PASSWORD 'secure_production_password';
GRANT ALL PRIVILEGES ON DATABASE your_program_prod TO your_program_prod;
```

## 🔗 연결 테스트

### Python 스크립트로 테스트

```python
# test_db_connection.py
import psycopg2
from psycopg2 import sql
import os

def test_connection():
    try:
        # 연결 설정
        conn = psycopg2.connect(
            host="localhost",
            database="your_program_dev",
            user="postgres",
            password="password",
            port="5432"
        )
        
        # 커서 생성
        cur = conn.cursor()
        
        # 테스트 쿼리
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ PostgreSQL 연결 성공!")
        print(f"버전: {version[0]}")
        
        # 데이터베이스 목록 확인
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cur.fetchall()
        print(f"\n📊 사용 가능한 데이터베이스:")
        for db in databases:
            print(f"  - {db[0]}")
        
        # 연결 종료
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

### 연결 테스트 실행

```powershell
python test_db_connection.py
```

## ⚡ 마이그레이션 실행

### 1. 환경 변수 설정

```powershell
# PowerShell에서 실행
$env:FLASK_ENV = "development"
$env:DATABASE_URL = "postgresql://postgres:password@localhost:5432/your_program_dev"
```

### 2. Flask 앱 초기화

```powershell
# Flask 앱 컨텍스트에서 데이터베이스 초기화
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('데이터베이스 테이블 생성 완료!')"
```

### 3. 마이그레이션 실행

```powershell
# 마이그레이션 초기화 (이미 있다면 건너뛰기)
flask db init

# 현재 모델 상태로 마이그레이션 생성
flask db migrate -m "Initial migration to PostgreSQL"

# 마이그레이션 적용
flask db upgrade
```

### 4. 마이그레이션 확인

```powershell
# 마이그레이션 히스토리 확인
flask db history

# 현재 마이그레이션 상태 확인
flask db current
```

## 🔧 추가 설정

### pg_hba.conf 설정 (필요시)

PostgreSQL 설치 디렉토리의 `data/pg_hba.conf` 파일 수정:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

### postgresql.conf 설정 (성능 최적화)

```conf
# 연결 설정
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# 로깅 설정
log_statement = 'all'  # 개발용
log_min_duration_statement = 1000  # 1초 이상 쿼리 로깅
```

## 🎯 성능 모니터링

### 기본 모니터링 쿼리

```sql
-- 활성 연결 확인
SELECT datname, usename, application_name, state, query_start, query 
FROM pg_stat_activity 
WHERE state = 'active';

-- 데이터베이스 크기 확인
SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database 
WHERE datistemplate = false;

-- 테이블 크기 확인
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🚨 문제 해결

### 일반적인 오류

1. **연결 거부 오류**
   ```
   FATAL: password authentication failed for user
   ```
   **해결**: 비밀번호 확인 또는 pg_hba.conf 설정 변경

2. **데이터베이스 존재하지 않음**
   ```
   FATAL: database "your_program_dev" does not exist
   ```
   **해결**: 데이터베이스 생성 단계 다시 실행

3. **포트 사용 중**
   ```
   could not connect to server: Connection refused
   ```
   **해결**: PostgreSQL 서비스 상태 확인 및 재시작

### 서비스 관리

```powershell
# Windows 서비스 확인
Get-Service -Name "*postgresql*"

# 서비스 시작
Start-Service postgresql-x64-15

# 서비스 중지
Stop-Service postgresql-x64-15

# 서비스 재시작
Restart-Service postgresql-x64-15
```

## ✅ 설정 완료 확인

모든 설정이 완료되면 다음 명령으로 확인:

```powershell
# 1. PostgreSQL 서비스 상태
Get-Service -Name "*postgresql*"

# 2. 데이터베이스 연결 테스트
python test_db_connection.py

# 3. Flask 앱 실행 테스트
python app.py

# 4. 마이그레이션 상태 확인
flask db current
```

---

**📝 참고사항:**
- 개발 환경에서는 보안보다 편의성을 우선으로 설정
- 프로덕션 환경에서는 반드시 강력한 비밀번호 사용
- 정기적인 백업 설정 권장
- 성능 모니터링 도구 설치 권장 (pgAdmin, DBeaver 등)

**🔗 추가 자료:**
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [Flask-SQLAlchemy 문서](https://flask-sqlalchemy.palletsprojects.com/)
- [Alembic 마이그레이션 가이드](https://alembic.sqlalchemy.org/en/latest/)