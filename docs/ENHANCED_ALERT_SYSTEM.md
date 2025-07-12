# 고도화된 알림 시스템

## 개요

고도화된 알림 시스템은 플러그인 모니터링의 실시간 알림/이벤트 연동 기능을 제공합니다. 임계치 초과, 오류, 중요 상태변화 등이 발생할 때 운영자/관리자에게 다양한 채널을 통해 실시간 알림을 전송합니다.

## 주요 기능

### 1. 실시간 알림 시스템
- **다중 채널 지원**: Web, Email, Slack, Telegram, SMS, Push, Dashboard
- **우선순위 기반 알림**: INFO, WARNING, ERROR, CRITICAL, EMERGENCY
- **쿨다운 시스템**: 중복 알림 방지
- **알림 승인/해결**: 관리자 작업 추적

### 2. 알림 규칙 관리
- **동적 규칙 생성**: 메트릭, 임계값, 연산자 설정
- **플러그인별 규칙**: 개별 플러그인에 대한 맞춤 규칙
- **규칙 활성화/비활성화**: 필요에 따른 규칙 제어

### 3. 채널 설정
- **이메일**: SMTP 서버 설정, 수신자 관리
- **Slack**: Webhook URL, 채널 설정
- **Telegram**: Bot Token, Chat ID 설정
- **SMS**: Twilio 등 SMS 서비스 연동

### 4. 통계 및 분석
- **실시간 통계**: 24시간 알림 분포
- **심각도별 분석**: 알림 레벨별 통계
- **플러그인별 분석**: 개별 플러그인 알림 현황

## 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   플러그인      │    │   모니터링      │    │   알림 시스템   │
│   메트릭        │───▶│   엔진          │───▶│   엔진          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   REST API      │    │   다중 채널     │
│   실시간 알림   │◀───│   관리 인터페이스│◀───│   전송 시스템   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 설치 및 설정

### 1. 백엔드 설정

#### 의존성 설치
```bash
pip install websockets requests psutil
```

#### 환경 변수 설정
```bash
# 이메일 설정
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=alerts@yourcompany.com

# Slack 설정
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_CHANNEL=#alerts

# Telegram 설정
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# SMS 설정 (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

### 2. 프론트엔드 설정

#### 컴포넌트 사용
```tsx
import EnhancedAlertSystem from '../components/EnhancedAlertSystem';

function App() {
  return (
    <div>
      <EnhancedAlertSystem />
    </div>
  );
}
```

## API 참조

### 시스템 상태 조회
```http
GET /api/enhanced-alerts/status
```

### 활성 알림 조회
```http
GET /api/enhanced-alerts/alerts/active
```

### 알림 히스토리 조회
```http
GET /api/enhanced-alerts/alerts/history?hours=24
```

### 알림 규칙 조회
```http
GET /api/enhanced-alerts/rules
```

### 알림 규칙 생성
```http
POST /api/enhanced-alerts/rules
Content-Type: application/json

{
  "name": "CPU 높음 알림",
  "description": "CPU 사용률이 80%를 초과할 때",
  "metric": "cpu_usage",
  "operator": ">",
  "threshold": 80.0,
  "severity": "warning",
  "channels": ["web", "email"],
  "cooldown_minutes": 5,
  "enabled": true
}
```

### 알림 승인
```http
POST /api/enhanced-alerts/alerts/{alert_id}/acknowledge
```

### 알림 해결
```http
POST /api/enhanced-alerts/alerts/{alert_id}/resolve
```

### 채널 설정 조회
```http
GET /api/enhanced-alerts/channels/config
```

### 채널 설정 업데이트
```http
PUT /api/enhanced-alerts/channels/{channel_name}/config
Content-Type: application/json

{
  "enabled": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "username": "your-email@gmail.com",
  "password": "your-app-password",
  "from_email": "alerts@yourcompany.com",
  "to_emails": ["admin@yourcompany.com"]
}
```

### 채널 테스트
```http
POST /api/enhanced-alerts/test/{channel_name}
```

### 알림 통계 조회
```http
GET /api/enhanced-alerts/statistics
```

## 사용 예시

### 1. 기본 알림 규칙 설정

```python
from core.backend.enhanced_alert_system import enhanced_alert_system, AlertRule, AlertSeverity, AlertChannel

# CPU 사용률 높음 알림 규칙
cpu_rule = AlertRule(
    id="cpu_high",
    name="CPU 사용률 높음",
    description="CPU 사용률이 80%를 초과할 때",
    metric="cpu_usage",
    operator=">",
    threshold=80.0,
    severity=AlertSeverity.WARNING,
    channels=[AlertChannel.WEB, AlertChannel.DASHBOARD],
    cooldown_minutes=5
)

enhanced_alert_system.add_alert_rule(cpu_rule)
```

### 2. 메트릭 체크 및 알림 생성

```python
# 플러그인 메트릭 업데이트
metrics = {
    'cpu_usage': 85.5,
    'memory_usage': 75.2,
    'error_rate': 5.0,
    'response_time': 2.5
}

enhanced_alert_system.check_metrics(
    plugin_id="my_plugin",
    plugin_name="내 플러그인",
    metrics=metrics
)
```

### 3. 채널 설정

```python
# 이메일 채널 설정
email_config = {
    'enabled': True,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your-email@gmail.com',
    'password': 'your-app-password',
    'from_email': 'alerts@yourcompany.com',
    'to_emails': ['admin@yourcompany.com']
}

enhanced_alert_system.update_channel_config(AlertChannel.EMAIL, email_config)
```

## 모니터링 및 관리

### 1. 실시간 모니터링

```bash
# 모니터링 시작
python scripts/start_plugin_monitoring.py

# 고도화된 알림 시스템 테스트
python scripts/test_enhanced_alerts.py
```

### 2. 로그 확인

```bash
# 알림 시스템 로그 확인
tail -f logs/plugin_monitoring.log

# WebSocket 서버 로그 확인
tail -f logs/alert_websocket.log
```

### 3. 성능 모니터링

```bash
# 시스템 리소스 사용량 확인
python scripts/plugin_performance_monitor.py
```

## 문제 해결

### 1. 알림이 전송되지 않는 경우

1. **채널 설정 확인**
   ```bash
   curl http://localhost:5000/api/enhanced-alerts/channels/config
   ```

2. **채널 테스트**
   ```bash
   curl -X POST http://localhost:5000/api/enhanced-alerts/test/web
   ```

3. **로그 확인**
   ```bash
   tail -f logs/plugin_monitoring.log | grep "알림"
   ```

### 2. WebSocket 연결 문제

1. **포트 확인**
   ```bash
   netstat -tlnp | grep 8765
   ```

2. **방화벽 설정**
   ```bash
   # Windows
   netsh advfirewall firewall add rule name="Alert WebSocket" dir=in action=allow protocol=TCP localport=8765

   # Linux
   sudo ufw allow 8765
   ```

### 3. 이메일 전송 실패

1. **SMTP 설정 확인**
   - Gmail의 경우 앱 비밀번호 사용
   - 2단계 인증 활성화 필요

2. **포트 확인**
   ```bash
   telnet smtp.gmail.com 587
   ```

## 성능 최적화

### 1. 알림 규칙 최적화

- **쿨다운 시간 조정**: 너무 짧으면 스팸, 너무 길면 지연
- **임계값 설정**: 실제 운영 환경에 맞게 조정
- **채널 선택**: 중요도에 따라 적절한 채널 선택

### 2. 시스템 리소스 관리

- **메트릭 수집 주기**: 30초에서 1분으로 조정 가능
- **히스토리 보관 기간**: 기본 7일, 필요에 따라 조정
- **메모리 사용량**: 활성 알림 수 제한

### 3. 확장성 고려사항

- **데이터베이스 사용**: 대용량 환경에서는 PostgreSQL/MongoDB 연동
- **Redis 캐싱**: 자주 조회되는 데이터 캐싱
- **로드 밸런싱**: 여러 인스턴스로 분산 처리

## 보안 고려사항

### 1. API 보안

- **인증**: JWT 토큰 기반 인증
- **권한**: 역할 기반 접근 제어
- **HTTPS**: 프로덕션 환경에서 HTTPS 사용

### 2. 채널 보안

- **이메일**: 암호화된 SMTP 연결
- **Slack**: Webhook URL 보안
- **Telegram**: Bot Token 보안

### 3. 데이터 보호

- **개인정보**: 민감한 정보 로깅 제외
- **암호화**: 설정 파일 암호화
- **백업**: 정기적인 설정 백업

## 향후 개발 계획

### 1. 추가 채널 지원
- **Microsoft Teams**: Teams Webhook 연동
- **Discord**: Discord Bot 연동
- **PagerDuty**: PagerDuty API 연동

### 2. 고급 기능
- **조건부 알림**: 복합 조건 지원
- **알림 그룹화**: 관련 알림 묶기
- **자동 해결**: 특정 조건에서 자동 해결

### 3. 분석 기능
- **예측 분석**: ML 기반 장애 예측
- **패턴 분석**: 알림 패턴 분석
- **성능 추이**: 장기 성능 추이 분석

## 지원 및 문의

- **문서**: 이 문서와 API 참조
- **로그**: `logs/` 디렉토리의 로그 파일
- **테스트**: `scripts/test_enhanced_alerts.py`
- **이슈**: GitHub Issues 페이지

---

**버전**: 1.0.0  
**최종 업데이트**: 2024년 12월  
**작성자**: 플러그인 시스템 개발팀 