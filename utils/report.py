from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime, date
import os

def generate_attendance_report_pdf(filename, user, month, year, lateness, early_leave, night_work, attendances=None):
    """근태 리포트 PDF 생성"""
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목 스타일
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    # 제목
    title = Paragraph(f"{year}년 {month}월 근태 리포트", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # 기본 정보
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )
    
    story.append(Paragraph(f"<b>사원명:</b> {user.name or user.username}", info_style))
    story.append(Paragraph(f"<b>사원번호:</b> {user.id}", info_style))
    story.append(Paragraph(f"<b>부서:</b> {user.branch.name if user.branch else '미지정'}", info_style))
    story.append(Paragraph(f"<b>생성일:</b> {datetime.now().strftime('%Y년 %m월 %d일')}", info_style))
    story.append(Spacer(1, 20))
    
    # 근태 통계
    stats_data = [
        ['구분', '횟수', '비고'],
        ['지각', str(lateness), f'{lateness}회 발생'],
        ['조퇴', str(early_leave), f'{early_leave}회 발생'],
        ['야근', str(night_work), f'{night_work}회 발생'],
        ['정상출근', str(max(0, len(attendances) - lateness - early_leave)), '정시 출근'],
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 1*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # 상세 출근 기록 (있는 경우)
    if attendances:
        story.append(Paragraph("<b>상세 출근 기록</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # 출근 기록 테이블 헤더
        detail_data = [['날짜', '출근시간', '퇴근시간', '근무시간', '상태']]
        
        for att in attendances:
            if att.clock_in and att.clock_out:
                work_hours = att.work_hours
                status = att.status
                detail_data.append([
                    att.clock_in.strftime('%m/%d'),
                    att.clock_in.strftime('%H:%M'),
                    att.clock_out.strftime('%H:%M'),
                    f'{work_hours:.1f}시간',
                    status
                ])
        
        if len(detail_data) > 1:  # 헤더 외에 데이터가 있는 경우
            detail_table = Table(detail_data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 1*inch, 1.5*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(detail_table)
    
    # 요약 및 코멘트
    story.append(Spacer(1, 20))
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        textColor=colors.darkred
    )
    
    total_issues = lateness + early_leave
    if total_issues > 0:
        story.append(Paragraph(f"<b>주의사항:</b> 이번 달 {total_issues}회의 근태 이상이 발생했습니다.", summary_style))
    else:
        story.append(Paragraph("<b>평가:</b> 이번 달 근태가 양호합니다.", summary_style))
    
    # PDF 생성
    doc.build(story)
    return filename

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