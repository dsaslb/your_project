# 레스토랑 통합 관리 시스템

## 프로젝트 개요
- 실시간 업무/통계/알림/혁신 기능을 통합한 레스토랑 관리 플랫폼
- 관리자/직원/운영자 권한별 맞춤 대시보드, 체크리스트, QSC, 실시간 모니터링 등 제공

## 주요 기능
- 대시보드, 스케줄, 직원, 발주, 재고, 알림/공지, 관리자 기능
- 실시간 알림(SSE), 상태/통계/차트, 모바일/PC 반응형, 자동화/테스트/배포
- 혁신 아이디어방(체크리스트, QSC, 주방 모니터링, 조리 예상시간 등)

## 설치/실행
1. 의존성 설치
   - 프론트: `cd your_program_frontend && npm install`
   - 백엔드: `pip install -r requirements.txt`
2. 개발 서버 실행
   - 프론트: `npm run dev`
   - 백엔드: `flask run`
3. 통합 실행: `docker-compose up --build`

## 개발/운영 가이드
- 환경변수: `.env.development`, `.env.production` 참고
- CI/CD: Github Actions, Docker, 배포 스크립트 자동화
- 로그/모니터링: logrotate, Sentry/Slack 연동
- 온보딩/FAQ/운영매뉴얼: `docs/ONBOARDING_GUIDE.md`, `FAQ.md`, `OPERATOR_MANUAL.md`

## FAQ
- Q: 배포/테스트 자동화는 어떻게?
  - A: Github Actions, Docker, 배포 스크립트로 자동화
- Q: 실시간 알림/상태 반영은?
  - A: SSE, NotificationSystem, 실시간 상태/통계/차트 연동
- Q: 운영환경 분리는?
  - A: .env 파일로 개발/운영 환경 분리

## 문의/기여
- 운영자/개발팀에 문의, PR/이슈 환영 
