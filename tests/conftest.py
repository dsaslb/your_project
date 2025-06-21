import pytest
import sys
import os
import requests
import time

# Add the parent directory to sys.path to allow importing app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from models import db, User, Notice
from config import TestConfig

API_URL = "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def ensure_admin():
    """세션 시작 시 관리자 계정이 존재하는지 확인하고 없으면 생성"""
    try:
        # 서버가 실행 중인지 확인
        requests.get(f"{API_URL}/", timeout=5)
        
        # 관리자 계정 생성 시도
        resp = requests.post(f"{API_URL}/register", data={
            "username": "admin",
            "password": "admin123",
            "email": "admin@test.com",
            "role": "admin"
        }, timeout=10)
        
        # 이미 존재하면 무시 (409 또는 다른 상태 코드)
        if resp.status_code not in [200, 201, 409]:
            print(f"Warning: Admin account creation failed with status {resp.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Warning: Flask server is not running. API tests will fail.")
    except Exception as e:
        print(f"Warning: Error ensuring admin account: {e}")
    
    yield

@pytest.fixture
def admin_token(ensure_admin):
    """관리자 토큰을 반환하는 fixture"""
    try:
        payload = {"username": "admin", "password": "admin123"}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("token")
        else:
            print(f"Warning: Admin login failed with status {resp.status_code}")
            return None
    except Exception as e:
        print(f"Warning: Error getting admin token: {e}")
        return None

@pytest.fixture
def test_user_token():
    """테스트용 일반 사용자 토큰을 반환하는 fixture"""
    try:
        # 테스트 사용자 생성 시도
        resp = requests.post(f"{API_URL}/register", data={
            "username": "testuser",
            "password": "test123",
            "email": "test@test.com",
            "role": "employee"
        }, timeout=10)
        
        # 로그인
        payload = {"username": "testuser", "password": "test123"}
        resp = requests.post(f"{API_URL}/api/auth/login", json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("token")
        else:
            print(f"Warning: Test user login failed with status {resp.status_code}")
            return None
    except Exception as e:
        print(f"Warning: Error getting test user token: {e}")
        return None

@pytest.fixture(scope='session')
def app():
    """Session-wide test `Flask` application."""
    flask_app.config.from_object(TestConfig)
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    """Creates a new database session for a test, and rolls back changes after."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        db.session.begin_nested()

        @db.event.listens_for(db.session, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.begin_nested()
        
        yield db.session
        
        db.session.remove()
        transaction.rollback()
        connection.close()

@pytest.fixture()
def admin_user(session):
    """Fixture for a test admin user."""
    user = User(username='testadmin', email='admin@example.com', role='admin', status='approved')
    user.set_password('a-very-secure-admin-password-123')
    session.add(user)
    session.commit()
    return user

@pytest.fixture()
def notice(session, admin_user):
    """Fixture for a sample notice."""
    n = Notice(title="Original Title", content="Original Content", author_id=admin_user.id, category="공지사항")
    session.add(n)
    session.commit()
    return n 