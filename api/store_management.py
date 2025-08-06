from models_main import Brand, Branch, User, AIDiagnosis, ImprovementRequest, AIImprovementSuggestion, SystemHealth, ApprovalWorkflow
from extensions import db
import json
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from flask import Blueprint, jsonify, request, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore


store_management_bp = Blueprint('store_management', __name__)


@store_management_bp.route('/api/stores', methods=['GET'])
def get_stores():
    """매장 목록 조회"""
    try:
        # 필터링 옵션
        brand_id = request.args.get('brand_id')
        status = request.args.get('status')
        store_type = request.args.get('store_type')

        query = Branch.query

        if brand_id:
            query = query.filter_by(brand_id=brand_id)

        if status:
            query = query.filter_by(status=status)
        if store_type:
            query = query.filter_by(store_type=store_type)

        stores = query.all()

        store_list = []
        for store in stores:
            # 매장별 통계 정보
            employee_count = len(store.users)
            active_employees = len([u for u in store.users if u.status == 'approved'])

            store_data = {
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'code': store.store_code,
                'manager_name': store.manager_name if hasattr(store, 'manager_name') else None,
                'brand_id': store.brand_id,
                'brand_name': store.brand.name if store.brand else None,
                'employee_count': employee_count,
                'status': store.status,
                'created_at': store.created_at.isoformat() if store.created_at else None,
                'updated_at': store.updated_at.isoformat() if store.updated_at else None
            }
            store_list.append(store_data)

        return jsonify({
            'success': True,
            'data': store_list,
            'message': '매장 목록을 성공적으로 조회했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"매장 목록 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '매장 목록을 불러오는 중 오류가 발생했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@store_management_bp.route('/api/stores', methods=['POST'])
def create_store():
    """새 매장 생성"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['name', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} 필드는 필수입니다.',
                    'timestamp': datetime.utcnow().isoformat()
                }), 400

        # 매장 코드 중복 확인
        if data.get('store_code'):
            existing_store = Branch.query.filter_by(store_code=data['store_code']).first()
            if existing_store:
                return jsonify({
                    'success': False,
                    'error': '이미 존재하는 매장 코드입니다.',
                    'timestamp': datetime.utcnow().isoformat()
                }), 400

        # 새 매장 생성
        new_store = Branch()
        new_store.name = data['name']
        new_store.address = data['address']
        new_store.phone = data.get('phone')
        new_store.store_code = data.get('store_code')
        new_store.store_type = data.get('store_type', 'franchise')
        new_store.brand_id = data.get('brand_id')
        new_store.business_hours = data.get('business_hours')
        new_store.capacity = data.get('capacity')
        new_store.status = data.get('status', 'active')
        new_store.processing_time_standard = data.get('processing_time_standard', 15)

        db.session.add(new_store)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'id': new_store.id,
                'name': new_store.name,
                'address': new_store.address,
                'phone': new_store.phone,
                'code': new_store.store_code,
                'brand_id': new_store.brand_id,
                'status': new_store.status
            },
            'message': '매장이 성공적으로 생성되었습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"매장 생성 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '매장 생성 중 오류가 발생했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@store_management_bp.route('/api/stores/<int:store_id>', methods=['GET'])
def get_store(store_id):
    """특정 매장 상세 정보 조회"""
    try:
        store = Branch.query.get_or_404(store_id)

        # 매장 정보
        store_data = {
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'phone': store.phone,
            'code': store.store_code,
            'store_type': store.store_type,
            'status': store.status,
            'brand_id': store.brand_id,
            'brand_name': store.brand.name if store.brand else None,
            'business_hours': store.business_hours,
            'capacity': store.capacity,
            'processing_time_standard': store.processing_time_standard,
            'created_at': store.created_at.isoformat() if store.created_at else None,
            'updated_at': store.updated_at.isoformat() if store.updated_at else None
        }

        return jsonify({
            'success': True,
            'data': store_data,
            'message': '매장 정보를 성공적으로 조회했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"매장 상세 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '매장 정보를 불러오는 중 오류가 발생했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@store_management_bp.route('/api/stores/<int:store_id>', methods=['PUT'])
def update_store(store_id):
    """매장 정보 수정"""
    try:
        store = Branch.query.get_or_404(store_id)
        data = request.get_json()

        # 업데이트 가능한 필드들
        updatable_fields = ['name', 'address', 'phone', 'store_code', 'store_type',
                            'business_hours', 'capacity', 'status', 'processing_time_standard']

        for field in updatable_fields:
            if field in data:
                setattr(store, field, data[field] if data is not None else None)

        store.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'code': store.store_code,
                'brand_id': store.brand_id,
                'status': store.status
            },
            'message': '매장 정보가 성공적으로 수정되었습니다.',
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"매장 수정 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '매장 수정 중 오류가 발생했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@store_management_bp.route('/api/stores/<int:store_id>', methods=['DELETE'])
def delete_store(store_id):
    """매장 삭제"""
    try:
        store = Branch.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 삭제되었습니다.',
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"매장 삭제 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '매장 삭제 중 오류가 발생했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
