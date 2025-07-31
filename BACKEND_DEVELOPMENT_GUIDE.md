# 백엔드 개발 가이드

## 📋 목차
1. [개발 환경 설정](#개발-환경-설정)
2. [프로젝트 구조](#프로젝트-구조)
3. [코딩 스타일](#코딩-스타일)
4. [테스트 작성](#테스트-작성)
5. [API 개발](#api-개발)
6. [데이터베이스 관리](#데이터베이스-관리)
7. [보안 가이드라인](#보안-가이드라인)
8. [성능 최적화](#성능-최적화)
9. [배포 가이드](#배포-가이드)

## 🚀 개발 환경 설정

### 필수 요구사항
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (선택사항)

### 초기 설정
```bash
# 1. 저장소 클론
git clone <repository-url>
cd your_program

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 개발 의존성 설치
pip install -r requirements-dev.txt

# 4. Pre-commit 설정
pre-commit install

# 5. 데이터베이스 설정
make setup-db
```

### 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# 필수 환경 변수
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-jwt-secret
```

## 📁 프로젝트 구조

```
your_program/
├── api/                    # API 엔드포인트
├── models/                 # 데이터베이스 모델
├── routes/                 # 라우트 정의
├── utils/                  # 유틸리티 함수
├── config/                 # 설정 파일
├── tests/                  # 테스트 코드
│   ├── unit/              # 단위 테스트
│   ├── integration/       # 통합 테스트
│   ├── api/               # API 테스트
│   └── performance/       # 성능 테스트
├── migrations/            # 데이터베이스 마이그레이션
├── logs/                  # 로그 파일
├── uploads/               # 업로드 파일
└── docs/                  # 문서
```

## 🎨 코딩 스타일

### Python 스타일 가이드
- **PEP 8** 준수
- **Black** 포맷터 사용 (라인 길이: 120)
- **isort** import 정렬
- **mypy** 타입 힌트 사용

### 코드 예시
```python
"""
모듈 설명
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session

from models.user import User
from utils.auth import require_auth
from utils.validators import validate_email


# Blueprint 정의
api_bp = Blueprint('api', __name__)


@api_bp.route('/users', methods=['GET'])
@require_auth
def get_users() -> Dict[str, Any]:
    """
    사용자 목록 조회
    
    Returns:
        Dict[str, Any]: 사용자 목록과 메타데이터
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'success': True,
            'data': [user.to_dict() for user in users.items],
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500


@api_bp.route('/users', methods=['POST'])
def create_user() -> Dict[str, Any]:
    """
    사용자 생성
    
    Returns:
        Dict[str, Any]: 생성된 사용자 정보
    """
    data = request.get_json()
    
    # 입력 검증
    if not validate_email(data.get('email')):
        return {
            'success': False,
            'error': 'Invalid email format'
        }, 400
    
    try:
        user = User(
            email=data['email'],
            username=data['username'],
            password=data['password']
        )
        user.save()
        
        return {
            'success': True,
            'data': user.to_dict()
        }, 201
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500
```

## 🧪 테스트 작성

### 테스트 구조
```python
"""
사용자 API 테스트
"""
import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from models.user import User


@pytest.fixture
def app() -> Flask:
    """테스트용 Flask 앱 생성"""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app: Flask):
    """테스트 클라이언트"""
    return app.test_client()


@pytest.fixture
def db_session(app: Flask):
    """테스트용 데이터베이스 세션"""
    with app.app_context():
        engine = create_engine(app.config['TESTING_DATABASE_URI'])
        Session = sessionmaker(bind=engine)
        session = Session()
        
        yield session
        
        session.close()
        engine.dispose()


class TestUserAPI:
    """사용자 API 테스트 클래스"""
    
    def test_get_users_success(self, client, db_session):
        """사용자 목록 조회 성공 테스트"""
        # Given
        user = User(email='test@example.com', username='testuser')
        db_session.add(user)
        db_session.commit()
        
        # When
        response = client.get('/api/users')
        
        # Then
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['email'] == 'test@example.com'
    
    def test_create_user_success(self, client, db_session):
        """사용자 생성 성공 테스트"""
        # Given
        user_data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'password123'
        }
        
        # When
        response = client.post('/api/users', json=user_data)
        
        # Then
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['email'] == 'new@example.com'
    
    def test_create_user_invalid_email(self, client):
        """잘못된 이메일로 사용자 생성 실패 테스트"""
        # Given
        user_data = {
            'email': 'invalid-email',
            'username': 'newuser',
            'password': 'password123'
        }
        
        # When
        response = client.post('/api/users', json=user_data)
        
        # Then
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid email format' in data['error']
```

### 테스트 실행
```bash
# 모든 테스트 실행
make test

# 특정 테스트만 실행
make test-unit
make test-integration
make test-api
make test-performance

# 커버리지 확인
pytest --cov=. --cov-report=html
```

## 🔌 API 개발

### RESTful API 설계 원칙
1. **리소스 중심 설계**
2. **HTTP 메서드 적절히 사용**
3. **일관된 응답 형식**
4. **적절한 HTTP 상태 코드 사용**

### API 응답 형식
```python
# 성공 응답
{
    "success": true,
    "data": {...},
    "meta": {
        "page": 1,
        "per_page": 10,
        "total": 100
    }
}

# 에러 응답
{
    "success": false,
    "error": "Error message",
    "code": "ERROR_CODE"
}
```

### API 문서화
```python
@api_bp.route('/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id: int) -> Dict[str, Any]:
    """
    특정 사용자 조회
    
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: 사용자 ID
    responses:
      200:
        description: 사용자 정보 조회 성공
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
      404:
        description: 사용자를 찾을 수 없음
    """
    user = User.query.get_or_404(user_id)
    return {
        'success': True,
        'data': user.to_dict()
    }
```

## 🗄️ 데이터베이스 관리

### 모델 정의
```python
"""
사용자 모델
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class User(Base):
    """사용자 모델"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, email: str, username: str, password: str):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """비밀번호 확인"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def save(self):
        """저장"""
        from extensions import db
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """삭제"""
        from extensions import db
        db.session.delete(self)
        db.session.commit()
```

### 마이그레이션
```bash
# 마이그레이션 생성
flask db migrate -m "Add user table"

# 마이그레이션 적용
flask db upgrade

# 마이그레이션 롤백
flask db downgrade
```

## 🔒 보안 가이드라인

### 인증 및 권한
```python
from functools import wraps
from flask import request, jsonify
import jwt

def require_auth(f):
    """인증 필요 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        try:
            token = token.split(' ')[1]  # Bearer token
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            request.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated
```

### 입력 검증
```python
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """사용자 데이터 검증 스키마"""
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=8))

def validate_user_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """사용자 데이터 검증"""
    schema = UserSchema()
    errors = []
    
    try:
        schema.load(data)
    except ValidationError as e:
        errors.extend(e.messages.values())
    
    return len(errors) == 0, errors
```

### SQL 인젝션 방지
```python
# ❌ 잘못된 방법
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ 올바른 방법
user = User.query.get(user_id)
# 또는
user = User.query.filter_by(id=user_id).first()
```

## ⚡ 성능 최적화

### 데이터베이스 최적화
```python
# N+1 문제 해결
users = User.query.options(joinedload('posts')).all()

# 페이지네이션
users = User.query.paginate(page=page, per_page=per_page)

# 인덱스 사용
class User(Base):
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_username', 'username'),
    )
```

### 캐싱
```python
from flask_caching import Cache

cache = Cache()

@cache.memoize(timeout=300)
def get_user_by_id(user_id: int) -> User:
    """사용자 정보 캐싱"""
    return User.query.get(user_id)

@cache.cached(timeout=60)
def get_active_users() -> List[User]:
    """활성 사용자 목록 캐싱"""
    return User.query.filter_by(is_active=True).all()
```

### 비동기 처리
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def send_email_task(user_id: int, subject: str, body: str):
    """이메일 전송 비동기 작업"""
    user = User.query.get(user_id)
    # 이메일 전송 로직
    pass
```

## 🚀 배포 가이드

### Docker 배포
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### 환경별 설정
```python
# config/production.py
class ProductionConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # 프로덕션 전용 설정
```

### 배포 스크립트
```bash
#!/bin/bash
# deploy.sh

# 1. 코드 업데이트
git pull origin main

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 데이터베이스 마이그레이션
flask db upgrade

# 4. 테스트 실행
pytest tests/ -v

# 5. 서버 재시작
sudo systemctl restart your-program
```

## 📚 추가 리소스

- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [Pytest 문서](https://docs.pytest.org/)
- [Python 보안 가이드](https://python-security.readthedocs.io/)

## 🤝 기여 가이드

1. Fork 저장소
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📞 지원

문제가 있거나 질문이 있으시면:
- Issue 생성
- 개발팀에 문의
- 문서 확인 