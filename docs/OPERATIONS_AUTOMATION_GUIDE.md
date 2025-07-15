# 운영 자동화/테스트/확장 가이드 (초보자용)

## 1. 운영 자동화 구조
- 실시간 이벤트 감지/알림: `api/realtime_monitoring.py` (30초마다 자동 감지)
- 일간 자동 보고: `scripts/auto_daily_report.py` (매일 자정 자동 실행)
- 관리자 이메일 자동 보고: 환경변수 `ADMIN_EMAIL`로 지정

## 2. 주요 API/컴포넌트
- 실시간 대시보드: `/api/realtime/dashboard`
- 실시간 알림 발송: `/api/realtime/notifications/push`
- 프론트 대시보드: `/enhanced-alerts` (엑셀/CSV 다운로드 포함)

## 3. 확장 방법
- 알림/보고 규칙 추가: `api/modules/automation.py` 참고
- 이메일/슬랙/웹훅 등 외부 채널 연동: `utils/email_utils.py` 참고
- 스케줄러 확장: `scripts/auto_daily_report.py` 참고 (cron/Task Scheduler 등록)

## 4. 테스트 실행법
- 자동화 테스트: `pytest tests/` 명령어로 전체 테스트 실행
- 주요 테스트 파일: `tests/test_realtime_alerts.py`

## 5. 자주 묻는 질문(FAQ)
- Q: 관리자 이메일은 어디서 설정하나요?
  - A: `.env` 또는 환경변수 `ADMIN_EMAIL`에 입력
- Q: 자동화 스케줄러는 어떻게 등록하나요?
  - A: 리눅스는 `crontab -e`, 윈도우는 작업 스케줄러에서 등록
- Q: 알림/보고 내역을 엑셀로 받고 싶어요
  - A: 프론트 대시보드 `/enhanced-alerts`에서 다운로드 버튼 클릭

---

> 본 가이드는 운영 자동화/테스트/확장에 바로 활용할 수 있도록 설계되었습니다. 추가 문의는 관리자에게 연락하세요. 