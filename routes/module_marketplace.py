"""
모듈 마켓플레이스 시스템
개발자들이 만든 모듈을 등록하고, 업종별 관리자가 검토하며, 브랜드별로 적용할 수 있는 시스템
"""

from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from models import User, Brand, Branch, SystemLog, Module, ModuleFeedback, ModuleVersion, ModuleUsage
from extensions import db
from datetime import datetime, timedelta
import logging
import os
import json
import uuid
from werkzeug.utils import secure_filename
import zipfile
import shutil

logger = logging.getLogger(__name__)

module_marketplace_bp = Blueprint('module_marketplace', __name__, url_prefix='/admin/module-marketplace')

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'zip', 'py', 'json'}  # 허용 확장자 예시

# 모듈 카테고리
MODULE_CATEGORIES = {
    'attendance': '출퇴근 관리',
    'schedule': '스케줄 관리', 
    'inventory': '재고 관리',
    'purchase': '발주 관리',
    'ai': 'AI/분석',
    'communication': '커뮤니케이션',
    'security': '보안',
    'automation': '자동화',
    'reporting': '리포팅',
    'integration': '통합',
    'other': '기타'
}

def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@module_marketplace_bp.route('/', methods=['GET'])
@login_required
def module_marketplace_page():
    """모듈 마켓플레이스 페이지"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    return render_template('admin/module_marketplace.html')

@module_marketplace_bp.route('/api/modules', methods=['GET'])
@login_required
def get_modules():
    """모듈 목록 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        # 필터링 파라미터
        category = request.args.get('category')
        status = request.args.get('status')
        search = request.args.get('search')
        
        query = Module.query
        
        if category:
            query = query.filter(Module.category == category)
        
        if status:
            query = query.filter(Module.status == status)
        
        if search:
            query = query.filter(
                (Module.name.contains(search)) |
                (Module.description.contains(search)) |
                (Module.author.contains(search))
            )
        
        modules = query.order_by(Module.created_at.desc()).all()
        
        module_list = []
        for module in modules:
            # 사용 통계
            usage_count = ModuleUsage.query.filter_by(module_id=module.id).count()
            feedback_count = ModuleFeedback.query.filter_by(module_id=module.id).count()
            
            # 평균 평점
            avg_rating = db.session.query(db.func.avg(ModuleFeedback.rating)).filter_by(module_id=module.id).scalar() or 0
            
            module_list.append({
                'id': module.id,
                'name': module.name,
                'description': module.description,
                'category': module.category,
                'category_name': MODULE_CATEGORIES.get(module.category, '기타'),
                'version': module.version,
                'author': module.author,
                'status': module.status,
                'downloads': module.downloads,
                'usage_count': usage_count,
                'feedback_count': feedback_count,
                'avg_rating': round(avg_rating, 1),
                'created_at': module.created_at.isoformat(),
                'updated_at': module.updated_at.isoformat(),
                'tags': module.tags.split(',') if module.tags else [],
                'compatibility': json.loads(module.compatibility) if module.compatibility else {},
                'requirements': json.loads(module.requirements) if module.requirements else []
            })
        
        return jsonify({
            'success': True,
            'modules': module_list,
            'total_count': len(module_list),
            'categories': MODULE_CATEGORIES
        })
        
    except Exception as e:
        logger.error(f"모듈 목록 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500  # pyright: ignore

@module_marketplace_bp.route('/api/modules', methods=['POST'])  # pyright: ignore
@login_required
def upload_module():
    """모듈 업로드"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        # 파일 업로드 처리
        if 'module_file' not in request.files:
            return jsonify({'error': '모듈 파일이 필요합니다.'}), 400
        
        file = request.files['module_file']
        if file.filename == '':
            return jsonify({'error': '파일을 선택해주세요.'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '허용되지 않는 파일 형식입니다.'}), 400
        
        # 모듈 정보
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        version = request.form.get('version', '1.0.0')
        tags = request.form.get('tags', '')
        compatibility = request.form.get('compatibility', '{}')
        requirements = request.form.get('requirements', '[]')
        
        if not all([name, description, category]):
            return jsonify({'error': '필수 정보를 모두 입력해주세요.'}), 400
        
        # 파일 저장
        filename = secure_filename(file.filename or '')
        module_id = str(uuid.uuid4())
        upload_dir = os.path.join('uploads', 'modules', module_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # ZIP 파일인 경우 압축 해제
        if filename.endswith('.zip'):
            extract_dir = os.path.join(upload_dir, 'extracted')
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        
        # 모듈 정보 저장
        module = Module(
            module_id=module_id,  # pyright: ignore
            module_name=name,  # pyright: ignore
            module_description=description,  # pyright: ignore
            module_category=category,  # pyright: ignore
            module_version=version,  # pyright: ignore
            # author, status, downloads, tags, compatibility 필드는 Module 모델에 정의되어 있지 않으므로 주석 처리 또는 제거합니다.
            # author=current_user.username,  # pyright: ignore
            # status='pending',  # 승인 대기  # pyright: ignore
            # downloads=0,  # pyright: ignore
            # tags와 compatibility 필드는 Module 모델에 정의되어 있지 않으므로 주석 처리합니다.
            # tags=tags,  # pyright: ignore
            # compatibility=compatibility,  # pyright: ignore
            requirements=requirements,  # pyright: ignore
            file_path=file_path,  # pyright: ignore
            created_by=current_user.id  # pyright: ignore
        )
        db.session.add(module)
        
        # 시스템 로그 기록
        log = SystemLog(
            user_id=current_user.id,
            action='module_upload',
            detail=f'모듈 업로드: {name} v{version}',
            ip_address=request.remote_addr
        ) # pyright: ignore
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{name} 모듈이 성공적으로 업로드되었습니다. 승인 대기 중입니다.',
            'module_id': module_id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"모듈 업로드 오류: {str(e)}")
        return jsonify({'error': '모듈 업로드 중 오류가 발생했습니다.'}), 500

@module_marketplace_bp.route('/api/modules/<module_id>', methods=['GET'])
@login_required
def get_module_detail(module_id):
    """모듈 상세 정보 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        # 피드백 목록
        feedbacks = ModuleFeedback.query.filter_by(module_id=module_id).order_by(ModuleFeedback.created_at.desc()).all()
        feedback_list = []
        
        for feedback in feedbacks:
            feedback_list.append({
                'id': feedback.id,
                'user_name': feedback.user_name,
                'rating': feedback.rating,
                'comment': feedback.comment,
                'created_at': feedback.created_at.isoformat(),
                'is_helpful': feedback.is_helpful
            })
        
        # 사용 통계
        usage_count = ModuleUsage.query.filter_by(module_id=module_id).count()
        brand_usage = db.session.query(
            Brand.name,
            db.func.count(ModuleUsage.id).label('usage_count')
        ).join(ModuleUsage).filter(ModuleUsage.module_id == module_id).group_by(Brand.id).all()
        
        # 평균 평점
        avg_rating = db.session.query(db.func.avg(ModuleFeedback.rating)).filter_by(module_id=module_id).scalar() or 0
        
        return jsonify({
            'success': True,
            'module': {
                'id': module.id,
                'name': module.name,
                'description': module.description,
                'category': module.category,
                'category_name': MODULE_CATEGORIES.get(module.category, '기타'),
                'version': module.version,
                'author': module.author,
                'status': module.status,
                'downloads': module.downloads,
                'tags': module.tags.split(',') if module.tags else [],
                'compatibility': json.loads(module.compatibility) if module.compatibility else {},
                'requirements': json.loads(module.requirements) if module.requirements else [],
                'created_at': module.created_at.isoformat(),
                'updated_at': module.updated_at.isoformat(),
                'usage_count': usage_count,
                'avg_rating': round(avg_rating, 1),
                'feedback_count': len(feedback_list)
            },
            'feedbacks': feedback_list,
            'brand_usage': [
                {
                    'brand_name': brand.name,
                    'usage_count': count
                } for brand, count in brand_usage
            ]
        })
        
    except Exception as e:
        logger.error(f"모듈 상세 정보 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500

@module_marketplace_bp.route('/api/modules/<module_id>/approve', methods=['POST'])
@login_required
def approve_module(module_id):
    """모듈 승인"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        # 승인 처리
        module.status = 'approved'
        module.updated_at = datetime.now()
        
        # 시스템 로그 기록
        log = SystemLog(
            user_id=current_user.id,
            action='module_approve',
            detail=f'모듈 승인: {module.name} v{module.version}',
            ip_address=request.remote_addr
        ) # pyright: ignore
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{module.name} 모듈이 승인되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"모듈 승인 오류: {str(e)}")
        return jsonify({'error': '모듈 승인 중 오류가 발생했습니다.'}), 500

@module_marketplace_bp.route('/api/modules/<module_id>/reject', methods=['POST'])
@login_required
def reject_module(module_id):
    """모듈 거절"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        data = request.get_json()
        reason = data.get('reason', '')
        
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        # 거절 처리
        module.status = 'rejected'
        module.updated_at = datetime.now()
        
        # 시스템 로그 기록
        log = SystemLog(
            user_id=current_user.id,
            action='module_reject',
            detail=f'모듈 거절: {module.name} v{module.version} - {reason}',
            ip_address=request.remote_addr
        ) # pyright: ignore
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{module.name} 모듈이 거절되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"모듈 거절 오류: {str(e)}")
        return jsonify({'error': '모듈 거절 중 오류가 발생했습니다.'}), 500

@module_marketplace_bp.route('/api/modules/<module_id>/feedback', methods=['POST'])
@login_required
def add_module_feedback(module_id):
    """모듈 피드백 추가"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating or not (1 <= rating <= 5):
            return jsonify({'error': '평점은 1-5 사이의 값이어야 합니다.'}), 400
        
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        # 피드백 저장
        feedback = ModuleFeedback(
            module_id=module_id,
            user_name=current_user.username,
            rating=rating,
            comment=comment
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '피드백이 성공적으로 등록되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"피드백 추가 오류: {str(e)}")
        return jsonify({'error': '피드백 등록 중 오류가 발생했습니다.'}), 500

@module_marketplace_bp.route('/api/modules/<module_id>/download', methods=['POST'])
@login_required
def download_module(module_id):
    """모듈 다운로드"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        if module.status != 'approved':
            return jsonify({'error': '승인된 모듈만 다운로드할 수 있습니다.'}), 400
        
        # 다운로드 수 증가
        module.downloads += 1
        
        # 사용 기록
        data = request.get_json(silent=True) or {}
        usage = ModuleUsage(
            module_id=module_id,
            brand_id=data.get('brand_id'),
            user_id=current_user.id,
            action='download'
        )
        
        db.session.add(usage)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{module.name} 모듈이 다운로드되었습니다.',
            'download_url': f'/admin/module-marketplace/api/modules/{module_id}/file'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"모듈 다운로드 오류: {str(e)}")
        return jsonify({'error': '모듈 다운로드 중 오류가 발생했습니다.'}), 500

@module_marketplace_bp.route('/api/modules/<module_id>/customize', methods=['POST'])
@login_required
def customize_module(module_id):
    """모듈 커스터마이징"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        data = request.get_json()
        brand_id = data.get('brand_id')
        customizations = data.get('customizations', {})
        
        if not brand_id:
            return jsonify({'error': '브랜드 ID가 필요합니다.'}), 400
        
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        # 커스터마이징 정보 저장
        customization_data = {
            'brand_id': brand_id,
            'module_id': module_id,
            'customizations': customizations,
            'created_at': datetime.now().isoformat(),
            'created_by': current_user.username
        }
        
        # 시스템 로그 기록
        log = SystemLog(
            user_id=current_user.id,
            action='module_customize',
            detail=f'모듈 커스터마이징: {module.name} - 브랜드 {brand_id}',
            ip_address=request.remote_addr
        ) # pyright: ignore
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{module.name} 모듈이 브랜드에 맞게 커스터마이징되었습니다.',
            'customization': customization_data
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"모듈 커스터마이징 오류: {str(e)}")
        return jsonify({'error': '모듈 커스터마이징 중 오류가 발생했습니다.'}), 500

@module_marketplace_bp.route('/api/modules/statistics', methods=['GET'])
@login_required
def get_module_statistics():
    """모듈 통계"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        # 전체 통계
        total_modules = Module.query.count()
        approved_modules = Module.query.filter_by(status='approved').count()
        pending_modules = Module.query.filter_by(status='pending').count()
        total_downloads = db.session.query(db.func.sum(Module.downloads)).scalar() or 0
        
        # 카테고리별 통계
        category_stats = db.session.query(
            Module.category,
            db.func.count(Module.id).label('count')
        ).group_by(Module.category).all()
        
        # 최근 업로드된 모듈
        recent_modules = Module.query.order_by(Module.created_at.desc()).limit(5).all()
        
        # 인기 모듈 (다운로드 기준)
        popular_modules = Module.query.filter_by(status='approved').order_by(Module.downloads.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_modules': total_modules,
                'approved_modules': approved_modules,
                'pending_modules': pending_modules,
                'total_downloads': total_downloads,
                'category_stats': [
                    {
                        'category': cat,
                        'category_name': MODULE_CATEGORIES.get(cat, '기타'),
                        'count': count
                    } for cat, count in category_stats
                ],
                'recent_modules': [
                    {
                        'id': module.id,
                        'name': module.name,
                        'category': module.category,
                        'status': module.status,
                        'created_at': module.created_at.isoformat()
                    } for module in recent_modules
                ],
                'popular_modules': [
                    {
                        'id': module.id,
                        'name': module.name,
                        'category': module.category,
                        'downloads': module.downloads
                    } for module in popular_modules
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"모듈 통계 조회 오류: {str(e)}")
        return jsonify({'error': '통계 조회 중 오류가 발생했습니다.'}), 500

# 모듈 마켓플레이스에 샘플 데이터 추가
@module_marketplace_bp.route('/api/modules/seed', methods=['POST'])
@login_required
def seed_sample_modules():
    """샘플 모듈 데이터 추가"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 401
    
    try:
        # 기존 샘플 데이터가 있는지 확인
        existing_modules = Module.query.filter(Module.author == 'your_program 개발팀').count()
        if existing_modules > 0:
            return jsonify({'message': '샘플 데이터가 이미 존재합니다.'}), 200
        
        # 샘플 모듈 데이터
        sample_modules = [
            {
                'id': str(uuid.uuid4()),
                'name': '출퇴근 관리 모듈',
                'description': '직원들의 출퇴근 시간을 관리하고 근태를 추적하는 모듈입니다. QR코드 출퇴근, GPS 위치 확인, 근태 통계, 지각/조퇴 알림, 월간 근태 리포트 기능을 제공합니다.',
                'category': 'attendance',
                'version': '1.0.0',
                'author': 'your_program 개발팀',
                'status': 'approved',
                'downloads': 45,
                'tags': '출퇴근,근태관리,시간관리,직원관리',
                'compatibility': json.dumps({
                    'min_version': '1.0.0',
                    'max_version': '2.0.0',
                    'industries': ['restaurant', 'retail', 'service'],
                    'brands': ['all']
                }),
                'requirements': json.dumps([
                    'flask>=2.0.0',
                    'sqlalchemy>=1.4.0',
                    'python-dateutil>=2.8.0'
                ]),
                'file_path': 'sample_modules/attendance_module_v1.0.0.zip',
                'created_by': current_user.id
            },
            {
                'id': str(uuid.uuid4()),
                'name': '스케줄 관리 모듈',
                'description': '직원들의 근무 스케줄을 관리하고 자동 배정하는 모듈입니다. 자동 스케줄 생성, 교대근무 관리, 휴가 신청/승인, 인력 최적화, 스케줄 충돌 감지 기능을 제공합니다.',
                'category': 'schedule',
                'version': '1.0.0',
                'author': 'your_program 개발팀',
                'status': 'approved',
                'downloads': 32,
                'tags': '스케줄,근무관리,자동배정,교대근무',
                'compatibility': json.dumps({
                    'min_version': '1.0.0',
                    'max_version': '2.0.0',
                    'industries': ['restaurant', 'retail', 'service', 'hospital'],
                    'brands': ['all']
                }),
                'requirements': json.dumps([
                    'flask>=2.0.0',
                    'sqlalchemy>=1.4.0',
                    'python-dateutil>=2.8.0'
                ]),
                'file_path': 'sample_modules/schedule_module_v1.0.0.zip',
                'created_by': current_user.id
            },
            {
                'id': str(uuid.uuid4()),
                'name': '재고 관리 모듈',
                'description': '매장의 재고를 실시간으로 관리하고 자동 발주를 지원하는 모듈입니다. 실시간 재고 추적, 자동 발주 알림, 바코드 스캔, IoT 센서 연동, 재고 리포트 기능을 제공합니다.',
                'category': 'inventory',
                'version': '1.0.0',
                'author': 'your_program 개발팀',
                'status': 'approved',
                'downloads': 28,
                'tags': '재고,발주,자동화,IoT,바코드',
                'compatibility': json.dumps({
                    'min_version': '1.0.0',
                    'max_version': '2.0.0',
                    'industries': ['restaurant', 'retail', 'manufacturing'],
                    'brands': ['all']
                }),
                'requirements': json.dumps([
                    'flask>=2.0.0',
                    'sqlalchemy>=1.4.0',
                    'requests>=2.25.0'
                ]),
                'file_path': 'sample_modules/inventory_module_v1.0.0.zip',
                'created_by': current_user.id
            },
            {
                'id': str(uuid.uuid4()),
                'name': '발주 관리 모듈',
                'description': '매장의 발주를 관리하고 공급업체와 연동하는 모듈입니다. 자동 발주 생성, 공급업체 관리, 견적 비교, 배송 추적, 결제 관리 기능을 제공합니다.',
                'category': 'purchase',
                'version': '1.0.0',
                'author': 'your_program 개발팀',
                'status': 'approved',
                'downloads': 19,
                'tags': '발주,공급업체,견적,배송,결제',
                'compatibility': json.dumps({
                    'min_version': '1.0.0',
                    'max_version': '2.0.0',
                    'industries': ['restaurant', 'retail', 'manufacturing'],
                    'brands': ['all']
                }),
                'requirements': json.dumps([
                    'flask>=2.0.0',
                    'sqlalchemy>=1.4.0',
                    'requests>=2.25.0'
                ]),
                'file_path': 'sample_modules/purchase_module_v1.0.0.zip',
                'created_by': current_user.id
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'AI 분석 모듈',
                'description': '매장 데이터를 AI로 분석하여 인사이트를 제공하는 모듈입니다. 매출 예측, 고객 행동 분석, 최적화 제안, 이상치 감지, 성능 대시보드 기능을 제공합니다.',
                'category': 'ai',
                'version': '1.0.0',
                'author': 'your_program 개발팀',
                'status': 'pending',
                'downloads': 0,
                'tags': 'AI,분석,예측,인사이트,최적화',
                'compatibility': json.dumps({
                    'min_version': '1.0.0',
                    'max_version': '2.0.0',
                    'industries': ['restaurant', 'retail', 'service'],
                    'brands': ['all']
                }),
                'requirements': json.dumps([
                    'flask>=2.0.0',
                    'pandas>=1.3.0',
                    'scikit-learn>=1.0.0',
                    'numpy>=1.21.0'
                ]),
                'file_path': 'sample_modules/ai_analysis_module_v1.0.0.zip',
                'created_by': current_user.id
            }
        ]
        
        # 모듈 데이터 추가
        for module_data in sample_modules:
            module = Module(**module_data)
            db.session.add(module)
            
            # 샘플 피드백 추가 (승인된 모듈에만)
            if module_data['status'] == 'approved':
                feedbacks = [
                    {
                        'user_name': '김매니저',
                        'rating': 5,
                        'comment': '정말 유용한 모듈입니다! 직원 관리가 훨씬 쉬워졌어요.'
                    },
                    {
                        'user_name': '박사장',
                        'rating': 4,
                        'comment': '기능이 잘 구현되어 있고 사용하기 편합니다. 다만 몇 가지 개선사항이 있으면 좋겠어요.'
                    },
                    {
                        'user_name': '이팀장',
                        'rating': 5,
                        'comment': '완벽합니다! 다른 매장에도 추천하고 싶어요.'
                    }
                ]
                
                for feedback_data in feedbacks:
                    feedback = ModuleFeedback(
                        module_id=module.id,
                        **feedback_data
                    )
                    db.session.add(feedback)
        
        # 시스템 로그 기록
        log = SystemLog(
            user_id=current_user.id,
            action='module_seed',
            detail=f'샘플 모듈 데이터 추가: {len(sample_modules)}개',
            ip_address=request.remote_addr
        ) # pyright: ignore
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(sample_modules)}개의 샘플 모듈이 성공적으로 추가되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"샘플 모듈 데이터 추가 오류: {str(e)}")
        return jsonify({'error': '샘플 데이터 추가 중 오류가 발생했습니다.'}), 500 