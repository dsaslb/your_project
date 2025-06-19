"""
급여 계산 유틸리티
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import time

def calc_wage(user, work_time_hour, wage_table=None):
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
    if wage_table and user.id in wage_table:
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

def get_monthly_stats(user_id, year, month, db_session):
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
    from sqlalchemy import extract, func
    from models import Attendance
    
    # 해당 월의 출퇴근 기록 조회
    attendances = db_session.query(Attendance).filter(
        Attendance.user_id == user_id,
        extract('year', Attendance.clock_in) == year,
        extract('month', Attendance.clock_in) == month
    ).all()
    
    total_days = len(attendances)
    total_minutes = sum(att.work_minutes for att in attendances)
    total_hours = total_minutes / 60
    
    # 지각/조퇴/결근 통계
    late_count = sum(1 for att in attendances if "지각" in att.status)
    early_leave_count = sum(1 for att in attendances if "조퇴" in att.status)
    absent_count = sum(1 for att in attendances if att.status == "결근")
    
    return {
        'total_days': total_days,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
        'late_count': late_count,
        'early_leave_count': early_leave_count,
        'absent_count': absent_count,
        'work_time_formatted': format_work_time(total_minutes)
    }

def generate_payroll_pdf(filename, user, month, year, work_days, total_hours, wage, 
                        late_count=0, early_leave_count=0, overtime_hours=0):
    """
    급여 명세서 PDF 생성
    
    Args:
        filename: PDF 파일 경로
        user: User 객체
        month: 월
        year: 년도
        work_days: 근무일수
        total_hours: 총 근무시간
        wage: 급여
        late_count: 지각 횟수
        early_leave_count: 조퇴 횟수
        overtime_hours: 초과근무 시간
    """
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # 중앙 정렬
    )
    title = Paragraph(f"{year}년 {month}월 급여 명세서", title_style)
    story.append(title)
    
    # 기본 정보 테이블
    basic_data = [
        ['사원명', user.name or user.username],
        ['사원번호', str(user.id)],
        ['부서', user.branch.name if user.branch else '미지정'],
        ['급여 지급일', f"{year}년 {month}월 말일"]
    ]
    
    basic_table = Table(basic_data, colWidths=[2*inch, 4*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(basic_table)
    story.append(Paragraph("<br/><br/>", styles['Normal']))
    
    # 근무 실적
    work_data = [
        ['구분', '내역', '비고'],
        ['근무일수', f"{work_days}일", ''],
        ['총 근무시간', f"{total_hours:.1f}시간", ''],
        ['지각', f"{late_count}회", ''],
        ['조퇴', f"{early_leave_count}회", ''],
        ['초과근무', f"{overtime_hours:.1f}시간", '']
    ]
    
    work_table = Table(work_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
    work_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(work_table)
    story.append(Paragraph("<br/><br/>", styles['Normal']))
    
    # 급여 내역
    base_pay, overtime_pay, total_pay = calc_overtime_pay(total_hours)
    
    salary_data = [
        ['구분', '금액', '비고'],
        ['기본급', f"{base_pay:,}원", f"시급 12,000원 × {total_hours:.1f}시간"],
        ['초과수당', f"{overtime_pay:,}원", f"초과근무 {overtime_hours:.1f}시간"],
        ['', '', ''],
        ['총 지급액', f"{total_pay:,}원", '']
    ]
    
    salary_table = Table(salary_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
    salary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue)
    ]))
    story.append(salary_table)
    
    # 하단 안내문
    story.append(Paragraph("<br/><br/>", styles['Normal']))
    notice = Paragraph(
        "※ 본 명세서는 자동 생성된 문서입니다.<br/>"
        "※ 문의사항이 있으시면 관리자에게 연락하시기 바랍니다.<br/>"
        "※ 급여 지급일은 매월 말일입니다.",
        styles['Normal']
    )
    story.append(notice)
    
    doc.build(story)

def analyze_attendance(attendance):
    """
    출퇴근 기록 분석 (지각/조퇴/야근 판정)
    
    Args:
        attendance: Attendance 객체
    
    Returns:
        tuple: (지각여부, 조퇴여부, 야근여부)
    """
    STANDARD_CLOCKIN = time(9, 0, 0)   # 오전 9시
    STANDARD_CLOCKOUT = time(18, 0, 0) # 오후 6시
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