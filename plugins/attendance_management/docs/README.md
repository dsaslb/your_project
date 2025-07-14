# 출퇴근 관리 시스템

## 개요

출퇴근 관리 시스템은 직원별 출근/퇴근/지각/초과근무 기록, 통계, 알림 관리 기능을 제공하는 종합 출퇴근 관리 모듈입니다.

## 주요 기능

### 1. 출퇴근 관리
- **출근 체크인**: 직원 출근 시간 기록
- **퇴근 체크아웃**: 직원 퇴근 시간 기록
- **지각 감지**: 설정된 출근 시간 기준 지각 여부 자동 판단
- **초과근무 계산**: 기본 근무시간 초과 시 자동 계산

### 2. 통계 및 리포트
- **실시간 통계**: 현재 출근 현황 실시간 모니터링
- **기간별 리포트**: 지정 기간 출근 데이터 분석
- **직원별 통계**: 개별 직원 출근 패턴 분석
- **팀/매장/브랜드별 통계**: 계층별 출근 현황 분석

### 3. 알림 시스템
- **지각 알림**: 지각 발생 시 관리자에게 자동 알림
- **초과근무 알림**: 초과근무 발생 시 관련자에게 알림
- **결근 알림**: 출근하지 않은 직원에 대한 알림

### 4. 권한 관리
- **계층별 접근 제어**: 브랜드/매장/직원 계층별 권한 분기
- **기능별 권한**: 출근 기록, 조회, 수정, 내보내기 권한 관리

## 설치 및 설정

### 1. 모듈 설치
```bash
# 마켓플레이스에서 모듈 설치
curl -X POST http://localhost:5000/api/marketplace/modules/attendance_management/install
```

### 2. 설정 파일
```json
{
  "default_work_hours": 8,
  "late_threshold_minutes": 15,
  "overtime_threshold_hours": 8,
  "notification_enabled": true,
  "auto_calculate_overtime": true
}
```

### 3. 권한 설정
```json
{
  "admin": ["view_all", "edit_all", "delete_all", "export_data"],
  "brand_manager": ["view_brand", "edit_brand", "export_brand"],
  "store_manager": ["view_store", "edit_store", "export_store"],
  "supervisor": ["view_team", "edit_team"],
  "employee": ["view_own", "check_in", "check_out"]
}
```

## API 사용법

### 1. 출근 체크인
```bash
curl -X POST http://localhost:5000/api/attendance/check-in \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp_001",
    "location": "main_office"
  }'
```

### 2. 퇴근 체크아웃
```bash
curl -X POST http://localhost:5000/api/attendance/check-out \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp_001"
  }'
```

### 3. 출근 리포트 조회
```bash
curl "http://localhost:5000/api/attendance/report/employee?user_id=emp_001&start_date=2024-01-01&end_date=2024-01-31"
```

### 4. 통계 조회
```bash
curl "http://localhost:5000/api/attendance/stats?user_id=emp_001&user_type=employee"
```

### 5. 데이터 내보내기
```bash
curl "http://localhost:5000/api/attendance/export?user_id=emp_001&user_type=admin&format=excel&start_date=2024-01-01&end_date=2024-01-31"
```

## 프론트엔드 컴포넌트

### 1. AttendanceDashboard
출퇴근 관리 메인 대시보드
```typescript
import { AttendanceDashboard } from '@/components/attendance/AttendanceDashboard';

<AttendanceDashboard />
```

### 2. AttendanceForm
출퇴근 기록 입력 폼
```typescript
import { AttendanceForm } from '@/components/attendance/AttendanceForm';

<AttendanceForm onCheckIn={handleCheckIn} onCheckOut={handleCheckOut} />
```

### 3. AttendanceReport
출근 리포트 표시
```typescript
import { AttendanceReport } from '@/components/attendance/AttendanceReport';

<AttendanceReport startDate="2024-01-01" endDate="2024-01-31" />
```

### 4. AttendanceStats
출근 통계 표시
```typescript
import { AttendanceStats } from '@/components/attendance/AttendanceStats';

<AttendanceStats userId="emp_001" userType="employee" />
```

## 데이터 구조

### AttendanceRecord
```typescript
interface AttendanceRecord {
  id: string;
  employee_id: string;
  date: string;
  check_in_time?: string;
  check_out_time?: string;
  work_hours?: number;
  is_late: boolean;
  overtime_hours: number;
  status: 'pending' | 'checked_in' | 'checked_out';
  location: string;
  notes?: string;
}
```

### AttendanceStats
```typescript
interface AttendanceStats {
  total_records: number;
  present_count: number;
  late_count: number;
  absent_count: number;
  average_work_hours: number;
  on_time_rate: number;
  total_overtime: number;
  period: string;
}
```

## 모듈 상태 관리

### 상태 정의
- **active**: 모듈이 정상적으로 작동 중
- **inactive**: 모듈이 비활성화됨
- **maintenance**: 모듈이 유지보수 중
- **error**: 모듈에 오류가 발생함

### 상태 확인
```bash
curl "http://localhost:5000/api/modules/attendance_management/status"
```

### 모듈 활성화/비활성화
```bash
# 활성화
curl -X POST http://localhost:5000/api/modules/attendance_management/toggle

# 비활성화
curl -X DELETE http://localhost:5000/api/modules/attendance_management/uninstall
```

## 알림 설정

### 알림 유형
1. **지각 알림**: 출근 시간 초과 시
2. **초과근무 알림**: 기본 근무시간 초과 시
3. **결근 알림**: 출근하지 않은 직원
4. **주간 리포트**: 주간 출근 현황 요약

### 알림 채널
- 이메일
- 푸시 알림
- SMS
- 웹 알림

## AI 연동

### 예측 기능
- **출근 패턴 예측**: 직원별 출근 시간 예측
- **지각 위험도 분석**: 지각 가능성 높은 직원 식별
- **근무 효율성 분석**: 근무 패턴과 성과 연관성 분석

### AI 설정
```json
{
  "ai_analytics": true,
  "prediction_enabled": true,
  "pattern_analysis": true,
  "efficiency_analysis": true
}
```

## 테스트

### 단위 테스트
```bash
python -m pytest tests/test_attendance_api.py
python -m pytest tests/test_attendance_service.py
```

### 통합 테스트
```bash
python -m pytest tests/integration/test_attendance_flow.py
```

## 성능 최적화

### 캐싱
- Redis를 사용한 출근 데이터 캐싱
- 통계 데이터 캐싱 (5분 TTL)
- 사용자 권한 캐싱 (1시간 TTL)

### 데이터베이스 최적화
- 인덱스 설정: employee_id, date, status
- 파티셔닝: 월별 파티셔닝
- 아카이빙: 1년 이상 데이터 자동 아카이빙

## 모니터링

### 메트릭
- API 응답 시간
- 데이터베이스 쿼리 성능
- 동시 사용자 수
- 오류율

### 로깅
- 출근/퇴근 로그
- 권한 검증 로그
- 시스템 오류 로그

## 문제 해결

### 일반적인 문제
1. **출근 기록 중복**: 같은 날짜 중복 체크 로직 확인
2. **권한 오류**: 사용자 권한 설정 확인
3. **데이터 불일치**: 캐시 초기화 및 데이터 동기화

### 로그 확인
```bash
tail -f logs/attendance.log
```

## 업데이트

### 버전 업데이트
```bash
# 마켓플레이스에서 최신 버전 확인
curl "http://localhost:5000/api/marketplace/modules/attendance_management"

# 업데이트 실행
curl -X POST http://localhost:5000/api/modules/attendance_management/update
```

## 라이선스

이 모듈은 MIT 라이선스 하에 배포됩니다.

## 지원

- **문서**: `/docs/attendance_management`
- **지원**: `/support/attendance_management`
- **데모**: `/marketplace/demo/attendance_management`

## 기여

버그 리포트나 기능 요청은 GitHub Issues를 통해 제출해주세요. 