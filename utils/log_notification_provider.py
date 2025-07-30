# -*- coding: utf-8 -*-
"""
로그 기반 알림 제공자
모바일 알림 시스템의 테스트용 제공자
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)


class LogNotificationProvider:
    """로그 기반 알림 제공자"""
    
    def __init__(self):
        self.log_file = 'logs/notifications.log'
        os.makedirs('logs', exist_ok=True)
        
    def send_notification(self, notification: Dict[str, Any]) -> bool:
        """알림을 로그 파일에 기록"""
        try:
            # 알림 데이터 준비
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'provider': 'log',
                'notification': notification
            }
            
            # 로그 파일에 기록
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
            # 콘솔에도 출력
            level_emoji = {
                'critical': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️'
            }
            emoji = level_emoji.get(notification['level'], 'ℹ️')
            
            print(f"{emoji} [알림] {notification['title']}: {notification['message']}")
            
            return True
            
        except Exception as e:
            logger.error(f"로그 알림 발송 오류: {e}")
            return False
            
    def get_notification_history(self, hours: int = 24) -> list:
        """알림 히스토리 조회"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            notifications = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if datetime.fromisoformat(entry['timestamp']) > cutoff_time:
                                notifications.append(entry)
                        except:
                            continue
                            
            return notifications
            
        except Exception as e:
            logger.error(f"알림 히스토리 조회 오류: {e}")
            return []


# 전역 인스턴스
log_notification_provider = LogNotificationProvider() 