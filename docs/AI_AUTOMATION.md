# AI·자동화 기반 운영 고도화 가이드

## 1. 통합 데이터 대시보드
- 엔드포인트: `/api/ai/automation/dashboard`
- 매출, 직원, 재고, 고객, KPI 등 통합 데이터 제공
- 예시 응답:
```
{
  "success": true,
  "dashboard": {
    "sales": 15000000,
    "staff": 12,
    "inventory": 85,
    "customer": 110,
    "kpi": {"revenue_growth": 0.12, "order_growth": 0.08, "customer_growth": 0.09},
    "last_updated": "2024-06-10T12:00:00"
  }
}
```

## 2. GPT 기반 자동 리포트/경보/개선점 추천
- 엔드포인트: `/api/ai/automation/gpt_report` (POST)
- 요청 예시: `{ "type": "summary" }`
- 예시 응답:
```
{
  "success": true,
  "report": {
    "summary": "이번 달 매출은 전월 대비 12% 증가...",
    "alerts": ["재고 부족 품목 2건"],
    "recommendations": ["A상품 발주량 증대"]
  },
  "type": "summary"
}
```

## 3. KPI 실시간 모니터링/알림
- 엔드포인트: `/api/ai/automation/kpi_monitor`
- 예시 응답:
```
{
  "success": true,
  "kpi": {
    "revenue": 18000000,
    "orders": 1500,
    "customer_satisfaction": 4.5,
    "alert": "정상"
  },
  "checked_at": "2024-06-10T12:00:00"
}
```

## 4. 테스트 방법
- Postman, curl 등으로 각 API 호출 및 응답 확인
- 정상/이상 케이스 테스트

## 5. 오류 대응/FAQ
- 오류 발생 시 API에서 success=false, error 메시지 반환
- 관리자 로그/알림 자동 기록
- 추가 문의: 관리자/개발팀에 문의 