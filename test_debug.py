import requests
import json

# 간단한 POST 요청 테스트
print("=== 간단한 POST 요청 테스트 ===")

# 1. 빈 데이터로 테스트
try:
    response = requests.post('http://192.168.45.44:5000/api/admin/industries',
                            json={},
                            headers={'Content-Type': 'application/json'})
    print(f'Empty data - Status: {response.status_code}')
    print(f'Empty data - Response: {response.text}')
except Exception as e:
    print(f'Empty data - Error: {e}')

print("\n" + "="*50 + "\n")

# 2. 최소 데이터로 테스트
try:
    response = requests.post('http://192.168.45.44:5000/api/admin/industries',
                            json={'name': 'test', 'code': 'TEST'},
                            headers={'Content-Type': 'application/json'})
    print(f'Minimal data - Status: {response.status_code}')
    print(f'Minimal data - Response: {response.text}')
except Exception as e:
    print(f'Minimal data - Error: {e}')

print("\n" + "="*50 + "\n")

# 3. Content-Type 없이 테스트
try:
    response = requests.post('http://192.168.45.44:5000/api/admin/industries',
                            json={'name': 'test', 'code': 'TEST'})
    print(f'No Content-Type - Status: {response.status_code}')
    print(f'No Content-Type - Response: {response.text}')
except Exception as e:
    print(f'No Content-Type - Error: {e}') 