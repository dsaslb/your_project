import os
import sys

# Add the parent directory to sys.path to allow importing app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time

import pytest
import requests

from app import app as flask_app
from config import TestConfig
from models import Notice, User, db

API_URL = "http://localhost:5000"

# @pytest.fixture(scope="session", autouse=True)
# def ensure_admin():
#     """세션 시작 시 관리자 계정이 존재하는지 확인하고 없으면 생성"""
#     try:
#         # 서버가 실행 중인지 확인
#         requests.get(f"{API_URL}/", timeout=5)

#         # 관리자 계정 생성 시도
#         resp = requests.post(f"{API_URL}/register", data={
#             "username": "admin",
#             "password": "admin123",
#             "email": "admin@test.com",
#             "role": "admin"
#         }, timeout=10)

#         # 이미 존재하면 무시 (409 또는 다른 상태 코드)
#         if resp.status_code not in [200, 201, 409]:
#             print(f"Warning: Admin account creation failed with status {resp.status_code}")

#     except requests.exceptions.ConnectionError:
#         print("Warning: Flask server is not running. API tests will fail.")
#     except Exception as e:
#         print(f"Warning: Error ensuring admin account: {e}")

#     yield

# @pytest.fixture
# def admin_token(ensure_admin):
#     """관리자 토큰을 반환하는 fixture"""
#     try:
#         payload = {"username": "admin", "password": "admin123"}
#         resp = requests.post(f"{API_URL}/api/auth/login", json=payload, timeout=10)
#         if resp.status_code == 200:
#             return resp.json().get("token")
#         else:
#             print(f"Warning: Admin login failed with status {resp.status_code}")
#             return None
#     except Exception as e:
#         print(f"Warning: Error getting admin token: {e}")
#         return None

# @pytest.fixture
# def test_user_token():
#     """테스트용 일반 사용자 토큰을 반환하는 fixture"""
#     try:
#         # 테스트 사용자 생성 시도
#         resp = requests.post(f"{API_URL}/register", data={
#             "username": "testuser",
#             "password": "test123",
#             "email": "test@test.com",
#             "role": "employee"
#         }, timeout=10)

#         # 로그인
#         payload = {"username": "testuser", "password": "test123"}
#         resp = requests.post(f"{API_URL}/api/auth/login", json=payload, timeout=10)
#         if resp.status_code == 200:
#             return resp.json().get("token")
#         else:
#             print(f"Warning: Test user login failed with status {resp.status_code}")
#             return None
#     except Exception as e:
#         print(f"Warning: Error getting test user token: {e}")
#         return None


@pytest.fixture(scope="session")
def app():
    """세션 단위의 Flask 앱 생성"""
    flask_app.config.from_object(TestConfig)

    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    """테스트용 클라이언트"""
    return app.test_client()


@pytest.fixture(scope="function")
def session(app):
    """
    각 테스트 함수에 대해 깨끗한 DB 세션을 제공합니다.
    테스트 시작 전에 모든 테이블을 삭제하고 재생성합니다.
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.session.remove()


@pytest.fixture()
def admin_user(session):
    """Fixture for a test admin user."""
    user = User(
        username="testadmin", email="admin@example.com", role="admin", status="approved"
    )
    user.set_password("a-very-secure-admin-password-123")
    session.add(user)
    session.flush()
    return user


@pytest.fixture()
def notice(session, admin_user):
    """Fixture for a sample notice."""
    n = Notice(
        title="Original Title",
        content="Original Content",
        author_id=admin_user.id,
        category="공지사항",
    )
    session.add(n)
    session.flush()
    return n


@pytest.fixture
def admin_token(client, admin_user, session):
    """Logs in the admin user and returns a JWT token."""
    session.add(admin_user)
    session.commit()

    login_payload = {
        "username": admin_user.username,
        "password": "a-very-secure-admin-password-123",
    }
    resp = client.post("/api/auth/login", json=login_payload)

    if resp.status_code != 200:
        pytest.fail(
            f"Admin login failed with status {resp.status_code}: {resp.data.decode()}"
        )

    token = resp.json.get("token")
    if not token:
        pytest.fail("Failed to retrieve admin token.")

    return token


@pytest.fixture
def admin_headers(admin_token):
    """Returns authorization headers for the admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def logged_in_admin_client(client, admin_user, session):
    """A client logged in as the admin user using web session login."""
    with client:
        # DB에 admin_user가 실제로 저장되어 있어야 /auth/login이 작동합니다.
        session.add(admin_user)
        session.commit()
        client.post(
            "/auth/login",
            data={
                "username": admin_user.username,
                "password": "a-very-secure-admin-password-123",
            },
            follow_redirects=True,
        )
        yield client


# @pytest.fixture(scope="session")
# def ensure_admin(app):
#     """
#     테스트 전에 관리자 계정이 있는지 확인하고 없으면 생성
#     """
#     with app.app_context():
#         admin = User.query.filter_by(username="admin_user").first()
#         if not admin:
#             admin = User(username="admin_user", email="admin@test.com", is_admin=True)
#             admin.set_password("admin_password")
#             db.session.add(admin)
#             db.session.commit()

#         test_user = User.query.filter_by(username="test_user").first()
#         if not test_user:
#             test_user = User(username="test_user", email="test@test.com", is_admin=False)
#             test_user.set_password("test_password")
#             db.session.add(test_user)
#             db.session.commit()

# @pytest.fixture
# def admin_token(ensure_admin):
#     """
#     관리자 토큰 발급
#     """
#     login_data = {"username": "admin_user", "password": "admin_password"}
#     response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
#     assert response.status_code == 200
#     return response.json()["access_token"]

# @pytest.fixture
# def test_user_token(ensure_admin):
#     """
#     일반 사용자 토큰 발급
#     """
#     login_data = {"username": "test_user", "password": "test_password"}
#     response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
#     assert response.status_code == 200
#     return response.json()["access_token"]
