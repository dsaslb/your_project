# 캐시 관리 시스템

캐시 관리 시스템은 메모리 및 디스크 기반의 고성능 캐싱 솔루션을 제공합니다.

## 주요 기능

- **다중 캐시 타입**: 메모리, 디스크, 하이브리드 캐시 지원
- **TTL 관리**: 자동 만료 및 수명 관리
- **LRU 정책**: Least Recently Used 제거 정책
- **태그 기반 관리**: 태그로 캐시 항목 검색 및 무효화
- **실시간 통계**: 히트율, 크기, 제거 횟수 모니터링
- **자동 정리**: 만료된 항목 자동 제거
- **SQLite 영속성**: 디스크 캐시 데이터 영속성

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# .env 예시
CACHE_DATA_DIR=data/cache
CACHE_MAX_MEMORY_SIZE=104857600  # 100MB
CACHE_MAX_DISK_SIZE=1073741824   # 1GB
CACHE_DEFAULT_TTL=3600           # 1시간
```

### 3. 데이터 디렉토리 생성
```bash
mkdir -p data/cache
```

## 사용법 예시

### 1. 기본 캐시 설정
```python
from cache.cache_manager import CacheManager, CacheConfig, CacheType

config = CacheConfig(
    data_dir="data/cache",
    max_memory_size=100 * 1024 * 1024,  # 100MB
    max_disk_size=1024 * 1024 * 1024,   # 1GB
    default_ttl=3600
)

cache_manager = CacheManager(config)
```

### 2. 캐시 항목 설정
```python
# 메모리 캐시
cache_manager.set("user:123", {"name": "John", "email": "john@example.com"}, 
                  ttl=1800, cache_type=CacheType.MEMORY, 
                  tags=["user", "profile"])

# 디스크 캐시
cache_manager.set("product:456", {"name": "Laptop", "price": 999}, 
                  ttl=7200, cache_type=CacheType.DISK, 
                  tags=["product", "electronics"])

# 하이브리드 캐시
cache_manager.set("config:app", {"theme": "dark", "lang": "ko"}, 
                  ttl=0, cache_type=CacheType.HYBRID, 
                  tags=["config"])
```

### 3. 캐시 항목 조회
```python
# 캐시 조회
user_data = cache_manager.get("user:123")
if user_data:
    print(f"사용자: {user_data['name']}")
else:
    print("캐시 미스")
```

### 4. 태그 기반 관리
```python
# 태그로 검색
user_items = cache_manager.get_by_tags(["user"])
print(f"사용자 관련 캐시: {len(user_items)}개")

# 태그로 무효화
invalidated_count = cache_manager.invalidate_by_tags(["product"])
print(f"제품 캐시 무효화: {invalidated_count}개")
```

## REST API 엔드포인트

- `GET /api/cache/health` : 시스템 상태 확인
- `GET /api/cache/stats` : 캐시 통계 조회
- `POST /api/cache/set` : 캐시 항목 설정
- `GET /api/cache/get/<key>` : 캐시 항목 조회
- `DELETE /api/cache/delete/<key>` : 캐시 항목 삭제
- `POST /api/cache/clear` : 캐시 전체 삭제
- `POST /api/cache/tags` : 태그로 캐시 검색
- `POST /api/cache/invalidate` : 태그로 캐시 무효화
- `GET /api/cache/config` : 설정 조회
- `PUT /api/cache/config` : 설정 업데이트
- `GET /api/cache/keys` : 키 목록 조회

## 캐시 타입

- **memory**: 빠른 메모리 기반 캐시 (기본값)
- **disk**: 영속적인 디스크 기반 캐시
- **hybrid**: 메모리와 디스크 모두에 저장

## 캐시 정책

- **LRU (Least Recently Used)**: 가장 오래 사용되지 않은 항목 제거
- **TTL (Time To Live)**: 설정된 시간 후 자동 만료
- **크기 제한**: 메모리/디스크 크기 초과 시 자동 제거

## 성능 최적화

- **메모리 우선**: 빠른 접근을 위해 메모리 캐시 우선 사용
- **자동 정리**: 백그라운드에서 만료된 항목 정리
- **크기 관리**: 설정된 크기 제한 내에서 자동 관리
- **접근 통계**: 히트율 및 성능 모니터링

## 확장 기능

- **압축**: 대용량 데이터 압축 지원
- **암호화**: 민감한 데이터 암호화
- **분산 캐시**: Redis 연동 (추후 확장)
- **캐시 워밍**: 시스템 시작 시 캐시 미리 로드
- **백업/복구**: 캐시 데이터 백업 및 복구

## 문제 해결

- **메모리 부족**: max_memory_size 조정
- **디스크 부족**: max_disk_size 조정
- **캐시 미스**: TTL 및 정책 재검토
- **성능 저하**: 캐시 타입 및 크기 최적화

## 라이선스
MIT 