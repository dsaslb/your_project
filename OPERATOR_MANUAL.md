# 운영자 매뉴얼 (Operator Manual)

## 1. 시스템 개요 / System Overview
- 레스토랑 통합 관리 시스템: 공지, 알림, 발주, 재고, 직원, 스케줄, 통계 등 통합 관리
- Restaurant management system: notices, notifications, orders, inventory, staff, schedule, stats, etc.

## 2. 권한/계정 관리 / Role & Account Management
- 최고관리자: 전체 매장/계정/설정/통계/권한 관리
- 매장관리자: 소속 매장 관리, 직원/발주/재고/스케줄 관리
- 직원: 본인 업무만 접근
- 권한별 메뉴/기능 분기, PermissionGuard 적용

## 3. 장애/오류 대응 / Error Handling
- 서버/프론트 장애 시 로그 확인: logs/app.log, Sentry, Slack 알림
- DB/네트워크 장애 시: 재시작, 백업/복구 메뉴 활용
- 주요 에러코드/메시지 FAQ 참고

## 4. 배포/운영 / Deployment & Operation
- Github Actions로 main 브랜치 push 시 자동 배포
- .env.production 환경변수 관리, secrets 보안 유지
- logrotate, Sentry, Slack 등 모니터링 연동

## 5. 실시간 모니터링/차트 / Live Monitoring & Charts
- /admin/dashboard/monitor(ing)에서 트래픽, 알림, 에러, 통계 실시간 확인
- 서버/DB/네트워크 상태, 알림/에러/트래픽 차트, 최근 이벤트 로그 제공
- react-chartjs-2로 실시간 트래픽/알림/에러 차트 시각화
- 실시간 데이터/차트 색상/옵션 커스터마이징 가능

## 6. 데이터/백업/복구 / Data/Backup/Restore
- 주기적 백업, 백업 관리 메뉴 활용
- 데이터 내보내기/복구 기능 제공

## 7. FAQ/도움말 / FAQ/Help
- FAQ.md, /faq, /guide, /help 페이지 참고
- 추가 문의는 개발팀 또는 시스템 관리자에게 연락
- For more, see FAQ.md, /faq, /guide, /help or contact admin/dev team 