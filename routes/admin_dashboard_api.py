from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from models import Brand, Branch, User, Order, Notification, SystemLog
from extensions import db
from datetime import datetime, timedelta
import json

admin_dashboard_api = Blueprint('admin_dashboard_api', __name__, url_prefix='/api/admin')

# 샘플 브랜드 데이터 생성 함수
def create_sample_brands():
    """샘플 브랜드 데이터 생성"""
    brands_data = [
        {
            'name': '백다방',
            'code': 'BAEK',
            'description': '전통 다방 브랜드',
            'logo_url': '/static/images/brands/baekdabang.png',
            'website': 'https://baekdabang.com',
            'contact_email': 'contact@baekdabang.com',
            'contact_phone': '02-1234-5678',
            'address': '서울특별시 강남구',
            'status': 'active'
        },
        {
            'name': '초선마리',
            'code': 'CHOSUN',
            'description': '한국 전통 차 브랜드',
            'logo_url': '/static/images/brands/chosunmari.png',
            'website': 'https://chosunmari.com',
            'contact_email': 'contact@chosunmari.com',
            'contact_phone': '02-2345-6789',
            'address': '서울특별시 종로구',
            'status': 'active'
        },
        {
            'name': '카페베네',
            'code': 'CAFFEBENE',
            'description': '프리미엄 커피 브랜드',
            'logo_url': '/static/images/brands/caffebene.png',
            'website': 'https://caffebene.co.kr',
            'contact_email': 'contact@caffebene.co.kr',
            'contact_phone': '02-3456-7890',
            'address': '서울특별시 서초구',
            'status': 'active'
        },
        {
            'name': '스타벅스',
            'code': 'STARBUCKS',
            'description': '글로벌 커피 브랜드',
            'logo_url': '/static/images/brands/starbucks.png',
            'website': 'https://starbucks.co.kr',
            'contact_email': 'contact@starbucks.co.kr',
            'contact_phone': '02-4567-8901',
            'address': '서울특별시 중구',
            'status': 'active'
        }
    ]
    
    for brand_data in brands_data:
        existing_brand = Brand.query.filter_by(name=brand_data['name']).first()
        if not existing_brand:
            brand = Brand(**brand_data)
            db.session.add(brand)
    
    db.session.commit()

# 샘플 매장 데이터 생성 함수
def create_sample_stores():
    """샘플 매장 데이터 생성"""
    stores_data = [
        # 백다방 매장들
        {
            'name': '백다방 강남점',
            'brand_id': 1,
            'store_code': 'BAEK_GANGNAM',
            'address': '서울특별시 강남구 강남대로 123',
            'phone': '02-1234-5678',
            'store_type': 'franchise',
            'status': 'active',
            'capacity': 50
        },
        {
            'name': '백다방 홍대점',
            'brand_id': 1,
            'store_code': 'BAEK_HONGDAE',
            'address': '서울특별시 마포구 홍대로 456',
            'phone': '02-1234-5679',
            'store_type': 'franchise',
            'status': 'active',
            'capacity': 40
        },
        {
            'name': '백다방 신촌점',
            'brand_id': 1,
            'store_code': 'BAEK_SINCHON',
            'address': '서울특별시 서대문구 신촌로 789',
            'phone': '02-1234-5680',
            'store_type': 'franchise',
            'status': 'active',
            'capacity': 35
        },
        
        # 초선마리 매장들
        {
            'name': '초선마리 강남점',
            'brand_id': 2,
            'store_code': 'CHOSUN_GANGNAM',
            'address': '서울특별시 강남구 테헤란로 321',
            'phone': '02-2345-6789',
            'store_type': 'franchise',
            'status': 'active',
            'capacity': 45
        },
        {
            'name': '초선마리 홍대점',
            'brand_id': 2,
            'store_code': 'CHOSUN_HONGDAE',
            'address': '서울특별시 마포구 와우산로 654',
            'phone': '02-2345-6790',
            'store_type': 'franchise',
            'status': 'active',
            'capacity': 38
        },
        {
            'name': '초선마리 종로점',
            'brand_id': 2,
            'store_code': 'CHOSUN_JONGNO',
            'address': '서울특별시 종로구 종로 987',
            'phone': '02-2345-6791',
            'store_type': 'corporate',
            'status': 'active',
            'capacity': 60
        },
        
        # 카페베네 매장들
        {
            'name': '카페베네 강남점',
            'brand_id': 3,
            'store_code': 'CAFFEBENE_GANGNAM',
            'address': '서울특별시 강남구 역삼로 147',
            'phone': '02-3456-7890',
            'store_type': 'franchise',
            'status': 'active',
            'capacity': 55
        },
        {
            'name': '카페베네 홍대점',
            'brand_id': 3,
            'store_code': 'CAFFEBENE_HONGDAE',
            'address': '서울특별시 마포구 동교로 258',
            'phone': '02-3456-7891',
            'store_type': 'franchise',
            'status': 'active',
            'capacity': 42
        },
        
        # 스타벅스 매장들
        {
            'name': '스타벅스 강남점',
            'brand_id': 4,
            'store_code': 'STARBUCKS_GANGNAM',
            'address': '서울특별시 강남구 삼성로 369',
            'phone': '02-4567-8901',
            'store_type': 'corporate',
            'status': 'active',
            'capacity': 70
        },
        {
            'name': '스타벅스 홍대점',
            'brand_id': 4,
            'store_code': 'STARBUCKS_HONGDAE',
            'address': '서울특별시 마포구 양화로 741',
            'phone': '02-4567-8902',
            'store_type': 'corporate',
            'status': 'active',
            'capacity': 65
        }
    ]
    
    for store_data in stores_data:
        existing_store = Branch.query.filter_by(store_code=store_data['store_code']).first()
        if not existing_store:
            store = Branch(**store_data)
            db.session.add(store)
    
    db.session.commit()

# 1. 브랜드별 통계
@admin_dashboard_api.route('/brand_stats')
@login_required
def brand_stats():
    """브랜드 통계 API"""
    try:
        # 전체 브랜드 수
        total_brands = Brand.query.count()
        active_brands = Brand.query.filter_by(status='active').count()
        
        # 브랜드별 매장 수
        brand_branch_stats = db.session.query(
            Brand.name,
            db.func.count(Branch.id).label('branch_count')
        ).outerjoin(Branch).group_by(Brand.id, Brand.name).all()
        
        # 브랜드별 사용자 수
        brand_user_stats = db.session.query(
            Brand.name,
            db.func.count(User.id).label('user_count')
        ).outerjoin(Branch).outerjoin(User).group_by(Brand.id, Brand.name).all()
        
        # 최근 30일 생성된 브랜드
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_brands = Brand.query.filter(
            Brand.created_at >= thirty_days_ago
        ).count()
        
        # 브랜드별 통계 데이터
        brand_stats = []
        for brand in Brand.query.all():
            branch_count = len(brand.stores) if hasattr(brand, 'stores') else 0
            user_count = User.query.join(Branch).filter(Branch.brand_id == brand.id).count()
            
            brand_stats.append({
                'id': brand.id,
                'name': brand.name,
                'status': brand.status,
                'branch_count': branch_count,
                'user_count': user_count,
                'created_at': brand.created_at.isoformat() if brand.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_brands': total_brands,
                    'active_brands': active_brands,
                    'inactive_brands': total_brands - active_brands,
                    'recent_brands': recent_brands
                },
                'brand_stats': brand_stats,
                'branch_distribution': [
                    {
                        'brand_name': stat.name,
                        'branch_count': stat.branch_count
                    } for stat in brand_branch_stats
                ],
                'user_distribution': [
                    {
                        'brand_name': stat.name,
                        'user_count': stat.user_count
                    } for stat in brand_user_stats
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'브랜드 통계 조회 실패: {str(e)}'
        }), 500

# 2. 매장별 통계
@admin_dashboard_api.route('/store_stats', methods=['GET'])
@login_required
def store_stats():
    """매장별 통계 조회"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    brand_id = request.args.get('brand_id')
    
    try:
        query = Branch.query.filter_by(status='active')
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        stores = query.all()
        stats = []
        
        for store in stores:
            # 매장별 직원 수
            employee_count = User.query.filter_by(branch_id=store.id, status='approved').count()
            
            # 매장별 주문 수 (최근 30일)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            order_count = Order.query.filter_by(
                store_id=store.id,
                created_at=thirty_days_ago
            ).count()
            
            # 매장별 미읽 알림 수
            unread_notifications = Notification.query.filter_by(
                branch_id=store.id,
                is_read=False
            ).count()
            
            stats.append({
                'store_id': store.id,
                'store_name': store.name,
                'store_code': store.store_code,
                'brand_id': store.brand_id,
                'brand_name': store.brand.name if store.brand else '',
                'employee_count': employee_count,
                'order_count': order_count,
                'unread_notifications': unread_notifications,
                'store_type': store.store_type,
                'status': store.status,
                'capacity': store.capacity,
                'address': store.address,
                'phone': store.phone
            })
        
        return jsonify({'success': True, 'stats': stats})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 3. 브랜드 목록 조회
@admin_dashboard_api.route('/brands', methods=['GET'])
@login_required
def get_brands():
    """브랜드 목록 조회"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    try:
        brands = Brand.query.filter_by(status='active').all()
        brand_list = []
        
        for brand in brands:
            store_count = Branch.query.filter_by(brand_id=brand.id, status='active').count()
            employee_count = User.query.filter_by(brand_id=brand.id, status='approved').count()
            
            brand_list.append({
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'description': brand.description,
                'logo_url': brand.logo_url,
                'website': brand.website,
                'contact_email': brand.contact_email,
                'contact_phone': brand.contact_phone,
                'address': brand.address,
                'status': brand.status,
                'store_count': store_count,
                'employee_count': employee_count,
                'created_at': brand.created_at.isoformat() if brand.created_at else None
            })
        
        return jsonify({'success': True, 'brands': brand_list})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 4. 매장 목록 조회
@admin_dashboard_api.route('/stores', methods=['GET'])
@login_required
def get_stores():
    """매장 목록 조회"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    brand_id = request.args.get('brand_id')
    
    try:
        query = Branch.query.filter_by(status='active')
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        stores = query.all()
        store_list = []
        
        for store in stores:
            employee_count = User.query.filter_by(branch_id=store.id, status='approved').count()
            
            store_list.append({
                'id': store.id,
                'name': store.name,
                'store_code': store.store_code,
                'brand_id': store.brand_id,
                'brand_name': store.brand.name if store.brand else '',
                'store_type': store.store_type,
                'status': store.status,
                'capacity': store.capacity,
                'address': store.address,
                'phone': store.phone,
                'employee_count': employee_count,
                'created_at': store.created_at.isoformat() if store.created_at else None
            })
        
        return jsonify({'success': True, 'stores': store_list})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 5. 직원 목록 및 승인/차단
@admin_dashboard_api.route('/users', methods=['GET'])
@login_required
def admin_users():
    """직원 목록 조회"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    brand_id = request.args.get('brand_id')
    store_id = request.args.get('store_id')
    
    try:
        query = User.query
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        if store_id:
            query = query.filter_by(branch_id=store_id)
        
        users = query.all()
        user_list = []
        
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'status': user.status,
                'brand_id': user.brand_id,
                'brand_name': user.brand.name if user.brand else '',
                'branch_id': user.branch_id,
                'branch_name': user.branch.name if user.branch else '',
                'position': user.position,
                'department': user.department,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({'success': True, 'users': user_list})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_dashboard_api.route('/user/<int:user_id>/status', methods=['POST'])
@login_required
def update_user_status(user_id):
    """직원 상태 업데이트"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': '사용자를 찾을 수 없습니다.'}), 404
        
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': '요청 데이터가 없습니다.'}), 400
        
        new_status = data.get('status')
        if new_status not in ['approved', 'blocked', 'pending']:
            return jsonify({'success': False, 'error': '잘못된 상태 값'}), 400
        
        user.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'user_id': user.id, 
            'new_status': user.status,
            'message': f'사용자 상태가 {new_status}로 변경되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# 6. 시스템 로그
@admin_dashboard_api.route('/system_logs', methods=['GET'])
@login_required
def system_logs():
    """시스템 로그 조회"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    try:
        logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(100).all()
        log_list = []
        
        for log in logs:
            log_list.append({
                'id': log.id,
                'action': log.action,
                'user_id': log.user_id,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'details': log.details if hasattr(log, 'details') else '',
            })
        
        return jsonify({'success': True, 'logs': log_list})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 7. 고급 분석 대시보드 페이지
@admin_dashboard_api.route('/advanced-analytics')
@login_required
def advanced_analytics_page():
    """고급 분석 대시보드 페이지"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    return render_template('admin/advanced_analytics_dashboard.html')

# 8. 브랜드 생성 API
@admin_dashboard_api.route('/brands', methods=['POST'])
@login_required
def create_brand():
    """브랜드 생성"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': '요청 데이터가 없습니다.'}), 400
        
        # 필수 필드 검증
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} 필드가 필요합니다.'}), 400
        
        # 중복 검사
        existing_brand = Brand.query.filter_by(name=data['name']).first()
        if existing_brand:
            return jsonify({'success': False, 'error': '이미 존재하는 브랜드명입니다.'}), 400
        
        existing_code = Brand.query.filter_by(code=data['code']).first()
        if existing_code:
            return jsonify({'success': False, 'error': '이미 존재하는 브랜드 코드입니다.'}), 400
        
        # 브랜드 생성
        brand = Brand(**data)
        db.session.add(brand)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 생성되었습니다.',
            'brand_id': brand.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# 9. 매장 생성 API
@admin_dashboard_api.route('/stores', methods=['POST'])
@login_required
def create_store():
    """매장 생성"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403
    
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': '요청 데이터가 없습니다.'}), 400
        
        # 필수 필드 검증
        required_fields = ['name', 'store_code', 'brand_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} 필드가 필요합니다.'}), 400
        
        # 브랜드 존재 확인
        brand = Brand.query.get(data['brand_id'])
        if not brand:
            return jsonify({'success': False, 'error': '존재하지 않는 브랜드입니다.'}), 400
        
        # 중복 검사
        existing_store = Branch.query.filter_by(store_code=data['store_code']).first()
        if existing_store:
            return jsonify({'success': False, 'error': '이미 존재하는 매장 코드입니다.'}), 400
        
        # 매장 생성
        store = Branch(**data)
        db.session.add(store)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 생성되었습니다.',
            'store_id': store.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500 