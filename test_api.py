import requests
import json

# 로그인 테스트
print("=== 로그인 테스트 ===")
login_response = requests.post('http://192.168.45.44:5000/api/auth/login', 
                              json={'username': 'admin', 'password': 'admin123'})
print(f'Login Status: {login_response.status_code}')
print(f'Login Response: {login_response.text}')
print(f'Login Cookies: {dict(login_response.cookies)}')

# 세션 생성
session = requests.Session()
session.cookies.update(login_response.cookies)

# 업종 생성 테스트
print("\n=== 업종 생성 테스트 ===")
industry_data = {
    'name': '테스트업종',
    'code': 'TEST001',
    'color': '#ff0000',
    'status': 'active'
}

industry_response = session.post('http://192.168.45.44:5000/api/admin/industries',
                                json=industry_data,
                                headers={'Content-Type': 'application/json'})
print(f'Industry Creation Status: {industry_response.status_code}')
print(f'Industry Creation Response: {industry_response.text}') 