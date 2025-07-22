# 빠른 시작 (Quick Start Guide)

---

## 1. 프로젝트 클론 및 환경 준비

```bash
git clone https://github.com/yourorg/your_program.git
cd your_program
python -m venv venv
source venv/bin/activate  # 또는 venv\Scripts\activate
pip install -r requirements.txt
cd frontend && npm install
```

---

## 2. 환경 변수/설정 파일 준비

- `config/production.env` 또는 `.env` 파일을 복사/수정
- DB, Redis, Stripe, Email 등 주요 환경 변수 입력

---

## 3. 개발 서버 실행

```bash
# 백엔드
python app.py
# 프론트엔드
cd frontend && npm run dev
```

---

## 4. Docker로 전체 서비스 실행

```bash
docker-compose up --build -d
```

---

## 5. 관리자 대시보드 접속

- http://localhost:3000/admin-dashboard
- (기본 관리자 계정/비밀번호는 운영자에게 문의)

---

## 6. 주요 기능/테스트

- 브랜드/지점/직원/플러그인/결제/통계/알림/운영 자동화 등 대시보드에서 확인
- API 테스트: `pytest tests/ --cov=. --cov-report=html`
- 부하 테스트: `python tests/test_load.py`

---

## 7. 배포/운영

- 배포: `docker-compose.yml`, `scripts/deploy.sh`, `docs/DEPLOYMENT_GUIDE.md` 참고
- 운영 체크리스트: `docs/OPERATIONS_CHECKLIST.md` 참고
- 장애/복구: `scripts/auto_recover.sh` 실행

---

## 8. 문의/지원

- 관리자/운영자: admin@yourprogram.com
- 기술 지원: support@yourprogram.com
- 슬랙: #your-program-support 