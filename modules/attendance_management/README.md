# 출퇴근 관리 모듈 (Attendance Management)

## 개요

출퇴근 관리 모듈은 직원별 출근/퇴근/지각/초과근무 기록, 통계, 알림을 관리하는 종합적인 시스템입니다.

## 주요 기능

### 1. 출퇴근 기록 관리
- **출근 기록**: 직원별 출근 시간 기록
- **퇴근 기록**: 직원별 퇴근 시간 기록
- **근무 유형**: 정규, 시급, 파트타임, 인턴 등
- **비고 기능**: 특이사항 기록

### 2. 근태 분석
- **지각 관리**: 설정 가능한 지각 기준
- **조퇴 관리**: 조퇴 여부 자동 판단
- **초과근무 계산**: 자동 초과근무 시간 계산
- **근무 시간 통계**: 일별/월별 근무 시간 분석

### 3. 통계 및 리포트
- **실시간 통계**: 현재 출퇴근 현황
- **월별 통계**: 월간 근태 분석
- **부서별 통계**: 부서별 근태 비교
- **개인별 통계**: 개인 근태 이력

### 4. 알림 시스템
- **지각 알림**: 지각 시 자동 알림
- **조퇴 알림**: 조퇴 시 자동 알림
- **결근 알림**: 결근 시 알림
- **설정 가능**: 알림 간격 및 조건 설정

### 5. 권한 관리
- **관리자**: 전체 직원 관리
- **매장 관리자**: 해당 매장 직원 관리
- **직원**: 본인 출퇴근만 관리

## 설치 및 설정

### 1. 모듈 설치
```bash
# 모듈 파일 복사
cp -r modules/attendance_management /your_program/modules/

# API 등록 확인
# app.py에 블루프린트 등록 확인
```

### 2. 설정 구성
```json
{
  "work_start_time": "09:00",
  "work_end_time": "18:00",
  "late_threshold_minutes": 10,
  "overtime_threshold_hours": 8,
  "auto_notification": true,
  "work_types": ["정규", "시급", "파트타임", "인턴"]
}
```

### 3. 권한 설정
- 관리자: 모든 기능 접근 가능
- 매장 관리자: 해당 매장 직원 관리
- 직원: 본인 출퇴근만 관리

## API 엔드포인트

### 출퇴근 기록
- `POST /api/attendance/clock-in` - 출근 기록
- `POST /api/attendance/clock-out` - 퇴근 기록
- `GET /api/attendance/records` - 출퇴근 기록 조회

### 통계 및 분석
- `GET /api/attendance/statistics` - 통계 조회
- `GET /api/attendance/settings` - 설정 조회
- `PUT /api/attendance/settings` - 설정 업데이트

### 알림
- `GET /api/attendance/notifications` - 알림 조회

### 테스트
- `POST /api/attendance/test-data` - 테스트 데이터 생성

## 사용법

### 1. 출근 기록
```javascript
// 출근 기록
const response = await fetch('/api/attendance/clock-in', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 123,
    work_type: '정규',
    note: '정상 출근'
  })
});
```

### 2. 퇴근 기록
```javascript
// 퇴근 기록
const response = await fetch('/api/attendance/clock-out', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 123,
    note: '정상 퇴근'
  })
});
```

### 3. 통계 조회
```javascript
// 통계 조회
const response = await fetch('/api/attendance/statistics?start_date=2024-01-01&end_date=2024-01-31');
const stats = await response.json();
```

## 연동 시스템

### 1. 알림 모듈
- 지각/조퇴 시 자동 알림 발송
- 설정 가능한 알림 조건

### 2. AI 예측 모듈
- 출퇴근 패턴 분석
- 지각 예측 기능

### 3. 대시보드 모듈
- 실시간 출퇴근 현황 표시
- 통계 위젯 제공

### 4. 사용자 관리 모듈
- 직원 정보 연동
- 권한 기반 접근 제어

## 테스트

### 1. 테스트 데이터 생성
```javascript
// 30일간의 테스트 데이터 생성
const response = await fetch('/api/attendance/test-data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ days: 30 })
});
```

### 2. 기능 테스트
- 출근/퇴근 기록 테스트
- 지각/조퇴 판단 테스트
- 통계 계산 테스트
- 알림 발송 테스트

## 모니터링

### 1. 성능 지표
- API 응답 시간
- 데이터베이스 쿼리 성능
- 동시 사용자 수

### 2. 오류 모니터링
- API 오류 로그
- 데이터 무결성 검사
- 권한 오류 추적

## 보안

### 1. 인증 및 권한
- JWT 토큰 기반 인증
- 역할 기반 접근 제어
- API 엔드포인트 보호

### 2. 데이터 보호
- 개인정보 암호화
- 접근 로그 기록
- 데이터 백업

## 문제 해결

### 1. 일반적인 문제
- **출근 기록 실패**: 권한 확인, 네트워크 연결 확인
- **통계 오류**: 데이터 무결성 검사, 캐시 초기화
- **알림 미발송**: 알림 설정 확인, 서비스 상태 확인

### 2. 로그 확인
```bash
# 애플리케이션 로그 확인
tail -f logs/app.log | grep attendance

# 오류 로그 확인
tail -f logs/error.log | grep attendance
```

## 업데이트 내역

### v1.0.0 (2024-01-01)
- 초기 버전 릴리스
- 기본 출퇴근 기록 기능
- 통계 및 알림 기능
- 테스트 데이터 생성 기능

## 라이선스

이 모듈은 Your Program의 일부로 제공됩니다.

## 지원

기술 지원이 필요한 경우:
- 이슈 트래커: [GitHub Issues](https://github.com/your-program/issues)
- 이메일: support@your-program.com
- 문서: [공식 문서](https://docs.your-program.com) 