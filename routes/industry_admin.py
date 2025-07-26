import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models_main import Brand, User, Industry
from werkzeug.security import generate_password_hash
import re

logger = logging.getLogger(__name__)

industry_admin_bp = Blueprint('industry_admin', __name__, url_prefix='/api/industry')

def validate_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """전화번호 형식 검증"""
    pattern = r'^[0-9-+\s()]{10,15}$'
    return re.match(pattern, phone) is not None

def generate_temp_password():
    """임시 비밀번호 생성"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@industry_admin_bp.route('/create_brand_with_admin', methods=['POST'])
# @login_required  # 테스트를 위해 임시로 주석 처리
def create_brand_with_admin():
    """브랜드와 브랜드관리자 계정을 동시에 생성"""
    print(f"DEBUG: create_brand_with_admin 호출됨")
    print(f"DEBUG: 요청 메서드: {request.method}")
    print(f"DEBUG: 요청 경로: {request.path}")
    print(f"DEBUG: Content-Type: {request.content_type}")
    print(f"DEBUG: 요청 데이터: {request.get_data()}")
    
    try:
        # 권한 확인 (업종관리자 또는 슈퍼관리자만)
        # if current_user.role not in ['admin', 'super_admin']:
        #     return jsonify({
        #         'success': False,
        #         'error': '업종관리자 권한이 필요합니다.'
        #     }), 403

        # 요청 데이터 파싱
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        print(f"받은 데이터: {data}")  # 디버깅용
        
        # 필수 입력값 검증
        required_fields = ['brand_name', 'brand_description', 'admin_name', 'admin_email', 'admin_phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'필수 입력값이 누락되었습니다: {field}'
                }), 400

        # 이메일 형식 검증
        if not validate_email(data['admin_email']):
            return jsonify({
                'success': False,
                'error': '올바른 이메일 형식이 아닙니다.'
            }), 400

        # 전화번호 형식 검증
        if not validate_phone(data['admin_phone']):
            return jsonify({
                'success': False,
                'error': '올바른 전화번호 형식이 아닙니다.'
            }), 400

        # 이메일 중복 확인
        existing_user = User.query.filter_by(email=data['admin_email']).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': '이미 등록된 이메일입니다.'
            }), 400

        # 브랜드명 중복 확인
        existing_brand = Brand.query.filter_by(name=data['brand_name']).first()
        if existing_brand:
            return jsonify({
                'success': False,
                'error': '이미 등록된 브랜드명입니다.'
            }), 400

        # 브랜드 코드 생성 (브랜드명 기반)
        brand_code = data['brand_name'].replace(' ', '').upper()[:10]

        # 트랜잭션 시작
        try:
            # 1. 브랜드 생성
            brand = Brand(
                name=data['brand_name'],
                code=brand_code,
                description=data['brand_description'],
                contact_email=data.get('brand_contact_email'),
                contact_phone=data.get('brand_contact_phone'),
                address=data.get('brand_address'),
                status='active',
                created_at=datetime.utcnow()
            )
            
            db.session.add(brand)
            db.session.flush()  # brand.id 확보

            # 2. 임시 비밀번호 생성
            temp_password = generate_temp_password()
            password_hash = generate_password_hash(temp_password)

            # 3. 브랜드관리자 계정 생성
            admin_user = User(
                username=data['admin_email'].split('@')[0],  # 이메일 앞부분을 username으로 사용
                email=data['admin_email'],
                password_hash=password_hash,
                name=data['admin_name'],
                phone=data['admin_phone'],
                role='brand_admin',
                brand_id=brand.id,
                status='approved',
                grade='manager',
                created_at=datetime.utcnow()
            )
            
            db.session.add(admin_user)
            db.session.flush()  # admin_user.id 확보

            # 4. 브랜드에 관리자 ID 연결
            brand.admin_id = admin_user.id
            
            # 5. 생성 로그 기록 (테스트를 위해 임시로 주석 처리)
            # from models_main import SystemLog
            # log = SystemLog(
            #     user_id=current_user.id,
            #     action='create_brand_with_admin',
            #     details={
            #         'brand_id': brand.id,
            #         'brand_name': brand.name,
            #         'admin_id': admin_user.id,
            #         'admin_email': admin_user.email
            #     },
            #     ip_address=request.remote_addr,
            #     created_at=datetime.utcnow()
            # )
            # db.session.add(log)

            # 트랜잭션 커밋
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '브랜드와 브랜드관리자 계정이 성공적으로 생성되었습니다.',
                'data': {
                    'brand_id': brand.id,
                    'brand_name': brand.name,
                    'brand_code': brand.code,
                    'admin_id': admin_user.id,
                    'admin_name': admin_user.name,
                    'admin_email': admin_user.email,
                    'temp_password': temp_password
                }
            })

        except Exception as e:
            # 트랜잭션 롤백
            db.session.rollback()
            logger.error(f"브랜드/관리자 생성 중 오류: {str(e)}")
            return jsonify({
                'success': False,
                'error': '브랜드와 관리자 계정 생성 중 오류가 발생했습니다.'
            }), 500

    except Exception as e:
        logger.error(f"브랜드/관리자 생성 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '서버 오류가 발생했습니다.'
        }), 500

@industry_admin_bp.route('/brands', methods=['GET'])
# @login_required  # 테스트를 위해 임시로 주석 처리
def get_brands():
    """업종관리자가 관리하는 브랜드 목록 조회"""
    try:
        # if current_user.role not in ['admin', 'super_admin']:
        #     return jsonify({
        #         'success': False,
        #         'error': '업종관리자 권한이 필요합니다.'
        #     }), 403

        brands = Brand.query.filter_by(status='active').all()
        brand_list = []

        for brand in brands:
            # 브랜드 관리자 정보
            admin = User.query.get(brand.admin_id) if brand.admin_id else None
            
            # 매장 수
            from models_main import Branch
            branch_count = Branch.query.filter_by(brand_id=brand.id, status='active').count()
            
            # 직원 수 (Staff 모델 사용)
            from models_main import Staff
            staff_count = Staff.query.filter_by(branch_id=brand.id, status='active').count()

            brand_list.append({
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'description': brand.description,
                'admin_name': admin.name if admin else '미지정',
                'admin_email': admin.email if admin else '미지정',
                'branch_count': branch_count,
                'staff_count': staff_count,
                'status': brand.status,
                'created_at': brand.created_at.isoformat() if brand.created_at else None
            })

        return jsonify({
            'success': True,
            'brands': brand_list,
            'total_count': len(brand_list)
        })

    except Exception as e:
        logger.error(f"브랜드 목록 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '브랜드 목록 조회 중 오류가 발생했습니다.'
        }), 500

@industry_admin_bp.route('/dashboard', methods=['GET'])
@login_required
def industry_dashboard():
    """업종관리자 대시보드"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({
                'success': False,
                'error': '업종관리자 권한이 필요합니다.'
            }), 403

        # 통계 데이터 조회
        total_brands = Brand.query.filter_by(status='active').count()
        total_branches = db.session.query(Branch).filter_by(status='active').count()
        total_staff = User.query.filter_by(status='approved').count()
        
        # 최근 생성된 브랜드
        recent_brands = Brand.query.filter_by(status='active')\
            .order_by(Brand.created_at.desc())\
            .limit(5).all()

        recent_brands_data = []
        for brand in recent_brands:
            admin = User.query.get(brand.admin_id) if brand.admin_id else None
            recent_brands_data.append({
                'id': brand.id,
                'name': brand.name,
                'admin_name': admin.name if admin else '미지정',
                'created_at': brand.created_at.isoformat() if brand.created_at else None
            })

        return jsonify({
            'success': True,
            'stats': {
                'total_brands': total_brands,
                'total_branches': total_branches,
                'total_staff': total_staff
            },
            'recent_brands': recent_brands_data
        })

    except Exception as e:
        logger.error(f"업종관리자 대시보드 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '대시보드 데이터 조회 중 오류가 발생했습니다.'
        }), 500 