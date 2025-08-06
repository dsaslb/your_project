from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models_main import db, Industry, Brand, Branch, User, Schedule
from datetime import datetime

multitenancy_bp = Blueprint('multitenancy_api', __name__, url_prefix='/api')

# 권한 체크 데코레이터(간단 버전)
def require_role(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return jsonify({'error': '권한이 없습니다.'}), 403
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

# 1. 업종(Industry) CRUD
@multitenancy_bp.route('/industries', methods=['GET'])
@login_required
@require_role('admin')
def get_industries():
    industries = Industry.query.all()
    return jsonify([{'id': i.id, 'name': i.name, 'code': i.code, 'description': i.description} for i in industries])

@multitenancy_bp.route('/industries', methods=['POST'])
@login_required
@require_role('admin')
def create_industry():
    """업종 생성 API"""
    try:
        data = request.json
        
        # 필수 필드 검증
        if not data or not data.get('name') or not data.get('code'):
            return jsonify({
                'success': False,
                'error': '업종명과 코드는 필수 입력 항목입니다.',
                'message': '업종명과 코드를 모두 입력해주세요.'
            }), 400
        
        # 중복 코드 검증
        existing_industry = Industry.query.filter_by(code=data['code']).first()
        if existing_industry:
            return jsonify({
                'success': False,
                'error': '이미 존재하는 업종 코드입니다.',
                'message': '다른 코드를 사용해주세요.'
            }), 409
        
        # 업종 생성
        industry = Industry(
            name=data['name'], 
            code=data['code'], 
            description=data.get('description', '')
        )
        db.session.add(industry)
        db.session.commit()
        
        # 생성된 업종 정보 반환
        return jsonify({
            'success': True,
            'message': '업종이 성공적으로 생성되었습니다.',
            'data': {
                'id': industry.id,
                'name': industry.name,
                'code': industry.code,
                'description': industry.description,
                'created_at': industry.created_at.isoformat() if industry.created_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '업종 생성 중 오류가 발생했습니다.',
            'message': str(e)
        }), 500

@multitenancy_bp.route('/industries/<int:industry_id>', methods=['PUT'])
@login_required
@require_role('admin')
def update_industry(industry_id):
    industry = Industry.query.get_or_404(industry_id)
    data = request.json
    industry.name = data.get('name', industry.name)
    industry.code = data.get('code', industry.code)
    industry.description = data.get('description', industry.description)
    db.session.commit()
    return jsonify({'result': 'ok'})

@multitenancy_bp.route('/industries/<int:industry_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_industry(industry_id):
    industry = Industry.query.get_or_404(industry_id)
    db.session.delete(industry)
    db.session.commit()
    return jsonify({'result': 'ok'})

# 2. 브랜드(Brand) CRUD
@multitenancy_bp.route('/brands', methods=['POST'])
def create_brand():
    """브랜드 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('code') or not data.get('industry_id'):
            return jsonify({
                'success': False,
                'message': '브랜드명, 코드, 업종 ID는 필수 입력 항목입니다.',
                'data': None
            }), 400
        
        # 중복 코드 검증
        existing_brand = Brand.query.filter_by(code=data['code']).first()
        if existing_brand:
            return jsonify({
                'success': False,
                'message': f'코드 "{data["code"]}"는 이미 사용 중입니다.',
                'data': None
            }), 409
        
        # 업종 존재 확인
        industry = Industry.query.get(data['industry_id'])
        if not industry:
            return jsonify({
                'success': False,
                'message': '존재하지 않는 업종입니다.',
                'data': None
            }), 404
        
        # 브랜드 생성
        new_brand = Brand(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            industry_id=data['industry_id'],
            status='active'
        )
        
        db.session.add(new_brand)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 생성되었습니다.',
            'data': {
                'id': new_brand.id,
                'name': new_brand.name,
                'code': new_brand.code,
                'description': new_brand.description,
                'industry_id': new_brand.industry_id,
                'industry_name': industry.name,
                'store_count': 0,
                'employee_count': 0,
                'status': new_brand.status,
                'created_at': new_brand.created_at.isoformat() if new_brand.created_at else None,
                'updated_at': new_brand.updated_at.isoformat() if new_brand.updated_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'브랜드 생성 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500

@multitenancy_bp.route('/brands', methods=['GET'])
def get_brands():
    """브랜드 목록 조회"""
    try:
        brands = Brand.query.all()
        brand_list = []
        
        for brand in brands:
            industry = Industry.query.get(brand.industry_id)
            store_count = Branch.query.filter_by(brand_id=brand.id).count()
            employee_count = User.query.filter_by(brand_id=brand.id).count()
            
            brand_list.append({
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'description': brand.description,
                'industry_id': brand.industry_id,
                'industry_name': industry.name if industry else None,
                'store_count': store_count,
                'employee_count': employee_count,
                'status': brand.status,
                'created_at': brand.created_at.isoformat() if brand.created_at else None,
                'updated_at': brand.updated_at.isoformat() if brand.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'message': '브랜드 목록을 성공적으로 조회했습니다.',
            'data': brand_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'브랜드 목록 조회 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500

@multitenancy_bp.route('/brands/<int:brand_id>', methods=['PUT'])
@login_required
@require_role('admin', 'brand_admin')
def update_brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    data = request.json
    brand.name = data.get('name', brand.name)
    brand.code = data.get('code', brand.code)
    brand.description = data.get('description', brand.description)
    db.session.commit()
    return jsonify({'result': 'ok'})

@multitenancy_bp.route('/brands/<int:brand_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    db.session.delete(brand)
    db.session.commit()
    return jsonify({'result': 'ok'})

# 3. 매장(Branch) CRUD
@multitenancy_bp.route('/branches', methods=['GET'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def get_branches():
    branches = Branch.query.all()
    return jsonify([{'id': b.id, 'name': b.name, 'brand_id': b.brand_id, 'industry_id': b.industry_id, 'address': b.address} for b in branches])

@multitenancy_bp.route('/branches', methods=['POST'])
@login_required
@require_role('admin', 'brand_admin')
def create_branch():
    data = request.json
    branch = Branch(name=data['name'], brand_id=data['brand_id'], industry_id=data['industry_id'], address=data.get('address'))
    db.session.add(branch)
    db.session.commit()
    return jsonify({'result': 'ok', 'id': branch.id})

@multitenancy_bp.route('/branches/<int:branch_id>', methods=['PUT'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def update_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    data = request.json
    branch.name = data.get('name', branch.name)
    branch.address = data.get('address', branch.address)
    db.session.commit()
    return jsonify({'result': 'ok'})

@multitenancy_bp.route('/branches/<int:branch_id>', methods=['DELETE'])
@login_required
@require_role('admin', 'brand_admin')
def delete_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    db.session.delete(branch)
    db.session.commit()
    return jsonify({'result': 'ok'})

# 4. 직원(User/Staff) CRUD
@multitenancy_bp.route('/users', methods=['GET'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role, 'brand_id': u.brand_id, 'branch_id': u.branch_id, 'industry_id': u.industry_id} for u in users])

# 5. 매장(Stores) CRUD - branches와 동일한 기능
@multitenancy_bp.route('/stores', methods=['GET'])
def get_stores():
    """매장 목록 조회"""
    try:
        branches = Branch.query.all()
        stores = []
        
        for branch in branches:
            # 브랜드 정보 조회
            brand = Brand.query.get(branch.brand_id)
            brand_name = brand.name if brand else 'Unknown'
            
            # 직원 수 계산
            employee_count = User.query.filter_by(branch_id=branch.id).count()
            
            store_data = {
                'id': branch.id,
                'name': branch.name,
                'code': f"ST{branch.id:04d}",  # 매장 코드 생성
                'address': branch.address or '',
                'phone': branch.phone or '',  # 기본값
                'manager_name': branch.manager_name or '',  # 기본값
                'brand_id': branch.brand_id,
                'brand_name': brand_name,
                'employee_count': employee_count,
                'status': 'active',  # 기본값
                'created_at': branch.created_at.isoformat() if branch.created_at else None,
                'updated_at': branch.updated_at.isoformat() if branch.updated_at else None
            }
            stores.append(store_data)
        
        return jsonify({
            'success': True,
            'data': stores
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'매장 목록 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@multitenancy_bp.route('/stores', methods=['POST'])
@login_required
@require_role('admin', 'brand_admin')
def create_store():
    """매장 생성"""
    try:
        data = request.json
        
        # 필수 필드 검증
        if not data or not data.get('name') or not data.get('brand_id'):
            return jsonify({
                'success': False,
                'error': '매장명과 브랜드 ID는 필수 입력 항목입니다.'
            }), 400
        
        # 브랜드 존재 확인
        brand = Brand.query.get(data['brand_id'])
        if not brand:
            return jsonify({
                'success': False,
                'error': '존재하지 않는 브랜드입니다.'
            }), 404
        
        # 매장 생성 (Branch 테이블에 저장)
        store = Branch(
            name=data['name'],
            brand_id=data['brand_id'],
            industry_id=brand.industry_id,
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            manager_name=data.get('manager_name', '')
        )
        db.session.add(store)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 생성되었습니다.',
            'data': {
                'id': store.id,
                'name': store.name,
                'code': f"ST{store.id:04d}",
                'address': store.address,
                'phone': store.phone,
                'manager_name': store.manager_name,
                'brand_id': store.brand_id,
                'brand_name': brand.name,
                'employee_count': 0,
                'status': 'active',
                'created_at': store.created_at.isoformat() if store.created_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'매장 생성 중 오류가 발생했습니다: {str(e)}'
        }), 500

@multitenancy_bp.route('/stores/<int:store_id>', methods=['PUT'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def update_store(store_id):
    """매장 정보 수정"""
    try:
        store = Branch.query.get_or_404(store_id)
        data = request.json
        
        store.name = data.get('name', store.name)
        store.address = data.get('address', store.address)
        store.phone = data.get('phone', store.phone)
        store.manager_name = data.get('manager_name', store.manager_name)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '매장 정보가 성공적으로 수정되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'매장 정보 수정 중 오류가 발생했습니다: {str(e)}'
        }), 500

@multitenancy_bp.route('/stores/<int:store_id>', methods=['DELETE'])
@login_required
@require_role('admin', 'brand_admin')
def delete_store(store_id):
    """매장 삭제"""
    try:
        store = Branch.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 삭제되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'매장 삭제 중 오류가 발생했습니다: {str(e)}'
        }), 500

@multitenancy_bp.route('/stores/<int:store_id>/status', methods=['PUT'])
@login_required
@require_role('admin', 'brand_admin')
def update_store_status(store_id):
    """매장 상태 변경 (활성화/비활성화)"""
    try:
        store = Branch.query.get_or_404(store_id)
        data = request.json
        status = data.get('status')
        
        if status not in ['active', 'inactive']:
            return jsonify({
                'success': False,
                'error': '유효하지 않은 상태값입니다.'
            }), 400
        
        # Branch 모델에 status 필드가 없다면 임시로 처리
        # 실제로는 Branch 모델에 status 필드를 추가해야 합니다
        store.status = status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'매장 상태가 {status}로 변경되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'매장 상태 변경 중 오류가 발생했습니다: {str(e)}'
        }), 500

@multitenancy_bp.route('/users', methods=['POST'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def create_user():
    data = request.json
    user = User(username=data['username'], email=data['email'], role=data['role'], brand_id=data.get('brand_id'), branch_id=data.get('branch_id'), industry_id=data.get('industry_id'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'result': 'ok', 'id': user.id})

@multitenancy_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@require_role('admin', 'brand_admin', 'store_admin')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({'result': 'ok'})

@multitenancy_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@require_role('admin', 'brand_admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'result': 'ok'}) 

@multitenancy_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """스케줄 목록 조회"""
    try:
        # 쿼리 파라미터
        store_id = request.args.get('store_id', type=int)
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        schedule_type = request.args.get('type')
        
        query = Schedule.query
        
        # 필터링
        if store_id:
            query = query.filter(Schedule.branch_id == store_id)
        if user_id:
            query = query.filter(Schedule.user_id == user_id)
        if start_date:
            query = query.filter(Schedule.date >= start_date)
        if end_date:
            query = query.filter(Schedule.date <= end_date)
        if schedule_type:
            query = query.filter(Schedule.type == schedule_type)
        
        # 직원과 매장 정보 조인
        query = query.join(User, Schedule.user_id == User.id)
        query = query.join(Branch, Schedule.branch_id == Branch.id)
        
        schedules = query.all()
        
        # 응답 데이터 구성
        schedule_list = []
        for schedule in schedules:
            schedule_data = {
                'id': str(schedule.id),
                'user_id': schedule.user_id,
                'store_id': schedule.branch_id,
                'date': schedule.date.strftime('%Y-%m-%d') if schedule.date else None,
                'start_time': schedule.start_time.strftime('%H:%M') if schedule.start_time else None,
                'end_time': schedule.end_time.strftime('%H:%M') if schedule.end_time else None,
                'type': schedule.type,
                'team': schedule.team,
                'memo': schedule.memo,
                'status': schedule.status,
                'employee_name': schedule.user.name if schedule.user else None,
                'store_name': schedule.branch.name if schedule.branch else None,
                'created_at': schedule.created_at.isoformat() if schedule.created_at else None,
                'updated_at': schedule.updated_at.isoformat() if schedule.updated_at else None
            }
            schedule_list.append(schedule_data)
        
        return jsonify({
            'success': True,
            'message': '스케줄 목록을 성공적으로 조회했습니다.',
            'data': schedule_list
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'스케줄 목록 조회 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500

@multitenancy_bp.route('/schedules', methods=['POST'])
def create_schedule():
    """스케줄 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['user_id', 'store_id', 'date', 'start_time', 'end_time', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} 필드는 필수 입력 항목입니다.',
                    'data': None
                }), 400
        
        # 사용자 존재 확인
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'message': '존재하지 않는 사용자입니다.',
                'data': None
            }), 404
        
        # 매장 존재 확인
        store = Branch.query.get(data['store_id'])
        if not store:
            return jsonify({
                'success': False,
                'message': '존재하지 않는 매장입니다.',
                'data': None
            }), 404
        
        # 날짜와 시간 파싱
        try:
            schedule_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'message': '날짜 또는 시간 형식이 올바르지 않습니다.',
                'data': None
            }), 400
        
        # 중복 스케줄 확인
        existing_schedule = Schedule.query.filter_by(
            user_id=data['user_id'],
            date=schedule_date
        ).first()
        
        if existing_schedule:
            return jsonify({
                'success': False,
                'message': '해당 날짜에 이미 스케줄이 있습니다.',
                'data': None
            }), 409
        
        # 스케줄 생성
        new_schedule = Schedule(
            user_id=data['user_id'],
            branch_id=data['store_id'],
            date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            type=data['type'],
            team=data.get('team'),
            memo=data.get('memo'),
            status='scheduled'
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '스케줄이 성공적으로 생성되었습니다.',
            'data': {
                'id': str(new_schedule.id),
                'user_id': new_schedule.user_id,
                'store_id': new_schedule.branch_id,
                'date': new_schedule.date.strftime('%Y-%m-%d'),
                'start_time': new_schedule.start_time.strftime('%H:%M'),
                'end_time': new_schedule.end_time.strftime('%H:%M'),
                'type': new_schedule.type,
                'team': new_schedule.team,
                'memo': new_schedule.memo,
                'status': new_schedule.status,
                'employee_name': user.name,
                'store_name': store.name,
                'created_at': new_schedule.created_at.isoformat() if new_schedule.created_at else None,
                'updated_at': new_schedule.updated_at.isoformat() if new_schedule.updated_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'스케줄 생성 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500

@multitenancy_bp.route('/schedules/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """스케줄 수정"""
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'message': '존재하지 않는 스케줄입니다.',
                'data': None
            }), 404
        
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['user_id', 'store_id', 'date', 'start_time', 'end_time', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} 필드는 필수 입력 항목입니다.',
                    'data': None
                }), 400
        
        # 사용자 존재 확인
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'message': '존재하지 않는 사용자입니다.',
                'data': None
            }), 404
        
        # 매장 존재 확인
        store = Branch.query.get(data['store_id'])
        if not store:
            return jsonify({
                'success': False,
                'message': '존재하지 않는 매장입니다.',
                'data': None
            }), 404
        
        # 날짜와 시간 파싱
        try:
            schedule_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'message': '날짜 또는 시간 형식이 올바르지 않습니다.',
                'data': None
            }), 400
        
        # 중복 스케줄 확인 (자신 제외)
        existing_schedule = Schedule.query.filter(
            Schedule.user_id == data['user_id'],
            Schedule.date == schedule_date,
            Schedule.id != schedule_id
        ).first()
        
        if existing_schedule:
            return jsonify({
                'success': False,
                'message': '해당 날짜에 이미 스케줄이 있습니다.',
                'data': None
            }), 409
        
        # 스케줄 수정
        schedule.user_id = data['user_id']
        schedule.branch_id = data['store_id']
        schedule.date = schedule_date
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.type = data['type']
        schedule.team = data.get('team')
        schedule.memo = data.get('memo')
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '스케줄이 성공적으로 수정되었습니다.',
            'data': {
                'id': str(schedule.id),
                'user_id': schedule.user_id,
                'store_id': schedule.branch_id,
                'date': schedule.date.strftime('%Y-%m-%d'),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'type': schedule.type,
                'team': schedule.team,
                'memo': schedule.memo,
                'status': schedule.status,
                'employee_name': user.name,
                'store_name': store.name,
                'created_at': schedule.created_at.isoformat() if schedule.created_at else None,
                'updated_at': schedule.updated_at.isoformat() if schedule.updated_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'스케줄 수정 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500

@multitenancy_bp.route('/schedules/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """스케줄 삭제"""
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({
                'success': False,
                'message': '존재하지 않는 스케줄입니다.',
                'data': None
            }), 404
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '스케줄이 성공적으로 삭제되었습니다.',
            'data': None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'스케줄 삭제 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }), 500 