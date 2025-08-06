# 📊 데이터 분석 시스템

퀀텀 비즈니스 관리 시스템의 고급 데이터 분석 및 비즈니스 인텔리전스 모듈입니다. 머신러닝, 예측 분석, 실시간 모니터링 등의 기능을 제공합니다.

## 주요 기능

### 🔍 고급 분석 도구
- **트렌드 분석**: 시계열 데이터의 트렌드와 패턴 분석
- **상관관계 분석**: 변수 간의 상관관계 및 인과관계 분석
- **클러스터링**: 고객 세그먼트 및 데이터 그룹화
- **이상 탐지**: 비정상적인 패턴 및 이상값 탐지

### 🤖 머신러닝 통합
- **예측 모델**: 매출, 재고, 고객 행동 예측
- **회귀 분석**: 선형 회귀, 랜덤 포레스트 등
- **분류 모델**: 고객 세그먼트 분류
- **모델 성능 평가**: 정확도, 신뢰도 측정

### ⚡ 실시간 분석
- **실시간 메트릭**: 시스템 성능 실시간 모니터링
- **실시간 대시보드**: 실시간 데이터 시각화
- **알림 시스템**: 임계값 기반 알림
- **성능 모니터링**: 시스템 성능 추적

### 💡 인사이트 생성
- **자동 인사이트**: 데이터 기반 자동 인사이트 생성
- **권장사항**: 비즈니스 개선 권장사항 제공
- **신뢰도 평가**: 인사이트의 신뢰도 측정
- **영향도 분석**: 비즈니스 영향도 평가

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r analytics/requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
ANALYTICS_DATA_DIR=data/analytics
ANALYTICS_MODEL_DIR=models
ANALYTICS_CACHE_DIR=cache
ANALYTICS_MAX_CACHE_SIZE=1000
ANALYTICS_PREDICTION_HORIZON=30
ANALYTICS_UPDATE_FREQUENCY=3600
ANALYTICS_ENABLE_ML=true
ANALYTICS_ENABLE_REALTIME=true
```

### 3. 분석 시스템 초기화
```python
from analytics.analytics_manager import AnalyticsManager, AnalyticsConfig

# 분석 설정
config = AnalyticsConfig(
    data_dir="data/analytics",
    model_dir="models",
    cache_dir="cache",
    max_cache_size=1000,
    prediction_horizon=30,
    update_frequency=3600,
    enable_ml=True,
    enable_realtime=True
)

# 분석 관리자 초기화
analytics_manager = AnalyticsManager(config)
```

## API 엔드포인트

### 시스템 상태
- `GET /api/analytics/health` - 분석 시스템 상태 확인
- `GET /api/analytics/summary` - 분석 요약 정보 조회

### 분석 도구
- `POST /api/analytics/trends` - 트렌드 분석
- `POST /api/analytics/correlations` - 상관관계 분석
- `POST /api/analytics/clustering` - 클러스터링 분석
- `POST /api/analytics/anomalies` - 이상 탐지

### 예측 모델
- `POST /api/analytics/predictions/sales` - 매출 예측
- `GET /api/analytics/models` - 예측 모델 조회
- `POST /api/analytics/models` - 예측 모델 생성

### 인사이트
- `GET /api/analytics/insights` - 인사이트 조회
- `POST /api/analytics/insights/generate` - 인사이트 자동 생성

### 실시간 모니터링
- `GET /api/analytics/realtime` - 실시간 메트릭 조회
- `POST /api/analytics/realtime/update` - 실시간 메트릭 업데이트

### 분석 결과
- `GET /api/analytics/analyses` - 분석 결과 조회
- `GET /api/analytics/analyses/{analysis_id}` - 특정 분석 결과 조회

## 사용 예시

### 트렌드 분석
```javascript
const response = await fetch('/api/analytics/trends', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    data_source: 'sales',
    metric: 'daily_sales',
    time_period: '30d'
  })
});

const result = await response.json();
if (result.status === 'success') {
  const { trend_direction, trend_strength } = result.data.results;
  console.log(`트렌드 방향: ${trend_direction}, 강도: ${trend_strength}`);
}
```

### 매출 예측
```javascript
const response = await fetch('/api/analytics/predictions/sales', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    days_ahead: 30
  })
});

const result = await response.json();
if (result.status === 'success') {
  const { predictions, total_predicted_sales, model_accuracy } = result.data;
  console.log(`총 예측 매출: ${total_predicted_sales}원`);
  console.log(`모델 정확도: ${(model_accuracy * 100).toFixed(1)}%`);
}
```

### 상관관계 분석
```javascript
const response = await fetch('/api/analytics/correlations', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    data_source: 'business_data',
    variables: ['sales', 'advertising', 'price', 'customer_satisfaction']
  })
});

const result = await response.json();
if (result.status === 'success') {
  const { strong_correlations } = result.data.results;
  console.log(`강한 상관관계: ${strong_correlations.length}개`);
}
```

### 클러스터링 분석
```javascript
const response = await fetch('/api/analytics/clustering', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    data_source: 'customer_data',
    features: ['purchase_frequency', 'avg_order_value', 'customer_lifetime'],
    n_clusters: 3
  })
});

const result = await response.json();
if (result.status === 'success') {
  const { n_clusters, cluster_characteristics } = result.data.results;
  console.log(`클러스터 수: ${n_clusters}`);
}
```

### 인사이트 생성
```javascript
const response = await fetch('/api/analytics/insights/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  }
});

const result = await response.json();
if (result.status === 'success') {
  const insights = result.data;
  console.log(`${insights.length}개의 인사이트가 생성되었습니다`);
}
```

## 분석 기능 상세

### 트렌드 분석
- **시계열 분석**: 시간에 따른 데이터 변화 패턴 분석
- **트렌드 방향**: 상승/하락/안정 트렌드 판별
- **트렌드 강도**: 변화의 크기와 속도 측정
- **계절성 분석**: 주간, 월간, 연간 패턴 탐지

### 예측 모델
- **매출 예측**: 과거 매출 데이터 기반 미래 매출 예측
- **재고 예측**: 수요 예측을 통한 최적 재고 수준 계산
- **고객 행동 예측**: 고객의 구매 패턴 및 이탈 예측
- **모델 성능**: 정확도, 신뢰도, 오차율 측정

### 클러스터링
- **고객 세그먼트**: 구매 행동 기반 고객 그룹화
- **제품 그룹**: 판매 패턴 기반 제품 분류
- **시장 세분화**: 지역, 연령, 소득 등 기반 시장 분할
- **세그먼트 특성**: 각 그룹의 특성 및 행동 패턴 분석

### 이상 탐지
- **통계적 이상**: 평균과 표준편차 기반 이상 탐지
- **패턴 이상**: 정상 패턴에서 벗어난 행동 탐지
- **시계열 이상**: 시간적 패턴의 비정상 변화 탐지
- **다변량 이상**: 여러 변수의 조합에서 발생하는 이상 탐지

### 실시간 모니터링
- **시스템 메트릭**: CPU, 메모리, 디스크 사용량
- **비즈니스 메트릭**: 매출, 주문, 고객 활동
- **성능 지표**: 응답 시간, 처리량, 오류율
- **알림 시스템**: 임계값 초과 시 자동 알림

## 프론트엔드 통합

### 분석 페이지 접근
```
http://localhost:3000/analytics
```

### 주요 기능
- **분석 요약**: 전체 분석 시스템 현황 파악
- **매출 예측**: 30일 매출 예측 및 시각화
- **실시간 메트릭**: 실시간 성능 지표 모니터링
- **분석 결과**: 다양한 분석 결과 조회
- **예측 모델**: 머신러닝 모델 관리
- **인사이트**: 자동 생성된 비즈니스 인사이트
- **분석 도구**: 트렌드, 상관관계, 클러스터링, 이상 탐지

### 차트 및 시각화
- **라인 차트**: 시계열 데이터 및 트렌드 표시
- **막대 차트**: 카테고리별 데이터 비교
- **파이 차트**: 비율 및 구성 요소 표시
- **산점도**: 상관관계 및 분포 시각화
- **히트맵**: 상관관계 매트릭스 표시

## 머신러닝 모델

### 지원 알고리즘
- **선형 회귀**: 연속형 변수 예측
- **랜덤 포레스트**: 분류 및 회귀 문제
- **K-means 클러스터링**: 데이터 그룹화
- **이상 탐지**: 비정상 패턴 탐지

### 모델 성능 평가
- **정확도 (Accuracy)**: 전체 예측 중 정확한 비율
- **R² 점수**: 회귀 모델의 설명력
- **신뢰도 (Confidence)**: 예측의 신뢰 수준
- **교차 검증**: 모델의 일반화 성능 평가

### 모델 관리
- **모델 저장**: 훈련된 모델의 영구 저장
- **모델 버전 관리**: 모델 버전 추적 및 관리
- **모델 배포**: 프로덕션 환경 배포
- **모델 모니터링**: 성능 지속적 모니터링

## 성능 최적화

### 캐싱 전략
- **분석 결과 캐싱**: 반복 분석 결과 저장
- **모델 캐싱**: 훈련된 모델 메모리 저장
- **데이터 캐싱**: 자주 사용되는 데이터 저장
- **캐시 정리**: 오래된 캐시 자동 정리

### 데이터 처리
- **배치 처리**: 대용량 데이터 배치 처리
- **증분 처리**: 새로운 데이터만 처리
- **병렬 처리**: 멀티스레드 병렬 처리
- **스트리밍 처리**: 실시간 데이터 스트리밍

### 메모리 관리
- **메모리 풀**: 객체 재사용을 통한 메모리 효율성
- **가비지 컬렉션**: 자동 메모리 정리
- **메모리 모니터링**: 메모리 사용량 추적
- **메모리 최적화**: 메모리 사용량 최소화

## 보안 및 개인정보보호

### 데이터 보안
- **데이터 암호화**: 민감한 데이터 암호화 저장
- **접근 제어**: 역할 기반 데이터 접근 제어
- **감사 로그**: 데이터 접근 및 사용 로그
- **데이터 마스킹**: 개인정보 자동 마스킹

### 모델 보안
- **모델 암호화**: 훈련된 모델 암호화
- **입력 검증**: 모델 입력 데이터 검증
- **출력 필터링**: 모델 출력 결과 필터링
- **보안 테스트**: 모델 보안 취약점 테스트

## 문제 해결

### 일반적인 문제
1. **메모리 부족**: 데이터 크기 줄이기 또는 배치 처리
2. **모델 성능 저하**: 하이퍼파라미터 튜닝 또는 데이터 품질 개선
3. **실시간 지연**: 캐싱 전략 또는 처리 최적화
4. **예측 정확도 낮음**: 특성 엔지니어링 또는 모델 선택 개선

### 로그 확인
```bash
# 분석 로그
tail -f logs/analytics.log

# 모델 훈련 로그
tail -f logs/model_training.log

# 실시간 메트릭 로그
tail -f logs/realtime_metrics.log
```

### 성능 모니터링
- CPU 및 메모리 사용량 모니터링
- 모델 훈련 및 예측 시간 측정
- 데이터 처리량 및 처리 시간 추적
- 오류율 및 성공률 모니터링

## 개발 가이드라인

### 새로운 분석 알고리즘 추가
```python
# 사용자 정의 분석 클래스
class CustomAnalysis:
    def __init__(self, parameters):
        self.parameters = parameters
    
    def analyze(self, data):
        # 분석 로직 구현
        results = self._perform_analysis(data)
        return results
    
    def _perform_analysis(self, data):
        # 실제 분석 수행
        pass

# 분석 관리자에 등록
analytics_manager.register_analysis('custom', CustomAnalysis)
```

### 새로운 예측 모델 추가
```python
# 사용자 정의 모델 클래스
class CustomModel:
    def __init__(self, parameters):
        self.parameters = parameters
        self.model = None
    
    def train(self, X, y):
        # 모델 훈련 로직
        self.model = self._create_model()
        self.model.fit(X, y)
    
    def predict(self, X):
        # 예측 로직
        return self.model.predict(X)
    
    def _create_model(self):
        # 모델 생성 로직
        pass

# 모델 관리자에 등록
analytics_manager.register_model('custom_model', CustomModel)
```

### 새로운 인사이트 생성기 추가
```python
# 사용자 정의 인사이트 생성기
class CustomInsightGenerator:
    def __init__(self):
        self.name = "Custom Insight Generator"
    
    def generate_insights(self, data):
        # 인사이트 생성 로직
        insights = []
        # 분석 및 인사이트 생성
        return insights

# 인사이트 생성기에 등록
analytics_manager.register_insight_generator(CustomInsightGenerator())
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 