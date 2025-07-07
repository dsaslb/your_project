#!/usr/bin/env python3
"""
백엔드 라우트 테스트 스크립트
각 엔드포인트가 정상 작동하는지 확인합니다.
"""

import requests
import json
from datetime import datetime

# 서버 기본 URL
BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, method="GET", data=None):
    """엔드포인트 테스트 함수"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text}")
        
        print()
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print()
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {str(e)}")
        print()
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 백엔드 라우트 테스트 시작")
    print("=" * 50)
    
    # 테스트할 엔드포인트 목록
    endpoints = [
        # 대시보드
        ("/api/dashboard/stats", "GET"),
        ("/api/dashboard/activities", "GET"),
        ("/api/dashboard/charts", "GET"),
        
        # 스케줄
        ("/api/schedule", "GET"),
        ("/api/schedule", "POST", {"staff": "테스트", "date": "2024-01-16", "shift": "오전"}),
        ("/api/schedule/1", "GET"),
        ("/api/schedule/calendar", "GET"),
        
        # 직원
        ("/api/staff", "GET"),
        ("/api/staff", "POST", {"name": "테스트직원", "email": "test@test.com", "role": "employee"}),
        ("/api/staff/1", "GET"),
        ("/api/staff/stats", "GET"),
        
        # 발주
        ("/api/orders", "GET"),
        ("/api/orders", "POST", {"item": "테스트물품", "quantity": 10, "unit": "개"}),
        ("/api/orders/1", "GET"),
        ("/api/orders/stats", "GET"),
        
        # 재고
        ("/api/inventory", "GET"),
        ("/api/inventory", "POST", {"name": "테스트재고", "quantity": 50, "unit": "개"}),
        ("/api/inventory/1", "GET"),
        ("/api/inventory/low-stock", "GET"),
        ("/api/inventory/stats", "GET"),
        
        # 알림/공지
        ("/api/notifications", "GET"),
        ("/api/notices", "GET"),
        ("/api/notifications", "POST", {"title": "테스트알림", "content": "테스트내용"}),
        ("/api/notices", "POST", {"title": "테스트공지", "content": "테스트내용"}),
        ("/api/notifications/stats", "GET"),
        ("/api/notices/stats", "GET"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint_info in endpoints:
        if len(endpoint_info) == 2:
            endpoint, method = endpoint_info
            data = None
        else:
            endpoint, method, data = endpoint_info
        
        if test_endpoint(endpoint, method, data):
            success_count += 1
    
    print("=" * 50)
    print(f"📊 테스트 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 엔드포인트가 정상 작동합니다!")
    else:
        print("⚠️  일부 엔드포인트에 문제가 있습니다.")
        print("   서버 로그를 확인하거나 인증 문제를 확인해보세요.")

if __name__ == "__main__":
    main() 