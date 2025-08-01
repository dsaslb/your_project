import requests
import json

# 로그인 없이 업종 생성 테스트
print("=== 로그인 없이 업종 생성 테스트 ===")
industry_data = {
    'name': '테스트업종',
    'code': 'TEST001',
    'color': '#ff0000',
    'status': 'active'
}

try:
    response = requests.post('http://192.168.45.44:5000/api/admin/industries',
                            json=industry_data,
                            headers={'Content-Type': 'application/json'})
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'Error: {e}') 