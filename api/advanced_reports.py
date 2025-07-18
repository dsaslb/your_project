from sqlalchemy import func, and_, or_
import tempfile
import os
from api.gateway import token_required, role_required, admin_required, manager_required, employee_required, log_request  # pyright: ignore
from reportlab.lib.units import inch  # pyright: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # pyright: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # pyright: ignore
from reportlab.lib.pagesizes import letter, A4  # pyright: ignore
from reportlab.lib import colors  # pyright: ignore
import xlsxwriter
import csv
import io
import json
from datetime import datetime, timedelta
import logging
from extensions import db
from models_main import User, Order, Attendance, Schedule, InventoryItem, Notification, db
from functools import wraps
from flask import Blueprint, request, jsonify, g, send_file
query = None  # pyright: ignore
form = None  # pyright: ignore

# 로깅 설정
logger = logging.getLogger(__name__)

# 고급 보고서 API Blueprint
advanced_reports = Blueprint('advanced_reports', __name__, url_prefix='/api/advanced-reports')

# 보고서 템플릿 설정
REPORT_TEMPLATES = {
    'sales_summary': {
        'name': '매출 요약 보고서',
        'description': '일별/월별 매출 현황 및 분석',
        'sections': ['매출 개요', '상품별 매출', '시간대별 매출', '트렌드 분석']
    },
    'staff_performance': {
        'name': '직원 성과 보고서',
        'description': '직원별 근무 시간, 출근률, 성과 분석',
        'sections': ['근무 현황', '출근률 분석', '성과 지표', '개선 제안']
    },
    'inventory_analysis': {
        'name': '재고 분석 보고서',
        'description': '재고 현황, 소비 패턴, 발주 최적화',
        'sections': ['재고 현황', '소비 패턴', '발주 분석', '최적화 제안']
    },
    'operational_efficiency': {
        'name': '운영 효율성 보고서',
        'description': '전체 운영 효율성 및 개선점 분석',
        'sections': ['운영 지표', '효율성 분석', '병목 지점', '개선 방안']
    }
}


def generate_pdf_report(report_data,  report_type):
    """PDF 보고서 생성"""
    try:
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            doc = SimpleDocTemplate(tmp_file.name, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()

            # 제목 스타일
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'] if styles is not None else None,
                fontSize=18,
                spaceAfter=30,
                alignment=1  # 중앙 정렬
            )

            # 헤더 스타일
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'] if styles is not None else None,
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20
            )

            # 보고서 제목
            title = Paragraph(f"{REPORT_TEMPLATES[report_type] if REPORT_TEMPLATES is not None else None['name']}", title_style)
            story.append(title)

            # 생성 날짜
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'] if styles is not None else None,
                fontSize=10,
                alignment=1,
                spaceAfter=20
            )
            date_text = Paragraph(f"생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}", date_style)
            story.append(date_text)
            story.append(Spacer(1, 20))

            # 보고서 내용 추가
            if report_type == 'sales_summary':
                story.extend(generate_sales_pdf_content(report_data, styles, header_style))
            elif report_type == 'staff_performance':
                story.extend(generate_staff_pdf_content(report_data, styles, header_style))
            elif report_type == 'inventory_analysis':
                story.extend(generate_inventory_pdf_content(report_data, styles, header_style))
            elif report_type == 'operational_efficiency':
                story.extend(generate_operational_pdf_content(report_data, styles, header_style))

            # PDF 생성
            doc.build(story)
            return tmp_file.name

    except Exception as e:
        logger.error(f"PDF 생성 오류: {str(e)}")
        raise


def generate_sales_pdf_content(data,  styles,  header_style):
    """매출 보고서 PDF 내용 생성"""
    story = []

    # 매출 개요
    story.append(Paragraph("매출 개요", header_style))

    summary_data = [
        ['지표', '값', '전월 대비'],
        ['총 매출', f"{data['total_sales'] if data is not None else None:,}원", f"{data['sales_growth'] if data is not None else None:+.1f}%"],
        ['주문 수', f"{data['total_orders'] if data is not None else None:,}건", f"{data['order_growth'] if data is not None else None:+.1f}%"],
        ['평균 주문 금액', f"{data['avg_order_value'] if data is not None else None:,}원", f"{data['avg_order_growth'] if data is not None else None:+.1f}%"],
        ['고객 수', f"{data['total_customers'] if data is not None else None:,}명", f"{data['customer_growth'] if data is not None else None:+.1f}%"]
    ]

    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # 일별 매출 차트 (텍스트로 표현)
    story.append(Paragraph("일별 매출 현황", header_style))
    daily_sales_text = ""
    for day_data in data['daily_sales'] if data is not None else None[:7]:  # 최근 7일
        daily_sales_text += f"• {day_data['date'] if day_data is not None else None}: {day_data['sales'] if day_data is not None else None:,}원 ({day_data['orders'] if day_data is not None else None}건)\n"

    story.append(Paragraph(daily_sales_text, styles['Normal'] if styles is not None else None))
    story.append(Spacer(1, 20))

    return story


def generate_staff_pdf_content(data,  styles,  header_style):
    """직원 성과 보고서 PDF 내용 생성"""
    story = []

    # 근무 현황
    story.append(Paragraph("근무 현황", header_style))

    staff_data = [['직원명', '근무일수', '총 근무시간', '출근률', '평균 근무시간']]
    for staff in data['staff_performance'] if data is not None else None:
        staff_data.append([
            staff['name'] if staff is not None else None,
            f"{staff['work_days'] if staff is not None else None}일",
            f"{staff['total_hours'] if staff is not None else None:.1f}시간",
            f"{staff['attendance_rate'] if staff is not None else None:.1f}%",
            f"{staff['avg_hours'] if staff is not None else None:.1f}시간"
        ])

    staff_table = Table(staff_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1*inch, 1.3*inch])
    staff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(staff_table)
    story.append(Spacer(1, 20))

    return story


def generate_inventory_pdf_content(data,  styles,  header_style):
    """재고 분석 보고서 PDF 내용 생성"""
    story = []

    # 재고 현황
    story.append(Paragraph("재고 현황", header_style))

    inventory_data = [['품목명', '현재 재고', '최소 재고', '상태', '소진 예상일']]
    for item in data['inventory_status'] if data is not None else None:
        status = "정상" if item['current_stock'] if item is not None else None > item['min_stock'] if item is not None else None else "부족"
        inventory_data.append([
            item['name'] if item is not None else None,
            f"{item['current_stock'] if item is not None else None}개",
            f"{item['min_stock'] if item is not None else None}개",
            status,
            f"{item['days_until_stockout'] if item is not None else None:.1f}일" if item['days_until_stockout'] if item is not None else None > 0 else "N/A"
        ])

    inventory_table = Table(inventory_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    inventory_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(inventory_table)
    story.append(Spacer(1, 20))

    return story


def generate_operational_pdf_content(data,  styles,  header_style):
    """운영 효율성 보고서 PDF 내용 생성"""
    story = []

    # 운영 지표
    story.append(Paragraph("운영 지표", header_style))

    operational_data = [
        ['지표', '현재값', '목표값', '달성률'],
        ['주문 처리 시간', f"{data['avg_order_time'] if data is not None else None:.1f}분", "15분", f"{data['order_time_achievement'] if data is not None else None:.1f}%"],
        ['고객 만족도', f"{data['customer_satisfaction'] if data is not None else None:.1f}점", "4.5점", f"{data['satisfaction_achievement'] if data is not None else None:.1f}%"],
        ['재고 회전율', f"{data['inventory_turnover'] if data is not None else None:.1f}회", "12회", f"{data['turnover_achievement'] if data is not None else None:.1f}%"],
        ['직원 생산성', f"{data['employee_productivity'] if data is not None else None:.1f}%", "85%", f"{data['productivity_achievement'] if data is not None else None:.1f}%"]
    ]

    operational_table = Table(operational_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    operational_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(operational_table)
    story.append(Spacer(1, 20))

    return story


def generate_excel_report(report_data,  report_type):
    """Excel 보고서 생성"""
    try:
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            workbook = xlsxwriter.Workbook(tmp_file.name)

            # 스타일 정의
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })

            data_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })

            number_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '#,##0'
            })

            currency_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '₩#,##0'
            })

            # 보고서 타입별 워크시트 생성
            if report_type == 'sales_summary':
                create_sales_excel_worksheet(workbook,  report_data,  header_format,  data_format,  number_format,  currency_format)
            elif report_type == 'staff_performance':
                create_staff_excel_worksheet(workbook,  report_data,  header_format,  data_format,  number_format)
            elif report_type == 'inventory_analysis':
                create_inventory_excel_worksheet(workbook,  report_data,  header_format,  data_format,  number_format)
            elif report_type == 'operational_efficiency':
                create_operational_excel_worksheet(workbook,  report_data,  header_format,  data_format,  number_format)

            workbook.close()
            return tmp_file.name

    except Exception as e:
        logger.error(f"Excel 생성 오류: {str(e)}")
        raise


def create_sales_excel_worksheet(workbook,  data,  header_format,  data_format,  number_format,  currency_format):
    """매출 보고서 Excel 워크시트 생성"""
    worksheet = workbook.add_worksheet('매출 요약')

    # 제목
    worksheet.merge_range('A1:E1', f"{REPORT_TEMPLATES['sales_summary'] if REPORT_TEMPLATES is not None else None['name']}", header_format)
    worksheet.write('A2', f"생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}", data_format)

    # 매출 개요
    worksheet.write('A4', '매출 개요', header_format)
    worksheet.write('A5', '지표', header_format)
    worksheet.write('B5', '값', header_format)
    worksheet.write('C5', '전월 대비', header_format)

    summary_data = [
        ['총 매출', data['total_sales'] if data is not None else None, f"{data['sales_growth'] if data is not None else None:+.1f}%"],
        ['주문 수', data['total_orders'] if data is not None else None, f"{data['order_growth'] if data is not None else None:+.1f}%"],
        ['평균 주문 금액', data['avg_order_value'] if data is not None else None, f"{data['avg_order_growth'] if data is not None else None:+.1f}%"],
        ['고객 수', data['total_customers'] if data is not None else None, f"{data['customer_growth'] if data is not None else None:+.1f}%"]
    ]

    for i, (label, value, growth) in enumerate(summary_data):
        row = 6 + i
        worksheet.write(f'A{row}', label, data_format)
        if '매출' in label or '금액' in label:
            worksheet.write(f'B{row}', value, currency_format)
        else:
            worksheet.write(f'B{row}', value, number_format)
        worksheet.write(f'C{row}', growth, data_format)

    # 일별 매출
    worksheet.write('A12', '일별 매출 현황', header_format)
    worksheet.write('A13', '날짜', header_format)
    worksheet.write('B13', '매출', header_format)
    worksheet.write('C13', '주문 수', header_format)

    for i, day_data in enumerate(data['daily_sales'] if data is not None else None[:7]):
        row = 14 + i
        worksheet.write(f'A{row}', day_data['date'] if day_data is not None else None, data_format)
        worksheet.write(f'B{row}', day_data['sales'] if day_data is not None else None, currency_format)
        worksheet.write(f'C{row}', day_data['orders'] if day_data is not None else None, number_format)


def create_staff_excel_worksheet(workbook,  data,  header_format,  data_format,  number_format):
    """직원 성과 보고서 Excel 워크시트 생성"""
    worksheet = workbook.add_worksheet('직원 성과')

    # 제목
    worksheet.merge_range('A1:F1', f"{REPORT_TEMPLATES['staff_performance'] if REPORT_TEMPLATES is not None else None['name']}", header_format)
    worksheet.write('A2', f"생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}", data_format)

    # 근무 현황
    worksheet.write('A4', '근무 현황', header_format)
    headers = ['직원명', '근무일수', '총 근무시간', '출근률', '평균 근무시간']
    for i, header in enumerate(headers):
        worksheet.write(4, i, header, header_format)

    for i, staff in enumerate(data['staff_performance'] if data is not None else None):
        row = 5 + i
        worksheet.write(row, 0, staff['name'] if staff is not None else None, data_format)
        worksheet.write(row, 1, staff['work_days'] if staff is not None else None, number_format)
        worksheet.write(row, 2, staff['total_hours'] if staff is not None else None, number_format)
        worksheet.write(row, 3, staff['attendance_rate'] if staff is not None else None, number_format)
        worksheet.write(row, 4, staff['avg_hours'] if staff is not None else None, number_format)


def create_inventory_excel_worksheet(workbook,  data,  header_format,  data_format,  number_format):
    """재고 분석 보고서 Excel 워크시트 생성"""
    worksheet = workbook.add_worksheet('재고 분석')

    # 제목
    worksheet.merge_range('A1:F1', f"{REPORT_TEMPLATES['inventory_analysis'] if REPORT_TEMPLATES is not None else None['name']}", header_format)
    worksheet.write('A2', f"생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}", data_format)

    # 재고 현황
    worksheet.write('A4', '재고 현황', header_format)
    headers = ['품목명', '현재 재고', '최소 재고', '상태', '소진 예상일']
    for i, header in enumerate(headers):
        worksheet.write(4, i, header, header_format)

    for i, item in enumerate(data['inventory_status'] if data is not None else None):
        row = 5 + i
        status = "정상" if item['current_stock'] if item is not None else None > item['min_stock'] if item is not None else None else "부족"
        worksheet.write(row, 0, item['name'] if item is not None else None, data_format)
        worksheet.write(row, 1, item['current_stock'] if item is not None else None, number_format)
        worksheet.write(row, 2, item['min_stock'] if item is not None else None, number_format)
        worksheet.write(row, 3, status, data_format)
        worksheet.write(row, 4, item['days_until_stockout'] if item is not None else None, number_format)


def create_operational_excel_worksheet(workbook,  data,  header_format,  data_format,  number_format):
    """운영 효율성 보고서 Excel 워크시트 생성"""
    worksheet = workbook.add_worksheet('운영 효율성')

    # 제목
    worksheet.merge_range('A1:E1', f"{REPORT_TEMPLATES['operational_efficiency'] if REPORT_TEMPLATES is not None else None['name']}", header_format)
    worksheet.write('A2', f"생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}", data_format)

    # 운영 지표
    worksheet.write('A4', '운영 지표', header_format)
    headers = ['지표', '현재값', '목표값', '달성률']
    for i, header in enumerate(headers):
        worksheet.write(4, i, header, header_format)

    operational_data = [
        ['주문 처리 시간', data['avg_order_time'] if data is not None else None, 15, data['order_time_achievement'] if data is not None else None],
        ['고객 만족도', data['customer_satisfaction'] if data is not None else None, 4.5, data['satisfaction_achievement'] if data is not None else None],
        ['재고 회전율', data['inventory_turnover'] if data is not None else None, 12, data['turnover_achievement'] if data is not None else None],
        ['직원 생산성', data['employee_productivity'] if data is not None else None, 85, data['productivity_achievement'] if data is not None else None]
    ]

    for i, (label, current, target, achievement) in enumerate(operational_data):
        row = 5 + i
        worksheet.write(row, 0, label, data_format)
        worksheet.write(row, 1, current, number_format)
        worksheet.write(row, 2, target, number_format)
        worksheet.write(row, 3, achievement, number_format)


@advanced_reports.route('/templates', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def get_report_templates():
    """보고서 템플릿 목록 조회"""
    try:
        return jsonify({
            'templates': REPORT_TEMPLATES,
            'available_formats': ['pdf', 'excel', 'csv']
        })
    except Exception as e:
        logger.error(f"보고서 템플릿 조회 오류: {str(e)}")
        return jsonify({'error': 'Failed to fetch report templates'}), 500


@advanced_reports.route('/generate/<report_type>', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def generate_report(report_type):
    """보고서 생성"""
    try:
        data = request.get_json() or {}
        format_type = data.get('format', 'pdf')
        date_range = data.get('date_range', 'month')

        # 날짜 범위 계산
        end_date = datetime.now()
        if date_range == 'week':
            start_date = end_date - timedelta(days=7)
        elif date_range == 'month':
            start_date = end_date - timedelta(days=30)
        elif date_range == 'quarter':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)

        # 보고서 데이터 수집
        report_data = collect_report_data(report_type,  start_date,  end_date)

        # 파일 생성
        if format_type == 'pdf':
            file_path = generate_pdf_report(report_data,  report_type)
            mime_type = 'application/pdf'
            file_extension = 'pdf'
        elif format_type == 'excel':
            file_path = generate_excel_report(report_data,  report_type)
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_extension = 'xlsx'
        else:
            return jsonify({'error': 'Unsupported format'}), 400

        # 파일 전송
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{REPORT_TEMPLATES[report_type] if REPORT_TEMPLATES is not None else None['name']}_{datetime.now().strftime('%Y%m%d_%H%M')}.{file_extension}",
            mimetype=mime_type
        )

    except Exception as e:
        logger.error(f"보고서 생성 오류: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500


def collect_report_data(report_type,  start_date,  end_date):
    """보고서 데이터 수집"""
    try:
        if report_type == 'sales_summary':
            return collect_sales_data(start_date,  end_date)
        elif report_type == 'staff_performance':
            return collect_staff_data(start_date,  end_date)
        elif report_type == 'inventory_analysis':
            return collect_inventory_data(start_date,  end_date)
        elif report_type == 'operational_efficiency':
            return collect_operational_data(start_date,  end_date)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    except Exception as e:
        logger.error(f"데이터 수집 오류: {str(e)}")
        raise


def collect_sales_data(start_date,  end_date):
    """매출 데이터 수집"""
    try:
        # 기본 매출 데이터
        orders = Order.query.filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        ).all()

        total_sales = sum(order.total_amount for order in orders)
        total_orders = len(orders)
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0

        # 이전 기간 데이터 (성장률 계산용)
        prev_start = start_date - (end_date - start_date)
        prev_orders = Order.query.filter(
            Order.created_at >= prev_start,
            Order.created_at < start_date
        ).all()

        prev_sales = sum(order.total_amount for order in prev_orders)
        prev_orders_count = len(prev_orders)

        # 성장률 계산
        sales_growth = ((total_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
        order_growth = ((total_orders - prev_orders_count) / prev_orders_count * 100) if prev_orders_count > 0 else 0

        # 일별 매출 데이터
        daily_sales = []
        current_date = start_date
        while current_date <= end_date:
            day_orders = [o for o in orders if o.created_at.date() == current_date.date()]
            daily_sales.append({
                'date': current_date.strftime('%m/%d'),
                'sales': sum(o.total_amount for o in day_orders),
                'orders': len(day_orders)
            })
            current_date += timedelta(days=1)

        return {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'total_customers': len(set(order.customer_name for order in orders)),
            'sales_growth': sales_growth,
            'order_growth': order_growth,
            'avg_order_growth': 0,  # 실제로는 계산 필요
            'customer_growth': 0,   # 실제로는 계산 필요
            'daily_sales': daily_sales
        }

    except Exception as e:
        logger.error(f"매출 데이터 수집 오류: {str(e)}")
        raise


def collect_staff_data(start_date,  end_date):
    """직원 성과 데이터 수집"""
    try:
        staff_performance = []

        # 모든 직원 조회
        employees = User.query.filter_by(role='employee').all()

        for employee in employees if employees is not None:
            # 출근 기록 조회
            attendances = Attendance.query.filter(
                Attendance.user_id == employee.id,
                Attendance.clock_in >= start_date,
                Attendance.clock_in <= end_date
            ).all()

            if not attendances:
                continue

            # 근무 시간 계산
            total_hours = 0
            work_days = len(attendances)

            for attendance in attendances if attendances is not None:
                if attendance.clock_out:
                    duration = attendance.clock_out - attendance.clock_in
                    total_hours += duration.total_seconds() / 3600

            # 출근률 계산 (실제로는 더 복잡한 로직 필요)
            attendance_rate = 100  # 임시값

            staff_performance.append({
                'name': employee.name,
                'work_days': work_days,
                'total_hours': round(total_hours, 1),
                'attendance_rate': attendance_rate,
                'avg_hours': round(total_hours / work_days, 1) if work_days > 0 else 0
            })

        return {
            'staff_performance': staff_performance
        }

    except Exception as e:
        logger.error(f"직원 데이터 수집 오류: {str(e)}")
        raise


def collect_inventory_data(start_date,  end_date):
    """재고 데이터 수집"""
    try:
        inventory_status = []

        # 모든 재고 품목 조회
        items = InventoryItem.query.all()

        for item in items if items is not None:
            # 소진 예상일 계산 (간단한 예측)
            daily_consumption = item.current_stock / 30 if item.current_stock > 0 else 0
            days_until_stockout = item.current_stock / daily_consumption if daily_consumption > 0 else float('inf')

            inventory_status.append({
                'name': item.name,
                'current_stock': item.current_stock,
                'min_stock': item.min_stock,
                'days_until_stockout': round(days_until_stockout, 1) if days_until_stockout != float('inf') else 0
            })

        return {
            'inventory_status': inventory_status
        }

    except Exception as e:
        logger.error(f"재고 데이터 수집 오류: {str(e)}")
        raise


def collect_operational_data(start_date,  end_date):
    """운영 효율성 데이터 수집"""
    try:
        # 주문 처리 시간 계산
        orders = Order.query.filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        ).all()

        # 임시 데이터 (실제로는 더 정확한 계산 필요)
        avg_order_time = 12.5  # 분
        customer_satisfaction = 4.2  # 점수
        inventory_turnover = 8.5  # 회전율
        employee_productivity = 78.5  # %

        return {
            'avg_order_time': avg_order_time,
            'customer_satisfaction': customer_satisfaction,
            'inventory_turnover': inventory_turnover,
            'employee_productivity': employee_productivity,
            'order_time_achievement': 83.3,  # 15분 대비 달성률
            'satisfaction_achievement': 93.3,  # 4.5점 대비 달성률
            'turnover_achievement': 70.8,  # 12회 대비 달성률
            'productivity_achievement': 92.4  # 85% 대비 달성률
        }

    except Exception as e:
        logger.error(f"운영 데이터 수집 오류: {str(e)}")
        raise


@advanced_reports.route('/schedule', methods=['POST'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def schedule_report():
    """보고서 스케줄링"""
    try:
        data = request.get_json()

        if not data or 'report_type' not in data:
            return jsonify({'error': 'Report type is required'}), 400

        # 스케줄링 정보 저장 (실제로는 데이터베이스에 저장)
        schedule_info = {
            'report_type': data['report_type'] if data is not None else None,
            'frequency': data.get() if data else None'frequency', 'weekly') if data else None,
            'recipients': data.get() if data else None'recipients', []) if data else None,
            'format': data.get() if data else None'format', 'pdf') if data else None,
            'created_by': g.user.id,
            'created_at': datetime.utcnow().isoformat()
        }

        return jsonify({
            'success': True,
            'message': 'Report scheduled successfully',
            'schedule_id': 'temp_schedule_id'  # 실제로는 생성된 ID
        })

    except Exception as e:
        logger.error(f"보고서 스케줄링 오류: {str(e)}")
        return jsonify({'error': 'Failed to schedule report'}), 500


@advanced_reports.route('/schedules', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def get_scheduled_reports():
    """스케줄된 보고서 목록 조회"""
    try:
        # 임시 데이터 (실제로는 데이터베이스에서 조회)
        scheduled_reports = [
            {
                'id': 'schedule_1',
                'report_type': 'sales_summary',
                'frequency': 'weekly',
                'recipients': ['admin@example.com'],
                'format': 'pdf',
                'next_run': (datetime.now() + timedelta(days=7)).isoformat(),
                'status': 'active'
            }
        ]

        return jsonify({
            'scheduled_reports': scheduled_reports
        })

    except Exception as e:
        logger.error(f"스케줄된 보고서 조회 오류: {str(e)}")
        return jsonify({'error': 'Failed to fetch scheduled reports'}), 500
