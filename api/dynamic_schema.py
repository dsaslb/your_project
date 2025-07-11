"""
동적 스키마 관리 API
업종별/브랜드별 커스터마이즈 필드 관리 API
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
import logging
from datetime import datetime

from core.backend.dynamic_schema import (
    schema_manager, DynamicField, IndustrySchema
)

logger = logging.getLogger(__name__)

dynamic_schema_bp = Blueprint('dynamic_schema', __name__)

def admin_required(f):
    """관리자 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
        
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@dynamic_schema_bp.route('/api/schemas/industries', methods=['GET'])
@login_required
@admin_required
def get_industry_schemas():
    """업종 스키마 목록 조회"""
    try:
        schemas = []
        for industry_id, schema in schema_manager.industry_schemas.items():
            schemas.append({
                'id': industry_id,
                'name': schema.industry_name,
                'version': schema.version,
                'fields_count': len(schema.fields),
                'created_at': schema.created_at.isoformat(),
                'updated_at': schema.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'schemas': schemas,
            'total': len(schemas)
        })
        
    except Exception as e:
        logger.error(f"업종 스키마 목록 조회 실패: {e}")
        return jsonify({'error': '업종 스키마 목록 조회에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/industries/<industry_id>', methods=['GET'])
@login_required
@admin_required
def get_industry_schema(industry_id):
    """특정 업종 스키마 조회"""
    try:
        schema = schema_manager.get_industry_schema(industry_id)
        
        if not schema:
            return jsonify({'error': '업종 스키마를 찾을 수 없습니다.'}), 404
        
        # 폼 스키마 생성
        form_schema = schema_manager.create_form_schema(schema.fields)
        
        return jsonify({
            'success': True,
            'schema': {
                'id': schema.industry_id,
                'name': schema.industry_name,
                'version': schema.version,
                'fields': form_schema['fields'],
                'created_at': schema.created_at.isoformat(),
                'updated_at': schema.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"업종 스키마 조회 실패: {e}")
        return jsonify({'error': '업종 스키마 조회에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/industries', methods=['POST'])
@login_required
@admin_required
def create_industry_schema():
    """업종 스키마 생성"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '스키마 데이터가 필요합니다.'}), 400
        
        # 필드 데이터를 DynamicField 객체로 변환
        fields = []
        for field_data in data.get('fields', []):
            field = DynamicField(**field_data)
            fields.append(field)
        
        # IndustrySchema 생성
        schema = IndustrySchema(
            industry_id=data['industry_id'],
            industry_name=data['industry_name'],
            fields=fields,
            version=data.get('version', '1.0.0'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 스키마 등록
        if schema_manager.register_industry_schema(data['industry_id'], schema):
            return jsonify({
                'success': True,
                'message': '업종 스키마가 생성되었습니다.',
                'schema_id': data['industry_id']
            })
        else:
            return jsonify({'error': '업종 스키마 생성에 실패했습니다.'}), 400
            
    except Exception as e:
        logger.error(f"업종 스키마 생성 실패: {e}")
        return jsonify({'error': '업종 스키마 생성에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/industries/<industry_id>', methods=['PUT'])
@login_required
@admin_required
def update_industry_schema(industry_id):
    """업종 스키마 업데이트"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '업데이트 데이터가 필요합니다.'}), 400
        
        # 기존 스키마 조회
        existing_schema = schema_manager.get_industry_schema(industry_id)
        if not existing_schema:
            return jsonify({'error': '업종 스키마를 찾을 수 없습니다.'}), 404
        
        # 필드 데이터를 DynamicField 객체로 변환
        fields = []
        for field_data in data.get('fields', []):
            field = DynamicField(**field_data)
            fields.append(field)
        
        # 업데이트된 스키마 생성
        updated_schema = IndustrySchema(
            industry_id=industry_id,
            industry_name=data.get('industry_name', existing_schema.industry_name),
            fields=fields,
            version=data.get('version', existing_schema.version),
            created_at=existing_schema.created_at,
            updated_at=datetime.utcnow()
        )
        
        # 스키마 등록
        if schema_manager.register_industry_schema(industry_id, updated_schema):
            return jsonify({
                'success': True,
                'message': '업종 스키마가 업데이트되었습니다.'
            })
        else:
            return jsonify({'error': '업종 스키마 업데이트에 실패했습니다.'}), 400
            
    except Exception as e:
        logger.error(f"업종 스키마 업데이트 실패: {e}")
        return jsonify({'error': '업종 스키마 업데이트에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/brands', methods=['GET'])
@login_required
@admin_required
def get_brand_schemas():
    """브랜드 스키마 목록 조회"""
    try:
        schemas = []
        for brand_id, schema in schema_manager.brand_schemas.items():
            schemas.append({
                'id': brand_id,
                'name': schema.brand_name,
                'industry_id': schema.industry_id,
                'version': schema.version,
                'fields_count': len(schema.fields),
                'created_at': schema.created_at.isoformat(),
                'updated_at': schema.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'schemas': schemas,
            'total': len(schemas)
        })
        
    except Exception as e:
        logger.error(f"브랜드 스키마 목록 조회 실패: {e}")
        return jsonify({'error': '브랜드 스키마 목록 조회에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/brands/<brand_id>', methods=['GET'])
@login_required
@admin_required
def get_brand_schema(brand_id):
    """특정 브랜드 스키마 조회"""
    try:
        schema = schema_manager.get_brand_schema(brand_id)
        
        if not schema:
            return jsonify({'error': '브랜드 스키마를 찾을 수 없습니다.'}), 404
        
        # 폼 스키마 생성
        form_schema = schema_manager.create_form_schema(schema.fields)
        
        return jsonify({
            'success': True,
            'schema': {
                'id': schema.brand_id,
                'name': schema.brand_name,
                'industry_id': schema.industry_id,
                'version': schema.version,
                'fields': form_schema['fields'],
                'created_at': schema.created_at.isoformat(),
                'updated_at': schema.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"브랜드 스키마 조회 실패: {e}")
        return jsonify({'error': '브랜드 스키마 조회에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/combined/<industry_id>/<brand_id>', methods=['GET'])
@login_required
def get_combined_schema(industry_id, brand_id):
    """업종 + 브랜드 결합 스키마 조회"""
    try:
        fields = schema_manager.get_combined_schema(industry_id, brand_id)
        
        # 폼 스키마 생성
        form_schema = schema_manager.create_form_schema(fields)
        
        return jsonify({
            'success': True,
            'schema': {
                'industry_id': industry_id,
                'brand_id': brand_id,
                'fields': form_schema['fields']
            }
        })
        
    except Exception as e:
        logger.error(f"결합 스키마 조회 실패: {e}")
        return jsonify({'error': '결합 스키마 조회에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/validate', methods=['POST'])
@login_required
def validate_data():
    """데이터 유효성 검증"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '검증할 데이터가 필요합니다.'}), 400
        
        industry_id = data.get('industry_id')
        brand_id = data.get('brand_id')
        form_data = data.get('data', {})
        
        if not industry_id:
            return jsonify({'error': '업종 ID가 필요합니다.'}), 400
        
        # 결합 스키마 가져오기
        fields = schema_manager.get_combined_schema(industry_id, brand_id or '')
        
        # 데이터 검증
        validated_data = schema_manager.validate_data(form_data, fields)
        
        return jsonify({
            'success': True,
            'message': '데이터 검증이 완료되었습니다.',
            'validated_data': validated_data
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"데이터 검증 실패: {e}")
        return jsonify({'error': '데이터 검증에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/export/<industry_id>', methods=['GET'])
@login_required
@admin_required
def export_schema(industry_id):
    """스키마 내보내기"""
    try:
        schema = schema_manager.get_industry_schema(industry_id)
        
        if not schema:
            return jsonify({'error': '업종 스키마를 찾을 수 없습니다.'}), 404
        
        export_data = schema_manager.export_schema(schema)
        
        return jsonify({
            'success': True,
            'schema': export_data
        })
        
    except Exception as e:
        logger.error(f"스키마 내보내기 실패: {e}")
        return jsonify({'error': '스키마 내보내기에 실패했습니다.'}), 500

@dynamic_schema_bp.route('/api/schemas/import', methods=['POST'])
@login_required
@admin_required
def import_schema():
    """스키마 가져오기"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '가져올 스키마 데이터가 필요합니다.'}), 400
        
        # 스키마 가져오기
        schema = schema_manager.import_schema(data)
        
        # 스키마 등록
        if schema_manager.register_industry_schema(schema.industry_id, schema):
            return jsonify({
                'success': True,
                'message': '스키마가 성공적으로 가져와졌습니다.',
                'schema_id': schema.industry_id
            })
        else:
            return jsonify({'error': '스키마 등록에 실패했습니다.'}), 400
            
    except Exception as e:
        logger.error(f"스키마 가져오기 실패: {e}")
        return jsonify({'error': '스키마 가져오기에 실패했습니다.'}), 500 