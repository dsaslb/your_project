from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tempfile
import uuid

contracts_bp = Blueprint('contracts', __name__)

# 한글 폰트 등록 (시스템에 한글 폰트가 있는 경우)
try:
    pdfmetrics.registerFont(TTFont('NanumGothic', 'C:/Windows/Fonts/malgun.ttf'))
    KOREAN_FONT = 'NanumGothic'
except:
    KOREAN_FONT = 'Helvetica'

@contracts_bp.route('/generate', methods=['POST'])
@cross_origin(supports_credentials=True)
def generate_contract():
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['employee_name', 'position', 'department', 'email', 'phone', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} 필드가 필요합니다.'}), 400
        
        # 임시 PDF 파일 생성
        temp_dir = tempfile.gettempdir()
        filename = f"contract_{data['employee_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(temp_dir, filename)
        
        # PDF 생성
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # 중앙 정렬
            fontName=KOREAN_FONT
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            fontName=KOREAN_FONT
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName=KOREAN_FONT
        )
        
        # 제목
        story.append(Paragraph("근로계약서", title_style))
        story.append(Spacer(1, 20))
        
        # 기본 정보
        story.append(Paragraph("1. 근로자 정보", heading_style))
        
        basic_info_data = [
            ['구분', '내용'],
            ['성명', data['employee_name']],
            ['직책', data['position']],
            ['부서', data['department']],
            ['이메일', data['email']],
            ['연락처', data['phone']]
        ]
        
        basic_table = Table(basic_info_data, colWidths=[1.5*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        
        # 계약 기간
        story.append(Paragraph("2. 계약 기간", heading_style))
        contract_period_data = [
            ['구분', '날짜'],
            ['계약 시작일', data['start_date']],
            ['계약 종료일', data.get('end_date', '무기한')]
        ]
        
        period_table = Table(contract_period_data, colWidths=[1.5*inch, 4*inch])
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(period_table)
        
        # 근무 조건
        story.append(Paragraph("3. 근무 조건", heading_style))
        
        # 근무일
        work_days = ', '.join(data.get('work_days', []))
        work_hours = data.get('work_hours', {})
        work_time = f"{work_hours.get('start', '')} ~ {work_hours.get('end', '')}"
        
        work_conditions_data = [
            ['구분', '내용'],
            ['근무일', work_days],
            ['근무시간', work_time]
        ]
        
        work_table = Table(work_conditions_data, colWidths=[1.5*inch, 4*inch])
        work_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(work_table)
        
        # 급여 정보
        story.append(Paragraph("4. 급여 정보", heading_style))
        salary = data.get('salary', {})
        salary_data = [
            ['구분', '금액'],
            ['기본급', f"{salary.get('base', 0):,}원"],
            ['수당', f"{salary.get('allowance', 0):,}원"],
            ['상여금', f"{salary.get('bonus', 0):,}원"],
            ['총 급여', f"{salary.get('total', 0):,}원"]
        ]
        
        salary_table = Table(salary_data, colWidths=[1.5*inch, 4*inch])
        salary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(salary_table)
        
        # 복리후생
        story.append(Paragraph("5. 복리후생", heading_style))
        benefits = data.get('benefits', [])
        benefits_text = ', '.join(benefits) if benefits else '해당없음'
        story.append(Paragraph(f"제공 복리후생: {benefits_text}", normal_style))
        
        # 기타 조건
        story.append(Paragraph("6. 기타 조건", heading_style))
        story.append(Paragraph(f"수습기간: {data.get('probation_period', 0)}개월", normal_style))
        story.append(Paragraph(f"사전통지기간: {data.get('notice_period', 0)}개월", normal_style))
        
        if data.get('responsibilities'):
            story.append(Paragraph(f"주요 업무: {data['responsibilities']}", normal_style))
        
        if data.get('terms'):
            story.append(Paragraph(f"특별 조건: {data['terms']}", normal_style))
        
        # 계약서 생성일
        story.append(Spacer(1, 30))
        generated_date = data.get('generated_date', datetime.now().isoformat())
        date_obj = datetime.fromisoformat(generated_date.replace('Z', '+00:00'))
        formatted_date = date_obj.strftime('%Y년 %m월 %d일')
        story.append(Paragraph(f"계약서 생성일: {formatted_date}", normal_style))
        
        # PDF 생성
        doc.build(story)
        
        # 파일 URL 생성
        download_url = f"/api/contracts/download/{filename}"
        
        return jsonify({
            'success': True,
            'message': '계약서가 성공적으로 생성되었습니다.',
            'download_url': download_url,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contracts_bp.route('/download/<filename>', methods=['GET'])
@cross_origin(supports_credentials=True)
def download_contract(filename):
    try:
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': '파일을 찾을 수 없습니다.'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contracts_bp.route('/list', methods=['GET'])
@cross_origin(supports_credentials=True)
def list_contracts():
    try:
        # 실제 구현에서는 데이터베이스에서 계약서 목록을 가져옴
        # 현재는 임시 데이터 반환
        contracts = [
            {
                'id': 1,
                'employee_name': '홍길동',
                'position': '매니저',
                'department': '영업팀',
                'created_date': '2024-01-15',
                'status': 'active'
            }
        ]
        
        return jsonify({
            'success': True,
            'contracts': contracts
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 