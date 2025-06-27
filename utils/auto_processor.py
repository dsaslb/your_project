"""
신고/이의제기 자동 처리 규칙 관리
"""

from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from extensions import db
from models import AttendanceDispute, User, Notification
from utils.logger import log_action, log_error
from utils.notification_automation import send_notification
from utils.assignee_manager import assignee_manager

class AutoProcessor:
    """자동 처리 규칙 관리 클래스"""
    
    def __init__(self):
        self.rules = {
            'sla_warning': {
                'enabled': True,
                'hours_before': 24,  # SLA 24시간 전 경고
                'message': 'SLA 임박 신고/이의제기 자동 경고'
            },
            'sla_overdue': {
                'enabled': True,
                'message': 'SLA 초과 신고/이의제기 자동 경고'
            },
            'repeated_reports': {
                'enabled': True,
                'threshold': 3,  # 3회 이상 신고 시
                'message': '반복 신고자 자동 경고'
            },
            'auto_approval': {
                'enabled': False,  # 기본 비활성화
                'keywords': ['오타', '실수', '기술적 오류'],
                'message': '경미한 신고 자동 승인'
            }
        }
    
    def process_all_rules(self):
        """모든 자동 처리 규칙 실행"""
        try:
            results = {
                'sla_warnings': self.process_sla_warnings(),
                'sla_overdue': self.process_sla_overdue(),
                'repeated_reports': self.process_repeated_reports(),
                'auto_approval': self.process_auto_approval()
            }
            
            log_action(
                user_id=None,
                action='AUTO_PROCESS_RULES_EXECUTED',
                details=f'Results: {results}'
            )
            
            return results
            
        except Exception as e:
            log_error(e, None, 'Auto process rules execution failed')
            return {'error': str(e)}
    
    def process_sla_warnings(self):
        """SLA 임박 경고 처리"""
        if not self.rules['sla_warning']['enabled']:
            return {'processed': 0, 'message': 'Disabled'}
        
        try:
            now = datetime.utcnow()
            warning_time = now + timedelta(hours=self.rules['sla_warning']['hours_before'])
            
            # SLA 임박 신고/이의제기 조회
            urgent_disputes = AttendanceDispute.query.filter(
                and_(
                    AttendanceDispute.status.in_(['pending', 'processing']),
                    AttendanceDispute.sla_due <= warning_time,
                    AttendanceDispute.sla_due > now
                )
            ).all()
            
            processed = 0
            for dispute in urgent_disputes:
                if dispute.assignee_id:
                    # 담당자에게 경고 알림
                    send_notification(
                        user_id=dispute.assignee_id,
                        content=f"{self.rules['sla_warning']['message']}: 신고 #{dispute.id} (SLA: {dispute.sla_due.strftime('%m-%d %H:%M')})",
                        category='SLA',
                        priority='중요'
                    )
                    processed += 1
            
            return {
                'processed': processed,
                'message': f'{processed}건 SLA 임박 경고 발송'
            }
            
        except Exception as e:
            log_error(e, None, 'SLA warning processing failed')
            return {'processed': 0, 'error': str(e)}
    
    def process_sla_overdue(self):
        """SLA 초과 처리"""
        if not self.rules['sla_overdue']['enabled']:
            return {'processed': 0, 'message': 'Disabled'}
        
        try:
            now = datetime.utcnow()
            
            # SLA 초과 신고/이의제기 조회
            overdue_disputes = AttendanceDispute.query.filter(
                and_(
                    AttendanceDispute.status.in_(['pending', 'processing']),
                    AttendanceDispute.sla_due < now
                )
            ).all()
            
            processed = 0
            for dispute in overdue_disputes:
                if dispute.assignee_id:
                    # 담당자에게 초과 경고
                    send_notification(
                        user_id=dispute.assignee_id,
                        content=f"{self.rules['sla_overdue']['message']}: 신고 #{dispute.id} (초과: {(now - dispute.sla_due).days}일)",
                        category='SLA',
                        priority='긴급'
                    )
                    
                    # 관리자에게도 알림
                    admins = User.query.filter_by(role='admin').all()
                    for admin in admins:
                        if admin.id != dispute.assignee_id:
                            send_notification(
                                user_id=admin.id,
                                content=f"SLA 초과 신고/이의제기: #{dispute.id} (담당자: {dispute.assignee.name or dispute.assignee.username})",
                                category='SLA',
                                priority='긴급'
                            )
                    
                    processed += 1
            
            return {
                'processed': processed,
                'message': f'{processed}건 SLA 초과 경고 발송'
            }
            
        except Exception as e:
            log_error(e, None, 'SLA overdue processing failed')
            return {'processed': 0, 'error': str(e)}
    
    def process_repeated_reports(self):
        """반복 신고자 처리"""
        if not self.rules['repeated_reports']['enabled']:
            return {'processed': 0, 'message': 'Disabled'}
        
        try:
            threshold = self.rules['repeated_reports']['threshold']
            
            # 최근 30일 내 반복 신고자 조회
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            repeated_users = db.session.query(
                AttendanceDispute.user_id,
                func.count().label('report_count')
            ).filter(
                AttendanceDispute.created_at >= thirty_days_ago
            ).group_by(AttendanceDispute.user_id).having(
                func.count() >= threshold
            ).all()
            
            processed = 0
            for user_id, count in repeated_users:
                # 반복 신고자에게 경고
                send_notification(
                    user_id=user_id,
                    content=f"반복 신고자 경고: 최근 30일 내 {count}회 신고/이의제기 접수",
                    category='경고',
                    priority='중요'
                )
                
                # 관리자에게 알림
                admins = User.query.filter_by(role='admin').all()
                for admin in admins:
                    user = User.query.get(user_id)
                    send_notification(
                        user_id=admin.id,
                        content=f"반복 신고자 감지: {user.name or user.username} (최근 30일 {count}회)",
                        category='모니터링',
                        priority='중요'
                    )
                
                processed += 1
            
            return {
                'processed': processed,
                'message': f'{processed}명 반복 신고자 경고 발송'
            }
            
        except Exception as e:
            log_error(e, None, 'Repeated reports processing failed')
            return {'processed': 0, 'error': str(e)}
    
    def process_auto_approval(self):
        """경미한 신고 자동 승인"""
        if not self.rules['auto_approval']['enabled']:
            return {'processed': 0, 'message': 'Disabled'}
        
        try:
            keywords = self.rules['auto_approval']['keywords']
            
            # 경미한 신고 조회 (키워드 포함)
            minor_disputes = AttendanceDispute.query.filter(
                and_(
                    AttendanceDispute.status == 'pending',
                    or_(*[AttendanceDispute.reason.contains(keyword) for keyword in keywords])
                )
            ).all()
            
            processed = 0
            for dispute in minor_disputes:
                # 자동 승인 처리
                dispute.status = 'resolved'
                dispute.admin_reply = f"자동 승인: {self.rules['auto_approval']['message']}"
                dispute.admin_id = None  # 시스템 자동 처리
                dispute.updated_at = datetime.utcnow()
                
                # 신고자에게 알림
                send_notification(
                    user_id=dispute.user_id,
                    content=f"신고/이의제기 자동 승인: {dispute.admin_reply}",
                    category='신고/이의제기',
                    link=f"/attendance/dispute/{dispute.id}"
                )
                
                processed += 1
            
            if processed > 0:
                db.session.commit()
            
            return {
                'processed': processed,
                'message': f'{processed}건 자동 승인 처리'
            }
            
        except Exception as e:
            log_error(e, None, 'Auto approval processing failed')
            db.session.rollback()
            return {'processed': 0, 'error': str(e)}
    
    def update_rule(self, rule_name, **kwargs):
        """규칙 설정 업데이트"""
        if rule_name in self.rules:
            self.rules[rule_name].update(kwargs)
            return True
        return False
    
    def get_rule_status(self):
        """규칙 상태 조회"""
        return self.rules

# 전역 인스턴스
auto_processor = AutoProcessor()
