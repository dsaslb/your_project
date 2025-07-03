# 접근성 가이드 (Accessibility Guide)

## 1. aria 속성 적용
- 모든 버튼/입력/카드/알림에 aria-label, aria-live, aria-modal 등 적용
- 실시간 알림/Toast: role="status", aria-live="polite"

## 2. role 속성
- 주요 섹션/카드/알림에 role="status", role="alert", role="dialog" 등 명확히 지정

## 3. 키보드 내비게이션
- tabIndex, Enter/Space 키로 모든 주요 기능 접근 가능
- 포커스 표시(Outline) 명확히 유지

## 4. 색상 대비/다크모드
- 텍스트/배경 대비 4.5:1 이상, 다크모드 지원

## 5. 스크린리더/보조기기
- aria, role, alt, label 등으로 스크린리더 완벽 지원

## 6. 접근성 자동 점검
- Lighthouse, axe-core 등으로 접근성 자동 테스트
- 접근성 오류 발생 시 CI에서 경고/실패 처리

## 7. 참고
- WAI-ARIA, WCAG 2.1, Lighthouse, axe-core 공식 문서 