# 🌐 가상 서버 실행 가이드

이 가이드는 가상 서버 환경에서 애플리케이션을 실행하는 방법을 설명합니다.

## 🔍 가상 서버 vs 로컬 환경 차이점

### 가상 서버에서 발생하는 문제들:
- **CORS 오류**: 가상 서버의 IP 주소가 허용되지 않음
- **Redis 연결 실패**: 가상 서버에 Redis가 설치되지 않음
- **네트워크 설정**: 포트 바인딩 및 방화벽 문제
- **환경변수**: 가상 서버 전용 설정 필요

## 🛠️ 해결 방법

### 1. 자동 실행 (권장)

**백엔드 서버 시작:**
```bash
start_virtual_server.bat
```

**프론트엔드 서버 시작** (새 터미널):
```bash
start_frontend_virtual.bat
```

### 2. 수동 실행

**백엔드:**
```bash
python start_virtual_server.py
```

**프론트엔드:**
```bash
cd frontend
set NEXT_PUBLIC_API_URL=http://localhost:5000
npm run dev
```

## 📋 가상 서버 최적화 설정

### `config/virtual_server.env`에 적용된 설정:
- ✅ **CORS**: 모든 Origin 허용 (`*`)
- ✅ **Redis**: 비활성화 (메모리 캐시 사용)
- ✅ **외부 서비스**: OAuth, SMS 등 비활성화
- ✅ **네트워크**: `0.0.0.0` 바인딩으로 외부 접근 허용
- ✅ **캐시**: 메모리 기반 캐시 사용

### `config/cache_fallback.py`에 적용된 개선:
- ✅ **자동 Fallback**: Redis 없어도 정상 작동
- ✅ **가상 서버 모드**: `DISABLE_REDIS=true` 지원
- ✅ **에러 방지**: Redis 연결 실패 시 안전하게 메모리 캐시 사용

## 🚀 접속 방법

서버 시작 후 브라우저에서:
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:5000
- **관리자 로그인**: admin / admin123

## ⚠️ 주의사항

### 가상 서버에서만 적용:
1. **방화벽 설정**: 포트 3000, 5000 열기
2. **IP 주소**: 가상 서버의 실제 IP로 접속 필요시 설정 변경
3. **메모리 제약**: Redis 대신 메모리 캐시 사용으로 재시작 시 캐시 초기화

### 성능 최적화:
- Redis 없이도 안정적 동작
- 메모리 캐시로 빠른 응답
- 불필요한 외부 서비스 비활성화

## 🔧 문제 해결

### 자주 발생하는 오류:

**1. CORS 오류**
- 해결: `config/virtual_server.env`의 `CORS_ORIGINS=*` 설정 적용됨

**2. Redis 연결 오류**  
- 해결: 자동으로 메모리 캐시로 전환됨

**3. 포트 접근 불가**
- 해결: 가상 서버 방화벽에서 3000, 5000 포트 허용

**4. 환경변수 로드 실패**
- 해결: `start_virtual_server.py` 사용하여 자동 로드

## 📞 지원

문제가 지속될 경우:
1. 로그 파일 확인: `logs/virtual_server.log`
2. 서버 상태 확인: http://localhost:5000/health
3. API 문서: http://localhost:5000/swagger-ui