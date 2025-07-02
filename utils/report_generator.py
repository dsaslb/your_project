import io
import logging
import os
import smtplib
from datetime import date, datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import render_template
from sqlalchemy import and_, extract, func

from models import Attendance, AttendanceReport, User, db
from utils.logger import log_action

logger = logging.getLogger(__name__)


def generate_attendance_report_pdf(period="week", user_id=None, admin_view=True):
    """근태 리포트 PDF 생성"""
    try:
        # 기간 설정
        if period == "week":
            from_date = date.today() - timedelta(days=7)
        elif period == "month":
            from_date = date.today().replace(day=1)
        else:  # custom
            from_date = date.today() - timedelta(days=30)

        to_date = date.today()

        # 데이터 조회
        if user_id:
            # 개별 사용자 리포트
            records = (
                Attendance.query.filter(
                    and_(
                        Attendance.user_id == user_id,
                        Attendance.clock_in >= from_date,
                        Attendance.clock_in <= to_date,
                    )
                )
                .order_by(Attendance.clock_in.desc())
                .all()
            )

            user = User.query.get(user_id)
            title = f"{user.name or user.username}님의 {period} 근태 리포트"
        else:
            # 전체 사용자 리포트 (관리자용)
            records = (
                Attendance.query.filter(
                    and_(
                        Attendance.clock_in >= from_date, Attendance.clock_in <= to_date
                    )
                )
                .order_by(Attendance.clock_in.desc())
                .all()
            )

            title = f"전체 직원 {period} 근태 리포트"

        # 통계 계산
        stats = calculate_attendance_stats(records, from_date, to_date)

        # HTML 템플릿 렌더링
        html = render_template(
            "reports/attendance_report_pdf.html",
            records=records,
            stats=stats,
            from_date=from_date,
            to_date=to_date,
            title=title,
            admin_view=admin_view,
        )

        # PDF 생성 (pdfkit 사용)
        try:
            import pdfkit

            options = {
                "page-size": "A4",
                "margin-top": "0.75in",
                "margin-right": "0.75in",
                "margin-bottom": "0.75in",
                "margin-left": "0.75in",
                "encoding": "UTF-8",
                "no-outline": None,
            }

            pdf = pdfkit.from_string(html, False, options=options)

            # 파일 저장
            filename = f"attendance_report_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join("static", "reports", filename)

            # 디렉토리 생성
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, "wb") as f:
                f.write(pdf)

            return filepath

        except ImportError:
            # pdfkit이 없는 경우 HTML 파일로 저장
            logger.warning("pdfkit not available, saving as HTML")
            filename = f"attendance_report_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join("static", "reports", filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

            return filepath

    except Exception as e:
        logger.error(f"PDF 생성 중 오류: {str(e)}")
        return None


def calculate_attendance_stats(records, from_date, to_date):
    """근태 통계 계산"""
    stats = {
        "total_days": len(records),
        "total_hours": 0,
        "late_count": 0,
        "early_leave_count": 0,
        "absent_count": 0,
        "overtime_hours": 0,
        "normal_count": 0,
        "users": {},
    }

    for record in records:
        user_id = record.user_id
        if user_id not in stats["users"]:
            stats["users"][user_id] = {
                "name": record.user.name or record.user.username,
                "total_days": 0,
                "total_hours": 0,
                "late_count": 0,
                "early_leave_count": 0,
                "overtime_hours": 0,
            }

        user_stats = stats["users"][user_id]
        user_stats["total_days"] += 1

        if record.clock_in and record.clock_out:
            work_seconds = (record.clock_out - record.clock_in).total_seconds()
            work_hours = work_seconds / 3600
            stats["total_hours"] += work_hours
            user_stats["total_hours"] += work_hours

            # 지각/조퇴/야근 판정
            if record.clock_in.time() > datetime.strptime("09:00", "%H:%M").time():
                stats["late_count"] += 1
                user_stats["late_count"] += 1
            if record.clock_out.time() < datetime.strptime("18:00", "%H:%M").time():
                stats["early_leave_count"] += 1
                user_stats["early_leave_count"] += 1
            if work_hours > 8:
                overtime = work_hours - 8
                stats["overtime_hours"] += overtime
                user_stats["overtime_hours"] += overtime
            else:
                stats["normal_count"] += 1
        else:
            stats["absent_count"] += 1

    # 평균 계산
    if stats["total_days"] > 0:
        stats["avg_hours_per_day"] = round(
            stats["total_hours"] / stats["total_days"], 2
        )
    else:
        stats["avg_hours_per_day"] = 0

    return stats


def send_email(to_email, subject, body, attach_path=None, html_body=None):
    """이메일 발송 함수"""
    try:
        # 환경 변수에서 SMTP 설정 가져오기
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL", "noreply@restaurant.com")

        if not all([smtp_username, smtp_password]):
            logger.warning("SMTP 설정이 없어 테스트 모드로 실행")
            print(
                f"메일 발송 테스트용(to={to_email}, subject={subject}, attach={attach_path})"
            )
            return True

        # 이메일 메시지 생성
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # 본문 추가
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))
        else:
            msg.attach(MIMEText(body, "plain", "utf-8"))

        # 첨부파일 추가
        if attach_path and os.path.exists(attach_path):
            with open(attach_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(attach_path)}",
            )
            msg.attach(part)

        # SMTP 서버 연결 및 발송
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()

        logger.info(f"이메일 발송 성공: {to_email}")
        return True

    except Exception as e:
        logger.error(f"이메일 발송 실패: {str(e)}")
        return False


def send_weekly_attendance_report():
    """주간 근태 리포트 자동 발송"""
    try:
        # 관리자 목록 조회
        admins = User.query.filter_by(role="admin").all()

        if not admins:
            logger.warning("발송할 관리자가 없습니다.")
            return

        # PDF 생성
        pdf_path = generate_attendance_report_pdf(period="week")

        if not pdf_path:
            logger.error("PDF 생성 실패")
            return

        # 이메일 본문
        html_body = """
        <html>
        <body>
            <h2>주간 근태 리포트</h2>
            <p>안녕하세요,</p>
            <p>이번 주 근태 리포트가 첨부되었습니다.</p>
            <p>감사합니다.</p>
        </body>
        </html>
        """

        # 각 관리자에게 발송
        success_count = 0
        for admin in admins:
            if admin.email:
                if send_email(
                    admin.email,
                    "주간 근태 리포트",
                    "이번 주 근태 리포트가 첨부되었습니다.",
                    attach_path=pdf_path,
                    html_body=html_body,
                ):
                    success_count += 1

        logger.info(f"주간 리포트 발송 완료: {success_count}/{len(admins)}")

        # 임시 파일 정리 (선택사항)
        # os.remove(pdf_path)

    except Exception as e:
        logger.error(f"주간 리포트 발송 중 오류: {str(e)}")


def send_monthly_attendance_report():
    """월간 근태 리포트 자동 발송"""
    try:
        # 관리자 목록 조회
        admins = User.query.filter_by(role="admin").all()

        if not admins:
            logger.warning("발송할 관리자가 없습니다.")
            return

        # PDF 생성
        pdf_path = generate_attendance_report_pdf(period="month")

        if not pdf_path:
            logger.error("PDF 생성 실패")
            return

        # 이메일 본문
        html_body = """
        <html>
        <body>
            <h2>월간 근태 리포트</h2>
            <p>안녕하세요,</p>
            <p>이번 달 근태 리포트가 첨부되었습니다.</p>
            <p>감사합니다.</p>
        </body>
        </html>
        """

        # 각 관리자에게 발송
        success_count = 0
        for admin in admins:
            if admin.email:
                if send_email(
                    admin.email,
                    "월간 근태 리포트",
                    "이번 달 근태 리포트가 첨부되었습니다.",
                    attach_path=pdf_path,
                    html_body=html_body,
                ):
                    success_count += 1

        logger.info(f"월간 리포트 발송 완료: {success_count}/{len(admins)}")

    except Exception as e:
        logger.error(f"월간 리포트 발송 중 오류: {str(e)}")


def send_individual_attendance_report(user_id, period="week"):
    """개별 사용자 근태 리포트 발송"""
    try:
        user = User.query.get(user_id)
        if not user or not user.email:
            logger.warning(f"사용자 {user_id}의 이메일이 없습니다.")
            return False

        # PDF 생성
        pdf_path = generate_attendance_report_pdf(
            period=period, user_id=user_id, admin_view=False
        )

        if not pdf_path:
            logger.error("PDF 생성 실패")
            return False

        # 이메일 본문
        html_body = f"""
        <html>
        <body>
            <h2>{period} 근태 리포트</h2>
            <p>{user.name or user.username}님, 안녕하세요.</p>
            <p>귀하의 {period} 근태 리포트가 첨부되었습니다.</p>
            <p>감사합니다.</p>
        </body>
        </html>
        """

        # 발송
        success = send_email(
            user.email,
            f"{period} 근태 리포트",
            f"귀하의 {period} 근태 리포트가 첨부되었습니다.",
            attach_path=pdf_path,
            html_body=html_body,
        )

        if success:
            logger.info(f"개별 리포트 발송 성공: {user.email}")

        return success

    except Exception as e:
        logger.error(f"개별 리포트 발송 중 오류: {str(e)}")
        return False


def generate_attendance_report(start_date, end_date, user_id=None):
    """근태 리포트 생성"""
    try:
        # 근태 데이터 조회
        query = db.session.query(Attendance).filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        )
        
        if user_id:
            query = query.filter(Attendance.user_id == user_id)
        
        attendances = query.all()
        
        # 리포트 데이터 구성
        report_data = {
            "period": f"{start_date} ~ {end_date}",
            "total_records": len(attendances),
            "generated_at": datetime.now().isoformat(),
            "data": []
        }
        
        for attendance in attendances:
            report_data["data"].append({
                "user_id": attendance.user_id,
                "date": attendance.date.isoformat(),
                "status": attendance.status,
                "clock_in": attendance.clock_in.isoformat() if attendance.clock_in else None,
                "clock_out": attendance.clock_out.isoformat() if attendance.clock_out else None
            })
        
        logger.info(f"근태 리포트 생성 완료: {len(attendances)}건")
        return report_data
        
    except Exception as e:
        logger.error(f"근태 리포트 생성 실패: {e}")
        return None
