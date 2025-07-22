# API 문서화 가이드

## 개요

이 프로젝트는 Swagger/OpenAPI 3.0을 사용하여 API 문서화와 자동 타입 생성을 구현합니다.

## 구조

```
├── api/
│   └── swagger_config.py          # Swagger 설정 및 스키마 정의
├── frontend/
│   ├── scripts/
│   │   └── generate-types.ts      # 자동 타입 생성 스크립트
│   ├── src/
│   │   ├── types/
│   │   │   └── api-types.ts       # 자동 생성된 타입 (생성 후)
│   │   └── utils/
│   │       ├── api.ts             # 기본 API 유틸리티
│   │       └── api-client.ts      # 타입 안전한 API 클라이언트
│   └── package.json               # 타입 생성 스크립트 포함
└── docs/
    └── API_DOCUMENTATION.md       # 이 파일
```

## 백엔드 설정

### 1. Swagger 설정

`api/swagger_config.py`에서 다음을 정의합니다:

- **스키마 정의**: Marshmallow를 사용한 데이터 모델 스키마
- **태그 정의**: API 엔드포인트 그룹화
- **응답 스키마**: 성공/실패 응답 형식

### 2. 스키마 추가 방법

```python
from marshmallow import Schema, fields, validate

class NewModelSchema(Schema):
    """새 모델 스키마"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    status = fields.Str(validate=validate.OneOf(['active', 'inactive']))
    created_at = fields.DateTime(dump_only=True)
```

### 3. 스키마 등록

```python
def create_swagger_config(app):
    api = Api(app)
    api.spec.components.schema("NewModel", schema=NewModelSchema)
    return api
```

## 프론트엔드 설정

### 1. 타입 생성

```bash
# 타입 생성
npm run generate-types

# 개발 중 자동 타입 생성 (watch 모드)
npm run generate-types:watch
```

### 2. API 클라이언트 사용

```typescript
import { apiClient } from '@/utils/api-client';

// 브랜드 목록 조회
const { data: brands } = await apiClient.brands.list();

// 브랜드 생성
const newBrand = await apiClient.brands.create({
  name: '새 브랜드',
  industry_id: 1,
  description: '브랜드 설명'
});
```

### 3. React Query와 함께 사용

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/utils/api-client';

export const useBrands = () => {
  return useQuery({
    queryKey: ['brands'],
    queryFn: () => apiClient.brands.list(),
  });
};
```

## API 문서 접근

### 1. Swagger UI
- URL: `http://localhost:5000/swagger-ui`
- 인터랙티브 API 문서 및 테스트

### 2. ReDoc
- URL: `http://localhost:5000/redoc`
- 읽기 쉬운 API 문서

### 3. OpenAPI JSON
- URL: `http://localhost:5000/swagger-ui/swagger.json`
- 자동 타입 생성용

## 태그별 API 그룹

### 인증 (auth)
- 로그인/로그아웃
- 사용자 인증

### 관리자 (admin)
- 시스템 관리
- 사용자 관리
- 권한 관리

### 브랜드 (brands)
- 브랜드 CRUD
- 브랜드 통계

### 매장 (stores)
- 매장 CRUD
- 매장 통계

### 직원 (employees)
- 직원 관리
- 근무 상태

### 플러그인 (plugins)
- 플러그인 관리
- 플러그인 마켓플레이스

### 모듈 (modules)
- 모듈 설치/제거
- 모듈 설정

### 피드백 (feedback)
- 피드백 시스템
- 피드백 관리

### 시스템 (system)
- 시스템 모니터링
- 로그 관리

### 대시보드 (dashboard)
- 통계 데이터
- 대시보드 정보

### 업종 (industries)
- 업종 관리
- 업종별 통계

## 개발 워크플로우

### 1. 새로운 API 엔드포인트 추가

1. **백엔드**: Flask 라우트 추가
2. **백엔드**: Swagger 스키마 정의
3. **백엔드**: API 문서화 데코레이터 추가
4. **프론트엔드**: 타입 생성 스크립트 실행
5. **프론트엔드**: API 클라이언트에 메서드 추가
6. **프론트엔드**: React Query 훅 생성

### 2. API 변경 시

1. **백엔드**: 스키마 업데이트
2. **프론트엔드**: 타입 재생성
3. **프론트엔드**: 타입 오류 수정

### 3. 문서 업데이트

1. Swagger UI에서 변경사항 확인
2. API 문서 README 업데이트
3. 팀원들과 변경사항 공유

## 모범 사례

### 1. 스키마 설계
- 명확한 필드명 사용
- 적절한 유효성 검사 추가
- 필수/선택 필드 구분

### 2. 에러 처리
- 일관된 에러 응답 형식
- 적절한 HTTP 상태 코드
- 상세한 에러 메시지

### 3. 타입 안전성
- TypeScript 타입 활용
- 런타임 타입 검증
- API 응답 타입 검증

### 4. 문서화
- 명확한 API 설명
- 요청/응답 예시
- 에러 케이스 문서화

## 문제 해결

### 1. 타입 생성 실패
```bash
# API 서버 실행 확인
curl http://localhost:5000/swagger-ui/swagger.json

# 수동 타입 생성
npx openapi-typescript http://localhost:5000/swagger-ui/swagger.json
```

### 2. 스키마 충돌
- 스키마 이름 중복 확인
- 필드 타입 일치 확인
- Marshmallow 버전 호환성 확인

### 3. 타입 오류
- 생성된 타입 파일 확인
- API 응답 형식 일치 확인
- TypeScript 설정 확인

## 추가 리소스

- [OpenAPI 3.0 명세](https://swagger.io/specification/)
- [Marshmallow 문서](https://marshmallow.readthedocs.io/)
- [flask-smorest 문서](https://flask-smorest.readthedocs.io/)
- [openapi-typescript 문서](https://github.com/drwpow/openapi-typescript) 