import requests

# 간단한 상태 확인
print("=== 서버 상태 확인 ===")
try:
    response = requests.get('http://192.168.45.44:5000/health')
    print(f'Health Status: {response.status_code}')
    print(f'Health Response: {response.text}')
except Exception as e:
    print(f'Health check failed: {e}')

# API 상태 확인
print("\n=== API 상태 확인 ===")
try:
    response = requests.get('http://192.168.45.44:5000/api/status')
    print(f'API Status: {response.status_code}')
    print(f'API Response: {response.text}')
except Exception as e:
    print(f'API status check failed: {e}')

# 업종 목록 조회 (GET 요청)
print("\n=== 업종 목록 조회 ===")
try:
    response = requests.get('http://192.168.45.44:5000/api/admin/industries')
    print(f'Industries Status: {response.status_code}')
    print(f'Industries Response: {response.text}')
except Exception as e:
    print(f'Industries list failed: {e}') 