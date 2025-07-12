#!/usr/bin/env python3
"""
다중 채널 알림 시스템
이메일, SMS, Slack, Discord 등 다양한 채널을 통한 알림 전송
"""

import os
import json
import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class NotificationChannel:
    """알림 채널 설정"""
    name: str
    type: str  # email, sms, slack, discord, webhook
    enabled: bool
    config: Dict[str, Any]
    priority: int  # 1: 높음, 2: 중간, 3: 낮음
    created_at: datetime
    updated_at: datetime

@dataclass
class NotificationMessage:
    """알림 메시지"""
    title: str
    message: str
    level: str  # info, warning, critical
    channel: str
    recipient: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class NotificationManager:
    """알림 관리자"""
    
    def __init__(self, config_file: str = "config/notification_channels.json"):
        self.config_file = config_file
        self.channels: Dict[str, NotificationChannel] = {}
        self.logger = logging.getLogger(__name__)
        self.load_channels()
    
    def load_channels(self):
        """채널 설정 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for channel_data in data.get('channels', []):
                    channel = NotificationChannel(
                        name=channel_data['name'],
                        type=channel_data['type'],
                        enabled=channel_data.get('enabled', True),
                        config=channel_data.get('config', {}),
                        priority=channel_data.get('priority', 2),
                        created_at=datetime.fromisoformat(channel_data['created_at']),
                        updated_at=datetime.fromisoformat(channel_data['updated_at'])
                    )
                    self.channels[channel.name] = channel
                
                self.logger.info(f"Loaded {len(self.channels)} notification channels")
            else:
                self.create_default_channels()
                
        except Exception as e:
            self.logger.error(f"Failed to load notification channels: {e}")
            self.create_default_channels()
    
    def create_default_channels(self):
        """기본 채널 생성"""
        default_channels = [
            {
                'name': 'email_admin',
                'type': 'email',
                'enabled': True,
                'config': {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': os.getenv('EMAIL_USERNAME', ''),
                    'password': os.getenv('EMAIL_PASSWORD', ''),
                    'from_email': os.getenv('FROM_EMAIL', 'noreply@yourprogram.com'),
                    'to_email': os.getenv('ADMIN_EMAIL', 'admin@yourprogram.com')
                },
                'priority': 1
            },
            {
                'name': 'slack_alerts',
                'type': 'slack',
                'enabled': True,
                'config': {
                    'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
                    'channel': '#alerts',
                    'username': 'Plugin Monitor'
                },
                'priority': 2
            },
            {
                'name': 'discord_notifications',
                'type': 'discord',
                'enabled': False,
                'config': {
                    'webhook_url': os.getenv('DISCORD_WEBHOOK_URL', ''),
                    'username': 'Plugin Monitor'
                },
                'priority': 2
            },
            {
                'name': 'sms_critical',
                'type': 'sms',
                'enabled': False,
                'config': {
                    'provider': 'twilio',
                    'account_sid': os.getenv('TWILIO_ACCOUNT_SID', ''),
                    'auth_token': os.getenv('TWILIO_AUTH_TOKEN', ''),
                    'from_number': os.getenv('TWILIO_FROM_NUMBER', ''),
                    'to_number': os.getenv('ADMIN_PHONE', '')
                },
                'priority': 1
            }
        ]
        
        for channel_data in default_channels:
            now = datetime.now()
            channel = NotificationChannel(
                name=channel_data['name'],
                type=channel_data['type'],
                enabled=channel_data['enabled'],
                config=channel_data['config'],
                priority=channel_data['priority'],
                created_at=now,
                updated_at=now
            )
            self.channels[channel.name] = channel
        
        self.save_channels()
        self.logger.info("Created default notification channels")
    
    def save_channels(self):
        """채널 설정 저장"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            data = {
                'channels': [
                    {
                        **asdict(channel),
                        'created_at': channel.created_at.isoformat(),
                        'updated_at': channel.updated_at.isoformat()
                    }
                    for channel in self.channels.values()
                ]
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save notification channels: {e}")
    
    def add_channel(self, name: str, channel_type: str, config: Dict[str, Any], 
                   priority: int = 2, enabled: bool = True) -> bool:
        """새 채널 추가"""
        try:
            if name in self.channels:
                self.logger.warning(f"Channel {name} already exists")
                return False
            
            now = datetime.now()
            channel = NotificationChannel(
                name=name,
                type=channel_type,
                enabled=enabled,
                config=config,
                priority=priority,
                created_at=now,
                updated_at=now
            )
            
            self.channels[name] = channel
            self.save_channels()
            self.logger.info(f"Added notification channel: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add channel {name}: {e}")
            return False
    
    def update_channel(self, name: str, **kwargs) -> bool:
        """채널 업데이트"""
        try:
            if name not in self.channels:
                self.logger.warning(f"Channel {name} not found")
                return False
            
            channel = self.channels[name]
            
            for key, value in kwargs.items():
                if hasattr(channel, key):
                    setattr(channel, key, value)
            
            channel.updated_at = datetime.now()
            self.save_channels()
            self.logger.info(f"Updated notification channel: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update channel {name}: {e}")
            return False
    
    def remove_channel(self, name: str) -> bool:
        """채널 제거"""
        try:
            if name not in self.channels:
                self.logger.warning(f"Channel {name} not found")
                return False
            
            del self.channels[name]
            self.save_channels()
            self.logger.info(f"Removed notification channel: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove channel {name}: {e}")
            return False
    
    def send_notification(self, message: NotificationMessage) -> Dict[str, bool]:
        """알림 전송"""
        results = {}
        
        # 메시지 타임스탬프 설정
        if not message.timestamp:
            message.timestamp = datetime.now()
        
        # 우선순위에 따라 채널 필터링
        target_channels = []
        for channel in self.channels.values():
            if not channel.enabled:
                continue
            
            # 레벨에 따른 채널 선택
            if message.level == 'critical' and channel.priority <= 2:
                target_channels.append(channel)
            elif message.level == 'warning' and channel.priority <= 3:
                target_channels.append(channel)
            elif message.level == 'info':
                target_channels.append(channel)
        
        # 각 채널로 알림 전송
        for channel in target_channels:
            try:
                success = self._send_to_channel(channel, message)
                results[channel.name] = success
                
                if success:
                    self.logger.info(f"Notification sent via {channel.name}")
                else:
                    self.logger.warning(f"Failed to send notification via {channel.name}")
                    
            except Exception as e:
                self.logger.error(f"Error sending notification via {channel.name}: {e}")
                results[channel.name] = False
        
        return results
    
    def _send_to_channel(self, channel: NotificationChannel, message: NotificationMessage) -> bool:
        """특정 채널로 알림 전송"""
        try:
            if channel.type == 'email':
                return self._send_email(channel, message)
            elif channel.type == 'slack':
                return self._send_slack(channel, message)
            elif channel.type == 'discord':
                return self._send_discord(channel, message)
            elif channel.type == 'sms':
                return self._send_sms(channel, message)
            elif channel.type == 'webhook':
                return self._send_webhook(channel, message)
            else:
                self.logger.warning(f"Unknown channel type: {channel.type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in _send_to_channel: {e}")
            return False
    
    def _send_email(self, channel: NotificationChannel, message: NotificationMessage) -> bool:
        """이메일 전송"""
        try:
            config = channel.config
            
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = config.get('from_email', 'noreply@yourprogram.com')
            msg['To'] = message.recipient or config.get('to_email', 'admin@yourprogram.com')
            msg['Subject'] = f"[{message.level.upper()}] {message.title}"
            
            # HTML 본문 생성
            html_content = f"""
            <html>
            <body>
                <h2>{message.title}</h2>
                <p><strong>Level:</strong> {message.level.upper()}</p>
                <p><strong>Time:</strong> {message.timestamp.strftime('%Y-%m-%d %H:%M:%S') if message.timestamp else 'N/A'}</p>
                <p><strong>Message:</strong></p>
                <p>{message.message}</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # SMTP 서버 연결 및 전송
            server = smtplib.SMTP(config.get('smtp_server', 'smtp.gmail.com'), 
                                config.get('smtp_port', 587))
            server.starttls()
            server.login(config.get('username', ''), config.get('password', ''))
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_slack(self, channel: NotificationChannel, message: NotificationMessage) -> bool:
        """Slack 전송"""
        try:
            config = channel.config
            webhook_url = config.get('webhook_url')
            
            if not webhook_url:
                self.logger.warning("Slack webhook URL not configured")
                return False
            
            # Slack 메시지 포맷
            slack_message = {
                "channel": config.get('channel', '#alerts'),
                "username": config.get('username', 'Plugin Monitor'),
                "icon_emoji": ":warning:" if message.level in ['warning', 'critical'] else ":information_source:",
                "attachments": [
                    {
                        "color": "danger" if message.level == 'critical' else 
                                "warning" if message.level == 'warning' else "good",
                        "title": message.title,
                        "text": message.message,
                        "fields": [
                            {
                                "title": "Level",
                                "value": message.level.upper(),
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": message.timestamp.strftime('%Y-%m-%d %H:%M:%S') if message.timestamp else 'N/A',
                                "short": True
                            }
                        ],
                        "footer": "Plugin Monitoring System"
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=slack_message, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack message: {e}")
            return False
    
    def _send_discord(self, channel: NotificationChannel, message: NotificationMessage) -> bool:
        """Discord 전송"""
        try:
            config = channel.config
            webhook_url = config.get('webhook_url')
            
            if not webhook_url:
                self.logger.warning("Discord webhook URL not configured")
                return False
            
            # Discord 메시지 포맷
            discord_message = {
                "username": config.get('username', 'Plugin Monitor'),
                "embeds": [
                    {
                        "title": message.title,
                        "description": message.message,
                        "color": 0xFF0000 if message.level == 'critical' else 
                                0xFFA500 if message.level == 'warning' else 0x00FF00,
                        "fields": [
                            {
                                "name": "Level",
                                "value": message.level.upper(),
                                "inline": True
                            },
                            {
                                "name": "Time",
                                "value": message.timestamp.strftime('%Y-%m-%d %H:%M:%S') if message.timestamp else 'N/A',
                                "inline": True
                            }
                        ],
                        "footer": {
                            "text": "Plugin Monitoring System"
                        }
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=discord_message, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            self.logger.error(f"Failed to send Discord message: {e}")
            return False
    
    def _send_sms(self, channel: NotificationChannel, message: NotificationMessage) -> bool:
        """SMS 전송 (Twilio 사용)"""
        try:
            config = channel.config
            provider = config.get('provider', 'twilio')
            
            if provider == 'twilio':
                try:
                    from twilio.rest import Client
                    
                    client = Client(config.get('account_sid'), config.get('auth_token'))
                    
                    to_number = message.recipient or config.get('to_number')
                    if not to_number:
                        self.logger.error("No recipient phone number provided for SMS")
                        return False
                    
                    sms_message = client.messages.create(
                        body=f"[{message.level.upper()}] {message.title}: {message.message}",
                        from_=config.get('from_number'),
                        to=to_number
                    )
                    
                    return sms_message.sid is not None
                except ImportError:
                    self.logger.warning("Twilio library not installed. Install with: pip install twilio")
                    return False
            else:
                self.logger.warning(f"SMS provider {provider} not supported")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")
            return False
    
    def _send_webhook(self, channel: NotificationChannel, message: NotificationMessage) -> bool:
        """웹훅 전송"""
        try:
            config = channel.config
            webhook_url = config.get('webhook_url')
            
            if not webhook_url:
                self.logger.warning("Webhook URL not configured")
                return False
            
            webhook_data = {
                "title": message.title,
                "message": message.message,
                "level": message.level,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None,
                "channel": channel.name,
                "metadata": message.metadata or {}
            }
            
            headers = config.get('headers', {})
            response = requests.post(webhook_url, json=webhook_data, 
                                   headers=headers, timeout=10)
            
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")
            return False
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """채널 목록 반환"""
        return [
            {
                **asdict(channel),
                'created_at': channel.created_at.isoformat(),
                'updated_at': channel.updated_at.isoformat()
            }
            for channel in self.channels.values()
        ]
    
    def test_channel(self, channel_name: str) -> bool:
        """채널 테스트"""
        try:
            if channel_name not in self.channels:
                return False
            
            channel = self.channels[channel_name]
            
            test_message = NotificationMessage(
                title="Channel Test",
                message="This is a test notification to verify channel configuration.",
                level="info",
                channel=channel_name
            )
            
            return self._send_to_channel(channel, test_message)
            
        except Exception as e:
            self.logger.error(f"Channel test failed for {channel_name}: {e}")
            return False

# 전역 인스턴스
notification_manager = NotificationManager() 