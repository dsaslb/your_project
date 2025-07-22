# 합 대시보드 (Comprehensive Dashboard)

## 개요

합 대시보드는 모든 모니터링 데이터를 통합하여 제공하는 종합적인 시스템 모니터링 대시보드입니다. 실시간 시스템 상태, 성능 메트릭, 사용자 활동, 알림 등을 한 곳에서 확인할 수 있습니다.

## 주요 기능

### 1. 시스템 건강도 모니터링
- **실시간 시스템 상태**: CPU, 메모리, 디스크, 네트워크 사용률
- **시스템 건강도 점수**: 0-100점 스케일로 시스템 전반적인 상태 표시
- **상태 레벨**: 우수(80-100), 양호(60-79), 주의(40-59), 위험(0-39)

### 2. 실시간 메트릭 대시보드
- **CPU 사용률**: 실시간 CPU 사용률 모니터링
- **메모리 사용률**: 메모리 사용량 및 가용성 확인
- **활성 사용자**: 현재 접속 중인 사용자 수
- **응답 시간**: 시스템 응답 시간 측정

### 3. 알림 관리
- **알림 요약**: 긴급, 경고, 정보 알림 개수 표시
- **실시간 알림 목록**: 최근 발생한 알림들의 상세 정보
- **알림 필터링**: 심각도별, 시간별 알림 필터링

### 4. 데이터베이스 및 네트워크 상태
- **데이터베이스 연결 상태**: DB 연결 상태 및 응답 시간
- **네트워크 상태**: 대역폭 사용률, 패킷 손실률, 지연 시간

### 5. 고급 분석 기능
- **트렌드 분석**: 시간별 시스템 메트릭 트렌드
- **사용자 활동 분석**: 사용자 행동 패턴 및 세션 분석
- **성능 병목 분석**: 시스템 성능 병목 지점 식별
- **예측 분석**: 향후 시스템 상태 예측

## 접근 방법

### URL
```
/admin/comprehensive
```

### 권한 요구사항
- 관리자 권한 (`admin` 역할)
- 모니터링 권한 (`monitor` 역할)

## API 엔드포인트

### 1. 개요 데이터
```
GET /admin/comprehensive/api/overview
```
전체 시스템 개요 데이터를 반환합니다.

### 2. 트렌드 데이터
```
GET /admin/comprehensive/api/trends?hours=24
```
시간별 트렌드 분석 데이터를 반환합니다.

### 3. 실시간 데이터
```
GET /admin/comprehensive/api/real-time
```
실시간 시스템 메트릭을 반환합니다.

### 4. 분석 데이터
```
GET /admin/comprehensive/api/analytics?days=7
```
고급 분석 데이터를 반환합니다.

### 5. 알림 설정
```
GET /admin/comprehensive/api/notifications
```
알림 설정 및 상태 정보를 반환합니다.

## 설정 관리

### 설정 페이지 접근
```
/admin/comprehensive/settings
```

### 설정 항목

#### 1. 모니터링 설정
- **실시간 모니터링**: 모니터링 활성화/비활성화
- **모니터링 간격**: 데이터 수집 주기 (5-300초)
- **데이터 보관 기간**: 메트릭 데이터 보관 기간 (1-365일)
- **임계값 설정**: CPU, 메모리 경고/위험 임계값

#### 2. 알림 설정
- **알림 채널**: 이메일, 슬랙, 웹훅 알림 설정
- **알림 규칙**: 긴급/경고/정보 알림 활성화
- **알림 반복**: 알림 반복 간격 설정

#### 3. 캐시 설정
- **캐시 활성화**: 캐시 시스템 활성화/비활성화
- **TTL 설정**: 기본 캐시 만료 시간
- **캐시 크기**: 최대 캐시 크기 제한
- **정리 정책**: LRU 정책 및 자동 정리 설정

#### 4. 보안 설정
- **IP 화이트리스트**: 허용된 IP 주소 설정
- **2단계 인증**: 2FA 활성화
- **감사 로그**: 시스템 접근 로그 설정

## 데이터 내보내기

### 지원 형식
- **JSON**: 구조화된 데이터 내보내기
- **CSV**: 스프레드시트 호환 형식

### 내보내기 옵션
```
GET /admin/comprehensive/export?format=json&type=all&days=7
```

- `format`: 내보내기 형식 (json, csv)
- `type`: 데이터 타입 (all, metrics, alerts, users)
- `days`: 내보낼 데이터 기간

## 모니터링 데이터베이스

### 데이터베이스 구조
- **system_metrics**: 시스템 메트릭 데이터
- **user_activity**: 사용자 활동 데이터
- **performance_alerts**: 성능 알림 데이터

### 데이터 보관 정책
- 기본 보관 기간: 30일
- 자동 정리: 설정 가능
- 백업: 정기적 백업 권장

## 알림 시스템

### 알림 채널
1. **이메일 알림**
   - SMTP 서버 설정 필요
   - 템플릿 기반 메시지

2. **슬랙 알림**
   - 웹훅 URL 설정
   - 실시간 채널 알림

3. **웹훅 알림**
   - 외부 시스템 연동
   - JSON 페이로드 전송

### 알림 규칙
- **긴급**: 시스템 중단, 심각한 성능 저하
- **경고**: 임계값 초과, 성능 저하
- **정보**: 일반적인 시스템 상태 변경

## 성능 최적화

### 캐싱 전략
- **L1 캐시**: 메모리 기반 빠른 캐시
- **L2 캐시**: Redis 기반 영속 캐시
- **다단계 캐시**: 성능과 안정성 균형

### 데이터 수집 최적화
- **배치 처리**: 효율적인 데이터 수집
- **압축**: 저장 공간 절약
- **인덱싱**: 빠른 데이터 조회

## 보안 고려사항

### 접근 제어
- **역할 기반 접근**: 관리자/모니터링 권한 분리
- **IP 제한**: 허용된 IP에서만 접근
- **세션 관리**: 안전한 세션 처리

### 데이터 보호
- **암호화**: 민감한 데이터 암호화
- **마스킹**: 로그에서 민감 정보 제거
- **감사**: 모든 접근 로그 기록

## 운영 환경 설정

### 프로덕션 환경 권장사항

#### 1. 모니터링 데이터베이스
```bash
# PostgreSQL 권장
CREATE DATABASE monitoring_db;
CREATE USER monitoring_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE monitoring_db TO monitoring_user;
```

#### 2. Redis 설정
```bash
# Redis 설정 파일
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### 3. 로그 관리
```bash
# 로그 로테이션 설정
/var/log/comprehensive_dashboard/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
}
```

#### 4. 백업 전략
```bash
# 자동 백업 스크립트
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump monitoring_db > backup_$DATE.sql
tar -czf backup_$DATE.tar.gz backup_$DATE.sql
rm backup_$DATE.sql
```

### 외부 모니터링 시스템 연동

#### 1. Prometheus 연동
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'comprehensive_dashboard'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
```

#### 2. Grafana 대시보드
- 시스템 메트릭 대시보드
- 알림 대시보드
- 사용자 활동 대시보드

#### 3. Slack 연동
```python
# 슬랙 웹훅 설정
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxx/yyy/zzz"
```

## 문제 해결

### 일반적인 문제

#### 1. 데이터 로드 실패
- 데이터베이스 연결 확인
- 권한 설정 확인
- 로그 파일 확인

#### 2. 알림 전송 실패
- 이메일 서버 설정 확인
- 슬랙 웹훅 URL 확인
- 네트워크 연결 확인

#### 3. 성능 저하
- 캐시 설정 최적화
- 데이터베이스 인덱스 확인
- 리소스 사용량 확인

### 로그 확인
```bash
# 애플리케이션 로그
tail -f /var/log/comprehensive_dashboard/app.log

# 에러 로그
tail -f /var/log/comprehensive_dashboard/error.log

# 모니터링 로그
tail -f /var/log/comprehensive_dashboard/monitoring.log
```

## 개발자 가이드

### 새로운 메트릭 추가
```python
# 1. 메트릭 클래스에 필드 추가
@dataclass
class SystemMetrics:
    new_metric: float

# 2. 수집 로직 구현
def collect_new_metric(self):
    # 메트릭 수집 로직
    pass

# 3. API 엔드포인트 추가
@comprehensive_dashboard_bp.route('/api/new-metric')
def get_new_metric():
    return jsonify({'new_metric': value})
```

### 새로운 알림 타입 추가
```python
# 1. 알림 타입 정의
ALERT_TYPES = {
    'new_alert_type': {
        'severity': 'warning',
        'threshold': 80,
        'message_template': '새로운 알림: {value}'
    }
}

# 2. 알림 생성 로직
def create_new_alert(self, value):
    if value > threshold:
        alert = PerformanceAlert(
            alert_type='new_alert_type',
            severity='warning',
            message=f'새로운 알림: {value}'
        )
        self._save_alert(alert)
```

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 지원

문제가 발생하거나 질문이 있으시면 다음 방법으로 문의해주세요:

- GitHub Issues: [이슈 등록](https://github.com/your-repo/issues)
- 이메일: support@your-company.com
- 문서: [전체 문서](https://docs.your-company.com) 