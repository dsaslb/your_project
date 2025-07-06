from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models import db, Staff, Contract, HealthCertificate, Notification, User
import os

staff_bp = Blueprint('api_staff', __name__)

@staff_bp.route('/api/staff', methods=['GET'])
# @login_required
def get_staff_list():
    """직원 목록 조회"""
    try:
        # 테스트용 더미 데이터 반환
        dummy_staff = get_dummy_staff_data()
        
        return jsonify({'staff': dummy_staff})
    
    except Exception as e:
        current_app.logger.error(f"직원 목록 조회 오류: {str(e)}")
        return jsonify({'error': '직원 목록을 불러오는데 실패했습니다.'}), 500

@staff_bp.route('/api/staff/<int:staff_id>/documents', methods=['GET'])
@login_required
def get_staff_documents(staff_id):
    """직원 서류 상세 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        staff = Staff.query.get_or_404(staff_id)
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and staff.restaurant_id != current_user.branch_id:
            return jsonify({'error': '접근 권한이 없습니다.'}), 403
        
        # 계약서 정보
        contracts = Contract.query.filter_by(staff_id=staff_id).all()
        contract_info = []
        for contract in contracts:
            contract_info.append({
                'id': contract.id,
                'contract_number': contract.contract_number,
                'start_date': contract.start_date.strftime('%Y-%m-%d'),
                'expiry_date': contract.expiry_date.strftime('%Y-%m-%d'),
                'renewal_date': contract.renewal_date.strftime('%Y-%m-%d'),
                'contract_type': contract.contract_type,
                'salary_amount': contract.salary_amount,
                'is_expiring_soon': contract.is_expiring_soon,
                'is_expired': contract.is_expired,
                'days_until_expiry': contract.days_until_expiry,
                'file_path': contract.file_path,
                'file_name': contract.file_name,
                'file_size': contract.file_size
            })
        
        # 보건증 정보
        health_certs = HealthCertificate.query.filter_by(staff_id=staff_id).all()
        health_info = []
        for cert in health_certs:
            health_info.append({
                'id': cert.id,
                'certificate_number': cert.certificate_number,
                'issue_date': cert.issue_date.strftime('%Y-%m-%d'),
                'expiry_date': cert.expiry_date.strftime('%Y-%m-%d'),
                'renewal_date': cert.renewal_date.strftime('%Y-%m-%d'),
                'issuing_authority': cert.issuing_authority,
                'certificate_type': cert.certificate_type,
                'is_expiring_soon': cert.is_expiring_soon,
                'is_expired': cert.is_expired,
                'days_until_expiry': cert.days_until_expiry,
                'file_path': cert.file_path,
                'file_name': cert.file_name,
                'file_size': cert.file_size
            })
        
        return jsonify({
            'staff': {
                'id': staff.id,
                'name': staff.name,
                'position': staff.position,
                'department': staff.department
            },
            'contracts': contract_info,
            'health_certificates': health_info
        })
    
    except Exception as e:
        current_app.logger.error(f"직원 서류 조회 오류: {str(e)}")
        return jsonify({'error': '서류 정보를 불러오는데 실패했습니다.'}), 500

@staff_bp.route('/api/staff/expiring-documents', methods=['GET'])
# @login_required
def get_expiring_documents():
    """만료 임박 서류 조회"""
    try:
        # 테스트용 더미 데이터 반환
        dummy_expiring = {
            'contracts': [
                {
                    'id': 1,
                    'staff_name': '김철수',
                    'contract_number': 'CT-2023-001',
                    'expiry_date': '2024-12-31',
                    'days_until_expiry': 25,
                    'contract_type': '정규직'
                }
            ],
            'health_certificates': [
                {
                    'id': 1,
                    'staff_name': '김철수',
                    'certificate_number': 'HC-2023-001',
                    'expiry_date': '2024-11-15',
                    'days_until_expiry': 15,
                    'certificate_type': '식품위생교육'
                }
            ]
        }
        
        return jsonify(dummy_expiring)
    
    except Exception as e:
        current_app.logger.error(f"만료 임박 서류 조회 오류: {str(e)}")
        return jsonify({'error': '만료 임박 서류를 불러오는데 실패했습니다.'}), 500

@staff_bp.route('/api/staff/documents/<int:document_id>/download/<document_type>', methods=['GET'])
@login_required
def download_document(document_id, document_type):
    """서류 파일 다운로드"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        if document_type == 'contract':
            document = Contract.query.get_or_404(document_id)
        elif document_type == 'health_certificate':
            document = HealthCertificate.query.get_or_404(document_id)
        else:
            return jsonify({'error': '잘못된 문서 유형입니다.'}), 400
        
        # 파일 존재 확인
        if not document.file_path or not os.path.exists(document.file_path):
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
        
        # 파일 다운로드
        from flask import send_file
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.file_name or f"{document_type}_{document_id}.pdf"
        )
    
    except Exception as e:
        current_app.logger.error(f"파일 다운로드 오류: {str(e)}")
        return jsonify({'error': '파일 다운로드에 실패했습니다.'}), 500

@staff_bp.route('/api/staff', methods=['POST'])
# @login_required
def create_staff():
    """새 직원 추가"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'email', 'phone', 'position', 'department', 'join_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 테스트용 더미 응답 (실제로는 DB에 저장)
        new_staff = {
            'id': len(get_dummy_staff_data()) + 1,
            'name': data['name'],
            'position': data['position'],
            'department': data['department'],
            'phone': data['phone'],
            'email': data['email'],
            'status': data.get('status', 'active'),
            'join_date': data['join_date'],
            'salary': data.get('salary', 0),
            'contracts': [],
            'health_certificates': []
        }
        
        # 계약서 정보가 있으면 추가
        if data.get('contract_type') and data.get('contract_start_date') and data.get('contract_expiry_date'):
            new_staff['contracts'].append({
                'id': 1,
                'contract_number': f'CT-{datetime.now().year}-{new_staff["id"]:03d}',
                'start_date': data['contract_start_date'],
                'expiry_date': data['contract_expiry_date'],
                'renewal_date': data['contract_expiry_date'],
                'contract_type': data['contract_type'],
                'is_expiring_soon': False,
                'is_expired': False,
                'days_until_expiry': 365,
                'file_path': None,
                'file_name': None
            })
        
        # 보건증 정보가 있으면 추가
        if data.get('health_certificate_type') and data.get('health_certificate_issue_date') and data.get('health_certificate_expiry_date'):
            new_staff['health_certificates'].append({
                'id': 1,
                'certificate_number': f'HC-{datetime.now().year}-{new_staff["id"]:03d}',
                'issue_date': data['health_certificate_issue_date'],
                'expiry_date': data['health_certificate_expiry_date'],
                'renewal_date': data['health_certificate_expiry_date'],
                'issuing_authority': data.get('issuing_authority', '서울시보건소'),
                'certificate_type': data['health_certificate_type'],
                'is_expiring_soon': False,
                'is_expired': False,
                'days_until_expiry': 365,
                'file_path': None,
                'file_name': None
            })
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 추가되었습니다.',
            'staff': new_staff
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"직원 추가 오류: {str(e)}")
        return jsonify({'error': '직원 추가에 실패했습니다.'}), 500

@staff_bp.route('/api/staff-stats', methods=['GET'])
@login_required
def staff_stats():
    """직원 통계 API (routes/staff_management.py에서 통합)"""
    try:
        total_staff = User.query.count()
        active_staff = User.query.filter_by(is_active=True).count()
        inactive_staff = total_staff - active_staff
        # 부서별 통계
        department_stats = (
            db.session.query(User.department, db.func.count(User.id).label("count"))
            .group_by(User.department)
            .all()
        )
        return jsonify({
            "total_staff": total_staff,
            "active_staff": active_staff,
            "inactive_staff": inactive_staff,
            "department_stats": [
                {"department": d.department, "count": d.count} for d in department_stats
            ],
        })
    except Exception as e:
        current_app.logger.error(f"직원 통계 조회 오류: {str(e)}")
        return jsonify({"error": "통계 조회 중 오류가 발생했습니다."}), 500

@staff_bp.route('/api/staff-status', methods=['GET'])
@login_required
def staff_status():
    """직원 현황 API (app.py에서 통합)"""
    try:
        staff_members = User.query.filter_by(role="employee").all()
        staff_data = []
        for staff in staff_members:
            staff_data.append({
                "id": f"EMP-{staff.id:03d}",
                "name": staff.username,
                "status": "active" if getattr(staff, 'status', None) == "approved" else "off",
                "role": getattr(staff, 'position', '직원')
            })
        # 더미 데이터 추가
        staff_data.extend([
            {"id": "EMP-101", "name": "김철수", "status": "active", "role": "주방장"},
            {"id": "EMP-102", "name": "이영희", "status": "active", "role": "서버"},
            {"id": "EMP-103", "name": "박민수", "status": "break", "role": "주방보조"},
            {"id": "EMP-104", "name": "정수진", "status": "off", "role": "매니저"}
        ])
        return jsonify({"success": True, "data": staff_data})
    except Exception as e:
        current_app.logger.error(f"직원 현황 조회 오류: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

def get_dummy_staff_data():
    """더미 직원 데이터 반환"""
    return [
        {
            'id': 1,
            'name': '김철수',
            'position': '주방장',
            'department': '주방',
            'phone': '010-1234-5678',
            'email': 'kim@restaurant.com',
            'status': 'active',
            'join_date': '2023-01-15',
            'salary': 3500000,
            'contracts': [
                {
                    'id': 1,
                    'contract_number': 'CT-2023-001',
                    'start_date': '2023-01-15',
                    'expiry_date': '2024-12-31',
                    'renewal_date': '2024-12-15',
                    'contract_type': '정규직',
                    'is_expiring_soon': True,
                    'is_expired': False,
                    'days_until_expiry': 25,
                    'file_path': '/documents/contract1.pdf',
                    'file_name': '김철수_계약서.pdf'
                }
            ],
            'health_certificates': [
                {
                    'id': 1,
                    'certificate_number': 'HC-2023-001',
                    'issue_date': '2023-01-10',
                    'expiry_date': '2024-11-15',
                    'renewal_date': '2024-11-01',
                    'issuing_authority': '서울시보건소',
                    'certificate_type': '식품위생교육',
                    'is_expiring_soon': True,
                    'is_expired': False,
                    'days_until_expiry': 15,
                    'file_path': '/documents/health1.pdf',
                    'file_name': '김철수_보건증.pdf'
                }
            ]
        },
        {
            'id': 2,
            'name': '이영희',
            'position': '서버',
            'department': '홀',
            'phone': '010-2345-6789',
            'email': 'lee@restaurant.com',
            'status': 'active',
            'join_date': '2023-03-20',
            'salary': 2800000,
            'contracts': [
                {
                    'id': 2,
                    'contract_number': 'CT-2023-002',
                    'start_date': '2023-03-20',
                    'expiry_date': '2025-03-15',
                    'renewal_date': '2025-03-01',
                    'contract_type': '정규직',
                    'is_expiring_soon': False,
                    'is_expired': False,
                    'days_until_expiry': 120,
                    'file_path': '/documents/contract2.pdf',
                    'file_name': '이영희_계약서.pdf'
                }
            ],
            'health_certificates': []
        }
    ] 