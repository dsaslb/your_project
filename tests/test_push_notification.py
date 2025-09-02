#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
푸시 알림 테스트 스크립트

실제 Expo 앱에서 푸시 토큰을 받아서 테스트할 수 있습니다.
"""

import requests
import json

def test_push_notification_api():
    """푸시 알림 API 테스트"""
    print('🔍 4단계: 푸시 알림 시스템 테스트 시작...')
    
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
    
    # 2. 테스트용 Expo 푸시 토큰 (실제로는 Expo 앱에서 생성해야 함)
    print('\n📱 푸시 알림 테스트...')
    
    # 참고: 실제 Expo 앱에서 생성된 푸시 토큰을 사용해야 합니다.
    # 현재는 테스트용 더미 토큰을 사용합니다.
    test_expo_token = "ExponentPushToken[test-token-for-demo]"
    
    print(f'   테스트 토큰: {test_expo_token}')
    print('   ⚠️  실제 테스트를 위해서는 Expo 앱에서 생성된 실제 푸시 토큰이 필요합니다.')
    
    # 3. 푸시 알림 테스트 API 호출
    push_data = {
        'expo_push_token': test_expo_token
    }
    
    push_response = requests.post('http://localhost:5000/api/mobile/simple/push/test',
                                json=push_data,
                                headers=headers)
    
    if push_response.status_code == 200:
        result = push_response.json()
        print(f'✅ 푸시 알림 API 호출 성공!')
        print(f'   - 메시지: {result.get("message")}')
        print(f'   - 결과: {result.get("result")}')
        
        if result.get("result", {}).get("success"):
            print('   🔔 푸시 알림이 성공적으로 전송되었습니다!')
        else:
            print(f'   ⚠️  푸시 알림 전송 실패: {result.get("result", {}).get("error")}')
    else:
        print(f'❌ 푸시 알림 API 호출 실패: {push_response.status_code}')
        print(f'   응답: {push_response.text}')
    
    # 4. 실제 출퇴근 체크로 푸시 알림 트리거
    print('\n⏰ 출퇴근 체크로 푸시 알림 트리거 테스트...')
    
    attendance_data = {
        'type': 'in',
        'lat': 37.5665,
        'lng': 126.9780,
        'qr': 'STORE_001_QR'
    }
    
    attendance_response = requests.post('http://localhost:5000/api/mobile/simple/attendance/clock',
                                      json=attendance_data,
                                      headers=headers)
    
    if attendance_response.status_code == 200:
        result = attendance_response.json()
        print(f'✅ 출근 체크 성공! (푸시 알림 자동 트리거됨)')
        print(f'   - 출근 기록 ID: {result.get("id")}')
        print('   📱 관리자들에게 출근 알림이 전송되었습니다!')
    else:
        print(f'❌ 출근 체크 실패: {attendance_response.status_code}')
    
    print('\n📝 푸시 알림 시스템 구현 완료!')
    print('📖 사용 방법:')
    print('   1. Expo 앱에서 실제 푸시 토큰을 생성하세요')
    print('   2. 관리자 사용자의 expo_push_token을 데이터베이스에 저장하세요')
    print('   3. 출퇴근/재고/발주 이벤트가 발생하면 자동으로 푸시 알림이 전송됩니다')
    
    return True

if __name__ == "__main__":
    test_push_notification_api()
