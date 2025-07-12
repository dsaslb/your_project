# Core Framework - 확장형 모듈 시스템

## 📁 프로젝트 구조
```
core_framework/
├── backend/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── app.py              # 메인 Flask 앱
│   │   ├── config.py           # 설정 관리
│   │   ├── database.py         # 데이터베이스 연결
│   │   ├── auth.py             # 인증 시스템
│   │   ├── permissions.py      # 권한 관리
│   │   └── utils.py            # 공통 유틸리티
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── base/               # 기본 모듈 인터페이스
│   │   └── your_program/         # 외식업 모듈 (예시)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── core/               # 코어 API
│   │   └── modules/            # 모듈별 API
│   └── templates/
│       ├── core/               # 코어 템플릿
│       └── modules/            # 모듈별 템플릿
├── frontend/
│   ├── src/
│   │   ├── core/               # 코어 컴포넌트
│   │   ├── modules/            # 모듈별 컴포넌트
│   │   └── shared/             # 공통 컴포넌트
│   └── public/
└── shared/
    ├── models/                 # 공통 데이터 모델
    ├── services/               # 공통 서비스
    └── types/                  # 공통 타입 정의
```

## 🎯 코어 기능
- **인증 & 권한**: 사용자 관리, 역할 기반 접근 제어
- **모듈 시스템**: 플러그인 방식 모듈 로딩
- **API 프레임워크**: RESTful API 표준
- **데이터베이스**: ORM 및 마이그레이션
- **템플릿 엔진**: 동적 템플릿 렌더링
- **로깅**: 중앙화된 로그 관리
- **설정 관리**: 환경별 설정 분리

## 🔌 모듈 시스템
- **BaseModule**: 모든 모듈의 기본 인터페이스
- **자동 등록**: 모듈 디렉토리 자동 스캔
- **의존성 관리**: 모듈 간 의존성 해결
- **API 라우팅**: 모듈별 API 자동 등록
- **템플릿 관리**: 모듈별 템플릿 분리

## 🚀 확장 방법
1. `modules/` 디렉토리에 새 모듈 생성
2. `BaseModule` 상속하여 구현
3. 자동으로 API, 템플릿, 라우트 등록
4. 코어 수정 없이 기능 확장 
