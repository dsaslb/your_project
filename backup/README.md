# 💾 데이터 백업 시스템

퀀텀 비즈니스 관리 시스템의 데이터 백업 및 복구 모듈입니다. 자동 백업, 스케줄링, 복구 등의 기능을 제공합니다.

## 주요 기능

### 🔄 자동 백업 관리
- **스케줄링된 백업**: 매일, 매주, 매월 자동 백업
- **백업 유형**: 전체 백업 및 증분 백업 지원
- **압축 및 암호화**: ZIP 압축 및 선택적 암호화
- **체크섬 검증**: MD5 체크섬을 통한 데이터 무결성 검증

### 📁 백업 저장소 관리
- **로컬 저장소**: 로컬 디렉토리에 백업 파일 저장
- **보존 정책**: 설정 가능한 백업 보존 기간 (기본 90일)
- **용량 관리**: 자동 오래된 백업 정리
- **중복 제거**: 효율적인 저장 공간 활용

### 🔧 복구 시스템
- **시점 복구**: 특정 시점의 백업에서 복구
- **선택적 복구**: 특정 파일/폴더만 복구 가능
- **복구 검증**: 복구 후 데이터 무결성 확인
- **복구 테스트**: 백업 파일의 복구 가능성 테스트

### 📊 백업 모니터링
- **실시간 상태**: 백업 작업의 실시간 진행 상황
- **통계 대시보드**: 백업 성공률, 크기, 빈도 등 통계
- **알림 시스템**: 백업 실패 시 자동 알림
- **로그 관리**: 상세한 백업 로그 기록

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r backup/requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
BACKUP_DIR=./backups
MAX_BACKUPS=30
COMPRESSION_LEVEL=6
ENCRYPT_BACKUPS=true
RETENTION_DAYS=90
AUTO_BACKUP_ENABLED=true
BACKUP_SCHEDULE=daily
BACKUP_TIME=02:00
```

### 3. 백업 시스템 초기화
```python
from backup.backup_manager import BackupManager, BackupConfig

# 백업 설정
config = BackupConfig(
    backup_dir="./backups",
    max_backups=30,
    compression_level=6,
    encrypt_backups=True,
    retention_days=90,
    auto_backup_enabled=True,
    backup_schedule="daily",
    backup_time="02:00"
)

# 백업 관리자 초기화
backup_manager = BackupManager(config)
```

## API 엔드포인트

### 백업 작업 관리
- `GET /api/backup/jobs` - 백업 작업 목록 조회
- `POST /api/backup/jobs` - 백업 작업 생성
- `PUT /api/backup/jobs/{job_id}` - 백업 작업 수정
- `DELETE /api/backup/jobs/{job_id}` - 백업 작업 삭제

### 백업 실행 및 테스트
- `POST /api/backup/jobs/{job_id}/run` - 백업 작업 실행
- `POST /api/backup/jobs/{job_id}/test` - 백업 작업 테스트

### 백업 기록 관리
- `GET /api/backup/records` - 백업 기록 조회
- `POST /api/backup/records/{backup_id}/restore` - 백업에서 복구
- `DELETE /api/backup/records/{backup_id}` - 백업 기록 삭제

### 시스템 관리
- `GET /api/backup/stats` - 백업 통계 조회
- `POST /api/backup/scheduler/start` - 스케줄러 시작
- `POST /api/backup/scheduler/stop` - 스케줄러 중지
- `GET /api/backup/scheduler/status` - 스케줄러 상태 조회
- `POST /api/backup/cleanup` - 오래된 백업 정리
- `GET /api/backup/health` - 백업 시스템 상태 확인

## 사용 예시

### 백업 작업 생성
```javascript
const response = await fetch('/api/backup/jobs', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: '데이터베이스 백업',
    source_paths: ['/data/database', '/config'],
    destination: '/backups/database',
    schedule: 'daily'
  })
});
```

### 백업 실행
```javascript
const response = await fetch('/api/backup/jobs/job-id/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    backup_type: 'full'
  })
});
```

### 백업에서 복구
```javascript
const response = await fetch('/api/backup/records/backup-id/restore', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    destination: '/restore/data'
  })
});
```

### 백업 통계 조회
```javascript
const response = await fetch('/api/backup/stats');
const stats = await response.json();
console.log(`성공률: ${stats.success_rate}%`);
console.log(`총 백업 크기: ${stats.total_size_mb} MB`);
```

## 백업 기능 상세

### 백업 스케줄
- **매일 (daily)**: 매일 지정된 시간에 백업 실행
- **매주 (weekly)**: 매주 지정된 요일과 시간에 백업 실행
- **매월 (monthly)**: 매월 1일 지정된 시간에 백업 실행

### 백업 유형
- **전체 백업 (full)**: 모든 데이터를 포함한 완전한 백업
- **증분 백업 (incremental)**: 변경된 파일만 백업
- **테스트 백업 (test)**: 백업 파일의 무결성 테스트

### 압축 및 보안
- **ZIP 압축**: 기본 압축 레벨 6 (0-9 조정 가능)
- **체크섬 검증**: MD5 해시를 통한 파일 무결성 확인
- **암호화**: 선택적 AES 암호화 지원

### 보존 정책
- **기본 보존 기간**: 90일
- **자동 정리**: 보존 기간이 지난 백업 자동 삭제
- **수동 정리**: 관리자가 수동으로 오래된 백업 정리

## 프론트엔드 통합

### 백업 페이지 접근
```
http://localhost:3000/backup
```

### 주요 기능
- **백업 대시보드**: 실시간 백업 통계 표시
- **작업 관리**: 백업 작업 생성, 수정, 삭제
- **기록 조회**: 백업 실행 기록 및 상태 확인
- **복구 기능**: 백업에서 데이터 복구
- **스케줄러 제어**: 자동 백업 스케줄러 시작/중지

## 모니터링 및 알림

### 백업 성공률 계산
- 성공한 백업: +1점
- 실패한 백업: -1점
- 진행 중인 백업: 0점

### 권장 백업 성공률
- **95-100%**: 우수
- **85-94%**: 양호
- **70-84%**: 주의
- **0-69%**: 위험

### 알림 조건
- 백업 실패 시 즉시 알림
- 성공률이 85% 미만일 때 경고
- 디스크 공간 부족 시 경고
- 백업 파일 손상 시 경고

## 개발 가이드라인

### 새로운 백업 기능 추가
1. `BackupManager` 클래스에 메서드 추가
2. API 엔드포인트 구현
3. 프론트엔드 컴포넌트 개발
4. 테스트 코드 작성

### 백업 작업 추가
```python
job_id = backup_manager.create_backup_job(
    name="사용자 정의 백업",
    source_paths=["/path/to/source"],
    destination="/path/to/destination",
    schedule="daily"
)
```

### 백업 이벤트 로깅
```python
backup_manager.log_backup_event(
    job_id=job_id,
    event_type='backup_started',
    description='백업 작업 시작',
    severity='info'
)
```

## 문제 해결

### 일반적인 문제
1. **백업 실패**: 소스 경로 존재 여부 확인
2. **용량 부족**: 디스크 공간 확인 및 정리
3. **권한 오류**: 파일 접근 권한 확인
4. **스케줄러 중지**: 스케줄러 상태 확인

### 로그 확인
```bash
# 백업 로그
tail -f logs/backup.log

# 시스템 로그
tail -f logs/system.log
```

### 성능 최적화
- 압축 레벨 조정 (높을수록 압축률 증가, 속도 감소)
- 백업 시간대 조정 (시스템 부하가 적은 시간)
- 증분 백업 활용 (전체 백업 대비)
- 병렬 백업 작업 제한

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 