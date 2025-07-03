# Sentry & Slack 연동 가이드

## Sentry 연동 (프론트엔드/백엔드)
- Sentry DSN을 환경변수에 입력
- 에러 추적/모니터링 자동화

### 프론트엔드(Next.js) 예시
```ts
// restaurant_frontend/sentry.client.config.ts
import * as Sentry from '@sentry/nextjs';
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
});
```

### 백엔드(Flask) 예시
```py
# app.py 또는 extensions.py
import sentry_sdk
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    traces_sample_rate=1.0
)
```

## Slack Webhook 연동 (백엔드)
- SLACK_WEBHOOK_URL 환경변수에 Webhook URL 입력
- 에러/이벤트 발생 시 Slack 알림 전송

### 예시 코드
```py
import requests, os

def send_slack_alert(message):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json={'text': message})
```

---
환경변수 예시는 .env.example 파일 참고 