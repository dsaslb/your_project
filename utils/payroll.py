from models_main import User, Payroll
from reportlab.lib import colors  # pyright: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle  # pyright: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # pyright: ignore
from reportlab.lib.pagesizes import A4  # pyright: ignore
from datetime import time
import logging
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
급여 관리 시스템
"""


logger = logging.getLogger(__name__)


def calc_wage(user,  work_time_hour, wage_table=None):
    """
    사용자별 급여 계산

    Args:
        user: User 객체
        work_time_hour: 근무 시간 (시간 단위)
        wage_table: 사용자별 시급 테이블 (dict {user_id: 시급})

    Returns:
        int: 계산된 급여 (원)
    """
    # 기본 시급
    wage_per_hour = 12000

    # 사용자별 급여 정책 적용
    if wage_table is not None and user.id in wage_table:
        wage_per_hour = wage_table[user.id]

    # 월급제/시급제/주급제 분기 가능
    # 현재는 시급제로 계산
    return int(work_time_hour * wage_per_hour)


def calc_overtime_pay(work_time_hour, base_wage_per_hour=12000):
    """
    초과근무 수당 계산

    Args:
        work_time_hour: 근무 시간 (시간 단위)
        base_wage_per_hour: 기본 시급

    Returns:
        tuple: (기본급여, 초과수당, 총급여)
    """
    standard_hours = 8  # 기준 근무시간
    overtime_rate = 1.5  # 초과수당 배율

    if work_time_hour <= standard_hours:
        base_pay = work_time_hour * base_wage_per_hour
        overtime_pay = 0
    else:
        base_pay = standard_hours * base_wage_per_hour
        overtime_hours = work_time_hour - standard_hours
        overtime_pay = overtime_hours * base_wage_per_hour * overtime_rate

    total_pay = base_pay + overtime_pay
    return int(base_pay), int(overtime_pay), int(total_pay)


def format_work_time(total_minutes):
    """
    근무시간을 시간:분 형식으로 포맷팅

    Args:
        total_minutes: 총 근무시간 (분)

    Returns:
        str: "X시간 Y분" 형식
    """
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}시간 {minutes}분"


def get_monthly_stats(user_id,  year,  month,  db_session):
    """
    사용자의 월별 근무 통계 조회

    Args:
        user_id: 사용자 ID
        year: 년도
        month: 월
        db_session: 데이터베이스 세션

    Returns:
        dict: 월별 통계 정보
    """
    from sqlalchemy import extract

    from models_main import Attendance

    # 해당 월의 출퇴근 기록 조회
    attendances = (
        db_session.query(Attendance)
        .filter(
            Attendance.user_id == user_id,
            extract("year", Attendance.clock_in) == year,
            extract("month", Attendance.clock_in) == month,
        )
        .all()
    )

    total_days = len(attendances)
    total_minutes = sum(att.work_minutes for att in attendances)
    total_hours = total_minutes / 60

    # 지각/조퇴/결근 통계
    late_count = sum(1 for att in attendances if "지각" in att.status)
    early_leave_count = sum(1 for att in attendances if "조퇴" in att.status)
    absent_count = sum(1 for att in attendances if att.status == "결근")

    return {
        "total_days": total_days,
        "total_hours": total_hours,
        "total_minutes": total_minutes,
        "late_count": late_count,
        "early_leave_count": early_leave_count,
        "absent_count": absent_count,
        "work_time_formatted": format_work_time(total_minutes),
    }


def generate_payroll_pdf(user_id,  year,  month, filename=None):
    """급여명세서 PDF 생성"""
    try:
        if not filename:
            filename = f"payroll_{user_id}_{year}_{month}.pdf"

        # 사용자 정보 조회
        user = None
        if query:
            user = User.query.get(user_id)
        if not user:
            return None

        # 급여 정보 조회
        payroll = Payroll.query.filter_by(
            user_id=user_id, year=year, month=month
        ).first()

        if not payroll:
            return None

        # PDF 생성
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []

        # 스타일 정의
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"] if styles is not None else None,
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # 중앙 정렬
        )

        # 제목
        title = Paragraph(f"{year}년 {month}월 급여명세서", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # 기본 정보 테이블
        basic_data = [
            ["성명", user.name or user.username],
            ["사번", str(user.id)],
            ["부서", getattr(user, "department", "-")],
            ["급여 지급일", f"{year}년 {month}월 말일"],
        ]

        basic_table = Table(basic_data, colWidths=[100, 300])
        basic_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 0), (0, -1), colors.grey),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )
        story.append(basic_table)
        story.append(Spacer(1, 20))

        # 급여 상세 테이블
        salary_data = [
            ["구분", "금액", "비고"],
            ["기본급", f"{payroll.base_salary:,}원", ""],
            ["수당", f"{payroll.allowance:,}원", ""],
            ["공제", f"{payroll.deduction:,}원", ""],
            ["실수령액", f"{payroll.net_salary:,}원", ""],
        ]

        salary_table = Table(salary_data, colWidths=[100, 200, 100])
        salary_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )
        story.append(salary_table)

        # PDF 생성
        doc.build(story)

        logger.info(f"급여명세서 PDF 생성 완료: {filename}")
        return filename

    except Exception as e:
        logger.error(f"급여명세서 PDF 생성 실패: {e}")
        return None


def generate_simple_payroll_pdf(user_id,  year,  month, filename=None):
    """간단 급여명세서 PDF 생성"""
    try:
        if not filename:
            filename = f"simple_payroll_{user_id}_{year}_{month}.pdf"

        # 사용자 정보 조회
        user = None
        if query:
            user = User.query.get(user_id)
        if not user:
            return None

        # 급여 정보 조회
        payroll = Payroll.query.filter_by(
            user_id=user_id, year=year, month=month
        ).first()

        if not payroll:
            return None

        # PDF 생성
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []

        # 스타일 정의
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"] if styles is not None else None,
            fontSize=16,
            spaceAfter=30,
            alignment=1,
        )

        # 제목
        title = Paragraph(f"{year}년 {month}월 급여명세서", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # 간단 정보
        info_text = f"""
        성명: {user.name or user.username}
        사번: {user.id}
        실수령액: {payroll.net_salary:,}원
        지급일: {year}년 {month}월 말일
        """
        info_para = Paragraph(info_text, styles["Normal"] if styles is not None else None)
        story.append(info_para)

        # PDF 생성
        doc.build(story)

        logger.info(f"간단 급여명세서 PDF 생성 완료: {filename}")
        return filename

    except Exception as e:
        logger.error(f"간단 급여명세서 PDF 생성 실패: {e}")
        return None


def analyze_attendance(attendance):
    """
    출퇴근 기록 분석 (지각/조퇴/야근 판정)

    Args:
        attendance: Attendance 객체

    Returns:
        tuple: (지각여부, 조퇴여부, 야근여부)
    """
    STANDARD_CLOCKIN = time(9, 0, 0)  # 오전 9시
    STANDARD_CLOCKOUT = time(18, 0, 0)  # 오후 6시
    NIGHT_WORK_START = time(21, 0, 0)  # 야근 시작 시간

    clock_in_late = False
    clock_out_early = False
    night_work = False

    if attendance.clock_in:
        if attendance.clock_in.time() > STANDARD_CLOCKIN:
            clock_in_late = True

    if attendance.clock_out:
        if attendance.clock_out.time() < STANDARD_CLOCKOUT:
            clock_out_early = True
        if attendance.clock_out.time() > NIGHT_WORK_START:
            night_work = True

    return clock_in_late, clock_out_early, night_work
