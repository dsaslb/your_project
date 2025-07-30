# 🚀 Redis 설치 및 설정 가이드

**작성일**: 2025년 1월 28일  
**대상**: Windows 환경  
**목적**: Your Program 프로젝트의 Redis 캐시 서버 설정

## 📋 목차

1. [Redis 설치](#redis-설치)
2. [서비스 시작](#서비스-시작)
3. [연결 테스트](#연결-테스트)
4. [Flask 앱 연동](#flask-앱-연동)
5. [성능 최적화](#성능-최적화)

## 🚀 Redis 설치

### 방법 1: 프로젝트 포함 설치 파일 사용 (권장)

1. **설치 파일 실행**
   ```powershell
   # 프로젝트 내 설치 파일 실행
   Start-Process -FilePath "C:\your_program\redis-server\Redis-x64-3.0.504.msi" -Wait
   ```

2. **설치 옵션 선택**
   - 모든 기본 옵션 사용
   - 서비스로 설치 선택
   - 방화벽 예외 허용

### 방법 2: Chocolatey 사용

1. **Redis 설치**
   ```powershell
   choco install redis-64
   ```

2. **서비스 시작**
   ```powershell
   redis-server --service-start
   ```

### 방법 3: 수동 다운로드

1. **Redis 다운로드**
   ```
   https://github.com/microsoftarchive/redis/releases
   ```

2. **압축 해제 후 설치**
   ```powershell
   # 압축을 C:\Redis에 해제
   # 시스템 환경변수 PATH에 C:\Redis 추가
   ```

## ⚡ 서비스 시작

### Windows 서비스로 시작

```powershell
# 서비스 상태 확인
Get-Service -Name "*Redis*"

# Redis 서비스 시작
Start-Service Redis

# 자동 시작으로 설정
Set-Service -Name Redis -StartupType Automatic
```

### 수동 시작 (개발용)

```powershell
# 기본 포트(6379)로 시작
redis-server

# 설정 파일과 함께 시작
redis-server C:\Redis\redis.windows.conf

# 백그라운드로 시작
Start-Process redis-server -WindowStyle Hidden
```

## 🔗 연결 테스트

### Redis CLI 테스트

```powershell
# Redis CLI 연결
redis-cli

# 연결 테스트
127.0.0.1:6379> ping
PONG

# 기본 작업 테스트
127.0.0.1:6379> set test_key "Hello Redis"
OK
127.0.0.1:6379> get test_key
"Hello Redis"

# 종료
127.0.0.1:6379> exit
```

### Python으로 연결 테스트

```python
# test_redis_connection.py
import redis
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('config/development.env')

def test_redis_connection():
    try:
        # Redis 연결 설정
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        # Redis 클라이언트 생성
        r = redis.from_url(redis_url)
        
        # 연결 테스트
        r.ping()
        print("✅ Redis 연결 성공!")
        
        # 기본 작업 테스트
        r.set('test_key', 'Hello from Python!')
        value = r.get('test_key')
        print(f"📊 테스트 값: {value.decode('utf-8')}")
        
        # 서버 정보 확인
        info = r.info()
        print(f"🔍 Redis 버전: {info['redis_version']}")
        print(f"💾 사용 메모리: {info['used_memory_human']}")
        print(f"🔗 연결된 클라이언트: {info['connected_clients']}")
        
        # 정리
        r.delete('test_key')
        
        return True
        
    except redis.ConnectionError:
        print("❌ Redis 서버에 연결할 수 없습니다.")
        print("💡 Redis 서버가 실행 중인지 확인해주세요.")
        return False
        
    except Exception as e:
        print(f"❌ Redis 연결 오류: {e}")
        return False

if __name__ == "__main__":
    test_redis_connection()
```

## 🔧 Flask 앱 연동

### 캐시 설정 업데이트

이미 `config/development.env`에 Redis 설정이 포함되어 있습니다:

```bash
# Redis 설정 (로컬 Redis)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# 캐시 설정
CACHE_TYPE=simple  # Redis 설치 후 'redis'로 변경
```

### Redis 사용 설정

1. **환경 변수 업데이트**
   ```bash
   # config/development.env 파일에서
   CACHE_TYPE=redis
   CACHE_REDIS_URL=redis://localhost:6379/1
   ```

2. **Flask-Caching 확인**
   ```python
   # requirements.txt에 이미 포함됨
   Flask-Caching==2.1.0
   ```

### 세션 저장소 설정

```python
# config/config.py에 추가 가능
class Config:
    # 기존 설정...
    
    # Redis 세션 설정
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/2'))
    SESSION_KEY_PREFIX = 'your_program_session:'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
```

## 📊 성능 최적화

### Redis 설정 파일 (redis.windows.conf)

```conf
# 메모리 설정
maxmemory 256mb
maxmemory-policy allkeys-lru

# 네트워크 설정
bind 127.0.0.1
port 6379
timeout 300

# 백업 설정
save 900 1
save 300 10
save 60 10000

# 로깅 설정
loglevel notice
logfile "redis-server.log"

# 보안 설정 (프로덕션용)
# requirepass your_strong_password

# 성능 최적화
tcp-keepalive 300
tcp-backlog 511
```

### 연결 풀 설정

```python
# utils/redis_client.py
import redis
import os
from redis.connection import ConnectionPool

# 연결 풀 생성
redis_pool = ConnectionPool.from_url(
    os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    max_connections=20,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)

# Redis 클라이언트
redis_client = redis.Redis(connection_pool=redis_pool)

def get_redis_client():
    """Redis 클라이언트 반환"""
    return redis_client

def test_redis_health():
    """Redis 상태 확인"""
    try:
        redis_client.ping()
        return True
    except:
        return False
```

## 🔍 모니터링 및 관리

### Redis 상태 모니터링

```python
# monitoring/redis_monitor.py
import redis
import psutil
import time

def get_redis_stats():
    """Redis 통계 정보 수집"""
    try:
        r = redis.Redis()
        info = r.info()
        
        stats = {
            'server': {
                'version': info['redis_version'],
                'uptime': info['uptime_in_seconds'],
                'tcp_port': info['tcp_port']
            },
            'memory': {
                'used_memory': info['used_memory'],
                'used_memory_human': info['used_memory_human'],
                'used_memory_peak': info['used_memory_peak'],
                'used_memory_peak_human': info['used_memory_peak_human']
            },
            'clients': {
                'connected_clients': info['connected_clients'],
                'client_recent_max_input_buffer': info.get('client_recent_max_input_buffer', 0),
                'client_recent_max_output_buffer': info.get('client_recent_max_output_buffer', 0)
            },
            'stats': {
                'total_connections_received': info['total_connections_received'],
                'total_commands_processed': info['total_commands_processed'],
                'instantaneous_ops_per_sec': info['instantaneous_ops_per_sec'],
                'keyspace_hits': info['keyspace_hits'],
                'keyspace_misses': info['keyspace_misses']
            }
        }
        
        return stats
        
    except Exception as e:
        return {'error': str(e)}

def monitor_redis(duration=60):
    """Redis 성능 모니터링"""
    print("🔍 Redis 모니터링 시작...")
    
    for i in range(duration):
        stats = get_redis_stats()
        
        if 'error' not in stats:
            print(f"[{i+1:02d}] "
                  f"메모리: {stats['memory']['used_memory_human']} | "
                  f"클라이언트: {stats['clients']['connected_clients']} | "
                  f"OPS: {stats['stats']['instantaneous_ops_per_sec']}")
        else:
            print(f"[{i+1:02d}] ❌ Redis 연결 오류: {stats['error']}")
        
        time.sleep(1)

if __name__ == "__main__":
    monitor_redis()
```

### Redis 관리 명령어

```powershell
# 메모리 사용량 확인
redis-cli info memory

# 연결된 클라이언트 확인
redis-cli client list

# 키 개수 확인
redis-cli dbsize

# 특정 패턴 키 검색
redis-cli keys "your_program:*"

# 메모리 최적화
redis-cli memory purge

# 백업 생성
redis-cli bgsave

# 로그 확인 (Windows)
Get-Content "C:\Program Files\Redis\Logs\redis-server.log" -Tail 50
```

## 🚨 문제 해결

### 일반적인 오류

1. **연결 거부 오류**
   ```
   ConnectionError: Error 10061 connecting to localhost:6379. 
   Connection refused.
   ```
   **해결**: Redis 서비스 시작 확인

2. **메모리 부족 오류**
   ```
   OOM command not allowed when used memory > 'maxmemory'
   ```
   **해결**: `maxmemory` 설정 증가 또는 `maxmemory-policy` 변경

3. **포트 사용 중 오류**
   ```powershell
   # 포트 사용 확인
   netstat -an | findstr :6379
   
   # 포트 사용 프로세스 확인
   Get-Process -Id (Get-NetTCPConnection -LocalPort 6379).OwningProcess
   ```

### 성능 튜닝

```conf
# redis.conf 성능 최적화 설정
tcp-nodelay yes
tcp-keepalive 300
timeout 300

# 백그라운드 저장 최적화
stop-writes-on-bgsave-error no
rdbcompression yes
rdbchecksum yes

# AOF 설정 (필요시)
appendonly no
appendfsync everysec
```

## ✅ 설정 완료 확인

모든 설정이 완료되면 다음 명령으로 확인:

```powershell
# 1. Redis 서비스 상태
Get-Service -Name "*Redis*"

# 2. Redis 연결 테스트
redis-cli ping

# 3. Python에서 연결 테스트
python test_redis_connection.py

# 4. Flask 앱에서 캐시 테스트
python -c "from app import app, cache; app.app_context().push(); cache.set('test', 'success'); print('✅ 캐시 테스트:', cache.get('test'))"
```

## 🎯 다음 단계

Redis 설치 완료 후:

1. **환경 변수 업데이트**
   ```bash
   # config/development.env
   CACHE_TYPE=redis
   ```

2. **Flask 앱 재시작**
   ```powershell
   python app.py
   ```

3. **성능 모니터링 시작**
   ```powershell
   python monitoring/redis_monitor.py
   ```

---

**📝 참고사항:**
- 개발 환경에서는 기본 설정으로 충분
- 프로덕션 환경에서는 보안 설정 필수
- 정기적인 백업 및 모니터링 권장
- 메모리 사용량 주기적 확인

**🔗 추가 자료:**
- [Redis 공식 문서](https://redis.io/documentation)
- [Flask-Caching 문서](https://flask-caching.readthedocs.io/)
- [Redis Windows 가이드](https://redis.io/docs/getting-started/installation/install-redis-on-windows/)