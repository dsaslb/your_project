#!/bin/bash
# 장애 감지 및 알림 자동화 예시

SLACK_WEBHOOK="https://hooks.slack.com/services/your/webhook/url"
ALERT_MSG="[장애] 서버/DB/네트워크 장애 발생! 즉시 확인 필요."

# 서버 상태 체크 예시
if ! curl -s http://localhost:5000/health | grep 'ok'; then
  curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$ALERT_MSG\"}" $SLACK_WEBHOOK
fi
# DB 상태 체크 예시 (Postgres)
if ! pg_isready -h localhost -p 5432; then
  curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$ALERT_MSG (DB)\"}" $SLACK_WEBHOOK
fi
# 네트워크 체크 예시
if ! ping -c 1 8.8.8.8 > /dev/null; then
  curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$ALERT_MSG (Network)\"}" $SLACK_WEBHOOK
fi 