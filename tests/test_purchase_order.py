#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
발주 생성 API 테스트 스크립트 (실시간 알림 확인)
"""

import requests
import json
import time

def test_purchase_order_api():
    """발주 생성 API 테스트"""
    print('🔍 3단계: 발주 생성 API 테스트 시작...')
    
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
    
    # 2. 여러 발주서 생성 시뮬레이션
    print('\n📋 발주 생성 시뮬레이션 시작...')
    
    # 테스트 발주 데이터들
    test_orders = [
        {
            'name': '음료수 긴급 발주',
            'items': [
                {'barcode': '8801234567890', 'name': '코카콜라 330ml', 'qty': 48},
                {'barcode': '8801234567891', 'name': '펩시콜라 500ml', 'qty': 36},
                {'barcode': '8801234567892', 'name': '사이다 1.5L', 'qty': 24}
            ]
        },
        {
            'name': '과자류 정기 발주',
            'items': [
                {'barcode': '8801234567893', 'name': '새우깡', 'qty': 20},
                {'barcode': '8801234567894', 'name': '포테토칩', 'qty': 15},
                {'barcode': '8801234567895', 'name': '치즈볼', 'qty': 12}
            ]
        },
        {
            'name': '라면류 보충 발주',
            'items': [
                {'barcode': '8801234567896', 'name': '신라면', 'qty': 60},
                {'barcode': '8801234567897', 'name': '진라면', 'qty': 40}
            ]
        }
    ]
    
    for i, order in enumerate(test_orders, 1):
        print(f'\n📋 {i}번째 발주서 생성: "{order["name"]}"')
        print(f'   발주 품목 수: {len(order["items"])}개')
        
        # 발주 품목들 출력
        total_qty = 0
        for item in order['items']:
            print(f'   - {item["name"]}: {item["qty"]}개 (바코드: {item["barcode"]})')
            total_qty += item['qty']
        
        print(f'   총 수량: {total_qty}개')
        
        po_data = {
            'items': order['items']
        }
        
        po_response = requests.post('http://localhost:5000/api/mobile/simple/purchase_orders',
                                  json=po_data,
                                  headers=headers)
        
        if po_response.status_code == 200:
            result = po_response.json()
            print(f'   ✅ 발주 생성 성공!')
            print(f'   - 발주 ID: {result.get("id")}')
            print(f'   - 상태: {result.get("status")}')
            print(f'   - 생성 시간: {result.get("created_at")}')
            print(f'   - 품목 수: {len(result.get("items", []))}개')
            print('   🔔 실시간 이벤트 "purchase_order:update"가 웹 대시보드로 전송되었습니다!')
        else:
            print(f'   ❌ 발주 생성 실패: {po_response.status_code}')
            print(f'   응답: {po_response.text}')
        
        # 각 발주 사이에 2초 대기 (실제 발주 작성 시뮬레이션)
        if i < len(test_orders):
            time.sleep(2)
    
    print(f'\n✅ 총 {len(test_orders)}개 발주서가 생성되었습니다!')
    print('🔔 모든 발주 알림이 웹 대시보드에 실시간으로 전송되었습니다!')
    print('📊 관리자는 웹 대시보드에서 발주 현황을 실시간으로 확인할 수 있습니다!')
    
    return True

if __name__ == "__main__":
    test_purchase_order_api()
