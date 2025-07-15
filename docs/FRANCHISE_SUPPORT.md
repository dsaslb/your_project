# 본사-지점/프랜차이즈 지원 가이드

## 1. 계층 구조
- 본사/지점 구분, 계층적 정책/리포트 관리
- 예시: 본사(1) → 강남지점(2), 홍대지점(3)

## 2. 정책/리포트 일괄 적용/배포
- 엔드포인트: `/api/franchise/apply_policy` (POST)
- 요청 예시: `{ "policy": "매출 급감 경보" }`
- 예시 응답:
```
{
  "success": true,
  "message": "정책 일괄 적용 완료"
}
```

## 3. 본사/지점 대시보드(지점 목록)
- 엔드포인트: `/api/franchise/branches` (GET)
- 예시 응답:
```
{
  "success": true,
  "branches": [
    {"id": 1, "name": "본사", "parent_id": null, "is_head_office": true},
    {"id": 2, "name": "강남지점", "parent_id": 1, "is_head_office": false}
  ]
}
```

## 4. 협업/Q&A/이슈 공유
- 엔드포인트: `/api/franchise/collaboration` (POST)
- 요청 예시: `{ "type": "Q&A", "content": "지점별 프로모션 문의" }`
- 예시 응답:
```
{
  "success": true,
  "message": "이슈/질문이 공유되었습니다."
}
```

## 5. 테스트 방법
- Postman, curl 등으로 각 API 호출 및 응답 확인
- 정상/이상 케이스 테스트

## 6. 오류 대응/FAQ
- 오류 발생 시 API에서 success=false, error 메시지 반환
- 관리자 로그/알림 자동 기록(확장 가능)
- 추가 문의: 관리자/개발팀에 문의 