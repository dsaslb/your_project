import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime, timedelta
from sqlalchemy import extract, func
from models import User, Attendance
from extensions import db
from utils.logger import log_action, log_error

def send_email(to_addr, subject, body, attachment_path=None):
    """
    이메일 발송 함수
    
    Args:
        to_addr (str): 수신자 이메일 주소
        subject (str): 이메일 제목
        body (str): 이메일 본문
        attachment_path (str, optional): 첨부파일 경로
    """
    try:
        # 실제 SMTP 설정 (실제 사용 시 config.py에서 가져오기)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', 'your-email@gmail.com')
        smtp_password = os.getenv('SMTP_PASSWORD', 'your-app-password')
        
        # 이메일 메시지 생성
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_addr
        msg['Subject'] = subject
        
        # 본문 추가
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 첨부파일 추가 (있는 경우)
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(attachment_path)}'
            )
            msg.attach(part)
        
        # SMTP 서버 연결 및 이메일 발송
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        text = msg.as_string()
        server.sendmail(smtp_username, to_addr, text)
        server.quit()
        
        print(f"✅ 이메일 발송 성공: {to_addr}")
        log_action(None, 'EMAIL_SENT', f'Email sent to {to_addr}: {subject}')
        
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {to_addr} - {str(e)}")
        log_error(e, None, f'Email send failed to {to_addr}')

def generate_monthly_report(user, year, month):
    """
    사용자의 월별 근태/급여 리포트 생성
    
    Args:
        user: User 객체
        year (int): 년도
        month (int): 월
    
    Returns:
        dict: 리포트 데이터
    """
    try:
        # 해당 월의 출근 기록 조회
        records = Attendance.query.filter(
            Attendance.user_id == user.id,
            extract('year', Attendance.clock_in) == year,
            extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
        ).all()
        
        # 통계 계산
        work_days = len(records)
        total_minutes = sum([(r.clock_out - r.clock_in).total_seconds() for r in records if r.clock_out]) // 60
        total_hours = total_minutes // 60
        overtime_hours = max(0, total_hours - (work_days * 8))  # 8시간 초과분
        
        # 급여 계산 (시급 12,000원 가정)
        hourly_wage = 12000
        regular_wage = min(total_hours, work_days * 8) * hourly_wage
        overtime_wage = overtime_hours * hourly_wage * 1.5  # 1.5배
        total_wage = regular_wage + overtime_wage
        
        # 지각/조퇴 통계
        late_count = 0
        early_leave_count = 0
        
        for record in records:
            if record.clock_in.time() > datetime.strptime('09:00', '%H:%M').time():
                late_count += 1
            if record.clock_out and record.clock_out.time() < datetime.strptime('18:00', '%H:%M').time():
                early_leave_count += 1
        
        return {
            'user': user,
            'year': year,
            'month': month,
            'work_days': work_days,
            'total_hours': total_hours,
            'overtime_hours': overtime_hours,
            'regular_wage': regular_wage,
            'overtime_wage': overtime_wage,
            'total_wage': total_wage,
            'late_count': late_count,
            'early_leave_count': early_leave_count,
            'records': records
        }
        
    except Exception as e:
        log_error(e, user.id if user else None, f'Monthly report generation failed for {year}-{month}')
        return None

def send_monthly_reports():
    """
    모든 사용자에게 월말 리포트 이메일 발송
    """
    try:
        users = User.query.filter_by(status='approved').all()
        now = datetime.utcnow()
        
        # 이전 달 계산
        if now.month == 1:
            prev_month = 12
            prev_year = now.year - 1
        else:
            prev_month = now.month - 1
            prev_year = now.year
        
        print(f"📧 {prev_year}년 {prev_month}월 월말 리포트 발송 시작...")
        
        success_count = 0
        fail_count = 0
        
        for user in users:
            try:
                if not user.email:
                    print(f"⚠️ 이메일 주소 없음: {user.username}")
                    continue
                
                # 리포트 생성
                report = generate_monthly_report(user, prev_year, prev_month)
                if not report:
                    continue
                
                # 이메일 본문 생성
                body = f"""
{user.name}님 안녕하세요,

{prev_year}년 {prev_month}월 근무/급여 리포트를 보내드립니다.

📊 근무 통계
• 근무일수: {report['work_days']}일
• 총 근무시간: {report['total_hours']}시간
• 초과근무: {report['overtime_hours']}시간
• 지각: {report['late_count']}회
• 조퇴: {report['early_leave_count']}회

💰 급여 내역
• 기본급: {report['regular_wage']:,}원
• 초과수당: {report['overtime_wage']:,}원
• 총 급여: {report['total_wage']:,}원

📅 상세 근무 기록은 시스템에서 확인하실 수 있습니다.

감사합니다.
식당 관리팀
                """.strip()
                
                # 이메일 발송
                subject = f"{prev_year}년 {prev_month}월 근무/급여 리포트"
                send_email(user.email, subject, body)
                
                success_count += 1
                print(f"✅ {user.username}에게 리포트 발송 완료")
                
            except Exception as e:
                fail_count += 1
                print(f"❌ {user.username} 리포트 발송 실패: {str(e)}")
                log_error(e, user.id, f'Monthly report email failed for {user.username}')
        
        print(f"📧 월말 리포트 발송 완료: 성공 {success_count}건, 실패 {fail_count}건")
        log_action(None, 'MONTHLY_REPORTS_SENT', f'Success: {success_count}, Failed: {fail_count}')
        
    except Exception as e:
        print(f"❌ 월말 리포트 발송 중 오류: {str(e)}")
        log_error(e, None, 'Monthly reports sending failed')

def send_attendance_reminder():
    """
    출근하지 않은 사용자에게 출근 알림 이메일 발송
    """
    try:
        today = datetime.utcnow().date()
        users = User.query.filter_by(status='approved').all()
        
        for user in users:
            try:
                if not user.email:
                    continue
                
                # 오늘 출근 기록 확인
                today_attendance = Attendance.query.filter(
                    Attendance.user_id == user.id,
                    func.date(Attendance.clock_in) == today
                ).first()
                
                if not today_attendance:
                    # 출근 알림 이메일 발송
                    subject = "출근 확인 알림"
                    body = f"""
{user.name}님 안녕하세요,

오늘({today.strftime('%Y년 %m월 %d일')}) 출근 기록이 없습니다.
혹시 출근을 잊으셨나요?

시스템에 로그인하여 출근 버튼을 눌러주시기 바랍니다.

감사합니다.
식당 관리팀
                    """.strip()
                    
                    send_email(user.email, subject, body)
                    print(f"📧 {user.username}에게 출근 알림 발송")
                    
            except Exception as e:
                print(f"❌ {user.username} 출근 알림 발송 실패: {str(e)}")
                
    except Exception as e:
        print(f"❌ 출근 알림 발송 중 오류: {str(e)}")
        log_error(e, None, 'Attendance reminder sending failed')

# CLI 명령어 추가
def create_email_commands(app):
    """이메일 관련 CLI 명령어 등록"""
    
    @app.cli.command('send-monthly-reports')
    def send_monthly_reports_command():
        """월말 리포트 이메일 발송"""
        print("월말 리포트 이메일 발송을 시작합니다...")
        send_monthly_reports()
        print("완료되었습니다.")
    
    @app.cli.command('send-attendance-reminder')
    def send_attendance_reminder_command():
        """출근 알림 이메일 발송"""
        print("출근 알림 이메일 발송을 시작합니다...")
        send_attendance_reminder()
        print("완료되었습니다.") 