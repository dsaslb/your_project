import logging
import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import render_template_string, current_app
from sqlalchemy import extract, func

from models import Attendance, AttendanceReport, User
from utils.logger import log_action, log_error

logger = logging.getLogger(__name__)


def send_email(to_addr, subject, body, html_body=None):
    """이메일 발송 함수"""
    try:
        # SMTP 설정 확인
        smtp_server = current_app.config.get("SMTP_SERVER")
        smtp_port = current_app.config.get("SMTP_PORT", 587)
        smtp_username = current_app.config.get("SMTP_USERNAME")
        smtp_password = current_app.config.get("SMTP_PASSWORD")

        if not all([smtp_server, smtp_username, smtp_password]):
            logger.warning("SMTP 설정이 완료되지 않았습니다.")
            return False

        # 이메일 메시지 생성
        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_username or ""
        msg["To"] = to_addr
        msg["Subject"] = subject

        # 텍스트 본문
        text_part = MIMEText(body, "plain", "utf-8")
        msg.attach(text_part)

        # HTML 본문 (있는 경우)
        if html_body:
            html_part = MIMEText(html_body, "html", "utf-8")
            msg.attach(html_part)

        # SMTP 서버 연결 및 발송
        if smtp_server:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            logger.error("SMTP 서버 설정이 없습니다.")
            return False

        logger.info(f"✅ 이메일 발송 성공: {to_addr}")
        return True

    except Exception as e:
        logger.error(f"❌ 이메일 발송 실패: {to_addr} - {str(e)}")
        return False


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
            extract("year", Attendance.clock_in) == year,
            extract("month", Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None),
        ).all()

        # 통계 계산
        work_days = len(records)
        total_minutes = (
            sum(
                [
                    (r.clock_out - r.clock_in).total_seconds()
                    for r in records
                    if r.clock_out
                ]
            )
            // 60
        )
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
            if record.clock_in.time() > datetime.strptime("09:00", "%H:%M").time():
                late_count += 1
            if (
                record.clock_out
                and record.clock_out.time() < datetime.strptime("18:00", "%H:%M").time()
            ):
                early_leave_count += 1

        return {
            "user": user,
            "year": year,
            "month": month,
            "work_days": work_days,
            "total_hours": total_hours,
            "overtime_hours": overtime_hours,
            "regular_wage": regular_wage,
            "overtime_wage": overtime_wage,
            "total_wage": total_wage,
            "late_count": late_count,
            "early_leave_count": early_leave_count,
            "records": records,
        }

    except Exception as e:
        log_error(
            e,
            user.id if user else None,
            f"Monthly report generation failed for {year}-{month}",
        )
        return None


def send_monthly_reports():
    """
    모든 사용자에게 월말 리포트 이메일 발송
    """
    try:
        users = User.query.filter_by(status="approved").all()
        now = datetime.utcnow()

        # 이전 달 계산
        if now.month == 1:
            prev_month = 12
            prev_year = now.year - 1
        else:
            prev_month = now.month - 1
            prev_year = now.year

        logger.info(f"📧 {prev_year}년 {prev_month}월 월말 리포트 발송 시작...")

        success_count = 0
        fail_count = 0

        for user in users:
            try:
                if not user.email:
                    logger.warning(f"⚠️ 이메일 주소 없음: {user.username}")
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
                logger.info(f"✅ {user.username}에게 리포트 발송 완료")

            except Exception as e:
                fail_count += 1
                logger.error(f"❌ {user.username} 리포트 발송 실패: {str(e)}")
                log_error(
                    e, user.id, f"Monthly report email failed for {user.username}"
                )

        logger.info(f"📧 월말 리포트 발송 완료: 성공 {success_count}건, 실패 {fail_count}건")
        log_action(
            None,
            "MONTHLY_REPORTS_SENT",
            f"Success: {success_count}, Failed: {fail_count}",
        )

    except Exception as e:
        logger.error(f"❌ 월말 리포트 발송 중 오류: {str(e)}")
        log_error(e, None, "Monthly reports sending failed")


def send_attendance_reminder():
    """
    출근하지 않은 사용자에게 출근 알림 이메일 발송
    """
    try:
        today = datetime.utcnow().date()
        users = User.query.filter_by(status="approved").all()

        for user in users:
            try:
                if not user.email:
                    continue

                # 오늘 출근 기록 확인
                today_attendance = Attendance.query.filter(
                    Attendance.user_id == user.id,
                    func.date(Attendance.clock_in) == today,
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
                    logger.info(f"📧 {user.username}에게 출근 알림 발송")

            except Exception as e:
                logger.error(f"❌ {user.username} 출근 알림 발송 실패: {str(e)}")

    except Exception as e:
        logger.error(f"❌ 출근 알림 발송 중 오류: {str(e)}")
        log_error(e, None, "Attendance reminder sending failed")


class EmailService:
    """이메일 서비스 클래스"""

    def __init__(self):
        self.smtp_config = {
            "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "use_tls": os.getenv("SMTP_USE_TLS", "True").lower() == "true",
        }

        self.from_email = os.getenv("FROM_EMAIL", self.smtp_config["username"])
        self.from_name = os.getenv("FROM_NAME", "레스토랑 관리 시스템")

    def send_email(
        self, to_email, subject, html_content, text_content=None, attachments=None
    ):
        """이메일 발송"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # HTML 버전
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)

            # 텍스트 버전 (있는 경우)
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                msg.attach(text_part)

            # 첨부파일 (있는 경우)
            if attachments:
                for filename, filepath in attachments.items():
                    with open(filepath, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition", f"attachment; filename= {filename}"
                        )
                        msg.attach(part)

            # SMTP 서버 연결 및 발송
            server = smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"])
            if self.smtp_config["use_tls"]:
                server.starttls()

            server.login(self.smtp_config["username"], self.smtp_config["password"])
            server.send_message(msg)
            server.quit()

            return True, "이메일 발송 성공"

        except Exception as e:
            log_error(e, None, f"Email sending failed to {to_email}")
            return False, f"이메일 발송 실패: {str(e)}"

    def send_dispute_notification(self, dispute_id, notification_type="created"):
        """신고/이의제기 알림 이메일 발송"""
        try:
            dispute = AttendanceReport.query.get(dispute_id)
            if not dispute:
                return False, "신고/이의제기를 찾을 수 없습니다."

            user = dispute.user
            assignee = dispute.assignee if dispute.assignee_id else None

            if notification_type == "created":
                # 신고 생성 시 담당자에게 알림
                if assignee and assignee.email:
                    subject = f"[신고/이의제기 접수] 신고 #{dispute.id}"
                    html_content = self._get_dispute_created_template(dispute, assignee)
                    return self.send_email(assignee.email, subject, html_content)

            elif notification_type == "assigned":
                # 담당자 배정 시 알림
                if assignee and assignee.email:
                    subject = f"[담당자 배정] 신고 #{dispute.id}"
                    html_content = self._get_dispute_assigned_template(
                        dispute, assignee
                    )
                    return self.send_email(assignee.email, subject, html_content)

            elif notification_type == "replied":
                # 답변 등록 시 신고자에게 알림
                if user.email:
                    subject = f"[답변 등록] 신고 #{dispute.id}"
                    html_content = self._get_dispute_replied_template(dispute, user)
                    return self.send_email(user.email, subject, html_content)

            elif notification_type == "sla_warning":
                # SLA 임박 경고
                if assignee and assignee.email:
                    subject = f"[SLA 임박 경고] 신고 #{dispute.id}"
                    html_content = self._get_sla_warning_template(dispute, assignee)
                    return self.send_email(assignee.email, subject, html_content)

            elif notification_type == "sla_overdue":
                # SLA 초과 경고
                if assignee and assignee.email:
                    subject = f"[SLA 초과 경고] 신고 #{dispute.id}"
                    html_content = self._get_sla_overdue_template(dispute, assignee)
                    return self.send_email(assignee.email, subject, html_content)

            return False, "지원하지 않는 알림 유형입니다."

        except Exception as e:
            log_error(e, None, f"Dispute email notification failed: {dispute_id}")
            return False, f"이메일 알림 발송 실패: {str(e)}"

    def _get_dispute_created_template(self, dispute, assignee):
        """신고 생성 알림 템플릿"""
        return render_template_string(
            """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #007bff; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f8f9fa; }
                .info-box { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>신고/이의제기 접수 알림</h2>
                </div>
                <div class="content">
                    <p><strong>{{ assignee.name or assignee.username }}</strong>님,</p>
                    <p>새로운 신고/이의제기가 접수되어 담당자로 배정되었습니다.</p>
                    
                    <div class="info-box">
                        <h3>신고 정보</h3>
                        <p><strong>신고 ID:</strong> #{{ dispute.id }}</p>
                        <p><strong>신고자:</strong> {{ dispute.user.name or dispute.user.username }}</p>
                        <p><strong>유형:</strong> {{ '신고' if dispute.dispute_type == 'report' else '이의제기' }}</p>
                        <p><strong>사유:</strong> {{ dispute.reason[:100] }}{% if dispute.reason|length > 100 %}...{% endif %}</p>
                        <p><strong>접수일시:</strong> {{ dispute.created_at.strftime('%Y년 %m월 %d일 %H:%M') }}</p>
                        <p><strong>SLA 기한:</strong> {{ dispute.sla_due.strftime('%Y년 %m월 %d일 %H:%M') if dispute.sla_due else '미설정' }}</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{{ url_for('my_reports.my_reports', _external=True) }}" class="btn">담당 신고/이의제기 확인</a>
                    </p>
                </div>
                <div class="footer">
                    <p>이 이메일은 레스토랑 관리 시스템에서 자동으로 발송되었습니다.</p>
                    <p>문의사항이 있으시면 관리자에게 연락해주세요.</p>
                </div>
            </div>
        </body>
        </html>
        """,
            dispute=dispute,
            assignee=assignee,
        )

    def _get_dispute_assigned_template(self, dispute, assignee):
        """담당자 배정 알림 템플릿"""
        return render_template_string(
            """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #28a745; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f8f9fa; }
                .info-box { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                .btn { display: inline-block; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>담당자 배정 알림</h2>
                </div>
                <div class="content">
                    <p><strong>{{ assignee.name or assignee.username }}</strong>님,</p>
                    <p>신고/이의제기 담당자로 배정되었습니다.</p>
                    
                    <div class="info-box">
                        <h3>배정 정보</h3>
                        <p><strong>신고 ID:</strong> #{{ dispute.id }}</p>
                        <p><strong>신고자:</strong> {{ dispute.user.name or dispute.user.username }}</p>
                        <p><strong>유형:</strong> {{ '신고' if dispute.dispute_type == 'report' else '이의제기' }}</p>
                        <p><strong>SLA 기한:</strong> {{ dispute.sla_due.strftime('%Y년 %m월 %d일 %H:%M') if dispute.sla_due else '미설정' }}</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{{ url_for('my_reports.my_reports', _external=True) }}" class="btn">담당 신고/이의제기 확인</a>
                    </p>
                </div>
                <div class="footer">
                    <p>이 이메일은 레스토랑 관리 시스템에서 자동으로 발송되었습니다.</p>
                </div>
            </div>
        </body>
        </html>
        """,
            dispute=dispute,
            assignee=assignee,
        )

    def _get_dispute_replied_template(self, dispute, user):
        """답변 등록 알림 템플릿"""
        return render_template_string(
            """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #17a2b8; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f8f9fa; }
                .info-box { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #17a2b8; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                .btn { display: inline-block; padding: 10px 20px; background: #17a2b8; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>답변 등록 알림</h2>
                </div>
                <div class="content">
                    <p><strong>{{ user.name or user.username }}</strong>님,</p>
                    <p>신고/이의제기에 답변이 등록되었습니다.</p>
                    
                    <div class="info-box">
                        <h3>답변 정보</h3>
                        <p><strong>신고 ID:</strong> #{{ dispute.id }}</p>
                        <p><strong>상태:</strong> {{ dispute.status }}</p>
                        <p><strong>답변:</strong> {{ dispute.admin_reply[:200] }}{% if dispute.admin_reply|length > 200 %}...{% endif %}</p>
                        <p><strong>답변일시:</strong> {{ dispute.updated_at.strftime('%Y년 %m월 %d일 %H:%M') }}</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{{ url_for('attendance.attendance_history', _external=True) }}" class="btn">출결 기록 확인</a>
                    </p>
                </div>
                <div class="footer">
                    <p>이 이메일은 레스토랑 관리 시스템에서 자동으로 발송되었습니다.</p>
                </div>
            </div>
        </body>
        </html>
        """,
            dispute=dispute,
            user=user,
        )

    def _get_sla_warning_template(self, dispute, assignee):
        """SLA 임박 경고 템플릿"""
        return render_template_string(
            """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #ffc107; color: #212529; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f8f9fa; }
                .warning-box { background: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ffc107; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                .btn { display: inline-block; padding: 10px 20px; background: #ffc107; color: #212529; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>⚠️ SLA 임박 경고</h2>
                </div>
                <div class="content">
                    <p><strong>{{ assignee.name or assignee.username }}</strong>님,</p>
                    <p>담당 신고/이의제기의 SLA 기한이 임박했습니다.</p>
                    
                    <div class="warning-box">
                        <h3>⚠️ 긴급 처리 필요</h3>
                        <p><strong>신고 ID:</strong> #{{ dispute.id }}</p>
                        <p><strong>신고자:</strong> {{ dispute.user.name or dispute.user.username }}</p>
                        <p><strong>SLA 기한:</strong> {{ dispute.sla_due.strftime('%Y년 %m월 %d일 %H:%M') }}</p>
                        <p><strong>남은 시간:</strong> 24시간 미만</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{{ url_for('my_reports.my_reports', _external=True) }}" class="btn">즉시 처리하기</a>
                    </p>
                </div>
                <div class="footer">
                    <p>이 이메일은 레스토랑 관리 시스템에서 자동으로 발송되었습니다.</p>
                </div>
            </div>
        </body>
        </html>
        """,
            dispute=dispute,
            assignee=assignee,
        )

    def _get_sla_overdue_template(self, dispute, assignee):
        """SLA 초과 경고 템플릿"""
        overdue_days = (
            (datetime.utcnow() - dispute.sla_due).days if dispute.sla_due else 0
        )

        return render_template_string(
            """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #dc3545; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f8f9fa; }
                .danger-box { background: #f8d7da; padding: 15px; margin: 10px 0; border-left: 4px solid #dc3545; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                .btn { display: inline-block; padding: 10px 20px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚨 SLA 초과 경고</h2>
                </div>
                <div class="content">
                    <p><strong>{{ assignee.name or assignee.username }}</strong>님,</p>
                    <p>담당 신고/이의제기의 SLA 기한이 초과되었습니다.</p>
                    
                    <div class="danger-box">
                        <h3>🚨 즉시 처리 필요</h3>
                        <p><strong>신고 ID:</strong> #{{ dispute.id }}</p>
                        <p><strong>신고자:</strong> {{ dispute.user.name or dispute.user.username }}</p>
                        <p><strong>SLA 기한:</strong> {{ dispute.sla_due.strftime('%Y년 %m월 %d일 %H:%M') }}</p>
                        <p><strong>초과일수:</strong> {{ overdue_days }}일</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{{ url_for('my_reports.my_reports', _external=True) }}" class="btn">즉시 처리하기</a>
                    </p>
                </div>
                <div class="footer">
                    <p>이 이메일은 레스토랑 관리 시스템에서 자동으로 발송되었습니다.</p>
                </div>
            </div>
        </body>
        </html>
        """,
            dispute=dispute,
            assignee=assignee,
            overdue_days=overdue_days,
        )


# 전역 인스턴스
email_service = EmailService()
