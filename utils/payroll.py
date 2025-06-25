"""
급여 계산 유틸리티
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import time, datetime

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

def generate_payroll_pdf(filename, user, month, year, work_days, total_hours, wage):
    """급여명세서 PDF 생성"""
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목 스타일
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # 제목
    title = Paragraph(f"{year}년 {month}월 급여 명세서", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # 기본 정보
    info_data = [
        ['사원명', user.name or user.username],
        ['사원번호', str(user.id)],
        ['근무일수', f"{work_days}일"],
        ['총 근무시간', f"{total_hours}시간"],
        ['시급', "12,000원"],
        ['지급액', f"{wage:,}원"]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # 급여 상세 내역
    detail_data = [
        ['구분', '시간', '단가', '금액'],
        ['기본급', f"{total_hours}시간", "12,000원", f"{wage:,}원"],
        ['수당', '-', '-', '0원'],
        ['공제', '-', '-', '0원'],
        ['', '', '합계', f"{wage:,}원"]
    ]
    
    detail_table = Table(detail_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12)
    ]))
    
    story.append(detail_table)
    story.append(Spacer(1, 30))
    
    # 발행일
    issue_date = Paragraph(f"발행일: {datetime.now().strftime('%Y년 %m월 %d일')}", styles['Normal'])
    story.append(issue_date)
    
    # PDF 생성
    doc.build(story)
    
    print(f"급여명세서 PDF 생성 완료: {filename}")

def generate_simple_payroll_pdf(filename, user, month, year, work_days, total_hours, wage):
    """간단한 급여명세서 PDF 생성 (기존 호환성)"""
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"{year}년 {month}월 급여 명세서")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"사원명: {user.name or user.username}")
    c.drawString(100, 750, f"근무일수: {work_days}일")
    c.drawString(100, 730, f"총 근무시간: {total_hours}시간")
    c.drawString(100, 710, f"지급액: {wage:,}원")
    c.save()
    print(f"간단 급여명세서 PDF 생성 완료: {filename}")

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