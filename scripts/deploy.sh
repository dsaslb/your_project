#!/bin/bash
# 운영 환경 배포/운영 자동화 스크립트 예시
# 1. 서버/스케줄러/이벤트 감지 서비스 자동 실행
# 2. supervisor/systemd 등과 연동 가능

# 가상환경 활성화 (필요시)
# source venv/bin/activate

# 서버 실행 (백그라운드)
nohup python app.py &

# 운영 자동화 스케줄러 실행 (백그라운드)
nohup python scripts/auto_admin_alerts.py &

# 이벤트 감지/알림 서비스 실행 (백그라운드)
nohup python -m utils.event_auto_detector &

echo "[배포] 서버/스케줄러/이벤트 감지 서비스가 자동 실행되었습니다." 
