import uuid
import json
from enum import Enum
from typing import Dict, List, Any, Optional
import logging
import time
import threading
import asyncio
from datetime import datetime, timedelta
from models_main import *
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
from typing import Optional
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
실시간 경보 시스템
- 이상징후 자동 탐지
- 관리자 실시간 알림
- 경보 우선순위 관리
- 알림 이력 추적
- 알림 그룹핑 및 필터링
- 알림 템플릿 시스템
"""


realtime_alert_system = Blueprint('realtime_alert_system', __name__, url_prefix='/api/alerts')

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """경보 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """경보 유형"""
    SALES_DROP = "sales_drop"
    COST_INCREASE = "cost_increase"
    INVENTORY_SHORTAGE = "inventory_shortage"
    STAFF_SHORTAGE = "staff_shortage"
    SYSTEM_ERROR = "system_error"
    SECURITY_BREACH = "security_breach"
    PERFORMANCE_ISSUE = "performance_issue"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    QUALITY_ISSUE = "quality_issue"
    FINANCIAL_ANOMALY = "financial_anomaly"


class AlertStatus(Enum):
    """경보 상태"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class AlertTemplate:
    """알림 템플릿"""

    def __init__(self):
        self.templates = {
            AlertType.SALES_DROP: {
                'title': '매출 급감 알림',
                'message_template': '매출이 {drop_rate:.1f}% 감소했습니다. (어제: {yesterday:,}원, 오늘: {today:,}원)',
                'icon': '📉',
                'color': '#ff4444',
                'action_required': True
            },
            AlertType.COST_INCREASE: {
                'title': '인건비 급증 알림',
                'message_template': '인건비가 {increase_rate:.1f}% 증가했습니다. (어제: {yesterday:,}원, 오늘: {today:,}원)',
                'icon': '💰',
                'color': '#ff8800',
                'action_required': True
            },
            AlertType.INVENTORY_SHORTAGE: {
                'title': '재고 부족 알림',
                'message_template': '{item_count}개 품목의 재고가 부족합니다.',
                'icon': '📦',
                'color': '#ff6600',
                'action_required': True
            },
            AlertType.STAFF_SHORTAGE: {
                'title': '인력 부족 알림',
                'message_template': '현재 {current_staff}명으로 {required_staff}명이 필요합니다.',
                'icon': '👥',
                'color': '#ffaa00',
                'action_required': True
            },
            AlertType.SYSTEM_ERROR: {
                'title': '시스템 오류 알림',
                'message_template': '{error_count}개의 시스템 오류가 발생했습니다.',
                'icon': '⚠️',
                'color': '#cc0000',
                'action_required': True
            },
            AlertType.CUSTOMER_SATISFACTION: {
                'title': '고객 만족도 하락 알림',
                'message_template': '고객 만족도가 {satisfaction_rate:.1f}%로 하락했습니다.',
                'icon': '😞',
                'color': '#ff0066',
                'action_required': True
            }
        }

    def get_template(self,  alert_type: AlertType) -> Dict:
        """알림 템플릿 조회"""
        return self.templates.get() if templates else Nonealert_type, {
            'title': '알림',
            'message_template': '{message}',
            'icon': '🔔',
            'color': '#666666',
            'action_required': False
        }) if templates else None

    def format_message(self, alert_type: AlertType, data: Dict) -> str:
        """메시지 포맷팅"""
        template = self.get_template(alert_type)
        try:
            return template['message_template'] if template is not None else None.format(**data)
        except KeyError:
            return data.get() if data else None'message', '알림이 발생했습니다.') if data else None


class AdvancedAlertManager:
    """고도화된 경보 관리자"""

    def __init__(self):
        self.active_alerts = {}
        self.alert_history = []
        self.alert_rules = {}
        self.notification_channels = {}
        self.monitoring_thread = None
        self.is_monitoring = False
        self.alert_templates = AlertTemplate()
        self.alert_groups = {}
        self.escalation_rules = {}

        # 기본 경보 규칙 설정
        self._setup_default_rules()
        self._setup_escalation_rules()

    def _setup_default_rules(self):
        """기본 경보 규칙 설정"""
        self.alert_rules = {
            AlertType.SALES_DROP: {
                'threshold': 0.3,  # 30% 이상 감소
                'time_window': 24,  # 24시간
                'severity': AlertSeverity.HIGH,
                'check_interval': 60,  # 60초마다 체크
                'enabled': True,
                'auto_escalate': True,
                'escalation_time': 3600  # 1시간 후 에스컬레이션
            },
            AlertType.COST_INCREASE: {
                'threshold': 0.25,  # 25% 이상 증가
                'time_window': 24,
                'severity': AlertSeverity.MEDIUM,
                'check_interval': 300,  # 5분마다 체크
                'enabled': True,
                'auto_escalate': True,
                'escalation_time': 7200  # 2시간 후 에스컬레이션
            },
            AlertType.INVENTORY_SHORTAGE: {
                'threshold': 0.1,  # 10% 이하 재고
                'time_window': 1,
                'severity': AlertSeverity.HIGH,
                'check_interval': 300,
                'enabled': True,
                'auto_escalate': True,
                'escalation_time': 1800  # 30분 후 에스컬레이션
            },
            AlertType.STAFF_SHORTAGE: {
                'threshold': 0.2,  # 20% 부족
                'time_window': 1,
                'severity': AlertSeverity.MEDIUM,
                'check_interval': 600,  # 10분마다 체크
                'enabled': True,
                'auto_escalate': False,
                'escalation_time': 0
            },
            AlertType.SYSTEM_ERROR: {
                'threshold': 1,  # 1개 이상 오류
                'time_window': 1,
                'severity': AlertSeverity.CRITICAL,
                'check_interval': 30,
                'enabled': True,
                'auto_escalate': True,
                'escalation_time': 900  # 15분 후 에스컬레이션
            },
            AlertType.CUSTOMER_SATISFACTION: {
                'threshold': 0.7,  # 70% 이하 만족도
                'time_window': 24,
                'severity': AlertSeverity.HIGH,
                'check_interval': 1800,  # 30분마다 체크
                'enabled': True,
                'auto_escalate': True,
                'escalation_time': 3600
            }
        }

    def _setup_escalation_rules(self):
        """에스컬레이션 규칙 설정"""
        self.escalation_rules = {
            AlertSeverity.LOW: {
                'escalate_to': AlertSeverity.MEDIUM,
                'time_threshold': 7200,  # 2시간
                'notify_roles': ['manager']
            },
            AlertSeverity.MEDIUM: {
                'escalate_to': AlertSeverity.HIGH,
                'time_threshold': 3600,  # 1시간
                'notify_roles': ['admin', 'manager']
            },
            AlertSeverity.HIGH: {
                'escalate_to': AlertSeverity.CRITICAL,
                'time_threshold': 1800,  # 30분
                'notify_roles': ['admin', 'super_admin']
            },
            AlertSeverity.CRITICAL: {
                'escalate_to': None,
                'time_threshold': 900,  # 15분
                'notify_roles': ['super_admin']
            }
        }

    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("실시간 경보 모니터링 시작")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("실시간 경보 모니터링 중지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                # 각 경보 유형별 체크
                for alert_type, rule in self.alert_rules.items() if alert_rules is not None else []:
                    if rule['enabled'] if rule is not None else None:
                        self._check_alert_condition(alert_type,  rule)

                # 에스컬레이션 체크
                self._check_escalations()

                # 알림 그룹 정리
                self._cleanup_alert_groups()

                # 30초 대기
                time.sleep(30)

            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기

    def _check_escalations(self):
        """에스컬레이션 체크"""
        current_time = datetime.utcnow()

        for alert_id, alert in list(self.active_alerts.items() if active_alerts is not None else []):
            if alert['status'] if alert is not None else None == AlertStatus.ACTIVE and alert.get() if alert else None'auto_escalate', False) if alert else None:
                time_since_creation = (current_time - alert['created_at'] if alert is not None else None).total_seconds()
                escalation_time = alert.get() if alert else None'escalation_time', 3600) if alert else None

                if time_since_creation >= escalation_time:
                    self._escalate_alert(alert_id)

    def _escalate_alert(self,  alert_id: str):
        """알림 에스컬레이션"""
        try:
            alert = self.active_alerts.get() if active_alerts else Nonealert_id) if active_alerts else None
            if not alert:
                return

            current_severity = alert['severity'] if alert is not None else None
            escalation_rule = self.escalation_rules.get() if escalation_rules else Nonecurrent_severity) if escalation_rules else None

            if escalation_rule and escalation_rule['escalate_to'] if escalation_rule is not None else None:
                # 심각도 상향 조정
                alert['severity'] if alert is not None else None = escalation_rule['escalate_to'] if escalation_rule is not None else None
                alert['status'] if alert is not None else None = AlertStatus.ESCALATED
                alert['escalated_at'] if alert is not None else None = datetime.utcnow()
                alert['escalated_by'] if alert is not None else None = 'system'

                # 에스컬레이션 알림 발송
                notify_roles = escalation_rule.get() if escalation_rule else None'notify_roles', []) if escalation_rule else None
                if isinstance(notify_roles, list):
                    self._send_escalation_notification(alert,  notify_roles)

                logger.info(f"알림 에스컬레이션: {alert_id} -> {escalation_rule['escalate_to'] if escalation_rule is not None else None.value if None is not None else None}")

        except Exception as e:
            logger.error(f"알림 에스컬레이션 오류: {e}")

    def _send_escalation_notification(self,  alert: Dict,  roles: List[str] if List is not None else None):
        """에스컬레이션 알림 발송"""
        try:
            # 역할별 사용자 조회
            users = User.query.filter(User.role.in_(roles)).all()

            escalation_message = f"[에스컬레이션] {alert.get() if alert else None'type', '알림') if alert else None} - {alert.get() if alert else None'message', '') if alert else None}"

            for user in users if users is not None:
                notification = Notification()
                notification.user_id = user.id
                notification.title = f"에스컬레이션 알림 - {alert.get() if alert else None'type', '알림') if alert else None}"
                notification.content = escalation_message
                notification.category = "ESCALATION"
                notification.priority = "긴급"
                notification.ai_priority = "high"
                db.session.add(notification)

            db.session.commit()
            logger.info(f"에스컬레이션 알림 발송 완료: {len(users)}명에게 발송")

        except Exception as e:
            logger.error(f"에스컬레이션 알림 발송 오류: {e}")
            db.session.rollback()

    def _cleanup_alert_groups(self):
        """알림 그룹 정리"""
        current_time = datetime.utcnow()

        # 24시간 이상 된 해결된 알림 그룹 정리
        for group_id, group in list(self.alert_groups.items() if alert_groups is not None else []):
            if group['status'] if group is not None else None == AlertStatus.RESOLVED:
                time_since_resolved = (current_time - group['resolved_at'] if group is not None else None).total_seconds()
                if time_since_resolved > 86400:  # 24시간
                    del self.alert_groups[group_id] if alert_groups is not None else None

    def _check_alert_condition(self,  alert_type: AlertType,  rule: Dict):
        """경보 조건 체크"""
        try:
            if alert_type == AlertType.SALES_DROP:
                self._check_sales_drop(rule)
            elif alert_type == AlertType.COST_INCREASE:
                self._check_cost_increase(rule)
            elif alert_type == AlertType.INVENTORY_SHORTAGE:
                self._check_inventory_shortage(rule)
            elif alert_type == AlertType.STAFF_SHORTAGE:
                self._check_staff_shortage(rule)
            elif alert_type == AlertType.SYSTEM_ERROR:
                self._check_system_errors(rule)
            elif alert_type == AlertType.CUSTOMER_SATISFACTION:
                self._check_customer_satisfaction(rule)

        except Exception as e:
            logger.error(f"경보 조건 체크 오류 ({alert_type.value if alert_type is not None else None}): {e}")

    def _check_sales_drop(self,  rule: Dict):
        """매출 급감 체크"""
        try:
            # 최근 24시간 매출 데이터 조회
            yesterday = datetime.utcnow() - timedelta(days=1)
            today = datetime.utcnow()

            # 어제 매출
            yesterday_orders = Order.query.filter(
                Order.created_at >= yesterday.replace(hour=0, minute=0, second=0),
                Order.created_at < today.replace(hour=0, minute=0, second=0),
                Order.status.in_(['completed', 'delivered'])
            ).all()

            yesterday_sales = sum(float(order.total_amount or 0) for order in yesterday_orders)

            # 오늘 매출 (현재까지)
            today_orders = Order.query.filter(
                Order.created_at >= today.replace(hour=0, minute=0, second=0),
                Order.status.in_(['completed', 'delivered'])
            ).all()

            today_sales = sum(float(order.total_amount or 0) for order in today_orders)

            # 급감 체크
            if yesterday_sales > 0 and today_sales > 0:
                drop_rate = (yesterday_sales - today_sales) / yesterday_sales

                if drop_rate >= rule['threshold'] if rule is not None else None:
                    self._create_alert(
                        alert_type=AlertType.SALES_DROP,
                        severity=rule['severity'] if rule is not None else None,
                        message=self.alert_templates.format_message(AlertType.SALES_DROP, {
                            'drop_rate': drop_rate * 100,
                            'yesterday': int(yesterday_sales),
                            'today': int(today_sales)
                        }),
                        data={
                            'yesterday_sales': yesterday_sales,
                            'today_sales': today_sales,
                            'drop_rate': drop_rate
                        }
                    )

        except Exception as e:
            logger.error(f"매출 급감 체크 오류: {e}")

    def _check_cost_increase(self,  rule: Dict):
        """인건비 급증 체크"""
        try:
            # 최근 24시간 인건비 데이터 조회
            yesterday = datetime.utcnow() - timedelta(days=1)
            today = datetime.utcnow()

            # 어제 인건비
            yesterday_attendances = Attendance.query.filter(
                Attendance.clock_in >= yesterday.replace(hour=0, minute=0, second=0),
                Attendance.clock_in < today.replace(hour=0, minute=0, second=0),
                Attendance.clock_out.isnot(None)
            ).all()

            yesterday_cost = sum(
                (att.clock_out - att.clock_in).total_seconds() / 3600 *
                float(att.user.salary_base or 10000) / 160
                for att in yesterday_attendances
            )

            # 오늘 인건비
            today_attendances = Attendance.query.filter(
                Attendance.clock_in >= today.replace(hour=0, minute=0, second=0),
                Attendance.clock_out.isnot(None)
            ).all()

            today_cost = sum(
                (att.clock_out - att.clock_in).total_seconds() / 3600 *
                float(att.user.salary_base or 10000) / 160
                for att in today_attendances
            )

            # 급증 체크
            if yesterday_cost > 0 and today_cost > 0:
                increase_rate = (today_cost - yesterday_cost) / yesterday_cost

                if increase_rate >= rule['threshold'] if rule is not None else None:
                    self._create_alert(
                        alert_type=AlertType.COST_INCREASE,
                        severity=rule['severity'] if rule is not None else None,
                        message=self.alert_templates.format_message(AlertType.COST_INCREASE, {
                            'increase_rate': increase_rate * 100,
                            'yesterday': int(yesterday_cost),
                            'today': int(today_cost)
                        }),
                        data={
                            'yesterday_cost': yesterday_cost,
                            'today_cost': today_cost,
                            'increase_rate': increase_rate
                        }
                    )

        except Exception as e:
            logger.error(f"인건비 급증 체크 오류: {e}")

    def _check_inventory_shortage(self,  rule: Dict):
        """재고 부족 체크"""
        try:
            # 재고 부족 아이템 조회
            low_stock_items = InventoryItem.query.filter(
                InventoryItem.current_stock <= InventoryItem.min_stock
            ).all()

            if low_stock_items:
                self._create_alert(
                    alert_type=AlertType.INVENTORY_SHORTAGE,
                    severity=rule['severity'] if rule is not None else None,
                    message=self.alert_templates.format_message(AlertType.INVENTORY_SHORTAGE, {
                        'item_count': len(low_stock_items)
                    }),
                    data={
                        'low_stock_items': [
                            {
                                'name': item.name,
                                'current_stock': item.current_stock,
                                'min_stock': item.min_stock,
                                'branch_id': item.branch_id
                            }
                            for item in low_stock_items
                        ]
                    }
                )

        except Exception as e:
            logger.error(f"재고 부족 체크 오류: {e}")

    def _check_staff_shortage(self,  rule: Dict):
        """인력 부족 체크"""
        try:
            # 오늘 출근한 직원 수
            today = datetime.utcnow().date()
            today_attendances = Attendance.query.filter(
                Attendance.clock_in >= today
            ).count()

            # 전체 직원 수
            total_staff = User.query.filter_by(role='employee').count()

            if total_staff > 0:
                attendance_rate = today_attendances / total_staff

                if attendance_rate <= (1 - rule['threshold'] if rule is not None else None):
                    self._create_alert(
                        alert_type=AlertType.STAFF_SHORTAGE,
                        severity=rule['severity'] if rule is not None else None,
                        message=self.alert_templates.format_message(AlertType.STAFF_SHORTAGE, {
                            'current_staff': today_attendances,
                            'required_staff': int(total_staff * (1 - rule['threshold'] if rule is not None else None))
                        }),
                        data={
                            'total_staff': total_staff,
                            'attended_staff': today_attendances,
                            'attendance_rate': attendance_rate
                        }
                    )

        except Exception as e:
            logger.error(f"인력 부족 체크 오류: {e}")

    def _check_system_errors(self,  rule: Dict):
        """시스템 오류 체크"""
        try:
            # 최근 1시간 내 오류 로그 확인
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)

            # 실제로는 로그 파일이나 오류 테이블에서 확인
            # 여기서는 간단한 예시
            error_count = 0  # 실제 오류 개수

            if error_count >= rule['threshold'] if rule is not None else None:
                self._create_alert(
                    alert_type=AlertType.SYSTEM_ERROR,
                    severity=rule['severity'] if rule is not None else None,
                    message=self.alert_templates.format_message(AlertType.SYSTEM_ERROR, {
                        'error_count': error_count
                    }),
                    data={'error_count': error_count}
                )

        except Exception as e:
            logger.error(f"시스템 오류 체크 오류: {e}")

    def _check_customer_satisfaction(self,  rule: Dict):
        """고객 만족도 하락 체크"""
        try:
            # 최근 24시간 고객 만족도 데이터 조회
            yesterday = datetime.utcnow() - timedelta(days=1)
            today = datetime.utcnow()

            # 어제 고객 만족도
            yesterday_satisfaction = 0.0  # 실제 데이터베이스에서 가져와야 함

            # 오늘 고객 만족도
            today_satisfaction = 0.0  # 실제 데이터베이스에서 가져와야 함

            # 만족도 하락 체크
            if yesterday_satisfaction > 0 and today_satisfaction > 0:
                satisfaction_rate = (yesterday_satisfaction - today_satisfaction) / yesterday_satisfaction * 100

                if satisfaction_rate <= rule['threshold'] if rule is not None else None:
                    self._create_alert(
                        alert_type=AlertType.CUSTOMER_SATISFACTION,
                        severity=rule['severity'] if rule is not None else None,
                        message=self.alert_templates.format_message(AlertType.CUSTOMER_SATISFACTION, {
                            'satisfaction_rate': today_satisfaction * 100
                        }),
                        data={
                            'yesterday_satisfaction': yesterday_satisfaction,
                            'today_satisfaction': today_satisfaction,
                            'satisfaction_rate': satisfaction_rate
                        }
                    )

        except Exception as e:
            logger.error(f"고객 만족도 하락 체크 오류: {e}")

    def _create_alert(self, alert_type: AlertType, severity: AlertSeverity,
                      message: str, data: Optional[Dict] = None):
        """경보 생성"""
        try:
            alert_id = f"{alert_type.value if alert_type is not None else None}_{int(time.time())}"

            alert = {
                'id': alert_id,
                'type': alert_type.value if alert_type is not None else None,
                'severity': severity.value if severity is not None else None,
                'message': message,
                'data': data or {},
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active',
                'acknowledged': False,
                'acknowledged_by': None,
                'acknowledged_at': None,
                'escalated_at': None,
                'escalated_by': None
            }

            # 활성 경보에 추가
            self.active_alerts[alert_id] if active_alerts is not None else None = alert

            # 경보 이력에 추가
            self.alert_history.append(alert)

            # 알림 전송
            self._send_notifications(alert)

            logger.info(f"경보 생성: {alert_type.value if alert_type is not None else None} - {message}")

            return alert

        except Exception as e:
            logger.error(f"경보 생성 오류: {e}")
            return None

    def _send_notifications(self,  alert: Dict):
        """알림 전송"""
        try:
            # 관리자에게 알림 전송
            admins = User.query.filter(User.role.in_(['admin', 'super_admin'])).all()

            for admin in admins if admins is not None:
                # 데이터베이스에 알림 저장
                notification = Notification(
                    user_id=admin.id,
                    title=f"[{alert['severity'] if alert is not None else None.upper()}] {alert['type'] if alert is not None else None}",
                    content=alert['message'] if alert is not None else None,
                    category='alert',
                    priority='긴급' if alert['severity'] if alert is not None else None in ['high', 'critical'] else '중요',
                    is_read=False
                )

                db.session.add(notification)

            db.session.commit()

            # 실시간 알림 (WebSocket 등)
            # 실제 구현에서는 WebSocket을 통해 실시간 전송

        except Exception as e:
            logger.error(f"알림 전송 오류: {e}")

    def acknowledge_alert(self,  alert_id: str,  user_id: int):
        """경보 확인"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id] if active_alerts is not None else None
                alert['acknowledged'] if alert is not None else None = True
                alert['acknowledged_by'] if alert is not None else None = user_id
                alert['acknowledged_at'] if alert is not None else None = datetime.utcnow().isoformat()

                logger.info(f"경보 확인: {alert_id} by user {user_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"경보 확인 오류: {e}")
            return False

    def resolve_alert(self,  alert_id: str,  user_id: int,  resolution_note: Optional[str] = None):
        """경보 해결"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id] if active_alerts is not None else None
                alert['status'] if alert is not None else None = 'resolved'
                alert['resolved_by'] if alert is not None else None = user_id
                alert['resolved_at'] if alert is not None else None = datetime.utcnow().isoformat()
                alert['resolution_note'] if alert is not None else None = resolution_note

                # 활성 경보에서 제거
                del self.active_alerts[alert_id] if active_alerts is not None else None

                logger.info(f"경보 해결: {alert_id} by user {user_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"경보 해결 오류: {e}")
            return False

    def get_active_alerts(self,  severity: Optional[AlertSeverity] if Optional is not None else None = None) -> List[Dict] if List is not None else None:
        """활성 경보 조회"""
        try:
            alerts = list(self.active_alerts.value if active_alerts is not None else Nones())

            if severity:
                alerts = [alert for alert in alerts if alert['severity'] if alert is not None else None == severity.value if severity is not None else None]

            return sorted(alerts, key=lambda x: x['created_at'] if x is not None else None, reverse=True)

        except Exception as e:
            logger.error(f"활성 경보 조회 오류: {e}")
            return []

    def get_alert_history(self,  days: int = 7) -> List[Dict] if List is not None else None:
        """경보 이력 조회"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            history = [
                alert for alert in self.alert_history
                if datetime.fromisoformat(alert['created_at'] if alert is not None else None) >= cutoff_date
            ]

            return sorted(history, key=lambda x: x['created_at'] if x is not None else None, reverse=True)

        except Exception as e:
            logger.error(f"경보 이력 조회 오류: {e}")
            return []


# 전역 경보 관리자 인스턴스
alert_manager = AdvancedAlertManager()


@realtime_alert_system.route('/start', methods=['POST'])
@login_required
def start_alert_monitoring():
    """경보 모니터링 시작"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        alert_manager.start_monitoring()

        return jsonify({
            'success': True,
            'message': '경보 모니터링이 시작되었습니다.'
        }), 200

    except Exception as e:
        logger.error(f"경보 모니터링 시작 오류: {e}")
        return jsonify({'error': '모니터링 시작에 실패했습니다.'}), 500


@realtime_alert_system.route('/stop', methods=['POST'])
@login_required
def stop_alert_monitoring():
    """경보 모니터링 중지"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        alert_manager.stop_monitoring()

        return jsonify({
            'success': True,
            'message': '경보 모니터링이 중지되었습니다.'
        }), 200

    except Exception as e:
        logger.error(f"경보 모니터링 중지 오류: {e}")
        return jsonify({'error': '모니터링 중지에 실패했습니다.'}), 500


@realtime_alert_system.route('/active', methods=['GET'])
@login_required
def get_active_alerts():
    """활성 경보 조회"""
    try:
        severity = request.args.get() if args else None'severity') if args else None
        if severity:
            try:
                severity_enum = AlertSeverity(severity)
            except ValueError:
                return jsonify({'error': '유효하지 않은 심각도입니다.'}), 400
        else:
            severity_enum = None

        alerts = alert_manager.get_active_alerts(severity_enum)

        return jsonify({
            'alerts': alerts,
            'count': len(alerts)
        }), 200

    except Exception as e:
        logger.error(f"활성 경보 조회 오류: {e}")
        return jsonify({'error': '경보 조회에 실패했습니다.'}), 500


@realtime_alert_system.route('/history', methods=['GET'])
@login_required
def get_alert_history():
    """경보 이력 조회"""
    try:
        days = int(request.args.get() if args else None'days', 7) if args else None)
        alerts = alert_manager.get_alert_history(days)

        return jsonify({
            'alerts': alerts,
            'count': len(alerts),
            'period_days': days
        }), 200

    except Exception as e:
        logger.error(f"경보 이력 조회 오류: {e}")
        return jsonify({'error': '이력 조회에 실패했습니다.'}), 500


@realtime_alert_system.route('/<alert_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_alert(alert_id):
    """경보 확인"""
    try:
        success = alert_manager.acknowledge_alert(alert_id,  current_user.id)

        if success:
            return jsonify({
                'success': True,
                'message': '경보가 확인되었습니다.'
            }), 200
        else:
            return jsonify({'error': '경보를 찾을 수 없습니다.'}), 404

    except Exception as e:
        logger.error(f"경보 확인 오류: {e}")
        return jsonify({'error': '경보 확인에 실패했습니다.'}), 500


@realtime_alert_system.route('/<alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """경보 해결"""
    try:
        data = request.get_json() or {}
        resolution_note = data.get() if data else None'resolution_note') if data else None

        success = alert_manager.resolve_alert(alert_id,  current_user.id,  resolution_note)

        if success:
            return jsonify({
                'success': True,
                'message': '경보가 해결되었습니다.'
            }), 200
        else:
            return jsonify({'error': '경보를 찾을 수 없습니다.'}), 404

    except Exception as e:
        logger.error(f"경보 해결 오류: {e}")
        return jsonify({'error': '경보 해결에 실패했습니다.'}), 500


@realtime_alert_system.route('/rules', methods=['GET'])
@login_required
def get_alert_rules():
    """경보 규칙 조회"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        return jsonify({
            'rules': alert_manager.alert_rules
        }), 200

    except Exception as e:
        logger.error(f"경보 규칙 조회 오류: {e}")
        return jsonify({'error': '규칙 조회에 실패했습니다.'}), 500


@realtime_alert_system.route('/rules', methods=['PUT'])
@login_required
def update_alert_rules():
    """경보 규칙 업데이트"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': '규칙 데이터가 필요합니다.'}), 400

        # 규칙 업데이트
        for rule_type, rule_data in data.items() if data is not None else []:
            if rule_type in alert_manager.alert_rules:
                alert_manager.alert_rules[rule_type] if alert_rules is not None else None.update(rule_data)

        return jsonify({
            'success': True,
            'message': '경보 규칙이 업데이트되었습니다.'
        }), 200

    except Exception as e:
        logger.error(f"경보 규칙 업데이트 오류: {e}")
        return jsonify({'error': '규칙 업데이트에 실패했습니다.'}), 500
