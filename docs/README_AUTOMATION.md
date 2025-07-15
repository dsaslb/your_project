# 운영/보안 자동화 구조 및 활용법 요약

## 1. 전체 구조
- 서버/스케줄러/이벤트 감지/알림/이력/정책/대시보드/보고/피드백 등 모든 운영/보안 체계가 자동화
- 관리자/운영자는 대시보드, 리포트, 알림, 정책 문서로 실시간 현황을 한눈에 파악

## 2. 주요 자동화 스크립트/서비스
- `scripts/auto_security_check.py`: 자동 점검 및 관리자 알림
- `scripts/auto_weekly_report.py`: 주간/월간 리포트 자동 생성
- `scripts/auto_report_notify.py`: 리포트/점검 결과 자동 발송
- `scripts/deploy.sh`: 서버/스케줄러/이벤트 감지 서비스 자동 실행

## 3. 스케줄링/정기 실행
- cron(리눅스) 또는 작업 스케줄러(윈도우)로 정기 실행
- 예시: 매일 점검, 매주 리포트, 장애/이벤트 발생 시 즉시 알림

## 4. 현장 운영 활용법
- 대시보드/이력/알림/정책/보고서/피드백 등 문서와 UI를 적극 활용
- 이상 징후/장애/이슈 발생 시 즉시 대응 및 기록
- 피드백/지속 개선 프로세스 정착

## 5. 참고 문서
- 관리자 가이드: docs/ADMIN_GUIDE.md
- 보안 정책: docs/SECURITY_POLICY.md
- 체크리스트: docs/OPERATION_SECURITY_CHECKLIST.md
- 워크플로우: docs/OPERATION_WORKFLOW.md
- 피드백/개선: docs/FEEDBACK_IMPROVEMENT_PROCESS.md
- 스케줄링: docs/AUTO_SCHEDULING_EXAMPLES.md
- 베스트 프랙티스: docs/OPERATION_BEST_PRACTICES.md 