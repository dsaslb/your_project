import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models_main import Branch, User, Brand
from werkzeug.security import generate_password_hash
import re

logger = logging.getLogger(__name__)

brand_admin_bp = Blueprint('brand_admin', __name__, url_prefix='/api/brand')

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

@brand_admin_bp.route('/create_store_with_manager', methods=['POST'])
@login_required
def create_store_with_manager():
    """매장과 매장관리자 계정을 동시에 생성"""
    try:
        # 권한 확인 (브랜드관리자만)
        if current_user.role != 'brand_admin':
            return jsonify({
                'success': False,
                'error': '브랜드관리자 권한이 필요합니다.'
            }), 403

        # 브랜드 ID 확인
        if not current_user.brand_id:
            return jsonify({
                'success': False,
                'error': '브랜드 정보가 없습니다.'
            }), 400

        data = request.get_json()
        
        # 필수 입력값 검증
        required_fields = ['name', 'address', 'phone', 'manager_name', 'manager_email', 'manager_phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'필수 입력값이 누락되었습니다: {field}'
                }), 400

        # 이메일 형식 검증
        if not validate_email(data['manager_email']):
            return jsonify({
                'success': False,
                'error': '올바른 이메일 형식이 아닙니다.'
            }), 400

        # 전화번호 형식 검증
        if not validate_phone(data['manager_phone']):
            return jsonify({
                'success': False,
                'error': '올바른 전화번호 형식이 아닙니다.'
            }), 400

        # 이메일 중복 확인
        existing_user = User.query.filter_by(email=data['manager_email']).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': '이미 등록된 이메일입니다.'
            }), 400

        # 매장명 중복 확인 (같은 브랜드 내에서)
        existing_store = Branch.query.filter_by(
            name=data['name'], 
            brand_id=current_user.brand_id
        ).first()
        if existing_store:
            return jsonify({
                'success': False,
                'error': '이미 등록된 매장명입니다.'
            }), 400

        # 매장 코드 생성 (브랜드코드 + 매장명 기반)
        brand = Brand.query.get(current_user.brand_id)
        store_code = f"{brand.code}_{data['name'].replace(' ', '').upper()}"[:20]

        # 트랜잭션 시작
        try:
            # 1. 매장 생성
            store = Branch(
                name=data['name'],
                address=data['address'],
                phone=data['phone'],
                email=data.get('email'),
                brand_id=current_user.brand_id,
                store_code=store_code,
                status='active',
                created_at=datetime.utcnow()
            )
            
            db.session.add(store)
            db.session.flush()  # store.id 확보

            # 2. 임시 비밀번호 생성
            temp_password = generate_temp_password()
            password_hash = generate_password_hash(temp_password)

            # 3. 매장관리자 계정 생성
            manager_user = User(
                username=data['manager_email'].split('@')[0],  # 이메일 앞부분을 username으로 사용
                email=data['manager_email'],
                password_hash=password_hash,
                name=data['manager_name'],
                phone=data['manager_phone'],
                role='store_admin',
                brand_id=current_user.brand_id,
                branch_id=store.id,
                status='approved',
                grade='manager',
                created_at=datetime.utcnow()
            )
            
            db.session.add(manager_user)
            db.session.flush()  # manager_user.id 확보

            # 4. 매장에 관리자 ID 연결
            store.manager_id = manager_user.id
            
            # 5. 생성 로그 기록
            from models_main import SystemLog
            log = SystemLog(
                user_id=current_user.id,
                action='create_store_with_manager',
                details={
                    'store_id': store.id,
                    'store_name': store.name,
                    'manager_id': manager_user.id,
                    'manager_email': manager_user.email
                },
                ip_address=request.remote_addr,
                created_at=datetime.utcnow()
            )
            db.session.add(log)

            # 트랜잭션 커밋
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '매장과 매장관리자 계정이 성공적으로 생성되었습니다.',
                'data': {
                    'store_id': store.id,
                    'store_name': store.name,
                    'store_code': store.store_code,
                    'manager_id': manager_user.id,
                    'manager_name': manager_user.name,
                    'manager_email': manager_user.email,
                    'temp_password': temp_password
                }
            })

        except Exception as e:
            # 트랜잭션 롤백
            db.session.rollback()
            logger.error(f"매장/관리자 생성 중 오류: {str(e)}")
            return jsonify({
                'success': False,
                'error': '매장과 관리자 계정 생성 중 오류가 발생했습니다.'
            }), 500

    except Exception as e:
        logger.error(f"매장/관리자 생성 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '서버 오류가 발생했습니다.'
        }), 500

@brand_admin_bp.route('/stores', methods=['GET'])
@login_required
def get_stores():
    """브랜드관리자가 관리하는 매장 목록 조회"""
    try:
        if current_user.role != 'brand_admin':
            return jsonify({
                'success': False,
                'error': '브랜드관리자 권한이 필요합니다.'
            }), 403

        if not current_user.brand_id:
            return jsonify({
                'success': False,
                'error': '브랜드 정보가 없습니다.'
            }), 400

        stores = Branch.query.filter_by(brand_id=current_user.brand_id, status='active').all()
        store_list = []

        for store in stores:
            # 매장 관리자 정보
            manager = User.query.get(store.manager_id) if store.manager_id else None
            
            # 직원 수
            employee_count = User.query.filter_by(branch_id=store.id, status='approved').count()

            store_list.append({
                'id': store.id,
                'name': store.name,
                'store_code': store.store_code,
                'address': store.address,
                'phone': store.phone,
                'email': store.email,
                'manager_name': manager.name if manager else '미지정',
                'manager_email': manager.email if manager else '미지정',
                'employee_count': employee_count,
                'status': store.status,
                'created_at': store.created_at.isoformat() if store.created_at else None
            })

        return jsonify({
            'success': True,
            'stores': store_list,
            'total_count': len(store_list)
        })

    except Exception as e:
        logger.error(f"매장 목록 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '매장 목록 조회 중 오류가 발생했습니다.'
        }), 500

@brand_admin_bp.route('/dashboard', methods=['GET'])
@login_required
def brand_dashboard():
    """브랜드관리자 대시보드"""
    try:
        if current_user.role != 'brand_admin':
            return jsonify({
                'success': False,
                'error': '브랜드관리자 권한이 필요합니다.'
            }), 403

        if not current_user.brand_id:
            return jsonify({
                'success': False,
                'error': '브랜드 정보가 없습니다.'
            }), 400

        # 통계 데이터 조회
        total_stores = Branch.query.filter_by(brand_id=current_user.brand_id, status='active').count()
        total_employees = User.query.filter_by(brand_id=current_user.brand_id, status='approved').count()
        pending_approvals = User.query.filter_by(brand_id=current_user.brand_id, status='pending').count()
        
        # 최근 생성된 매장
        recent_stores = Branch.query.filter_by(brand_id=current_user.brand_id, status='active')\
            .order_by(Branch.created_at.desc())\
            .limit(5).all()

        recent_stores_data = []
        for store in recent_stores:
            manager = User.query.get(store.manager_id) if store.manager_id else None
            recent_stores_data.append({
                'id': store.id,
                'name': store.name,
                'manager_name': manager.name if manager else '미지정',
                'created_at': store.created_at.isoformat() if store.created_at else None
            })

        return jsonify({
            'success': True,
            'stats': {
                'total_stores': total_stores,
                'total_employees': total_employees,
                'pending_approvals': pending_approvals
            },
            'recent_stores': recent_stores_data
        })

    except Exception as e:
        logger.error(f"브랜드관리자 대시보드 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '대시보드 데이터 조회 중 오류가 발생했습니다.'
        }), 500 