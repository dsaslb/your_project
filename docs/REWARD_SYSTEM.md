# 복지/참여/보상 시스템 가이드

## 1. 건강설문/피드백
- 설문 제출: `/api/reward/survey` (POST)
- 피드백 제출: `/api/reward/feedback` (POST)
- 예시 응답:
```
{
  "success": true,
  "message": "설문이 제출되었습니다."
}
```

## 2. 포인트/리워드 지급
- 엔드포인트: `/api/reward/reward` (POST)
- 예시 응답:
```
{
  "success": true,
  "message": "포인트/리워드가 지급되었습니다."
}
```

## 3. 이벤트/쿠폰 발급
- 엔드포인트: `/api/reward/event` (POST)
- 예시 응답:
```
{
  "success": true,
  "message": "이벤트/쿠폰이 발급되었습니다."
}
```

## 4. 테스트 방법
- Postman, curl 등으로 각 API 호출 및 응답 확인
- 정상/이상 케이스 테스트

## 5. 오류 대응/FAQ
- 오류 발생 시 API에서 success=false, error 메시지 반환
- 관리자 로그/알림 자동 기록(확장 가능)
- 추가 문의: 관리자/개발팀에 문의 