# 성능 최적화 가이드

이 문서는 Your Program의 성능 최적화에 대한 상세한 가이드를 제공합니다.

## 🚀 성능 최적화 개요

### 성능 목표
- **응답 시간**: 95th percentile < 2초
- **처리량**: 초당 1000+ 요청
- **가용성**: 99.9% 이상
- **에러율**: < 1%
- **캐시 히트율**: > 80%

### 성능 지표
- **CPU 사용률**: < 80%
- **메모리 사용률**: < 85%
- **디스크 I/O**: 최적화
- **네트워크 대역폭**: 효율적 사용

## 🗄️ 데이터베이스 최적화

### 1. 인덱스 최적화

#### 인덱스 생성 전략
```sql
-- 자주 조회되는 컬럼에 인덱스 생성
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 복합 인덱스 생성
CREATE INDEX idx_attendance_user_date ON attendance_records(user_id, date);

-- 부분 인덱스 (조건부 인덱스)
CREATE INDEX idx_active_users ON users(id) WHERE status = 'active';
```

#### 인덱스 사용량 분석
```python
from utils.database_optimizer import get_database_optimizer

db_optimizer = get_database_optimizer()
index_usage = db_optimizer.analyze_index_usage()

# 사용되지 않는 인덱스 확인
unused_indexes = index_usage['unused_indexes']
for index in unused_indexes:
    print(f"사용되지 않는 인덱스: {index['indexname']}")
```

#### 인덱스 제안
```python
# 인덱스 제안 받기
suggestions = db_optimizer.suggest_indexes('users')
for suggestion in suggestions:
    print(f"제안: {suggestion['column']} - {suggestion['reason']}")
```

### 2. 쿼리 최적화

#### 쿼리 성능 분석
```python
# 느린 쿼리 찾기
slow_queries = db_optimizer.find_slow_queries(10)
for query in slow_queries:
    print(f"느린 쿼리: {query['query']}")
    print(f"평균 시간: {query['mean_time']}ms")
```

#### 쿼리 최적화 기법
```python
from utils.api_optimizer import get_query_optimizer

query_optimizer = get_query_optimizer()

# 쿼리 최적화
optimized_query = query_optimizer.optimize_query(query, max_results=1000)

# 페이지네이션
result = query_optimizer.paginate_query(query, page=1, per_page=20)

# 배치 쿼리
results = query_optimizer.batch_query(User, user_ids, batch_size=100)
```

#### 쿼리 튜닝 팁
- **SELECT * 대신 필요한 컬럼만 선택**
- **JOIN 최소화**
- **서브쿼리 대신 JOIN 사용**
- **LIMIT과 OFFSET 적절히 사용**

### 3. 데이터베이스 설정 최적화

#### PostgreSQL 설정
```ini
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

#### 연결 풀 설정
```python
# 데이터베이스 연결 풀 최적화
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600
}
```

## 🗂️ 캐시 최적화

### 1. Redis 캐시 전략

#### 캐시 계층 구조
```
L1: 애플리케이션 캐시 (메모리)
L2: Redis 캐시 (분산)
L3: 데이터베이스 (영구 저장)
```

#### 캐시 사용 패턴
```python
from utils.cache_optimizer import get_cache_manager

cache_manager = get_cache_manager()

# 캐시 데코레이터 사용
@cache_manager.cached(timeout=3600, key_prefix="user_profile")
def get_user_profile(user_id):
    return User.query.get(user_id)

# 수동 캐시 관리
cache_manager.cache_optimizer.set(f"user:{user_id}", user_data, timeout=1800)
user_data = cache_manager.cache_optimizer.get(f"user:{user_id}")
```

#### 캐시 무효화 전략
```python
# 사용자 관련 캐시 무효화
cache_manager.invalidate_user_cache(user_id)

# 브랜드 관련 캐시 무효화
cache_manager.invalidate_brand_cache(brand_id)

# 패턴 기반 무효화
cache_manager.cache_optimizer.invalidate_pattern("user:*:profile")
```

### 2. 캐시 성능 모니터링

#### 캐시 통계 조회
```python
# 캐시 통계
stats = cache_manager.get_cache_stats()
print(f"히트율: {stats['hit_rate']}%")
print(f"총 요청: {stats['total_requests']}")
print(f"캐시 히트: {stats['hits']}")
print(f"캐시 미스: {stats['misses']}")
```

#### 메모리 최적화
```python
# 메모리 최적화 실행
optimization_result = cache_manager.optimize_memory()
print(f"절약된 메모리: {optimization_result['memory_saved']} bytes")
```

### 3. 캐시 설정 최적화

#### Redis 설정
```ini
# redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### 캐시 정책
- **TTL (Time To Live)**: 데이터 특성에 맞는 만료 시간 설정
- **LRU (Least Recently Used)**: 메모리 부족 시 최근 사용하지 않은 데이터 삭제
- **압축**: 큰 데이터는 압축하여 저장

## 🔄 비동기 작업 최적화

### 1. Celery 작업 큐

#### 작업 정의
```python
from utils.async_queue import get_celery_app

celery_app = get_celery_app()

@celery_app.task(bind=True)
def process_large_data(self, data_id):
    """대용량 데이터 처리"""
    try:
        # 데이터 처리 로직
        result = process_data(data_id)
        return result
    except Exception as e:
        self.retry(countdown=60, max_retries=3)
```

#### 작업 스케줄링
```python
from utils.async_queue import get_task_scheduler

scheduler = get_task_scheduler()

# 지연 실행
task_id = scheduler.schedule_task(
    'process_large_data',
    args=[data_id],
    countdown=300  # 5분 후 실행
)

# 주기적 작업
scheduler.schedule_periodic_task(
    'daily_backup',
    crontab(hour=2, minute=0)  # 매일 새벽 2시
)
```

### 2. 작업 모니터링

#### 작업 상태 조회
```python
# 작업 상태 확인
status = scheduler.get_task_status(task_id)
print(f"작업 상태: {status['status']}")

# 활성 작업 목록
active_tasks = scheduler.get_active_tasks()
for task in active_tasks:
    print(f"활성 작업: {task['task_name']}")
```

## ⚖️ 로드 밸런싱 및 확장

### 1. 로드 밸런서 설정

#### 알고리즘 선택
```python
from utils.load_balancer import LoadBalancer, LoadBalancingAlgorithm

# 라운드 로빈
lb = LoadBalancer(LoadBalancingAlgorithm.ROUND_ROBIN)

# 최소 연결
lb = LoadBalancer(LoadBalancingAlgorithm.LEAST_CONNECTIONS)

# 가중 라운드 로빈
lb = LoadBalancer(LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN)
```

#### 서버 관리
```python
# 서버 추가
lb.add_server("server1", "192.168.1.10", 5000, weight=1)
lb.add_server("server2", "192.168.1.11", 5000, weight=2)

# 서버 선택
server = lb.get_server()
print(f"선택된 서버: {server.host}:{server.port}")

# 서버 통계
stats = lb.get_server_stats()
print(f"정상 서버: {stats['healthy_servers']}")
```

### 2. 자동 스케일링

#### 스케일링 조건
```python
# CPU 사용률 기반 스케일링
if avg_cpu > 80:
    scale_up()
elif avg_cpu < 30:
    scale_down()

# 메모리 사용률 기반 스케일링
if avg_memory > 85:
    scale_up()
elif avg_memory < 40:
    scale_down()
```

#### 스케일링 설정
```python
AUTO_SCALING_CONFIG = {
    'min_instances': 2,
    'max_instances': 10,
    'cpu_threshold': 80,
    'memory_threshold': 85,
    'scale_up_cooldown': 300,
    'scale_down_cooldown': 600
}
```

## 📊 성능 모니터링

### 1. 실시간 모니터링

#### 시스템 메트릭 수집
```python
from utils.performance_monitor import get_performance_monitor

monitor = get_performance_monitor()

# 모니터링 시작
monitor.start_monitoring()

# 성능 리포트 생성
report = monitor.get_performance_report(hours=24)
print(f"CPU 평균: {report['cpu']['avg']}%")
print(f"메모리 평균: {report['memory']['avg']}%")
```

#### 임계값 알림
```python
# 알림 콜백 등록
def alert_callback(alert_data):
    print(f"성능 알림: {alert_data['alerts']}")

monitor.alert_callbacks.append(alert_callback)
```

### 2. 성능 분석

#### 병목 지점 분석
```python
from utils.performance_monitor import get_performance_analyzer

analyzer = get_performance_analyzer()

# 병목 지점 찾기
bottlenecks = analyzer.analyze_bottlenecks()
for bottleneck in bottlenecks['bottlenecks']:
    print(f"병목: {bottleneck['description']}")
    print(f"권장사항: {bottleneck['recommendation']}")
```

#### 트렌드 분석
```python
# 성능 트렌드 분석
trends = analyzer.analyze_trends(hours=24)
for trend in trends['trends']:
    print(f"트렌드: {trend['description']}")
```

### 3. 최적화 권장사항

#### 자동 권장사항 생성
```python
# 최적화 권장사항
recommendations = analyzer.generate_optimization_recommendations()
for rec in recommendations:
    print(f"우선순위: {rec['priority']}")
    print(f"카테고리: {rec['category']}")
    print(f"권장사항: {rec['recommendation']}")
```

## 🔧 API 최적화

### 1. 응답 캐싱

#### API 캐싱 전략
```python
from utils.api_optimizer import get_api_optimizer

api_optimizer = get_api_optimizer()

# API 응답 캐싱
@api_optimizer.cache_response(ttl=1800, key_prefix="api")
def get_user_list(page=1, per_page=20):
    return User.query.paginate(page=page, per_page=per_page)
```

#### 캐시 무효화
```python
# API 캐시 무효화
api_optimizer.invalidate_cache("api:get_user_list:*")
```

### 2. 응답 최적화

#### 응답 압축
```python
from utils.api_optimizer import get_response_optimizer

response_optimizer = get_response_optimizer()

# 응답 최적화
data = {"users": user_list, "total": total_count}
response = response_optimizer.optimize_response(data, compress=True)
```

#### 스트리밍 응답
```python
# 대용량 데이터 스트리밍
def generate_large_data():
    for chunk in large_data_generator():
        yield json.dumps(chunk) + '\n'

response = response_optimizer.stream_response(generate_large_data)
```

### 3. API 모니터링

#### 엔드포인트 모니터링
```python
from utils.api_optimizer import get_api_monitor

api_monitor = get_api_monitor()

@api_monitor.monitor_endpoint('/api/users')
def get_users():
    return User.query.all()

# API 통계 조회
stats = api_monitor.get_endpoint_stats('/api/users')
print(f"요청 수: {stats['count']}")
print(f"평균 응답 시간: {stats['avg_time']}ms")
```

## 📈 성능 벤치마크

### 1. 성능 테스트

#### 부하 테스트
```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def load_test(url, num_requests=1000, concurrency=10):
    """부하 테스트"""
    def make_request():
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        return {
            'status_code': response.status_code,
            'response_time': end_time - start_time
        }
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results = [future.result() for future in futures]
    
    # 결과 분석
    response_times = [r['response_time'] for r in results]
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    print(f"평균 응답 시간: {avg_time:.3f}s")
    print(f"최대 응답 시간: {max_time:.3f}s")
    print(f"최소 응답 시간: {min_time:.3f}s")
    print(f"처리량: {num_requests / sum(response_times):.2f} req/s")
```

#### 성능 벤치마크
```python
def benchmark_cache_performance():
    """캐시 성능 벤치마크"""
    cache = CacheOptimizer("redis://localhost:6379/0")
    
    # 쓰기 성능 테스트
    start_time = time.time()
    for i in range(1000):
        cache.set(f"key_{i}", f"value_{i}", timeout=60)
    write_time = time.time() - start_time
    
    # 읽기 성능 테스트
    start_time = time.time()
    for i in range(1000):
        cache.get(f"key_{i}")
    read_time = time.time() - start_time
    
    print(f"캐시 쓰기: {1000/write_time:.2f} ops/s")
    print(f"캐시 읽기: {1000/read_time:.2f} ops/s")
```

### 2. 성능 프로파일링

#### 메모리 프로파일링
```python
import tracemalloc

def profile_memory_usage():
    """메모리 사용량 프로파일링"""
    tracemalloc.start()
    
    # 테스트 코드 실행
    test_function()
    
    # 메모리 사용량 분석
    current, peak = tracemalloc.get_traced_memory()
    print(f"현재 메모리: {current / 1024 / 1024:.2f} MB")
    print(f"최대 메모리: {peak / 1024 / 1024:.2f} MB")
    
    # 상위 메모리 사용자
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    for stat in top_stats[:3]:
        print(stat)
    
    tracemalloc.stop()
```

## 🔍 성능 문제 해결

### 1. 일반적인 성능 문제

#### 느린 응답 시간
```python
# 원인 분석
def analyze_slow_response():
    # 1. 데이터베이스 쿼리 분석
    slow_queries = db_optimizer.find_slow_queries(10)
    
    # 2. 캐시 히트율 확인
    cache_stats = cache_manager.get_cache_stats()
    
    # 3. 시스템 리소스 확인
    system_stats = monitor.get_performance_report(hours=1)
    
    # 4. 네트워크 지연 확인
    network_latency = check_network_latency()
    
    return {
        'slow_queries': slow_queries,
        'cache_hit_rate': cache_stats['hit_rate'],
        'system_resources': system_stats,
        'network_latency': network_latency
    }
```

#### 높은 CPU 사용률
```python
# CPU 사용률 최적화
def optimize_cpu_usage():
    # 1. 불필요한 프로세스 종료
    kill_unnecessary_processes()
    
    # 2. 코드 최적화
    optimize_algorithm()
    
    # 3. 캐시 활용
    increase_cache_usage()
    
    # 4. 비동기 처리
    use_async_processing()
```

#### 메모리 누수
```python
# 메모리 누수 감지
def detect_memory_leak():
    # 1. 메모리 사용량 모니터링
    memory_usage = monitor_memory_usage()
    
    # 2. 객체 참조 확인
    check_object_references()
    
    # 3. 가비지 컬렉션 강제 실행
    import gc
    gc.collect()
    
    # 4. 메모리 프로파일링
    profile_memory_usage()
```

### 2. 성능 최적화 체크리스트

#### 데이터베이스 최적화
- [ ] 인덱스 최적화
- [ ] 쿼리 튜닝
- [ ] 연결 풀 설정
- [ ] 통계 업데이트

#### 캐시 최적화
- [ ] 캐시 전략 수립
- [ ] 캐시 무효화 전략
- [ ] 메모리 최적화
- [ ] 히트율 모니터링

#### API 최적화
- [ ] 응답 캐싱
- [ ] 압축 활성화
- [ ] 페이지네이션
- [ ] 배치 처리

#### 시스템 최적화
- [ ] 로드 밸런싱
- [ ] 자동 스케일링
- [ ] 모니터링 설정
- [ ] 알림 설정

## 📊 성능 지표 대시보드

### 1. 주요 지표

#### 시스템 지표
- CPU 사용률
- 메모리 사용률
- 디스크 I/O
- 네트워크 대역폭

#### 애플리케이션 지표
- 응답 시간
- 처리량
- 에러율
- 활성 연결 수

#### 비즈니스 지표
- 사용자 활동
- 기능별 사용량
- 성능 개선 효과

### 2. 대시보드 구성

#### 실시간 모니터링
```python
# 실시간 대시보드 데이터
def get_realtime_dashboard():
    return {
        'system': {
            'cpu_usage': get_cpu_usage(),
            'memory_usage': get_memory_usage(),
            'disk_usage': get_disk_usage()
        },
        'application': {
            'response_time': get_avg_response_time(),
            'request_rate': get_request_rate(),
            'error_rate': get_error_rate()
        },
        'cache': {
            'hit_rate': get_cache_hit_rate(),
            'memory_usage': get_cache_memory_usage()
        }
    }
```

#### 히스토리 차트
```python
# 히스토리 데이터
def get_history_charts(hours=24):
    return {
        'response_time_trend': get_response_time_history(hours),
        'cpu_usage_trend': get_cpu_usage_history(hours),
        'cache_hit_rate_trend': get_cache_hit_rate_history(hours)
    }
```

## 🎯 성능 최적화 로드맵

### 1단계: 기본 최적화
- [ ] 데이터베이스 인덱스 최적화
- [ ] 기본 캐싱 구현
- [ ] 응답 압축 활성화
- [ ] 기본 모니터링 설정

### 2단계: 고급 최적화
- [ ] 고급 캐싱 전략
- [ ] 비동기 작업 큐
- [ ] 로드 밸런싱
- [ ] 성능 분석 도구

### 3단계: 자동화
- [ ] 자동 스케일링
- [ ] 자동 성능 튜닝
- [ ] 예측 분석
- [ ] 자동 복구

### 4단계: 최적화
- [ ] 마이크로서비스 아키텍처
- [ ] 분산 캐싱
- [ ] 고급 모니터링
- [ ] AI 기반 최적화

이 가이드를 따라 체계적으로 성능을 최적화하여 사용자 경험을 향상시키고 시스템 안정성을 확보할 수 있습니다. 