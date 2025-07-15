# 외부 시스템 연동/감성분석 가이드

## 1. POS 연동
- 엔드포인트: `/api/integration/pos` (POST)
- 요청 예시: `{ "data": ... }`
- 예시 응답:
```
{
  "success": true,
  "message": "POS 연동 성공",
  "synced_at": "2024-06-10T12:00:00"
}
```

## 2. 회계 연동
- 엔드포인트: `/api/integration/accounting` (POST)
- 요청 예시: `{ "data": ... }`
- 예시 응답:
```
{
  "success": true,
  "message": "회계 연동 성공",
  "synced_at": "2024-06-10T12:00:00"
}
```

## 3. 리뷰 플랫폼 연동 및 감성분석
- 엔드포인트: `/api/integration/review` (POST)
- 요청 예시: `{ "data": ... }`
- 예시 응답:
```
{
  "success": true,
  "reviews": [ ... ],
  "sentiment": { "positive": 2, "negative": 1, "neutral": 0, "avg_score": 3.67 },
  "synced_at": "2024-06-10T12:00:00"
}
```

## 4. 테스트 방법
- Postman, curl 등으로 각 API 호출 및 응답 확인
- 정상/이상 케이스 테스트

## 5. 오류 대응/FAQ
- 오류 발생 시 API에서 success=false, error 메시지 반환
- 관리자 로그/알림 자동 기록(확장 가능)
- 추가 문의: 관리자/개발팀에 문의 