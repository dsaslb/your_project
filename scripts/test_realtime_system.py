#!/usr/bin/env python3
"""
실시간 시스템 API 테스트 스크립트
"""

import requests
import json
import uuid
import time
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def generate_idempotency_key():
    """UUID 기반 멱등성 키 생성"""
    return str(uuid.uuid4())

def test_mobile_purchase_order_creation():
    """모바일 발주 생성 API 테스트"""
    print("🔍 모바일 발주 생성 API 테스트")
    
    # 테스트 데이터
    test_data = {
        "branch_id": 1,
        "items": [
            {"barcode": "123456789", "name": "테스트 상품 A", "qty": 5},
            {"barcode": "987654321", "name": "테스트 상품 B", "qty": 3}
        ],
        "notes": "테스트 발주입니다."
    }
    
    # 멱등성 키 생성
    idempotency_key = generate_idempotency_key()
    
    headers = {
        "Content-Type": "application/json",
        "X-Idempotency-Key": idempotency_key,
        "Authorization": "Bearer test-token-123"  # 테스트용 인증 토큰
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/mobile/purchase_orders",
            json=test_data,
            headers=headers
        )
        
        print(f"📤 요청 데이터: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        print(f"🔑 멱등성 키: {idempotency_key}")
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 내용: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ 발주 생성 성공!")
            return response.json().get("id")
        else:
            print("❌ 발주 생성 실패!")
            return None
            
    except Exception as e:
        print(f"❌ API 호출 오류: {str(e)}")
        return None

def test_purchase_order_status_update(po_id):
    """발주 상태 변경 API 테스트"""
    print(f"🔍 관리자 발주 상태 변경 API 테스트 (발주 ID: {po_id})")
    
    test_data = {
        "status": "approved",
        "notes": "테스트 승인입니다."
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer admin-token-456"  # 관리자 테스트용 토큰
    }
    
    try:
        # po_id가 문자열인 경우 정수로 변환 시도
        try:
            numeric_id = int(po_id) if isinstance(po_id, str) else po_id
        except (ValueError, TypeError):
            # UUID 형태의 문자열인 경우 테스트용 ID 사용
            numeric_id = 999
            print(f"⚠️ 발주 ID '{po_id}'를 숫자로 변환할 수 없어 테스트용 ID {numeric_id}를 사용합니다.")
        
        response = requests.put(
            f"{API_BASE}/admin/purchase_orders/{numeric_id}/status",
            json=test_data,
            headers=headers
        )
        
        print(f"📤 요청 데이터: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        print(f"📤 사용된 ID: {numeric_id}")
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 내용: {response.text}")
        
        if response.status_code == 200:
            print("✅ 발주 상태 변경 성공!")
        else:
            print("❌ 발주 상태 변경 실패!")
            
    except Exception as e:
        print(f"❌ API 호출 오류: {str(e)}")

def test_purchase_order_count():
    """발주 카운트 API 테스트"""
    print("🔍 발주 카운트 API 테스트")
    
    headers = {
        "Authorization": "Bearer admin-token-456"  # 관리자 테스트용 토큰
    }
    
    try:
        response = requests.get(
            f"{API_BASE}/admin/purchase_orders/count",
            headers=headers
        )
        
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 내용: {response.text}")
        
        if response.status_code == 200:
            print("✅ 발주 카운트 조회 성공!")
        else:
            print("❌ 발주 카운트 조회 실패!")
            
    except Exception as e:
        print(f"❌ API 호출 오류: {str(e)}")

def test_duplicate_idempotency_key():
    """중복 멱등성 키 테스트"""
    print("🔍 중복 멱등성 키 테스트")
    
    # 동일한 키로 두 번 요청
    idempotency_key = generate_idempotency_key()
    
    test_data = {
        "branch_id": 1,
        "items": [{"barcode": "999999999", "name": "중복 테스트 상품", "qty": 1}],
        "notes": "중복 요청 테스트입니다."
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Idempotency-Key": idempotency_key,
        "Authorization": "Bearer test-token-123"  # 테스트용 인증 토큰
    }
    
    try:
        # 첫 번째 요청
        print(f"🔑 첫 번째 요청 (키: {idempotency_key})")
        response1 = requests.post(
            f"{API_BASE}/mobile/purchase_orders",
            json=test_data,
            headers=headers
        )
        print(f"📥 첫 번째 응답: {response1.status_code}")
        
        # 두 번째 요청 (동일한 키)
        print(f"🔑 두 번째 요청 (동일한 키: {idempotency_key})")
        response2 = requests.post(
            f"{API_BASE}/mobile/purchase_orders",
            json=test_data,
            headers=headers
        )
        print(f"📥 두 번째 응답: {response2.status_code}")
        
        if response2.status_code == 200 and "duplicate" in response2.text:
            print("✅ 중복 요청 방지 성공!")
        else:
            print("❌ 중복 요청 방지 실패!")
            
    except Exception as e:
        print(f"❌ API 호출 오류: {str(e)}")

def test_websocket_connection():
    """웹소켓 연결 테스트"""
    print("🔍 웹소켓 연결 테스트")
    print("⚠️ 웹소켓 테스트는 브라우저에서 수동으로 진행해야 합니다.")
    print("📋 브라우저 콘솔에서 다음 코드를 실행하세요:")
    print("""
    // Socket.IO 클라이언트 테스트
    const socket = io('ws://localhost:5000');
    
    socket.on('connect', () => {
        console.log('🔌 웹소켓 연결됨:', socket.id);
    });
    
    socket.on('po:created', (data) => {
        console.log('📋 발주 생성 이벤트:', data);
    });
    
    socket.on('po:status', (data) => {
        console.log('📋 발주 상태 변경 이벤트:', data);
    });
    
    socket.on('disconnect', (reason) => {
        console.log('🔌 웹소켓 연결 해제:', reason);
    });
    """)

def main():
    """메인 테스트 실행"""
    print("🚀 실시간 시스템 API 테스트 시작")
    print("=" * 50)
    
    # 1. 모바일 발주 생성 테스트
    po_id = test_mobile_purchase_order_creation()
    print()
    
    # 2. 관리자 발주 상태 변경 테스트
    test_purchase_order_status_update(po_id)
    print()
    
    # 3. 발주 카운트 테스트
    test_purchase_order_count()
    print()
    
    # 4. 중복 멱등성 키 테스트
    test_duplicate_idempotency_key()
    print()
    
    # 5. 웹소켓 연결 테스트 안내
    test_websocket_connection()
    print()
    
    print("=" * 50)
    print("✅ 모든 테스트 완료!")
    print("📋 웹소켓 테스트는 브라우저에서 수동으로 진행하세요.")

if __name__ == "__main__":
    main()
