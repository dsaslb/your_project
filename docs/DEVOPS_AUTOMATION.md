# 운영/개발 프로세스 자동화(CI/CD) 가이드

## 1. 파이프라인 구조
- scripts/ci_cd_pipeline.py 스크립트 사용
- 주요 함수: build, test, deploy, record_release, run_pipeline
- 빌드 → 테스트 → 배포 → 릴리즈 이력 기록 순서로 자동화

## 2. 사용법
- python scripts/ci_cd_pipeline.py 실행
- 릴리즈 버전별 자동 빌드/테스트/배포/이력 기록

## 3. 테스트 방법
- 스크립트 실행 후 ci_cd_pipeline.log 및 릴리즈 이력 확인
- 테스트 실패 시 파이프라인 중단 및 오류 기록

## 4. FAQ/오류 대응
- 빌드/테스트/배포 오류 발생 시 로그 기록 및 관리자 알림(확장 가능)
- 릴리즈 이력 자동 기록
- 추가 문의: 관리자/개발팀에 문의 