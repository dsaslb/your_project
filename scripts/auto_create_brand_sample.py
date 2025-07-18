import requests
import re
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"
session = requests.Session()

# 1. CSRF 토큰 추출
login_page = session.get(f"{BASE_URL}/login")
soup = BeautifulSoup(login_page.text, "html.parser")
csrf_token = soup.find("input", {"name": "csrf_token"})
csrf_token = csrf_token["value"] if csrf_token else None
assert csrf_token, "CSRF 토큰 추출 실패"

# 2. 로그인(admin)
login_resp = session.post(f"{BASE_URL}/login", data={
    "username": "admin",
    "password": "admin123",
    "csrf_token": csrf_token
}, allow_redirects=True)
assert login_resp.ok, f"로그인 실패: {login_resp.text}"

# 로그인 후 최신 CSRF 토큰 추출
login_page2 = session.get(f"{BASE_URL}/login")
soup2 = BeautifulSoup(login_page2.text, "html.parser")
csrf_token2 = soup2.find("input", {"name": "csrf_token"})
csrf_token2 = csrf_token2["value"] if csrf_token2 else None
assert csrf_token2, "로그인 후 CSRF 토큰 추출 실패"
headers = {"X-CSRFToken": csrf_token2}

# 3. 브랜드 생성
brand_data = {
    "name": "AI테스트브랜드",
    "description": "자동화 테스트용 샘플 브랜드",
    "contact_email": "admin@example.com",
    "contact_phone": "010-0000-0000",
    "address": "서울시 테스트구 테스트로 1",
    "industry_id": 1,
    "create_frontend_server": True
}
brand_resp = session.post(f"{BASE_URL}/api/admin/brands", json=brand_data, headers=headers)
assert brand_resp.ok, f"브랜드 생성 실패: {brand_resp.text}"
brand_id = brand_resp.json()["brand"]["id"]
print(f"브랜드 생성 완료: {brand_id}")

# 4. 매장 생성
store_data = {
    "name": "AI테스트매장1",
    "address": "서울시 테스트구 테스트로 2",
    "brand_id": brand_id
}
store_resp = session.post(f"{BASE_URL}/stores", json=store_data, headers=headers)
assert store_resp.ok, f"매장 생성 실패: {store_resp.text}"
store_id = store_resp.json()["store_id"]
print(f"매장 생성 완료: {store_id}")

# 5. 직원 생성
user_data = {
    "username": "ai_manager",
    "password": "test1234",
    "name": "AI매니저",
    "email": "ai_manager@example.com",
    "role": "brand_manager",
    "brand_id": brand_id,
    "status": "approved"
}
user_resp = session.post(f"{BASE_URL}/api/admin/users", json=user_data, headers=headers)
assert user_resp.ok, f"직원 생성 실패: {user_resp.text}"
user_id = user_resp.json()["user"]["id"]
print(f"직원 생성 완료: {user_id}")

# 6. 개선요청 샘플 생성
improve_data = {
    "title": "테스트 개선요청",
    "description": "자동화 테스트용 개선요청",
    "category": "운영",
    "priority": "중요",
    "brand_id": brand_id
}
improve_resp = session.post(f"{BASE_URL}/improvement_requests", json=improve_data, headers=headers)
print(f"개선요청 생성 결과: {improve_resp.text}") 