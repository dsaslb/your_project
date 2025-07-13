from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models import db, Staff, Contract, HealthCertificate, Notification, User, ApproveLog
import os
import json
from werkzeug.utils import secure_filename
import uuid

staff_bp = Blueprint('staff', __name__)

# 파일 업로드 설정
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder):
    """파일 저장 함수"""
    if file and allowed_file(file.filename):
        # 고유한 파일명 생성
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 폴더가 없으면 생성
        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, folder)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return {
            'filename': unique_filename,
            'original_filename': filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path)
        }
    return None

@staff_bp.route('/staff', methods=['GET'])
# @login_required  # 임시로 인증 우회 (테스트용)
def get_staff_list():
    """통합 직원 목록 조회 API - 모든 페이지에서 사용"""
    try:
        # 권한 확인 (인증되지 않은 사용자 처리)
        if current_user.is_authenticated:
            if not current_user.has_permission('employee_management', 'view'):
                current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
                return jsonify({'error': '권한이 없습니다.'}), 403
        else:
            current_app.logger.info("인증되지 않은 사용자 접근 - 테스트 모드")
        
        # 검색 파라미터
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        status = request.args.get('status', '')
        include_pending = request.args.get('include_pending', 'false').lower() == 'true'
        page_type = request.args.get('page_type', 'all')  # 'all', 'attendance', 'schedule', 'management'
        
        # User 테이블에서 직원 데이터 조회
        query = User.query.filter(User.role.in_(['employee', 'manager']))
        
        # page_type에 따른 필터링
        if page_type == 'attendance':
            # 근태 관리: 승인된 직원만
            query = query.filter(User.status.in_(['approved', 'active']))
        elif page_type == 'schedule':
            # 스케줄 관리: 승인된 직원만
            query = query.filter(User.status.in_(['approved', 'active']))
        elif page_type == 'management':
            # 직원 관리: 모든 상태 (pending 포함)
            pass  # 필터링 없음
        else:
            # 기본값: 승인된 직원만
            query = query.filter(User.status.in_(['approved', 'active']))
        
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
        
        # 매장별 필터링 (관리자가 아닌 경우)
        if current_user.is_authenticated and not current_user.is_admin():
            query = query.filter(
                or_(
                    User.branch_id == None,
                    User.branch_id == current_user.branch_id
                )
            )
        
        users = query.order_by(User.name).all()
        
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
                health_certs = HealthCertificate.query.filter_by(staff_id=staff_profile.id).all()
                for cert in health_certs:
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
                'name': staff_profile.name if staff_profile else (user.name or user.username),
                'username': user.username,
                'position': staff_profile.position if staff_profile else (user.position or '직원'),
                'department': staff_profile.department if staff_profile else (user.department or '미지정'),
                'email': staff_profile.email if staff_profile else user.email,
                'phone': staff_profile.phone if staff_profile else user.phone,
                'join_date': staff_profile.join_date.strftime('%Y-%m-%d') if staff_profile and staff_profile.join_date else (user.created_at.strftime('%Y-%m-%d') if user.created_at else None),
                'status': user.status or 'active',
                'role': user.role,
                'is_active': user.is_active,
                'branch_id': user.branch_id,
                'branch_name': user.branch.name if user.branch else None,
                'salary': staff_profile.salary if staff_profile else None,
                'contracts': contracts,
                'health_certificates': health_certificates,
                'permissions': user.permissions or {},
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else None
            }
            
            staff_data.append(staff_info)
        
        # 통계 정보 계산
        total_count = len(staff_data)
        active_count = len([s for s in staff_data if s['status'] in ['active', 'approved']])
        pending_count = len([s for s in staff_data if s['status'] == 'pending'])
        inactive_count = total_count - active_count - pending_count
        
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
                'pending': pending_count,
                'inactive': inactive_count,
                'departments': department_stats
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"직원 목록 조회 오류: {str(e)}")
        return jsonify({'error': f'직원 목록 조회에 실패했습니다: {str(e)}'}), 500

@staff_bp.route('/staff/<int:staff_id>', methods=['GET'])
@login_required
def get_staff_detail(staff_id):
    """직원 상세 정보 조회"""
    try:
        current_app.logger.info(f"직원 상세 조회 요청: staff_id={staff_id}")
        
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # staff_id가 실제로는 user_id인 경우를 처리
        user = User.query.get(staff_id)
        if not user:
            current_app.logger.error(f"사용자를 찾을 수 없음: staff_id={staff_id}")
            return jsonify({'error': '직원을 찾을 수 없습니다.'}), 404
        
        current_app.logger.info(f"사용자 찾음: user_id={user.id}, username={user.username}")
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and user.branch_id != current_user.branch_id:
            current_app.logger.warning(f"매장 접근 권한 없음: user_branch={user.branch_id}, current_branch={current_user.branch_id}")
            return jsonify({'error': '접근 권한이 없습니다.'}), 403
        
        # Staff 프로필 정보 조회
        staff_profile = Staff.query.filter_by(user_id=user.id).first()
        current_app.logger.info(f"Staff 프로필 조회: found={staff_profile is not None}")
        
        # 계약서 정보
        contracts = []
        if staff_profile:
            contract_list = Contract.query.filter_by(staff_id=staff_profile.id).all()
            current_app.logger.info(f"계약서 조회: count={len(contract_list)}")
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
            health_certs = HealthCertificate.query.filter_by(staff_id=staff_profile.id).all()
            current_app.logger.info(f"보건증 조회: count={len(health_certs)}")
            for cert in health_certs:
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
        
        # 응답 데이터 구성
        response_data = {
            'id': user.id,
            'staff_id': staff_profile.id if staff_profile else None,
            'name': staff_profile.name if staff_profile else (user.name or user.username),
            'username': user.username,
            'position': staff_profile.position if staff_profile else (user.position or '직원'),
            'department': staff_profile.department if staff_profile else (user.department or '미지정'),
            'email': staff_profile.email if staff_profile else user.email,
            'phone': staff_profile.phone if staff_profile else user.phone,
            'join_date': staff_profile.join_date.strftime('%Y-%m-%d') if staff_profile and staff_profile.join_date else (user.created_at.strftime('%Y-%m-%d') if user.created_at else None),
            'status': user.status or 'active',
            'role': user.role,
            'is_active': user.is_active,
            'branch_id': user.branch_id,
            'branch_name': user.branch.name if user.branch else None,
            'salary': staff_profile.salary if staff_profile else None,
            'contracts': contracts,
            'health_certificates': health_certificates,
            'permissions': user.permissions or {},
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
            'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else None
        }
        
        current_app.logger.info(f"직원 상세 조회 성공: user_id={user.id}")
        
        return jsonify({
            'success': True,
            'staff': response_data
        })
    
    except Exception as e:
        current_app.logger.error(f"직원 상세 조회 오류: {str(e)}")
        return jsonify({'error': f'직원 상세 조회에 실패했습니다: {str(e)}'}), 500

@staff_bp.route('/staff/<int:staff_id>/documents', methods=['GET'])
@login_required
def get_staff_documents(staff_id):
    """직원 서류 상세 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        user = User.query.get_or_404(staff_id)
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and user.branch_id != current_user.branch_id:
            current_app.logger.warning(f"매장 접근 권한 없음: user_branch={user.branch_id}, current_branch={current_user.branch_id}")
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
        return jsonify({'error': f'서류 조회에 실패했습니다: {str(e)}'}), 500

@staff_bp.route('/staff/expiring-documents', methods=['GET'])
# @login_required  # 임시로 인증 우회 (테스트용)
def get_expiring_documents():
    """만료 임박 서류 조회"""
    try:
        # 권한 확인 (인증되지 않은 사용자 처리)
        if current_user.is_authenticated:
            if not current_user.has_permission('employee_management', 'view'):
                current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
                return jsonify({'error': '권한이 없습니다.'}), 403
        else:
            current_app.logger.info("인증되지 않은 사용자 접근 - 테스트 모드")
        
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
        return jsonify({'error': f'만료 임박 서류 조회에 실패했습니다: {str(e)}'}), 500

@staff_bp.route('/staff/documents/<int:document_id>/download/<document_type>', methods=['GET'])
@login_required
def download_document(document_id, document_type):
    """서류 파일 다운로드"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
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

@staff_bp.route('/staff', methods=['POST'])
@login_required
def create_staff():
    """새 직원 추가"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'create'):
            current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.form.to_dict()
        
        # 필수 필드 검증
        required_fields = ['name', 'position', 'department', 'email', 'phone', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}은(는) 필수 입력 항목입니다.'}), 400
        
        # 사용자명 중복 확인
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': '이미 사용 중인 사용자명입니다.'}), 400
        
        # 이메일 중복 확인
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': '이미 사용 중인 이메일입니다.'}), 400
        
        # 새 사용자 생성
        new_user = User()
        new_user.username = data['username']
        new_user.email = data['email']
        new_user.set_password(data['password'])
        new_user.role = data.get('role', 'employee')
        new_user.status = data.get('status', 'pending')
        new_user.branch_id = current_user.branch_id
        new_user.position = data['position']
        new_user.department = data['department']
        
        # 권한 설정
        if data.get('permissions'):
            new_user.permissions = json.loads(data['permissions'])
        
        db.session.add(new_user)
        db.session.flush()  # ID 생성
        
        # 직원 프로필 생성
        staff_profile = Staff()
        staff_profile.name = data['name']
        staff_profile.position = data['position']
        staff_profile.department = data['department']
        staff_profile.email = data['email']
        staff_profile.phone = data['phone']
        staff_profile.join_date = datetime.strptime(data.get('join_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        staff_profile.salary = data.get('salary', '2500000')
        staff_profile.your_program_id = current_user.branch_id
        staff_profile.user_id = new_user.id
        
        db.session.add(staff_profile)
        db.session.flush()  # ID 생성
        
        # 계약서 정보가 있으면 추가
        if data.get('contract_start_date') and data.get('contract_expiry_date'):
            contract = Contract()
            contract.staff_id = staff_profile.id
            contract.contract_number = f"CT-{datetime.now().year}-{new_user.id:03d}"
            contract.start_date = datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date()
            contract.expiry_date = datetime.strptime(data['contract_expiry_date'], '%Y-%m-%d').date()
            contract.renewal_date = datetime.strptime(data['contract_expiry_date'], '%Y-%m-%d').date()
            contract.contract_type = data.get('contract_type', '정규직')
            contract.salary_amount = int(data.get('salary', 2500000))
            
            # 계약서 파일 업로드 처리
            if 'contract_file' in request.files:
                file_info = save_file(request.files['contract_file'], 'contracts')
                if file_info:
                    contract.file_path = file_info['file_path']
                    contract.file_name = file_info['original_filename']
                    contract.file_size = file_info['file_size']
            
            db.session.add(contract)
        
        # 보건증 정보가 있으면 추가
        if data.get('health_certificate_issue_date') and data.get('health_certificate_expiry_date'):
            health_cert = HealthCertificate()
            health_cert.staff_id = staff_profile.id
            health_cert.certificate_number = f"HC-{datetime.now().year}-{new_user.id:03d}"
            health_cert.issue_date = datetime.strptime(data['health_certificate_issue_date'], '%Y-%m-%d').date()
            health_cert.expiry_date = datetime.strptime(data['health_certificate_expiry_date'], '%Y-%m-%d').date()
            health_cert.renewal_date = datetime.strptime(data['health_certificate_expiry_date'], '%Y-%m-%d').date()
            health_cert.issuing_authority = data.get('issuing_authority', '서울시보건소')
            health_cert.certificate_type = data.get('health_certificate_type', '일반보건증')
            
            # 보건증 파일 업로드 처리
            if 'health_certificate_file' in request.files:
                file_info = save_file(request.files['health_certificate_file'], 'health_certificates')
                if file_info:
                    health_cert.file_path = file_info['file_path']
                    health_cert.file_name = file_info['original_filename']
                    health_cert.file_size = file_info['file_size']
            
            db.session.add(health_cert)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 추가되었습니다.',
            'staff_id': staff_profile.id,
            'user_id': new_user.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"직원 추가 오류: {str(e)}")
        return jsonify({'error': f'직원 추가에 실패했습니다: {str(e)}'}), 500

@staff_bp.route('/staff/<int:staff_id>', methods=['PUT'])
@login_required
def update_staff(staff_id):
    """직원 정보 수정"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'edit'):
            current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        user = User.query.get_or_404(staff_id)
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and user.branch_id != current_user.branch_id:
            current_app.logger.warning(f"매장 접근 권한 없음: user_branch={user.branch_id}, current_branch={current_user.branch_id}")
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

@staff_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
@login_required
def delete_staff(staff_id):
    """직원 삭제"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'delete'):
            current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        user = User.query.get_or_404(staff_id)
        
        # 매장별 접근 권한 확인
        if not current_user.is_admin() and user.branch_id != current_user.branch_id:
            current_app.logger.warning(f"매장 접근 권한 없음: user_branch={user.branch_id}, current_branch={current_user.branch_id}")
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

@staff_bp.route('/staff-stats', methods=['GET'])
@login_required
def staff_stats():
    """직원 통계 API"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
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

@staff_bp.route('/staff-status', methods=['GET'])
@login_required
def staff_status():
    """직원 현황 API"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            current_app.logger.warning(f"권한 없음: user_id={current_user.id}")
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

@staff_bp.route('/staff/pending', methods=['GET'])
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
                'username': user.username,
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

@staff_bp.route('/staff/<int:staff_id>/approve', methods=['POST'])
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
        log = ApproveLog()
        log.user_id = user.id
        log.action = 'approved'
        log.admin_id = current_user.id
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'message': '직원이 승인되었습니다.'})
    except Exception as e:
        current_app.logger.error(f"직원 승인 오류: {str(e)}")
        return jsonify({'error': '직원 승인에 실패했습니다.'}), 500

@staff_bp.route('/staff/<int:staff_id>/reject', methods=['POST'])
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
        log = ApproveLog()
        log.user_id = user.id
        log.action = 'rejected'
        log.admin_id = current_user.id
        log.reason = reason
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'message': '직원이 거절되었습니다.'})
    except Exception as e:
        current_app.logger.error(f"직원 거절 오류: {str(e)}")
        return jsonify({'error': '직원 거절에 실패했습니다.'}), 500

# 더미 데이터 함수 제거 - 실제 데이터베이스에서 조회하도록 변경 
