# 빠른 참조 가이드

## 🚀 빠른 시작

### 1. 모니터링 시스템 시작
```bash
# 기본 모니터링 시작
python scripts/start_plugin_monitoring.py

# 백그라운드 실행
nohup python scripts/start_plugin_monitoring.py > monitoring.log 2>&1 &
```

### 2. 웹 대시보드 접속
- **기본 모니터링**: http://localhost:3000/admin/plugin-monitoring
- **고급 모니터링**: http://localhost:3000/admin/advanced-monitoring

### 3. WebSocket 연결 확인
```bash
# WebSocket 서버 상태 확인
netstat -tulpn | grep 8765
```

---

## 📊 주요 API 엔드포인트

### 플러그인 모니터링
```bash
# 모니터링 시작
POST /api/advanced-monitoring/start

# 플러그인 등록
POST /api/advanced-monitoring/register-plugin
{
  "plugin_id": "my_plugin",
  "plugin_name": "내 플러그인"
}

# 메트릭 업데이트
POST /api/advanced-monitoring/update-metrics
{
  "plugin_id": "my_plugin",
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "response_time": 1.2,
    "error_count": 3,
    "request_count": 150
  }
}
```

### 데이터 조회
```bash
# 상세 메트릭 조회 (24시간)
GET /api/advanced-monitoring/metrics/my_plugin?hours=24

# 성능 트렌드 조회
GET /api/advanced-monitoring/trends/my_plugin

# 사용량 패턴 조회
GET /api/advanced-monitoring/usage-patterns/my_plugin

# 종합 분석 데이터
GET /api/advanced-monitoring/analytics/my_plugin?hours=24
```

### 데이터 내보내기
```bash
# JSON 형식
GET /api/advanced-monitoring/export/my_plugin?hours=24&format=json

# CSV 형식
GET /api/advanced-monitoring/export/my_plugin?hours=24&format=csv
```

---

## 🔧 문제 해결

### 일반적인 문제

#### 1. 모니터링이 시작되지 않음
```bash
# 프로세스 확인
ps aux | grep plugin_monitoring

# 포트 확인
netstat -tulpn | grep 8765

# 로그 확인
tail -f logs/plugin_monitoring.log
```

#### 2. WebSocket 연결 실패
```bash
# WebSocket 서버 상태 확인
curl http://localhost:8765

# 방화벽 설정 확인
ufw status

# 포트 개방
ufw allow 8765/tcp
```

#### 3. 데이터베이스 오류
```bash
# 데이터베이스 파일 확인
ls -la plugin_monitoring.db

# 데이터베이스 무결성 검사
sqlite3 plugin_monitoring.db "PRAGMA integrity_check;"

# 백업에서 복구
sqlite3 plugin_monitoring.db ".restore backup_$(date +%Y%m%d).db"
```

#### 4. 메모리 부족
```bash
# 메모리 사용량 확인
free -h

# 프로세스별 메모리 사용량
ps aux --sort=-%mem | head -10

# 불필요한 프로세스 종료
pkill -f "python.*monitoring"
```

---

## 📈 성능 모니터링

### 주요 지표

| 지표 | 정상 범위 | 경고 | 심각 |
|------|-----------|------|------|
| CPU 사용률 | < 70% | 70-80% | > 80% |
| 메모리 사용률 | < 75% | 75-85% | > 85% |
| 응답 시간 | < 1초 | 1-3초 | > 3초 |
| 에러율 | < 1% | 1-5% | > 5% |

### 임계값 설정
```python
from core.backend.plugin_monitoring import plugin_monitor

# 임계값 변경
plugin_monitor.thresholds.cpu_threshold = 70.0
plugin_monitor.thresholds.memory_threshold = 80.0
plugin_monitor.thresholds.response_time_threshold = 2.0
plugin_monitor.thresholds.error_rate_threshold = 5.0
```

---

## 🔔 알림 시스템

### 알림 레벨
- **Info**: 정보성 알림 (파란색)
- **Warning**: 주의가 필요한 상황 (노란색)
- **Error**: 오류 상황 (주황색)
- **Critical**: 심각한 문제 (빨간색)

### 알림 설정
```javascript
// WebSocket 연결
const ws = new WebSocket('ws://localhost:8765');

// 인증
ws.send(JSON.stringify({
  type: 'auth',
  user_id: 'admin',
  role: 'admin'
}));

// 알림 필터링
ws.send(JSON.stringify({
  type: 'filter',
  levels: ['error', 'critical']
}));
```

### 알림 해결
```bash
# 알림 해결 API
curl -X POST http://localhost:5000/api/advanced-monitoring/resolve-alert \
  -H "Content-Type: application/json" \
  -d '{"alert_id": "alert_123"}'
```

---

## 📊 데이터 분석

### 메트릭 유형
- **CPU**: CPU 사용률, 로드 평균
- **Memory**: 메모리 사용률, RSS, VMS
- **Response Time**: P50, P95, P99 백분위수
- **Throughput**: 초당 처리 요청 수
- **Error Rate**: 에러율, 연속 에러 수
- **I/O**: 디스크 및 네트워크 I/O

### 트렌드 분석
```bash
# 트렌드 데이터 조회
curl http://localhost:5000/api/advanced-monitoring/trends/my_plugin

# 응답 예시
{
  "cpu": {
    "trend_direction": "up",
    "trend_strength": "moderate",
    "change_percent": 15.2
  },
  "memory": {
    "trend_direction": "stable",
    "trend_strength": "weak",
    "change_percent": 2.1
  }
}
```

### 패턴 분석
```bash
# 사용량 패턴 조회
curl http://localhost:5000/api/advanced-monitoring/usage-patterns/my_plugin

# 응답 예시
{
  "peak_hours": [9, 10, 11, 14, 15, 16],
  "low_usage_hours": [2, 3, 4, 5],
  "daily_usage_pattern": {
    "Monday": 85.2,
    "Tuesday": 87.1,
    "Wednesday": 89.3
  }
}
```

---

## 🛠️ 유지보수

### 일일 점검
```bash
# 시스템 상태 확인
curl http://localhost:5000/api/advanced-monitoring/status

# 활성 알림 확인
curl http://localhost:5000/api/advanced-monitoring/alerts

# 로그 확인
tail -f logs/plugin_monitoring.log
```

### 주간 점검
```bash
# 성능 분석
curl "http://localhost:5000/api/advanced-monitoring/analytics/my_plugin?hours=168"

# 데이터 정리 (30일 이상 오래된 데이터)
sqlite3 plugin_monitoring.db "DELETE FROM detailed_metrics WHERE timestamp < datetime('now', '-30 days');"

# 백업 생성
sqlite3 plugin_monitoring.db ".backup backup_$(date +%Y%m%d).db"
```

### 월간 점검
```bash
# 전체 시스템 점검
python scripts/system_health_check.py

# 성능 보고서 생성
python scripts/generate_performance_report.py

# 보안 감사
python scripts/security_audit.py
```

---

## 🔒 보안

### 기본 보안 설정
```bash
# 방화벽 설정
ufw allow 5000/tcp  # 웹 서버
ufw allow 8765/tcp  # WebSocket
ufw deny 22/tcp     # SSH (필요시만)

# 로그 파일 권한 설정
chmod 600 logs/*.log
chown monitoring:monitoring logs/

# SSL 인증서 설정
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

### API 보안
```bash
# API 키 생성
python scripts/generate_api_key.py

# API 키 검증
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:5000/api/status
```

---

## 📝 로그 분석

### 주요 로그 파일
- **시스템 로그**: `logs/system.log`
- **모니터링 로그**: `logs/plugin_monitoring.log`
- **플러그인 로그**: `logs/plugins/*.log`
- **알림 로그**: `logs/notifications.log`

### 로그 분석 명령어
```bash
# 에러 로그 집계
grep "ERROR" logs/*.log | wc -l

# 특정 시간대 로그 확인
grep "2024-01-15 14:" logs/*.log

# 플러그인별 에러 통계
grep "ERROR" logs/*.log | cut -d' ' -f1 | sort | uniq -c

# 실시간 로그 모니터링
tail -f logs/plugin_monitoring.log | grep -E "(ERROR|WARNING|CRITICAL)"
```

---

## 🚨 긴급 상황

### 시스템 중단 시
```bash
# 1. 모든 플러그인 중지
curl -X POST http://localhost:5000/api/plugins/stop-all

# 2. 시스템 상태 확인
curl http://localhost:5000/api/system/health

# 3. 로그 확인
tail -f logs/system.log

# 4. 복구 후 순차적 재시작
curl -X POST http://localhost:5000/api/plugins/start-all
```

### 보안 위협 시
```bash
# 1. 의심스러운 플러그인 비활성화
curl -X POST http://localhost:5000/api/plugins/disable/suspicious_plugin

# 2. 로그 분석
grep "ERROR\|WARNING\|CRITICAL" logs/*.log

# 3. 네트워크 연결 확인
netstat -tulpn | grep :5000

# 4. 방화벽 강화
ufw deny from suspicious_ip
```

---

## 📞 지원 연락처

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

---

## 📚 추가 자료

### 문서
- [관리자 가이드](ADMIN_GUIDE.md)
- [API 문서](API_DOCUMENTATION.md)
- [플러그인 개발 가이드](PLUGIN_DEVELOPMENT.md)

### 도구
- [성능 분석 도구](tools/performance_analyzer.py)
- [로그 분석 도구](tools/log_analyzer.py)
- [백업 도구](tools/backup_manager.py)

### 스크립트
- [시스템 점검 스크립트](scripts/system_health_check.py)
- [성능 보고서 생성 스크립트](scripts/generate_performance_report.py)
- [보안 감사 스크립트](scripts/security_audit.py) 