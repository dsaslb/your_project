#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expo Push Notification 서비스

실제 Expo 푸시 알림을 전송하는 서비스
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class ExpoPushService:
    """Expo Push Notification 서비스 클래스"""
    
    EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
    
    def is_valid_expo_token(self, token: str) -> bool:
        """Expo 푸시 토큰이 유효한지 확인"""
        if not token:
            return False
        return token.startswith('ExponentPushToken[') or token.startswith('ExpoPushToken[')
    
    def send_notification(self, 
                         push_token: str, 
                         title: str, 
                         body: str, 
                         data: Optional[Dict] = None,
                         sound: str = 'default') -> Dict:
        """
        단일 푸시 알림 전송
        
        Args:
            push_token: Expo 푸시 토큰
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터
            sound: 알림 소리
            
        Returns:
            전송 결과 딕셔너리
        """
        if not self.is_valid_expo_token(push_token):
            return {
                'success': False,
                'error': 'Invalid Expo push token',
                'token': push_token
            }
        
        message = {
            'to': push_token,
            'title': title,
            'body': body,
            'sound': sound,
            'data': data or {}
        }
        
        try:
            response = self.session.post(
                self.EXPO_PUSH_URL,
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('data', {}).get('status') == 'ok':
                    return {
                        'success': True,
                        'ticket': result.get('data', {}).get('id'),
                        'token': push_token
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('data', {}).get('message', 'Unknown error'),
                        'token': push_token
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'token': push_token
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'token': push_token
            }
    
    def send_batch_notifications(self, messages: List[Dict]) -> List[Dict]:
        """
        배치로 푸시 알림 전송
        
        Args:
            messages: 푸시 메시지 리스트
            
        Returns:
            전송 결과 리스트
        """
        if not messages:
            return []
        
        # 유효한 토큰만 필터링
        valid_messages = []
        results = []
        
        for message in messages:
            token = message.get('to')
            if self.is_valid_expo_token(token):
                valid_messages.append(message)
            else:
                results.append({
                    'success': False,
                    'error': 'Invalid Expo push token',
                    'token': token
                })
        
        if not valid_messages:
            return results
        
        try:
            response = self.session.post(
                self.EXPO_PUSH_URL,
                json=valid_messages,
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                batch_results = response_data.get('data', [])
                
                for i, result in enumerate(batch_results):
                    token = valid_messages[i].get('to') if i < len(valid_messages) else 'unknown'
                    
                    if result.get('status') == 'ok':
                        results.append({
                            'success': True,
                            'ticket': result.get('id'),
                            'token': token
                        })
                    else:
                        results.append({
                            'success': False,
                            'error': result.get('message', 'Unknown error'),
                            'token': token
                        })
            else:
                # 전체 배치 실패
                for message in valid_messages:
                    results.append({
                        'success': False,
                        'error': f'Batch request failed: HTTP {response.status_code}',
                        'token': message.get('to')
                    })
                
        except requests.exceptions.RequestException as e:
            # 전체 배치 실패
            for message in valid_messages:
                results.append({
                    'success': False,
                    'error': f'Batch request failed: {str(e)}',
                    'token': message.get('to')
                })
        
        return results

# 전역 푸시 서비스 인스턴스
push_service = ExpoPushService()

def send_attendance_notification(user_tokens: List[str], user_name: str, action: str):
    """출퇴근 알림 전송"""
    title = "출퇴근 알림"
    body = f"{user_name}님이 {action}했습니다."
    
    messages = []
    for token in user_tokens:
        if push_service.is_valid_expo_token(token):
            messages.append({
                'to': token,
                'title': title,
                'body': body,
                'sound': 'default',
                'data': {
                    'type': 'attendance',
                    'action': action,
                    'user_name': user_name,
                    'timestamp': datetime.now().isoformat()
                }
            })
    
    if messages:
        results = push_service.send_batch_notifications(messages)
        success_count = sum(1 for r in results if r['success'])
        print(f"✅ 출퇴근 알림 전송 완료: {success_count}/{len(messages)}개 성공")
        return results
    
    return []

def send_inventory_notification(user_tokens: List[str], barcode: str, qty: int):
    """재고 조사 알림 전송"""
    title = "재고 업데이트"
    body = f"상품 {barcode}의 재고가 {qty}개로 업데이트되었습니다."
    
    messages = []
    for token in user_tokens:
        if push_service.is_valid_expo_token(token):
            messages.append({
                'to': token,
                'title': title,
                'body': body,
                'sound': 'default',
                'data': {
                    'type': 'inventory',
                    'barcode': barcode,
                    'qty': qty,
                    'timestamp': datetime.now().isoformat()
                }
            })
    
    if messages:
        results = push_service.send_batch_notifications(messages)
        success_count = sum(1 for r in results if r['success'])
        print(f"✅ 재고 알림 전송 완료: {success_count}/{len(messages)}개 성공")
        return results
    
    return []

def send_purchase_order_notification(user_tokens: List[str], order_id: int, items_count: int):
    """발주 알림 전송"""
    title = "새로운 발주 요청"
    body = f"발주 #{order_id}가 생성되었습니다. ({items_count}개 품목)"
    
    messages = []
    for token in user_tokens:
        if push_service.is_valid_expo_token(token):
            messages.append({
                'to': token,
                'title': title,
                'body': body,
                'sound': 'default',
                'data': {
                    'type': 'purchase_order',
                    'order_id': order_id,
                    'items_count': items_count,
                    'timestamp': datetime.now().isoformat()
                }
            })
    
    if messages:
        results = push_service.send_batch_notifications(messages)
        success_count = sum(1 for r in results if r['success'])
        print(f"✅ 발주 알림 전송 완료: {success_count}/{len(messages)}개 성공")
        return results
    
    return []

# 테스트용 함수
def test_push_notification(test_token: str):
    """푸시 알림 테스트"""
    title = "테스트 알림"
    body = "모바일 앱 푸시 알림이 정상적으로 작동합니다!"
    
    result = push_service.send_notification(
        push_token=test_token,
        title=title,
        body=body,
        data={
            'type': 'test',
            'timestamp': datetime.now().isoformat()
        }
    )
    
    print(f"푸시 알림 테스트 결과: {result}")
    return result
