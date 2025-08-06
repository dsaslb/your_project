# API 문서 시스템

API 문서 시스템은 Flask 애플리케이션의 모든 엔드포인트를 자동으로 스캔하여 OpenAPI 3.0 스펙을 생성하고 다양한 형태의 문서를 제공합니다.

## 주요 기능

- **자동 엔드포인트 스캔**: Flask 앱의 모든 라우트 자동 감지
- **OpenAPI 3.0 스펙 생성**: 표준 OpenAPI 스펙 JSON/YAML 생성
- **다중 문서 형식**: Swagger UI, ReDoc, 마크다운, Postman, Insomnia
- **실시간 문서 생성**: API 변경 시 즉시 문서 업데이트
- **태그 기반 분류**: Blueprint별 자동 태그 분류
- **설정 관리**: 문서 제목, 버전, 연락처 등 커스터마이징

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# .env 예시
API_DOCS_TITLE="비즈니스 관리 시스템 API"
API_DOCS_VERSION="1.0.0"
API_DOCS_SERVER_URL="http://localhost:5000"
API_DOCS_OUTPUT_DIR="data/api_docs"
```

### 3. 데이터 디렉토리 생성
```bash
mkdir -p data/api_docs
```

## 사용법 예시

### 1. 기본 설정
```python
from api_docs.docs_generator import ApiDocsGenerator, ApiDocsConfig

config = ApiDocsConfig(
    title="비즈니스 관리 시스템 API",
    version="1.0.0",
    description="비즈니스 관리 시스템의 REST API 문서",
    server_url="http://localhost:5000",
    output_dir="data/api_docs"
)

generator = ApiDocsGenerator(app, config)
```

### 2. 문서 생성
```python
# 모든 문서 생성
success = generator.generate_all_docs()

# 개별 문서 생성
spec = generator.generate_openapi_spec()
generator.save_openapi_spec(spec)
generator.generate_markdown_docs(spec)
generator.generate_postman_collection(spec)
```

### 3. 엔드포인트 스캔
```python
# 모든 엔드포인트 스캔
generator.scan_endpoints()

# 스캔된 엔드포인트 확인
for endpoint in generator.endpoints:
    print(f"{endpoint.path} - {endpoint.methods}")
```

## REST API 엔드포인트

- `GET /api/docs/health` : 시스템 상태 확인
- `POST /api/docs/generate` : API 문서 생성
- `GET /api/docs/files` : 생성된 파일 목록 조회
- `GET /api/docs/files/<filename>` : 파일 다운로드
- `GET /api/docs/openapi` : OpenAPI 스펙 조회
- `GET /api/docs/swagger` : Swagger UI 제공
- `GET /api/docs/redoc` : ReDoc UI 제공
- `GET /api/docs/stats` : 문서 통계 조회
- `GET /api/docs/config` : 설정 조회
- `PUT /api/docs/config` : 설정 업데이트

## 생성되는 문서

### 1. OpenAPI 스펙
- `openapi.json`: JSON 형식 OpenAPI 3.0 스펙
- `openapi.yaml`: YAML 형식 OpenAPI 3.0 스펙

### 2. 마크다운 문서
- `api_documentation.md`: 사람이 읽기 쉬운 API 문서

### 3. API 클라이언트 컬렉션
- `postman_collection.json`: Postman 컬렉션
- `insomnia_collection.json`: Insomnia 컬렉션

## 문서 UI

### Swagger UI
- URL: `/api/docs/swagger`
- 인터랙티브 API 문서
- 실시간 API 테스트 가능

### ReDoc
- URL: `/api/docs/redoc`
- 깔끔하고 읽기 쉬운 문서
- 반응형 디자인

## 설정 옵션

```python
@dataclass
class ApiDocsConfig:
    title: str = "API 문서"
    version: str = "1.0.0"
    description: str = "API 문서 설명"
    contact_name: str = "API Support"
    contact_email: str = "support@example.com"
    server_url: str = "http://localhost:5000"
    output_dir: str = "data/api_docs"
    enable_swagger_ui: bool = True
    enable_redoc: bool = True
    enable_postman: bool = True
    enable_insomnia: bool = True
```

## 엔드포인트 정보 추출

### docstring 파싱
```python
def example_endpoint():
    """
    사용자 정보 조회
    
    사용자의 상세 정보를 조회합니다.
    
    @response 200 성공적으로 사용자 정보 반환
    @response 404 사용자를 찾을 수 없음
    """
    pass
```

### 자동 추출 정보
- **경로 파라미터**: URL 경로의 동적 파라미터
- **HTTP 메서드**: GET, POST, PUT, DELETE 등
- **태그**: Blueprint 이름 기반 자동 분류
- **요약**: docstring의 첫 번째 줄
- **설명**: docstring 전체 내용
- **응답**: @response 태그 기반 응답 정보

## 확장 기능

- **커스텀 스키마**: 복잡한 데이터 모델 스키마 정의
- **보안 스키마**: JWT, API Key 등 인증 방식 정의
- **예제 요청/응답**: 실제 사용 예제 추가
- **버전 관리**: API 버전별 문서 관리
- **자동화**: CI/CD 파이프라인 연동

## 문제 해결

- **엔드포인트 누락**: Blueprint 등록 확인
- **docstring 파싱 오류**: 표준 형식 사용
- **파일 생성 실패**: 출력 디렉토리 권한 확인
- **UI 로딩 실패**: 네트워크 연결 및 CDN 확인

## 라이선스
MIT 