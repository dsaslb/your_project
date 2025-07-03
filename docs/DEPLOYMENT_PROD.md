# 운영환경 배포/테스트 가이드 (Production Deployment/Test Guide)

## 1. 배포 자동화
- main 브랜치 push 시 Github Actions로 자동 빌드/배포
- Docker Compose, .env.production 환경변수 사용
- 배포 후 Sentry/Slack 등으로 성공/실패 알림

## 2. 롤백/복구
- 이전 이미지/버전으로 롤백 스크립트 제공
- DB/데이터 백업 및 복구 메뉴 활용

## 3. 접근성/E2E 테스트
- Lighthouse, axe-core 등으로 접근성 자동 점검
- Playwright, Cypress 등으로 E2E 시나리오 테스트
- CI에서 테스트 실패 시 배포 중단

## 4. 운영환경 체크리스트
- 환경변수/비밀키 분리, DEBUG=False, 로그/보안 정책 적용
- 실시간 모니터링, 알림, 장애 대응 메뉴 확인

## 5. 참고
- DEPLOYMENT.md, ACCESSIBILITY.md, OPERATOR_MANUAL.md 