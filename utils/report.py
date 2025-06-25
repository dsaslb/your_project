from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime, date
import os

def generate_attendance_report_pdf(filename, user, month, year, lateness, early_leave, night_work):
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"{year}년 {month}월 근태 리포트")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"사원명: {user.name or user.username}")
    c.drawString(100, 750, f"지각: {lateness}회")
    c.drawString(100, 730, f"조퇴: {early_leave}회")
    c.drawString(100, 710, f"야근: {night_work}회")
    c.save()

def generate_monthly_summary_pdf(filename, users_data, month, year):
    """월별 전체 직원 근태 요약 PDF"""
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(f"{year}년 {month}월 전체 직원 근태 요약", title_style))
    story.append(Spacer(1, 20))
    
    # 요약 테이블
    summary_data = [['사원명', '지각', '조퇴', '야근', '총 근무시간', '평가']]
    
    for user_data in users_data:
        user = user_data['user']
        lateness = user_data['lateness']
        early_leave = user_data['early_leave']
        night_work = user_data['night_work']
        total_hours = user_data['total_hours']
        
        # 평가 결정
        total_issues = lateness + early_leave
        if total_issues == 0:
            evaluation = "우수"
        elif total_issues <= 2:
            evaluation = "양호"
        elif total_issues <= 5:
            evaluation = "보통"
        else:
            evaluation = "주의"
        
        summary_data.append([
            user.name or user.username,
            str(lateness),
            str(early_leave),
            str(night_work),
            f"{total_hours:.1f}시간",
            evaluation
        ])
    
    summary_table = Table(summary_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.2*inch, 0.8*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(summary_table)
    
    # 통계 요약
    story.append(Spacer(1, 20))
    total_lateness = sum(u['lateness'] for u in users_data)
    total_early_leave = sum(u['early_leave'] for u in users_data)
    total_night_work = sum(u['night_work'] for u in users_data)
    
    stats_text = f"""
    <b>전체 통계:</b><br/>
    • 총 직원 수: {len(users_data)}명<br/>
    • 총 지각: {total_lateness}회<br/>
    • 총 조퇴: {total_early_leave}회<br/>
    • 총 야근: {total_night_work}회<br/>
    • 평균 근무시간: {sum(u['total_hours'] for u in users_data) / len(users_data):.1f}시간
    """
    
    story.append(Paragraph(stats_text, styles['Normal']))
    
    doc.build(story)
    return filename 