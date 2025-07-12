# 관리자/운영자 가이드

## 목차
1. [시스템 개요](#시스템-개요)
2. [플러그인 모니터링 시스템](#플러그인-모니터링-시스템)
3. [실시간 알림 시스템](#실시간-알림-시스템)
4. [고급 모니터링 기능](#고급-모니터링-기능)
5. [문제 대응 가이드](#문제-대응-가이드)
6. [성능 최적화](#성능-최적화)
7. [백업 및 복구](#백업-및-복구)
8. [보안 가이드](#보안-가이드)

---

## 시스템 개요

### 플러그인 기반 아키텍처
- **모듈화된 구조**: 각 기능이 독립적인 플러그인으로 구현
- **동적 로딩**: 필요에 따라 플러그인 활성화/비활성화
- **확장성**: 새로운 기능을 플러그인으로 쉽게 추가

### 모니터링 시스템 구성
- **기본 모니터링**: CPU, 메모리, 응답시간, 에러율 모니터링
- **고급 모니터링**: 상세 메트릭, 트렌드 분석, 패턴 분석
- **실시간 알림**: WebSocket 기반 실시간 알림 시스템

---

## 플러그인 모니터링 시스템

### 1. 모니터링 시작/중지

#### 웹 인터페이스
1. 관리자 대시보드 → 플러그인 모니터링
2. "모니터링 시작" 버튼 클릭
3. 실시간 메트릭 확인

#### 명령줄
```bash
# 모니터링 시작
python scripts/start_plugin_monitoring.py

# 백그라운드 실행
nohup python scripts/start_plugin_monitoring.py > monitoring.log 2>&1 &
```

### 2. 플러그인 등록

#### API를 통한 등록
```bash
curl -X POST http://localhost:5000/api/advanced-monitoring/register-plugin \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "plugin_id": "my_plugin",
    "plugin_name": "내 플러그인"
  }'
```

#### 자동 등록
- 플러그인 디렉토리 감지 시 자동 등록
- `plugins/` 디렉토리 내 플러그인 자동 스캔

### 3. 메트릭 업데이트

#### 자동 업데이트
- 30초마다 자동 메트릭 수집
- 시스템 리소스 모니터링

#### 수동 업데이트
```bash
curl -X POST http://localhost:5000/api/advanced-monitoring/update-metrics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "plugin_id": "my_plugin",
    "metrics": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "response_time": 1.2,
      "error_count": 3,
      "request_count": 150
    }
  }'
```

### 4. 임계값 설정

#### 기본 임계값
- **CPU 사용률**: 80% (경고), 95% (심각)
- **메모리 사용률**: 85% (경고), 95% (심각)
- **응답 시간**: 5초 (경고)
- **에러율**: 10% (경고)
- **연속 에러**: 5회 (심각)

#### 임계값 변경
```python
from core.backend.plugin_monitoring import plugin_monitor

# 임계값 변경
plugin_monitor.thresholds.cpu_threshold = 70.0
plugin_monitor.thresholds.memory_threshold = 80.0
plugin_monitor.thresholds.response_time_threshold = 3.0
```

---

## 실시간 알림 시스템

### 1. 알림 레벨

#### 알림 레벨별 의미
- **Info**: 정보성 알림 (로그인, 설정 변경 등)
- **Warning**: 주의가 필요한 상황 (임계값 초과)
- **Error**: 오류 상황 (연속 실패, 에러율 증가)
- **Critical**: 심각한 문제 (시스템 중단, 보안 위협)

### 2. 알림 수신 방법

#### 웹 인터페이스
- 실시간 Toast 알림
- 알림 센터에서 확인
- 대시보드 알림 배지

#### 브라우저 알림
- 브라우저 권한 허용 필요
- 탭이 비활성화되어도 알림 수신

#### WebSocket 연결
- 실시간 알림 스트리밍
- 자동 재연결 기능

### 3. 알림 설정

#### 알림 필터링
```javascript
// 특정 플러그인 알림만 수신
ws.send(JSON.stringify({
  type: 'subscribe',
  plugin_id: 'specific_plugin'
}));

// 특정 레벨 알림만 수신
ws.send(JSON.stringify({
  type: 'filter',
  levels: ['error', 'critical']
}));
```

#### 알림 해결
- 알림 클릭 시 자동 해결 처리
- 수동 해결 버튼으로 상태 변경

### 4. 알림 히스토리

#### 알림 조회
```bash
# 활성 알림 조회
curl http://localhost:5000/api/advanced-monitoring/alerts

# 알림 히스토리 조회
curl http://localhost:5000/api/advanced-monitoring/alerts/history
```

---

## 고급 모니터링 기능

### 1. 상세 메트릭

#### 수집되는 메트릭
- **CPU 사용률**: 전체 CPU 사용률
- **메모리 사용률**: RSS, VMS 메모리 사용량
- **응답 시간**: P50, P95, P99 백분위수
- **에러율**: 요청 대비 에러 비율
- **처리량**: 초당 처리 요청 수
- **연결 수**: 활성/총 연결 수
- **I/O**: 디스크 및 네트워크 I/O

#### 메트릭 조회
```bash
# 상세 메트릭 조회 (24시간)
curl "http://localhost:5000/api/advanced-monitoring/metrics/my_plugin?hours=24"

# 특정 시간 범위 조회
curl "http://localhost:5000/api/advanced-monitoring/metrics/my_plugin?hours=168"
```

### 2. 성능 트렌드 분석

#### 트렌드 방향
- **Up**: 값이 증가하는 추세
- **Down**: 값이 감소하는 추세
- **Stable**: 안정적인 상태

#### 트렌드 강도
- **Strong**: 20% 이상 변화
- **Moderate**: 10-20% 변화
- **Weak**: 10% 미만 변화

#### 트렌드 조회
```bash
curl http://localhost:5000/api/advanced-monitoring/trends/my_plugin
```

### 3. 사용량 패턴 분석

#### 패턴 유형
- **시간대별 패턴**: 피크 시간, 저사용 시간
- **일별 패턴**: 요일별 사용량 차이
- **주별 패턴**: 주간 사용량 패턴
- **월별 패턴**: 월간 사용량 패턴

#### 패턴 조회
```bash
curl http://localhost:5000/api/advanced-monitoring/usage-patterns/my_plugin
```

### 4. 종합 분석

#### 분석 데이터 조회
```bash
curl "http://localhost:5000/api/advanced-monitoring/analytics/my_plugin?hours=24"
```

#### 포함되는 정보
- 상세 메트릭 히스토리
- 성능 트렌드
- 사용량 패턴
- 통계 요약 (평균, 최대, 최소, 현재값)

### 5. 데이터 내보내기

#### JSON 형식
```bash
curl "http://localhost:5000/api/advanced-monitoring/export/my_plugin?hours=24&format=json"
```

#### CSV 형식
```bash
curl "http://localhost:5000/api/advanced-monitoring/export/my_plugin?hours=24&format=csv"
```

---

## 문제 대응 가이드

### 1. 일반적인 문제 해결

#### 플러그인이 응답하지 않음
1. **확인 사항**
   - 플러그인 프로세스 상태 확인
   - 로그 파일 확인
   - 리소스 사용량 확인

2. **해결 방법**
   ```bash
   # 프로세스 상태 확인
   ps aux | grep plugin_name
   
   # 로그 확인
   tail -f logs/plugin_name.log
   
   # 플러그인 재시작
   curl -X POST http://localhost:5000/api/plugins/restart/plugin_name
   ```

#### CPU 사용률이 높음
1. **원인 분석**
   - 무한 루프 또는 비효율적인 알고리즘
   - 과도한 요청 처리
   - 메모리 누수로 인한 GC 부하

2. **해결 방법**
   - 코드 프로파일링
   - 요청 제한 설정
   - 메모리 사용량 최적화

#### 메모리 사용률이 높음
1. **원인 분석**
   - 메모리 누수
   - 큰 데이터셋 처리
   - 캐시 크기 과다

2. **해결 방법**
   - 메모리 프로파일링
   - 데이터 처리 방식 최적화
   - 캐시 크기 조정

#### 응답 시간이 느림
1. **원인 분석**
   - 데이터베이스 쿼리 최적화 필요
   - 외부 API 응답 지연
   - 리소스 부족

2. **해결 방법**
   - 쿼리 최적화
   - 캐싱 도입
   - 리소스 증설

### 2. 긴급 상황 대응

#### 시스템 중단
1. **즉시 조치**
   ```bash
   # 모든 플러그인 중지
   curl -X POST http://localhost:5000/api/plugins/stop-all
   
   # 시스템 상태 확인
   curl http://localhost:5000/api/system/health
   
   # 로그 확인
   tail -f logs/system.log
   ```

2. **복구 절차**
   - 원인 파악 및 해결
   - 플러그인 순차적 재시작
   - 모니터링 강화

#### 보안 위협
1. **즉시 조치**
   ```bash
   # 의심스러운 플러그인 비활성화
   curl -X POST http://localhost:5000/api/plugins/disable/suspicious_plugin
   
   # 로그 분석
   grep "ERROR\|WARNING\|CRITICAL" logs/*.log
   
   # 네트워크 연결 확인
   netstat -tulpn | grep :5000
   ```

2. **보안 강화**
   - 방화벽 설정 강화
   - 접근 로그 분석
   - 보안 패치 적용

### 3. 성능 문제 진단

#### 진단 도구
```bash
# 시스템 리소스 확인
htop
iotop
nethogs

# 네트워크 연결 확인
ss -tulpn
netstat -i

# 디스크 사용량 확인
df -h
du -sh /path/to/plugin/data
```

#### 로그 분석
```bash
# 에러 로그 집계
grep "ERROR" logs/*.log | wc -l

# 특정 시간대 로그 확인
grep "2024-01-15 14:" logs/*.log

# 플러그인별 에러 통계
grep "ERROR" logs/*.log | cut -d' ' -f1 | sort | uniq -c
```

---

## 성능 최적화

### 1. 플러그인 최적화

#### 코드 최적화
- **알고리즘 개선**: 시간 복잡도 최적화
- **메모리 관리**: 불필요한 객체 생성 방지
- **비동기 처리**: I/O 작업 비동기화

#### 설정 최적화
```python
# 플러그인 설정 예시
PLUGIN_CONFIG = {
    'max_workers': 4,           # 워커 스레드 수
    'cache_size': 1000,         # 캐시 크기
    'timeout': 30,              # 타임아웃 설정
    'batch_size': 100,          # 배치 처리 크기
    'connection_pool': 10       # 연결 풀 크기
}
```

### 2. 시스템 최적화

#### 리소스 할당
- **CPU**: 플러그인별 CPU 제한 설정
- **메모리**: 메모리 사용량 제한
- **디스크**: I/O 최적화

#### 네트워크 최적화
- **연결 풀링**: 데이터베이스 연결 재사용
- **캐싱**: 자주 사용되는 데이터 캐싱
- **압축**: 네트워크 전송 데이터 압축

### 3. 모니터링 최적화

#### 데이터 수집 최적화
- **수집 주기 조정**: 필요에 따라 수집 주기 변경
- **데이터 압축**: 오래된 데이터 압축 저장
- **데이터 보관**: 오래된 데이터 자동 삭제

#### 알림 최적화
- **알림 그룹화**: 유사한 알림 그룹화
- **알림 스로틀링**: 과도한 알림 방지
- **알림 우선순위**: 중요도별 알림 분류

---

## 백업 및 복구

### 1. 데이터 백업

#### 자동 백업 설정
```bash
# 백업 스크립트 실행
python scripts/auto_backup.py

# cron 작업 등록 (매일 새벽 2시)
0 2 * * * /usr/bin/python /path/to/scripts/auto_backup.py
```

#### 수동 백업
```bash
# 데이터베이스 백업
sqlite3 plugin_monitoring.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# 설정 파일 백업
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz config/
```

### 2. 복구 절차

#### 데이터베이스 복구
```bash
# 백업에서 복구
sqlite3 plugin_monitoring.db ".restore backup_20240115_020000.db"

# 설정 파일 복구
tar -xzf config_backup_20240115_020000.tar.gz
```

#### 플러그인 복구
```bash
# 플러그인 재설치
pip install -r requirements.txt

# 플러그인 설정 복원
cp backup/plugin_config.json config/
```

### 3. 재해 복구 계획

#### 복구 우선순위
1. **핵심 시스템**: 기본 모니터링 시스템
2. **데이터 복구**: 메트릭 및 설정 데이터
3. **플러그인 복구**: 비즈니스 로직 플러그인
4. **고급 기능**: 분석 및 보고 기능

#### 복구 시간 목표
- **RTO (Recovery Time Objective)**: 4시간
- **RPO (Recovery Point Objective)**: 1시간

---

## 보안 가이드

### 1. 접근 제어

#### 사용자 권한 관리
- **관리자**: 모든 기능 접근 가능
- **운영자**: 모니터링 및 알림 관리
- **뷰어**: 읽기 전용 접근

#### API 보안
```bash
# API 키 생성
python scripts/generate_api_key.py

# API 키 검증
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:5000/api/status
```

### 2. 네트워크 보안

#### 방화벽 설정
```bash
# 필요한 포트만 개방
ufw allow 5000/tcp  # 웹 서버
ufw allow 8765/tcp  # WebSocket
ufw deny 22/tcp     # SSH (필요시만)
```

#### SSL/TLS 설정
```bash
# SSL 인증서 설정
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# HTTPS 서버 실행
python app.py --ssl-cert cert.pem --ssl-key key.pem
```

### 3. 데이터 보안

#### 데이터 암호화
- **전송 중 암호화**: HTTPS/TLS 사용
- **저장 중 암호화**: 민감한 데이터 암호화 저장
- **백업 암호화**: 백업 파일 암호화

#### 로그 보안
```bash
# 로그 파일 권한 설정
chmod 600 logs/*.log
chown monitoring:monitoring logs/

# 로그 로테이션 설정
logrotate /etc/logrotate.d/plugin_monitoring
```

### 4. 보안 모니터링

#### 보안 이벤트 감지
- **로그인 시도**: 실패한 로그인 시도 모니터링
- **API 사용량**: 비정상적인 API 호출 감지
- **시스템 변경**: 설정 변경 이력 추적

#### 보안 알림
```python
# 보안 이벤트 알림 설정
SECURITY_ALERTS = {
    'failed_login_threshold': 5,      # 5회 실패 시 알림
    'api_rate_limit': 100,            # 분당 100회 초과 시 알림
    'config_change': True,            # 설정 변경 시 알림
    'plugin_installation': True       # 플러그인 설치 시 알림
}
```

---

## 유지보수 일정

### 일일 작업
- [ ] 시스템 상태 확인
- [ ] 알림 확인 및 처리
- [ ] 로그 파일 확인
- [ ] 백업 상태 확인

### 주간 작업
- [ ] 성능 분석 및 최적화
- [ ] 보안 업데이트 적용
- [ ] 데이터 정리 (오래된 로그 삭제)
- [ ] 플러그인 업데이트

### 월간 작업
- [ ] 전체 시스템 점검
- [ ] 성능 보고서 작성
- [ ] 보안 감사
- [ ] 백업 복구 테스트

### 분기별 작업
- [ ] 시스템 아키텍처 검토
- [ ] 성능 벤치마크
- [ ] 보안 정책 업데이트
- [ ] 사용자 교육

---

## 연락처 및 지원

### 기술 지원
- **이메일**: support@yourprogram.com
- **전화**: 02-1234-5678
- **온라인 문서**: https://docs.yourprogram.com

### 긴급 상황
- **24시간 지원**: 02-1234-9999
- **긴급 이메일**: emergency@yourprogram.com

### 커뮤니티
- **포럼**: https://community.yourprogram.com
- **GitHub**: https://github.com/yourprogram
- **문서**: https://docs.yourprogram.com

---

## 부록

### A. 명령어 참조
```bash
# 시스템 상태 확인
systemctl status your_program

# 로그 확인
journalctl -u your_program -f

# 프로세스 확인
ps aux | grep python

# 포트 확인
netstat -tulpn | grep :5000
```

### B. 설정 파일 위치
- **메인 설정**: `config/settings.py`
- **플러그인 설정**: `plugins/*/config/`
- **로그 설정**: `config/logging.conf`
- **데이터베이스**: `plugin_monitoring.db`

### C. 로그 파일 위치
- **시스템 로그**: `logs/system.log`
- **플러그인 로그**: `logs/plugins/*.log`
- **모니터링 로그**: `logs/plugin_monitoring.log`
- **알림 로그**: `logs/notifications.log`

### D. 성능 지표
- **응답 시간**: 평균 < 1초, P95 < 3초
- **가용성**: 99.9% 이상
- **처리량**: 초당 1000+ 요청
- **에러율**: 1% 미만 