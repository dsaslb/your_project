"""
동기화 시스템 테스트 스크립트
"""
import os
import sys
import requests
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_health_endpoints():
    """헬스체크 엔드포인트 테스트"""
    base_url = "http://localhost:5000"
    
    print("🏥 헬스체크 엔드포인트 테스트")
    print("=" * 50)
    
    # /healthz 테스트
    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        print(f"✅ /healthz: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   DB 상태: {data.get('database', {}).get('status', 'unknown')}")
            print(f"   시스템 상태: {'정상' if data.get('ok') else '비정상'}")
    except Exception as e:
        print(f"❌ /healthz: {e}")
    
    # /readyz 테스트
    try:
        response = requests.get(f"{base_url}/readyz", timeout=5)
        print(f"✅ /readyz: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   전체 상태: {'준비됨' if data.get('ok') else '준비 안됨'}")
    except Exception as e:
        print(f"❌ /readyz: {e}")
    
    # /metrics 테스트
    try:
        response = requests.get(f"{base_url}/metrics", timeout=5)
        print(f"✅ /metrics: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Outbox 이벤트: {data.get('outbox', {}).get('total_events', 0)}개")
    except Exception as e:
        print(f"❌ /metrics: {e}")

def test_batch_sync():
    """배치 동기화 API 테스트"""
    base_url = "http://localhost:5000"
    
    print("\n🔄 배치 동기화 API 테스트")
    print("=" * 50)
    
    # 테스트 데이터
    test_data = {
        "items": [
            {
                "type": "attendance",
                "idem": "test-attendance-001",
                "payload": {
                    "user_id": 1,
                    "type": "in",
                    "lat": 37.5665,
                    "lng": 126.9780,
                    "timestamp": "2024-01-15T09:00:00Z"
                }
            },
            {
                "type": "inventory",
                "idem": "test-inventory-001", 
                "payload": {
                    "user_id": 1,
                    "barcode": "1234567890",
                    "quantity": 10,
                    "timestamp": "2024-01-15T09:05:00Z"
                }
            }
        ],
        "meta": {
            "device_id": "test-device-001",
            "branch_id": 1,
            "user_id": 1
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/mobile/sync/batch",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "X-Idempotency-Key": "test-batch-001"
            },
            timeout=10
        )
        
        print(f"✅ 배치 동기화: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   처리 결과: {data.get('stats', {})}")
            print(f"   처리 시간: {data.get('processing_time_ms', 0)}ms")
        else:
            print(f"   오류: {response.text}")
            
    except Exception as e:
        print(f"❌ 배치 동기화: {e}")

def test_sync_status():
    """동기화 상태 조회 테스트"""
    base_url = "http://localhost:5000"
    
    print("\n📊 동기화 상태 조회 테스트")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/mobile/sync/status", timeout=5)
        print(f"✅ 동기화 상태: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            outbox = data.get('outbox', {})
            print(f"   Outbox 상태:")
            print(f"     - 전체 이벤트: {outbox.get('total', 0)}개")
            print(f"     - 대기 중: {outbox.get('pending', 0)}개")
            print(f"     - 전송 완료: {outbox.get('delivered', 0)}개")
            print(f"     - 실패: {outbox.get('failed', 0)}개")
    except Exception as e:
        print(f"❌ 동기화 상태: {e}")

def main():
    """메인 테스트 함수"""
    print("🧪 동기화 시스템 테스트 시작")
    print("=" * 60)
    
    # 서버가 실행 중인지 확인
    try:
        response = requests.get("http://localhost:5000/", timeout=3)
        print("✅ 서버가 실행 중입니다")
    except Exception as e:
        print("❌ 서버가 실행되지 않았습니다. 먼저 서버를 시작하세요.")
        print("   python app.py")
        return
    
    # 각 테스트 실행
    test_health_endpoints()
    test_batch_sync()
    test_sync_status()
    
    print("\n🎉 테스트 완료!")
    print("=" * 60)

if __name__ == '__main__':
    main()
