import requests
import json

def test_api():
    # 근태 관리용 API 테스트
    url = "http://localhost:5000/api/staff?page_type=attendance"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                staff_count = len(data.get('staff', []))
                print(f"근태 관리 직원 수: {staff_count}명")
                for staff in data.get('staff', [])[:5]:  # 처음 5명만 출력
                    print(f"  - {staff.get('name')} ({staff.get('status')})")
            else:
                print(f"API 오류: {data.get('error')}")
        else:
            print(f"HTTP 오류: {response.status_code}")
            
    except Exception as e:
        print(f"요청 오류: {e}")

if __name__ == "__main__":
    test_api() 