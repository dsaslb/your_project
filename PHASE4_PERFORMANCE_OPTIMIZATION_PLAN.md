# Phase 4: 성능 최적화 (2-3주)

## 🎯 목표
- 전체 시스템 성능 70% 개선
- 데이터베이스 쿼리 최적화
- 프론트엔드 로딩 속도 개선
- 캐싱 전략 구현
- 모니터링 시스템 구축

## 📊 성능 지표

### 1. 백엔드 성능 지표
- API 응답 시간: 평균 < 200ms
- 데이터베이스 쿼리 시간: 평균 < 50ms
- 동시 사용자 처리: 1000명 이상
- 메모리 사용량: < 2GB
- CPU 사용률: < 70%

### 2. 프론트엔드 성능 지표
- 페이지 로딩 시간: < 2초
- 번들 크기: < 2MB
- First Contentful Paint: < 1.5초
- Largest Contentful Paint: < 2.5초
- Cumulative Layout Shift: < 0.1

## 🔧 구현 계획

### Week 1: 데이터베이스 최적화
- [ ] 쿼리 최적화 및 인덱스 추가
- [ ] N+1 쿼리 문제 해결
- [ ] 데이터베이스 연결 풀 최적화
- [ ] 쿼리 캐싱 구현

### Week 2: 백엔드 성능 최적화
- [ ] API 응답 캐싱
- [ ] 비동기 처리 구현
- [ ] 메모리 사용량 최적화
- [ ] 로깅 시스템 최적화

### Week 3: 프론트엔드 최적화
- [ ] 번들 크기 최적화
- [ ] 이미지 최적화
- [ ] 코드 스플리팅
- [ ] 지연 로딩 구현

## 📋 상세 구현 내용

### 1. 데이터베이스 최적화

#### 쿼리 최적화
```python
# 최적화 전
def get_user_attendance(user_id):
    user = User.query.get(user_id)
    attendances = Attendance.query.filter_by(user_id=user_id).all()
    return {'user': user, 'attendances': attendances}

# 최적화 후
def get_user_attendance(user_id):
    user = User.query.options(
        db.joinedload(User.attendances)
    ).get(user_id)
    return {'user': user, 'attendances': user.attendances}
```

#### 인덱스 추가
```python
# 복합 인덱스 추가
class Attendance(db.Model):
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'clock_in'),
        db.Index('idx_status_date', 'status', 'created_at'),
        db.Index('idx_branch_user', 'branch_id', 'user_id'),
    )
```

#### 쿼리 캐싱
```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key, query_func, ttl=3600):
    """캐시된 데이터 조회"""
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    data = query_func()
    redis_client.setex(key, ttl, json.dumps(data))
    return data

@lru_cache(maxsize=128)
def get_user_permissions(user_id):
    """사용자 권한 캐싱"""
    return User.query.get(user_id).permissions
```

### 2. 백엔드 성능 최적화

#### API 응답 캐싱
```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@app.route('/api/dashboard/stats')
@cache.cached(timeout=300)  # 5분 캐시
def get_dashboard_stats():
    """대시보드 통계 캐싱"""
    return {
        'total_users': User.query.count(),
        'active_orders': Order.query.filter_by(status='active').count(),
        'today_attendance': Attendance.query.filter(
            Attendance.clock_in >= today
        ).count()
    }
```

#### 비동기 처리
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/1')

@celery.task
def send_bulk_notifications(user_ids, message):
    """대량 알림 발송 (비동기)"""
    for user_id in user_ids:
        send_notification(user_id, message)

@celery.task
def generate_report_pdf(report_data):
    """PDF 보고서 생성 (비동기)"""
    # PDF 생성 로직
    return pdf_url
```

#### 메모리 최적화
```python
# 제너레이터 사용으로 메모리 절약
def get_large_dataset():
    """대용량 데이터 조회 (제너레이터)"""
    query = User.query.yield_per(100)
    for user in query:
        yield user.to_dict()

# 컨텍스트 매니저 사용
def process_data_with_context():
    """컨텍스트 매니저로 메모리 관리"""
    with app.app_context():
        data = process_large_dataset()
        return data
```

### 3. 프론트엔드 최적화

#### 번들 최적화
```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
        },
      },
    },
  },
  plugins: [
    new BundleAnalyzerPlugin(),
    new CompressionPlugin(),
  ],
};
```

#### 동적 임포트
```typescript
// 코드 스플리팅
const AdminDashboard = lazy(() => import('./AdminDashboard'));
const ManagerDashboard = lazy(() => import('./ManagerDashboard'));
const EmployeeDashboard = lazy(() => import('./EmployeeDashboard'));

// 권한별 컴포넌트 로딩
const Dashboard = () => {
  const { user } = useAuth();
  
  return (
    <Suspense fallback={<LoadingSpinner />}>
      {user.role === 'admin' && <AdminDashboard />}
      {user.role === 'manager' && <ManagerDashboard />}
      {user.role === 'employee' && <EmployeeDashboard />}
    </Suspense>
  );
};
```

#### 이미지 최적화
```typescript
// Next.js Image 컴포넌트 사용
import Image from 'next/image';

const OptimizedImage = ({ src, alt, width, height }) => (
  <Image
    src={src}
    alt={alt}
    width={width}
    height={height}
    placeholder="blur"
    blurDataURL="data:image/jpeg;base64,..."
    loading="lazy"
  />
);

// WebP 포맷 사용
const getOptimizedImageUrl = (url: string, format: 'webp' | 'avif' = 'webp') => {
  return url.replace(/\.(jpg|jpeg|png)$/, `.${format}`);
};
```

### 4. 캐싱 전략

#### Redis 캐싱
```python
# Redis 캐싱 설정
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'restaurant_',
}

# 캐시 데코레이터
def cache_response(timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = f(*args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return decorated_function
    return decorator
```

#### 브라우저 캐싱
```typescript
// Service Worker 캐싱
const CACHE_NAME = 'restaurant-cache-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
```

### 5. 모니터링 시스템

#### 성능 모니터링
```python
import time
from functools import wraps

def monitor_performance(func_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 성능 로깅
            if execution_time > 1.0:  # 1초 이상 걸리는 요청
                logger.warning(f"Slow query: {func_name} took {execution_time:.2f}s")
            
            # 메트릭 수집
            record_metric(func_name, execution_time)
            return result
        return decorated_function
    return decorator
```

#### 실시간 모니터링
```python
# Prometheus 메트릭
from prometheus_client import Counter, Histogram, Gauge

# 요청 수 카운터
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])

# 응답 시간 히스토그램
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# 활성 사용자 수 게이지
ACTIVE_USERS = Gauge('active_users', 'Number of active users')

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    REQUEST_DURATION.observe(duration)
    return response
```

## 📊 성능 테스트

### 1. 부하 테스트
```python
# Locust 부하 테스트
from locust import HttpUser, task, between

class RestaurantUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def view_dashboard(self):
        self.client.get("/dashboard")
    
    @task
    def view_attendance(self):
        self.client.get("/attendance")
    
    @task
    def create_order(self):
        self.client.post("/api/orders", json={
            "item": "Test Item",
            "quantity": 1
        })
```

### 2. 성능 프로파일링
```python
# cProfile 사용
import cProfile
import pstats

def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 상위 10개 함수
    
    return result
```

## 🎯 성공 기준

### 1. 성능 지표
- [ ] API 응답 시간 70% 개선
- [ ] 페이지 로딩 시간 60% 개선
- [ ] 데이터베이스 쿼리 시간 50% 개선
- [ ] 메모리 사용량 30% 감소

### 2. 사용자 경험
- [ ] 사용자 만족도 90% 이상
- [ ] 시스템 안정성 99.9% 이상
- [ ] 오류율 0.1% 미만
- [ ] 동시 사용자 1000명 이상 지원

### 3. 운영 효율성
- [ ] 모니터링 시스템 완성
- [ ] 자동 알림 시스템 구축
- [ ] 성능 대시보드 제공
- [ ] 트러블슈팅 가이드 작성 