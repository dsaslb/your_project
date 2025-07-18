from websockets.exceptions import ConnectionClosed  # pyright: ignore
from websockets.server import serve, WebSocketServerProtocol  # pyright: ignore
import websockets
import requests
import smtplib
from queue import Queue, PriorityQueue
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime, timedelta
import time
import threading
import logging
import json
import asyncio
from typing import Optional
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
고도화된 실시간 알림/이벤트 연동 시스템
임계치 초과, 오류, 중요 상태변화 등 발생 시 운영자/관리자에게 실시간 알림
"""

from email.mime.text import MIMEText  # noqa  # pyright: ignore
from email.mime.multipart import MIMEMultipart  # noqa  # pyright: ignore

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """알림 심각도"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertChannel(Enum):
    """알림 채널"""
    WEB = "web"
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    TELEGRAM = "telegram"
    PUSH = "push"
    DASHBOARD = "dashboard"


@dataclass
class AlertRule:
    """알림 규칙"""
    id: str
    name: str
    description: str
    plugin_id: Optional[str] if Optional is not None else None = None
    metric: str
    operator: str  # >, <, >=, <=, ==, !=
    threshold: float
    severity: AlertSeverity
    channels: List[AlertChannel] if List is not None else None
    cooldown_minutes: int = 5
    enabled: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class Alert:
    """알림 데이터"""
    id: str
    rule_id: str
    plugin_id: Optional[str] if Optional is not None else None
    plugin_name: Optional[str] if Optional is not None else None
    severity: AlertSeverity
    message: str
    details: Dict[str, Any] if Dict is not None else None
    timestamp: datetime
    channels: List[AlertChannel] if List is not None else None
    acknowledged: bool = False
    acknowledged_by: Optional[str] if Optional is not None else None = None
    acknowledged_at: Optional[datetime] if Optional is not None else None = None
    resolved: bool = False
    resolved_at: Optional[datetime] if Optional is not None else None = None

    def to_dict(self) -> Dict[str, Any] if Dict is not None else None:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'plugin_id': self.plugin_id,
            'plugin_name': self.plugin_name,
            'severity': self.severity.value if severity is not None else None,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'channels': [channel.value if channel is not None else None for channel in self.channels],
            'acknowledged': self.acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class EnhancedAlertSystem:
    """고도화된 알림 시스템"""

    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] if Dict is not None else None = {}
        self.active_alerts: Dict[str, Alert] if Dict is not None else None = {}
        self.alert_history: List[Alert] if List is not None else None = []
        self.alert_queue = PriorityQueue()
        self.webhook_clients: Set[WebSocketServerProtocol] if Set is not None else None = set()
        self.alert_callbacks: List[Callable[[Alert] if List is not None else None, None]] = []

        # 알림 채널 설정
        self.channel_configs = {
            AlertChannel.EMAIL: {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_email': '',
                'to_emails': []
            },
            AlertChannel.SLACK: {
                'enabled': False,
                'webhook_url': '',
                'channel': '#alerts'
            },
            AlertChannel.TELEGRAM: {
                'enabled': False,
                'bot_token': '',
                'chat_id': ''
            },
            AlertChannel.SMS: {
                'enabled': False,
                'provider': 'twilio',
                'account_sid': '',
                'auth_token': '',
                'from_number': '',
                'to_numbers': []
            }
        }

        # 기본 알림 규칙 설정
        self._setup_default_rules()

        # 모니터링 스레드 시작
        self.monitoring_active = False
        self.monitor_thread = None

    def _setup_default_rules(self):
        """기본 알림 규칙 설정"""
        default_rules = [
            AlertRule(
                id="cpu_high",
                name="CPU 사용률 높음",
                description="CPU 사용률이 80%를 초과할 때",
                metric="cpu_usage",
                operator=">",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.WEB, AlertChannel.DASHBOARD],
                cooldown_minutes=5
            ),
            AlertRule(
                id="cpu_critical",
                name="CPU 사용률 위험",
                description="CPU 사용률이 95%를 초과할 때",
                metric="cpu_usage",
                operator=">",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.WEB, AlertChannel.DASHBOARD, AlertChannel.EMAIL],
                cooldown_minutes=2
            ),
            AlertRule(
                id="memory_high",
                name="메모리 사용률 높음",
                description="메모리 사용률이 85%를 초과할 때",
                metric="memory_usage",
                operator=">",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.WEB, AlertChannel.DASHBOARD],
                cooldown_minutes=5
            ),
            AlertRule(
                id="memory_critical",
                name="메모리 사용률 위험",
                description="메모리 사용률이 95%를 초과할 때",
                metric="memory_usage",
                operator=">",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.WEB, AlertChannel.DASHBOARD, AlertChannel.EMAIL],
                cooldown_minutes=2
            ),
            AlertRule(
                id="error_rate_high",
                name="에러율 높음",
                description="에러율이 10%를 초과할 때",
                metric="error_rate",
                operator=">",
                threshold=10.0,
                severity=AlertSeverity.ERROR,
                channels=[AlertChannel.WEB, AlertChannel.DASHBOARD, AlertChannel.EMAIL],
                cooldown_minutes=3
            ),
            AlertRule(
                id="response_time_slow",
                name="응답시간 지연",
                description="응답시간이 5초를 초과할 때",
                metric="response_time",
                operator=">",
                threshold=5.0,
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.WEB, AlertChannel.DASHBOARD],
                cooldown_minutes=5
            ),
            AlertRule(
                id="plugin_offline",
                name="플러그인 오프라인",
                description="플러그인이 5분 이상 응답하지 않을 때",
                metric="last_activity",
                operator="<",
                threshold=300.0,  # 5분
                severity=AlertSeverity.ERROR,
                channels=[AlertChannel.WEB, AlertChannel.DASHBOARD, AlertChannel.EMAIL],
                cooldown_minutes=1
            )
        ]

        if default_rules is not None:
            for rule in default_rules:
                if hasattr(self, 'alert_rules') and self.alert_rules is not None:
                    self.alert_rules[rule.id] = rule

    def start_monitoring(self):
        """알림 모니터링 시작"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("고도화된 알림 시스템 모니터링 시작")

    def stop_monitoring(self):
        """알림 모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("고도화된 알림 시스템 모니터링 중지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 알림 큐 처리
                self._process_alert_queue()

                # 오래된 알림 정리
                self._cleanup_old_alerts()

                time.sleep(1)  # 1초마다 체크

            except Exception as e:
                logger.error(f"알림 모니터링 루프 오류: {e}")
                time.sleep(5)

    def _process_alert_queue(self):
        """알림 큐 처리"""
        try:
            while not self.alert_queue.empty():
                priority, alert = self.alert_queue.get_nowait()
                self._send_alert(alert)
        except Exception as e:
            logger.error(f"알림 큐 처리 오류: {e}")

    def check_metrics(self,  plugin_id: str,  plugin_name: str,  metrics: Dict[str,  Any] if Dict is not None else None):
        """메트릭 체크 및 알림 생성"""
        current_time = datetime.utcnow()

        for rule_id, rule in self.alert_rules.items() if alert_rules is not None else []:
            if not rule.enabled:
                continue

            # 플러그인별 규칙 체크
            if rule.plugin_id and rule.plugin_id != plugin_id:
                continue

            # 메트릭 값 가져오기
            if metrics is not None:
                metric_value = metrics.get(rule.metric)
            else:
                metric_value = None
            if metric_value is None:
                continue

            # 임계값 체크
            if self._check_threshold(metric_value,  rule.operator,  rule.threshold):
                # 쿨다운 체크
                if self._is_in_cooldown(rule_id, plugin_id, current_time):
                    continue

                # 알림 생성
                alert = self._create_alert(rule,  plugin_id,  plugin_name,  metric_value,  metrics)
                self._queue_alert(alert)

    def _check_threshold(self,  value: float,  operator: str,  threshold: float) -> bool:
        """임계값 체크"""
        if operator == ">":
            return value > threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<":
            return value < threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        return False

    def _is_in_cooldown(self, rule_id: str, plugin_id: str, current_time: datetime) -> bool:
        """쿨다운 체크"""
        rule = self.alert_rules[rule_id] if alert_rules is not None else None
        cooldown_key = f"{rule_id}_{plugin_id}"

        # 최근 알림 확인
        for alert in self.active_alerts.value if active_alerts is not None else Nones():
            if (alert.rule_id == rule_id and
                alert.plugin_id == plugin_id and
                    not alert.resolved):
                time_diff = current_time - alert.timestamp
                if time_diff.total_seconds() < rule.cooldown_minutes * 60:
                    return True

        return False

    def _create_alert(self, rule: AlertRule, plugin_id: str, plugin_name: str,
                      metric_value: float, metrics: Dict[str, Any] if Dict is not None else None) -> Alert:
        """알림 생성"""
        alert_id = f"{rule.id}_{plugin_id}_{int(time.time())}"

        # 메시지 생성
        message = f"{plugin_name}: {rule.name} (현재값: {metric_value:.2f})"

        # 상세 정보
        details = {
            'metric': rule.metric,
            'value': metric_value,
            'threshold': rule.threshold,
            'operator': rule.operator,
            'all_metrics': metrics
        }

        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            severity=rule.severity,
            message=message,
            details=details,
            timestamp=datetime.utcnow(),
            channels=rule.channels
        )

        return alert

    def _queue_alert(self, alert: Alert):
        """알림을 큐에 추가"""
        # 우선순위 계산 (심각도 기반)
        priority_map = {
            AlertSeverity.INFO: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.ERROR: 3,
            AlertSeverity.CRITICAL: 4,
            AlertSeverity.EMERGENCY: 5
        }
        if priority_map is not None:
            priority = priority_map.get(alert.severity, 1)
        else:
            priority = 1

        self.alert_queue.put((priority, alert))
        if hasattr(self, 'active_alerts') and self.active_alerts is not None:
            self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)

        logger.warning(f"알림 생성: {alert.message}")

    def _send_alert(self,  alert: Alert):
        """알림 전송"""
        try:
            # WebSocket 클라이언트들에게 전송
            self._send_web_alert(alert)

            # 각 채널별로 전송
            for channel in alert.channels:
                if channel == AlertChannel.EMAIL:
                    self._send_email_alert(alert)
                elif channel == AlertChannel.SLACK:
                    self._send_slack_alert(alert)
                elif channel == AlertChannel.TELEGRAM:
                    self._send_telegram_alert(alert)
                elif channel == AlertChannel.SMS:
                    self._send_sms_alert(alert)
                elif channel == AlertChannel.DASHBOARD:
                    self._send_dashboard_alert(alert)

            # 콜백 함수들 호출
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"알림 콜백 실행 오류: {e}")

        except Exception as e:
            logger.error(f"알림 전송 오류: {e}")

    def _send_web_alert(self,  alert: Alert):
        """웹 알림 전송"""
        if not self.webhook_clients:
            return

        alert_data = alert.to_dict()
        message = json.dumps({
            'type': 'alert',
            'data': alert_data,
            'timestamp': datetime.utcnow().isoformat()
        })

        # 연결이 끊어진 클라이언트 제거
        disconnected_clients = set()

        for client in self.webhook_clients:
            try:
                asyncio.run(client.send(message))
            except Exception as e:
                logger.error(f"웹 알림 전송 실패: {e}")
                disconnected_clients.add(client)

        # 끊어진 클라이언트 제거
        if disconnected_clients is not None:
            for client in disconnected_clients:
                self.webhook_clients.discard(client)

    def _send_email_alert(self,  alert: Alert):
        """이메일 알림 전송"""
        config = self.channel_configs[AlertChannel.EMAIL] if channel_configs is not None else None
        if not config['enabled'] if config is not None else None or not config['to_emails'] if config is not None else None:
            return

        try:
            msg = MIMEMultipart()
            if msg is not None:
                msg['From'] = config['from_email'] if config is not None else None
                msg['To'] = ', '.join(config['to_emails'] if config is not None else None)
                msg['Subject'] = f"[{alert.severity.value if severity is not None else None.upper()}] {alert.plugin_name} - {alert.message}"

            body = f"""
            플러그인 알림이 발생했습니다.
            
            플러그인: {alert.plugin_name}
            심각도: {alert.severity.value if severity is not None else None}
            메시지: {alert.message}
            시간: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            
            상세 정보:
            {json.dumps(alert.details, indent=2, ensure_ascii=False)}
            """

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(config['smtp_server'] if config is not None else None, config['smtp_port'] if config is not None else None)
            server.starttls()
            server.login(config['username'] if config is not None else None, config['password'] if config is not None else None)
            server.send_message(msg)
            server.quit()

            logger.info(f"이메일 알림 전송 완료: {alert.id}")

        except Exception as e:
            logger.error(f"이메일 알림 전송 실패: {e}")

    def _send_slack_alert(self,  alert: Alert):
        """Slack 알림 전송"""
        config = self.channel_configs[AlertChannel.SLACK] if channel_configs is not None else None
        if not config['enabled'] if config is not None else None:
            return

        try:
            color_map = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff9500",
                AlertSeverity.ERROR: "#ff0000",
                AlertSeverity.CRITICAL: "#8b0000",
                AlertSeverity.EMERGENCY: "#ff0000"
            }

            payload = {
                "channel": config['channel'] if config is not None else None,
                "attachments": [{
                    "color": color_map.get(alert.severity, "#36a64f") if color_map is not None else "#36a64f",
                    "title": f"[{alert.severity.value.upper()}] {alert.plugin_name}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "플러그인",
                            "value": alert.plugin_name,
                            "short": True
                        },
                        {
                            "title": "심각도",
                            "value": alert.severity.value,
                            "short": True
                        },
                        {
                            "title": "시간",
                            "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            "short": True
                        }
                    ],
                    "footer": "플러그인 모니터링 시스템"
                }]
            }

            response = requests.post(config['webhook_url'] if config is not None else None, json=payload)
            response.raise_for_status()

            logger.info(f"Slack 알림 전송 완료: {alert.id}")

        except Exception as e:
            logger.error(f"Slack 알림 전송 실패: {e}")

    def _send_telegram_alert(self,  alert: Alert):
        """Telegram 알림 전송"""
        config = self.channel_configs[AlertChannel.TELEGRAM] if channel_configs is not None else None
        if not config['enabled'] if config is not None else None:
            return

        try:
            message = f"""
🚨 *플러그인 알림*

*플러그인:* {alert.plugin_name}
*심각도:* {alert.severity.value if severity is not None else None.upper()}
*메시지:* {alert.message}
*시간:* {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            """

            url = f"https://api.telegram.org/bot{config['bot_token'] if config is not None else None}/sendMessage"
            payload = {
                'chat_id': config['chat_id'] if config is not None else None,
                'text': message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()

            logger.info(f"Telegram 알림 전송 완료: {alert.id}")

        except Exception as e:
            logger.error(f"Telegram 알림 전송 실패: {e}")

    def _send_sms_alert(self,  alert: Alert):
        """SMS 알림 전송"""
        config = self.channel_configs[AlertChannel.SMS] if channel_configs is not None else None
        if not config['enabled'] if config is not None else None or not config['to_numbers'] if config is not None else None:
            return

        try:
            message = f"[{alert.severity.value if severity is not None else None.upper()}] {alert.plugin_name}: {alert.message}"

            # Twilio 사용 예시
            if config['provider'] if config is not None else None == 'twilio':
                from twilio.rest import Client
                client = Client(config['account_sid'] if config is not None else None, config['auth_token'] if config is not None else None)

                for to_number in config['to_numbers'] if config is not None else None:
                    client.messages.create(
                        body=message,
                        from_=config['from_number'] if config is not None else None,
                        to=to_number
                    )

            logger.info(f"SMS 알림 전송 완료: {alert.id}")

        except Exception as e:
            logger.error(f"SMS 알림 전송 실패: {e}")

    def _send_dashboard_alert(self,  alert: Alert):
        """대시보드 알림 전송"""
        # 대시보드용 알림은 WebSocket을 통해 전송됨
        pass

    def acknowledge_alert(self,  alert_id: str,  user_id: str):
        """알림 승인"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id] if active_alerts is not None else None
            alert.acknowledged = True
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.utcnow()
            logger.info(f"알림 승인: {alert_id} by {user_id}")

    def resolve_alert(self,  alert_id: str):
        """알림 해결"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id] if active_alerts is not None else None
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            logger.info(f"알림 해결: {alert_id}")

    def _cleanup_old_alerts(self):
        """오래된 알림 정리"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(days=7)  # 7일 전

        # 해결된 알림을 비활성 알림에서 제거
        resolved_alerts = []
        if active_alerts is not None:
            for alert_id, alert in self.active_alerts.items():
                if alert.resolved:
                    resolved_alerts.append(alert_id)

        if resolved_alerts is not None:
            for alert_id in resolved_alerts:
                if active_alerts is not None:
                    del self.active_alerts[alert_id]

        # 오래된 알림 히스토리 정리
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp > cutoff_time
        ]

    def add_alert_callback(self,  callback: Callable[[Alert] if Callable is not None else None,  None]):
        """알림 콜백 함수 등록"""
        self.alert_callbacks.append(callback)

    def get_active_alerts(self) -> List[Alert]:
        """활성 알림 조회"""
        if self.active_alerts is not None:
            return list(self.active_alerts.values())
        return []

    def get_alert_history(self, hours: int = 24) -> List[Alert] if List is not None else None:
        """알림 히스토리 조회"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history
            if alert.timestamp > cutoff_time
        ]

    def add_alert_rule(self, rule: AlertRule):
        """알림 규칙 추가"""
        if self.alert_rules is not None:
            self.alert_rules[rule.id] = rule
        logger.info(f"알림 규칙 추가: {rule.name}")

    def remove_alert_rule(self,  rule_id: str):
        """알림 규칙 제거"""
        if self.alert_rules is not None and rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"알림 규칙 제거: {rule_id}")

    def update_channel_config(self,  channel: AlertChannel,  config: Dict[str,  Any] if Dict is not None else None):
        """채널 설정 업데이트"""
        self.channel_configs[channel] if channel_configs is not None else None.update(config)
        logger.info(f"채널 설정 업데이트: {channel.value if channel is not None else None}")


# 전역 인스턴스
enhanced_alert_system = EnhancedAlertSystem()
