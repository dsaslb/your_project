# 통합 연동 모듈 시스템

## 개요

통합 연동 모듈 시스템은 모든 모듈이 중앙 데이터를 공유하고 실시간으로 연동되는 통합 시스템입니다. 출퇴근 관리, 매출 관리, 급여 관리, 재고 관리 등 모든 모듈이 하나의 중앙 데이터 레이어를 통해 데이터를 공유하고, 자동으로 연동되어 효율성 분석 및 개선 제안을 생성합니다.

## 주요 특징

### 🔄 실시간 연동
- 모든 모듈이 중앙 데이터 레이어를 통해 실시간으로 데이터 공유
- 모듈 간 자동 이벤트 트리거 및 처리
- 실시간 효율성 분석 및 알림

### 📊 통합 분석
- 크로스 모듈 데이터 분석
- 자동 효율성 지표 계산
- AI 기반 인사이트 생성
- 예측적 개선 제안

### 🚀 자동화
- 출퇴근 → 매출 → 급여 → 분석 → 알림 자동 연동
- 백그라운드 분석 작업
- 자동 알림 및 리포트 생성

## 시스템 아키텍처

### 중앙 데이터 레이어
```
┌─────────────────────────────────────────────────────────────┐
│                    중앙 데이터 레이어                        │
├─────────────────────────────────────────────────────────────┤
│  브랜드 │  매장  │  직원  │ 출퇴근 │  매출  │ 급여 │ 재고  │
├─────────────────────────────────────────────────────────────┤
│                    SQLite 데이터베이스                       │
└─────────────────────────────────────────────────────────────┘
```

### 통합 연동 시스템
```
┌─────────────────────────────────────────────────────────────┐
│                 통합 연동 모듈 시스템                        │
├─────────────────────────────────────────────────────────────┤
│  이벤트 핸들러  │  백그라운드 작업자  │  분석 엔진          │
├─────────────────────────────────────────────────────────────┤
│  알림 시스템   │  효율성 분석      │  개선 제안 생성      │
└─────────────────────────────────────────────────────────────┘
```

## 연동 시나리오

### 1. 출퇴근 → 매출 연동
```
출퇴근 기록 → 매출 데이터 조회 → 효율성 분석 → 인사이트 생성
```

**자동 처리 과정:**
- 직원 출퇴근 기록 시 해당 날짜 매출 데이터 자동 조회
- 근무 시간 대비 매출 효율성 계산
- 효율성 저하 시 자동 알림 생성

### 2. 매출 → 급여 연동
```
매출 기록 → 급여 계산 → 인건비 비율 분석 → 개선 제안
```

**자동 처리 과정:**
- 매출 데이터 기반 급여 계산
- 매출 대비 인건비 비율 자동 계산
- 비율이 높을 경우 개선 제안 생성

### 3. 급여 → 분석 연동
```
급여 계산 → 효율성 분석 → 개선 사항 도출 → 관리자 알림
```

**자동 처리 과정:**
- 급여 계산 완료 시 통합 효율성 분석 실행
- 개선 가능한 영역 자동 식별
- 관리자에게 개선 제안 알림

### 4. 분석 → 알림 연동
```
분석 결과 → 중요 인사이트 추출 → 알림 생성 → 리포트 전송
```

**자동 처리 과정:**
- 분석 결과에서 중요한 인사이트 자동 추출
- 우선순위에 따른 알림 생성
- 관리자 대시보드 업데이트

## API 엔드포인트

### 통합 대시보드
```http
GET /api/integrated/dashboard
```
모든 모듈의 통합 현황 및 실시간 데이터 조회

### 통합 데이터 조회
```http
GET /api/integrated/data/{branch_id}?types=attendance,sales,payroll
```
특정 매장의 모든 모듈 데이터 통합 조회

### 효율성 분석
```http
GET /api/integrated/efficiency/{branch_id}?period=month
```
매장별 효율성 분석 결과 조회

### 출퇴근 기록 (통합 연동)
```http
POST /api/integrated/attendance/record
Content-Type: application/json

{
  "employee_id": 1,
  "branch_id": 1,
  "action": "clock_in"
}
```

### 매출 기록 (통합 연동)
```http
POST /api/integrated/sales/record
Content-Type: application/json

{
  "employee_id": 1,
  "branch_id": 1,
  "amount": 50000,
  "category": "음료"
}
```

### 급여 계산 (통합 연동)
```http
POST /api/integrated/payroll/calculate
Content-Type: application/json

{
  "employee_id": 1,
  "branch_id": 1,
  "year": 2024,
  "month": 1
}
```

### 통합 분석 생성
```http
POST /api/integrated/analytics/generate
Content-Type: application/json

{
  "branch_id": 1,
  "period": "month"
}
```

### 통합 시나리오 데모
```http
POST /api/integrated/demo/integrated-scenario
```
전체 통합 연동 시나리오 데모 실행

## 효율성 지표

### 인건비 비율
```
인건비 비율 = (총 급여 / 총 매출) × 100
```
- 경고 임계값: 30%
- 위험 임계값: 40%

### 시간당 매출
```
시간당 매출 = 총 매출 / 총 근무 시간
```
- 경고 임계값: 50,000원

### 출근률
```
출근률 = (정시 출근자 수 / 전체 직원 수) × 100
```
- 경고 임계값: 85%

### 근무 효율성
```
근무 효율성 = (실제 근무 시간 / 예상 근무 시간) × 100
```

## 알림 시스템

### 실시간 알림
- 지각 알림
- 초과근무 알림
- 효율성 저하 알림
- 인건비 비율 경고

### 관리자 알림
- 일일 분석 완료 알림
- 개선 제안 알림
- 시스템 상태 업데이트

### 알림 우선순위
- **High**: 긴급한 개선 필요
- **Normal**: 일반적인 알림
- **Low**: 정보성 알림

## 데모 시스템

### 통합 시나리오 데모
1. 출퇴근 기록 시뮬레이션
2. 매출 기록 시뮬레이션
3. 급여 계산 시뮬레이션
4. 통합 분석 실행
5. 자동 알림 생성

### 실시간 모니터링
- 현재 근무자 수
- 오늘 매출
- 지각자 수
- 미읽 알림 수

### 효율성 지표 실시간 표시
- 인건비 비율
- 시간당 매출
- 출근률

## 설정 및 구성

### 시스템 설정
```json
{
  "system_config": {
    "central_data_layer": {
      "database_path": "data/central_data.db",
      "auto_backup": true,
      "backup_interval_hours": 24
    },
    "integration_system": {
      "auto_start": true,
      "event_handlers_enabled": true,
      "background_workers": 10
    }
  }
}
```

### 모듈별 설정
```json
{
  "modules": {
    "attendance_management": {
      "enabled": true,
      "auto_integration": true,
      "real_time_updates": true
    }
  }
}
```

### 효율성 임계값 설정
```json
{
  "analytics": {
    "efficiency_thresholds": {
      "labor_cost_ratio_warning": 30.0,
      "labor_cost_ratio_critical": 40.0,
      "attendance_rate_warning": 85.0,
      "sales_per_hour_warning": 50000
    }
  }
}
```

## 사용 방법

### 1. 시스템 시작
```python
from core.backend.integrated_module_system import integrated_system

# 통합 시스템 시작
integrated_system.start_integration_system()
```

### 2. 이벤트 발생
```python
from core.backend.integrated_module_system import IntegrationEvent, IntegrationEventData

# 출퇴근 기록 이벤트 발생
event_data = IntegrationEventData(
    event_type=IntegrationEvent.ATTENDANCE_RECORDED,
    module_id="attendance_management",
    data=attendance_data,
    timestamp=datetime.now(),
    user_id=employee_id,
    branch_id=branch_id
)

integrated_system.emit_event(event_data)
```

### 3. 통합 데이터 조회
```python
# 특정 매장의 통합 데이터 조회
integrated_data = integrated_system.get_integrated_data(branch_id=1)

# 효율성 분석 조회
efficiency_data = integrated_system.get_efficiency_analysis(branch_id=1, period="month")
```

### 4. 관리자 대시보드
```python
# 관리자 대시보드 데이터 조회
dashboard_data = integrated_system.get_management_dashboard(user_id=1)
```

## 모니터링 및 관리

### 시스템 상태 모니터링
```http
GET /api/integrated/status
```

### 실시간 데이터 스트림
```http
GET /api/integrated/realtime/stream?branch_id=1
```

### 성능 지표
- 응답 시간
- 메모리 사용량
- CPU 사용량
- 활성 연결 수

## 확장성

### 새로운 모듈 추가
1. 모듈을 중앙 데이터 레이어에 등록
2. 이벤트 핸들러 구현
3. 연동 시나리오 정의
4. API 엔드포인트 추가

### 새로운 연동 시나리오 추가
1. 시나리오 정의
2. 이벤트 핸들러 구현
3. 분석 로직 추가
4. 알림 규칙 설정

## 보안

### 데이터 보안
- 중앙 데이터 레이어 암호화
- 접근 제어 및 권한 관리
- 감사 로깅

### API 보안
- 인증 및 권한 확인
- 요청 검증
- 속도 제한

## 문제 해결

### 일반적인 문제
1. **연동이 작동하지 않는 경우**
   - 이벤트 핸들러 등록 확인
   - 모듈 상태 확인
   - 로그 확인

2. **성능 문제**
   - 백그라운드 작업자 수 조정
   - 캐시 크기 조정
   - 데이터베이스 최적화

3. **알림이 오지 않는 경우**
   - 알림 설정 확인
   - 임계값 설정 확인
   - 이벤트 발생 확인

### 로그 확인
```python
import logging
logging.getLogger('integrated_system').setLevel(logging.DEBUG)
```

## 업데이트 및 유지보수

### 정기 업데이트
- 데이터베이스 백업
- 성능 최적화
- 보안 패치 적용

### 모니터링
- 시스템 성능 모니터링
- 오류 로그 확인
- 사용자 피드백 수집

## 지원 및 문의

### 기술 지원
- 이슈 트래커: GitHub Issues
- 문서: `/docs/integrated_module_system.md`
- API 문서: `/docs/api/integrated.md`

### 커뮤니티
- 포럼: 커뮤니티 포럼
- 슬랙: 개발자 슬랙 채널
- 이메일: support@yourprogram.com

---

**버전**: 1.0.0  
**최종 업데이트**: 2024-01-15  
**작성자**: Your Program Team 