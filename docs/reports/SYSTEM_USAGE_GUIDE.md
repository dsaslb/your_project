# 🚀 AI 기반 시스템 사용법 가이드

**시스템 버전**: 2.0.0  
**최종 업데이트**: 2025년 7월 29일

## 🎯 시스템 개요

이 시스템은 AI 기반 성능 예측, 실시간 모니터링, 자동 최적화, 모바일 알림을 제공하는 **지능형 시스템 관리 플랫폼**입니다.

## 📊 주요 기능

### 1. AI 성능 예측
- **미래 6-72시간 성능 예측**
- **CPU, 메모리, 응답시간 예측**
- **패턴 기반 예측 모델**

### 2. 실시간 모니터링
- **30초 간격 성능 추적**
- **임계값 기반 알림**
- **자동 데이터 수집**

### 3. 자동 최적화
- **시스템 자동 최적화**
- **캐시 및 로그 정리**
- **데이터베이스 최적화**

### 4. 모바일 알림
- **다중 플랫폼 지원**
- **스마트 알림 규칙**
- **실시간 알림**

## 🌐 웹 대시보드 접근

### 시스템 상태 대시보드
```
URL: http://localhost:3000/system-health
기능: 실시간 시스템 상태 모니터링
```

### 고급 분석 대시보드
```
URL: http://localhost:3000/advanced-analytics
기능: AI 예측 및 고급 분석
```

## 🔧 API 사용법

### 1. 시스템 상태 조회
```bash
# 전체 시스템 상태
curl -X GET "http://localhost:5000/api/system/health"

# 빠른 상태 점검
curl -X GET "http://localhost:5000/api/system/health/quick"
```

### 2. AI 예측 및 분석
```bash
# AI 모델 훈련
curl -X POST "http://localhost:5000/api/ai/train"

# 성능 예측 (24시간)
curl -X GET "http://localhost:5000/api/ai/predict?hours=24"

# 성능 분석
curl -X GET "http://localhost:5000/api/ai/analysis"

# AI 인사이트
curl -X GET "http://localhost:5000/api/ai/insights"
```

### 3. 시스템 최적화
```bash
# 시스템 최적화 실행
curl -X POST "http://localhost:5000/api/system/optimize"

# 자동 유지보수 시작
curl -X POST "http://localhost:5000/api/system/maintenance/start"

# 백업 생성
curl -X POST "http://localhost:5000/api/system/backup"
```

## 📱 모바일 알림 설정

### 1. 설정 파일 위치
```
config/mobile_notifications.json
```

### 2. Telegram 설정 예시
```json
{
  "enabled": true,
  "providers": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN",
      "chat_id": "YOUR_CHAT_ID"
    }
  },
  "notification_levels": {
    "critical": true,
    "warning": true,
    "info": false
  }
}
```

### 3. 지원 플랫폼
- **Telegram**: 봇 기반 메시징
- **Slack**: 워크스페이스 알림
- **Pushover**: 모바일 푸시 알림
- **Email**: 이메일 알림
- **Log**: 로그 파일 알림 (테스트용)

## 🧠 AI 모델 관리

### 1. 모델 훈련
```python
from ai.performance_predictor import train_performance_models
result = train_performance_models()
print(result)
```

### 2. 성능 예측
```python
from ai.performance_predictor import predict_future_performance
predictions = predict_future_performance(hours=24)
print(predictions)
```

### 3. 모델 상태 확인
```bash
curl -X GET "http://localhost:5000/api/ai/models/status"
```

## 🔍 모니터링 및 로그

### 1. 성능 모니터링
```python
from scripts.performance_monitor import get_performance_status
status = get_performance_status()
print(status)
```

### 2. 로그 파일 위치
```
logs/
├── performance_monitor.log      # 성능 모니터링 로그
├── automated_maintenance.log    # 자동 유지보수 로그
├── mobile_notifications.json    # 모바일 알림 히스토리
└── notifications.log           # 알림 로그
```

### 3. 성능 데이터베이스
```
data/performance_metrics.db
```

## 🛠️ 시스템 관리 명령어

### 1. 서버 시작/중지
```bash
# 백엔드 서버 시작
python app.py

# 프론트엔드 서버 시작
cd frontend
npm run dev
```

### 2. 성능 모니터링 제어
```python
# 모니터링 시작
from scripts.performance_monitor import start_performance_monitoring
start_performance_monitoring()

# 모니터링 중지
from scripts.performance_monitor import stop_performance_monitoring
stop_performance_monitoring()
```

### 3. 자동 유지보수 제어
```python
# 유지보수 시작
from scripts.automated_maintenance import start_maintenance
start_maintenance()

# 유지보수 중지
from scripts.automated_maintenance import stop_maintenance
stop_maintenance()
```

## 📈 성능 지표

### 1. AI 예측 정확도
- **CPU 사용률 예측**: 평균 오차 < 5%
- **메모리 사용률 예측**: 평균 오차 < 3%
- **응답시간 예측**: 평균 오차 < 0.5초

### 2. 시스템 성능
- **모니터링 간격**: 30초
- **데이터 보관 기간**: 7일
- **알림 응답 시간**: < 1초

### 3. 최적화 효과
- **캐시 정리**: 평균 50MB 공간 확보
- **로그 정리**: 평균 30MB 공간 확보
- **데이터베이스 최적화**: 쿼리 속도 20% 향상

## 🔧 문제 해결

### 1. AI 모델 훈련 실패
```bash
# 데이터 확인
python -c "import sqlite3; conn = sqlite3.connect('data/performance_metrics.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM performance_metrics'); print(cursor.fetchone()[0]); conn.close()"

# 테스트 데이터 생성
python scripts/generate_test_data.py
```

### 2. 알림이 발송되지 않음
```bash
# 설정 파일 확인
cat config/mobile_notifications.json

# 로그 확인
tail -f logs/notifications.log
```

### 3. 성능 모니터링 중단
```python
# 모니터링 재시작
from scripts.performance_monitor import start_performance_monitoring
start_performance_monitoring()
```

## 🚀 고급 사용법

### 1. 커스텀 알림 규칙
```python
from utils.mobile_notification_system import send_system_alert

# 커스텀 알림 발송
send_system_alert(
    title="커스텀 알림",
    message="사용자 정의 알림 메시지",
    level="warning",
    category="custom",
    data={"custom_field": "value"}
)
```

### 2. 성능 데이터 내보내기
```bash
# CSV 형식으로 내보내기
curl -X GET "http://localhost:5000/api/ai/data/export?days=7"
```

### 3. 실시간 성능 추적
```python
from scripts.performance_monitor import performance_monitor

# 실시간 데이터 접근
recent_data = performance_monitor.performance_history[-10:]
print(recent_data)
```

## 📞 지원 및 문의

### 1. 시스템 상태 확인
```bash
# 통합 테스트 실행
python scripts/integration_test.py
```

### 2. 로그 분석
```bash
# 최근 알림 확인
tail -n 20 logs/notifications.log

# 성능 모니터링 로그 확인
tail -n 50 logs/performance_monitor.log
```

### 3. 데이터베이스 백업
```bash
# 수동 백업 생성
python -c "from scripts.automated_maintenance import automated_maintenance; result = automated_maintenance.create_backup(); print(result)"
```

---

**시스템 관리자**: AI 어시스턴트  
**문의**: 시스템 내 알림 기능 활용  
**업데이트**: 자동 업데이트 시스템 활용 