from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models import db, Staff, Contract, HealthCertificate, Notification, User
import os

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/api/staff', methods=['GET'])
@login_required
def get_staff_list():
    """직원 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 검색 및 필터링
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')
        
        query = Staff.query
        
        # 검색 필터
        if search:
            query = query.filter(
                or_(
                    Staff.name.contains(search),
                    Staff.position.contains(search),
                    Staff.department.contains(search)
                )
            )
        
        # 상태 필터
        if status_filter != 'all':
            query = query.filter(Staff.status == status_filter)
        
        # 매장별 필터링 (관리자가 아닌 경우)
        if not current_user.is_admin():
            query = query.filter(Staff.restaurant_id == current_user.branch_id)
        
        staff_list = query.all()
        
        result = []
        for staff in staff_list:
            # 계약서 정보
            contracts = Contract.query.filter_by(staff_id=staff.id).all()
            contract_info = []
            for contract in contracts:
                contract_info.append({
                    'id': contract.id,
                    'contract_number': contract.contract_number,
                    'start_date': contract.start_date.strftime('%Y-%m-%d'),
                    'expiry_date': contract.expiry_date.strftime('%Y-%m-%d'),
                    'renewal_date': contract.renewal_date.strftime('%Y-%m-%d'),
                    'contract_type': contract.contract_type,
                    'is_expiring_soon': contract.is_expiring_soon,
                    'is_expired': contract.is_expired,
                    'days_until_expiry': contract.days_until_expiry,
                    'file_path': contract.file_path,
                    'file_name': contract.file_name
                })
            
            # 보건증 정보
            health_certs = HealthCertificate.query.filter_by(staff_id=staff.id).all()
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
                    'file_name': cert.file_name
                })
            
            staff_data = {
                'id': staff.id,
                'name': staff.name,
                'position': staff.position,
                'department': staff.department,
                'phone': staff.phone,
                'email': staff.email,
                'status': staff.status,
                'join_date': staff.join_date.strftime('%Y-%m-%d'),
                'salary': staff.salary,
                'contracts': contract_info,
                'health_certificates': health_info
            }
            result.append(staff_data)
        
        return jsonify({'staff': result})
    
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
@login_required
def get_expiring_documents():
    """만료 임박 서류 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 30일 이내 만료되는 서류 조회
        thirty_days_from_now = datetime.now().date() + timedelta(days=30)
        
        # 계약서 만료 임박
        expiring_contracts = Contract.query.filter(
            and_(
                Contract.expiry_date <= thirty_days_from_now,
                Contract.expiry_date >= datetime.now().date()
            )
        ).all()
        
        # 보건증 만료 임박
        expiring_health_certs = HealthCertificate.query.filter(
            and_(
                HealthCertificate.expiry_date <= thirty_days_from_now,
                HealthCertificate.expiry_date >= datetime.now().date()
            )
        ).all()
        
        result = {
            'contracts': [],
            'health_certificates': []
        }
        
        for contract in expiring_contracts:
            staff = Staff.query.get(contract.staff_id)
            if staff:
                result['contracts'].append({
                    'id': contract.id,
                    'staff_name': staff.name,
                    'staff_position': staff.position,
                    'contract_number': contract.contract_number,
                    'expiry_date': contract.expiry_date.strftime('%Y-%m-%d'),
                    'days_until_expiry': contract.days_until_expiry,
                    'is_expired': contract.is_expired
                })
        
        for cert in expiring_health_certs:
            staff = Staff.query.get(cert.staff_id)
            if staff:
                result['health_certificates'].append({
                    'id': cert.id,
                    'staff_name': staff.name,
                    'staff_position': staff.position,
                    'certificate_number': cert.certificate_number,
                    'expiry_date': cert.expiry_date.strftime('%Y-%m-%d'),
                    'days_until_expiry': cert.days_until_expiry,
                    'is_expired': cert.is_expired
                })
        
        return jsonify(result)
    
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