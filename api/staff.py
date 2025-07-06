from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models import db, Staff, Contract, HealthCertificate, Notification, User, ApproveLog
import os

staff_bp = Blueprint('api_staff', __name__)

@staff_bp.route('/api/staff', methods=['GET'])
@login_required
def get_staff_list():
    """통합 직원 목록 조회 API"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 검색 파라미터
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        status = request.args.get('status', '')
        
        # User 테이블에서 직원 데이터 조회
        query = User.query.filter(User.role.in_(['employee', 'manager']))
        
        # 검색 필터 적용
        if search:
            query = query.filter(
                or_(
                    User.username.contains(search),
                    User.name.contains(search),
                    User.email.contains(search),
                    User.phone.contains(search)
                )
            )
        
        if department:
            query = query.filter(User.department == department)
        
        if status:
            query = query.filter(User.status == status)
        
        # 매장별 필터링 (관리자가 아닌 경우)
        if not current_user.is_admin():
            query = query.filter(User.branch_id == current_user.branch_id)
        
        users = query.all()
        
        # 통합된 직원 데이터 구성
        staff_data = []
        for user in users:
            # Staff 테이블에서 추가 정보 조회
            staff_profile = Staff.query.filter_by(user_id=user.id).first()
            
            # 계약서 정보 조회
            contracts = []
            if staff_profile:
                contract_list = Contract.query.filter_by(staff_id=staff_profile.id).all()
                for contract in contract_list:
                    contracts.append({
                        'id': contract.id,
                        'contract_number': contract.contract_number,
                        'start_date': contract.start_date.strftime('%Y-%m-%d') if contract.start_date else None,
                        'expiry_date': contract.expiry_date.strftime('%Y-%m-%d') if contract.expiry_date else None,
                        'renewal_date': contract.renewal_date.strftime('%Y-%m-%d') if contract.renewal_date else None,
                        'contract_type': contract.contract_type,
                        'salary_amount': contract.salary_amount,
                        'is_expiring_soon': contract.is_expiring_soon if hasattr(contract, 'is_expiring_soon') else False,
                        'is_expired': contract.is_expired if hasattr(contract, 'is_expired') else False,
                        'days_until_expiry': contract.days_until_expiry if hasattr(contract, 'days_until_expiry') else 0,
                        'file_path': contract.file_path,
                        'file_name': contract.file_name,
                        'file_size': contract.file_size
                    })
            
            # 보건증 정보 조회
            health_certificates = []
            if staff_profile:
                health_list = HealthCertificate.query.filter_by(staff_id=staff_profile.id).all()
                for cert in health_list:
                    health_certificates.append({
                        'id': cert.id,
                        'certificate_number': cert.certificate_number,
                        'issue_date': cert.issue_date.strftime('%Y-%m-%d') if cert.issue_date else None,
                        'expiry_date': cert.expiry_date.strftime('%Y-%m-%d') if cert.expiry_date else None,
                        'renewal_date': cert.renewal_date.strftime('%Y-%m-%d') if cert.renewal_date else None,
                        'issuing_authority': cert.issuing_authority,
                        'certificate_type': cert.certificate_type,
                        'is_expiring_soon': cert.is_expiring_soon if hasattr(cert, 'is_expiring_soon') else False,
                        'is_expired': cert.is_expired if hasattr(cert, 'is_expired') else False,
                        'days_until_expiry': cert.days_until_expiry if hasattr(cert, 'days_until_expiry') else 0,
                        'file_path': cert.file_path,
                        'file_name': cert.file_name,
                        'file_size': cert.file_size
                    })
            
            # 통합된 직원 정보
            staff_info = {
                'id': user.id,
                'name': user.name or user.username,
                'username': user.username,
                'position': getattr(user, 'position', '직원'),
                'department': user.department or '미지정',
                'email': user.email,
                'phone': user.phone,
                'join_date': user.created_at.strftime('%Y-%m-%d') if user.created_at else None,
                'status': user.status or 'active',
                'role': user.role,
                'is_active': user.is_active,
                'branch_id': user.branch_id,
                'branch_name': user.branch.name if user.branch else None,
                'salary': getattr(staff_profile, 'salary', None) if staff_profile else None,
                'contracts': contracts,
                'health_certificates': health_certificates,
                'permissions': user.permissions or {},
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else None
            }
            
            staff_data.append(staff_info)
        
        # 통계 정보 계산
        total_count = len(staff_data)
        active_count = len([s for s in staff_data if s['status'] == 'active'])
        inactive_count = total_count - active_count
        
        # 부서별 통계
        department_stats = {}
        for staff in staff_data:
            dept = staff['department']
            if dept not in department_stats:
                department_stats[dept] = 0
            department_stats[dept] += 1
        
        return jsonify({
            'success': True,
            'staff': staff_data,
            'stats': {
                'total': total_count,
                'active': active_count,
                'inactive': inactive_count,
                'departments': department_stats
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"직원 목록 조회 오류: {str(e)}")
        return jsonify({'error': '직원 목록을 불러오는데 실패했습니다.'}), 500

@staff_bp.route('/api/staff/<int:staff_id>', methods=['GET'])
@login_required
def get_staff_detail(staff_id):
    """직원 상세 정보 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        user = User.query.get_or_404(staff_id)
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and user.branch_id != current_user.branch_id:
            return jsonify({'error': '접근 권한이 없습니다.'}), 403
        
        # Staff 프로필 정보 조회
        staff_profile = Staff.query.filter_by(user_id=user.id).first()
        
        # 계약서 정보
        contracts = []
        if staff_profile:
            contract_list = Contract.query.filter_by(staff_id=staff_profile.id).all()
            for contract in contract_list:
                contracts.append({
                    'id': contract.id,
                    'contract_number': contract.contract_number,
                    'start_date': contract.start_date.strftime('%Y-%m-%d') if contract.start_date else None,
                    'expiry_date': contract.expiry_date.strftime('%Y-%m-%d') if contract.expiry_date else None,
                    'renewal_date': contract.renewal_date.strftime('%Y-%m-%d') if contract.renewal_date else None,
                    'contract_type': contract.contract_type,
                    'salary_amount': contract.salary_amount,
                    'is_expiring_soon': contract.is_expiring_soon if hasattr(contract, 'is_expiring_soon') else False,
                    'is_expired': contract.is_expired if hasattr(contract, 'is_expired') else False,
                    'days_until_expiry': contract.days_until_expiry if hasattr(contract, 'days_until_expiry') else 0,
                    'file_path': contract.file_path,
                    'file_name': contract.file_name,
                    'file_size': contract.file_size
                })
        
        # 보건증 정보
        health_certificates = []
        if staff_profile:
            health_list = HealthCertificate.query.filter_by(staff_id=staff_profile.id).all()
            for cert in health_list:
                health_certificates.append({
                    'id': cert.id,
                    'certificate_number': cert.certificate_number,
                    'issue_date': cert.issue_date.strftime('%Y-%m-%d') if cert.issue_date else None,
                    'expiry_date': cert.expiry_date.strftime('%Y-%m-%d') if cert.expiry_date else None,
                    'renewal_date': cert.renewal_date.strftime('%Y-%m-%d') if cert.renewal_date else None,
                    'issuing_authority': cert.issuing_authority,
                    'certificate_type': cert.certificate_type,
                    'is_expiring_soon': cert.is_expiring_soon if hasattr(cert, 'is_expiring_soon') else False,
                    'is_expired': cert.is_expired if hasattr(cert, 'is_expired') else False,
                    'days_until_expiry': cert.days_until_expiry if hasattr(cert, 'days_until_expiry') else 0,
                    'file_path': cert.file_path,
                    'file_name': cert.file_name,
                    'file_size': cert.file_size
                })
        
        return jsonify({
            'success': True,
            'staff': {
                'id': user.id,
                'name': user.name or user.username,
                'username': user.username,
                'position': getattr(user, 'position', '직원'),
                'department': user.department or '미지정',
                'email': user.email,
                'phone': user.phone,
                'join_date': user.created_at.strftime('%Y-%m-%d') if user.created_at else None,
                'status': user.status or 'active',
                'role': user.role,
                'is_active': user.is_active,
                'branch_id': user.branch_id,
                'branch_name': user.branch.name if user.branch else None,
                'salary': getattr(staff_profile, 'salary', None) if staff_profile else None,
                'contracts': contracts,
                'health_certificates': health_certificates,
                'permissions': user.permissions or {},
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else None
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"직원 상세 조회 오류: {str(e)}")
        return jsonify({'error': '직원 정보를 불러오는데 실패했습니다.'}), 500

@staff_bp.route('/api/staff/<int:staff_id>/documents', methods=['GET'])
@login_required
def get_staff_documents(staff_id):
    """직원 서류 상세 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        user = User.query.get_or_404(staff_id)
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and user.branch_id != current_user.branch_id:
            return jsonify({'error': '접근 권한이 없습니다.'}), 403
        
        staff_profile = Staff.query.filter_by(user_id=user.id).first()
        if not staff_profile:
            return jsonify({'error': '직원 프로필을 찾을 수 없습니다.'}), 404
        
        # 계약서 정보
        contracts = Contract.query.filter_by(staff_id=staff_profile.id).all()
        contract_info = []
        for contract in contracts:
            contract_info.append({
                'id': contract.id,
                'contract_number': contract.contract_number,
                'start_date': contract.start_date.strftime('%Y-%m-%d') if contract.start_date else None,
                'expiry_date': contract.expiry_date.strftime('%Y-%m-%d') if contract.expiry_date else None,
                'renewal_date': contract.renewal_date.strftime('%Y-%m-%d') if contract.renewal_date else None,
                'contract_type': contract.contract_type,
                'salary_amount': contract.salary_amount,
                'is_expiring_soon': contract.is_expiring_soon if hasattr(contract, 'is_expiring_soon') else False,
                'is_expired': contract.is_expired if hasattr(contract, 'is_expired') else False,
                'days_until_expiry': contract.days_until_expiry if hasattr(contract, 'days_until_expiry') else 0,
                'file_path': contract.file_path,
                'file_name': contract.file_name,
                'file_size': contract.file_size
            })
        
        # 보건증 정보
        health_certs = HealthCertificate.query.filter_by(staff_id=staff_profile.id).all()
        health_info = []
        for cert in health_certs:
            health_info.append({
                'id': cert.id,
                'certificate_number': cert.certificate_number,
                'issue_date': cert.issue_date.strftime('%Y-%m-%d') if cert.issue_date else None,
                'expiry_date': cert.expiry_date.strftime('%Y-%m-%d') if cert.expiry_date else None,
                'renewal_date': cert.renewal_date.strftime('%Y-%m-%d') if cert.renewal_date else None,
                'issuing_authority': cert.issuing_authority,
                'certificate_type': cert.certificate_type,
                'is_expiring_soon': cert.is_expiring_soon if hasattr(cert, 'is_expiring_soon') else False,
                'is_expired': cert.is_expired if hasattr(cert, 'is_expired') else False,
                'days_until_expiry': cert.days_until_expiry if hasattr(cert, 'days_until_expiry') else 0,
                'file_path': cert.file_path,
                'file_name': cert.file_name,
                'file_size': cert.file_size
            })
        
        return jsonify({
            'success': True,
            'staff': {
                'id': user.id,
                'name': user.name or user.username,
                'position': getattr(user, 'position', '직원'),
                'department': user.department or '미지정'
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
        today = datetime.now().date()
        thirty_days_later = today + timedelta(days=30)
        
        # 만료 임박 계약서
        expiring_contracts = []
        contracts = Contract.query.filter(
            and_(
                Contract.expiry_date >= today,
                Contract.expiry_date <= thirty_days_later
            )
        ).all()
        
        for contract in contracts:
            staff = contract.staff
            user = staff.user if staff else None
            if user:
                expiring_contracts.append({
                    'id': contract.id,
                    'staff_name': user.name or user.username,
                    'contract_number': contract.contract_number,
                    'expiry_date': contract.expiry_date.strftime('%Y-%m-%d') if contract.expiry_date else None,
                    'days_until_expiry': (contract.expiry_date - today).days if contract.expiry_date else 0,
                    'contract_type': contract.contract_type
                })
        
        # 만료 임박 보건증
        expiring_health_certs = []
        health_certs = HealthCertificate.query.filter(
            and_(
                HealthCertificate.expiry_date >= today,
                HealthCertificate.expiry_date <= thirty_days_later
            )
        ).all()
        
        for cert in health_certs:
            staff = cert.staff
            user = staff.user if staff else None
            if user:
                expiring_health_certs.append({
                    'id': cert.id,
                    'staff_name': user.name or user.username,
                    'certificate_number': cert.certificate_number,
                    'expiry_date': cert.expiry_date.strftime('%Y-%m-%d') if cert.expiry_date else None,
                    'days_until_expiry': (cert.expiry_date - today).days if cert.expiry_date else 0,
                    'certificate_type': cert.certificate_type
                })
        
        return jsonify({
            'success': True,
            'contracts': expiring_contracts,
            'health_certificates': expiring_health_certs
        })
    
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
@login_required
def create_staff():
    """새 직원 추가"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'create'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'email', 'phone', 'position', 'department', 'join_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 이메일 중복 확인
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': '이미 존재하는 이메일입니다.'}), 400
        
        # 새 사용자 생성
        new_user = User(
            username=data['email'].split('@')[0],  # 이메일에서 사용자명 생성
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            role='employee',
            department=data['department'],
            position=data['position'],
            status='active',
            branch_id=current_user.branch_id,
            permissions=data.get('permissions', {})
        )
        
        # 임시 비밀번호 설정 (이메일로 전송 예정)
        new_user.set_password('temp123456')
        
        db.session.add(new_user)
        db.session.flush()  # ID 생성
        
        # Staff 프로필 생성
        staff_profile = Staff(
            name=data['name'],
            position=data['position'],
            phone=data['phone'],
            email=data['email'],
            status='active',
            join_date=datetime.strptime(data['join_date'], '%Y-%m-%d').date(),
            salary=data.get('salary'),
            department=data['department'],
            restaurant_id=current_user.branch_id,
            user_id=new_user.id
        )
        
        db.session.add(staff_profile)
        db.session.flush()  # ID 생성
        
        # 계약서 정보가 있으면 추가
        if data.get('contract_type') and data.get('contract_start_date') and data.get('contract_expiry_date'):
            contract = Contract(
                staff_id=staff_profile.id,
                contract_number=f"CT-{datetime.now().year}-{new_user.id:03d}",
                start_date=datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date(),
                expiry_date=datetime.strptime(data['contract_expiry_date'], '%Y-%m-%d').date(),
                contract_type=data['contract_type'],
                salary_amount=data.get('salary', 0)
            )
            db.session.add(contract)
        
        # 보건증 정보가 있으면 추가
        if data.get('health_certificate_type') and data.get('health_certificate_issue_date') and data.get('health_certificate_expiry_date'):
            health_cert = HealthCertificate(
                staff_id=staff_profile.id,
                certificate_number=f"HC-{datetime.now().year}-{new_user.id:03d}",
                issue_date=datetime.strptime(data['health_certificate_issue_date'], '%Y-%m-%d').date(),
                expiry_date=datetime.strptime(data['health_certificate_expiry_date'], '%Y-%m-%d').date(),
                issuing_authority=data.get('issuing_authority', '서울시보건소'),
                certificate_type=data['health_certificate_type']
            )
            db.session.add(health_cert)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 추가되었습니다.',
            'staff_id': new_user.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"직원 추가 오류: {str(e)}")
        return jsonify({'error': '직원 추가에 실패했습니다.'}), 500

@staff_bp.route('/api/staff/<int:staff_id>', methods=['PUT'])
@login_required
def update_staff(staff_id):
    """직원 정보 수정"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'edit'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        user = User.query.get_or_404(staff_id)
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and user.branch_id != current_user.branch_id:
            return jsonify({'error': '접근 권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 사용자 정보 업데이트
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'position' in data:
            user.position = data['position']
        if 'department' in data:
            user.department = data['department']
        if 'status' in data:
            user.status = data['status']
        if 'permissions' in data:
            user.permissions = data['permissions']
        
        # Staff 프로필 업데이트
        staff_profile = Staff.query.filter_by(user_id=user.id).first()
        if staff_profile:
            if 'name' in data:
                staff_profile.name = data['name']
            if 'position' in data:
                staff_profile.position = data['position']
            if 'phone' in data:
                staff_profile.phone = data['phone']
            if 'email' in data:
                staff_profile.email = data['email']
            if 'status' in data:
                staff_profile.status = data['status']
            if 'department' in data:
                staff_profile.department = data['department']
            if 'salary' in data:
                staff_profile.salary = data['salary']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '직원 정보가 성공적으로 수정되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"직원 수정 오류: {str(e)}")
        return jsonify({'error': '직원 정보 수정에 실패했습니다.'}), 500

@staff_bp.route('/api/staff/<int:staff_id>', methods=['DELETE'])
@login_required
def delete_staff(staff_id):
    """직원 삭제"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'delete'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        user = User.query.get_or_404(staff_id)
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and user.branch_id != current_user.branch_id:
            return jsonify({'error': '접근 권한이 없습니다.'}), 403
        
        # Staff 프로필 삭제 (계약서, 보건증도 함께 삭제됨)
        staff_profile = Staff.query.filter_by(user_id=user.id).first()
        if staff_profile:
            db.session.delete(staff_profile)
        
        # 사용자 삭제
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 삭제되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"직원 삭제 오류: {str(e)}")
        return jsonify({'error': '직원 삭제에 실패했습니다.'}), 500

@staff_bp.route('/api/staff-stats', methods=['GET'])
@login_required
def staff_stats():
    """직원 통계 API"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 전체 직원 수
        query = User.query.filter(User.role.in_(['employee', 'manager']))
        
        # 매장별 필터링
        if not current_user.is_admin():
            query = query.filter(User.branch_id == current_user.branch_id)
        
        total_staff = query.count()
        active_staff = query.filter_by(status='active').count()
        inactive_staff = total_staff - active_staff
        
        # 부서별 통계
        department_stats = (
            db.session.query(User.department, db.func.count(User.id).label("count"))
            .filter(User.role.in_(['employee', 'manager']))
            .group_by(User.department)
            .all()
        )
        
        # 매장별 필터링 적용
        if not current_user.is_admin():
            department_stats = (
                db.session.query(User.department, db.func.count(User.id).label("count"))
                .filter(User.role.in_(['employee', 'manager']))
                .filter(User.branch_id == current_user.branch_id)
                .group_by(User.department)
                .all()
            )
        
        return jsonify({
            "success": True,
            "total_staff": total_staff,
            "active_staff": active_staff,
            "inactive_staff": inactive_staff,
            "department_stats": [
                {"department": d.department or "미지정", "count": d.count} for d in department_stats
            ],
        })
    except Exception as e:
        current_app.logger.error(f"직원 통계 조회 오류: {str(e)}")
        return jsonify({"error": "통계 조회 중 오류가 발생했습니다."}), 500

@staff_bp.route('/api/staff-status', methods=['GET'])
@login_required
def staff_status():
    """직원 현황 API"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        query = User.query.filter(User.role.in_(['employee', 'manager']))
        
        # 매장별 필터링
        if not current_user.is_admin():
            query = query.filter(User.branch_id == current_user.branch_id)
        
        staff_members = query.all()
        staff_data = []
        
        for staff in staff_members:
            staff_data.append({
                "id": f"EMP-{staff.id:03d}",
                "name": staff.name or staff.username,
                "status": "active" if staff.status == "active" else "off",
                "role": getattr(staff, 'position', '직원'),
                "department": staff.department or "미지정"
            })
        
        return jsonify({"success": True, "data": staff_data})
    except Exception as e:
        current_app.logger.error(f"직원 현황 조회 오류: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@staff_bp.route('/api/staff/pending', methods=['GET'])
@login_required
def get_pending_staff():
    """미승인(대기중) 직원 목록 조회 API"""
    try:
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        users = User.query.filter_by(status='pending').all()
        staff_data = []
        for user in users:
            staff_profile = Staff.query.filter_by(user_id=user.id).first()
            staff_info = {
                'id': user.id,
                'name': user.name or user.username,
                'position': getattr(user, 'position', '직원'),
                'department': user.department or '미지정',
                'email': user.email,
                'phone': user.phone,
                'join_date': user.created_at.strftime('%Y-%m-%d') if user.created_at else None,
                'status': user.status or 'pending',
                'role': user.role,
                'branch_id': user.branch_id,
                'branch_name': user.branch.name if user.branch else None,
                'salary': getattr(staff_profile, 'salary', None) if staff_profile else None,
            }
            staff_data.append(staff_info)
        return jsonify({'success': True, 'staff': staff_data})
    except Exception as e:
        current_app.logger.error(f"미승인 직원 목록 조회 오류: {str(e)}")
        return jsonify({'error': '미승인 직원 목록을 불러오는데 실패했습니다.'}), 500

@staff_bp.route('/api/staff/<int:staff_id>/approve', methods=['POST'])
@login_required
def approve_staff(staff_id):
    """직원 승인 API"""
    try:
        if not current_user.has_permission('employee_management', 'approve'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        user = User.query.get_or_404(staff_id)
        if user.status != 'pending':
            return jsonify({'error': '이미 처리된 직원입니다.'}), 400
        user.status = 'active'
        user.updated_at = datetime.utcnow()
        db.session.commit()
        # 승인 로그 남기기
        log = ApproveLog(user_id=user.id, action='approved', admin_id=current_user.id)
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'message': '직원이 승인되었습니다.'})
    except Exception as e:
        current_app.logger.error(f"직원 승인 오류: {str(e)}")
        return jsonify({'error': '직원 승인에 실패했습니다.'}), 500

@staff_bp.route('/api/staff/<int:staff_id>/reject', methods=['POST'])
@login_required
def reject_staff(staff_id):
    """직원 거절 API (사유 입력 가능)"""
    try:
        if not current_user.has_permission('employee_management', 'approve'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        user = User.query.get_or_404(staff_id)
        if user.status != 'pending':
            return jsonify({'error': '이미 처리된 직원입니다.'}), 400
        data = request.get_json() or {}
        reason = data.get('reason', '')
        user.status = 'rejected'
        user.updated_at = datetime.utcnow()
        db.session.commit()
        # 거절 로그 남기기
        log = ApproveLog(user_id=user.id, action='rejected', admin_id=current_user.id, reason=reason)
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'message': '직원이 거절되었습니다.'})
    except Exception as e:
        current_app.logger.error(f"직원 거절 오류: {str(e)}")
        return jsonify({'error': '직원 거절에 실패했습니다.'}), 500

def get_dummy_staff_data():
    """더미 직원 데이터 반환 (API 실패 시 폴백용)"""
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