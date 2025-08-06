# API 문서 시스템

퀀텀 비즈니스 관리 시스템의 API 문서화 및 관리를 위한 시스템입니다.

## 기능

### 📖 Swagger UI
- 실시간 API 문서 확인
- 인터랙티브 API 테스트
- 요청/응답 예시 제공

### 🔧 자동 문서 생성
- Flask 앱에서 자동으로 API 엔드포인트 스캔
- OpenAPI 3.0 스펙 자동 생성
- 다양한 형식 지원 (JSON, YAML, Markdown)

### 📦 외부 도구 지원
- Postman 컬렉션 자동 생성
- Insomnia 컬렉션 자동 생성
- 환경 변수 설정 지원

### 🔄 실시간 업데이트
- 코드 변경 시 자동 문서 업데이트
- 버전 관리 및 변경 이력 추적

## 설치 및 실행

### 1. 의존성 설치

```bash
cd api
pip install -r requirements.txt
```

### 2. API 문서 서버 실행

```bash
python api_documentation.py
```

### 3. 문서 생성 스크립트 실행

```bash
python ../scripts/generate_api_docs.py
```

## 사용 방법

### Swagger UI 접속

서버 실행 후 브라우저에서 다음 URL에 접속:

```
http://localhost:5000/api/docs
```

### API 문서 확인

- **JSON 형식**: `http://localhost:5000/static/swagger.json`
- **상태 확인**: `http://localhost:5000/api/docs/health`
- **버전 정보**: `http://localhost:5000/api/docs/version`

### 문서 내보내기

```bash
# JSON 형식으로 내보내기
curl "http://localhost:5000/api/docs/export?format=json"

# YAML 형식으로 내보내기
curl "http://localhost:5000/api/docs/export?format=yaml"
```

## 파일 구조

```
api/
├── api_documentation.py      # API 문서 서버
├── documentation_generator.py # 자동 문서 생성기
├── requirements.txt          # Python 의존성
└── README.md                # 이 파일

docs/
└── api/
    ├── openapi.json         # OpenAPI JSON 스펙
    ├── openapi.yaml         # OpenAPI YAML 스펙
    ├── API_Documentation.md # Markdown 문서
    ├── postman_collection.json # Postman 컬렉션
    ├── insomnia_collection.json # Insomnia 컬렉션
    └── README.md            # API 문서 README
```

## API 엔드포인트

### 인증
- `POST /api/auth/login` - 사용자 로그인

### 대시보드
- `GET /api/dashboard/stats` - 대시보드 통계 조회

### 매장 관리
- `GET /api/stores` - 매장 목록 조회
- `POST /api/stores` - 새 매장 등록

### 재고 관리
- `GET /api/inventory` - 재고 목록 조회

### 주문 관리
- `GET /api/orders` - 주문 목록 조회

### 스케줄 관리
- `GET /api/schedules` - 스케줄 목록 조회

### 알림
- `GET /api/notifications` - 알림 목록 조회

### 사용자 관리
- `GET /api/users` - 사용자 목록 조회

## 개발 가이드

### 새로운 API 엔드포인트 추가

1. Flask 앱에 새로운 라우트 추가
2. docstring에 API 정보 추가:

```python
@app.route('/api/new-endpoint')
def new_endpoint():
    """
    @summary 새로운 엔드포인트
    @description 새로운 기능을 위한 엔드포인트
    @tag 기타
    @param id 아이템 ID
    @response 200 성공
    """
    return {"message": "success"}
```

3. 문서 재생성:

```bash
python scripts/generate_api_docs.py
```

### 커스텀 스키마 추가

`api_documentation.py`의 `components.schemas` 섹션에 추가:

```python
"components": {
    "schemas": {
        "CustomModel": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            }
        }
    }
}
```

### 보안 스키마 수정

JWT 인증 외에 다른 인증 방식을 사용하려면:

```python
"securitySchemes": {
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key"
    }
}
```

## 환경 설정

### 환경 변수

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
export API_BASE_URL=http://localhost:5000
```

### 설정 파일

`config.py` 파일을 생성하여 설정을 관리할 수 있습니다:

```python
class Config:
    API_TITLE = "퀀텀 비즈니스 관리 시스템 API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "비즈니스 관리를 위한 종합 API 시스템"
    CONTACT_NAME = "API 지원팀"
    CONTACT_EMAIL = "support@quantum-business.com"
```

## 문제 해결

### 일반적인 오류

1. **포트 충돌**: 다른 포트 사용
   ```bash
   python api_documentation.py --port 5001
   ```

2. **CORS 오류**: CORS 설정 확인
   ```python
   CORS(app, origins=["http://localhost:3000"])
   ```

3. **문서 로딩 실패**: 정적 파일 경로 확인
   ```python
   app.static_folder = 'static'
   ```

### 디버깅

```bash
# 디버그 모드로 실행
FLASK_DEBUG=1 python api_documentation.py

# 로그 확인
tail -f logs/api_docs.log
```

## 성능 최적화

### 캐싱

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def get_api_docs():
    return api_documentation
```

### 압축

```python
from flask_compress import Compress

Compress(app)
```

## 보안

### 인증

- JWT 토큰 검증
- API 키 인증 지원
- Rate limiting 적용

### CORS 설정

```python
CORS(app, origins=[
    "http://localhost:3000",
    "https://your-domain.com"
])
```

## 모니터링

### 헬스 체크

```bash
curl http://localhost:5000/api/docs/health
```

### 메트릭 수집

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요. 