# ⚙️ 시스템 설정 관리

퀀텀 비즈니스 관리 시스템의 중앙화된 설정 관리 모듈입니다. 애플리케이션 설정, 환경 변수 관리, 설정 백업 및 복원 등의 기능을 제공합니다.

## 주요 기능

### 🔧 설정 관리
- **중앙화된 설정 관리**: 모든 애플리케이션 설정을 한 곳에서 관리
- **카테고리별 분류**: 시스템, 데이터베이스, API, 보안 등 카테고리별 설정 분류
- **실시간 설정 변경**: 설정 값 변경 및 즉시 적용
- **설정 검증**: 데이터 타입 및 규칙 기반 설정 값 검증

### 🛡️ 보안 기능
- **민감한 정보 보호**: 비밀번호, API 키 등 민감한 설정 암호화
- **접근 제어**: 권한 기반 설정 접근 관리
- **변경 이력 추적**: 모든 설정 변경 사항 로깅
- **감사 로그**: 설정 변경에 대한 상세한 감사 정보

### 📊 모니터링 및 관리
- **설정 통계**: 설정 현황 및 사용 통계 제공
- **변경 이력**: 설정 변경 내역 조회 및 분석
- **백업 및 복원**: 설정 백업 생성 및 복원 기능
- **환경별 관리**: 개발/테스트/운영 환경별 설정 분리

### 🔄 백업 및 복원
- **자동 백업**: 정기적인 설정 백업 생성
- **백업 관리**: 백업 파일 관리 및 정리
- **복원 기능**: 백업에서 설정 복원
- **백업 검증**: 백업 파일 무결성 검증

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r settings/requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
SETTINGS_DATA_DIR=data/settings
SETTINGS_BACKUP_DIR=backups
SETTINGS_MAX_BACKUPS=10
SETTINGS_AUTO_BACKUP=true
SETTINGS_VALIDATE_ON_SAVE=true
SETTINGS_ENCRYPT_SENSITIVE=true
```

### 3. 설정 시스템 초기화
```python
from settings.settings_manager import SettingsManager, SettingsConfig

# 설정 관리자 초기화
config = SettingsConfig(
    data_dir="data/settings",
    config_file="config.json",
    env_file=".env",
    backup_dir="backups",
    max_backups=10,
    auto_backup=True,
    validate_on_save=True,
    encrypt_sensitive=True
)

settings_manager = SettingsManager(config)
```

## API 엔드포인트

### 시스템 상태
- `GET /api/settings/health` - 설정 시스템 상태 확인
- `GET /api/settings/stats` - 설정 통계 조회

### 설정 관리
- `GET /api/settings/settings` - 모든 설정 조회
- `GET /api/settings/settings/<key>` - 특정 설정 조회
- `PUT /api/settings/settings/<key>` - 설정 값 변경
- `POST /api/settings/settings` - 새 설정 생성
- `POST /api/settings/settings/<key>/validate` - 설정 값 검증

### 카테고리 관리
- `GET /api/settings/categories` - 설정 카테고리 조회

### 변경 이력
- `GET /api/settings/changes` - 설정 변경 이력 조회

### 백업 관리
- `GET /api/settings/backup` - 백업 목록 조회
- `POST /api/settings/backup` - 백업 생성
- `POST /api/settings/backup/<backup_id>/restore` - 백업 복원

### 도구
- `GET /api/settings/export` - 설정 내보내기 (JSON/YAML)
- `POST /api/settings/import` - 설정 가져오기
- `GET /api/settings/env-file` - 환경 변수 파일 생성

## 사용 예시

### 설정 값 조회
```javascript
const response = await fetch('/api/settings/settings');
const settings = await response.json();

// 특정 설정 조회
const setting = await fetch('/api/settings/settings/app_name');
```

### 설정 값 변경
```javascript
const response = await fetch('/api/settings/settings/debug_mode', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    value: true,
    changed_by: 'admin',
    change_reason: '디버그 모드 활성화'
  })
});
```

### 설정 백업 생성
```javascript
const response = await fetch('/api/settings/backup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: '프로덕션 설정 백업',
    description: '프로덕션 환경 설정 백업',
    created_by: 'admin'
  })
});
```

### 설정 내보내기
```javascript
// JSON 형식으로 내보내기
const response = await fetch('/api/settings/export?format=json');
const data = await response.json();

// 파일 다운로드
const blob = new Blob([data.content], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'settings.json';
a.click();
```

## 설정 카테고리

### 시스템 설정 (system)
- `app_name`: 애플리케이션 이름
- `app_version`: 애플리케이션 버전
- `debug_mode`: 디버그 모드 활성화
- `timezone`: 기본 시간대
- `language`: 기본 언어

### 데이터베이스 설정 (database)
- `db_host`: 데이터베이스 호스트
- `db_port`: 데이터베이스 포트
- `db_name`: 데이터베이스 이름
- `db_user`: 데이터베이스 사용자
- `db_password`: 데이터베이스 비밀번호
- `db_pool_size`: 연결 풀 크기

### API 설정 (api)
- `api_host`: API 서버 호스트
- `api_port`: API 서버 포트
- `api_timeout`: API 요청 타임아웃
- `cors_origins`: CORS 허용 오리진
- `rate_limit`: API 요청 제한

### 보안 설정 (security)
- `jwt_secret`: JWT 시크릿 키
- `jwt_expiry_hours`: JWT 토큰 만료 시간
- `password_min_length`: 최소 비밀번호 길이
- `session_timeout`: 세션 타임아웃
- `max_login_attempts`: 최대 로그인 시도 횟수

### 로깅 설정 (logging)
- `log_level`: 로그 레벨
- `log_file`: 로그 파일 경로
- `log_max_size`: 로그 파일 최대 크기
- `log_backup_count`: 로그 백업 파일 수
- `log_format`: 로그 포맷

### 이메일 설정 (email)
- `smtp_host`: SMTP 서버 호스트
- `smtp_port`: SMTP 서버 포트
- `smtp_user`: SMTP 사용자
- `smtp_password`: SMTP 비밀번호
- `email_from`: 발신자 이메일

## 프론트엔드 통합

### 설정 페이지 접근
```
http://localhost:3000/system-settings
```

### 주요 기능
- **설정 조회**: 카테고리별 설정 목록 조회
- **설정 편집**: 설정 값 변경 및 검증
- **변경 이력**: 설정 변경 내역 모니터링
- **설정 내보내기**: JSON/YAML 형식으로 설정 내보내기
- **민감한 정보 관리**: 민감한 설정 값 보호

### 설정 관리 컴포넌트
```javascript
// 설정 조회
const loadSettings = async () => {
  const response = await fetch('/api/settings/settings');
  const settings = await response.json();
  return settings;
};

// 설정 변경
const updateSetting = async (key, value, reason) => {
  const response = await fetch(`/api/settings/settings/${key}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      value,
      changed_by: 'admin',
      change_reason: reason
    })
  });
  return response.json();
};

// 설정 통계
const loadStats = async () => {
  const response = await fetch('/api/settings/stats');
  const stats = await response.json();
  return stats;
};
```

## 설정 검증 규칙

### 데이터 타입별 검증
- **string**: 문자열 타입 검증
- **number**: 숫자 타입 및 범위 검증
- **boolean**: 불린 타입 검증
- **json**: JSON 형식 검증
- **array**: 배열 타입 검증

### 검증 규칙 예시
```python
# 숫자 범위 검증
validation_rules = {
    'min': 1,
    'max': 100
}

# 문자열 길이 검증
validation_rules = {
    'min_length': 3,
    'max_length': 50
}

# 패턴 검증
validation_rules = {
    'pattern': r'^[a-zA-Z0-9_]+$'
}

# 열거형 검증
validation_rules = {
    'enum': ['DEBUG', 'INFO', 'WARNING', 'ERROR']
}
```

## 백업 및 복원

### 백업 생성
```python
# 수동 백업 생성
backup_id = settings_manager.create_backup(
    name="수동 백업",
    description="중요 설정 변경 전 백업",
    created_by="admin"
)
```

### 백업 복원
```python
# 백업 복원 (민감한 정보 제외)
success = settings_manager.restore_backup(backup_id, restore_sensitive=False)

# 백업 복원 (민감한 정보 포함)
success = settings_manager.restore_backup(backup_id, restore_sensitive=True)
```

### 백업 관리
- **자동 백업**: 설정 변경 시 자동 백업 생성
- **백업 정리**: 오래된 백업 파일 자동 삭제
- **백업 검증**: 백업 파일 체크섬 검증
- **백업 메타데이터**: 백업 생성 정보 및 설명 관리

## 환경 변수 관리

### 환경 변수 파일 생성
```python
# .env 파일 생성
env_content = settings_manager.generate_env_file()
```

### 생성되는 환경 변수 예시
```bash
# 퀀텀 비즈니스 관리 시스템 환경 변수
# 생성일: 2024-01-15 10:30:00

APP_NAME=퀀텀 비즈니스 관리 시스템
APP_VERSION=1.0.0
DEBUG_MODE=false
TIMEZONE=Asia/Seoul
LANGUAGE=ko
DB_HOST=localhost
DB_PORT=5432
DB_NAME=quantum_business
DB_USER=***
DB_PASSWORD=***
API_HOST=localhost
API_PORT=5000
JWT_SECRET=***
```

## 모니터링 및 알림

### 설정 통계
- 총 설정 항목 수
- 카테고리별 설정 분포
- 민감한 설정 항목 수
- 필수 설정 항목 수
- 오늘 변경된 설정 수
- 백업 파일 수

### 변경 이력 모니터링
- 설정 변경 시점
- 변경자 정보
- 변경 사유
- 이전 값과 새 값
- 카테고리별 변경 추이

### 알림 설정
- 중요 설정 변경 알림
- 민감한 설정 접근 알림
- 백업 생성/복원 알림
- 설정 검증 실패 알림

## 개발 가이드라인

### 새로운 설정 추가
```python
# 설정 생성
setting_key = settings_manager.create_setting(
    key='custom_setting',
    value='default_value',
    category='custom',
    description='사용자 정의 설정',
    data_type='string',
    is_sensitive=False,
    is_required=False,
    default_value='default_value',
    validation_rules={'min_length': 1, 'max_length': 100}
)
```

### 설정 값 검증
```python
# 사용자 정의 검증
validation_result = settings_manager.validate_setting_value(
    key='custom_setting',
    value='test_value',
    data_type='string',
    validation_rules={'pattern': r'^[a-z]+$'}
)

if validation_result['valid']:
    print("검증 성공")
else:
    print(f"검증 실패: {validation_result['message']}")
```

### 설정 변경 이벤트 처리
```python
# 설정 변경 시 추가 작업
def on_setting_changed(setting_key, old_value, new_value):
    # 로그 기록
    logger.info(f"설정 변경: {setting_key} = {new_value}")
    
    # 캐시 무효화
    cache.invalidate(f"setting:{setting_key}")
    
    # 알림 전송
    send_notification(f"설정 {setting_key}이(가) 변경되었습니다")
```

## 문제 해결

### 일반적인 문제
1. **설정 값 검증 실패**: 데이터 타입 및 검증 규칙 확인
2. **민감한 정보 노출**: 민감한 설정 표시 여부 확인
3. **백업 복원 실패**: 백업 파일 무결성 및 권한 확인
4. **설정 변경 이력 누락**: 데이터베이스 연결 및 로깅 설정 확인

### 로그 확인
```bash
# 설정 시스템 로그
tail -f logs/settings.log

# 설정 변경 이력
tail -f logs/settings_changes.log
```

### 성능 최적화
- 설정 캐싱 전략 적용
- 백업 파일 압축 및 정리
- 데이터베이스 인덱스 최적화
- 설정 변경 배치 처리

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 