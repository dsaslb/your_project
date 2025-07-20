# 🍽️ 레스토랑 특화 통합 관리 시스템

## 📋 시스템 개요

레스토랑 업종에 특화된 종합 관리 시스템으로, AI 예측, 자동화, 모바일 최적화, 고급 분석 기능을 제공합니다.

## 🚀 주요 기능

### 1. AI 예측 시스템
- **매출 예측**: 향후 30일 매출 예측 및 트렌드 분석
- **고객 이탈 위험 예측**: RFM 분석 기반 고객 이탈 위험도 측정
- **재고 예측**: AI 기반 재고 필요량 예측 및 자동 발주 제안
- **직원 스케줄링 예측**: 주문량 예측 기반 최적 인력 배치

### 2. 자동화 시스템
- **자동 재고 발주**: 재고 부족 시 자동 발주 생성
- **스케줄 최적화**: AI 기반 직원 스케줄 자동 최적화
- **자동 알림**: 재고 부족, 주문 대기, 성과 알림
- **설정 관리**: 자동화 규칙 및 임계값 설정

### 3. 모바일 대시보드
- **모바일 최적화**: 터치 친화적 UI/UX
- **실시간 모니터링**: 주문, 재고, 직원 현황 실시간 확인
- **탭 기반 네비게이션**: 대시보드, 주문, 재고, 직원, 분석 탭
- **풀 투 리프레시**: 모바일 친화적 데이터 새로고침

### 4. 고급 분석 시스템
- **이상치 탐지**: 매출, 주문 데이터 이상치 자동 탐지
- **고객 세분화**: K-means 클러스터링 기반 고객 분류
- **트렌드 분석**: 시계열 분석을 통한 트렌드 예측
- **경쟁사 분석**: SWOT 분석 및 시장 포지셔닝
- **AI 인사이트**: 자동 생성되는 비즈니스 인사이트

## 📁 파일 구조

```
your_program/
├── api/
│   ├── restaurant_analytics.py          # 기본 분석 API
│   ├── restaurant_ai_prediction.py      # AI 예측 API
│   ├── restaurant_automation.py         # 자동화 API
│   └── restaurant_advanced_analytics.py # 고급 분석 API
├── routes/
│   ├── restaurant_enhanced_dashboard.py # 데스크톱 대시보드
│   └── mobile_restaurant_dashboard.py   # 모바일 대시보드
├── templates/
│   ├── restaurant_enhanced_dashboard.html # 데스크톱 UI
│   └── mobile_restaurant_dashboard.html   # 모바일 UI
├── static/
│   └── css/
│       └── restaurant-dashboard.css     # 스타일시트
└── docs/
    ├── RESTAURANT_ENHANCED_DASHBOARD.md # 기본 문서
    └── RESTAURANT_COMPLETE_SYSTEM.md    # 통합 문서
```

## 🔧 설치 및 설정

### 1. 의존성 설치
```bash
pip install scikit-learn pandas numpy joblib schedule
```

### 2. 디렉토리 생성
```bash
mkdir -p data/ai_analytics/models
mkdir -p data/ai_analytics/scalers
mkdir -p data/advanced_analytics/models
mkdir -p data/automation_config
```

### 3. 앱 등록 확인
`app.py`에서 다음 블루프린트들이 등록되어 있는지 확인:
- `restaurant_analytics`
- `restaurant_ai_prediction`
- `restaurant_automation`
- `restaurant_advanced_analytics`
- `mobile_restaurant_dashboard`

## 🎯 사용법

### 1. 데스크톱 대시보드 접근
```
http://localhost:5000/restaurant/enhanced-dashboard
```

### 2. 모바일 대시보드 접근
```
http://localhost:5000/mobile/restaurant/dashboard
```

### 3. API 엔드포인트

#### AI 예측 API
- `GET /api/restaurant/predict/sales` - 매출 예측
- `GET /api/restaurant/predict/customer-churn` - 고객 이탈 예측
- `GET /api/restaurant/predict/inventory` - 재고 예측
- `GET /api/restaurant/predict/staff-scheduling` - 스케줄링 예측

#### 자동화 API
- `GET /api/restaurant/automation/status` - 자동화 상태
- `GET /api/restaurant/automation/config` - 자동화 설정
- `POST /api/restaurant/automation/auto-order` - 자동 발주 실행
- `POST /api/restaurant/automation/optimize-schedule` - 스케줄 최적화

#### 고급 분석 API
- `GET /api/restaurant/advanced/anomaly-detection` - 이상치 탐지
- `GET /api/restaurant/advanced/customer-segmentation` - 고객 세분화
- `GET /api/restaurant/advanced/trend-analysis` - 트렌드 분석
- `GET /api/restaurant/advanced/competitive-analysis` - 경쟁사 분석
- `GET /api/restaurant/advanced/insights` - AI 인사이트

## 📊 주요 기능 상세

### AI 예측 시스템

#### 매출 예측
```python
# 예측 모델 특성
- 이전 7일/30일 매출 평균
- 요일, 월, 계절성 특성
- 공휴일 여부
- 주문 수량

# 예측 결과
{
    "predictions": [
        {
            "date": "2024-01-15",
            "predicted_revenue": 1250000,
            "confidence": 0.85
        }
    ],
    "model_accuracy": 0.85
}
```

#### 고객 이탈 예측
```python
# RFM 분석 기반
- Recency: 최근 구매일
- Frequency: 구매 빈도
- Monetary: 구매 금액

# 위험도 분류
- High Risk: 이탈 위험 높음
- Medium Risk: 주의 필요
- Low Risk: 안정적 고객
```

### 자동화 시스템

#### 자동 재고 발주
```json
{
    "auto_inventory": {
        "enabled": true,
        "check_interval_hours": 6,
        "low_stock_threshold": 10,
        "auto_order_threshold": 5,
        "order_quantity_multiplier": 1.5
    }
}
```

#### 스케줄 최적화
```json
{
    "auto_scheduling": {
        "enabled": true,
        "optimization_interval_days": 7,
        "min_staff_per_shift": 2,
        "max_staff_per_shift": 8,
        "preferred_shifts": ["morning", "afternoon", "evening"]
    }
}
```

### 고급 분석 시스템

#### 이상치 탐지
```python
# Isolation Forest 알고리즘 사용
- 매출 데이터 이상치 탐지
- 주문 수 이상치 탐지
- 이상치 심각도 분류 (high/medium/low)
```

#### 고객 세분화
```python
# K-means 클러스터링 (4개 그룹)
- VIP 고객: 고가치, 고빈도
- 고가치 고객: 고가치, 저빈도
- 정기 고객: 저가치, 고빈도
- 일회성 고객: 저가치, 저빈도
```

## 🎨 UI/UX 특징

### 데스크톱 대시보드
- **반응형 디자인**: 다양한 화면 크기 지원
- **실시간 차트**: Chart.js 기반 인터랙티브 차트
- **카드 기반 레이아웃**: 정보 그룹화 및 시각화
- **다크 모드 지원**: 사용자 선호도에 따른 테마

### 모바일 대시보드
- **터치 최적화**: 터치 친화적 버튼 및 인터페이스
- **탭 네비게이션**: 하단 탭바를 통한 쉬운 이동
- **풀 투 리프레시**: 모바일 친화적 데이터 새로고침
- **실시간 알림**: 긴급 상황 실시간 알림

## 🔒 보안 및 권한

### 권한 체계
- **관리자**: 모든 기능 접근 가능
- **매니저**: 대시보드 및 분석 기능
- **직원**: 제한된 대시보드 접근

### 데이터 보안
- 사용자별 매장 데이터 필터링
- API 인증 및 권한 확인
- 민감 정보 암호화

## 📈 성능 최적화

### 데이터베이스 최적화
- 인덱스 최적화
- 쿼리 최적화
- 캐싱 전략

### 프론트엔드 최적화
- 이미지 압축
- CSS/JS 최소화
- CDN 활용

## 🐛 문제 해결

### 일반적인 문제

#### 1. 모델 로딩 실패
```bash
# 해결 방법
- data/ai_analytics/models 디렉토리 확인
- 모델 파일 권한 확인
- 의존성 패키지 재설치
```

#### 2. 자동화 작동 안함
```bash
# 해결 방법
- 자동화 설정 확인
- 로그 파일 확인
- 권한 설정 확인
```

#### 3. 모바일 대시보드 로딩 실패
```bash
# 해결 방법
- 네트워크 연결 확인
- 브라우저 캐시 삭제
- 서버 재시작
```

### 로그 확인
```bash
# 애플리케이션 로그
tail -f logs/app.log

# 에러 로그
tail -f logs/error.log
```

## 🔄 업데이트 및 유지보수

### 정기 업데이트
- **모델 재훈련**: 월 1회 AI 모델 재훈련
- **데이터 백업**: 일일 데이터베이스 백업
- **성능 모니터링**: 주간 성능 분석

### 버전 관리
- Git을 통한 코드 버전 관리
- 배포 전 테스트 환경 검증
- 롤백 계획 수립

## 📞 지원 및 문의

### 기술 지원
- 이슈 트래커: GitHub Issues
- 문서: `/docs` 디렉토리
- 로그: `/logs` 디렉토리

### 연락처
- 개발팀: dev@restaurant.com
- 기술지원: support@restaurant.com

## 🎯 향후 개발 계획

### 단기 계획 (1-3개월)
- [ ] 실시간 알림 시스템 고도화
- [ ] 모바일 앱 개발
- [ ] 다국어 지원

### 중기 계획 (3-6개월)
- [ ] 고급 머신러닝 모델 도입
- [ ] 외부 API 연동 확대
- [ ] 고객 피드백 시스템

### 장기 계획 (6개월 이상)
- [ ] AI 챗봇 도입
- [ ] 블록체인 기반 공급망 관리
- [ ] AR/VR 기술 적용

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**🍽️ 레스토랑 특화 통합 관리 시스템** - 더 스마트한 레스토랑 운영을 위한 선택 