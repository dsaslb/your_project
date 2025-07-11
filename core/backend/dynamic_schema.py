"""
동적 스키마 시스템
업종별/브랜드별 커스터마이즈 필드 관리
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class DynamicField:
    """동적 필드 정의"""
    name: str
    type: str  # string, number, boolean, date, select, json
    label: str
    required: bool = False
    default: Any = None
    options: Optional[List[Any]] = None
    validation: Optional[Dict[str, Any]] = None
    order: int = 0
    category: str = "general"
    description: str = ""

@dataclass
class IndustrySchema:
    """업종별 스키마"""
    industry_id: str
    industry_name: str
    fields: List[DynamicField]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"

@dataclass
class BrandSchema:
    """브랜드별 스키마"""
    brand_id: str
    brand_name: str
    industry_id: str
    fields: List[DynamicField]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"

class DynamicSchemaManager:
    """동적 스키마 관리자"""
    
    def __init__(self):
        self.industry_schemas: Dict[str, IndustrySchema] = {}
        self.brand_schemas: Dict[str, BrandSchema] = {}
        self.field_types = {
            'string': self._validate_string,
            'number': self._validate_number,
            'boolean': self._validate_boolean,
            'date': self._validate_date,
            'select': self._validate_select,
            'json': self._validate_json
        }
    
    def register_industry_schema(self, industry_id: str, schema: IndustrySchema) -> bool:
        """업종 스키마 등록"""
        try:
            self.industry_schemas[industry_id] = schema
            logger.info(f"업종 스키마 등록: {industry_id}")
            return True
        except Exception as e:
            logger.error(f"업종 스키마 등록 실패: {e}")
            return False
    
    def register_brand_schema(self, brand_id: str, schema: BrandSchema) -> bool:
        """브랜드 스키마 등록"""
        try:
            self.brand_schemas[brand_id] = schema
            logger.info(f"브랜드 스키마 등록: {brand_id}")
            return True
        except Exception as e:
            logger.error(f"브랜드 스키마 등록 실패: {e}")
            return False
    
    def get_industry_schema(self, industry_id: str) -> Optional[IndustrySchema]:
        """업종 스키마 조회"""
        return self.industry_schemas.get(industry_id)
    
    def get_brand_schema(self, brand_id: str) -> Optional[BrandSchema]:
        """브랜드 스키마 조회"""
        return self.brand_schemas.get(brand_id)
    
    def get_combined_schema(self, industry_id: str, brand_id: str) -> List[DynamicField]:
        """업종 + 브랜드 스키마 결합"""
        fields = []
        
        # 업종 스키마 필드 추가
        industry_schema = self.get_industry_schema(industry_id)
        if industry_schema:
            fields.extend(industry_schema.fields)
        
        # 브랜드 스키마 필드 추가 (업종 필드 오버라이드)
        brand_schema = self.get_brand_schema(brand_id)
        if brand_schema:
            # 기존 필드 업데이트 또는 새 필드 추가
            existing_field_names = {f.name for f in fields}
            for brand_field in brand_schema.fields:
                if brand_field.name in existing_field_names:
                    # 기존 필드 업데이트
                    for i, field in enumerate(fields):
                        if field.name == brand_field.name:
                            fields[i] = brand_field
                            break
                else:
                    # 새 필드 추가
                    fields.append(brand_field)
        
        # 순서대로 정렬
        fields.sort(key=lambda x: x.order)
        return fields
    
    def validate_data(self, data: Dict[str, Any], schema: List[DynamicField]) -> Dict[str, Any]:
        """데이터 유효성 검증"""
        validated_data = {}
        errors = []
        
        for field in schema:
            field_name = field.name
            field_value = data.get(field_name, field.default)
            
            # 필수 필드 검증
            if field.required and field_value is None:
                errors.append(f"필수 필드 '{field.label}'이 누락되었습니다")
                continue
            
            # 필드 타입 검증
            if field_value is not None:
                validator = self.field_types.get(field.type)
                if validator:
                    try:
                        validated_value = validator(field_value, field)
                        validated_data[field_name] = validated_value
                    except ValueError as e:
                        errors.append(f"필드 '{field.label}': {str(e)}")
                else:
                    validated_data[field_name] = field_value
            else:
                validated_data[field_name] = field_value
        
        if errors:
            raise ValueError("데이터 검증 실패: " + "; ".join(errors))
        
        return validated_data
    
    def _validate_string(self, value: Any, field: DynamicField) -> str:
        """문자열 검증"""
        if not isinstance(value, str):
            raise ValueError("문자열 타입이어야 합니다")
        
        # 길이 검증
        if field.validation:
            min_length = field.validation.get('min_length')
            max_length = field.validation.get('max_length')
            
            if min_length and len(value) < min_length:
                raise ValueError(f"최소 {min_length}자 이상이어야 합니다")
            
            if max_length and len(value) > max_length:
                raise ValueError(f"최대 {max_length}자까지 가능합니다")
        
        return value
    
    def _validate_number(self, value: Any, field: DynamicField) -> float:
        """숫자 검증"""
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            raise ValueError("숫자 타입이어야 합니다")
        
        # 범위 검증
        if field.validation:
            min_value = field.validation.get('min')
            max_value = field.validation.get('max')
            
            if min_value is not None and num_value < min_value:
                raise ValueError(f"최소값 {min_value} 이상이어야 합니다")
            
            if max_value is not None and num_value > max_value:
                raise ValueError(f"최대값 {max_value} 이하여야 합니다")
        
        return num_value
    
    def _validate_boolean(self, value: Any, field: DynamicField) -> bool:
        """불린 검증"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif value.lower() in ['false', '0', 'no', 'off']:
                return False
            else:
                raise ValueError("유효한 불린 값이어야 합니다")
        else:
            raise ValueError("불린 타입이어야 합니다")
    
    def _validate_date(self, value: Any, field: DynamicField) -> str:
        """날짜 검증"""
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return value
            except ValueError:
                raise ValueError("유효한 날짜 형식이어야 합니다 (YYYY-MM-DD)")
        else:
            raise ValueError("날짜 문자열이어야 합니다")
    
    def _validate_select(self, value: Any, field: DynamicField) -> Any:
        """선택 필드 검증"""
        if field.options and value not in field.options:
            raise ValueError(f"유효한 옵션 중 하나를 선택해야 합니다: {field.options}")
        return value
    
    def _validate_json(self, value: Any, field: DynamicField) -> Dict[str, Any]:
        """JSON 검증"""
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("유효한 JSON 형식이어야 합니다")
        else:
            raise ValueError("JSON 객체 또는 문자열이어야 합니다")
    
    def create_form_schema(self, fields: List[DynamicField]) -> Dict[str, Any]:
        """폼 스키마 생성 (프론트엔드용)"""
        form_schema = {
            'fields': [],
            'validation': {}
        }
        
        for field in fields:
            field_schema = {
                'name': field.name,
                'type': field.type,
                'label': field.label,
                'required': field.required,
                'default': field.default,
                'order': field.order,
                'category': field.category,
                'description': field.description
            }
            
            if field.options:
                field_schema['options'] = field.options
            
            if field.validation:
                field_schema['validation'] = field.validation
            
            form_schema['fields'].append(field_schema)
        
        return form_schema
    
    def export_schema(self, schema: IndustrySchema) -> Dict[str, Any]:
        """스키마 내보내기"""
        return {
            'schema_type': 'industry',
            'schema_id': schema.industry_id,
            'schema_name': schema.industry_name,
            'version': schema.version,
            'fields': [asdict(field) for field in schema.fields],
            'created_at': schema.created_at.isoformat(),
            'updated_at': schema.updated_at.isoformat()
        }
    
    def import_schema(self, schema_data: Dict[str, Any]) -> IndustrySchema:
        """스키마 가져오기"""
        fields = []
        for field_data in schema_data.get('fields', []):
            field = DynamicField(**field_data)
            fields.append(field)
        
        schema = IndustrySchema(
            industry_id=schema_data['schema_id'],
            industry_name=schema_data['schema_name'],
            fields=fields,
            version=schema_data.get('version', '1.0.0'),
            created_at=datetime.fromisoformat(schema_data['created_at']),
            updated_at=datetime.fromisoformat(schema_data['updated_at'])
        )
        
        return schema

# 전역 스키마 관리자 인스턴스
schema_manager = DynamicSchemaManager() 