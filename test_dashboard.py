"""
대시보드 API 테스트 스크립트
"""
import requests
import json

def test_dashboard_api():
    """대시보드 API 테스트"""
    base_url = "http://localhost:5000"
    
    print("🧪 대시보드 API 테스트")
    print("=" * 50)
    
    # 1. 헬스체크 테스트
    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        print(f"✅ 헬스체크: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   DB 상태: {data.get('database', {}).get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ 헬스체크 실패: {e}")
        return
    
    # 2. 대시보드 API 테스트
    try:
        print("\n📊 대시보드 API 테스트...")
        response = requests.get(f"{base_url}/api/mobile/dashboard", timeout=10)
        print(f"✅ 대시보드 API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📋 응답 데이터:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 오류 응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 대시보드 API 실패: {e}")
    
    # 3. 다른 엔드포인트들 테스트
    endpoints = [
        "/readyz",
        "/metrics",
        "/api/mobile/sync/status"
    ]
    
    print("\n🔍 기타 엔드포인트 테스트...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == '__main__':
    test_dashboard_api()
