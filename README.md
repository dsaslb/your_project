# 🍽️ 레스토랑 직원 관리 시스템

Flask 기반의 직원 출근 및 스케줄 관리 시스템입니다.

## 🚀 주요 기능

- **🔐 보안**: 비밀번호 해싱, 역할 기반 접근 제어(RBAC)
- **👥 사용자 관리**: 관리자/매니저/직원 역할 구분, 승인 시스템
- **⏰ 출근 관리**: 출근/퇴근 기록, 근태 판정(지각/조퇴/정상)
- **📊 통계**: 일별/주별/월별 출근 통계, 사용자별 근무 시간
- **📝 로깅**: 모든 사용자 액션 로그 기록
- **🔄 소프트 삭제**: 데이터 안전한 삭제 처리

## 🛠️ 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=sqlite:///restaurant.db
FLASK_ENV=development
```

### 3. 데이터베이스 초기화

```bash
# Flask 앱 실행
python app.py

# 새 터미널에서 샘플 데이터 생성
python -c "from utils.sample_data import create_sample_data; from app import create_app; app = create_app(); app.app_context().push(); create_sample_data()"
```

### 4. 서버 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000`으로 접속하세요.

## 👤 기본 계정

| 역할 | 사용자명 | 비밀번호 | 설명 |
|------|----------|----------|------|
| 관리자 | admin01 | adminpass | 전체 시스템 관리 |
| 매니저 | manager01 | managerpass | 직원 관리 |
| 직원 | employee01 | employeepass | 출근 기록 |
| 직원 | employee02 | employeepass | 출근 기록 |
| 직원 | employee03 | employeepass | 출근 기록 |
| 직원 | employee04 | employeepass | 출근 기록 |
| 직원 | employee05 | employeepass | 출근 기록 |
| 승인대기 | newemployee | newpass | 관리자 승인 필요 |

## 📁 프로젝트 구조

```
restaurant_project/
├── app.py                 # Flask 앱 메인 파일
├── config.py              # 환경 설정
├── requirements.txt       # Python 패키지 목록
├── .env                   # 환경변수 (생성 필요)
├── models/                # 데이터 모델
│   ├── __init__.py
│   ├── user.py           # 사용자 모델
│   ├── attendance.py     # 출근 기록 모델
│   └── action_log.py     # 액션 로그 모델
├── routes/                # 라우트 (Blueprint)
│   ├── __init__.py
│   ├── auth.py           # 인증 관련
│   ├── admin.py          # 관리자 기능
│   └── employee.py       # 직원 기능
├── templates/             # HTML 템플릿
│   ├── base.html         # 기본 템플릿
│   ├── auth/             # 인증 페이지
│   ├── admin/            # 관리자 페이지
│   └── employee/         # 직원 페이지
├── static/                # 정적 파일
│   └── style.css         # CSS 스타일
└── utils/                 # 유틸리티
    ├── decorators.py     # 데코레이터
    ├── logger.py         # 로깅 유틸리티
    └── sample_data.py    # 샘플 데이터 생성
```

## 🔧 주요 API

### 인증 API

- `GET /login` - 로그인 페이지
- `POST /login` - 로그인 처리
- `GET /logout` - 로그아웃
- `GET /register` - 회원가입 페이지
- `POST /register` - 회원가입 처리

### 관리자 API

- `GET /admin/dashboard` - 관리자 대시보드
- `GET /admin/users` - 사용자 목록
- `POST /admin/users/<id>/approve` - 사용자 승인
- `POST /admin/users/<id>/reject` - 사용자 거절
- `POST /admin/users/<id>/delete` - 사용자 삭제
- `GET /admin/attendance` - 출근 기록 목록
- `GET /admin/logs` - 액션 로그 목록

### 직원 API

- `GET /employee/dashboard` - 직원 대시보드
- `POST /employee/clock_in` - 출근 기록
- `POST /employee/clock_out` - 퇴근 기록
- `GET /employee/attendance` - 내 출근 기록

## 🔒 보안 기능

### 비밀번호 보안
- 모든 비밀번호는 Werkzeug의 `generate_password_hash`로 해싱
- 평문 비밀번호는 절대 저장하지 않음

### 역할 기반 접근 제어 (RBAC)
- `admin`: 전체 시스템 관리
- `manager`: 직원 관리 및 통계 조회
- `employee`: 개인 출근 기록만 관리

### 입력 검증
- 모든 사용자 입력에 대한 검증
- SQL Injection 방지
- XSS 공격 방지

### 로깅 및 감사
- 모든 사용자 액션 로그 기록
- IP 주소 및 User-Agent 정보 저장
- 로그인 실패 시도 기록

## 📊 데이터 모델

### User 모델
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")
    status = db.Column(db.String(20), nullable=False, default="pending")
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Attendance 모델
```python
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clock_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    clock_out = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## 🚀 배포 가이드

### 개발 환경
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### 프로덕션 환경
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Nginx 설정 (별도 관리)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 문제 해결

### 일반적인 문제

1. **데이터베이스 오류**
   ```bash
   # 데이터베이스 파일 삭제 후 재생성
   rm instance/restaurant.db
   python app.py
   ```

2. **패키지 설치 오류**
   ```bash
   # 가상환경 재생성
   deactivate
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # 또는 venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **권한 오류**
   ```bash
   # 파일 권한 확인
   chmod 755 app.py
   chmod 644 requirements.txt
   ```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요. 