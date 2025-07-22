# 성능 최적화 가이드

이 문서는 멀티테넌시 관리 시스템의 성능 최적화 방법과 모니터링 시스템 사용법을 설명합니다.

## 📊 성능 모니터링 시스템

### 시스템 모니터링
- **CPU 사용률**: 실시간 CPU 사용량 모니터링
- **메모리 사용률**: 메모리 사용량 및 가용 메모리 추적
- **디스크 사용률**: 디스크 공간 및 I/O 성능 모니터링
- **네트워크**: 네트워크 트래픽 및 연결 수 추적
- **로드 평균**: 시스템 부하 평균값

### 애플리케이션 모니터링
- **요청/분**: 분당 처리되는 요청 수
- **에러율**: HTTP 에러 응답 비율
- **평균 응답시간**: API 응답 시간 평균
- **활성 엔드포인트**: 현재 활성화된 API 엔드포인트 수

### 프론트엔드 모니터링
- **메모리 사용량**: 브라우저 메모리 사용량
- **렌더링 성능**: 컴포넌트 렌더링 시간
- **캐시 효율성**: 캐시 히트율 및 크기
- **번들 크기**: JavaScript 번들 크기

## 🔧 백엔드 성능 최적화

### 1. 데이터베이스 최적화

#### 인덱스 최적화
```sql
-- 자주 사용되는 쿼리에 인덱스 추가
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_date ON orders(created_at);
CREATE INDEX idx_brand_status ON brands(status);

-- 복합 인덱스
CREATE INDEX idx_user_brand_role ON users(brand_id, role);
```

#### 쿼리 최적화
```python
# N+1 문제 해결
# 비효율적
users = User.query.all()
for user in users:
    print(user.brand.name)  # 각 사용자마다 추가 쿼리

# 효율적
users = User.query.options(joinedload('brand')).all()
for user in users:
    print(user.brand.name)  # 단일 쿼리로 모든 데이터 로드
```

#### 연결 풀 최적화
```python
# 데이터베이스 연결 풀 설정
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # 기본 연결 풀 크기
    max_overflow=30,        # 최대 오버플로우
    pool_pre_ping=True,     # 연결 상태 확인
    pool_recycle=3600       # 1시간마다 연결 재생성
)
```

### 2. 캐싱 전략

#### Redis 캐싱
```python
from utils.performance_optimizer import performance_optimizer

@performance_optimizer.cache_result("user_profile", ttl=300)
def get_user_profile(user_id: int):
    # 비용이 큰 데이터베이스 쿼리
    return User.query.get(user_id)

# 캐시 무효화
performance_optimizer.clear_cache("user_profile")
```

#### 메모리 캐싱
```python
# 자주 사용되는 데이터 메모리 캐싱
class ConfigCache:
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._ttl = 300  # 5분

    def get(self, key):
        if key in self._cache:
            if time.time() - self._cache_time[key] < self._ttl:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._cache_time[key]
        return None

    def set(self, key, value):
        self._cache[key] = value
        self._cache_time[key] = time.time()
```

### 3. 비동기 처리

#### Celery 작업 큐
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def process_large_file(file_path):
    # 시간이 오래 걸리는 작업
    time.sleep(10)
    return "처리 완료"

# 비동기 실행
result = process_large_file.delay("large_file.csv")
```

#### 백그라운드 작업
```python
import threading

def background_task():
    # 백그라운드에서 실행할 작업
    pass

thread = threading.Thread(target=background_task, daemon=True)
thread.start()
```

### 4. 메모리 최적화

#### 메모리 사용량 모니터링
```python
import psutil

def monitor_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"메모리 사용량: {memory_info.rss / 1024 / 1024:.2f} MB")

# 정기적 모니터링
import schedule
schedule.every(5).minutes.do(monitor_memory)
```

#### 가비지 컬렉션 최적화
```python
import gc

# 수동 가비지 컬렉션
gc.collect()

# 메모리 누수 방지
def cleanup_resources():
    # 리소스 정리
    pass

# 정기적 정리
schedule.every(10).minutes.do(cleanup_resources)
```

## 🎨 프론트엔드 성능 최적화

### 1. React 컴포넌트 최적화

#### 메모이제이션
```tsx
import React, { memo, useMemo, useCallback } from 'react';

// 컴포넌트 메모이제이션
const ExpensiveComponent = memo(({ data }) => {
  return <div>{data.map(item => <span key={item.id}>{item.name}</span>)}</div>;
});

// 계산 결과 메모이제이션
const MyComponent = ({ items }) => {
  const expensiveValue = useMemo(() => {
    return items.reduce((sum, item) => sum + item.value, 0);
  }, [items]);

  const handleClick = useCallback((id) => {
    console.log('Clicked:', id);
  }, []);

  return (
    <div>
      <p>Total: {expensiveValue}</p>
      <button onClick={() => handleClick(1)}>Click</button>
    </div>
  );
};
```

#### 코드 스플리팅
```tsx
import React, { lazy, Suspense } from 'react';

// 지연 로딩
const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );
}
```

### 2. 번들 최적화

#### Webpack 설정
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
      },
    },
  },
  performance: {
    hints: 'warning',
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
  },
};
```

#### Tree Shaking
```javascript
// ES6 모듈 사용으로 Tree Shaking 활성화
import { only, what, you, need } from 'large-library';

// 전체 라이브러리 import 방지
// import * as library from 'large-library'; // 비효율적
```

### 3. 이미지 최적화

#### 지연 로딩
```tsx
import { useLazyImage } from '../utils/performance';

const OptimizedImage = ({ src, alt }) => {
  const { imageSrc, isLoaded } = useLazyImage(src, '/placeholder.jpg');
  
  return (
    <img 
      src={imageSrc} 
      alt={alt}
      className={isLoaded ? 'loaded' : 'loading'}
    />
  );
};
```

#### 이미지 압축
```javascript
// WebP 포맷 사용
const OptimizedImage = ({ src, alt }) => {
  const webpSrc = src.replace(/\.(jpg|jpeg|png)$/, '.webp');
  
  return (
    <picture>
      <source srcSet={webpSrc} type="image/webp" />
      <img src={src} alt={alt} />
    </picture>
  );
};
```

### 4. 네트워크 최적화

#### HTTP/2 활용
```javascript
// 서버 설정 (nginx)
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # HTTP/2 푸시
    location / {
        http2_push /css/main.css;
        http2_push /js/main.js;
    }
}
```

#### CDN 활용
```javascript
// 정적 파일 CDN 사용
const CDN_BASE = 'https://cdn.example.com';

const StaticAsset = ({ path }) => {
  return <img src={`${CDN_BASE}${path}`} />;
};
```

## 📈 성능 모니터링 및 알림

### 1. 모니터링 대시보드

#### 성능 대시보드 사용
```tsx
import { PerformanceDashboard } from './components/PerformanceDashboard';

function AdminPage() {
  return (
    <div>
      <h1>관리자 대시보드</h1>
      <PerformanceDashboard title="시스템 성능 모니터링" />
    </div>
  );
}
```

#### 실시간 메트릭 조회
```typescript
// API를 통한 메트릭 조회
const fetchMetrics = async () => {
  const [systemRes, appRes] = await Promise.all([
    fetch('/api/monitoring/system-metrics'),
    fetch('/api/monitoring/application-metrics')
  ]);
  
  const systemMetrics = await systemRes.json();
  const appMetrics = await appRes.json();
  
  return { system: systemMetrics.data, application: appMetrics.data };
};
```

### 2. 성능 알림 설정

#### 알림 임계값 설정
```python
# 백엔드 알림 설정
alert_thresholds = {
    'cpu_percent': 80.0,        # CPU 80% 이상
    'memory_percent': 85.0,     # 메모리 85% 이상
    'disk_usage_percent': 90.0, # 디스크 90% 이상
    'error_rate': 0.05,         # 에러율 5% 이상
    'avg_response_time': 2.0    # 평균 응답시간 2초 이상
}
```

#### 알림 전송
```python
def send_alert(alert_type, message, severity='warning'):
    """알림 전송"""
    if severity == 'critical':
        # Slack, 이메일 등으로 즉시 알림
        send_slack_alert(f"🚨 {alert_type}: {message}")
        send_email_alert(f"Critical Alert: {alert_type}", message)
    elif severity == 'warning':
        # Slack으로 알림
        send_slack_alert(f"⚠️ {alert_type}: {message}")
```

### 3. 성능 리포트 생성

#### 자동 리포트 생성
```python
def generate_daily_report():
    """일일 성능 리포트 생성"""
    system_report = system_monitor.get_performance_report()
    app_report = application_monitor.get_performance_report()
    
    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'system': system_report,
        'application': app_report,
        'recommendations': generate_recommendations(system_report, app_report)
    }
    
    # 리포트 저장 및 전송
    save_report(report)
    send_daily_report(report)
```

## 🚀 성능 튜닝 체크리스트

### 백엔드 튜닝
- [ ] 데이터베이스 인덱스 최적화
- [ ] 쿼리 성능 분석 및 개선
- [ ] 캐싱 전략 구현
- [ ] 비동기 처리 도입
- [ ] 메모리 사용량 최적화
- [ ] 연결 풀 설정 조정
- [ ] 로드 밸런싱 구성

### 프론트엔드 튜닝
- [ ] 컴포넌트 메모이제이션 적용
- [ ] 코드 스플리팅 구현
- [ ] 이미지 최적화
- [ ] 번들 크기 최소화
- [ ] HTTP/2 활용
- [ ] CDN 구성
- [ ] 지연 로딩 구현

### 모니터링 설정
- [ ] 성능 메트릭 수집 설정
- [ ] 알림 임계값 설정
- [ ] 대시보드 구성
- [ ] 자동 리포트 설정
- [ ] 로그 분석 도구 구성

## 📊 성능 벤치마크

### 목표 성능 지표
- **페이지 로드 시간**: < 2초
- **API 응답 시간**: < 500ms
- **데이터베이스 쿼리**: < 100ms
- **메모리 사용량**: < 1GB
- **CPU 사용률**: < 70%
- **에러율**: < 1%

### 성능 테스트
```bash
# 부하 테스트
ab -n 1000 -c 10 http://localhost:5000/api/health

# 메모리 프로파일링
python -m memory_profiler app.py

# 성능 프로파일링
python -m cProfile -o profile.stats app.py
```

## 🔍 성능 문제 해결

### 일반적인 성능 문제

#### 느린 데이터베이스 쿼리
```sql
-- 느린 쿼리 분석
EXPLAIN ANALYZE SELECT * FROM users WHERE email LIKE '%@example.com';

-- 인덱스 추가
CREATE INDEX idx_users_email ON users(email);
```

#### 메모리 누수
```python
# 메모리 프로파일링
import tracemalloc

tracemalloc.start()
# 코드 실행
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
print("[ Top 10 ]")
for stat in top_stats[:10]:
    print(stat)
```

#### 높은 CPU 사용률
```python
# CPU 프로파일링
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# 코드 실행
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

이 가이드를 따라 시스템의 성능을 최적화하고 지속적으로 모니터링하여 안정적인 서비스를 제공할 수 있습니다. 