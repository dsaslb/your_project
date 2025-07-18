# 멀티테넌시 관리 시스템

업종 → 브랜드 → 매장 → 직원 계층별 관리 및 플러그인 ON/OFF/권한 분배 시스템

## 🚀 시스템 개요

### 아키텍처
- **백엔드**: Flask + SQLAlchemy + PostgreSQL
- **프론트엔드**: Next.js + TypeScript + Tailwind CSS
- **데이터베이스**: PostgreSQL (프로덕션) / SQLite (개발)
- **캐시**: Redis
- **컨테이너**: Docker + Docker Compose
- **모니터링**: Prometheus + Grafana

### 계층 구조
```
업종(Industry) → 브랜드(Brand) → 매장(Branch) → 직원(Staff/User)
```

### 주요 기능
- ✅ 계층별 CRUD API (업종/브랜드/매장/직원)
- ✅ 플러그인 ON/OFF 및 권한 분배
- ✅ MVP 플러그인 (출근/재고/구매/스케줄/AI분석)
- ✅ 권한 체크 및 인증 시스템
- ✅ 에러 로깅 및 모니터링
- ✅ 샘플 데이터 자동 삽입
- ✅ 반응형 관리자 대시보드

## 📋 요구사항

### 시스템 요구사항
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ (프로덕션)
- Redis 7+
- Docker & Docker Compose (선택사항)

### 개발 환경
- Windows 10/11, macOS, Linux
- Git
- VS Code (권장)

## 🛠️ 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd your_program
```

### 2. 백엔드 설정

#### 개발 환경
```bash
# Python 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export FLASK_ENV=development
export SECRET_KEY=your-secret-key

# 데이터베이스 초기화
python app.py
```

#### 프로덕션 환경
```bash
# 프로덕션 설정 적용
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:password@localhost/multitenancy
export REDIS_URL=redis://localhost:6379/0

# 배포 스크립트 실행
chmod +x scripts/deploy.sh
./scripts/deploy.sh production
```

### 3. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build
npm start
```

### 4. Docker 실행 (권장)

```bash
# 전체 시스템 실행
docker-compose up -d

# 특정 서비스만 실행
docker-compose up backend frontend db redis

# 로그 확인
docker-compose logs -f backend
```

## 🌐 접근 URL

### 개발 환경
- **메인 페이지**: http://localhost:3000
- **업종 관리자**: http://localhost:3000/admin/industry
- **브랜드 관리자**: http://localhost:3000/admin/brand
- **매장 관리자**: http://localhost:3000/admin/branch
- **직원 페이지**: http://localhost:3000/user
- **백엔드 API**: http://localhost:5000

### 프로덕션 환경
- **메인 페이지**: https://your-domain.com
- **관리자 대시보드**: https://your-domain.com/admin/industry
- **API 문서**: https://your-domain.com/api/docs

## 📚 API 문서

### 주요 엔드포인트

#### 업종 관리
```http
GET    /api/industries          # 업종 목록 조회
POST   /api/industries          # 업종 생성
PUT    /api/industries/<id>     # 업종 수정
DELETE /api/industries/<id>     # 업종 삭제
```

#### 브랜드 관리
```http
GET    /api/brands              # 브랜드 목록 조회
POST   /api/brands              # 브랜드 생성
PUT    /api/brands/<id>         # 브랜드 수정
DELETE /api/brands/<id>         # 브랜드 삭제
```

#### 매장 관리
```http
GET    /api/branches            # 매장 목록 조회
POST   /api/branches            # 매장 생성
PUT    /api/branches/<id>       # 매장 수정
DELETE /api/branches/<id>       # 매장 삭제
```

#### 직원 관리
```http
GET    /api/users               # 직원 목록 조회
POST   /api/users               # 직원 생성
PUT    /api/users/<id>          # 직원 수정
DELETE /api/users/<id>          # 직원 삭제
```

#### 플러그인 관리
```http
GET    /api/plugins             # 플러그인 목록 조회
POST   /api/plugins/<id>/enable # 플러그인 활성화
POST   /api/plugins/<id>/disable # 플러그인 비활성화
POST   /api/plugins/<id>/access-control/brand  # 브랜드별 권한 설정
POST   /api/plugins/<id>/access-control/branch # 매장별 권한 설정
POST   /api/plugins/<id>/access-control/user   # 직원별 권한 설정
```

## 🔧 플러그인 시스템

### 기본 플러그인
1. **출근 관리** - 직원 출근/퇴근 기록 및 통계
2. **재고 관리** - 상품별 재고 추적 및 알림
3. **구매 관리** - 발주/공급업체 관리
4. **스케줄 관리** - 직원 스케줄 및 근무표
5. **AI 분석** - 매출/근태/운영 데이터 분석

### 플러그인 권한 분배
- **업종 관리자**: 모든 플러그인 관리 가능
- **브랜드 관리자**: 할당된 플러그인만 관리 가능
- **매장 관리자**: 할당된 플러그인만 관리 가능
- **직원**: 권한이 있는 플러그인만 사용 가능

## 🧪 테스트

### 자동화 테스트
```bash
# 전체 테스트 실행
python -m pytest tests/ -v

# 특정 테스트 실행
python -m pytest tests/test_multitenancy.py::MultitenancyTestCase::test_industry_crud -v

# 커버리지 테스트
python -m pytest tests/ --cov=. --cov-report=html
```

### 수동 테스트
```bash
# 통합 테스트 체크리스트 확인
cat docs/integration_test_checklist.md

# 주요 시나리오 테스트
cat docs/usage_checklist.md
```

## 📊 모니터링

### 로그 확인
```bash
# 에러 로그
tail -f logs/errors.log

# 애플리케이션 로그
tail -f logs/app.log

# 성능 로그
tail -f logs/performance.log
```

### 모니터링 대시보드
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### 헬스 체크
```bash
# 백엔드 헬스 체크
curl http://localhost:5000/health

# 프론트엔드 헬스 체크
curl http://localhost:3000/api/health
```

## 🔒 보안

### 인증/인가
- JWT 토큰 기반 인증
- 계층별 권한 체크
- API 요청 제한 (Rate Limiting)
- CSRF 보호

### 데이터 보안
- 민감한 데이터 암호화
- SQL 인젝션 방지
- XSS 공격 방지
- HTTPS 강제 적용 (프로덕션)

## 🚀 배포

### Docker 배포
```bash
# 이미지 빌드
docker build -t multitenancy-system .

# 컨테이너 실행
docker-compose up -d

# 배포 확인
docker-compose ps
```

### 수동 배포
```bash
# 배포 스크립트 실행
./scripts/deploy.sh production

# 서비스 상태 확인
systemctl status multitenancy-backend
systemctl status multitenancy-frontend
```

## 📈 성능 최적화

### 데이터베이스 최적화
- 인덱스 최적화
- 쿼리 최적화
- 커넥션 풀링

### 캐시 전략
- Redis 캐시 활용
- API 응답 캐싱
- 정적 파일 캐싱

### 프론트엔드 최적화
- 코드 스플리팅
- 이미지 최적화
- 번들 크기 최적화

## 🐛 문제 해결

### 일반적인 문제

#### 백엔드 서버 시작 실패
```bash
# 포트 확인
netstat -tulpn | grep :5000

# 로그 확인
tail -f logs/errors.log

# 데이터베이스 연결 확인
python -c "from app import app, db; print('DB 연결 성공')"
```

#### 프론트엔드 빌드 실패
```bash
# Node.js 버전 확인
node --version

# 의존성 재설치
rm -rf node_modules package-lock.json
npm install

# 캐시 정리
npm cache clean --force
```

#### Docker 컨테이너 문제
```bash
# 컨테이너 로그 확인
docker-compose logs -f

# 컨테이너 재시작
docker-compose restart

# 볼륨 정리
docker-compose down -v
```

## 📞 지원

### 문서
- [API 문서](docs/api.md)
- [플러그인 개발 가이드](docs/plugin-development.md)
- [배포 가이드](docs/deployment.md)
- [문제 해결 가이드](docs/troubleshooting.md)

### 로그 및 모니터링
- 에러 로그: `logs/errors.log`
- 성능 로그: `logs/performance.log`
- 모니터링: Grafana 대시보드

### 연락처
- 이슈 리포트: GitHub Issues
- 기술 지원: support@example.com
- 문서: [Wiki](https://github.com/your-repo/wiki)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여

프로젝트에 기여하고 싶으시다면:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 변경 이력

### v1.0.0 (2024-06-01)
- ✅ 멀티테넌시 구조 구현
- ✅ 플러그인 시스템 구현
- ✅ 관리자 대시보드 구현
- ✅ 권한 체크 시스템 구현
- ✅ Docker 컨테이너화
- ✅ 모니터링 시스템 구현

---

**멀티테넌시 관리 시스템** - 업종/브랜드/매장/직원 계층별 통합 관리 플랫폼

