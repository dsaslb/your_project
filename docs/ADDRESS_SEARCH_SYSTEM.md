# 주소 검색 시스템 - 개선된 버전

## 📋 개요

주소 검색 시스템은 카카오 주소 검색 API를 활용하여 사용자 친화적이고 정확한 주소 입력 및 검증 기능을 제공합니다. 이 시스템은 브랜드, 매장, 직원 등록 시 일관된 주소 검색 경험을 제공하며, 실시간 검증, 자동완성, 좌표 변환 등의 고급 기능을 포함합니다.

## 🚀 주요 개선 사항

### 1. 성능 및 사용자 경험 개선
- **자동완성 기능**: 실시간 주소 제안 및 키보드 네비게이션
- **디바운싱**: 입력 지연을 통한 성능 최적화
- **로딩 표시기**: 사용자 피드백 강화
- **Toast 메시지**: 개선된 알림 시스템
- **실시간 검증**: 입력 중 주소 유효성 검사

### 2. 백엔드 API 개선
- **캐싱 시스템**: 메모리 기반 캐시로 성능 향상
- **성능 모니터링**: API 실행 시간 추적
- **로깅 시스템**: 상세한 오류 및 성능 로그
- **주소 정규화**: 일관된 주소 형식 보장
- **에러 처리 강화**: 상세한 오류 메시지 및 복구

### 3. 관리 기능 추가
- **주소 대시보드**: 통계 및 모니터링
- **설정 관리**: 시스템 설정 중앙화
- **캐시 관리**: 캐시 초기화 및 모니터링
- **API 상태 확인**: 실시간 API 연결 상태

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
# 필요한 Python 패키지
pip install requests flask-sqlalchemy

# 프론트엔드 의존성 (이미 설치됨)
npm install
```

### 2. 카카오 API 키 설정

1. [카카오 개발자 센터](https://developers.kakao.com/)에서 애플리케이션 생성
2. REST API 키 발급
3. 환경변수 설정:

```bash
export KAKAO_API_KEY="your_kakao_api_key_here"
```

또는 설정 파일에서 관리:

```json
{
  "kakao_api_key": "your_kakao_api_key_here",
  "default_similarity_threshold": 0.8,
  "max_suggestions": 5,
  "debounce_delay": 300,
  "enable_cache": true,
  "cache_ttl": 300,
  "geocode_cache_ttl": 3600
}
```

### 3. 데이터베이스 마이그레이션

```bash
# 새로운 주소 필드 추가
flask db migrate -m "Add address fields to models"
flask db upgrade
```

## 📁 파일 구조

```
├── static/js/address-search.js          # 개선된 주소 검색 JavaScript
├── api/address_validation.py            # 개선된 백엔드 API
├── templates/admin/
│   ├── address_dashboard.html          # 주소 대시보드
│   ├── address_settings.html           # 설정 관리 페이지
│   └── brand_management.html           # 브랜드 관리 (주소 검색 포함)
├── config/address_search_config.json   # 설정 파일
└── docs/ADDRESS_SEARCH_SYSTEM.md       # 이 문서
```

## 🔧 사용법

### 1. 기본 주소 검색

```javascript
// 기본 초기화
const addressSearch = new AddressSearch({
    apiKey: 'YOUR_KAKAO_API_KEY',
    enableAutoComplete: true,
    enableValidation: true,
    enableCoordinates: true
});
```

### 2. 고급 설정

```javascript
// 고급 설정으로 초기화
const addressSearch = new AddressSearch({
    apiKey: 'YOUR_KAKAO_API_KEY',
    searchButtonId: 'custom-search-btn',
    addressInputId: 'custom-address-input',
    detailAddressId: 'custom-detail-input',
    zipCodeId: 'custom-zipcode-input',
    roadAddressId: 'custom-road-input',
    jibunAddressId: 'custom-jibun-input',
    latitudeId: 'custom-latitude-input',
    longitudeId: 'custom-longitude-input',
    enableAutoComplete: true,
    enableValidation: true,
    enableCoordinates: true,
    debounceDelay: 300,
    maxSuggestions: 5,
    onAddressSelected: function(data) {
        console.log('주소 선택됨:', data);
    },
    onError: function(message) {
        console.error('오류:', message);
    }
});
```

### 3. 동적 필드 생성

```javascript
// 주소 검색 버튼 생성
createAddressSearchButton('container-id', {
    buttonId: 'my-search-btn',
    buttonClass: 'btn btn-primary',
    apiKey: 'YOUR_KAKAO_API_KEY'
});

// 주소 입력 필드 생성
createAddressInputFields('container-id', {
    zipCodeId: 'my-zipcode',
    roadAddressId: 'my-road-address',
    jibunAddressId: 'my-jibun-address',
    detailAddressId: 'my-detail-address',
    addressInputId: 'my-address',
    latitudeId: 'my-latitude',
    longitudeId: 'my-longitude'
});
```

## 🔌 API 엔드포인트

### 1. 주소 중복 체크

```http
POST /api/admin/check-address-duplicate
Content-Type: application/json

{
    "address": "서울특별시 강남구 테헤란로 123",
    "exclude_id": 123,
    "entity_type": "brand",
    "similarity_threshold": 0.8
}
```

**응답:**
```json
{
    "success": true,
    "duplicate": false,
    "similar_addresses": [],
    "message": "중복된 주소가 없습니다.",
    "normalized_address": "서울특별시 강남구 테헤란로 123"
}
```

### 2. 주소 유효성 검증

```http
POST /api/admin/validate-address
Content-Type: application/json

{
    "address": "서울특별시 강남구 테헤란로 123"
}
```

**응답:**
```json
{
    "success": true,
    "valid": true,
    "message": "유효한 주소입니다.",
    "normalized_address": "서울특별시 강남구 테헤란로 123",
    "validation_details": {
        "length": 15,
        "korean_words": 4,
        "numbers": 1,
        "has_special_chars": false,
        "word_count": 4
    }
}
```

### 3. 주소 좌표 변환

```http
POST /api/admin/geocode-address
Content-Type: application/json

{
    "address": "서울특별시 강남구 테헤란로 123"
}
```

**응답:**
```json
{
    "success": true,
    "latitude": 37.5665,
    "longitude": 126.9780,
    "formatted_address": "서울특별시 강남구 테헤란로 123",
    "normalized_address": "서울특별시 강남구 테헤란로 123"
}
```

### 4. 주소 자동완성 제안

```http
POST /api/admin/address-suggestions
Content-Type: application/json

{
    "query": "서울 강남",
    "limit": 5,
    "entity_type": "all"
}
```

**응답:**
```json
{
    "success": true,
    "suggestions": [
        "서울특별시 강남구 테헤란로 123",
        "서울특별시 강남구 역삼동 456",
        "서울특별시 강남구 삼성동 789"
    ],
    "query": "서울 강남"
}
```

### 5. 주소 통계

```http
GET /api/admin/address-statistics
```

**응답:**
```json
{
    "success": true,
    "statistics": {
        "brands": {
            "total_with_address": 150,
            "with_coordinates": 120,
            "coordinate_percentage": 80.0
        },
        "stores": {
            "total_with_address": 500,
            "with_coordinates": 450,
            "coordinate_percentage": 90.0
        },
        "employees": {
            "total_with_address": 1000,
            "with_coordinates": 800,
            "coordinate_percentage": 80.0
        }
    }
}
```

### 6. 캐시 관리

```http
POST /api/admin/clear-address-cache
Content-Type: application/json
```

**응답:**
```json
{
    "success": true,
    "message": "캐시가 초기화되었습니다. (25개 항목 제거)"
}
```

## 🎛️ 설정 옵션

### JavaScript 설정

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `apiKey` | string | 'YOUR_KAKAO_API_KEY' | 카카오 API 키 |
| `enableAutoComplete` | boolean | true | 자동완성 활성화 |
| `enableValidation` | boolean | true | 실시간 검증 활성화 |
| `enableCoordinates` | boolean | true | 좌표 자동 조회 활성화 |
| `debounceDelay` | number | 300 | 검색 지연시간 (ms) |
| `maxSuggestions` | number | 5 | 최대 제안 수 |

### 백엔드 설정

| 설정 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `kakao_api_key` | string | - | 카카오 API 키 |
| `default_similarity_threshold` | float | 0.8 | 기본 유사도 임계값 |
| `max_suggestions` | int | 5 | 최대 제안 수 |
| `debounce_delay` | int | 300 | 검색 지연시간 |
| `enable_cache` | boolean | true | 캐시 활성화 |
| `cache_ttl` | int | 300 | 캐시 유효시간 (초) |
| `geocode_cache_ttl` | int | 3600 | 좌표 캐시 유효시간 (초) |

## 📊 성능 최적화

### 1. 캐싱 전략
- **주소 검증 결과**: 1분 캐시
- **좌표 변환 결과**: 1시간 캐시
- **자동완성 제안**: 5분 캐시

### 2. 데이터베이스 최적화
- 주소가 있는 레코드만 조회
- 인덱스 활용
- 배치 처리 지원

### 3. API 호출 최적화
- 디바운싱을 통한 중복 요청 방지
- 에러 재시도 로직
- 타임아웃 설정

## 🔍 모니터링 및 로깅

### 1. 성능 모니터링
- API 실행 시간 추적
- 캐시 히트율 모니터링
- 데이터베이스 쿼리 성능

### 2. 오류 로깅
- API 오류 상세 로그
- 사용자 입력 오류 추적
- 시스템 오류 알림

### 3. 사용 통계
- 주소 검색 빈도
- 좌표 변환 성공률
- 사용자 만족도 지표

## 🛡️ 보안 고려사항

### 1. API 키 보안
- 환경변수 사용
- 설정 파일 암호화
- 정기적인 키 로테이션

### 2. 입력 검증
- XSS 방지
- SQL 인젝션 방지
- 주소 형식 검증

### 3. 접근 제어
- 관리자 권한 확인
- API 요청 제한
- 로그 감사

## 🚨 문제 해결

### 1. 일반적인 문제

**Q: 카카오 API 키 오류**
```
A: 환경변수 KAKAO_API_KEY가 올바르게 설정되었는지 확인하세요.
```

**Q: 주소 검색이 작동하지 않음**
```
A: 브라우저 콘솔에서 JavaScript 오류를 확인하고, 네트워크 연결을 점검하세요.
```

**Q: 좌표 변환이 실패함**
```
A: 카카오 Geocoding API 키가 유효한지 확인하고, 주소 형식이 올바른지 점검하세요.
```

### 2. 성능 문제

**Q: 주소 검색이 느림**
```
A: 캐시 설정을 확인하고, 데이터베이스 인덱스를 점검하세요.
```

**Q: 메모리 사용량이 높음**
```
A: 캐시 TTL을 조정하고, 불필요한 데이터를 정리하세요.
```

### 3. 디버깅

```javascript
// 디버그 모드 활성화
const addressSearch = new AddressSearch({
    debug: true,
    onError: function(message) {
        console.error('주소 검색 오류:', message);
    }
});
```

## 🔄 업데이트 내역

### v2.0.0 (최신)
- 자동완성 기능 추가
- 성능 모니터링 시스템
- 캐싱 시스템 개선
- 관리 대시보드 추가
- 설정 관리 페이지
- 실시간 검증 강화

### v1.0.0
- 기본 주소 검색 기능
- 카카오 API 연동
- 좌표 변환 기능
- 중복 체크 기능

## 📞 지원

문제가 발생하거나 추가 기능이 필요한 경우:

1. 로그 파일 확인: `logs/address_search.log`
2. 관리자 대시보드에서 시스템 상태 확인
3. 설정 페이지에서 API 키 및 옵션 점검
4. 개발팀에 문의

---

**참고**: 이 시스템은 카카오 주소 검색 API를 사용합니다. API 사용량 제한 및 정책을 확인하시기 바랍니다. 