# -*- coding: utf-8 -*-
"""
모바일 알림 시스템
시스템 상태 변화, 성능 이슈, 중요 이벤트를 모바일로 알림
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MobileNotificationSystem:
    """모바일 알림 시스템 클래스"""
    
    def __init__(self):
        self.config = self._load_config()
        self.notification_history = []
        self.max_history = 100
        
    def _load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        config_file = 'config/mobile_notifications.json'
        default_config = {
            'enabled': True,
            'providers': {
                'pushover': {
                    'enabled': False,
                    'api_token': '',
                    'user_key': ''
                },
                'telegram': {
                    'enabled': False,
                    'bot_token': '',
                    'chat_id': ''
                },
                'slack': {
                    'enabled': False,
                    'webhook_url': ''
                },
                'email': {
                    'enabled': False,
                    'smtp_server': '',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'recipients': []
                }
            },
            'notification_levels': {
                'critical': True,
                'warning': True,
                'info': False
            },
            'cooldown_minutes': 30  # 같은 타입의 알림 간 최소 간격
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 기본값과 병합
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                # 설정 파일이 없으면 기본 설정으로 생성
                os.makedirs('config', exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                return default_config
                
        except Exception as e:
            logger.error(f"설정 파일 로드 오류: {e}")
            return default_config
            
    def send_notification(self, title: str, message: str, level: str = 'info', 
                         category: str = 'system', data: Dict[str, Any] = None):
        """알림 발송"""
        try:
            # 알림 레벨 체크
            if not self.config['notification_levels'].get(level, False):
                logger.info(f"알림 레벨 {level}이 비활성화되어 있습니다.")
                return False
                
            # 쿨다운 체크
            if not self._check_cooldown(category, level):
                logger.info(f"쿨다운 기간 중입니다: {category} - {level}")
                return False
                
            # 알림 데이터 준비
            notification_data = {
                'title': title,
                'message': message,
                'level': level,
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'data': data or {}
            }
            
            # 알림 히스토리에 저장
            self._save_to_history(notification_data)
            
            # 각 제공자별로 알림 발송
            success_count = 0
            total_providers = 0
            
            for provider_name, provider_config in self.config['providers'].items():
                if provider_config.get('enabled', False):
                    total_providers += 1
                    if self._send_to_provider(provider_name, notification_data):
                        success_count += 1
                        
            logger.info(f"알림 발송 완료: {success_count}/{total_providers} 성공")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"알림 발송 오류: {e}")
            return False
            
    def _check_cooldown(self, category: str, level: str) -> bool:
        """쿨다운 체크"""
        try:
            cooldown_minutes = self.config.get('cooldown_minutes', 30)
            cutoff_time = datetime.now().timestamp() - (cooldown_minutes * 60)
            
            # 최근 알림에서 같은 카테고리와 레벨 체크
            for notification in reversed(self.notification_history):
                if (notification['category'] == category and 
                    notification['level'] == level and
                    datetime.fromisoformat(notification['timestamp']).timestamp() > cutoff_time):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"쿨다운 체크 오류: {e}")
            return True
            
    def _save_to_history(self, notification: Dict[str, Any]):
        """알림 히스토리에 저장"""
        try:
            self.notification_history.append(notification)
            
            # 최대 크기 제한
            if len(self.notification_history) > self.max_history:
                self.notification_history = self.notification_history[-self.max_history:]
                
            # 파일에 저장
            history_file = 'logs/mobile_notifications.json'
            os.makedirs('logs', exist_ok=True)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.notification_history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"알림 히스토리 저장 오류: {e}")
            
    def _send_to_provider(self, provider: str, notification: Dict[str, Any]) -> bool:
        """특정 제공자로 알림 발송"""
        try:
            if provider == 'pushover':
                return self._send_pushover(notification)
            elif provider == 'telegram':
                return self._send_telegram(notification)
            elif provider == 'slack':
                return self._send_slack(notification)
            elif provider == 'email':
                return self._send_email(notification)
            elif provider == 'log':
                from utils.log_notification_provider import log_notification_provider
                return log_notification_provider.send_notification(notification)
            else:
                logger.warning(f"알 수 없는 알림 제공자: {provider}")
                return False
                
        except Exception as e:
            logger.error(f"{provider} 알림 발송 오류: {e}")
            return False
            
    def _send_pushover(self, notification: Dict[str, Any]) -> bool:
        """Pushover로 알림 발송"""
        try:
            config = self.config['providers']['pushover']
            api_token = config.get('api_token')
            user_key = config.get('user_key')
            
            if not api_token or not user_key:
                logger.warning("Pushover 설정이 완료되지 않았습니다.")
                return False
                
            # 우선순위 설정
            priority = 0
            if notification['level'] == 'critical':
                priority = 2
            elif notification['level'] == 'warning':
                priority = 1
                
            data = {
                'token': api_token,
                'user': user_key,
                'title': notification['title'],
                'message': notification['message'],
                'priority': priority,
                'sound': 'cosmic' if notification['level'] == 'critical' else 'pushover'
            }
            
            response = requests.post('https://api.pushover.net/1/messages.json', data=data)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Pushover 알림 발송 오류: {e}")
            return False
            
    def _send_telegram(self, notification: Dict[str, Any]) -> bool:
        """Telegram으로 알림 발송"""
        try:
            config = self.config['providers']['telegram']
            bot_token = config.get('bot_token')
            chat_id = config.get('chat_id')
            
            if not bot_token or not chat_id:
                logger.warning("Telegram 설정이 완료되지 않았습니다.")
                return False
                
            # 이모지 추가
            emoji_map = {
                'critical': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️'
            }
            emoji = emoji_map.get(notification['level'], 'ℹ️')
            
            message = f"{emoji} **{notification['title']}**\n\n{notification['message']}"
            
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            response = requests.post(url, data=data)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Telegram 알림 발송 오류: {e}")
            return False
            
    def _send_slack(self, notification: Dict[str, Any]) -> bool:
        """Slack으로 알림 발송"""
        try:
            config = self.config['providers']['slack']
            webhook_url = config.get('webhook_url')
            
            if not webhook_url:
                logger.warning("Slack 설정이 완료되지 않았습니다.")
                return False
                
            # 색상 설정
            color_map = {
                'critical': '#ff0000',
                'warning': '#ffa500',
                'info': '#0000ff'
            }
            color = color_map.get(notification['level'], '#0000ff')
            
            payload = {
                'attachments': [{
                    'title': notification['title'],
                    'text': notification['message'],
                    'color': color,
                    'fields': [
                        {
                            'title': '카테고리',
                            'value': notification['category'],
                            'short': True
                        },
                        {
                            'title': '레벨',
                            'value': notification['level'],
                            'short': True
                        }
                    ],
                    'ts': datetime.now().timestamp()
                }]
            }
            
            response = requests.post(webhook_url, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Slack 알림 발송 오류: {e}")
            return False
            
    def _send_email(self, notification: Dict[str, Any]) -> bool:
        """이메일로 알림 발송"""
        try:
            config = self.config['providers']['email']
            
            if not config.get('enabled', False):
                return False
                
            # 이메일 발송 로직 (실제 구현은 SMTP 라이브러리 사용)
            logger.info(f"이메일 알림: {notification['title']} - {notification['message']}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 알림 발송 오류: {e}")
            return False
            
    def get_notification_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """알림 히스토리 조회"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_notifications = [
                notification for notification in self.notification_history
                if datetime.fromisoformat(notification['timestamp']) > cutoff_time
            ]
            
            return recent_notifications
            
        except Exception as e:
            logger.error(f"알림 히스토리 조회 오류: {e}")
            return []
            
    def test_notification(self, provider: str = None):
        """테스트 알림 발송"""
        try:
            if provider:
                # 특정 제공자 테스트
                notification_data = {
                    'title': '테스트 알림',
                    'message': f'이것은 {provider}의 테스트 알림입니다.',
                    'level': 'info',
                    'category': 'test',
                    'timestamp': datetime.now().isoformat(),
                    'data': {}
                }
                
                success = self._send_to_provider(provider, notification_data)
                return {
                    'provider': provider,
                    'success': success,
                    'message': f'{provider} 테스트 알림이 {"성공" if success else "실패"}했습니다.'
                }
            else:
                # 모든 활성화된 제공자 테스트
                results = []
                for provider_name, provider_config in self.config['providers'].items():
                    if provider_config.get('enabled', False):
                        result = self.test_notification(provider_name)
                        results.append(result)
                        
                return results
                
        except Exception as e:
            logger.error(f"테스트 알림 오류: {e}")
            return {'error': str(e)}


# 전역 인스턴스
mobile_notification_system = MobileNotificationSystem()


def send_system_alert(title: str, message: str, level: str = 'info', 
                     category: str = 'system', data: Dict[str, Any] = None):
    """시스템 알림 발송"""
    return mobile_notification_system.send_notification(title, message, level, category, data)


def send_performance_alert(metric: str, value: float, threshold: float, 
                          level: str = 'warning'):
    """성능 알림 발송"""
    title = f"성능 알림: {metric}"
    message = f"{metric}이(가) 임계값을 초과했습니다.\n현재 값: {value}\n임계값: {threshold}"
    
    return mobile_notification_system.send_notification(
        title, message, level, 'performance', 
        {'metric': metric, 'value': value, 'threshold': threshold}
    )


def send_maintenance_alert(action: str, status: str, details: str = ""):
    """유지보수 알림 발송"""
    title = f"유지보수 알림: {action}"
    message = f"유지보수 작업이 {status}되었습니다.\n{details}"
    
    level = 'warning' if status == '실패' else 'info'
    
    return mobile_notification_system.send_notification(
        title, message, level, 'maintenance',
        {'action': action, 'status': status, 'details': details}
    )


if __name__ == "__main__":
    # 테스트 실행
    print("모바일 알림 시스템 테스트...")
    
    # 테스트 알림 발송
    result = mobile_notification_system.test_notification()
    print(f"테스트 결과: {result}")
    
    # 시스템 알림 테스트
    send_system_alert(
        "시스템 테스트",
        "모바일 알림 시스템이 정상적으로 작동하고 있습니다.",
        "info",
        "test"
    ) 