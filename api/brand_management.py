from models_main import Brand, Industry
from extensions import db, csrf
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import string
import random
import logging
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
브랜드 관리 API
브랜드 생성, 수정, 삭제, 조회 기능
"""


logger = logging.getLogger(__name__)

brand_management_bp = Blueprint('brand_management', __name__)


def generate_brand_code(industry_name,  brand_name):
    """업종별 브랜드 코드 자동 생성"""
    # 업종별 접두사 매핑
    industry_prefixes = {
        '음식점': 'REST',
        '카페': 'CAFE',
        '바': 'BAR',
        '고기집': 'BBQ',
        '편의점': 'CVS',
        '미용실': 'SALON',
        '병원': 'HOSP',
        '약국': 'PHARM',
        '옷가게': 'FASH',
        '기타': 'GEN'
    }

    # 업종 접두사 가져오기
    prefix = industry_prefixes.get(industry_name, 'BRAND')

    # 브랜드명에서 영문/숫자만 추출하여 3-5자리로 제한
    import re
    clean_name = re.sub(r'[^A-Za-z0-9]', '', brand_name.upper())
    if len(clean_name) > 5:
        clean_name = clean_name[:5]
    elif len(clean_name) < 3:
        clean_name = clean_name + ''.join(random.choices(string.ascii_uppercase, k=3-len(clean_name)))

    # 랜덤 숫자 3자리 추가
    random_num = ''.join(random.choices(string.digits, k=3))

    # 최종 브랜드 코드 생성
    brand_code = f"{prefix}_{clean_name}_{random_num}"

    return brand_code


def get_brand_code_suggestions(industry_name, brand_name):
    """브랜드 코드 제안 목록 생성"""
    suggestions = []

    # 업종별 접두사 매핑
    industry_prefixes = {
        '음식점': ['REST', 'FOOD', 'DINE'],
        '카페': ['CAFE', 'COFF', 'TEA'],
        '바': ['BAR', 'PUB', 'CLUB'],
        '고기집': ['BBQ', 'MEAT', 'GRILL'],
        '편의점': ['CVS', 'MART', 'STORE'],
        '미용실': ['SALON', 'BEAUTY', 'HAIR'],
        '병원': ['HOSP', 'MED', 'CLINIC'],
        '약국': ['PHARM', 'DRUG', 'MEDI'],
        '옷가게': ['FASH', 'CLOTH', 'STYLE'],
        '기타': ['GEN', 'BIZ', 'COMP']
    }

    prefixes = industry_prefixes.get(industry_name, ['BRAND'])

    for prefix in prefixes:
        # 브랜드명에서 영문/숫자만 추출
        import re
        clean_name = re.sub(r'[^A-Za-z0-9]', '', brand_name.upper())
        if len(clean_name) > 5:
            clean_name = clean_name[:5]
        elif len(clean_name) < 2:
            clean_name = clean_name + ''.join(random.choices(string.ascii_uppercase, k=2-len(clean_name)))

        # 여러 가지 조합 생성
        suggestions.append(f"{prefix}_{clean_name}")
        suggestions.append(f"{prefix}_{clean_name[:3]}")
        suggestions.append(f"{prefix}_{clean_name}_{random.randint(100, 999)}")

    return suggestions[:5]  # 최대 5개 제안


@brand_management_bp.route('/api/admin/brands/code-suggestions', methods=['POST'])
@csrf.exempt
@login_required
def get_brand_code_suggestions_api():
    """브랜드 코드 제안 API"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'create'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        industry_name = data.get('industry_name', '기타')
        brand_name = data.get('brand_name', '')

        if not brand_name:
            return jsonify({'error': '브랜드명이 필요합니다.'}), 400

        suggestions = get_brand_code_suggestions(industry_name,  brand_name)

        return jsonify({
            'suggestions': suggestions,
            'auto_generated': generate_brand_code(industry_name,  brand_name)
        })

    except Exception as e:
        logger.error(f"브랜드 코드 제안 생성 실패: {e}")
        return jsonify({'error': '브랜드 코드 제안 생성에 실패했습니다.'}), 500


@brand_management_bp.route('/api/admin/industries', methods=['GET'])
@login_required
def get_industries():
    """업종 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        industries = Industry.query.filter_by(is_active=True).all()

        return jsonify({
            'industries': [
                {
                    'id': industry.id,
                    'name': industry.name,
                    'code': industry.code,
                    'description': industry.description
                }
                for industry in industries
            ]
        })

    except Exception as e:
        logger.error(f"업종 목록 조회 실패: {e}")
        return jsonify({'error': '업종 목록 조회에 실패했습니다.'}), 500


@brand_management_bp.route('/brands', methods=['POST'])
@login_required
def create_brand():
    """
    브랜드 생성 시 샘플 매장/직원/계약 등 기본 데이터 자동 생성 (초보자/운영자 주석)
    """
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'create'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400

        # 브랜드 코드 처리
        brand_code = data.get('code')
        if not brand_code:
            # 자동 생성
            industry_name = data.get('industry_name', '기타')
            brand_code = generate_brand_code(industry_name,  data['name'])

        # 브랜드 코드 중복 확인
        existing_brand = Brand.query.filter_by(code=brand_code).first()
        if existing_brand:
            return jsonify({'error': '이미 존재하는 브랜드 코드입니다.'}), 400

        # 업종 ID 가져오기
        industry_id = None
        if data.get('industry_name'):
            industry = Industry.query.filter_by(name=data['industry_name']).first()
            if industry:
                industry_id = industry.id

        # 브랜드 생성
        new_brand = Brand(
            name=data['name'],
            code=brand_code,
            description=data.get('description', ''),
            logo_url=data.get('logo_url', ''),
            website=data.get('website', ''),
            contact_email=data.get('contact_email', ''),
            contact_phone=data.get('contact_phone', ''),
            address=data.get('address', ''),
            industry_id=industry_id,
            status='active'
        )
        db.session.add(new_brand)
        db.session.commit()  # brand_id 확보

        # 샘플 매장(지점) 1~2개 자동 생성
        from models_main import Branch, User, Contract
        sample_stores = [
            Branch(name=f"{new_brand.name} 1호점", address="서울시 강남구", brand_id=new_brand.id),
            Branch(name=f"{new_brand.name} 2호점", address="서울시 서초구", brand_id=new_brand.id),
        ]
        db.session.add_all(sample_stores)
        db.session.commit()

        # 샘플 직원 자동 생성 (브랜드 관리자, 매장 직원)
        admin_user = User(
            username=f"{new_brand.name.lower()}_admin",
            name=f"{new_brand.name} 관리자",
            email=f"{new_brand.name.lower()}_admin@brand.com",
            role="brand_manager",
            brand_id=new_brand.id,
            status="approved",
            is_active=True,
        )
        admin_user.set_password("sample1234")
        db.session.add(admin_user)
        # 매장 직원
        for store in sample_stores:
            staff = User(
                username=f"{store.name.lower()}_staff",
                name=f"{store.name} 직원",
                email=f"{store.name.lower()}_staff@brand.com",
                role="employee",
                brand_id=new_brand.id,
                branch_id=store.id,
                status="approved",
                is_active=True,
            )
            staff.set_password("sample1234")
            db.session.add(staff)
        db.session.commit()

        # 샘플 계약/메뉴 등 추가 가능 (필요시)
        # contract = Contract(...)
        # db.session.add(contract)
        # db.session.commit()

        # 브랜드별 관리자 권한/메뉴/기본 데이터 자동 생성
        try:
            from core.backend.menu_integration_system import assign_brand_admin_and_menu
            assign_brand_admin_and_menu(new_brand)
        except Exception as e:
            logger.warning(f"브랜드 권한/메뉴 자동 생성 실패: {e}")

        # 프론트엔드 서버 생성 (선택적)
        frontend_result = None
        if data.get('create_frontend_server', False):
            try:
                from core.backend.brand_management_system import BrandManagementSystem
                bms = BrandManagementSystem()
                frontend_result = bms.create_frontend_server(
                    brand_code,
                    data['name'],
                    3001
                )
            except Exception as e:
                logger.error(f"프론트엔드 서버 생성 실패: {e}")
                frontend_result = {'error': str(e)}

        # 온보딩 시작
        try:
            from api.brand_onboarding_api import start_onboarding
            onboarding_response = start_onboarding(new_brand.id)
            onboarding_data = onboarding_response.get_json() if hasattr(onboarding_response, 'get_json') else None
        except Exception as e:
            logger.error(f"온보딩 시작 실패: {e}")
            onboarding_data = None

        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 생성되었습니다.',
            'brand': {
                'id': new_brand.id,
                'name': new_brand.name,
                'code': new_brand.code,
                'industry_id': new_brand.industry_id
            },
            'frontend_server': frontend_result,
            'onboarding': onboarding_data
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        tb = traceback.format_exc()
        current_app.logger.error(f"브랜드 생성 오류: {str(e)}\n{tb}")
        return jsonify({'error': f'브랜드 생성 중 오류: {str(e)}', 'traceback': tb}), 500


@brand_management_bp.route('/brands', methods=['GET'])
@login_required
def get_brands():
    """브랜드 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        brands = Brand.query.all()

        return jsonify({
            'brands': [
                {
                    'id': brand.id,
                    'name': brand.name,
                    'code': brand.code,
                    'description': brand.description,
                    'status': brand.status,
                    'created_at': brand.created_at.isoformat() if brand.created_at else None
                }
                for brand in brands
            ]
        })

    except Exception as e:
        logger.error(f"브랜드 목록 조회 실패: {e}")
        return jsonify({'error': '브랜드 목록 조회에 실패했습니다.'}), 500


@brand_management_bp.route('/brands/<int:brand_id>', methods=['GET'])
@login_required
def get_brand(brand_id):
    """브랜드 상세 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        brand = Brand.query.get_or_404(brand_id)

        return jsonify({
            'brand': {
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'description': brand.description,
                'logo_url': brand.logo_url,
                'website': brand.website,
                'contact_email': brand.contact_email,
                'contact_phone': brand.contact_phone,
                'address': brand.address,
                'industry_id': brand.industry_id,
                'status': brand.status,
                'created_at': brand.created_at.isoformat() if brand.created_at else None,
                'updated_at': brand.updated_at.isoformat() if brand.updated_at else None
            }
        })

    except Exception as e:
        logger.error(f"브랜드 상세 조회 실패: {e}")
        return jsonify({'error': '브랜드 상세 조회에 실패했습니다.'}), 500


@brand_management_bp.route('/brands/<int:brand_id>', methods=['PUT'])
@login_required
def update_brand(brand_id):
    """브랜드 수정"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'edit'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        brand = Brand.query.get_or_404(brand_id)
        data = request.get_json()

        # 업데이트 가능한 필드들
        updatable_fields = [
            'name', 'description', 'logo_url', 'website',
            'contact_email', 'contact_phone', 'address', 'status'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(brand, field, data[field])

        brand.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 수정되었습니다.',
            'brand': {
                'id': brand.id,
                'name': brand.name,
                'code': brand.code
            }
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"브랜드 수정 실패: {e}")
        return jsonify({'error': '브랜드 수정에 실패했습니다.'}), 500


@brand_management_bp.route('/brands/<int:brand_id>', methods=['DELETE'])
@login_required
def delete_brand(brand_id):
    """브랜드 삭제"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'delete'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        brand = Brand.query.get_or_404(brand_id)

        # 브랜드에 연결된 매장이나 사용자가 있는지 확인
        if brand.stores or brand.brand_manager:
            return jsonify({'error': '연결된 매장이나 사용자가 있어 삭제할 수 없습니다.'}), 400

        db.session.delete(brand)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 삭제되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"브랜드 삭제 실패: {e}")
        return jsonify({'error': '브랜드 삭제에 실패했습니다.'}), 500

# --- [자동화] 브랜드별 관리자 권한/메뉴/기본 데이터 자동 생성 더미 함수 (실제 구현 필요) ---
def assign_brand_admin_and_menu(brand):
    """
    신규 브랜드 생성 시 관리자 권한/메뉴/기본 데이터 자동 생성 (실제 구현 필요)
    """
    # TODO: 실제 권한/메뉴/기본 데이터 생성 로직 구현
    pass
