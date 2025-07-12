# 플러그인 성능 최적화 자동화 엔진

## 개요

플러그인 성능 최적화 자동화 엔진은 플러그인별 성능 데이터를 분석하여 자동으로 최적화 제안, 실행, 이력 관리를 지원하는 시스템입니다. CPU/메모리/에러율/응답시간 등 주요 지표를 기반으로 워커 수 조정, 캐시 최적화, 에러 원인 분석 등 다양한 자동화 제안을 생성하고, 관리자가 클릭 한 번으로 실행할 수 있습니다.

---

## 주요 기능
- 플러그인별 실시간 성능 분석 및 임계치 감지
- 자동 최적화 제안 생성 (워커/캐시/설정/에러 등)
- 제안 실행(자동 튜닝) 및 결과 이력 관리
- REST API 및 프론트엔드 대시보드 제공
- 머신러닝 기반 예측/이상 탐지(향후 계획)

---

## 시스템 구조

### 1. 백엔드
- `core/backend/plugin_optimization_engine.py` : 분석/제안/튜닝/이력 관리 엔진
- `api/plugin_optimization_api.py` : REST API (제안 조회/실행/이력)
- Flask Blueprint로 앱에 등록

### 2. 프론트엔드
- `frontend/src/components/PluginOptimizationDashboard.tsx` : 대시보드 UI (제안/실행/이력)
- `frontend/src/app/plugin-optimization/page.tsx` : 페이지 라우팅

### 3. 테스트/문서
- `scripts/test_plugin_optimization.py` : API 자동화 테스트
- `docs/PLUGIN_OPTIMIZATION_ENGINE.md` : 본 문서

---

## 설치 및 설정

### 1. 백엔드
- 의존성: Flask, flask-login, requests 등
- `app.py`에 Blueprint 등록
```python
try:
    from api.plugin_optimization_api import plugin_optimization_bp
    app.register_blueprint(plugin_optimization_bp, name='plugin_optimization_api')
except Exception as e:
    logger.error(f"플러그인 성능 최적화 API 블루프린트 등록 실패: {e}")
```
- 서버 재시작 시 자동 분석 스레드 실행됨

### 2. 프론트엔드
- Next.js/React 환경에서 컴포넌트/페이지 자동 인식
- `/plugin-optimization` 경로로 접속

### 3. 테스트
```bash
python scripts/test_plugin_optimization.py
```

---

## API 명세

### 1. 최적화 제안 목록 조회
```
GET /api/plugin-optimization/suggestions
```
- 응답: `[ { id, plugin_id, suggestion_type, description, created_at, details, executed, executed_at, result } ]`

### 2. 최적화 제안 실행
```
POST /api/plugin-optimization/execute/<suggestion_id>
```
- 응답: `{ success, message }`

### 3. 최적화 실행 이력 조회
```
GET /api/plugin-optimization/history
```
- 응답: `[ { plugin_id, suggestion_type, description, executed_at, result } ]`

---

## 사용법 예시

### 1. 대시보드에서 제안 실행
- `/plugin-optimization` 접속 → 제안 목록 확인 → [실행] 버튼 클릭
- 실행 결과는 이력 탭에서 확인 가능

### 2. API 직접 호출
```python
import requests
r = requests.get('http://localhost:5000/api/plugin-optimization/suggestions')
print(r.json())
```

### 3. 테스트 스크립트
```bash
python scripts/test_plugin_optimization.py
```

---

## 문제 해결

### 1. 제안이 생성되지 않는 경우
- 플러그인 모니터링 데이터가 충분히 쌓였는지 확인
- 엔진이 정상적으로 실행 중인지 로그 확인

### 2. 실행이 안 되는 경우
- 서버 로그에서 오류 메시지 확인
- 제안이 이미 실행된 상태인지 확인

### 3. 프론트엔드에서 데이터가 안 보임
- API 서버가 정상 동작 중인지 확인
- 인증/권한 문제(로그인 필요) 확인

---

## 향후 개발 계획
- 머신러닝 기반 이상 탐지/성능 예측
- 자동 튜닝(실제 설정값 변경, 배포 자동화)
- Slack/이메일 등 외부 알림 연동
- 플러그인별 맞춤형 최적화 정책 지원
- 대시보드 차트/시각화 고도화

---

## 결론

플러그인 성능 최적화 자동화 엔진은 플러그인 운영의 효율성과 안정성을 크게 높여줍니다. 실시간 분석, 자동 제안, 클릭 한 번의 실행, 이력 관리까지 통합적으로 제공하여 운영자의 부담을 줄이고, 시스템의 품질을 한 단계 끌어올릴 수 있습니다. 