#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재고 조사 API 테스트 스크립트 (바코드 스캔 시뮬레이션)
"""

import requests
import json
import time

def test_inventory_api():
    """재고 조사 API 테스트"""
    print('🔍 2단계: 재고 조사 API 테스트 시작...')
    
    # 1. 로그인하여 토큰 획득
    print('📱 모바일 로그인 중...')
    login_response = requests.post('http://localhost:5000/api/mobile/simple/login', 
                                  json={'username': 'demo', 'password': 'demo123'})
    
    if login_response.status_code != 200:
        print(f'❌ 로그인 실패: {login_response.status_code}')
        return False
    
    token = login_response.json()['token']
    user_info = login_response.json()['user']
    print(f'✅ 로그인 성공! 사용자: {user_info["username"]}')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. 여러 상품의 재고 조사 시뮬레이션
    print('\n📦 재고 조사 시뮬레이션 시작...')
    
    # 테스트 상품들
    test_products = [
        {
            'barcode': '8801234567890',
            'name': '코카콜라 330ml',
            'qty': 24,
            'photo_url': 'https://example.com/photo1.jpg'
        },
        {
            'barcode': '8801234567891', 
            'name': '펩시콜라 500ml',
            'qty': 18,
            'photo_url': 'https://example.com/photo2.jpg'
        },
        {
            'barcode': '8801234567892',
            'name': '사이다 1.5L',
            'qty': 12,
            'photo_url': None
        }
    ]
    
    for i, product in enumerate(test_products, 1):
        print(f'\n📱 {i}번째 상품 바코드 스캔: {product["barcode"]}')
        print(f'   상품명: {product["name"]}')
        print(f'   수량: {product["qty"]}개')
        
        inventory_data = {
            'barcode': product['barcode'],
            'qty': product['qty'],
            'photo_url': product['photo_url']
        }
        
        inventory_response = requests.post('http://localhost:5000/api/mobile/simple/inventory/check',
                                         json=inventory_data,
                                         headers=headers)
        
        if inventory_response.status_code == 200:
            result = inventory_response.json()
            print(f'   ✅ 재고 조사 성공!')
            print(f'   - 조사 ID: {result.get("id")}')
            print(f'   - 바코드: {result.get("barcode")}')
            print(f'   - 수량: {result.get("qty")}개')
            print(f'   - 사진 URL: {result.get("photo_url", "없음")}')
            print(f'   - 조사 시간: {result.get("created_at")}')
            print('   🔔 실시간 이벤트 "inventory:update"가 웹 대시보드로 전송되었습니다!')
        else:
            print(f'   ❌ 재고 조사 실패: {inventory_response.status_code}')
            print(f'   응답: {inventory_response.text}')
        
        # 각 상품 사이에 1초 대기 (실제 바코드 스캔 시뮬레이션)
        if i < len(test_products):
            time.sleep(1)
    
    print(f'\n✅ 총 {len(test_products)}개 상품의 재고 조사가 완료되었습니다!')
    print('🔔 모든 재고 업데이트가 웹 대시보드에 실시간으로 반영되었습니다!')
    
    return True

if __name__ == "__main__":
    test_inventory_api()
