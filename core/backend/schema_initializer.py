"""
스키마 초기화 시스템
시스템 시작 시 기본 스키마 로드
"""

import json
import logging
from pathlib import Path
from datetime import datetime

from .dynamic_schema import schema_manager, IndustrySchema, DynamicField

logger = logging.getLogger(__name__)

def initialize_default_schemas():
    """기본 스키마 초기화"""
    try:
        logger.info("기본 스키마 초기화 시작")
        
        # 스키마 디렉토리 경로
        schemas_dir = Path("schemas")
        
        if not schemas_dir.exists():
            logger.warning("스키마 디렉토리가 존재하지 않습니다")
            return
        
        # 업종별 스키마 파일들 로드
        for schema_file in schemas_dir.glob("*_industry.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                
                # 필드 데이터를 DynamicField 객체로 변환
                fields = []
                for field_data in schema_data.get('fields', []):
                    field = DynamicField(**field_data)
                    fields.append(field)
                
                # 날짜 파싱 (Z 형식과 +00:00 형식 모두 지원)
                created_at_str = schema_data['created_at'].replace('Z', '+00:00')
                updated_at_str = schema_data['updated_at'].replace('Z', '+00:00')
                
                # IndustrySchema 생성
                schema = IndustrySchema(
                    industry_id=schema_data['schema_id'],
                    industry_name=schema_data['schema_name'],
                    fields=fields,
                    version=schema_data.get('version', '1.0.0'),
                    created_at=datetime.fromisoformat(created_at_str),
                    updated_at=datetime.fromisoformat(updated_at_str)
                )
                
                # 스키마 등록
                if schema_manager.register_industry_schema(schema_data['schema_id'], schema):
                    logger.info(f"업종 스키마 로드 완료: {schema_data['schema_name']}")
                else:
                    logger.error(f"업종 스키마 등록 실패: {schema_data['schema_name']}")
                    
            except Exception as e:
                logger.error(f"스키마 파일 로드 실패 {schema_file}: {e}")
        
        logger.info("기본 스키마 초기화 완료")
        
    except Exception as e:
        logger.error(f"스키마 초기화 실패: {e}")

def create_sample_brand_schema():
    """샘플 브랜드 스키마 생성"""
    try:
        from .dynamic_schema import BrandSchema
        
        # 레스토랑 업종의 브랜드별 커스터마이즈 필드
        brand_fields = [
            DynamicField(
                name="brand_color",
                type="string",
                label="브랜드 컬러",
                required=False,
                default="#FF6B6B",
                validation={"max_length": 7},
                order=1,
                category="branding",
                description="브랜드 대표 컬러 (HEX 코드)"
            ),
            DynamicField(
                name="signature_menu",
                type="string",
                label="시그니처 메뉴",
                required=False,
                default="",
                validation={"max_length": 100},
                order=2,
                category="menu",
                description="브랜드 대표 메뉴"
            ),
            DynamicField(
                name="loyalty_program",
                type="boolean",
                label="로열티 프로그램",
                required=False,
                default=False,
                order=3,
                category="service",
                description="로열티 프로그램 제공 여부"
            ),
            DynamicField(
                name="discount_rate",
                type="number",
                label="기본 할인율",
                required=False,
                default=0,
                validation={"min": 0, "max": 50},
                order=4,
                category="pricing",
                description="기본 할인율 (%)"
            )
        ]
        
        # 샘플 브랜드 스키마 생성
        sample_brand_schema = BrandSchema(
            brand_id="sample_restaurant",
            brand_name="샘플 레스토랑",
            industry_id="restaurant",
            fields=brand_fields,
            version="1.0.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 스키마 등록
        if schema_manager.register_brand_schema("sample_restaurant", sample_brand_schema):
            logger.info("샘플 브랜드 스키마 생성 완료")
            return True
        else:
            logger.error("샘플 브랜드 스키마 생성 실패")
            return False
            
    except Exception as e:
        logger.error(f"샘플 브랜드 스키마 생성 실패: {e}")
        return False 