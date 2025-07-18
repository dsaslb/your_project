# 통합 대시보드 시스템

## 개요

통합 대시보드 시스템은 레스토랑 관리 플랫폼의 모든 실시간 데이터를 하나의 인터페이스에서 통합하여 제공하는 고도화된 모니터링 시스템입니다.

## 주요 기능

### 🔄 실시간 데이터 통합
- **시스템 상태**: CPU, 메모리, 디스크 사용률, 네트워크 I/O
- **성능 메트릭**: 주문 현황, 근무 현황, 사용자 활동
- **AI 인사이트**: 예측 분석, 권장사항, 트렌드 분석
- **IoT 데이터**: 센서 데이터, 기기 상태, 환경 모니터링
- **플러그인 모니터링**: 플러그인 성능, 상태, 오류 추적
- **알림 시스템**: 실시간 알림, 우선순위 관리

### 📊 데이터 시각화
- **실시간 차트**: 성과 지표, 트렌드 분석
- **상태 표시**: 시스템 건강도, 성능 지표
- **알림 대시보드**: 중요도별 알림 분류
- **사용자 활동**: 실시간 사용자 통계

### 🔔 실시간 알림
- **SSE (Server-Sent Events)**: 실시간 데이터 스트리밍
- **WebSocket 지원**: 양방향 실시간 통신
- **알림 우선순위**: Critical, Warning, Info 레벨
- **자동 재연결**: 연결 끊김 시 자동 복구

## API 엔드포인트

### 통합 대시보드 API

#### 1. 통합 대시보드 데이터 조회
```http
GET /api/dashboard/integrated
Authorization: Bearer <token>
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2024-01-15T10:30:00Z",
    "system_status": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 32.1,
      "active_connections": 15,
      "uptime": "24h 30m",
      "database_status": "healthy",
      "api_response_time": 150
    },
    "performance_metrics": {
      "today_orders": {
        "total": 156,
        "pending": 12,
        "completed": 144,
        "total_sales": 2850000
      },
      "today_attendance": {
        "total": 8,
        "on_time": 7,
        "late": 1
      },
      "active_users": 23
    },
    "active_alerts": [
      {
        "type": "low_stock",
        "severity": "warning",
        "message": "재고 부족 알림",
        "timestamp": "2024-01-15T10:25:00Z"
      }
    ],
    "ai_insights": {
      "recommendations": [
        {
          "type": "sales_optimization",
          "title": "매출 최적화",
          "description": "피크 시간대 인력 배치 권장",
          "priority": "high",
          "action": "staff_scheduling"
        }
      ]
    }
  }
}
```

#### 2. 실시간 데이터 스트림
```http
GET /api/dashboard/stream
Authorization: Bearer <token>
```

**SSE 이벤트 형식:**
```
data: {"type": "dashboard_update", "data": {...}, "timestamp": "..."}

data: {"type": "heartbeat", "timestamp": "..."}

data: {"type": "connected", "connection_id": "..."}
```

#### 3. 대시보드 메트릭 조회
```http
GET /api/dashboard/metrics
Authorization: Bearer <token>
```

#### 4. 활성 알림 조회
```http
GET /api/dashboard/alerts
Authorization: Bearer <token>
```

#### 5. 시스템 상태 조회
```http
GET /api/dashboard/system-status
Authorization: Bearer <token>
```

#### 6. AI 인사이트 조회
```http
GET /api/dashboard/ai-insights
Authorization: Bearer <token>
```

## 프론트엔드 컴포넌트

### 통합 대시보드 컴포넌트
```typescript
import IntegratedDashboard from '@/components/IntegratedDashboard';

// 사용 예시
<IntegratedDashboard />
```

**주요 기능:**
- 실시간 데이터 업데이트
- SSE 연결 관리
- 자동 재연결
- 에러 처리
- 로딩 상태 관리

### 컴포넌트 구조
```
IntegratedDashboard/
├── SystemStatusCard      # 시스템 상태 카드
├── AlertCard            # 알림 카드
├── PerformanceMetrics   # 성과 메트릭
├── SystemStatus         # 시스템 상태
├── AIInsights          # AI 인사이트
└── ProgressBar         # 진행률 바
```

## 모바일 앱 지원

### 통합 대시보드 화면
```typescript
import IntegratedDashboardScreen from '../screens/IntegratedDashboardScreen';

// 네비게이션에 추가
<Tab.Screen 
  name="IntegratedDashboard" 
  component={IntegratedDashboardScreen} 
  options={{ title: '통합 대시보드' }} 
/>
```

**모바일 특화 기능:**
- 터치 친화적 UI
- 스와이프 제스처
- 푸시 알림 연동
- 오프라인 모드 지원

## 실시간 모니터링 시스템

### 모니터링 루프
```python
def _monitoring_loop(self):
    """실시간 모니터링 루프"""
    while self.monitoring_active:
        try:
            # 모든 실시간 데이터 수집
            dashboard_data = self._collect_all_data()
            
            # 캐시 업데이트
            self.data_cache = dashboard_data
            self.cache_expiry = datetime.now() + timedelta(seconds=30)
            
            # 활성 연결에 데이터 브로드캐스트
            self._broadcast_to_connections(dashboard_data)
            
            time.sleep(10)  # 10초마다 업데이트
            
        except Exception as e:
            logger.error(f"모니터링 루프 오류: {e}")
            time.sleep(30)
```

### 데이터 수집 프로세스
1. **시스템 상태 수집**: CPU, 메모리, 디스크 사용률
2. **성능 메트릭 수집**: 주문, 근무, 사용자 통계
3. **AI 인사이트 수집**: 예측 분석, 권장사항
4. **IoT 데이터 수집**: 센서 데이터, 기기 상태
5. **알림 데이터 수집**: 활성 알림, 우선순위

## 캐싱 시스템

### 캐시 구조
```python
self.data_cache = {
    'timestamp': datetime.now().isoformat(),
    'system_status': {...},
    'performance_metrics': {...},
    'active_alerts': [...],
    'ai_insights': {...},
    'iot_data': {...},
    'notifications': [...]
}
```

### 캐시 전략
- **TTL**: 30초
- **업데이트 주기**: 10초
- **에러 시 재시도**: 30초 후
- **메모리 최적화**: 불필요한 데이터 정리

## 보안 및 인증

### 인증 요구사항
- JWT 토큰 기반 인증
- 역할 기반 접근 제어 (RBAC)
- API 레이트 리미팅

### 권한 레벨
- **Admin**: 모든 데이터 접근
- **Manager**: 제한된 데이터 접근
- **Employee**: 기본 데이터만 접근

## 성능 최적화

### 최적화 전략
1. **데이터 캐싱**: Redis 기반 캐싱
2. **비동기 처리**: 백그라운드 데이터 수집
3. **연결 풀링**: 데이터베이스 연결 최적화
4. **압축**: SSE 데이터 압축
5. **배치 처리**: 대량 데이터 처리

### 모니터링 지표
- **응답 시간**: < 200ms
- **처리량**: 1000+ requests/min
- **메모리 사용률**: < 80%
- **CPU 사용률**: < 70%

## 오류 처리

### 오류 유형
1. **연결 오류**: 네트워크 문제
2. **데이터 오류**: 데이터베이스 문제
3. **인증 오류**: 토큰 만료
4. **시스템 오류**: 서버 문제

### 복구 전략
- **자동 재연결**: 5초 후 재시도
- **폴백 데이터**: 캐시된 데이터 사용
- **에러 로깅**: 상세한 오류 기록
- **사용자 알림**: 오류 상태 표시

## 배포 및 설정

### 환경 변수
```bash
# 대시보드 설정
DASHBOARD_UPDATE_INTERVAL=10
DASHBOARD_CACHE_TTL=30
DASHBOARD_MAX_CONNECTIONS=100

# 모니터링 설정
MONITORING_ENABLED=true
MONITORING_INTERVAL=10
ALERT_THRESHOLDS_CPU=80
ALERT_THRESHOLDS_MEMORY=85
```

### 의존성
```python
# 필수 패키지
psutil>=5.8.0
redis>=4.0.0
websockets>=10.0
asyncio>=3.4.3
```

## 사용 예시

### 웹 브라우저에서 접근
```javascript
// SSE 연결 설정
const eventSource = new EventSource('/api/dashboard/stream', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'dashboard_update') {
    updateDashboard(data.data);
  }
};
```

### 모바일 앱에서 접근
```typescript
// 실시간 데이터 구독
useEffect(() => {
  const eventSource = new EventSource('/api/dashboard/stream', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'dashboard_update') {
      setDashboardData(data.data);
    }
  };

  return () => eventSource.close();
}, []);
```

## 향후 개선 계획

### 단기 계획 (1-2개월)
- [ ] 실시간 차트 개선
- [ ] 알림 필터링 기능
- [ ] 모바일 푸시 알림
- [ ] 오프라인 모드 지원

### 중기 계획 (3-6개월)
- [ ] AI 예측 모델 통합
- [ ] 고급 분석 도구
- [ ] 커스텀 대시보드
- [ ] API 성능 최적화

### 장기 계획 (6개월 이상)
- [ ] 머신러닝 기반 이상 감지
- [ ] 자동화된 인사이트 생성
- [ ] 멀티 테넌트 지원
- [ ] 확장 가능한 아키텍처

## 문제 해결

### 일반적인 문제

#### 1. 실시간 연결 끊김
**증상**: 대시보드가 업데이트되지 않음
**해결책**: 
- 네트워크 연결 확인
- 토큰 만료 확인
- 자동 재연결 대기

#### 2. 데이터 로딩 지연
**증상**: 데이터가 늦게 표시됨
**해결책**:
- 캐시 상태 확인
- 서버 성능 모니터링
- 데이터베이스 연결 확인

#### 3. 메모리 사용률 높음
**증상**: 시스템이 느려짐
**해결책**:
- 캐시 정리
- 연결 수 제한
- 메모리 최적화

### 로그 확인
```bash
# 애플리케이션 로그
tail -f logs/app.log | grep dashboard

# 에러 로그
tail -f logs/error.log | grep dashboard

# 성능 로그
tail -f logs/performance.log | grep dashboard
```

## 지원 및 문의

### 기술 지원
- **이메일**: support@your_program.com
- **문서**: https://docs.your_program.com
- **GitHub**: https://github.com/your_program

### 커뮤니티
- **포럼**: https://forum.your_program.com
- **Discord**: https://discord.gg/your_program
- **Slack**: https://your_program.slack.com

---

**버전**: 1.0.0  
**최종 업데이트**: 2024-01-15  
**작성자**: Your Program Team 