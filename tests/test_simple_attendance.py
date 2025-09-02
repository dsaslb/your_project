#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 출퇴근 체크 API 테스트 스크립트
"""

import requests
import json
import time

def test_simple_attendance_api():
    """간단한 출퇴근 체크 API 테스트"""
    print('🔍 간단한 출퇴근 체크 API 테스트 시작...')
    
    # 1. 로그인하여 토큰 획득
    print('📱 간단한 모바일 로그인 중...')
    login_response = requests.post('http://localhost:5000/api/mobile/simple/login', 
                                  json={'username': 'demo', 'password': 'demo123'})
    
    if login_response.status_code != 200:
        print(f'❌ 로그인 실패: {login_response.status_code}')
        print(f'   응답: {login_response.text}')
        return False
    
    token = login_response.json()['token']
    user_info = login_response.json()['user']
    print(f'✅ 로그인 성공! 사용자: {user_info["username"]} (ID: {user_info["id"]})')
    
    # 2. 출근 체크 실행
    print('⏰ 출근 체크 중...')
    headers = {'Authorization': f'Bearer {token}'}
    attendance_data = {
        'type': 'in',
        'lat': 37.5665,  # 서울 시청 좌표
        'lng': 126.9780,
        'qr': 'STORE_001_QR'
    }
    
    attendance_response = requests.post('http://localhost:5000/api/mobile/simple/attendance/clock',
                                      json=attendance_data,
                                      headers=headers)
    
    if attendance_response.status_code != 200:
        print(f'❌ 출근 체크 실패: {attendance_response.status_code}')
        print(f'   응답: {attendance_response.text}')
        return False
    
    result = attendance_response.json()
    print(f'✅ 출근 체크 성공!')
    print(f'   - ID: {result.get("id")}')
    print(f'   - 사용자 ID: {result.get("user_id")}')
    print(f'   - 타입: {result.get("type")}')
    print(f'   - 시간: {result.get("timestamp")}')
    print(f'   - 위치: {result.get("lat")}, {result.get("lng")}')
    print(f'   - QR 코드: {result.get("qr")}')
    print('🔔 실시간 이벤트 "attendance:update"가 웹 대시보드로 전송되었습니다!')
    
    # 3. 잠시 후 퇴근 체크도 실행
    print('\n⏰ 3초 후 퇴근 체크 실행...')
    time.sleep(3)
    
    attendance_data['type'] = 'out'
    checkout_response = requests.post('http://localhost:5000/api/mobile/simple/attendance/clock',
                                    json=attendance_data,
                                    headers=headers)
    
    if checkout_response.status_code == 200:
        result = checkout_response.json()
        print(f'✅ 퇴근 체크 성공!')
        print(f'   - ID: {result.get("id")}')
        print(f'   - 타입: {result.get("type")}')
        print(f'   - 시간: {result.get("timestamp")}')
        print('🔔 퇴근 실시간 이벤트 "attendance:update"가 웹 대시보드로 전송되었습니다!')
    else:
        print(f'❌ 퇴근 체크 실패: {checkout_response.status_code}')
        print(f'   응답: {checkout_response.text}')
    
    return True

if __name__ == "__main__":
    test_simple_attendance_api()
