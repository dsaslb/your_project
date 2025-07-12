# 플러그인 성능 대시보드 사용법

## 1. 개요
- 플러그인별 CPU/메모리/응답시간 등 실시간 성능 모니터링
- 모니터링 시작/중지, 실시간 알림, 상태/이상 탐지 지원
- 관리자 권한에서 접근 가능

## 2. 접근 방법
- 사이드바 메뉴에서 "플러그인 성능" 클릭
- `/plugin-performance` 경로 직접 접근 가능

## 3. 주요 기능
- 플러그인별 실시간 성능 데이터(그래프/카드) 표시
- 모니터링 시작/중지 버튼
- 실시간 알림/경고 표시
- 플러그인별 상태/재시작/메트릭 API 연동

## 4. API 명세 (백엔드)
- `GET /api/plugins/performance` : 전체 플러그인 성능 데이터
- `GET /api/plugins/status` : 전체 플러그인 상태/알림/모니터링 상태
- `POST /api/plugins/monitoring/start|stop` : 모니터링 시작/중지
- `GET /api/plugin-operations/<plugin_name>/status` : 플러그인별 상태
- `GET /api/plugin-operations/<plugin_name>/metrics` : 플러그인별 메트릭
- `POST /api/plugin-operations/<plugin_name>/restart` : 플러그인 재시작

## 5. 테스트 방법
- `npm run test` : E2E 및 단위 테스트 실행
- 테스트 환경에서 IntersectionObserver, next/link 등은 jest.setup.js에서 mock 처리 필요

## 6. 실시간 모니터링/알림
- 임계치 초과, 오류 발생 시 실시간 알림 표시
- 알림/경고는 대시보드 상단 및 카드에 표시됨

## 7. 기타
- 관리자 권한이 없는 경우 접근 제한
- API 키, 환경 변수 등은 .env 파일에서 관리

---
문의/개선 요청은 GitHub Issue 또는 관리자에게 전달해 주세요. 