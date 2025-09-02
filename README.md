# 멀티테넌시 관리 시스템

업종-브랜드-매장-직원 계층 구조와 플러그인 시스템을 지원하는 Flask 기반 웹 애플리케이션입니다.

## 🚀 주요 기능

### 🔧 핵심 시스템
- **계층별 권한 관리**: 업종 → 브랜드 → 매장 → 직원
- **플러그인 시스템**: 확장 가능한 모듈식 아키텍처
- **실시간 대시보드**: WebSocket 기반 실시간 데이터 업데이트
- **AI 통합**: 머신러닝 및 예측 분석

### 📊 관리 기능
- **브랜드 관리**: 브랜드 생성, 설정, 모니터링
- **매장 관리**: 매장별 운영 데이터 관리
- **직원 관리**: 출퇴근, 스케줄, 성과 관리
- **QSC 관리**: 품질, 서비스, 청결 평가 시스템

### 🔌 플러그인 마켓플레이스
- **플러그인 업로드**: 개발자용 플러그인 등록 시스템
- **승인 관리**: 업로드된 플러그인 검토 및 승인
- **설치 관리**: 브랜드/매장별 플러그인 설치
- **UI 스키마**: JSON 기반 자동 UI 생성

## 🛠️ 기술 스택

### Backend
- **Flask 2.3.3**: Python 웹 프레임워크
- **SQLAlchemy 2.0.23**: ORM
- **Flask-SocketIO 5.3.6**: 실시간 통신
- **Pandas 2.1.4**: 데이터 분석
- **NumPy 1.25.2**: 수치 계산

### Frontend
- **Next.js**: React 프레임워크
- **TypeScript**: 타입 안전성
- **Tailwind CSS**: 스타일링
- **Socket.IO Client**: 실시간 통신

### Database
- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 캐싱 및 세션 저장

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/dsaslb/your_program.git
cd your_program
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
# 개발 환경
make install-dev

# 또는 프로덕션 환경
make install
```

### 4. 환경 변수 설정
```bash
cp env.example .env
# .env 파일을 편집하여 데이터베이스 연결 정보 등 설정
```

### 5. 데이터베이스 초기화
```bash
make setup-db
```

### 6. 애플리케이션 실행
```bash
# 개발 서버
make dev

# 프로덕션 서버 (Gunicorn)
make run

# 자동 재시작 개발 서버
make run-dev
```

서버가 http://localhost:5000 에서 실행됩니다.

## 🛠️ 개발 도구

### 코드 품질 관리
```bash
# 코드 포맷팅
make format

# 린팅 검사
make lint

# 전체 시스템 점검
make check
```

### 테스트
```bash
# 모든 테스트 실행
make test

# 단위 테스트만 실행
make test-unit

# API 테스트만 실행
make test-api

# 성능 테스트 실행
make test-performance
```

### 시스템 관리
```bash
# 시스템 최적화
make optimize

# 데이터베이스 백업
make backup

# 데이터베이스 복원
make restore BACKUP_FILE=backups/app_backup_20240101_120000.db

# 로그 정리
make logs-clean

# 시스템 상태 확인
make health-check
```

### Docker 사용
```bash
# Docker 이미지 빌드
make docker-build

# Docker 컨테이너 실행
make docker-run

# Docker Compose로 전체 서비스 실행
make docker-compose-up

# Docker Compose 서비스 중지
make docker-compose-down
```

## 🔌 플러그인 개발

### 플러그인 구조
```
plugins/
├── your_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   ├── ui_schema.json
│   └── README.md
```

### UI 스키마 예시
```json
{
  "menu": {
    "title": "AI 스케줄 추천",
    "icon": "Calendar",
    "position": 1
  },
  "dashboard": {
    "type": "card",
    "title": "스케줄 최적화",
    "description": "AI가 추천한 최적 스케줄",
    "component": "ScheduleOptimizer",
    "size": "medium"
  }
}
```

### 플러그인 업로드
1. 관리자 대시보드 → "플러그인 관리" 클릭
2. "플러그인 업로드" 버튼 클릭
3. 플러그인 정보 및 파일 업로드
4. 승인 대기 → 관리자 승인 → 마켓플레이스 등록

## 🧪 테스트

### 테스트 실행
```bash
# 전체 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=. --cov-report=html

# 특정 테스트 파일 실행
pytest tests/test_basic.py
```

### 린팅
```bash
# 코드 스타일 검사
flake8 .

# 타입 검사
mypy .

# 코드 포맷팅
black .
```

## 📁 프로젝트 구조

```
your_program/
├── app.py                 # 메인 애플리케이션
├── models/               # 데이터 모델
│   ├── __init__.py
│   └── plugin_models.py
├── api/                  # API 엔드포인트
├── templates/            # HTML 템플릿
│   ├── admin/           # 관리자 페이지
│   └── plugin_marketplace.html
├── frontend/            # Next.js 프론트엔드
├── plugins/             # 플러그인 디렉토리
├── tests/               # 테스트 파일
├── requirements.txt     # Python 의존성
└── README.md           # 프로젝트 문서
```

## 🔐 환경 변수

필요한 환경 변수들을 `.env` 파일에 설정하세요:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-jwt-secret
```

## 🚀 배포

### Docker를 사용한 배포
```bash
# Docker 이미지 빌드
docker build -t your-program .

# 컨테이너 실행
docker run -p 5000:5000 your-program
```

### GitHub Actions
프로젝트는 GitHub Actions를 통해 자동 CI/CD가 설정되어 있습니다:
- **테스트**: Python 3.9, 3.10, 3.11, 3.13.2에서 테스트 실행
- **보안 스캔**: Snyk를 통한 보안 취약점 검사
- **배포**: 스테이징/프로덕션 환경 자동 배포

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 있거나 질문이 있으시면 [Issues](https://github.com/dsaslb/your_program/issues)를 통해 문의해주세요.

## 🔄 업데이트 로그

### v1.0.0 (2024-01-27)
- ✨ 플러그인 업로드 및 승인 시스템 구축
- 🔧 SQLAlchemy 모델 충돌 해결
- 🐛 프론트엔드 정렬 에러 수정
- 🚀 플러그인 마켓플레이스 구현
- 📊 계층별 플러그인 관리 시스템

---

**개발자**: [Your Name]  
**버전**: 1.0.0  
**최종 업데이트**: 2024-01-27

