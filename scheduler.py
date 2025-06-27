from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date, timedelta
import logging
from models import User, Attendance, db
from sqlalchemy import extract, func, and_
from utils.auto_processor import auto_processor
from utils.email_utils import email_service

logger = logging.getLogger(__name__)

class AttendanceScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()
    
    def setup_jobs(self):
        """스케줄 작업 설정"""
        try:
            # 매주 월요일 오전 8시에 주간 리포트 발송
            self.scheduler.add_job(
                self.send_weekly_report,
                CronTrigger(day_of_week='mon', hour=8),
                id='weekly_report',
                name='주간 근태 리포트 발송',
                replace_existing=True
            )
            
            # 매월 1일 오전 9시에 월간 리포트 발송
            self.scheduler.add_job(
                self.send_monthly_report,
                CronTrigger(day=1, hour=9),
                id='monthly_report',
                name='월간 근태 리포트 발송',
                replace_existing=True
            )
            
            # 매일 오전 7시에 출근 알림 체크
            self.scheduler.add_job(
                self.check_attendance_alerts,
                CronTrigger(hour=7),
                id='attendance_alerts',
                name='출근 알림 체크',
                replace_existing=True
            )
            
            # 매일 오후 6시에 퇴근 알림 체크
            self.scheduler.add_job(
                self.check_leave_alerts,
                CronTrigger(hour=18),
                id='leave_alerts',
                name='퇴근 알림 체크',
                replace_existing=True
            )
            
            logger.info("스케줄러 작업이 설정되었습니다.")
            
        except Exception as e:
            logger.error(f"스케줄러 설정 중 오류: {str(e)}")
    
    def start(self):
        """스케줄러 시작"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("스케줄러가 시작되었습니다.")
        except Exception as e:
            logger.error(f"스케줄러 시작 중 오류: {str(e)}")
    
    def stop(self):
        """스케줄러 중지"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("스케줄러가 중지되었습니다.")
        except Exception as e:
            logger.error(f"스케줄러 중지 중 오류: {str(e)}")
    
    def send_weekly_report(self):
        """주간 근태 리포트 발송"""
        try:
            logger.info("주간 근태 리포트 발송 시작")
            
            # 관리자 목록 조회
            admins = User.query.filter_by(role='admin').all()
            
            if not admins:
                logger.warning("발송할 관리자가 없습니다.")
                return
            
            # PDF 생성 (간단한 버전)
            report_data = self.generate_weekly_report_data()
            
            # 이메일 발송 (테스트용)
            for admin in admins:
                if admin.email:
                    self.send_email_report(
                        admin.email,
                        "주간 근태 리포트",
                        report_data,
                        "week"
                    )
            
            logger.info(f"주간 리포트 발송 완료: {len(admins)}명")
            
        except Exception as e:
            logger.error(f"주간 리포트 발송 중 오류: {str(e)}")
    
    def send_monthly_report(self):
        """월간 근태 리포트 발송"""
        try:
            logger.info("월간 근태 리포트 발송 시작")
            
            # 관리자 목록 조회
            admins = User.query.filter_by(role='admin').all()
            
            if not admins:
                logger.warning("발송할 관리자가 없습니다.")
                return
            
            # PDF 생성 (간단한 버전)
            report_data = self.generate_monthly_report_data()
            
            # 이메일 발송 (테스트용)
            for admin in admins:
                if admin.email:
                    self.send_email_report(
                        admin.email,
                        "월간 근태 리포트",
                        report_data,
                        "month"
                    )
            
            logger.info(f"월간 리포트 발송 완료: {len(admins)}명")
            
        except Exception as e:
            logger.error(f"월간 리포트 발송 중 오류: {str(e)}")
    
    def generate_weekly_report_data(self):
        """주간 리포트 데이터 생성"""
        try:
            # 지난 주 데이터
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
            
            # 근태 데이터 조회
            records = Attendance.query.filter(
                and_(
                    Attendance.clock_in >= start_date,
                    Attendance.clock_in <= end_date
                )
            ).all()
            
            # 통계 계산
            stats = {
                'period': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
                'total_records': len(records),
                'total_hours': 0,
                'late_count': 0,
                'early_leave_count': 0,
                'absent_count': 0,
                'users': {}
            }
            
            for record in records:
                user_id = record.user_id
                if user_id not in stats['users']:
                    stats['users'][user_id] = {
                        'name': record.user.name or record.user.username,
                        'days': 0,
                        'hours': 0,
                        'late': 0,
                        'early_leave': 0
                    }
                
                user_stats = stats['users'][user_id]
                user_stats['days'] += 1
                
                if record.clock_in and record.clock_out:
                    work_seconds = (record.clock_out - record.clock_in).total_seconds()
                    work_hours = work_seconds / 3600
                    stats['total_hours'] += work_hours
                    user_stats['hours'] += work_hours
                    
                    # 지각/조퇴 판정
                    if record.clock_in.time() > datetime.strptime('09:00', '%H:%M').time():
                        stats['late_count'] += 1
                        user_stats['late'] += 1
                    if record.clock_out.time() < datetime.strptime('18:00', '%H:%M').time():
                        stats['early_leave_count'] += 1
                        user_stats['early_leave'] += 1
                else:
                    stats['absent_count'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"주간 리포트 데이터 생성 중 오류: {str(e)}")
            return {}
    
    def generate_monthly_report_data(self):
        """월간 리포트 데이터 생성"""
        try:
            # 이번 달 데이터
            start_date = date.today().replace(day=1)
            end_date = date.today()
            
            # 근태 데이터 조회
            records = Attendance.query.filter(
                and_(
                    Attendance.clock_in >= start_date,
                    Attendance.clock_in <= end_date
                )
            ).all()
            
            # 통계 계산 (주간과 동일한 로직)
            stats = {
                'period': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
                'total_records': len(records),
                'total_hours': 0,
                'late_count': 0,
                'early_leave_count': 0,
                'absent_count': 0,
                'users': {}
            }
            
            for record in records:
                user_id = record.user_id
                if user_id not in stats['users']:
                    stats['users'][user_id] = {
                        'name': record.user.name or record.user.username,
                        'days': 0,
                        'hours': 0,
                        'late': 0,
                        'early_leave': 0
                    }
                
                user_stats = stats['users'][user_id]
                user_stats['days'] += 1
                
                if record.clock_in and record.clock_out:
                    work_seconds = (record.clock_out - record.clock_in).total_seconds()
                    work_hours = work_seconds / 3600
                    stats['total_hours'] += work_hours
                    user_stats['hours'] += work_hours
                    
                    # 지각/조퇴 판정
                    if record.clock_in.time() > datetime.strptime('09:00', '%H:%M').time():
                        stats['late_count'] += 1
                        user_stats['late'] += 1
                    if record.clock_out.time() < datetime.strptime('18:00', '%H:%M').time():
                        stats['early_leave_count'] += 1
                        user_stats['early_leave'] += 1
                else:
                    stats['absent_count'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"월간 리포트 데이터 생성 중 오류: {str(e)}")
            return {}
    
    def send_email_report(self, to_email, subject, report_data, period):
        """이메일 리포트 발송 (테스트용)"""
        try:
            # 간단한 텍스트 리포트 생성
            report_text = f"""
{subject}

기간: {report_data.get('period', 'N/A')}
총 기록: {report_data.get('total_records', 0)}건
총 근무시간: {round(report_data.get('total_hours', 0), 2)}시간
지각: {report_data.get('late_count', 0)}건
조퇴: {report_data.get('early_leave_count', 0)}건
결근: {report_data.get('absent_count', 0)}건

사용자별 상세:
"""
            
            for user_id, user_data in report_data.get('users', {}).items():
                report_text += f"""
- {user_data['name']}:
  근무일수: {user_data['days']}일
  총 근무시간: {round(user_data['hours'], 2)}시간
  지각: {user_data['late']}회
  조퇴: {user_data['early_leave']}회
"""
            
            # 실제 이메일 발송 대신 로그 출력
            logger.info(f"이메일 발송 (테스트): {to_email}")
            logger.info(f"제목: {subject}")
            logger.info(f"내용: {report_text}")
            
            # 실제 환경에서는 SMTP를 사용하여 발송
            # send_email(to_email, subject, report_text)
            
        except Exception as e:
            logger.error(f"이메일 리포트 발송 중 오류: {str(e)}")
    
    def check_attendance_alerts(self):
        """출근 알림 체크"""
        try:
            logger.info("출근 알림 체크 시작")
            
            today = date.today()
            current_time = datetime.now().time()
            
            # 아직 출근하지 않은 직원 체크
            users = User.query.filter(
                and_(
                    User.role == 'employee',
                    User.deleted_at == None
                )
            ).all()
            
            for user in users:
                # 오늘 출근 기록 확인
                today_attendance = Attendance.query.filter(
                    and_(
                        Attendance.user_id == user.id,
                        extract('date', Attendance.clock_in) == today
                    )
                ).first()
                
                # 출근하지 않았고, 출근 시간이 지났으면 알림
                if not today_attendance and current_time > datetime.strptime('09:30', '%H:%M').time():
                    logger.info(f"출근 알림: {user.name or user.username}")
                    # 실제 알림 발송 로직 추가 가능
            
            logger.info("출근 알림 체크 완료")
            
        except Exception as e:
            logger.error(f"출근 알림 체크 중 오류: {str(e)}")
    
    def check_leave_alerts(self):
        """퇴근 알림 체크"""
        try:
            logger.info("퇴근 알림 체크 시작")
            
            today = date.today()
            current_time = datetime.now().time()
            
            # 아직 퇴근하지 않은 직원 체크
            attendances = Attendance.query.filter(
                and_(
                    extract('date', Attendance.clock_in) == today,
                    Attendance.clock_out == None
                )
            ).all()
            
            for attendance in attendances:
                # 퇴근 시간이 지났으면 알림
                if current_time > datetime.strptime('18:30', '%H:%M').time():
                    user = attendance.user
                    logger.info(f"퇴근 알림: {user.name or user.username}")
                    # 실제 알림 발송 로직 추가 가능
            
            logger.info("퇴근 알림 체크 완료")
            
        except Exception as e:
            logger.error(f"퇴근 알림 체크 중 오류: {str(e)}")

def schedule_auto_processing():
    """자동 처리 규칙 스케줄링"""
    try:
        # 매시간 SLA 경고 체크
        scheduler.add_job(
            func=check_sla_warnings,
            trigger='interval',
            hours=1,
            id='sla_warnings_check',
            replace_existing=True
        )
        
        # 매일 반복 신고자 체크
        scheduler.add_job(
            func=check_repeated_reports,
            trigger='cron',
            hour=9,  # 오전 9시
            id='repeated_reports_check',
            replace_existing=True
        )
        
        # 매일 자동 승인 처리 (활성화된 경우)
        scheduler.add_job(
            func=process_auto_approval,
            trigger='cron',
            hour=8,  # 오전 8시
            id='auto_approval_process',
            replace_existing=True
        )
        
        print("✅ 자동 처리 규칙 스케줄링 완료")
        
    except Exception as e:
        print(f"❌ 자동 처리 규칙 스케줄링 실패: {str(e)}")

def check_sla_warnings():
    """SLA 경고 체크 및 이메일 발송"""
    try:
        results = auto_processor.process_all_rules()
        
        # 이메일 알림 발송
        for dispute in get_sla_urgent_disputes():
            if dispute.assignee_id and dispute.assignee.email:
                email_service.send_dispute_notification(dispute.id, 'sla_warning')
        
        for dispute in get_sla_overdue_disputes():
            if dispute.assignee_id and dispute.assignee.email:
                email_service.send_dispute_notification(dispute.id, 'sla_overdue')
        
        print(f"✅ SLA 경고 체크 완료: {results}")
        
    except Exception as e:
        print(f"❌ SLA 경고 체크 실패: {str(e)}")

def check_repeated_reports():
    """반복 신고자 체크"""
    try:
        result = auto_processor.process_repeated_reports()
        print(f"✅ 반복 신고자 체크 완료: {result}")
        
    except Exception as e:
        print(f"❌ 반복 신고자 체크 실패: {str(e)}")

def process_auto_approval():
    """자동 승인 처리"""
    try:
        result = auto_processor.process_auto_approval()
        print(f"✅ 자동 승인 처리 완료: {result}")
        
    except Exception as e:
        print(f"❌ 자동 승인 처리 실패: {str(e)}")

def get_sla_urgent_disputes():
    """SLA 임박 신고/이의제기 조회"""
    from datetime import datetime, timedelta
    from models import AttendanceDispute
    from sqlalchemy import and_
    
    now = datetime.utcnow()
    warning_time = now + timedelta(hours=24)
    
    return AttendanceDispute.query.filter(
        and_(
            AttendanceDispute.status.in_(['pending', 'processing']),
            AttendanceDispute.sla_due <= warning_time,
            AttendanceDispute.sla_due > now
        )
    ).all()

def get_sla_overdue_disputes():
    """SLA 초과 신고/이의제기 조회"""
    from datetime import datetime
    from models import AttendanceDispute
    from sqlalchemy import and_
    
    now = datetime.utcnow()
    
    return AttendanceDispute.query.filter(
        and_(
            AttendanceDispute.status.in_(['pending', 'processing']),
            AttendanceDispute.sla_due < now
        )
    ).all()

# 전역 스케줄러 인스턴스
scheduler = AttendanceScheduler()

def init_scheduler():
    """스케줄러 초기화"""
    scheduler.start()

def stop_scheduler():
    """스케줄러 중지"""
    scheduler.stop() 