# 자동 점검/리포트/알림 스케줄링 예시

## 1. 리눅스/유닉스: cron(크론) 활용

### (1) 매일 새벽 2시 자동 점검
```
0 2 * * * /usr/bin/python /path/to/scripts/auto_security_check.py
```

### (2) 매주 월요일 오전 8시 주간 리포트 생성 및 알림
```
0 8 * * 1 /usr/bin/python /path/to/scripts/auto_weekly_report.py && /usr/bin/python /path/to/scripts/auto_report_notify.py /path/to/weekly_report_$(date +\%Y-\%m-\%d).csv
```

### (3) 크론 등록 방법
- `crontab -e` 명령어로 편집
- 위 예시 줄을 추가 후 저장

## 2. 윈도우: 작업 스케줄러 활용

### (1) 작업 스케줄러 등록 예시
- "작업 만들기" → 트리거(매일/매주) → 동작(프로그램 시작)
- 프로그램/스크립트: `python`
- 인수 추가: `C:\your_program\scripts\auto_security_check.py`

### (2) 참고
- Python 경로, 스크립트 경로를 환경에 맞게 지정
- 관리자 권한으로 실행 필요시 "가장 높은 권한으로 실행" 체크

## 3. 기타
- 점검/리포트/알림 스크립트는 언제든 수동 실행도 가능
- 스케줄링 결과는 로그/이메일/슬랙 등으로 확인 